---
name: issue
description: Use when managing GitHub Issues - view, claim, update status, or create issues. This is the core skill for Issue-driven development.
---

# Issue Management

## Overview

GitHub Issues 的核心管理 skill，支持查看、认领、更新状态、创建等所有操作。

**这是 Issue-Driven Development 的核心 skill，其他 skills 调用此 skill 来更新 Issue 状态。**

**Announce at start:** "使用 issue skill 管理 GitHub Issues。"

## 智能上下文检测

调用 `/issue` 时，**先自动检测当前状态**，然后推荐操作：

### Step 1: 收集上下文

```bash
# 1. 当前分支
BRANCH=$(git branch --show-current)

# 2. 是否有未提交的代码
git status --porcelain

# 3. 最近的 commit
git log -1 --pretty="%h %s"

# 4. 查找相关的 Issues（根据分支名或最近 commit 搜索）
gh issue list --state open --search "$BRANCH"
```

### Step 2: 智能推荐

根据检测结果推荐操作：

| 检测到的状态 | 推荐操作 |
|--------------|----------|
| 没有关联的 Issue | 询问是否创建新 Issue 或认领现有任务 |
| 有 `提案` 状态的相关 Issue | 推荐认领（→ 正在工作） |
| 有 `正在工作` 的 Issue + 有新 commit | 推荐标记代码完成（或继续开发） |
| 有 `代码完成` 的 Issue | 推荐标记测试完成（或报告问题） |
| 有 `测试完成` 的 Issue | 推荐使用 merge-pr 部署 |

### Step 3: 确认并执行

向用户展示检测结果和推荐操作：

```
检测到：
- 当前分支: lkyxuan/add-news-crawler
- 相关 Issue: #27 "部署 RSSHub 自托管新闻爬虫" [代码完成]
- 状态: 有未提交的代码

推荐操作：
1. 继续开发（保持现状）
2. 标记测试完成（如果测试已通过）
3. 查看 Issue 详情

请选择操作：
```

## 中文标签体系

**基础状态（互斥）：**
| 标签 | 说明 | 颜色 |
|------|------|------|
| `提案` | 新任务/想法，等待认领 | 紫色 |
| `正在工作` | 有人正在开发 | 黄色 |
| `验证` | 需要验证或测试 | 蓝色 |
| `讨论` | 需要讨论或澄清 | 灰色 |

**开发阶段（里程碑）：**
| 标签 | 说明 | 颜色 |
|------|------|------|
| `代码完成` | 代码开发完成 | 浅绿 |
| `测试完成` | 测试验证通过 | 绿色 |
| `部署完成` | 已部署到生产 | 深绿 |

**状态流转：**
```
[提案] → [正在工作] → [代码完成] → [测试完成] → [部署完成] → Closed
 创建      认领         push-to-dev   测试通过     merge-pr
```

## 操作列表

当用户调用 `/issue` 时，询问要执行哪个操作：

### 1. 查看 Issues

```bash
# 查看待认领的任务
gh issue list --state open --label "提案"

# 查看正在进行的任务
gh issue list --state open --label "正在工作"

# 查看待测试的任务
gh issue list --state open --label "代码完成"

# 查看待部署的任务
gh issue list --state open --label "测试完成"

# 查看所有开放的 Issues
gh issue list --state open

# 搜索特定关键词
gh issue list --state open --search "关键词"
```

### 2. 认领任务

从 `提案` → `正在工作`：

```bash
# 1. 移除 提案，添加 正在工作
gh issue edit <ISSUE_NUMBER> --remove-label "提案" --add-label "正在工作"

# 2. 添加评论
gh issue comment <ISSUE_NUMBER> --body "开始开发此任务"

# 3. （可选）分配给自己
gh issue edit <ISSUE_NUMBER> --add-assignee @me
```

### 3. 更新状态

**标记代码完成**（由 push-to-dev 调用）：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "正在工作" --add-label "代码完成"
gh issue comment <ISSUE_NUMBER> --body "代码完成，已合并到 dev (commit <HASH>)，等待测试"
```

**标记测试完成**：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "代码完成" --add-label "测试完成"
gh issue comment <ISSUE_NUMBER> --body "测试验证通过，等待部署"
```

