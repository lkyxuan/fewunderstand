## Context
MVP 前端需要以单页方式呈现三块核心模块：专业图表、可插指标的自有 K 线图、以及实时信号信息流。后端数据由 Hasura GraphQL 提供，前端只消费数据，不承担计算逻辑。

## Goals / Non-Goals
- Goals:
  - 在同一屏内清晰展示三块模块
  - TradingView 插件提供专业图表视角
  - Lightweight Charts 支持自有 K 线与自定义指标
  - 信息流对新增信号提供明显视觉提示
- Non-Goals:
  - 多币种切换
  - 用户登录/权限
  - 新闻热点系统

## Decisions
- Decision: 单页三栏布局（左侧图表区，上下两张图；右侧信息流）
- Decision: 数据源统一走 GraphQL 查询与订阅（klines/indicators/signals）
- Decision: MVP 以 BTC/USDT 固定展示，简化交互
- Decision: 图表区域显示当前交易对标识，不提供切换功能
- Decision: 小屏以纵向堆叠方式展示，允许滚动查看三块模块

## Risks / Trade-offs
- TradingView 插件与 Lightweight Charts 的并存会增加首屏资源加载；MVP 优先功能正确性。
- 信息流的“闪烁/跳动”需要节制，避免视觉干扰；需提供最小可用的提醒效果。

## Migration Plan
1. 先接入静态或历史数据，确保两张图可稳定渲染
2. 接入实时订阅信号流并联动信息流显示
3. 再扩展指标与告警策略

## Open Questions
- 信息流告警规则的最低可用定义

## Technical Requirements (审计后补充)

### 后端数据源
- **klines 视图**: 1分钟 K 线连续聚合 (OHLC)，从 prices 自动聚合
- **GraphQL 端点**: `http://<server>:8080/v1/graphql`
- **订阅端点**: `ws://<server>:8080/v1/graphql` (WebSocket)
- **匿名访问**: 已启用 `anonymous` 角色，前端无需认证

### 可用查询
```graphql
# K 线数据
query { klines(where: {symbol: {_eq: "BTCUSDT"}}, order_by: {time: desc}, limit: 100) { time open high low close } }

# 实时信号订阅
subscription { signals(order_by: {time: desc}, limit: 10) { time symbol signal_type change_pct } }
```

### 数据刷新频率
- prices: 每 10 秒采集
- klines: 每 1 分钟自动聚合
- indicators: 每 60 秒计算
- signals: 每 60 秒检测
