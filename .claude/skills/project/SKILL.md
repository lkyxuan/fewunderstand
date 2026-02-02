---
name: project
description: Use when managing GitHub Projects and Issues - view board, move status, create issues, sync from openspec. This is the unified project management skill.
---

# Project Management

## Overview

GitHub Projects + Issues 统一管理 skill，负责项目进度追踪和协调。

**与 openspec 的分工：**
- **project** - 项目管理（看板、Issue 状态、进度追踪）
- **openspec** - 技术设计（proposal、design、tasks）

**Announce at start:** "使用 project skill 管理 GitHub Projects。"

## 看板配置

**Project URL:** https://github.com/users/lkyxuan/projects/2

**状态列（8 列）：**

| 状态 | 含义 | 谁做 | 产出 |
|------|------|------|------|
| `问题` | 发现问题/提出需求 | 任何人 | Issue 描述 |
| `待定方案` | 需要人想解决思路 | 人 | 评论里写思路 |
| `待出设计` | 有思路了，需要详细设计 | AI (openspec) | proposal/design/tasks |
| `设计审核` | 设计完成，等待审核 | 人审 AI | 审核意见 |
| `开发中` | 按 tasks.md 开发 | AI/人 | 代码 + PR |
| `待测试` | 代码完成，等待测试 | 人/QA | 测试结果 |
| `待部署` | 测试通过，等待部署 | 运维/人 | 部署确认 |
| `Done` | 已部署上线 | - | openspec archive |

**辅助标签：** `阻塞`（任何阶段遇到问题时）

## 流程图

```
问题
 │
 ├─ 小改动 ──────────────────→ 开发中 → 待测试 → 待部署 → Done
 │
 └─ 大改动 → 待定方案 → 待出设计 → 设计审核 → 开发中 → 待测试 → 待部署 → Done
              (人想思路)  (AI出设计)  (人审核)
```

## 智能上下文检测

调用 `/project` 时，**先自动检测当前状态**：

### Step 1: 收集上下文

```bash
# 1. 当前分支
BRANCH=$(git branch --show-current)

# 2. 是否有未提交的代码
git status --porcelain

# 3. 最近的 commit
git log -1 --pretty="%h %s"

# 4. 查找相关的 Issues
gh issue list --state open --search "$BRANCH"

# 5. 看板状态
gh project item-list 2 --owner lkyxuan
```

### Step 2: 智能推荐

| 检测到的状态 | 推荐操作 |
|--------------|----------|
| 没有关联的 Issue | 创建新 Issue 或认领现有任务 |
| Issue 在 `问题` | 询问是大改动还是小改动 |
| Issue 在 `待定方案` | 等人写方案思路，或帮忙整理思路 |
| Issue 在 `待出设计` | 使用 openspec 出详细设计 |
| Issue 在 `设计审核` | 审核设计或开始开发 |
| Issue 在 `开发中` + 有新 commit | 推荐标记待测试 |
| Issue 在 `待测试` | 推荐测试或标记待部署 |
| Issue 在 `待部署` | 推荐使用 merge-pr 部署 |

### Step 3: 确认并执行

```
检测到：
- 当前分支: lkyxuan/add-news-crawler
- 相关 Issue: #27 "部署 RSSHub" [开发中]
- 状态: 有未提交的代码

推荐操作：
1. 继续开发
2. 标记待测试（代码完成）
3. 查看看板状态

请选择：
```

## 操作列表

### 1. status - 查看看板状态

```bash
# 查看所有 Issues
gh project item-list 2 --owner lkyxuan

# 按状态筛选
gh issue list --state open --label "问题"
gh issue list --state open --label "开发中"
gh issue list --state open --label "待测试"
```

### 2. move - 移动 Issue 状态

**使用标签系统：**

