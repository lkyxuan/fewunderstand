## ADDED Requirements
### Requirement: MVP 前端三块模块
系统 MUST 提供单页三块模块布局：TradingView 专业图表、Lightweight Charts 自有 K 线图、右侧信息流。

#### Scenario: 桌面端页面加载
- **WHEN** 用户打开前端首页且视口宽度 >= 1280px 且高度 >= 720px
- **THEN** 三块模块在同一屏幕内可见且主要区域尺寸保持不变

#### Scenario: 小屏降级
- **WHEN** 视口宽度 < 1280px 或高度 < 720px
- **THEN** 三块模块按纵向堆叠展示并可滚动查看

### Requirement: GraphQL 数据源
系统 MUST 仅通过 Hasura GraphQL 查询/订阅获取 klines/indicators/signals 数据。

#### Scenario: 数据加载
- **WHEN** 页面初始化加载
- **THEN** 通过 GraphQL Query 从 klines 视图获取 OHLC 数据

#### Scenario: 信号订阅
- **WHEN** `signals` 表插入新记录
- **THEN** GraphQL Subscription 推送并触发信息流更新

### Requirement: TradingView 插件集成
系统 MUST 在主图区域集成 TradingView 插件展示专业图表。

#### Scenario: 专业图表可用
- **WHEN** 页面加载完成
- **THEN** TradingView 图表可交互（缩放/拖拽/时间轴）

### Requirement: Lightweight Charts K 线图
系统 MUST 使用自有 K 线数据渲染 Lightweight Charts 图表，并支持插入自定义指标。

#### Scenario: K 线数据渲染
- **WHEN** 获取到 BTC/USDT 的 K 线数据
- **THEN** 轻量图表正确渲染蜡烛图并显示最新价格

#### Scenario: 自定义指标展示
- **WHEN** 指标数据可用
- **THEN** 指标以叠加或子图方式展示在轻量图表中

### Requirement: 交易对标识展示
系统 MUST 在图表区域展示当前交易对标识（BTC/USDT）。

#### Scenario: 交易对标识可见
- **WHEN** 用户查看图表区域
- **THEN** 当前交易对（如 BTC/USDT）清晰可见

### Requirement: 右侧信息流与告警提示
系统 MUST 提供右侧信息流模块，并对新信号提供明确视觉提示。

#### Scenario: 新信号提醒
- **WHEN** 有新信号到达
- **THEN** 信息流出现新条目且该条目高亮至少 3 秒

### Requirement: 空状态与错误提示
系统 MUST 在数据不可用或请求失败时提供可理解的空状态或错误提示。

#### Scenario: 空状态
- **WHEN** K 线或指标数据为空
- **THEN** 对应图表区域显示空状态说明

#### Scenario: 请求失败
- **WHEN** GraphQL 请求失败或订阅中断
- **THEN** 显示错误提示并提供重试入口
