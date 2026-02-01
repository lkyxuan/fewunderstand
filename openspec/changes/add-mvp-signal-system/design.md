# MVP 信号系统 - 技术设计

## Context
这是 Few Understand 社区版的第一个可运行版本。目标是用最简单的方式跑通完整的信号流程，验证核心逻辑。

## Goals / Non-Goals

**Goals:**
- 用 Binance 真实数据验证信号流程
- 一键启动（docker compose up）
- 代码简单直接，易于理解和修改

**Non-Goals:**
- 多币种支持（MVP 只做 BTC）
- 高可用、高性能（本地自托管场景）
- 前端界面（先验证后端逻辑）
- 新闻热点系统（Phase 2）

## 项目目录结构

```
fuce/
├── docker-compose.yml          # 服务编排入口
├── .env.example                 # 环境变量模板
│
├── db/
│   └── init.sql                 # 数据库初始化（建表、hypertable、索引）
│
├── hasura/
│   ├── config.yaml              # Hasura CLI 配置
│   └── metadata/                # Hasura 元数据（自动生成）
│       ├── databases/
│       │   └── default/
│       │       └── tables/      # 表 track 配置
│       └── ...
│
├── crawlers/
│   ├── requirements.txt         # Python 依赖
│   ├── main.py                  # 爬虫入口（APScheduler 调度）
│   ├── config.py                # 配置（数据库连接、API 地址等）
│   ├── db.py                    # 数据库连接工具
│   │
│   ├── price_crawler.py         # 价格采集（Binance ticker）
│   ├── indicator_calculator.py  # 指标计算（5分钟涨跌幅）
│   └── signal_detector.py       # 信号检测（阈值判断）
│
└── openspec/                    # 规格文档（你现在看到的）
```

### 文件职责说明

| 文件 | 职责 |
|------|------|
| `docker-compose.yml` | 定义 postgres、hasura 两个服务（数据库环境） |
| `db/init.sql` | 建表语句，容器启动时自动执行 |
| `hasura/metadata/` | Hasura 自动管理，记录哪些表被 track |
| `crawlers/main.py` | 启动 APScheduler，注册所有定时任务 |
| `crawlers/price_crawler.py` | 调用 Binance API，写入 `prices` 表 |
| `crawlers/indicator_calculator.py` | 读 `prices`，算涨跌幅，写 `indicators` |
| `crawlers/signal_detector.py` | 读 `indicators`，判断阈值，写 `signals` |

## Decisions

### 1. 数据采集频率
- **决定**: 价格 10 秒/次，指标和信号 1 分钟/次
- **理由**: 平衡数据精度和资源消耗，Binance API 无需认证的限流足够

### 2. 信号阈值
- **决定**: 5 分钟涨跌幅 > 1% 触发信号
- **理由**: MVP 阶段用较低阈值，更容易验证流程

### 3. Python 爬虫架构
- **决定**: 本地 Python 直接运行，APScheduler 调度
- **理由**: MVP 先跑通业务逻辑，容器化是后续部署的事

### 4. 数据库连接
- **决定**: 爬虫直连 PostgreSQL，不经过 Hasura
- **理由**: 写入走直连更简单，Hasura 只负责读取和订阅

## 数据流

```
Binance API
    │
    ▼ (每10秒)
┌─────────┐
│ prices  │ ──────┐
└─────────┘       │
                  ▼ (每分钟)
            ┌────────────┐
            │ indicators │ ──────┐
            └────────────┘       │
                                 ▼ (每分钟)
                           ┌─────────┐
                           │ signals │
                           └─────────┘
                                 │
                                 ▼ (实时)
                           Hasura Subscription
                                 │
                                 ▼
                           GraphQL Client
```

## 表结构设计

```sql
-- 原始价格数据
CREATE TABLE prices (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    price       DECIMAL(20, 8) NOT NULL,
    PRIMARY KEY (time, symbol)
);
SELECT create_hypertable('prices', 'time');

-- 计算指标
CREATE TABLE indicators (
    time            TIMESTAMPTZ NOT NULL,
    symbol          TEXT NOT NULL,
    change_5min_pct DECIMAL(10, 4),
    PRIMARY KEY (time, symbol)
);

-- 信号
CREATE TABLE signals (
    id          SERIAL PRIMARY KEY,
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    signal_type TEXT NOT NULL,  -- 'pump_5min' | 'dump_5min'
    change_pct  DECIMAL(10, 4),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_signals_time ON signals(time DESC);

-- 1分钟 OHLC 视图（供前端图表使用）
CREATE VIEW klines AS
SELECT
    time_bucket('1 minute', time) AS time,
    symbol,
    first(price, time) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, time) AS close
FROM prices
GROUP BY 1, 2;
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| Binance API 限流 | 10秒间隔足够安全，无需认证 |
| 数据库写入性能 | 单币种数据量很小，不是问题 |
| 爬虫进程崩溃 | MVP 阶段手动重启，后续加 supervisor |

## Open Questions
- 信号阈值是否需要可配置？（MVP 先硬编码）
- 是否需要去重逻辑避免重复信号？（MVP 先不管）
