# L2: 爬虫系统

## 职责

从外部数据源采集数据，计算指标，检测信号，写入数据库。

## 目录结构

```
crawlers/
├── _base/           # 共享基类
├── binance_price/   # 价格采集
├── indicator_5min/  # 指标计算
└── signal_detector/ # 信号检测
```

## 组件列表

| 组件 | 文档 | 职责 | 间隔 |
|-----|------|------|-----|
| binance-price | [../L3/binance-price.md](../L3/binance-price.md) | 采集币安实时价格 | 10s |
| indicator-5min | [../L3/indicator-5min.md](../L3/indicator-5min.md) | 计算 5 分钟涨跌幅 | 60s |
| signal-detector | [../L3/signal-detector.md](../L3/signal-detector.md) | 检测异动信号 | 60s |

## 数据流

```
binance_price ──→ prices 表
                      │
indicator_5min ←──────┘
      │
      ↓
 indicators 表
      │
signal_detector ←─────┘
      │
      ↓
  signals 表
```

## 基类设计

| 基类 | 用途 |
|-----|------|
| `BaseCrawler` | 外部数据采集，实现 `fetch()` 方法 |
| `BaseCalculator` | 数据库内计算，实现 `calculate()` 方法 |

## 部署方式

每个组件独立 Docker 容器，通过 `docker-compose.yml` 编排。
