---
name: push
description: 推送代码。检查任务状态和分支名，自动提交，推送后 GitHub Actions 会自动创建 PR。
---

# /push - 推送代码

自动提交并推送到远程，GitHub Actions 会自动创建 PR。

**数据源：** `docs/backlog.json`

**Announce at start:** "使用 push skill 来推送代码。"

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

### Step 4: 检查分支名是否有意义

**规则：** 分支名应该反映任务内容，格式建议：`<user>/<task-id>` 或 `<type>/<描述>`

```python
# 检查当前分支名是否能关联到任务
task_keywords = task['id'].lower().replace('-', ' ').split()
branch_has_meaning = any(kw in current_branch.lower() for kw in task_keywords)

if not branch_has_meaning:
    # 建议重命名分支
    suggested_name = f"lkyxuan/{task['id']}"
    print(f"⚠️ 当前分支名 '{current_branch}' 与任务 [{task['id']}] 无关")
    print(f"建议重命名为: {suggested_name}")
    # 询问用户是否重命名
```

**如果需要重命名分支：**
```bash
git branch -m $OLD_BRANCH $NEW_BRANCH
git push origin :$OLD_BRANCH  # 删除旧远程分支
git push origin $NEW_BRANCH -u
```

### Step 5: 检查并自动提交

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

### Step 6: 推送

```bash
git push origin $CURRENT_BRANCH -u
```

推送后，GitHub Actions (`auto-pr.yml`) 会自动创建 PR 到 `dev` 分支。

### Step 7: 获取 PR URL

```bash
# 等待 PR 创建
sleep 5
PR_URL=$(gh pr list --head "$CURRENT_BRANCH" --json url -q '.[0].url')
```

PR 标题由 workflow 从分支名自动生成，分支名有意义就够了。

### Step 8: 更新 backlog.json 状态

```python
task['status'] = 'testing'
task['pr'] = pr_url
save_backlog()
git_commit("chore: update backlog - task testing")
git_push()
```

### Step 9: 输出

```
✅ 推送完成！

分支: <branch>
任务: [<id>] <title>
PR: <pr_url>（workflow 自动创建）
状态: developing → testing

下一步：
- 测试通过后: /merge-pr <pr_number>
- 部署完成后: /backlog done <id>
```

## 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 分支名 | `<user>/<task-id>` | `lkyxuan/backlog-migration` |
| PR 标题 | `<type>: <任务标题>` | `feat: 迁移到 backlog.json` |
| Commit | `<type>: <描述>` | `feat: 添加 backlog skill` |

**type 类型：** feat, fix, chore, refactor, docs, test

## 状态检查速查表

```
要 push 代码，任务必须在 developing 状态

problem    → ... → developing
developing → 可以 push ✅
testing    → 已经推送过了
deploying  → 应该部署了
done       → 任务已完成
```

## 与 GitHub 的关系

- **backlog.json** = 任务管理（AI 原生）
- **GitHub Actions** = 自动创建 PR 到 dev
- **GitHub PR** = 代码 review（标题由 skill 更新）
