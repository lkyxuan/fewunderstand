# Spec 规格文档

**改代码前必须先读 spec！**

功能规格文档在 `openspec/specs/` 目录：

```
openspec/specs/
├── frontend-dashboard/spec.md   ← 前端仪表盘
├── infrastructure/spec.md       ← 基础设施
├── kline-data-collection/spec.md ← K线数据采集
├── news-crawler/spec.md         ← 新闻爬虫
└── price-signals/spec.md        ← 价格信号
```

**AI 改代码前：**
1. `ls openspec/specs/` 查看有哪些功能
2. `cat openspec/specs/<功能>/spec.md` 阅读相关规格
3. 按 spec 要求实现

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

> **多人协作必须通过 GitHub Issues + Projects 协调，避免重复开发。**
>
> **详细操作流程见 `/project` skill。**

### 核心流程

```
1. 创建 Issue（提案）
       ↓
2. /project design → AI 出技术方案
       ↓
3. 方案审核（人审 AI 方案，或 AI 审人方案）
       ↓
4. /project split → 拆成子 Issues
       ↓
5. 认领子 Issue → /project move 正在工作
       ↓
6. 开发 → /push-to-dev（创建 PR，Closes #子Issue）
       ↓
7. Review → /merge-pr → 子 Issue 自动关闭
       ↓
8. 所有子 Issue 完成 → 父 Issue 完成
```

### 关键原则

1. **Issue 任何人都可以提**（用户、开发者、AI）
2. **方案先行**：大改动必须先出方案再动手
3. **交叉审核**：AI 出方案人审核，人出方案 AI 审核
4. **小改动可跳过方案**：直接 `提案` → `正在工作`

### Project 看板状态

**主流程（7 列）：** `提案` → `待出方案` → `方案审核` → `正在工作` → `代码完成` → `测试完成` → `Done`

**看板地址**：https://github.com/users/lkyxuan/projects/2

### 开始任务前（必做）

1. 检查是否已有相关 Issue：`gh issue list --state open --search "关键词"`
2. 有 Issue → 认领或协调；没有 → 创建新 Issue
3. 大改动 → `/project design` 出方案；小改动 → 直接认领

### 相关 Skills

- `/project` - **统一入口**（init、status、move、design、split、link）
- `/push-to-dev` - 推送代码并创建 PR（关联 Issue）
- `/merge-pr` - 合并 PR（自动关闭 Issue）

<!-- MANUAL ADDITIONS END -->