**标记部署完成并关闭**（由 merge-pr 调用）：
```bash
gh issue edit <ISSUE_NUMBER> --add-label "部署完成"
gh issue close <ISSUE_NUMBER> --comment "已部署，完成于 PR #<PR_NUMBER>"
```

**标记需要讨论**：
```bash
gh issue edit <ISSUE_NUMBER> --add-label "讨论"
gh issue comment <ISSUE_NUMBER> --body "需要讨论：<问题描述>"
```

**标记需要验证**：
```bash
gh issue edit <ISSUE_NUMBER> --add-label "验证"
gh issue comment <ISSUE_NUMBER> --body "需要验证：<验证内容>"
```

### 4. 创建 Issue

```bash
gh issue create \
  --title "<标题>" \
  --body "$(cat <<'EOF'
## 任务描述
<描述>

## 验证标准
<如何验证完成>
EOF
)" \
  --label "提案"
```

### 5. 关闭 Issue

```bash
gh issue close <ISSUE_NUMBER> --comment "<关闭原因>"
```

## 交互流程

当用户调用 `/issue` 时：

### 默认流程（智能模式）

1. **自动检测上下文**（见上方"智能上下文检测"）
2. **展示检测结果和推荐操作**
3. **用户选择或指定其他操作**
4. **执行并确认**

### 指定操作（直接模式）

用户可以直接指定操作，跳过智能检测：

- `/issue 查看` - 直接查看 Issues
- `/issue 认领 27` - 直接认领 Issue #27
- `/issue 代码完成 27` - 直接标记 #27 为代码完成
- `/issue 测试完成 27` - 直接标记 #27 为测试完成
- `/issue 创建 "标题"` - 直接创建新 Issue

### 支持的操作

| 操作 | 说明 |
|------|------|
| 查看 | 列出指定状态的 Issues |
| 认领 | 提案 → 正在工作 |
| 代码完成 | 正在工作 → 代码完成 |
| 测试完成 | 代码完成 → 测试完成 |
| 部署完成 | 测试完成 → 部署完成 + 关闭 |
| 讨论 | 添加讨论标签 |
| 验证 | 添加验证标签 |
| 创建 | 创建新 Issue（提案状态） |
| 关闭 | 关闭 Issue |

## 供其他 Skills 调用

### push-to-dev 调用

在 push-to-dev 的 Step 6 中：
```
调用 issue skill 的"标记代码完成"操作：
- 查找 正在工作 状态的相关 Issues
- 更新为 代码完成
- 添加 commit 信息评论
```

### merge-pr 调用

在 merge-pr 的 Step 6 中：
```
调用 issue skill 的"标记部署完成并关闭"操作：
- 查找 代码完成 或 测试完成 状态的相关 Issues
- 添加 部署完成 标签
- 关闭 Issue 并添加 PR 引用评论
```

## Quick Reference

| 操作 | 命令 |
|------|------|
| 查看待认领 | `gh issue list --state open --label "提案"` |
| 查看进行中 | `gh issue list --state open --label "正在工作"` |
| 认领任务 | `gh issue edit <N> --remove-label "提案" --add-label "正在工作"` |
| 标记代码完成 | `gh issue edit <N> --remove-label "正在工作" --add-label "代码完成"` |
| 标记测试完成 | `gh issue edit <N> --remove-label "代码完成" --add-label "测试完成"` |
| 标记部署完成 | `gh issue edit <N> --add-label "部署完成" && gh issue close <N>` |
| 创建 Issue | `gh issue create --title "..." --label "提案"` |

## Red Flags

**Never:**
- 跳过认领直接开发（会导致重复工作）
- 忘记更新状态（其他人不知道进度）
- 直接关闭没有完成的 Issue

**Always:**
- 认领前检查是否已有人在做
- 状态变更时添加评论说明
- 关闭时说明原因或引用 PR
