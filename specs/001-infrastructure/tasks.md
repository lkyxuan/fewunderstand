# Tasks: 基础架构

**Input**: Design documents from `/specs/001-infrastructure/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: 根据 Constitution II (TDD 非谈判)，基础架构使用集成测试验证。

**Organization**: 任务按用户故事组织，支持独立实现和测试。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 所属用户故事 (US1, US2, US3, US4)
- 包含精确的文件路径

---

## Phase 1: Setup (项目初始化)

**Purpose**: 创建基础目录结构和配置文件

- [ ] T001 创建项目目录结构：db/init/, db/migrations/, hasura/metadata/, scripts/, tests/integration/, .github/
- [ ] T002 [P] 创建环境变量模板文件 .env.example
- [ ] T003 [P] 创建 .gitignore 文件，忽略 .env 和 Docker volumes

### GitHub 自动化

- [ ] T004 [P] 创建 CI 工作流 .github/workflows/ci.yml (push 时运行测试)
- [ ] T005 [P] 创建 Docker 构建工作流 .github/workflows/docker.yml (构建并推送镜像)
- [ ] T006 [P] 创建 Bug Report 模板 .github/ISSUE_TEMPLATE/bug_report.md
- [ ] T007 [P] 创建 Feature Request 模板 .github/ISSUE_TEMPLATE/feature_request.md
- [ ] T008 [P] 创建 PR 模板 .github/PULL_REQUEST_TEMPLATE.md
- [ ] T009 [P] 创建 Release 工作流 .github/workflows/release.yml (tag 时自动发布)

**Checkpoint**: 目录结构就绪，GitHub Actions 配置完成

---

## Phase 2: Foundational (阻塞性前置任务)

**Purpose**: 核心基础设施，所有用户故事依赖此阶段

**⚠️ CRITICAL**: 此阶段必须完成后才能开始用户故事

- [ ] T010 创建 docker-compose.yml，定义 postgres 和 hasura 服务
- [ ] T011 配置 PostgreSQL 服务：使用 timescale/timescaledb:latest-pg15 镜像
- [ ] T012 配置 Hasura 服务：使用 hasura/graphql-engine:v2.36.0 镜像
- [ ] T013 配置服务依赖：hasura depends_on postgres (condition: service_healthy)
- [ ] T014 配置 Docker volumes 用于数据持久化
- [ ] T015 配置服务健康检查 (healthcheck)

**Checkpoint**: docker-compose.yml 完成，可以 `docker compose config` 验证

---

## Phase 3: User Story 1 - 一键启动开发环境 (Priority: P1) 🎯 MVP

**Goal**: 开发者运行一条命令就能启动完整环境

**Independent Test**: 运行 `./scripts/start.sh`，2 分钟内所有服务 healthy

### Implementation for US1

- [ ] T016 [US1] 创建数据库初始化脚本 db/init/00_init.sql (启用 TimescaleDB 扩展)
- [ ] T017 [US1] 创建启动脚本 scripts/start.sh
- [ ] T018 [US1] 创建停止脚本 scripts/stop.sh
- [ ] T019 [US1] 创建健康检查脚本 scripts/health-check.sh
- [ ] T020 [US1] 创建升级迁移脚本 scripts/migrate.sh (按序执行 db/migrations/*.sql)
- [ ] T021 [US1] 配置 Hasura Console 访问 (HASURA_GRAPHQL_ENABLE_CONSOLE=true)

### Tests for US1

- [ ] T022 [US1] 创建集成测试 tests/integration/test_startup.py (验证服务启动)

**Checkpoint**: `./scripts/start.sh` 可成功启动所有服务，`./scripts/health-check.sh` 显示全部 healthy

---

## Phase 4: User Story 2 - 数据写入能力 (Priority: P1)

**Goal**: 后台程序可以将数据写入数据库

**Independent Test**: 使用 psql 连接并执行 INSERT，数据正确持久化

### Implementation for US2

- [ ] T023 [US2] 创建数据库初始化脚本 db/init/001_extensions.sql (启用 TimescaleDB 扩展)
- [ ] T024 [US2] 创建表结构脚本 db/init/002_tables.sql (所有 6 张表 + 索引)
- [ ] T025 [US2] 配置 Docker 挂载 db/init/ 目录到 postgres 容器的 /docker-entrypoint-initdb.d/

### Tests for US2

- [ ] T026 [US2] 创建集成测试 tests/integration/test_database.py (验证表创建和数据写入)

**Checkpoint**: 可以通过 psql 连接并向各表插入数据

---

## Phase 5: User Story 3 - GraphQL API 自动暴露 (Priority: P1)

**Goal**: Hasura 自动将数据库表暴露为 GraphQL API

**Independent Test**: 在 GraphQL Playground 执行查询，返回数据库中的数据

### Implementation for US3

- [ ] T027 [US3] 创建 Hasura 配置文件 hasura/config.yaml
- [ ] T028 [US3] 配置 Hasura 元数据目录结构 hasura/metadata/
- [ ] T029 [US3] 创建数据库连接配置 hasura/metadata/databases/databases.yaml
- [ ] T030 [US3] 配置表跟踪 (track tables) hasura/metadata/databases/default/tables/
- [ ] T031 [US3] 配置 Hasura 使用元数据目录 (通过环境变量或 CLI)

### Tests for US3

- [ ] T032 [US3] 创建集成测试 tests/integration/test_graphql.py (验证查询和订阅)

**Checkpoint**: 在 http://localhost:8080 的 GraphQL Playground 可以查询数据

---

## Phase 6: User Story 4 - 时序数据优化 (Priority: P2)

**Goal**: TimescaleDB 优化时序数据存储和查询，自动清理过期数据

**Independent Test**: 插入大量数据后，查询最近时间段响应快速

### Implementation for US4

- [ ] T033 [US4] 创建 hypertable 和保留策略脚本 db/init/003_timescale.sql
- [ ] T034 [US4] 配置保留天数环境变量 RETENTION_DAYS 在 .env.example

### Tests for US4

- [ ] T035 [US4] 创建集成测试 tests/integration/test_timescale.py (验证 hypertable 和保留策略)

**Checkpoint**: 数据保留策略配置完成，可通过 SQL 查询验证

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 完善文档和最终验证

- [ ] T036 [P] 更新 README.md 添加快速开始说明
- [ ] T037 [P] 创建 CONTRIBUTING.md 开发者指南
- [ ] T038 验证 quickstart.md 步骤可正常执行
- [ ] T039 运行所有集成测试确保通过

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 - **阻塞所有用户故事**
- **User Stories (Phase 3-6)**: 全部依赖 Foundational 完成
  - US1, US2, US3 可并行执行（如有多人）
  - US4 依赖 US2（需要表结构）
- **Polish (Phase 7)**: 依赖所有用户故事完成

### User Story Dependencies

```
Phase 2 (Foundational)
         │
         ▼
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
  US1       US2       US3
