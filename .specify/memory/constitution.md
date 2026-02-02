<!--
Sync Impact Report
==================
Version change: N/A → 1.0.0
Added sections: All (initial creation)
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (no changes needed)
  - .specify/templates/spec-template.md ✅ (no changes needed)
  - .specify/templates/tasks-template.md ✅ (no changes needed)
Follow-up TODOs: None
-->

# Few Understand 社区版 Constitution

## Core Principles

### I. 数据库即 API

所有数据通过 Hasura 自动暴露为 GraphQL API，后端只负责写入数据库。

- **MUST**: 新功能通过定义数据库表结构实现，Hasura 自动生成 CRUD 和 Subscriptions
- **MUST**: 前端直接调用 GraphQL，不手写 REST API
- **MUST**: 数据变更通过 Hasura Subscriptions 实时推送
- **理由**: 减少样板代码，维护好表结构就行

### II. TDD 非谈判

测试驱动开发是强制要求，不可妥协。

- **MUST**: 先写测试，用户确认测试用例后，运行测试确认失败，然后才写实现
- **MUST**: 遵循 Red-Green-Refactor 循环
- **MUST**: 信号检测、爬虫解析等核心逻辑必须有单元测试
- **MUST**: 数据库操作使用集成测试验证
- **理由**: 保证代码质量，防止回归

### III. 简单优先 (YAGNI)

不过度工程，够用就行。

- **MUST**: 选择最简单的实现方案，除非有明确的性能或扩展需求
- **MUST**: 不引入不需要的抽象层
- **MUST**: 单机部署优先，PostgreSQL 够用就不用 Kafka
- **SHOULD**: 代码行数越少越好，但不牺牲可读性
- **理由**: 社区版面向个人用户，资源有限，复杂度是敌人

### IV. 本地优先

Docker Compose 单机自托管，数据留在本地。

- **MUST**: 所有组件通过 docker-compose.yml 一键启动
- **MUST**: 支持 Windows/Mac/Linux 跨平台部署
- **MUST**: 数据保留策略可配置（默认 7-30 天），本地存储可控
- **MUST**: 无需外部云服务依赖（除了数据源 API）
- **理由**: 用户数据自主权，降低运营成本

### V. 可观测性

系统状态必须可见、可追踪。

- **MUST**: 使用结构化日志（JSON 格式）
- **MUST**: 爬虫状态（成功/失败/延迟）可查询
- **MUST**: 信号触发历史可追溯
- **SHOULD**: 提供健康检查端点
- **理由**: 便于调试和运维

## 开发约束

### 技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| API 层 | Hasura (GraphQL) | 自动生成，不用手写接口 |
| 数据库 | PostgreSQL + TimescaleDB | 时序数据优化，Hasura 原生支持 |
| 爬虫调度 | APScheduler | 轻量，每任务独立线程 |
| 页面爬虫 | Playwright | 绕过 API 限制 |
| K 线展示 | TradingView + Lightweight Charts | 专业看盘 + 信号标记 |
| 部署 | Docker Compose | 跨平台单机部署 |

### 代码风格

- Python: 遵循 PEP 8，使用 type hints
- SQL: 表名小写复数形式（如 `prices`, `signals`）
- 配置: 使用环境变量，不硬编码

## 质量门禁

### 合并前必须

- [ ] 所有测试通过
- [ ] 新功能有对应测试
- [ ] Docker Compose 可正常启动
- [ ] 无 lint 错误

### 代码审查关注点

- 是否遵循数据库即 API 原则
- 是否有不必要的复杂度
- 是否有硬编码配置

## Governance

本 Constitution 是项目最高指导原则，所有开发决策必须符合。

- **修订流程**: 修改需在 PR 中说明理由，获得确认后合并
- **版本规则**: 遵循语义化版本
  - MAJOR: 原则删除或重大变更
  - MINOR: 新增原则或扩展
  - PATCH: 澄清、措辞修正
- **合规检查**: PR 审查时验证是否符合 Constitution

**Version**: 1.0.0 | **Ratified**: 2026-01-21 | **Last Amended**: 2026-01-21
