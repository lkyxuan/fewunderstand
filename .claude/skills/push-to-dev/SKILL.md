---
name: push-to-dev
description: Use when you need to push current branch and merge to dev - handles auto-commit, branch renaming, push, merge or create PR with issue linking, mark issues as ready-for-review, and cleanup. Supports Issue-driven development.
---

# Push to Dev

## Overview

自动提交、重命名分支、推送到远程、合并到 dev 分支（或创建 PR）、标记 Issues 为等待审核状态的完整流程。

**Core principle:** 自动提交 → 根据 commit 重命名分支 → 推送 → 合并到 dev 或创建 PR → 标记 Issues 代码完成 → 返回原分支

**两种模式**：
- **直接合并模式**（默认）：快速迭代，无需 PR
- **PR 模式**：创建 PR 并自动关联 Issue，走 review 流程

**与 merge-pr 的区别**：
- push-to-dev：推送代码，可选直接合并或创建 PR
- merge-pr：合并已有的 PR

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

### Step 5: 选择合并模式

**询问用户选择模式**（或根据上下文自动判断）：

| 模式 | 适用场景 |
|------|----------|
| 直接合并 | 小改动、个人项目、快速迭代 |
| 创建 PR | 需要 review、多人协作、正式流程 |

#### 模式 A: 直接合并到 dev

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

#### 模式 B: 创建 PR 并关联 Issue（推荐）

**1. 查找相关的 Issue：**
```bash
# 查找正在工作的 Issue
ISSUE_NUM=$(gh issue list --state open --label "正在工作" --json number,title -q '.[0].number')
ISSUE_TITLE=$(gh issue list --state open --label "正在工作" --json number,title -q '.[0].title')

# 如果没找到，搜索分支名相关的 Issue
if [ -z "$ISSUE_NUM" ]; then
  ISSUE_NUM=$(gh issue list --state open --search "$CURRENT_BRANCH" --json number -q '.[0].number')
fi
```

**2. 创建 PR 并自动关联 Issue：**
```bash
# 生成 PR 标题（从最近的 commit 或 Issue 标题）
PR_TITLE="<type>: <描述>"

# 生成 PR body，包含 Closes 关键词
if [ -n "$ISSUE_NUM" ]; then
  PR_BODY="$(cat <<EOF
## Summary
<改动描述>

Closes #$ISSUE_NUM

## Test Plan
- [ ] 本地测试通过
- [ ] 相关功能验证
EOF
)"
else
  PR_BODY="$(cat <<EOF
## Summary
<改动描述>

## Test Plan
- [ ] 本地测试通过
EOF
)"
fi

# 创建 PR
gh pr create --base dev --title "$PR_TITLE" --body "$PR_BODY"
```

**关键**：PR body 中的 `Closes #xx` 会在 PR 合并时自动关闭 Issue，并触发 Project 自动化将 Issue 移到 Done 列。

### Step 6: 调用 project skill 更新状态

合并到 dev 或创建 PR 后，调用 `/project` skill 更新 Issue 状态。

**操作步骤：**

1. 查找相关 Issue：
```bash
# 按分支名或标签查找
ISSUE_NUM=$(gh issue list --state open --label "正在工作" --json number -q '.[0].number')
```

2. 调用 `/project move` 将 Issue 移到「代码完成」：
```bash
# 更新 Project 看板状态
# 参考 /project skill 的 move 操作
```

3. 添加评论说明：
```bash
gh issue comment $ISSUE_NUM --body "代码完成，已合并到 dev (commit <COMMIT_HASH>)，等待测试验证"
```

**参考 `/project` skill 获取完整的状态流转规则。**

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
| 5a | 直接合并到 dev | 显示冲突，停止 |
| 5b | 创建 PR + 关联 Issue | 自动添加 `Closes #xx` |
| 6 | 标记 Issues 代码完成 | 等待测试验证 |
| 7 | 返回原分支 | - |

## PR 关联 Issue 示例

创建 PR 时自动关联 Issue：
```bash
gh pr create --base dev --title "feat: 添加用户认证" --body "$(cat <<'EOF'
## Summary
实现用户登录和注册功能

Closes #27

## Test Plan
- [ ] 登录功能测试
- [ ] 注册功能测试
EOF
)"
```

**效果**：PR 合并时 → Issue #27 自动关闭 → Project 看板自动移到 Done

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
