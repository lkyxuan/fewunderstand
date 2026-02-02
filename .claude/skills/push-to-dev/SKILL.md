---
name: push-to-dev
description: Use when you need to push current branch and merge to dev - handles auto-commit, branch renaming, push, merge or create PR with issue linking, mark issues as ready-for-review, and cleanup. Supports Issue-driven development.
---

# Push to Dev

## Overview

自动提交、检查 Issue 关联、推送到远程、合并到 dev 或创建 PR 的完整流程。

**Core principle:** 检查 Issue → 自动提交 → 推送 → 合并/创建 PR → 更新 Issue 状态

**与 merge-pr 的区别**：
- push-to-dev：推送代码，创建/更新 PR，标记 Issue 待测试
- merge-pr：合并 PR，关闭 Issue，归档 openspec

**Announce at start:** "使用 push-to-dev skill 来推送代码。"

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

### Step 2: 检查相关 Issue（调用 project skill）

**这是关键步骤：确保每次推送都有对应的 Issue。**

1. 根据分支名和最近 commit 搜索相关 Issue：
```bash
# 从分支名提取关键词
BRANCH_KEYWORDS=$(echo $CURRENT_BRANCH | sed 's/[^a-zA-Z0-9]/ /g')

# 搜索相关 Issue
gh issue list --state open --search "$BRANCH_KEYWORDS"

# 也检查 commit 消息中的 Issue 引用（#123）
git log --oneline -5 | grep -oE '#[0-9]+'
```

2. **如果找到相关 Issue：**
   - 确认 Issue 状态是否为 `开发中`
   - 如果不是，调用 `/project claim <N>` 认领

3. **如果没有找到相关 Issue：**
   ```
   ⚠️ 没有找到与此次更改相关的 Issue。

   根据 Issue-Driven Development 原则，每次代码更改都应该关联到一个 Issue。

   请选择：
   1. 创建新 Issue 描述这次更改解决的问题
   2. 关联到现有 Issue（输入 Issue 编号）
   3. 跳过（不推荐）
   ```

   **如果选择创建 Issue，调用 project skill：**
   ```
   /project create "<commit 标题>"
   /project claim <NEW_ISSUE_NUMBER>
   ```

   project skill 会自动创建 Issue 并设置为「开发中」状态。

4. **记录关联的 Issue 编号：** `RELATED_ISSUE=<number>`

### Step 3: 检查并自动提交

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

3. 添加并提交（包含 Issue 引用）：
```bash
git add <相关文件>
git commit -m "<type>: <描述>

<详细说明如有必要>

Refs #$RELATED_ISSUE

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**如果没有更改也没有新 commit:** 提示无内容可推送，停止。

### Step 4: 根据 commit 内容重命名分支

**始终检查分支名是否反映当前工作内容。**

分支名应符合 `用户名/功能描述` 格式，且功能描述必须反映实际改动内容。

1. 获取 git 用户名：
```bash
GIT_USER=$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
```

2. 从最近的 commit 消息提取功能描述，转换为英文短横线格式

3. 如需重命名：
```bash
NEW_BRANCH="${GIT_USER}/${FEATURE_DESC}"
git branch -m "$CURRENT_BRANCH" "$NEW_BRANCH"
CURRENT_BRANCH="$NEW_BRANCH"
echo "分支已重命名: <旧名> → <新名>"
```

### Step 5: 推送当前分支

```bash
git push origin $CURRENT_BRANCH -u
```

**如果推送失败:** 显示错误信息并停止。

### Step 6: 创建或更新 PR

**检查是否已有 PR：**
```bash
gh pr list --head $CURRENT_BRANCH --state open
```

**如果没有 PR，创建 PR：**
```bash
gh pr create \
  --title "<commit 消息>" \
  --body "$(cat <<EOF
## Summary

<变更摘要>

## Related Issue

Closes #$RELATED_ISSUE

## Test Plan

- [ ] 功能测试
- [ ] 回归测试

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base dev
```

**如果已有 PR：** 更新 PR 描述确保关联了 Issue。

### Step 7: 更新 Issue 状态（调用 project skill）

**所有状态变更都通过 project skill 完成。**

推送完成后，调用 project skill 更新状态：

```
/project move $RELATED_ISSUE 待测试
```

project skill 会自动：
- 移除「开发中」标签
- 添加「待测试」标签
- 添加评论说明状态变更

### Step 8: 输出结果

```
✅ 推送完成！

分支: <branch>
关联 Issue: #<number>
PR: <pr_url>
状态: 开发中 → 待测试

下一步：
- 测试验证后，使用 /merge-pr 合并
```

## 与 project skill 的协作

| push-to-dev 步骤 | 调用 project skill 功能 |
|-----------------|------------------------|
| Step 2: 检查 Issue | `status`、`create`、`claim` |
| Step 7: 更新状态 | `move <N> 待测试` |

## Quick Reference

| 步骤 | 操作 | 失败处理 |
|------|------|---------|
| 1 | 检查当前分支 | 停止，不允许在 dev/main 操作 |
| 2 | 检查相关 Issue | 没有则创建 |
| 3 | 检查并自动提交 | 自动 commit |
| 4 | 重命名分支 | 自动重命名 |
| 5 | 推送分支 | 显示错误，停止 |
| 6 | 创建/更新 PR | 关联 Issue |
| 7 | 更新 Issue 状态 | 开发中 → 待测试 |

## Red Flags

**Never:**
- 在 dev 或 main 分支直接执行
- 推送没有关联 Issue 的代码（除非明确跳过）
- Force push 到 dev 分支
- 忽略合并冲突

**Always:**
- 确保每次推送都有对应的 Issue
- 自动提交未暂存的更改
- PR 描述中使用 `Closes #issue` 关联 Issue
- 更新 Issue 状态为待测试
