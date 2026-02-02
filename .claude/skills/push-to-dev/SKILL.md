---
name: push-to-dev
description: Use when you need to push current branch and create PR. Enforces Issue status check - Issue MUST be in 开发中 state before pushing.
---

# Push to Dev

## Overview

自动提交、检查 Issue 状态、推送到远程、创建 PR 的完整流程。

**强制检查：** Issue 必须在「开发中」状态才能推送，否则拒绝执行。

**与 merge-pr 的区别**：
- push-to-dev：推送代码，创建 PR，状态 开发中 → 待测试
- merge-pr：合并 PR，状态 待测试 → 待部署 或 待部署 → Done

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
❌ 当前在 <branch> 分支，不应直接在此分支开发。
请切换到功能分支后再执行。
```
停止。

### Step 2: 查找关联 Issue

```bash
# 从分支名提取关键词
BRANCH_KEYWORDS=$(echo $CURRENT_BRANCH | sed 's/[^a-zA-Z0-9]/ /g')

# 搜索相关 Issue
gh issue list --state open --search "$BRANCH_KEYWORDS"

# 也检查 commit 消息中的 Issue 引用（#123）
git log --oneline -5 | grep -oE '#[0-9]+'
```

**如果没有找到关联 Issue：**
```
❌ 没有找到关联的 Issue。

根据 Issue-Driven Development 原则，必须先有 Issue 才能推送代码。

请先执行：
1. /project create "问题描述"  → 创建 Issue
2. /project claim <N>         → 认领（问题 → 待定方案）
3. /project idea <N>          → 写方案（待定方案 → 待出设计）
4. /project design <N>        → 出设计（待出设计 → 设计审核）
5. /project approve <N>       → 审核通过（设计审核 → 开发中）
6. 然后才能 /push-to-dev
```
停止。

### Step 3: 强制检查 Issue 状态（核心）

```bash
# 获取 Issue 当前标签
gh issue view <ISSUE_NUMBER> --json labels --jq '[.labels[].name]'
```

**状态检查规则：**

| Issue 当前状态 | 是否允许 push | 处理 |
|---------------|--------------|------|
| `开发中` | ✅ 允许 | 继续流程 |
| `问题` | ❌ 拒绝 | 提示需要先完成 claim → idea → design → approve |
| `待定方案` | ❌ 拒绝 | 提示需要先完成 idea → design → approve |
| `待出设计` | ❌ 拒绝 | 提示需要先完成 design → approve |
| `设计审核` | ❌ 拒绝 | 提示需要先完成 approve |
| `待测试` | ❌ 拒绝 | 已经推送过了，应该等测试或 merge |
| `待部署` | ❌ 拒绝 | 已经测试通过了，应该 merge 到 main |
| `Done` | ❌ 拒绝 | Issue 已关闭 |

**拒绝时的提示模板：**

```
❌ Issue #<N> 当前状态是「<当前状态>」，不能直接推送代码。

必须先完成以下步骤：
<根据当前状态列出需要完成的步骤>

或者调用 /project 查看当前状态并更新。
```

**示例 - Issue 在「待出设计」：**
```
❌ Issue #37 当前状态是「待出设计」，不能直接推送代码。

必须先完成以下步骤：
1. /project design 37   → 设计审核（用 openspec 出设计后执行）
2. /project approve 37  → 开发中（审核通过后执行）
3. 然后才能 /push-to-dev

或者调用 /project 查看当前状态并更新。
```

### Step 4: 检查并自动提交

```bash
git status --porcelain
```

**如果有未提交的更改，自动提交：**

1. 查看变更内容：
```bash
git diff --stat
git diff
```

2. 分析变更，生成合适的 commit 消息

3. 添加并提交（包含 Issue 引用）：
```bash
git add <相关文件>
git commit -m "<type>: <描述>

<详细说明如有必要>

Refs #$RELATED_ISSUE

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**如果没有更改也没有新 commit:** 提示无内容可推送，停止。

### Step 5: 根据 commit 内容重命名分支

分支名应符合 `用户名/功能描述` 格式。

```bash
GIT_USER=$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
NEW_BRANCH="${GIT_USER}/${FEATURE_DESC}"
git branch -m "$CURRENT_BRANCH" "$NEW_BRANCH"
```

### Step 6: 推送当前分支

```bash
git push origin $CURRENT_BRANCH -u
```

### Step 7: 智能判断关联哪个 Issue（AI 自动）

**AI 自动执行以下判断：**

```bash
# 1. 检查父 Issue 是否有 sub-issues
PARENT_BODY=$(gh issue view $RELATED_ISSUE --json body -q .body)
SUB_ISSUES=$(echo "$PARENT_BODY" | grep -oE '#[0-9]+' | tr -d '#')

# 2. 检查 openspec/tasks.md 有多少任务
TASK_COUNT=$(grep -c '^\s*-\s*\[' openspec/changes/*/tasks.md 2>/dev/null || echo 0)
```

**情况 A: Issue 已有 sub-issues**
```
检测到父 Issue #10 有以下 sub-issues:
  - [ ] #11 实现登录 API
  - [x] #12 实现注册 API
  - [ ] #13 添加 JWT 验证

根据你的代码变更，这个 PR 应该关闭 #11（实现登录 API）

确认吗？[Y/n]
```
→ AI 分析 commit 内容，自动匹配最相关的 sub-issue

**情况 B: Issue 没有 sub-issues，但 tasks.md 有多个任务**
```
检测到 Issue #10 的 tasks.md 有 5 个任务，但没有拆分 sub-issues。

建议先拆分：/project split 10

这样每个 PR 可以独立追踪进度。

是否现在拆分？[Y/n]
```
→ 如果用户同意，自动执行 split

**情况 C: 简单 Issue，直接关闭**
```
Issue #10 是简单任务，直接用 Closes #10
```

### Step 8: 创建 PR

```bash
# TARGET_ISSUE 由 Step 7 自动确定（可能是 sub-issue）
gh pr create \
  --title "<commit 消息>" \
  --body "$(cat <<EOF
## Summary
<变更摘要>

## Related Issue
Closes #$TARGET_ISSUE

## Test Plan
- [ ] 功能测试
- [ ] 回归测试

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base dev
```

### Step 9: 更新 Issue 状态

```
/project move $TARGET_ISSUE 待测试
```

### Step 10: 输出结果

```
✅ 推送完成！

分支: <branch>
关联 Issue: #<number>
PR: <pr_url>
状态: 开发中 → 待测试

下一步：
- 测试验证后，使用 /merge-pr 合并到 dev
```

## 状态检查速查表

```
要 push 代码，Issue 必须在「开发中」

如果 Issue 在其他状态，需要先完成：

问题       → claim → idea → design → approve → 开发中 → 可以 push
待定方案   →         idea → design → approve → 开发中 → 可以 push
待出设计   →                design → approve → 开发中 → 可以 push
设计审核   →                         approve → 开发中 → 可以 push
开发中     →                                            可以 push ✅
待测试     → 不能 push（已经推送过了）
待部署     → 不能 push（应该 merge 到 main）
Done       → 不能 push（Issue 已关闭）
```

## Red Flags

**Never:**
- 跳过状态检查直接推送
- 在 dev 或 main 分支直接执行
- 推送没有关联 Issue 的代码
- Force push 到 dev 分支

**Always:**
- Issue 必须在「开发中」才能推送
- 状态不对时，先用 /project 更新状态
- PR 描述中使用 `Closes #issue` 关联 Issue
