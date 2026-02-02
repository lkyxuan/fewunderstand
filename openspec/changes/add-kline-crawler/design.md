# Design: add-kline-crawler

## Context
需要实现币安 K-Line 数据的历史回填和增量采集，与现有 `prices` → `klines` 聚合视图并行存在。

## Goals / Non-Goals

### Goals
- 支持首次部署时自动回填 30 天历史数据
- 每分钟增量采集最新 K 线
- 数据精度与币安官方一致（精确 OHLC + volume）
- 复用现有爬虫基础设施（_base/db.py）

### Non-Goals
- 替换现有的 prices → klines 连续聚合（两者并存）
- 实现多时间级别 K 线（5m/15m/1h/1d）
- WebSocket 实时推送（保持简单的 HTTP 轮询）

## Decisions

### Decision 1: 新增 `klines_raw` 表而非修改现有 `klines` 视图

**理由**：
- `klines` 是从 `prices` 自动聚合的连续聚合视图，不宜直接插入数据
- 保留两套数据源便于对比验证
- 前端可选择使用哪个数据源

### Decision 2: 使用币安 `/api/v3/klines` API

**API 特点**：
- 单次最多返回 1000 条 K 线
- 支持 `startTime`/`endTime` 参数
- 返回完整 OHLCV 数据

**历史回填策略**：
- 30 天 × 24 小时 × 60 分钟 = 43,200 条
- 分批请求：每次 1000 条，约 44 次请求
- 加入适当延迟避免限流

### Decision 3: 采集哪些交易对

**MVP 方案**：仅采集 BTCUSDT（与前端 MVP 一致）

**扩展方案**：复用 `binance_price` 的交易对过滤逻辑，但 K-Line API 需逐个请求

### Decision 4: 增量采集策略

```
每分钟运行一次：
1. 查询 klines_raw 中该 symbol 最新时间
2. 从最新时间开始请求到当前时间
3. 使用 UPSERT 避免重复
```

## Risks / Trade-offs

### Risk 1: API 限流
- 币安限制：1200 次/分钟
- 风险：历史回填时密集请求可能触发限流
- 缓解：每批次请求后 sleep 1 秒

### Risk 2: 数据一致性
- 风险：爬虫重启时可能有数据空隙
- 缓解：每次启动检查最新时间，回补缺失数据

### Trade-off: 存储空间
- 30 天数据量：~43,200 行/交易对
- 如果扩展到 100 个交易对：~432 万行
- 可接受，TimescaleDB 压缩后占用较小

## Data Model

```sql
CREATE TABLE IF NOT EXISTS klines_raw (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8) NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    quote_volume DECIMAL(30,8),  -- 成交额
    trades INTEGER,               -- 成交笔数
    PRIMARY KEY (time, symbol)
);

-- 转为 TimescaleDB hypertable
SELECT create_hypertable('klines_raw', 'time', if_not_exists => TRUE);

-- 保留 30 天数据
SELECT add_retention_policy('klines_raw', INTERVAL '30 days', if_not_exists => TRUE);
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   binance-kline 容器                 │
│                                                     │
│  ┌──────────────┐    ┌───────────────────────────┐ │
│  │ 历史回填模块 │    │     增量采集模块           │ │
│  │              │    │                           │ │
│  │ 启动时检查   │    │ 每分钟检查最新时间         │ │
│  │ 补齐30天数据 │    │ 请求新 K 线并写入         │ │
│  └──────────────┘    └───────────────────────────┘ │
│           │                      │                 │
│           └──────────┬───────────┘                 │
│                      ↓                             │
│              PostgreSQL (klines_raw)               │
└─────────────────────────────────────────────────────┘
```

## Frontend Integration

### 数据源选择

前端 MVP 当前期望使用 `klines` 视图，但 `klines_raw` 提供更精确的数据：

| 数据源 | 来源 | 精度 | 历史数据 |
|--------|------|------|----------|
| `klines` | prices 表聚合 | 10秒快照聚合 | 依赖爬虫运行时间 |
| `klines_raw` | 币安 API 直接获取 | 官方精确 OHLCV | 首次启动即有30天 |

**决策**：前端应优先使用 `klines_raw`，因为：
1. 数据精度更高（真实 OHLC，非快照聚合）
2. 首次部署即有历史数据
3. 包含成交量等完整信息

### 字段映射

```
klines 视图:     time, symbol, open, high, low, close, tick_count
klines_raw 表:   time, symbol, open, high, low, close, volume, ...

前端 GraphQL 查询只需：time, open, high, low, close, volume
两者核心字段兼容，klines_raw 额外提供 volume
```

### 兼容性视图（可选）

如需同时支持两个数据源，可创建统一视图：

```sql
CREATE VIEW klines_unified AS
SELECT time, symbol, open, high, low, close, volume
FROM klines_raw
UNION ALL
SELECT time, symbol, open, high, low, close, NULL as volume
FROM klines
WHERE NOT EXISTS (
    SELECT 1 FROM klines_raw kr
    WHERE kr.time = klines.time AND kr.symbol = klines.symbol
);
```

## Open Questions

1. **是否需要支持多交易对？**
   - MVP 建议仅 BTCUSDT
   - 可通过环境变量 `SYMBOLS=BTCUSDT,ETHUSDT` 扩展

2. **K 线时间级别？**
   - MVP 建议仅 1m
   - 更大级别可通过 SQL 聚合生成