(启动)    (数据库)   (API)
    │         │         │
    │         ▼         │
    │       US4        │
    │    (时序优化)     │
    │         │         │
    └────┬────┴─────────┘
         ▼
    Phase 7 (Polish)
```

### Within Each User Story

- 基础配置先于功能实现
- 迁移脚本按序号执行
- 测试在实现完成后执行

### Parallel Opportunities

- Phase 1 中的 T002, T003 可并行
- Phase 4 中的迁移脚本 T016-T022 可并行编写
- Phase 7 中的 T036, T037 可并行

---

## Parallel Example: User Story 2

```bash
# 并行创建所有迁移脚本
Task: "创建 db/migrations/002_create_prices_table.sql"
Task: "创建 db/migrations/003_create_klines_table.sql"
Task: "创建 db/migrations/004_create_indicators_table.sql"
Task: "创建 db/migrations/005_create_signals_table.sql"
Task: "创建 db/migrations/006_create_news_table.sql"
Task: "创建 db/migrations/007_create_word_freq_table.sql"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational
3. 完成 Phase 3: User Story 1 (一键启动)
4. **STOP and VALIDATE**: 验证 `./scripts/start.sh` 可正常启动
5. 此时可演示：开发环境一键启动

### Incremental Delivery

1. Setup + Foundational → 基础就绪
2. 添加 US1 → 测试启动流程 → MVP!
3. 添加 US2 → 测试数据写入 → 数据层完成
4. 添加 US3 → 测试 GraphQL → API 层完成
5. 添加 US4 → 测试时序优化 → 性能优化完成
6. 每个故事独立增加价值，不破坏已有功能

---

## Notes

- [P] 标记的任务可并行执行（不同文件，无依赖）
- [Story] 标签将任务映射到用户故事，便于追踪
- 每个用户故事可独立完成和测试
- 每完成一个任务后建议 commit
- 在任意 checkpoint 可停下来验证