```bash
# 问题 → 待定方案（大改动，需要人想思路）
gh issue edit <N> --remove-label "问题" --add-label "待定方案"
gh issue comment <N> --body "大改动，需要先想解决思路"

# 问题 → 开发中（小改动，直接开发）
gh issue edit <N> --remove-label "问题" --add-label "开发中"
gh issue comment <N> --body "小改动，直接开发"

# 待定方案 → 待出设计（人写完思路后）
gh issue edit <N> --remove-label "待定方案" --add-label "待出设计"
gh issue comment <N> --body "方案思路已定，需要用 openspec 出详细设计"

# 待出设计 → 设计审核（openspec 设计完成后）
gh issue edit <N> --remove-label "待出设计" --add-label "设计审核"
gh issue comment <N> --body "设计完成，请审核：openspec/changes/<feature>/"

# 设计审核 → 开发中（审核通过）
gh issue edit <N> --remove-label "设计审核" --add-label "开发中"
gh issue comment <N> --body "设计审核通过，开始开发"

# 设计审核 → 待出设计（审核不通过，打回修改）
gh issue edit <N> --remove-label "设计审核" --add-label "待出设计"
gh issue comment <N> --body "设计需要修改：<原因>"

# 开发中 → 待测试（代码完成）
gh issue edit <N> --remove-label "开发中" --add-label "待测试"
gh issue comment <N> --body "代码完成，等待测试"

# 待测试 → 待部署（测试通过）
gh issue edit <N> --remove-label "待测试" --add-label "待部署"
gh issue comment <N> --body "测试通过，等待部署"

# 待部署 → Done（部署完成）
gh issue edit <N> --add-label "部署完成"
gh issue close <N> --comment "已部署完成"
```

### 3. create - 创建 Issue

```bash
gh issue create \
  --title "<标题>" \
  --body "$(cat <<'EOF'
## 问题描述
<描述问题或需求>

## 期望结果
<期望的解决效果>
EOF
)" \
  --label "问题"
```

### 4. claim - 认领 Issue

```bash
# 小改动：直接认领开发
gh issue edit <N> --add-assignee @me
gh issue edit <N> --remove-label "问题" --add-label "开发中"
gh issue comment <N> --body "已认领，小改动直接开发"

# 大改动：认领并进入方案阶段
gh issue edit <N> --add-assignee @me
gh issue edit <N> --remove-label "问题" --add-label "待定方案"
gh issue comment <N> --body "已认领，需要先想解决方案"
```

### 5. idea - 提交方案思路

人在 Issue 评论里写解决思路：

```bash
gh issue comment <N> --body "$(cat <<'EOF'
## 方案思路

### 解决方向
<高层次的解决思路，几句话描述>

### 大致步骤
1. <步骤1>
2. <步骤2>
3. <步骤3>

---
思路确定后，请用 openspec 出详细设计
EOF
)"

# 然后移动到待出设计
gh issue edit <N> --remove-label "待定方案" --add-label "待出设计"
```

### 6. design - 提交 openspec 设计

用 openspec 出详细设计后：

```bash
gh issue edit <N> --remove-label "待出设计" --add-label "设计审核"
gh issue comment <N> --body "$(cat <<'EOF'
## OpenSpec 设计完成

设计文档位置：`openspec/changes/<feature>/`

- proposal.md - 变更说明
- design.md - 技术设计
- tasks.md - 实现任务

请审核设计方案。
EOF
)"
```

### 7. sync - 从 openspec 同步任务

从 `openspec/changes/<feature>/tasks.md` 创建子 Issues：

```bash
# 创建子 Issue
gh issue create \
  --title "<任务标题>" \
  --body "$(cat <<'EOF'
## 来源
openspec/changes/<feature>/tasks.md

## 任务描述
<从 tasks.md 提取>

## 父 Issue
#<PARENT_ISSUE_NUMBER>
EOF
)" \
  --label "问题"
```

### 8. link - PR 关联 Issue

