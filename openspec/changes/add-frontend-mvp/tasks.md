## 1. Implementation

### 1.1 项目初始化（已决定技术栈）
- [x] 1.1.1 框架选型：**Next.js 14 + React 18 + TypeScript**
- [x] 1.1.2 初始化 `frontend/` 目录，配置 Next.js App Router
- [x] 1.1.3 安装依赖：Apollo Client、Lightweight Charts、TradingView Widget
- [x] 1.1.4 配置 Apollo Client 连接 Hasura GraphQL

**技术栈确定**（2026-01-22）：
- 框架：Next.js + React + TypeScript
- GraphQL：Apollo Client
- 图表：TradingView Widget + Lightweight Charts
- 样式：深色主题，CSS Modules 或 Tailwind
- 详见 `design.md` → Technology Stack Decisions

### 1.2-1.10 功能实现
- [x] 1.2 搭建页面三块布局骨架（主图区上下两图 + 右侧信息流）
- [x] 1.3 集成 TradingView 插件并完成基础交互
- [x] 1.4 接入 Hasura GraphQL 数据源（klines/indicators/signals），含订阅
- [x] 1.4.1 环境变量配置 GraphQL HTTP/WS 端点
- [x] 1.5 使用 Lightweight Charts 渲染 K 线与指标
- [x] 1.6 实现信息流展示与新信号视觉提示（含高亮持续时间）
- [x] 1.7 添加交易对标识（仅展示 BTC/USDT）
- [x] 1.8 响应式布局与小屏降级（允许滚动查看三块模块）
- [x] 1.9 基础错误处理与空状态
- [ ] 1.10 最小验收验证：图表渲染 + 订阅信号到达时提示出现
