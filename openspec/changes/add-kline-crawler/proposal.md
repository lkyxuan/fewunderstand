# Proposal: add-kline-crawler

## Summary
新增币安 K-Line 历史数据爬虫，支持首次运行时下载 30 天历史 K 线，之后持续增量采集。

## Why
当前系统通过 `binance_price` 爬虫每 10 秒采集一次价格快照，然后通过 TimescaleDB 连续聚合生成 1 分钟 K 线。这种方式存在两个问题：

1. **历史数据缺失**：新部署时没有历史数据，前端图表无法展示有意义的 K 线
2. **聚合精度有限**：10 秒一次的快照聚合成 OHLC，可能丢失真实的最高/最低价

币安提供标准的 K-Line API，可以直接获取精确的 OHLC 数据，解决上述问题。

## Scope

### In Scope
- 币安 K-Line API 爬虫（1 分钟级别）
- 首次运行：下载 30 天历史 K 线
- 持续运行：每分钟增量采集最新 K 线
- 新增 `klines_raw` 表存储原始 K 线数据
- Docker 容器化，与现有服务集成

### Out of Scope
- 多时间级别（5m/15m/1h/1d）- 可后续扩展
- 多交易所支持 - 当前仅币安
- K 线数据计算指标 - 复用现有 indicators 流程

## Impact
- **数据库**: 新增 `klines_raw` 表
- **服务**: 新增 `binance-kline` 容器
- **GraphQL**: Hasura 自动暴露新表，前端可直接查询

## Related Changes
- add-frontend-mvp: 前端需要 K 线数据展示图表

## Deltas
- specs/kline-data-collection: K 线数据采集能力规格
