# Infrastructure Spec Delta

## ADDED Requirements

### Requirement: Docker Compose 服务编排
系统 SHALL 通过单一 `docker-compose.yml` 文件定义所有服务。

#### Scenario: 一键启动
- **WHEN** 用户执行 `docker compose up`
- **THEN** PostgreSQL、TimescaleDB、Hasura 服务启动
- **AND** 服务之间网络互通

#### Scenario: 服务健康检查
- **WHEN** 所有服务启动完成
- **THEN** Hasura Console 可通过 `http://localhost:8080` 访问
- **AND** PostgreSQL 可通过 `localhost:5432` 连接

### Requirement: TimescaleDB 时序数据库
系统 SHALL 使用 TimescaleDB 扩展来优化时序数据存储和查询。

#### Scenario: Hypertable 创建
- **WHEN** 数据库初始化
- **THEN** `prices` 表被创建为 hypertable
- **AND** 按 `time` 字段自动分区

#### Scenario: 数据保留策略
- **WHEN** 配置数据保留策略
- **THEN** 超过保留期的数据自动清理
- **AND** 保留期可通过环境变量配置

### Requirement: Hasura GraphQL 引擎
系统 SHALL 使用 Hasura 自动生成 GraphQL API。

#### Scenario: 表自动追踪
- **WHEN** 数据库表结构初始化完成
- **THEN** Hasura 自动 track 所有业务表
- **AND** 生成对应的 Query、Mutation、Subscription

#### Scenario: 实时订阅
- **WHEN** 数据库表有新数据插入
- **THEN** GraphQL Subscription 能实时推送变更

### Requirement: 爬虫运行环境
系统 SHALL 支持本地 Python 运行爬虫任务。

#### Scenario: 本地运行
- **WHEN** 用户执行 `python crawlers/main.py`
- **THEN** APScheduler 启动并调度所有爬虫任务
- **AND** 爬虫连接到 Docker 中的 PostgreSQL
