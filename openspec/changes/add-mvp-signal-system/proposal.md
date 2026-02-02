# Change: MVP 信号系统

## Why
之前的开发方式先写测试再实现，但没有真实数据导致测试无法通过，陷入死循环。

需要换一个思路：**先用 Binance API 真实数据跑通完整流程**，验证核心逻辑，再逐步扩展。

## What Changes
MVP 聚焦单一币种（BTC/USDT）的完整信号流程：

1. **基础设施**
   - Docker Compose 编排（PostgreSQL + TimescaleDB + Hasura）
   - 数据库表结构（prices, indicators, signals）

2. **价格信号系统**
   - Binance API 价格采集（每10秒）
   - 指标计算（5分钟涨跌幅）
   - 信号检测（涨跌超过阈值触发）
   - GraphQL 订阅推送

**暂不包含**：
- 新闻热点系统
- 前端界面（框架待定）
- 多币种支持

## Impact
- Affected specs: `infrastructure`, `price-signals`（新增）
- Affected code: `db/`, `crawlers/`

## Success Criteria
- [ ] 币安价格写入 `prices` 表
- [ ] 指标计算写入 `indicators` 表
- [ ] 信号检测写入 `signals` 表
