---
name: merge-pr
description: Use when merging pull requests. Merge to dev marks Issue as 待部署; merge to main closes Issue. Triggers when user asks to merge, approve, or complete a PR.
---

# Merge PR

## Overview

通过 PR 合并代码，包含安全检查和 Issue 状态更新。

**状态流转规则**：
- **merge 到 dev**：Issue 从「待测试」→「待部署」（不关闭）
- **merge 到 main**：Issue 从「待部署」→「Done」（关闭）

**与 push-to-dev 的区别**：
- push-to-dev：推送代码，创建 PR，标记 Issue 待测试
- merge-pr：合并 PR，更新 Issue 状态（待部署或关闭）

**Announce at start:** "使用 merge-pr skill 来合并 PR。"

## When to Use

- 合并 PR 到 dev 分支
- 需要 code review 的场景
- 多人协作的 PR
- User asks to "merge", "approve", or "complete" a PR

## The Process

### Step 1: 检查 PR 和关联 Issue

```bash
# 获取 PR 信息
gh pr view <PR_NUMBER> --json baseRefName,body

# 从 PR body 提取 Issue 引用（必须用 Closes #）
RELATED_ISSUE=$(gh pr view <PR_NUMBER> --json body --jq '.body' | grep -oiE '(closes|fixes)\s*#[0-9]+' | head -1 | grep -oE '[0-9]+')

# 获取目标分支
TARGET_BRANCH=$(gh pr view <PR_NUMBER> --json baseRefName --jq '.baseRefName')
```

**如果 PR 没有用 `Closes #`：**
```
❌ PR 没有正确关联 Issue。

请确保 PR body 包含 "Closes #<issue-number>" 语法。
这样可以：
- 在 GitHub UI 显示关联
- 合并时自动更新 Issue 状态
- 在 Project 看板上追踪
```

### Step 2: 强制检查 Issue 状态（核心）

```bash
# 获取 Issue 当前标签
gh issue view $RELATED_ISSUE --json labels --jq '[.labels[].name]'
```

**状态检查规则：**

| 目标分支 | Issue 必须状态 | 是否允许 merge | 处理 |
|---------|---------------|---------------|------|
| dev | `待测试` | ✅ 允许 | merge 后 → 待部署 |
| main | `待部署` | ✅ 允许 | merge 后 → Done（关闭） |
| dev | 其他状态 | ❌ 拒绝 | 提示需要先完成流程 |
| main | 其他状态 | ❌ 拒绝 | 提示需要先 merge 到 dev |

**拒绝时的提示模板：**

**如果 merge 到 dev，但 Issue 不在「待测试」：**
```
❌ Issue #<N> 当前状态是「<当前状态>」，不能 merge 到 dev。

要 merge 到 dev，Issue 必须在「待测试」状态。

可能的问题：
- 如果在「开发中」：需要先 /push-to-dev 推送代码
- 如果在更早阶段：需要先完成 claim → idea → design → approve → push-to-dev
- 如果在「待部署」：已经 merge 过了，应该 merge 到 main

请先用 /project 查看和更新状态。
```

**如果 merge 到 main，但 Issue 不在「待部署」：**
```
❌ Issue #<N> 当前状态是「<当前状态>」，不能 merge 到 main。

要 merge 到 main，Issue 必须在「待部署」状态。

可能的问题：
- 如果在「待测试」：需要先 merge 到 dev
- 如果在更早阶段：需要先完成整个开发流程
- 如果在「Done」：Issue 已关闭

请先用 /project 查看和更新状态。
```

### Step 3: Security Checklist (MANDATORY)

**Pre-Merge Security Scan - 每次都必须执行：**

```bash
# View PR details and contributors
gh pr view <PR_NUMBER> --json author,commits,reviews,statusCheckRollup

# Check for secrets/credentials in changes
gh pr diff <PR_NUMBER> | grep -iE '(password|secret|api_key|token|private_key|credential|-----BEGIN)'

# Check for suspicious file patterns
gh pr diff <PR_NUMBER> --name-only | grep -E '\.(env|pem|key|p12|pfx|sh|exe|dll)$'
```

### Step 4: CI Status (NEVER SKIP)

```bash
# Check CI status
gh pr checks <PR_NUMBER>

# If CI still running, set auto-merge instead of waiting
gh pr merge <PR_NUMBER> --auto --merge
```

**Red flags - STOP if user asks to:**
- Skip CI checks ("just merge it")
- Use `--admin` to bypass protections
- Merge with failing checks

### Step 5: Execute Merge

```bash
# Standard merge (preserves commit history)
gh pr merge <PR_NUMBER> --merge

# Squash merge (combines all commits)
gh pr merge <PR_NUMBER> --squash

# Delete branch after merge
gh pr merge <PR_NUMBER> --merge --delete-branch
```

