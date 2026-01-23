---
name: issue
description: Use when managing GitHub Issues - view, claim, update status, or create issues. This is the core skill for Issue-driven development.
---

# Issue Management

## Overview

GitHub Issues 的核心管理 skill，支持查看、认领、更新状态、创建等所有操作。

**这是 Issue-Driven Development 的核心 skill，其他 skills 调用此 skill 来更新 Issue 状态。**

**Announce at start:** "使用 issue skill 管理 GitHub Issues。"

## 核心流程

```
提 Issue → 出方案 → 审核方案 → 认领开发 → 代码完成 → 测试 → 部署
   ↑         ↑         ↑
 任何人    AI或人    交叉审核
```

**关键原则：**
- Issue 任何人都可以提（用户、开发者、AI）
- 方案先行：先想清楚再动手
- 交叉审核：AI 出方案人审核，人出方案 AI 审核

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
| 有 `提案` 状态的相关 Issue | 推荐出方案（→ 待出方案） |
| 有 `待出方案` 的 Issue | 推荐提交方案（→ 方案审核） |
| 有 `方案审核` 的 Issue | 推荐审核方案或认领开发（→ 正在工作） |
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

**主流程状态（互斥，只能有一个）：**
| 标签 | 说明 | 颜色 |
|------|------|------|
| `提案` | 新任务/想法，等待处理 | 紫色 |
| `待出方案` | 需要先出技术方案 | 橙色 |
| `方案审核` | 方案已出，等待审核 | 蓝色 |
| `正在工作` | 方案已定，正在开发 | 黄色 |
| `代码完成` | 代码开发完成 | 浅绿 |
| `测试完成` | 测试验证通过 | 绿色 |
| `部署完成` | 已部署到生产 | 深绿 |

**辅助状态（可叠加）：**
| 标签 | 说明 | 颜色 |
|------|------|------|
| `阻塞` | 当前阶段卡住了，需要讨论或验证 | 红色 |

**完整状态流转：**
```
[提案] → [待出方案] → [方案审核] → [正在工作] → [代码完成] → [测试完成] → [部署完成] → Closed
 创建     分配出方案    交叉审核      认领开发      push-to-dev   测试通过      merge-pr
```

**简化流程（小改动可跳过方案阶段）：**
```
[提案] → [正在工作] → [代码完成] → [测试完成] → [部署完成] → Closed
```

**遇到问题时：**
```
任何阶段 + [阻塞] → 在 Issue 评论说明问题 → 解决后移除 [阻塞] → 继续原流程
```

## 操作列表

当用户调用 `/issue` 时，询问要执行哪个操作：

### 1. 查看 Issues

```bash
# 查看新提案
gh issue list --state open --label "提案"

# 查看待出方案
gh issue list --state open --label "待出方案"

# 查看待审核方案
gh issue list --state open --label "方案审核"

# 查看正在进行的任务
gh issue list --state open --label "正在工作"

# 查看待测试的任务
gh issue list --state open --label "代码完成"

# 查看待部署的任务
gh issue list --state open --label "测试完成"

# 查看被阻塞的任务
gh issue list --state open --label "阻塞"

# 查看所有开放的 Issues
gh issue list --state open

# 搜索特定关键词
gh issue list --state open --search "关键词"
```

### 2. 方案流程

**分配出方案**（`提案` → `待出方案`）：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "提案" --add-label "待出方案"
gh issue comment <ISSUE_NUMBER> --body "需要先出技术方案，由 @xxx 负责"
```

**提交方案**（`待出方案` → `方案审核`）：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "待出方案" --add-label "方案审核"
gh issue comment <ISSUE_NUMBER> --body "$(cat <<'EOF'
## 技术方案

### 实现思路
<描述>

### 涉及文件
<文件列表>

### 风险点
<可能的问题>

---
请审核此方案 @xxx
EOF
)"
```

**审核通过，开始开发**（`方案审核` → `正在工作`）：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "方案审核" --add-label "正在工作"
gh issue comment <ISSUE_NUMBER> --body "方案审核通过，开始开发"
```

**审核不通过，打回修改**（`方案审核` → `待出方案`）：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "方案审核" --add-label "待出方案"
gh issue comment <ISSUE_NUMBER> --body "方案需要修改：<原因>"
```

### 3. 直接认领（跳过方案，适用于小改动）

从 `提案` → `正在工作`：

```bash
gh issue edit <ISSUE_NUMBER> --remove-label "提案" --add-label "正在工作"
gh issue comment <ISSUE_NUMBER> --body "小改动，直接开始开发"
gh issue edit <ISSUE_NUMBER> --add-assignee @me
```

### 4. 开发阶段状态更新

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

### 5. 阻塞处理

**标记阻塞**（任何阶段遇到问题时）：
```bash
gh issue edit <ISSUE_NUMBER> --add-label "阻塞"
gh issue comment <ISSUE_NUMBER> --body "阻塞原因：<问题描述>"
```

**解除阻塞**（问题解决后）：
```bash
gh issue edit <ISSUE_NUMBER> --remove-label "阻塞"
gh issue comment <ISSUE_NUMBER> --body "阻塞已解除：<解决方案>"
```

### 6. 创建 Issue

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

### 7. 关闭 Issue

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
| 出方案 | 提案 → 待出方案 |
| 提交方案 | 待出方案 → 方案审核（在评论中写方案） |
| 审核通过 | 方案审核 → 正在工作 |
| 审核打回 | 方案审核 → 待出方案 |
| 认领 | 提案 → 正在工作（跳过方案，适用于小改动） |
| 代码完成 | 正在工作 → 代码完成 |
| 测试完成 | 代码完成 → 测试完成 |
| 部署完成 | 测试完成 → 部署完成 + 关闭 |
| 阻塞 | 添加阻塞标签（任何阶段可用） |
| 解除阻塞 | 移除阻塞标签 |
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
| 查看新提案 | `gh issue list --state open --label "提案"` |
| 查看待出方案 | `gh issue list --state open --label "待出方案"` |
| 查看方案审核 | `gh issue list --state open --label "方案审核"` |
| 查看进行中 | `gh issue list --state open --label "正在工作"` |
| 查看被阻塞 | `gh issue list --state open --label "阻塞"` |
| 分配出方案 | `gh issue edit <N> --remove-label "提案" --add-label "待出方案"` |
| 提交方案 | `gh issue edit <N> --remove-label "待出方案" --add-label "方案审核"` |
| 审核通过 | `gh issue edit <N> --remove-label "方案审核" --add-label "正在工作"` |
| 直接认领 | `gh issue edit <N> --remove-label "提案" --add-label "正在工作"` |
| 标记代码完成 | `gh issue edit <N> --remove-label "正在工作" --add-label "代码完成"` |
| 标记测试完成 | `gh issue edit <N> --remove-label "代码完成" --add-label "测试完成"` |
| 标记部署完成 | `gh issue edit <N> --add-label "部署完成" && gh issue close <N>` |
| 标记阻塞 | `gh issue edit <N> --add-label "阻塞"` |
| 解除阻塞 | `gh issue edit <N> --remove-label "阻塞"` |
| 创建 Issue | `gh issue create --title "..." --label "提案"` |

## Red Flags

**Never:**
- 大改动跳过方案直接开发（可能方向错误）
- 忘记更新状态（其他人不知道进度）
- 直接关闭没有完成的 Issue
- 方案没审核就开始写代码

**Always:**
- 认领前检查是否已有人在做
- 方案写在 Issue 评论里，方便追溯
- 状态变更时添加评论说明
- 关闭时说明原因或引用 PR
- AI 出方案人审核，人出方案 AI 审核（交叉审核）
