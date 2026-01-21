# Research: 基础架构

**Branch**: `001-infrastructure` | **Date**: 2026-01-21

## Overview

本文档记录基础架构技术选型的决策过程和最佳实践研究。

## 技术决策

### 1. 数据库选型：PostgreSQL + TimescaleDB

**Decision**: 使用 PostgreSQL 15 + TimescaleDB 2.x 扩展

**Rationale**:
- TimescaleDB 是 PostgreSQL 的时序数据扩展，无需额外学习成本
- 原生支持数据保留策略 (`add_retention_policy`)，自动清理过期数据
- Hasura 原生支持 PostgreSQL，无缝集成
- 社区版活跃，文档完善

**Alternatives Considered**:
| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| InfluxDB | 专业时序数据库 | Hasura 不支持，需要额外 API 层 | 不采用 |
| MySQL | 熟悉度高 | 时序支持弱，Hasura 支持不如 PG | 不采用 |
| 纯 PostgreSQL | 简单 | 大量时序数据性能差 | 不采用 |

### 2. API 层选型：Hasura GraphQL Engine

**Decision**: 使用 Hasura GraphQL Engine 2.x

**Rationale**:
- 自动将数据库表暴露为 GraphQL API，零代码
- 内置 Subscriptions 支持实时数据推送
- 表结构变更后 API 自动更新
- 提供 Console 可视化管理界面
- 符合"数据库即 API"原则

**Alternatives Considered**:
| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| PostgREST | 简单 | 只有 REST，无 Subscriptions | 不采用 |
| 手写 FastAPI | 灵活 | 需要大量样板代码，违反 YAGNI | 不采用 |
| Prisma | 类型安全 | 需要定义 schema，不够"自动" | 不采用 |

### 3. 容器编排：Docker Compose

**Decision**: 使用 Docker Compose v2

**Rationale**:
- 单文件定义所有服务
- 跨平台支持 (Windows/Mac/Linux)
- 内置 health check 和依赖管理
- 开发者熟悉度高

**Alternatives Considered**:
| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| Kubernetes | 生产级 | 过度复杂，违反 YAGNI | 不采用 |
| Docker Swarm | 可扩展 | 单机场景不需要 | 不采用 |
| 裸机安装 | 性能好 | 环境一致性差，部署复杂 | 不采用 |

### 4. Docker 镜像版本

**Decision**: 使用官方镜像的特定版本标签

**Rationale**:
- 避免 `latest` 标签导致的不可预测更新
- 锁定主版本，允许小版本更新获取安全补丁

**Selected Versions**:
| 服务 | 镜像 | 版本策略 |
|------|------|----------|
| PostgreSQL + TimescaleDB | `timescale/timescaledb:latest-pg15` | 锁定 PG15 |
| Hasura | `hasura/graphql-engine:v2.36.0` | 锁定具体版本 |

## 最佳实践

### Docker Compose 配置

1. **服务依赖**: 使用 `depends_on` + `condition: service_healthy`
2. **健康检查**: 每个服务配置 `healthcheck`
3. **数据持久化**: 使用 named volumes，不用 bind mounts
4. **环境变量**: 敏感信息通过 `.env` 文件注入

### 数据库初始化

1. **启动顺序**: PostgreSQL → TimescaleDB 扩展 → 基础表 → Hasura 连接
2. **迁移管理**: SQL 文件按序号命名 (001_, 002_...)
3. **幂等性**: 所有迁移脚本使用 `IF NOT EXISTS`

### Hasura 配置

1. **元数据管理**: 使用 `hasura/metadata/` 目录版本化
2. **环境分离**: 开发/生产使用不同的 `.env`
3. **权限控制**: 初期使用 admin secret，后续按需配置角色

## 端口分配

| 服务 | 端口 | 说明 |
|------|------|------|
| PostgreSQL | 5432 | 数据库连接 |
| Hasura Console | 8080 | GraphQL API + 管理界面 |
| Hasura API | 8080/v1/graphql | GraphQL 端点 |

## 环境变量规划

```bash
# Database
POSTGRES_USER=lagos
POSTGRES_PASSWORD=<生成的密码>
POSTGRES_DB=lagos

# Hasura
HASURA_GRAPHQL_DATABASE_URL=postgres://lagos:<password>@postgres:5432/lagos
HASURA_GRAPHQL_ADMIN_SECRET=<管理员密钥>
HASURA_GRAPHQL_ENABLE_CONSOLE=true

# Data retention
RETENTION_DAYS=30
```

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 端口冲突 | 服务无法启动 | 脚本检测并提示 |
| 磁盘空间不足 | 数据丢失 | 配置保留策略，监控磁盘使用 |
| Docker 未安装 | 无法运行 | 文档说明前置要求 |

## 结论

所有技术选型已确定，无 NEEDS CLARIFICATION 项。可以进入 Phase 1 设计阶段。
