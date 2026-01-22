# Few Understand 社区版

加密货币信息平台 - 信号系统 + 新闻热点

## 核心功能

- **新闻热点**: 词频聚合，实时推送
- **价格信号**: 异动检测，触发推送
- **K 线展示**: TradingView + Lightweight Charts 双模式

## 快速开始

### 前置要求

- Docker Desktop 或 Docker Engine + Docker Compose
- 4GB 可用内存

### 启动

```bash
git clone https://github.com/<owner>/fuce.git
cd fuce
cp .env.example .env
./scripts/start.sh
```

### 访问

- **Hasura Console**: http://localhost:8080
- **PostgreSQL**: localhost:5432

### 停止

```bash
./scripts/stop.sh
```

## 技术栈

| 组件 | 选型 |
|------|------|
| API | Hasura (GraphQL) |
| 数据库 | PostgreSQL + TimescaleDB |
| 部署 | Docker Compose |

## 项目状态

🚧 **开发中** - 基础架构搭建阶段

## 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

[待定]
