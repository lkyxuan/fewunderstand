<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# FUCE Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-21

## Active Technologies

- SQL (PostgreSQL 15), YAML (Docker Compose) + Docker, Docker Compose, PostgreSQL 15, TimescaleDB 2.x, Hasura GraphQL Engine 2.x (001-infrastructure)

## Project Structure

```text
src/
tests/
```

## Commands

# Add commands for SQL (PostgreSQL 15), YAML (Docker Compose)

## Code Style

SQL (PostgreSQL 15), YAML (Docker Compose): Follow standard conventions

## Recent Changes

- 001-infrastructure: Added SQL (PostgreSQL 15), YAML (Docker Compose) + Docker, Docker Compose, PostgreSQL 15, TimescaleDB 2.x, Hasura GraphQL Engine 2.x

<!-- MANUAL ADDITIONS START -->

## 核心架构

```
Python 爬虫 → PostgreSQL → Hasura (GraphQL) → TypeScript 前端
```

### 架构原则

1. **数据库即 API**：所有程序只需读写数据库，Hasura 自动生成 GraphQL
2. **语言无关**：数据处理可用任意语言（Python/TypeScript/Go），通过数据库解耦
3. **简单优先**：本地自托管场景，不做复杂 ML 计算

### 模块分工

| 模块 | 语言 | 职责 |
|------|------|------|
| 爬虫 | Python | 采集原始数据 → 写入 prices 表 |
| 计算 | Python/TS | 指标计算 → 写入 indicators 表 |
| 检测 | Python/TS | 信号检测 → 写入 signals 表 |
| 前端 | TypeScript | 读取 GraphQL → 展示 |

### 服务器测试环境

- IP: 46.224.5.136
- 用户: root
- 服务: docker compose (postgres + hasura)
- 爬虫: /root/fuce/crawlers/

### 常用命令

```bash
# 启动服务
ssh root@46.224.5.136 "cd /root/fuce && docker compose up -d"

# 查看爬虫日志
ssh root@46.224.5.136 "docker compose logs -f binance-price"

# 查询数据
ssh root@46.224.5.136 "docker exec fuce-postgres psql -U fuce -d fuce -c 'SELECT * FROM prices ORDER BY time DESC LIMIT 5;'"
```

<!-- MANUAL ADDITIONS END -->
