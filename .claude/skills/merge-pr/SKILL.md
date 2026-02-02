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

### Step 5: 更新相关 Issue 状态（调用 project skill）

**所有状态变更都通过 project skill 完成。**

1. 查看 PR 关联的 Issues 和目标分支：
```bash
# 获取 PR 的目标分支
gh pr view <PR_NUMBER> --json baseRefName --jq '.baseRefName'

# 从 PR body 提取 Issue 引用
gh pr view <PR_NUMBER> --json body | grep -oE '#[0-9]+'
```

2. 调用 project skill 更新状态：

**如果 merge 到 dev：**
```
/project move <ISSUE_NUMBER> 待部署
```

**如果 merge 到 main：**
```
/project move <ISSUE_NUMBER> Done
```
（project skill 的 move Done 会自动关闭 Issue）

### Step 6: 归档 openspec（如有）

如果这次 PR 对应一个 openspec change，归档它：

```bash
# 检查是否有对应的 openspec change
ls openspec/changes/

# 如果有，归档
openspec archive <change-id> --yes
```

### Step 7: 输出结果

**如果 merge 到 dev：**
```
✅ PR 合并完成！

PR: #<number>
合并到: dev
Issue 状态: 待测试 → 待部署

下一步：部署到生产环境后，merge 到 main 关闭 Issue
```

**如果 merge 到 main：**
```
✅ PR 合并完成！

PR: #<number>
合并到: main
关闭的 Issues: #<issue1>, #<issue2>

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

```
push-to-dev 完成后：Issue 在 待测试
           ↓
merge 到 dev：Issue 移到 待部署（不关闭）
           ↓
merge 到 main：Issue 关闭（Done）
```
