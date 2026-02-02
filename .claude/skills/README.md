# Issue-Driven Project Management Skills

基于 GitHub Projects + Issues 的项目管理 skills，实现 8 列状态流程和强制检查机制。

## 核心理念

**Issue-Driven Development（IDD）**：所有改动必须先有 Issue，按流程推进，状态可追溯。

```
问题 → 待定方案 → 待出设计 → 设计审核 → 开发中 → 待测试 → 待部署 → Done
```

## Skills 列表

| Skill | 命令 | 用途 |
|-------|------|------|
| setup | `/setup` | 新项目初始化（只需运行一次） |
| project | `/project` | 查看看板、创建 Issue、移动状态 |
| push-to-dev | `/push-to-dev` | 推送代码、创建 PR（检查 Issue 在「开发中」） |
| merge-pr | `/merge-pr <N>` | 合并 PR（检查 Issue 状态匹配） |

## 快速开始

### 1. 复制 skills 到新项目

```bash
cp -r .claude/skills /path/to/new-project/.claude/
```

### 2. 初始化

```bash
# 在新项目中运行
/setup
```

这会：
- 创建 GitHub Project
- 创建状态标签
- 生成配置文件

### 3. 手动完成（GitHub UI）

1. 打开创建的 Project
2. 添加 8 个状态列：问题、待定方案、待出设计、设计审核、开发中、待测试、待部署、Done
3. 删除默认的 Todo/In Progress/Done
4. 启用 "Auto-add to project"

### 4. 更新配置文件

运行 `/setup` 的 Step 5 获取状态选项 ID，填入 `.claude/skills/_config/project.json`

## 配置文件

`.claude/skills/_config/project.json`：

```json
{
  "github": {
    "owner": "your-username",
    "repo": "your-repo",
    "project_number": 1
  },
  "project": {
    "id": "PVT_xxx",
    "status_field_id": "PVTSSF_xxx"
  },
  "status_options": {
    "问题": "option-id-1",
    "待定方案": "option-id-2",
    ...
  }
}
```

## 8 列状态流程

| # | 状态 | 含义 | 谁做 | 下一步 |
|---|------|------|------|--------|
| 1 | 问题 | 发现问题/提出需求 | 任何人 | `/project claim` |
| 2 | 待定方案 | 需要人想解决思路 | 人 | `/project idea` |
| 3 | 待出设计 | 有思路了，出详细设计 | AI | `/project design` |
| 4 | 设计审核 | 设计完成，等待审核 | 人审 | `/project approve` |
| 5 | 开发中 | 按设计开发 | AI/人 | `/push-to-dev` |
| 6 | 待测试 | 代码完成，等待测试 | QA | `/merge-pr` (到 dev) |
| 7 | 待部署 | 测试通过，等待部署 | 运维 | `/merge-pr` (到 main) |
| 8 | Done | 已部署上线 | - | (结束) |

## 状态检查（强制）

### push-to-dev

Issue 必须在「开发中」才能推送：
```
❌ Issue #10 当前状态是「待出设计」，不能直接推送代码。

必须先完成以下步骤：
1. /project design 10   → 设计审核
2. /project approve 10  → 开发中
3. 然后才能 /push-to-dev
```

### merge-pr

- Merge 到 dev：Issue 必须在「待测试」
- Merge 到 main：Issue 必须在「待部署」

## 工作流示例

```bash
# 1. 发现问题，创建 Issue
/project create "用户无法登录"

# 2. 认领并思考方案
/project claim 10

# 3. 写方案思路
/project idea 10

# 4. AI 出详细设计
# (使用 openspec 或其他工具)
/project design 10

# 5. 审核通过
/project approve 10

# 6. 开发完成，推送代码
/push-to-dev

# 7. 测试通过，合并到 dev
/merge-pr 42

# 8. 部署完成，合并到 main
/merge-pr 43
```

## 文件结构

```
.claude/skills/
├── _config/
│   └── project.json        # 项目配置（每个项目不同）
├── _setup/
│   └── SKILL.md            # 初始化 skill
├── project/
│   └── SKILL.md            # 项目管理
├── push-to-dev/
│   └── SKILL.md            # 推送代码
├── merge-pr/
│   └── SKILL.md            # 合并 PR
└── README.md               # 本文件
```

## 注意事项

1. **配置文件不要提交到公开仓库**（包含项目 ID）
2. **每个项目需要独立配置**
3. **GitHub Projects UI 需要手动创建状态列**（API 限制）

## 自定义

### 修改状态数量

如果不需要 8 列，可以精简：

```
简化版（5 列）：
问题 → 设计中 → 开发中 → 测试中 → Done
```

修改：
1. `project.json` 的 `status_options`
2. `project/SKILL.md` 的状态转换规则
3. GitHub Project 的状态列

### 修改分支策略

默认：`feature → dev → main`

如果只用 main：修改 `project.json` 的 `branches` 配置
