---
name: merge-pr
description: 合并 PR。合并后自动更新 backlog.json 任务状态为「待部署」。
---

# Merge PR

合并 PR，更新 backlog.json 状态。

**Announce at start:** "使用 merge-pr skill 来合并 PR。"

## The Process

### Step 1: 获取 PR 信息

```bash
gh pr view <PR_NUMBER> --json baseRefName,body,title
```

从 PR body 提取 task ID：
```bash
TASK_ID=$(gh pr view <PR_NUMBER> --json body -q '.body' | grep -oE 'Implements: [a-z0-9-]+' | cut -d' ' -f2)
```

### Step 2: 检查 backlog.json 任务状态

```python
import json
backlog = json.load(open('docs/backlog.json'))
task = next((t for t in backlog['tasks'] if t['id'] == task_id), None)

if not task:
    print(f"⚠️ 未找到任务 {task_id}，跳过状态检查")
elif task['status'] != 'testing':
    print(f"⚠️ 任务 [{task_id}] 状态是 {task['status']}，建议先测试")
```

### Step 3: 安全检查

```bash
# 检查 secrets
gh pr diff <PR_NUMBER> | grep -iE '(password|secret|api_key|token)'

# 检查 CI
gh pr checks <PR_NUMBER>
```

### Step 4: 执行 Merge

```bash
gh pr merge <PR_NUMBER> --merge --delete-branch
```

### Step 5: 更新 backlog.json

```python
if task:
    task['status'] = 'deploying'  # testing → deploying
    task['merged_pr'] = pr_number
    save_backlog()
    git_commit("chore: update backlog - task deploying")
```

### Step 6: 输出

```
✅ PR 合并完成！

PR: #<number>
任务: [<id>] <title>
状态: testing → deploying

下一步：
- 部署完成后: /backlog done <id>
```

## 快捷流程

```
/push-to-dev    → PR 创建，任务 developing → testing
/merge-pr       → PR 合并，任务 testing → deploying
/backlog done   → 部署完成，任务 → done
```

## 注意

- 这个 skill 只处理 GitHub PR 合并
- 任务状态管理在 backlog.json
- 不再依赖 GitHub Issues/Projects
