---
name: push-to-dev
description: Use when you need to push current branch and merge to dev - handles branch naming validation, push, merge, and cleanup
---

# Push to Dev

## Overview

检查当前分支、推送到远程、合并到 dev 分支的完整流程。

**Core principle:** 检查状态 → 验证分支名 → 推送 → 合并到 dev → 返回原分支

**Announce at start:** "使用 push-to-dev skill 来推送并合并到 dev 分支。"

## The Process

### Step 1: 检查 Git 状态

```bash
# 检查未提交的更改
git status --porcelain
```

**如果有未提交的更改:**
```
发现未提交的更改：
<列出更改的文件>

请先提交或暂存这些更改后再执行 push。
```

停止。不继续后续步骤。

**如果没有未提交的更改:** 继续 Step 2。

### Step 2: 验证当前分支

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

### Step 3: 验证并自动修复分支命名

分支名应符合 `用户名/功能描述` 格式（如 `lkyxuan/add-feature`）。

**如果分支名不符合规范，自动重命名：**

1. 获取 git 用户名：
```bash
GIT_USER=$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
```

2. 从最近的 commit 消息提取功能描述：
```bash
# 获取最近 commit 的标题，提取类型和描述
COMMIT_MSG=$(git log -1 --pretty=%s)
# 例如 "feat: 添加飞书通知" -> "add-feishu-notify"
# 例如 "fix: 修复 JSON 格式" -> "fix-json-format"
```

3. 生成新分支名并重命名：
```bash
NEW_BRANCH="${GIT_USER}/${FEATURE_DESC}"
git branch -m "$CURRENT_BRANCH" "$NEW_BRANCH"
CURRENT_BRANCH="$NEW_BRANCH"
```

4. 输出：
```
分支已自动重命名: <旧名> → <新名>
```

**命名规则：**
- 用户名：从 git config user.name 获取，转小写，空格变连字符
- 功能描述：从 commit 消息提取，使用英文短横线连接，如 `add-multi-coin-crawler`

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

### Step 6: 返回原分支

```bash
git checkout $CURRENT_BRANCH
```

### Step 7: 输出结果

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
| 1 | 检查未提交更改 | 停止，要求先提交 |
| 2 | 检查当前分支 | 停止，不允许在 dev/main 操作 |
| 3 | 验证分支名 | 自动根据 commit 内容重命名 |
| 4 | 推送分支 | 显示错误，停止 |
| 5 | 合并到 dev | 显示冲突，停止 |
| 6 | 返回原分支 | - |

## Common Mistakes

**跳过状态检查**
- **问题:** 未提交的更改导致合并失败
- **修复:** 始终先检查 git status

**在 dev/main 分支直接操作**
- **问题:** 破坏主分支历史
- **修复:** 强制要求在功能分支操作

**不验证分支名**
- **问题:** 分支名混乱，难以追踪
- **修复:** 强制 `用户名/功能` 格式

## Red Flags

**Never:**
- 在 dev 或 main 分支直接执行
- 跳过未提交更改检查
- Force push 到 dev 分支
- 忽略合并冲突

**Always:**
- 先检查 git 状态
- 验证分支命名规范
- 合并后返回原分支
- 显示操作结果
