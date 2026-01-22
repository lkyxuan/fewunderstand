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

## Technology Stack Decisions (2026-01-22 讨论确定)

### 前端框架：Next.js + React

**选择理由**：
- AI（Codex/Claude）对 React/Next.js 最熟悉，生成代码质量最高
- 生态成熟，TradingView 和 Lightweight Charts 都有良好的 React 集成
- 支持长远演进：SSR/SSG、API Routes、NextAuth 认证、PWA 等
- 部署简单（Vercel 一键部署）

**不选原生 JS 的原因**：
- 虽然 MVP 场景简单，原生 JS 够用
- 但从终极形态考虑（用户系统、AI 配置、多币种），Next.js 一步到位，避免后期重写

### GraphQL 客户端：Apollo Client

**选择理由**：
- 与 React/Next.js 集成最成熟
- 内置缓存管理
- 支持 Subscription（WebSocket 实时订阅）
- 类型安全（配合 GraphQL Code Generator）

### 图表库

| 图表 | 库 | 用途 |
|------|---|------|
| 专业图表 | TradingView Widget | 用户自由看盘、画线、加指标 |
| 自有 K 线 | Lightweight Charts | 自有数据渲染，支持自定义标记（买入/卖出信号） |

### 样式方案

- **主题**：深色主题（参考 json-render.dev 风格）
- **配色**：
  - 背景：`#000` / `#0a0a0a`
  - 强调色：`#00ff88`（青绿色）
  - 涨：`#00ff88`，跌：`#ff4757`
- **动画**：CSS `@keyframes` 实现信号弹入效果
- **方案**：CSS Modules 或 Tailwind CSS（待定）

### 项目结构

```
frontend/
├── app/
│   ├── layout.tsx          # 根布局（深色主题）
│   ├── page.tsx            # 主页（三栏布局）
│   └── globals.css         # 全局样式
├── components/
│   ├── TradingViewChart.tsx    # TradingView 封装
│   ├── LightweightChart.tsx    # Lightweight Charts 封装
│   └── SignalFeed.tsx          # 信号信息流
├── lib/
│   ├── apollo-client.ts    # Apollo Client 配置
│   └── queries.ts          # GraphQL 查询/订阅
├── package.json
└── next.config.js
```

### 架构演进路径

| 阶段 | 功能 | 技术 |
|------|------|------|
| **MVP** | 固定看板，BTC 数据 | Next.js + Apollo + Hasura |
| **V1** | 多币种支持 | 状态管理（Zustand） |
| **V2** | 用户登录、保存配置 | NextAuth + Hasura 权限 |
| **V3** | 告警推送 | Telegram Bot / Email |
| **V4** | AI 自定义界面 | json-render 集成 |
| **V5** | 付费订阅 | Stripe |

### 关于 json-render

**当前**：MVP 不使用，固定布局即可

**未来**：当需要「让用户通过 AI 自定义界面」时引入
- 用户输入「给我加个 ETH 图表」
- AI 生成符合组件目录的 JSON
- json-render 渲染成实际组件

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
