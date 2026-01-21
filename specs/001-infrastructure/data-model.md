# Data Model: 基础架构

**Branch**: `001-infrastructure` | **Date**: 2026-01-21

## Overview

本文档定义 Few Understand 社区版的核心数据模型。所有表都是 TimescaleDB hypertables，支持高效的时序查询和自动数据保留。

## Entity Relationship

```
┌─────────────┐     计算      ┌─────────────┐     检测      ┌─────────────┐
│   prices    │ ──────────► │  indicators  │ ──────────► │   signals   │
│  (原始价格)  │              │   (指标)     │              │   (信号)    │
└─────────────┘              └─────────────┘              └─────────────┘

┌─────────────┐              ┌─────────────┐
│   klines    │              │    news     │ ──────────► │  word_freq  │
│  (K线数据)   │              │   (新闻)    │    统计      │  (词频)     │
└─────────────┘              └─────────────┘              └─────────────┘
```

## Entities

### 1. prices (价格数据)

存储实时价格快照，用于计算指标。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| time | TIMESTAMPTZ | NOT NULL | 记录时间 (主键之一) |
| symbol | VARCHAR(20) | NOT NULL | 交易对，如 BTCUSDT |
| price | DECIMAL(20,8) | NOT NULL | 当前价格 |
| volume_24h | DECIMAL(30,8) | | 24小时交易量 |
| source | VARCHAR(50) | | 数据来源 |

**Primary Key**: (time, symbol)
**Hypertable Partition**: time (按天分区)
**Retention Policy**: 可配置 (默认 30 天)

---

### 2. klines (K线数据)

存储 1 分钟 K 线，用于图表展示。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| time | TIMESTAMPTZ | NOT NULL | K线开始时间 (主键之一) |
| symbol | VARCHAR(20) | NOT NULL | 交易对 |
| open | DECIMAL(20,8) | NOT NULL | 开盘价 |
| high | DECIMAL(20,8) | NOT NULL | 最高价 |
| low | DECIMAL(20,8) | NOT NULL | 最低价 |
| close | DECIMAL(20,8) | NOT NULL | 收盘价 |
| volume | DECIMAL(30,8) | | 成交量 |

**Primary Key**: (time, symbol)
**Hypertable Partition**: time (按天分区)
**Retention Policy**: 可配置 (默认 30 天)

---

### 3. indicators (指标数据)

存储计算后的技术指标。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| time | TIMESTAMPTZ | NOT NULL | 计算时间 (主键之一) |
| symbol | VARCHAR(20) | NOT NULL | 交易对 |
| change_5min | DECIMAL(10,4) | | 5分钟涨跌幅 (%) |
| change_15min | DECIMAL(10,4) | | 15分钟涨跌幅 (%) |
| change_1h | DECIMAL(10,4) | | 1小时涨跌幅 (%) |
| volume_change | DECIMAL(10,4) | | 交易量变化 (%) |

**Primary Key**: (time, symbol)
**Hypertable Partition**: time (按天分区)
**Retention Policy**: 覆盖模式 (只保留最新)

---

### 4. signals (信号数据)

存储触发的交易信号。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 自增 ID |
| time | TIMESTAMPTZ | NOT NULL | 信号触发时间 |
| symbol | VARCHAR(20) | NOT NULL | 交易对 |
| signal_type | VARCHAR(50) | NOT NULL | 信号类型 (pump_5min, dump_5min 等) |
| change_pct | DECIMAL(10,4) | | 触发时的涨跌幅 |
| price | DECIMAL(20,8) | | 触发时的价格 |
| metadata | JSONB | | 额外信息 |

**Index**: (time DESC), (symbol, time DESC)
**Hypertable Partition**: time (按天分区)
**Retention Policy**: 可配置 (默认 30 天)

---

### 5. news (新闻数据)

存储爬取的新闻文章。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 自增 ID |
| time | TIMESTAMPTZ | NOT NULL | 发布时间 |
| source | VARCHAR(50) | NOT NULL | 来源 (coindesk, cointelegraph 等) |
| title | TEXT | NOT NULL | 标题 |
| url | TEXT | UNIQUE | 原文链接 |
| content | TEXT | | 正文内容 |
| crawled_at | TIMESTAMPTZ | DEFAULT NOW() | 爬取时间 |

**Index**: (time DESC), (source, time DESC)
**Hypertable Partition**: time (按天分区)
**Retention Policy**: 可配置 (默认 30 天)

---

### 6. word_freq (词频统计)

存储新闻词频聚合结果。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| time | TIMESTAMPTZ | NOT NULL | 统计时间 (主键之一) |
| window | VARCHAR(20) | NOT NULL | 时间窗口 (5min, 1h, 24h) |
| word | VARCHAR(100) | NOT NULL | 关键词 |
| count | INTEGER | NOT NULL | 出现次数 |
| latest_news_id | BIGINT | REFERENCES news(id) | 最新相关新闻 |

**Primary Key**: (time, window, word)
**Retention Policy**: 覆盖模式 (每个窗口只保留最新统计)

---

## Validation Rules

1. **prices.price**: 必须 > 0
2. **klines**: high >= low, high >= open, high >= close, low <= open, low <= close
3. **signals.signal_type**: 必须是预定义的类型之一
4. **news.url**: 必须唯一，防止重复爬取

## State Transitions

### Signal Lifecycle

```
[计算指标] → [检测阈值] → [写入 signals 表] → [Hasura Subscription 推送]
```

### News Processing

```
[爬取新闻] → [去重检查] → [写入 news 表] → [词频统计] → [写入 word_freq]
```

## Index Strategy

| 表 | 索引 | 用途 |
|------|------|------|
| prices | (time, symbol) | 按时间和交易对查询 |
| signals | (time DESC) | 最新信号列表 |
| signals | (symbol, time DESC) | 按币种查信号历史 |
| news | (time DESC) | 最新新闻列表 |
| news | (source, time DESC) | 按来源查新闻 |
| word_freq | (window, count DESC) | 热门词排序 |

## TimescaleDB 特性

### Hypertables

所有时序表转换为 hypertables：

```sql
SELECT create_hypertable('prices', 'time');
SELECT create_hypertable('klines', 'time');
SELECT create_hypertable('indicators', 'time');
SELECT create_hypertable('signals', 'time');
SELECT create_hypertable('news', 'time');
```

### Retention Policies

```sql
-- 可配置保留期限
SELECT add_retention_policy('prices', INTERVAL '30 days');
SELECT add_retention_policy('klines', INTERVAL '30 days');
SELECT add_retention_policy('signals', INTERVAL '30 days');
SELECT add_retention_policy('news', INTERVAL '30 days');
```

### Continuous Aggregates (可选优化)

如需要聚合查询性能，可添加：

```sql
-- 示例：5分钟价格聚合
CREATE MATERIALIZED VIEW prices_5min
WITH (timescaledb.continuous) AS
SELECT time_bucket('5 minutes', time) AS bucket,
       symbol,
       first(price, time) AS open,
       max(price) AS high,
       min(price) AS low,
       last(price, time) AS close
FROM prices
GROUP BY bucket, symbol;
```
