---
name: push-to-dev
description: Use when you need to push current branch and merge to dev - handles auto-commit, branch renaming, push, merge, close issues, and cleanup. Supports Issue-driven development.
---

# Push to Dev

## Overview

自动提交、重命名分支、推送到远程、合并到 dev 分支、关闭相关 Issues 的完整流程。

**Core principle:** 自动提交 → 根据 commit 重命名分支 → 推送 → 合并到 dev → 关闭 Issues → 返回原分支

**与 merge-pr 的区别**：
- push-to-dev：直接合并，快速迭代，无需 PR
- merge-pr：通过 PR 合并，有 review 流程

**Announce at start:** "使用 push-to-dev skill 来推送并合并到 dev 分支。"

## The Process

### Step 1: 检查当前分支

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"
```

**检查是否在 dev 或 main 分支:**

如果 `$CURRENT_BRANCH` 是 `dev` 或 `main`：
```
⚠️ 当前在 <branch> 分支，不应直接在此分支开发。
请切换到功能分支后再执行。
```

停止。

### Step 2: 检查并自动提交

```bash
git status --porcelain
```

**如果有未提交的更改，自动提交：**

1. 查看变更内容：
```bash
git diff --stat
git diff
```

2. 分析变更，生成合适的 commit 消息（遵循仓库的 commit 风格）

3. 添加并提交：
```bash
git add <相关文件>
git commit -m "<type>: <描述>

<详细说明如有必要>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**如果没有更改也没有新 commit:** 提示无内容可推送，停止。

### Step 3: 根据 commit 内容重命名分支

**始终检查分支名是否反映当前工作内容。**

分支名应符合 `用户名/功能描述` 格式，且功能描述必须反映实际改动内容。

1. 获取 git 用户名：
```bash
GIT_USER=$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
```

2. 从最近的 commit 消息提取功能描述，转换为英文短横线格式：
```bash
COMMIT_MSG=$(git log -1 --pretty=%s)
# 分析 commit 消息，提取核心功能
# 例如：
# "feat: 完善 Hasura GraphQL 配置支持前端 MVP" -> "hasura-graphql-frontend-mvp"
# "fix: 修复飞书通知 JSON 格式问题" -> "fix-feishu-notify-json"
# "refactor: 简化 CI 流程" -> "simplify-ci"
```

3. 检查当前分支名是否已经正确反映功能：
   - 如果分支名像 `lkyxuan/salvador`、`lkyxuan/test`、`feature-1` 等通用名称 → 需要重命名
   - 如果分支名已经反映功能如 `lkyxuan/hasura-graphql-config` → 可以保留

4. 如需重命名：
```bash
NEW_BRANCH="${GIT_USER}/${FEATURE_DESC}"
git branch -m "$CURRENT_BRANCH" "$NEW_BRANCH"
CURRENT_BRANCH="$NEW_BRANCH"
echo "分支已重命名: <旧名> → <新名>"
```

**命名规则：**
- 用户名：从 git config user.name 获取，转小写，空格变连字符
- 功能描述：从 commit 消息核心内容提取，使用英文短横线连接
- 保持简洁：3-5 个单词，如 `add-klines-view`、`fix-hasura-metadata`

### Step 4: 推送当前分支

```bash
git push origin $CURRENT_BRANCH
```

**如果推送失败:** 显示错误信息并停止。

### Step 5: 合并到 dev 分支

```bash
# 获取最新的 dev
git fetch origin dev

# 切换到 dev
git checkout dev

# 拉取最新
git pull origin dev

# 合并功能分支
git merge $CURRENT_BRANCH --no-edit

# 推送 dev
git push origin dev
```

**如果合并有冲突:**
```
合并冲突！请手动解决以下文件的冲突：
<冲突文件列表>

解决后运行:
git add . && git commit && git push origin dev
```

停止。

### Step 6: 关闭相关 Issues (Issue-Driven Development)

合并完成后，检查并关闭相关的 Issues：

```bash
# 查看当前开放的 task issues
gh issue list --state open --label task

# 对比本次改动和 issue 描述，识别已完成的 issues
```

**关闭 Issue：**
```bash
# 关闭已完成的 issues
gh issue close <ISSUE_NUMBER> --comment "完成于 commit <COMMIT_HASH>，已合并到 dev"
```

**检查清单：**
1. 列出本次 commit 涉及的文件
2. 对比开放的 task issues
3. 确认哪些 issues 的验证标准已满足
4. 关闭已完成的 issues，附带 commit 引用

### Step 7: 返回原分支

```bash
git checkout $CURRENT_BRANCH
```

### Step 8: 输出结果

```
✅ 推送并合并完成！

分支: <branch>
合并到: dev
最新提交: <commit hash> <commit message>

dev 分支已更新并推送到远程。
```

## Quick Reference

| 步骤 | 操作 | 失败处理 |
|------|------|---------|
| 1 | 检查当前分支 | 停止，不允许在 dev/main 操作 |
| 2 | 检查并自动提交 | 自动 commit |
| 3 | 根据 commit 重命名分支 | 自动重命名 |
| 4 | 推送分支 | 显示错误，停止 |
| 5 | 合并到 dev | 显示冲突，停止 |
| 6 | 关闭相关 Issues | 检查并关闭已完成的 issues |
| 7 | 返回原分支 | - |

## Branch Naming Examples

| Commit 消息 | 分支名 |
|------------|--------|
| feat: 完善 Hasura GraphQL 配置 | `lkyxuan/hasura-graphql-config` |
| fix: 修复飞书通知 JSON 格式 | `lkyxuan/fix-feishu-notify-json` |
| feat: 添加 K 线连续聚合视图 | `lkyxuan/add-klines-view` |
| refactor: 简化 CI 流程 | `lkyxuan/simplify-ci` |
| feat: 爬虫支持多币种采集 | `lkyxuan/multi-coin-crawler` |

## Red Flags

**Never:**
- 在 dev 或 main 分支直接执行
- 使用通用分支名如 `test`、`feature`、`dev2`
- Force push 到 dev 分支
- 忽略合并冲突

**Always:**
- 自动提交未暂存的更改
- 根据实际改动内容命名分支
- 合并后返回原分支
- 显示操作结果
