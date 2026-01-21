# Implementation Plan: 基础架构

**Branch**: `001-infrastructure` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-infrastructure/spec.md`

## Summary

搭建 Few Understand 社区版的基础运行环境，通过 Docker Compose 一键启动 PostgreSQL + TimescaleDB + Hasura 服务栈。后台程序写入数据库，Hasura 自动暴露 GraphQL API 供前端读取，支持实时订阅。

## Technical Context

**Language/Version**: SQL (PostgreSQL 15), YAML (Docker Compose)
**Primary Dependencies**: Docker, Docker Compose, PostgreSQL 15, TimescaleDB 2.x, Hasura GraphQL Engine 2.x
**Storage**: PostgreSQL + TimescaleDB (时序数据优化)
**Testing**: Docker health checks, psql 连接测试, GraphQL Playground 手动验证
**Target Platform**: Docker 容器 (Linux)，宿主机支持 Windows/Mac/Linux
**Project Type**: Infrastructure (容器编排配置)
**Performance Goals**: 启动 < 2 分钟, 查询 < 500ms, 写入 < 100ms, 订阅延迟 < 1s
**Constraints**: 最小 4GB RAM, 10GB 磁盘, 需要 Docker 环境
**Scale/Scope**: 单机本地部署，开发者自用

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原则 | 要求 | 本方案 | 状态 |
|------|------|--------|------|
| I. 数据库即 API | Hasura 自动生成 GraphQL | 使用 Hasura，表结构变更自动同步 API | ✅ 通过 |
| II. TDD 非谈判 | 先写测试 | 基础架构使用 health check + 集成测试验证 | ✅ 通过 |
| III. 简单优先 | 不过度工程 | 仅 3 个服务：PostgreSQL + TimescaleDB + Hasura | ✅ 通过 |
| IV. 本地优先 | Docker Compose 一键启动 | 单个 docker-compose.yml 文件 | ✅ 通过 |
| V. 可观测性 | 健康检查端点 | Docker health checks + Hasura /healthz | ✅ 通过 |

**Gate Status**: ✅ 所有检查通过

## Project Structure

### Documentation (this feature)

```text
specs/001-infrastructure/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (基础表结构)
├── quickstart.md        # Phase 1 output (快速开始指南)
├── contracts/           # Phase 1 output (GraphQL schema)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
# Infrastructure configuration
docker-compose.yml           # 服务编排定义
.env                         # 自动生成 (gitignored，由 config/settings.yaml 生成)

# Centralized Configuration (配置优先原则)
config/
├── README.md                # 配置目录说明
├── settings.yaml            # 运行时配置 (用户编辑此文件)
├── database.yaml            # 数据库 Schema 定义 (表结构、字段、约束、索引)
├── services.yaml            # Docker 服务配置 (镜像、端口、资源限制)
└── scripts.yaml             # 脚本行为配置 (超时、重试、健康检查)

# Database
db/
├── init/                    # 首次安装时执行 (挂载到 /docker-entrypoint-initdb.d/)
│   ├── 00_init.sql          # 启用 TimescaleDB 扩展
│   ├── 01_tables.sql        # 创建所有表 + 索引
│   └── 02_timescale.sql     # hypertable + 保留策略
└── migrations/              # 版本升级时执行 (幂等脚本)
    └── .gitkeep             # 初始为空，后续版本添加

# Hasura
hasura/
├── config.yaml              # Hasura CLI 配置
├── metadata/                # Hasura 元数据 (表跟踪、权限)
│   ├── databases/
│   └── actions/
└── migrations/              # Hasura 迁移 (可选)

# Scripts
scripts/
├── start.sh                 # 启动脚本
├── stop.sh                  # 停止脚本
├── health-check.sh          # 健康检查脚本
└── migrate.sh               # 升级迁移脚本

# Tests
tests/
└── integration/
    ├── test_startup.py      # US1: 服务启动测试
    ├── test_database.py     # US2: 数据库写入测试
    ├── test_graphql.py      # US3: GraphQL API 测试
    └── test_timescale.py    # US4: 时序数据优化测试
```

**Structure Decision**: 采用 Infrastructure 配置结构。**配置优先原则**：所有可配置项集中在 `config/` 目录，便于 AI 开发和模块化管理。数据库迁移放在 `db/migrations/`，Hasura 配置放在 `hasura/`，便于独立管理。启动/停止脚本放在 `scripts/` 方便跨平台使用。

## Complexity Tracking

> 无违规项，方案符合所有 Constitution 原则。

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