```bash
# 在 PR 描述中添加（自动关闭）
Closes #<ISSUE_NUMBER>

# 或手动关联
gh pr edit <PR_NUMBER> --body "Closes #<ISSUE_NUMBER>"
```

### 9. block / unblock - 阻塞管理

```bash
# 标记阻塞
gh issue edit <N> --add-label "阻塞"
gh issue comment <N> --body "阻塞原因：<问题描述>"

# 解除阻塞
gh issue edit <N> --remove-label "阻塞"
gh issue comment <N> --body "阻塞已解除：<解决方案>"
```

## 交互流程

### 默认流程（智能模式）

用户调用 `/project` 时：

1. **自动检测上下文**
2. **显示看板概览 + 推荐操作**
3. **用户选择或指定其他操作**
4. **执行并确认**

### 直接模式

用户可以直接指定操作：

- `/project status` - 查看看板
- `/project create "标题"` - 创建 Issue
- `/project claim 42` - 认领 Issue #42
- `/project move 42 开发中` - 移动状态
- `/project idea 42` - 提交方案思路到 #42
- `/project design 42` - 提交 openspec 设计到 #42
- `/project sync add-news-crawler` - 同步 openspec 任务
- `/project link 42` - 关联当前 PR 到 #42
- `/project block 42` - 标记阻塞
- `/project unblock 42` - 解除阻塞

## 与 openspec 协作

**典型工作流（大改动）：**

```
1. 发现问题/需求
       ↓
2. /project create "问题描述"     ← 创建 Issue（问题）
       ↓
3. /project move <N> 待定方案     ← 大改动需要方案
       ↓
4. /project idea <N>              ← 人写方案思路
       ↓
5. /project move <N> 待出设计     ← 需要详细设计
       ↓
6. openspec proposal/design/tasks ← AI 用 openspec 出详细设计
       ↓
7. /project design <N>            ← 提交设计到 Issue
       ↓
8. 审核通过
   /project move <N> 开发中       ← 开始开发
       ↓
9. /push-to-dev                   ← 自动标记待测试
       ↓
10. 测试通过
    /project move <N> 待部署      ← 等待部署
       ↓
11. /merge-pr                     ← 自动关闭 Issue + openspec archive
```

**小改动流程：**

```
/project create → /project claim（直接开发）→ /push-to-dev → 测试 → /merge-pr
```

## 自动化触发

| 操作 | 状态变更 |
|------|----------|
| `/push-to-dev` | → `待测试` |
| 手动确认测试通过 | → `待部署` |
| `/merge-pr` | → `Done` + `openspec archive` |

## Quick Reference

| 操作 | 命令 |
|------|------|
| 看板状态 | `gh project item-list 2 --owner lkyxuan` |
| 按标签查看 | `gh issue list --state open --label "<状态>"` |
| 创建 Issue | `gh issue create --title "..." --label "问题"` |
| 认领 | `gh issue edit <N> --add-assignee @me` |
| 移动状态 | `gh issue edit <N> --remove-label "A" --add-label "B"` |
| 添加评论 | `gh issue comment <N> --body "..."` |
| 关闭 Issue | `gh issue close <N> --comment "..."` |

## 标签列表

**主流程（8 个，互斥）：**
- `问题` - 紫色
- `待定方案` - 橙色
- `待出设计` - 浅蓝
- `设计审核` - 蓝色
- `开发中` - 黄色
- `待测试` - 浅绿
- `待部署` - 绿色
- `部署完成` - 深绿

**辅助（可叠加）：**
- `阻塞` - 红色

## Red Flags

**Never:**
- 大改动跳过方案直接开发（可能方向错误）
- 忘记更新状态（其他人不知道进度）
- 同一任务多人同时做（先检查看板）
- 设计没审核就开始写代码

**Always:**
- 开始前检查看板，避免重复
- 状态变更时添加评论说明
- 大功能：人出思路 → AI 出设计 → 人审核
- 小改动可以跳过方案阶段直接开发
