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

## 开发流程规范（强制执行）

> **重要**: 多人协作环境，必须严格遵守以下流程，禁止直接在服务器上修改代码。

### 前端开发流程

```
本地修改 → rsync 同步 → 服务器构建 → 浏览器测试 → 本地 git 提交
```

#### 1. 本地修改代码

所有代码修改必须在本地进行：
- 本地路径: `/Users/qiji/conductor/workspaces/fewunderstand-v1/dakar/frontend/`
- 使用 Edit/Write 工具修改文件

#### 2. 同步到服务器

```bash
rsync -avz --exclude 'node_modules' --exclude '.next' \
  /Users/qiji/conductor/workspaces/fewunderstand-v1/dakar/frontend/ \
  root@46.224.5.136:/root/fuce/frontend/
```

#### 3. 服务器构建和重启

```bash
# 构建
ssh root@46.224.5.136 "cd /root/fuce/frontend && npm run build"

# 重启（先停后启）
ssh root@46.224.5.136 "pkill -f 'next-server' || true"
ssh root@46.224.5.136 "cd /root/fuce/frontend && PORT=18080 npm start &"
```

#### 4. 浏览器测试

- 前端地址: http://46.224.5.136:18080
- GraphQL: http://46.224.5.136:8080/v1/graphql

#### 5. 本地 Git 提交

测试通过后，在本地提交代码：
```bash
git add <files>
git commit -m "feat/fix: 描述"
git push origin <branch>
```

### 禁止事项

- **禁止**直接在服务器 `/root/fuce/frontend/` 目录修改代码
- **禁止**在服务器上执行 git 操作
- **禁止**跳过 rsync 直接在服务器编辑文件

### 服务器目录说明

| 目录 | 用途 | 可否修改 |
|------|------|----------|
| `/root/fuce/frontend/` | 前端运行目录 | 仅通过 rsync 同步 |
| `/root/fuce/crawlers/` | 爬虫脚本 | 仅通过 rsync 同步 |
| `/root/fuce/docker-compose.yml` | 服务配置 | 仅通过 rsync 同步 |

## Issue-Driven Development（强制执行）

> **多人协作必须通过 GitHub Issues 协调，避免重复开发。**
>
> **详细操作流程见 `/issue` skill。**

### 核心流程

```
提 Issue → 出方案 → 审核方案 → 认领开发 → 代码完成 → 测试 → 部署
   ↑         ↑         ↑
 任何人    AI或人    交叉审核
```

### 关键原则

1. **Issue 任何人都可以提**（用户、开发者、AI）
2. **方案先行**：大改动必须先出方案再动手
3. **交叉审核**：AI 出方案人审核，人出方案 AI 审核
4. **小改动可跳过方案**：直接 `提案` → `正在工作`

### 标签体系

**主流程（互斥）：** `提案` → `待出方案` → `方案审核` → `正在工作` → `代码完成` → `测试完成` → `部署完成`

**辅助（可叠加）：** `阻塞`（任何阶段遇到问题时）

### 开始任务前（必做）

1. 检查是否已有相关 Issue：`gh issue list --state open --search "关键词"`
2. 有 Issue → 认领或协调；没有 → 创建新 Issue
3. 大改动 → 先出方案；小改动 → 直接认领

### 相关 Skills

- `/issue` - Issue 管理（查看、认领、更新状态）
- `/push-to-dev` - 推送代码并自动标记 `代码完成`
- `/merge-pr` - 合并 PR 并自动标记 `部署完成`

<!-- MANUAL ADDITIONS END -->