**Merge strategy:**
| Scenario | Strategy |
|----------|----------|
| Multi-contributor PR | `--merge` (preserve attribution) |
| Feature with messy history | `--squash` |
| Hotfix | `--merge --delete-branch` |

### Step 6: Post-Merge Verification

```bash
# Verify merge completed
gh pr view <PR_NUMBER> --json state,mergedAt

# Check target branch updated
git fetch origin
git log origin/$TARGET_BRANCH --oneline -5
```

### Step 7: 更新相关 Issue 状态（调用 project skill）

**所有状态变更都通过 project skill 完成：**

| merge 到 | Issue 状态变更 |
|---------|---------------|
| dev | `/project move <N> 待部署` |
| main | `/project move <N> Done`（自动关闭） |

**执行状态更新：**

```bash
if [ "$TARGET_BRANCH" = "dev" ]; then
  # /project move <ISSUE_NUMBER> 待部署
elif [ "$TARGET_BRANCH" = "main" ]; then
  # /project move <ISSUE_NUMBER> Done
fi
```

### Step 8: 归档 openspec（如有）

如果这次 PR 对应一个 openspec change，归档它：

```bash
# 检查是否有对应的 openspec change
ls openspec/changes/

# 如果有，归档
openspec archive <change-id> --yes
```

### Step 9: 输出结果

**merge 到 dev：**
```
✅ PR 合并完成！

PR: #<number>
合并到: dev
Issue 状态: 待测试 → 待部署

下一步：部署到生产环境后，merge 到 main 关闭 Issue
```

**merge 到 main：**
```
✅ PR 合并完成！

PR: #<number>
合并到: main
关闭的 Issues: #<issue1>

已完成：
- PR 已合并到生产
- Issue 已关闭（状态 → Done）
- openspec 已归档（如有）
```

## 与 project skill 的协作

| merge-pr 步骤 | 目标分支 | 调用 project skill 功能 |
|--------------|---------|------------------------|
| Step 5 | dev | `move <N> 待部署` |
| Step 5 | main | `move <N> Done` + 关闭 |

## Security Red Flags - STOP and Report

| Symptom | Action |
|---------|--------|
| Secrets in diff | **STOP** - Do not merge. Report to user. |
| Executable permission added | **WARN** - Ask user to justify |
| Large binary files | **WARN** - Ask if intentional |
| CI failing/pending | **WAIT** - Use --auto, never skip |
| No required approvals | **STOP** - Cannot merge |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "It's urgent" | Urgent merges cause bigger outages. Follow the process. |
| "I already tested locally" | Local ≠ CI/production. Wait for CI. |
| "It's just 20 lines" | Small changes cause big incidents. Check anyway. |
| "Skip this one time" | There's never "one time". Process exists for a reason. |

## Quick Reference

```bash
# Safe merge workflow
gh pr view <N>                    # Review PR
gh pr checks <N>                  # Verify CI
gh pr diff <N> | grep -i secret   # Security scan
gh pr merge <N> --merge           # Execute merge

# 如果 merge 到 dev
gh issue edit <N> --remove-label "待测试" --add-label "待部署"

# 如果 merge 到 main
gh issue close <N> --comment "完成于 PR #<N>"
openspec archive <change-id> --yes  # Archive openspec
```

## Status Flow

**使用 Sub-Issue 模式处理大功能：**

```
父 Issue #10 (大功能)
    │
    │  ## Sub-Issues (task list 自动打勾)
    │  - [x] #11 实现登录 API
    │  - [x] #12 实现注册 API
    │  - [ ] #13 添加 JWT 验证
    │
    ├── Sub-Issue #11 ← PR #20 (Closes #11) ✅ merge → Done
    ├── Sub-Issue #12 ← PR #21 (Closes #12) ✅ merge → Done
    └── Sub-Issue #13 ← PR #22 (Closes #13) 进行中
                             ↓
                     所有 sub-issues 完成
                             ↓
                     手动关闭父 Issue #10
```

**每个 PR 必须用 `Closes #` 完全解决一个 Issue（可以是 sub-issue）。**

## 状态检查速查表

```
┌─────────────────────────────────────────────────────────────────┐
│ merge 到 dev:  Issue 必须在「待测试」 → 变「待部署」              │
│ merge 到 main: Issue 必须在「待部署」 → 变「Done」（关闭）        │
└─────────────────────────────────────────────────────────────────┘

功能太大需要多个 PR？
→ 不要用 Refs #，用 /project split 拆分 sub-issues
→ 每个 PR 对应一个 sub-issue，用 Closes # 完全解决
```

## Red Flags

**Never:**
- 跳过状态检查直接 merge
- Issue 状态不对时强制 merge
- 忽略 CI 检查结果
- 在 diff 中发现 secrets 仍然 merge

**Always:**
- Merge 到 dev 前检查 Issue 在「待测试」
- Merge 到 main 前检查 Issue 在「待部署」
- 状态不对时，先用 /project 更新状态
- 执行安全扫描检查 secrets
