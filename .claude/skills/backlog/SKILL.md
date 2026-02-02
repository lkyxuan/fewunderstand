---
name: backlog
description: Use when managing tasks - view, create, move status, assign owner. AI-native alternative to GitHub Projects with 8 statuses.
---

# /backlog - AI 原生任务管理

基于 `docs/backlog.json` 的任务追踪，替代 GitHub Projects。

**Announce at start:** "使用 backlog skill 管理任务。"

## 8 个状态

| 状态 | ID | 说明 | 下一步 |
|------|-----|------|--------|
| ❓ 问题 | `problem` | 发现问题/提出需求 | → planning |
| 🤔 待定方案 | `planning` | 人想解决思路 | → designing |
| 📐 待出设计 | `designing` | AI 出详细设计 | → reviewing |
| 👀 设计审核 | `reviewing` | 人审核设计 | → developing 或 → designing |
| 💻 开发中 | `developing` | 写代码 | → testing |
| 🧪 待测试 | `testing` | 测试验证 | → deploying |
| 🚀 待部署 | `deploying` | 等待上线 | → done |
| ✅ Done | `done` | 完成 | (归档) |

## 命令

| 命令 | 说明 |
|------|------|
| `/backlog` | 显示所有任务（按状态分组） |
| `/backlog add "标题"` | 添加新任务（status = problem） |
| `/backlog <id>` | 查看任务详情 |
| `/backlog move <id> <status>` | 移动状态 |
| `/backlog claim <id>` | 认领任务（设置 owner） |
| `/backlog split <id>` | 拆分为 sub-tasks |
| `/backlog done <id>` | 标记完成并归档 |

## 操作实现

### 1. 显示任务列表

```bash
cat docs/backlog.json | jq -r '
  .tasks | group_by(.status) | .[] |
  "### " + .[0].status + "\n" +
  (map("- [" + .id + "] " + .title + " (" + (.owner // "无人") + ")") | join("\n"))
'
```

**输出格式：**
```
### ❓ 问题 (2)
- [auth-001] 用户无法登录 (无人)
- [perf-002] 页面加载慢 (无人)

### 💻 开发中 (1)
- [api-003] 添加搜索接口 (@claude)

### ✅ Done (3)
- [setup-001] 项目初始化
...
```

### 2. 添加任务

```bash
# /backlog add "用户无法登录"
```

```python
new_task = {
    "id": generate_id(),  # 如 "task-001"
    "title": "用户无法登录",
    "status": "problem",
    "priority": "P1",
    "owner": None,
    "created": today(),
    "why": "",  # 让用户补充
    "what": "",
    "context": {"files": [], "related": []},
    "checklist": []
}
backlog["tasks"].append(new_task)
save_backlog()
```

### 3. 移动状态

```bash
# /backlog move auth-001 planning
```

**检查转换规则：**
```python
allowed = config["transitions"][current_status]
if new_status not in allowed:
    print(f"❌ 不能从 {current_status} 直接跳到 {new_status}")
    print(f"允许的下一步: {allowed}")
    return

task["status"] = new_status
save_backlog()
```

### 4. 认领任务

```bash
# /backlog claim auth-001
```

```python
task["owner"] = "@claude"  # 或 "@human"
save_backlog()
```

### 5. 拆分 Sub-tasks

```bash
# /backlog split auth-001
```

根据任务的 checklist 或 AI 分析，创建子任务：

```python
parent = find_task("auth-001")
sub_tasks = [
    {"id": "auth-001-a", "title": "实现登录 API", "parent": "auth-001", ...},
    {"id": "auth-001-b", "title": "实现注册 API", "parent": "auth-001", ...},
]
backlog["tasks"].extend(sub_tasks)
parent["sub_tasks"] = ["auth-001-a", "auth-001-b"]
save_backlog()
```

### 6. 完成任务

```bash
# /backlog done auth-001
```

```python
task["status"] = "done"
task["completed"] = today()
# 移到 archive
backlog["archive"].append(task)
backlog["tasks"].remove(task)
save_backlog()
```

## 任务结构

```json
{
  "id": "auth-001",
  "title": "用户无法登录",
  "status": "developing",
  "priority": "P1",
  "owner": "@claude",
  "created": "2026-02-02",
  "why": "用户反馈登录失败",
  "what": "检查 JWT 验证逻辑",
  "context": {
    "files": ["src/auth/jwt.py", "tests/test_auth.py"],
    "related": ["api-003"]
  },
  "checklist": [
    "检查 token 过期时间",
    "添加错误日志",
    "编写测试"
  ],
  "sub_tasks": [],
  "parent": null
}
```

## 与 push-to-dev 集成

当 `/push-to-dev` 时：

1. AI 读取 `docs/backlog.json`
2. 找到当前 owner 为 `@claude` 且 status 为 `developing` 的任务
3. PR 描述中引用任务 ID：`Implements: auth-001`
4. 自动移动状态：`developing → testing`

## 与 GitHub 的关系

| 场景 | 用什么 |
|------|--------|
| 内部任务管理 | backlog.json |
| 外部用户报 bug | GitHub Issues → 同步到 backlog |
| 代码 review | GitHub PR |
| CI/CD | GitHub Actions |

**从 GitHub Issue 同步到 backlog：**
```bash
# 当有新 Issue 时，添加到 backlog
gh issue view <N> --json title,body | jq '...' >> docs/backlog.json
```

## 快捷流程

```
/backlog add "问题描述"     → 创建任务（问题）
/backlog claim <id>         → 认领（问题 → 待定方案）
/backlog move <id> designing → 写完思路（待定方案 → 待出设计）
/backlog move <id> reviewing → AI 出完设计（待出设计 → 设计审核）
/backlog move <id> developing → 审核通过（设计审核 → 开发中）
/push-to-dev                 → 代码完成（开发中 → 待测试，自动）
/backlog move <id> deploying → 测试通过（待测试 → 待部署）
/backlog done <id>           → 部署完成（待部署 → Done）
```

## AI 行为

1. **会话开始**：读取 backlog.json，显示待办概览
2. **开始任务前**：检查是否有认领的任务
3. **完成任务后**：更新状态，提醒 git commit
4. **始终保持**：backlog.json 是 single source of truth
