---
name: merge-pr
description: Use when merging pull requests to dev branch, especially multi-contributor PRs or security-sensitive changes. Triggers when user asks to merge, approve, or complete a PR. Supports Issue-driven development by closing related issues after merge.
---

# Merge PR to Dev

## Overview

通过 PR 合并代码到 dev 分支，包含安全检查、Issue 关闭和 openspec 归档。

**目标分支**：dev（开发分支）

**与 push-to-dev 的区别**：
- push-to-dev：推送代码，创建 PR，标记 Issue 待测试
- merge-pr：合并 PR，关闭 Issue，归档 openspec

**Announce at start:** "使用 merge-pr skill 来合并 PR。"

## When to Use

- 合并 PR 到 dev 分支
- 需要 code review 的场景
- 多人协作的 PR
- User asks to "merge", "approve", or "complete" a PR

## The Process

### Step 1: Security Checklist (MANDATORY)

**Pre-Merge Security Scan - 每次都必须执行：**

```bash
# View PR details and contributors
gh pr view <PR_NUMBER> --json author,commits,reviews,statusCheckRollup

# Check for secrets/credentials in changes
gh pr diff <PR_NUMBER> | grep -iE '(password|secret|api_key|token|private_key|credential|-----BEGIN)'

# Check for suspicious file patterns
gh pr diff <PR_NUMBER> --name-only | grep -E '\.(env|pem|key|p12|pfx|sh|exe|dll)$'
```

### Step 2: CI Status (NEVER SKIP)

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

### Step 3: Execute Merge

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

### Step 4: Post-Merge Verification

```bash
# Verify merge completed
gh pr view <PR_NUMBER> --json state,mergedAt

# Check target branch updated
git fetch origin
git log origin/dev --oneline -5
```

### Step 5: 关闭相关 Issue（调用 project skill）

Merge 完成后，更新相关 Issues 状态为 Done 并关闭。

**操作步骤：**

1. 查看 PR 关联的 Issues：
```bash
# 从 PR body 提取 Issue 引用
gh pr view <PR_NUMBER> --json body | grep -oE '#[0-9]+'

# 查看待测试和待部署的 Issues
gh issue list --state open --label "待测试"
gh issue list --state open --label "待部署"
```

2. 关闭相关 Issues：
```bash
# 待测试/待部署 → Done（关闭）
gh issue edit <ISSUE_NUMBER> --add-label "部署完成"
gh issue close <ISSUE_NUMBER> --comment "已部署完成，PR #<PR_NUMBER> 已合并到 dev。"
```

### Step 6: 归档 openspec（如有）

如果这次 PR 对应一个 openspec change，归档它：

```bash
# 检查是否有对应的 openspec change
ls openspec/changes/

# 如果有，归档
openspec archive <change-id> --yes
```

### Step 7: 输出结果

```
✅ PR 合并完成！

PR: #<number>
合并到: dev
关闭的 Issues: #<issue1>, #<issue2>

已完成：
- PR 已合并
- Issue 已关闭（状态 → Done）
- openspec 已归档（如有）
```

## 与 project skill 的协作

| merge-pr 步骤 | 调用 project skill 功能 |
|--------------|------------------------|
| Step 5: 关闭 Issue | `move <N> Done` + 关闭 |

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
gh issue close <N> --comment "完成于 PR #<N>"  # Close issues
openspec archive <change-id> --yes  # Archive openspec
```

## Status Flow

```
push-to-dev 完成后：Issue 在 待测试
           ↓
测试通过后：手动移到 待部署
           ↓
merge-pr 完成后：Issue 关闭（Done）
```
