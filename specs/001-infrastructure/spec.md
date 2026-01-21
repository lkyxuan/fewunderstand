# Feature Specification: 基础架构

**Feature Branch**: `001-infrastructure`
**Created**: 2026-01-21
**Status**: Draft
**Input**: 基础架构：Docker Compose 一键启动环境，包含 PostgreSQL + TimescaleDB + Hasura，支持数据写入和 GraphQL 读取

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 一键启动开发环境 (Priority: P1)

作为开发者，我希望运行一条命令就能启动完整的开发环境，包括数据库和 API 服务，这样我可以立即开始开发和测试功能。

**Why this priority**: 这是所有后续功能的基础，没有运行环境就无法开发任何功能。

**Independent Test**: 在一台全新的机器上（只安装了 Docker），运行启动命令后，能成功访问数据库和 GraphQL API。

**Acceptance Scenarios**:

1. **Given** 用户已安装 Docker 和 Docker Compose, **When** 用户运行启动命令, **Then** 所有服务在 2 分钟内启动完成并处于健康状态
2. **Given** 所有服务已启动, **When** 用户访问 GraphQL 控制台, **Then** 能看到 Hasura 的 GraphQL Playground 界面
3. **Given** 所有服务已启动, **When** 用户运行停止命令, **Then** 所有服务优雅关闭，数据保留在本地卷中

---

### User Story 2 - 数据写入能力 (Priority: P1)

作为后台程序，我需要能够将计算结果（价格、指标、信号、新闻）写入数据库，这样前端才能读取和展示这些数据。

**Why this priority**: 与 P1 并列，因为数据写入是整个系统的数据来源，没有数据就没有内容可展示。

**Independent Test**: 使用数据库客户端连接，成功执行 INSERT 语句，数据正确持久化。

**Acceptance Scenarios**:

1. **Given** 数据库服务已启动, **When** 程序插入一条价格记录, **Then** 记录成功写入并可查询
2. **Given** 数据库服务已启动, **When** 程序批量插入 1000 条记录, **Then** 所有记录在 5 秒内写入完成
3. **Given** 数据已写入, **When** 服务重启后, **Then** 数据仍然存在（持久化）

---

### User Story 3 - GraphQL API 自动暴露 (Priority: P1)

作为前端开发者，我需要通过 GraphQL API 读取数据库中的数据，这样我可以构建用户界面来展示信息。

**Why this priority**: 与 P1 并列，因为 API 是前端获取数据的唯一途径。

**Independent Test**: 使用 GraphQL Playground 执行查询，能返回数据库中的数据。

**Acceptance Scenarios**:

1. **Given** 数据库中有数据, **When** 前端执行 GraphQL 查询, **Then** 返回对应的数据
2. **Given** 数据库中有数据, **When** 前端订阅数据变更 (Subscription), **Then** 新数据写入时实时收到通知
3. **Given** GraphQL API 运行中, **When** 数据库表结构变更, **Then** API 自动更新，无需手动配置

---

### User Story 4 - 时序数据优化 (Priority: P2)

作为系统运维者，我需要数据库能高效存储和查询时序数据（价格、K线），并自动清理过期数据，这样本地存储空间可控。

**Why this priority**: 优化性能和存储，在基础功能之后实现。

**Independent Test**: 插入大量时序数据后，查询最近时间段的数据仍然快速响应。

**Acceptance Scenarios**:

1. **Given** 数据库存有 100 万条时序记录, **When** 查询最近 1 小时的数据, **Then** 查询在 1 秒内返回结果
2. **Given** 配置了 30 天的数据保留策略, **When** 有超过 30 天的数据, **Then** 系统自动删除过期数据
3. **Given** 数据保留策略执行后, **When** 检查存储空间, **Then** 过期数据占用的空间已释放

---

### Edge Cases

- 启动时端口被占用怎么办？ → 服务启动失败并显示清晰的错误信息，提示哪个端口被占用
- 数据库连接断开后如何恢复？ → 服务自动重试连接，最多重试 5 次，每次间隔递增
- 磁盘空间不足时如何处理？ → 写入操作失败并记录错误日志，不影响读取操作

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统 MUST 通过单条命令启动所有服务（数据库、API、管理界面）
- **FR-002**: 系统 MUST 通过单条命令停止所有服务并保留数据
- **FR-003**: 系统 MUST 提供 GraphQL API 端点供前端查询数据
- **FR-004**: 系统 MUST 支持 GraphQL Subscriptions 实现实时数据推送
- **FR-005**: 系统 MUST 在数据库表结构变更后自动更新 API（无需手动配置）
- **FR-006**: 系统 MUST 支持时序数据的高效存储和查询
- **FR-007**: 系统 MUST 支持配置数据保留期限（7-30 天可配置）
- **FR-008**: 系统 MUST 自动清理超过保留期限的数据
- **FR-009**: 系统 MUST 提供健康检查端点，报告各服务状态
- **FR-010**: 系统 MUST 支持跨平台运行（Windows/Mac/Linux），至少提供 `docker compose up -d` 的一键启动路径
- **FR-011**: 系统 MUST 使用环境变量管理配置，不硬编码敏感信息
- **FR-012**: 系统 MUST 默认仅绑定到 localhost（127.0.0.1），避免对外暴露管理端口

### Key Entities

- **Service**: 系统中的一个独立服务（数据库、API 等），包含名称、状态、健康检查端点
- **Configuration**: 系统配置项，包含数据保留期限、端口映射、服务连接信息
- **HealthStatus**: 服务健康状态，包含服务名、状态（healthy/unhealthy）、最后检查时间

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 新开发者在 5 分钟内完成环境搭建（从 git clone 到服务可用）
- **SC-002**: 所有服务启动时间不超过 2 分钟（冷启动，不含镜像下载）
- **SC-003**: 单条记录写入延迟小于 100 毫秒
- **SC-004**: GraphQL 查询响应时间小于 500 毫秒（1000 条记录以内）
- **SC-005**: 实时订阅延迟小于 1 秒（从数据写入到前端收到通知）
- **SC-006**: 100 万条时序记录查询最近 1 小时数据，响应时间小于 1 秒
- **SC-007**: 系统在 Windows/Mac/Linux 上均可正常运行

## Assumptions

- 用户已安装 Docker 和 Docker Compose
- 用户机器至少有 4GB 可用内存
- 用户机器至少有 10GB 可用磁盘空间
- 用户有基本的命令行操作能力
