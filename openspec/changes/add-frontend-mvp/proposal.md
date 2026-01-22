# Change: MVP 前端看板

## Why
当前 MVP 已具备后端数据流，但缺少用户可视化入口，无法验证“信号 + 图表 + 事件流”的产品体验。

需要一套最小可用的前端页面来承载：专业图表、可插指标的自有 K 线图、以及实时信号信息流。

## What Changes
- 新增前端 MVP 页面布局（三大模块）
- 集成 TradingView 插件展示专业图表
- 集成 TradingView Lightweight Charts 展示自有 K 线与自定义指标
- 新增右侧实时信息流与告警视觉提示
- 图表区域显示当前交易对标识（MVP 固定 BTC/USDT）
- 数据来源仅使用 Hasura GraphQL（prices/indicators/signals）

## Dependencies
- 依赖 `add-mvp-signal-system` 提供 prices/indicators/signals 表与 GraphQL Subscription

## Impact
- Affected specs: `frontend-dashboard`（新增）
- Affected code: `frontend/`（待建）、GraphQL 查询层

## Success Criteria
- [ ] 页面包含三块区域：TradingView 图表、Lightweight Chart 图表、右侧信息流
- [ ] Lightweight Chart 使用后端 K 线数据渲染 BTC/USDT
- [ ] 信息流在新信号到达时出现新条目并高亮提示（有时长）
- [ ] 图表区域展示当前交易对标识（BTC/USDT）
- [ ] 小屏下可滚动查看三块模块，布局不重叠
