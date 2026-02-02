---
name: push-to-dev
description: 推送代码并创建 PR。从 backlog.json 读取任务，强制检查任务状态必须是「开发中」。
---

# Push to Dev

自动提交、推送到远程、创建 PR 的完整流程。

**数据源：** `docs/backlog.json`（AI 原生，替代 GitHub Projects）

**Announce at start:** "使用 push-to-dev skill 来推送代码。"

## The Process

### Step 1: 检查当前分支

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

如果在 `dev` 或 `main`：
```
❌ 当前在 <branch> 分支，不应直接在此分支开发。
```
停止。

### Step 2: 读取 backlog.json，找到当前任务

```python
import json
backlog = json.load(open('docs/backlog.json'))

# 找到 owner=@claude 且 status=developing 的任务
my_tasks = [t for t in backlog['tasks']
            if t['owner'] == '@claude' and t['status'] == 'developing']

if not my_tasks:
    # 尝试从分支名匹配任务
    branch_keywords = current_branch.replace('-', ' ').replace('/', ' ')
    matched = [t for t in backlog['tasks']
               if any(kw in t['title'].lower() for kw in branch_keywords.split())]
```

**如果找到任务：**
```
找到关联任务: [auth-001] 用户无法登录
状态: 💻 开发中
```

**如果没找到：**
```
❌ 没有找到关联任务。

请先创建任务：
/backlog add "任务描述"
/backlog claim <id>
/backlog move <id> developing
```

### Step 3: 检查状态（必须是 developing）

```python
if task['status'] != 'developing':
    print(f"❌ 任务 [{task['id']}] 状态是 {task['status']}，不是 developing")
    print("请先: /backlog move <id> developing")
    return
```

### Step 4: 检查并自动提交

```bash
git status --porcelain
```

如果有未提交的更改：
```bash
git add <相关文件>
git commit -m "<type>: <描述>

Implements: <task-id>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### Step 5: 推送

```bash
git push origin $CURRENT_BRANCH -u
```

### Step 6: 创建 PR

```bash
gh pr create \
  --title "<commit 消息>" \
  --body "$(cat <<EOF
## Summary
<变更摘要>

## Task
Implements: $TASK_ID
- Title: $TASK_TITLE
- Why: $TASK_WHY

## Test Plan
- [ ] 功能测试
- [ ] 回归测试

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base dev
```

### Step 7: 更新 backlog.json 状态

```python
task['status'] = 'testing'
task['pr'] = pr_url
save_backlog()
git_commit("chore: update backlog - task testing")
```

### Step 8: 输出

```
✅ 推送完成！

分支: <branch>
任务: [<id>] <title>
PR: <pr_url>
状态: developing → testing

下一步：
- 测试通过后: /backlog move <id> deploying
- 部署完成后: /backlog done <id>
```

## 状态检查速查表

```
要 push 代码，任务必须在 developing 状态

如果任务在其他状态：

problem    → /backlog move <id> planning → ... → developing
planning   → /backlog move <id> designing → ... → developing
designing  → /backlog move <id> reviewing → developing
reviewing  → /backlog move <id> developing ✅
developing → 可以 push ✅
testing    → 已经推送过了
deploying  → 应该部署了
done       → 任务已完成
```

## 与 GitHub 的关系

- **backlog.json** = 任务管理（AI 原生）
- **GitHub PR** = 代码 review（保留）
- **GitHub Issues** = 外部用户报 bug（可选同步到 backlog）

PR 不再强制关联 GitHub Issue，而是引用 backlog task ID。
