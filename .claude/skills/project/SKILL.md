---
name: project
description: Use when managing GitHub Projects and Issues - initialize projects, update status, link PRs to issues. This is the unified skill for all GitHub project management.
---

# GitHub Project Management（统一入口）

## Overview

GitHub Projects + Issues 的统一管理 skill。所有状态管理、看板操作、PR 关联都通过这个 skill。

**这是唯一的项目管理入口，其他 skills（push-to-dev、merge-pr）调用此 skill。**

**Announce at start:** "使用 project skill 管理 GitHub Projects。"

## 前置条件

首次使用需要授权 Projects 权限（用户在终端执行）：

```bash
gh auth refresh -s project,read:project
```

## 操作列表

调用 `/project` 时，询问要执行哪个操作：

| 操作 | 说明 |
|------|------|
| **init** | 初始化新项目（创建 Project + 字段 + 添加 Issues） |
| **status** | 查看当前项目状态 |
| **move** | 移动 Issue 到指定状态列 |
| **add** | 添加 Issue 到 Project |
| **link** | PR 关联 Issue |
| **design** | 为 Issue 出技术方案（写到评论） |
| **split** | 将大 Issue 拆分成子 Issues |

---

## 1. 初始化项目（/project init）

一键初始化完整的项目看板：

### Step 1: 检查权限

```bash
gh auth status 2>&1 | grep -E 'project|read:project'
```

如果没有 project 权限，提示用户执行：
```bash
gh auth refresh -s project,read:project
```

### Step 2: 获取仓库信息

```bash
# 获取仓库 owner
OWNER=$(gh repo view --json owner -q '.owner.login')
REPO=$(gh repo view --json name -q '.name')
echo "仓库: $OWNER/$REPO"
```

### Step 3: 创建 Project

```bash
gh project create --title "$REPO Development" --owner $OWNER
```

### Step 4: 获取 Project ID

```bash
PROJECT_INFO=$(gh project list --owner $OWNER --format json | jq '.projects[0]')
PROJECT_NUM=$(echo $PROJECT_INFO | jq -r '.number')
PROJECT_ID=$(echo $PROJECT_INFO | jq -r '.id')
echo "Project #$PROJECT_NUM 创建成功"
```

### Step 5: 创建「状态」字段（7 个选项）

```bash
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    dataType: SINGLE_SELECT
    name: "状态"
    singleSelectOptions: [
      {name: "提案", color: PURPLE, description: "新任务等待处理"}
      {name: "待出方案", color: ORANGE, description: "需要先出技术方案"}
      {name: "方案审核", color: BLUE, description: "方案已出等待审核"}
      {name: "正在工作", color: YELLOW, description: "正在开发中"}
      {name: "代码完成", color: GREEN, description: "代码开发完成"}
      {name: "测试完成", color: GREEN, description: "测试验证通过"}
      {name: "Done", color: GRAY, description: "已部署完成"}
    ]
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}'
```

### Step 6: 创建日期字段

```bash
# 开始时间
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    dataType: DATE
    name: "开始时间"
  }) {
    projectV2Field { ... on ProjectV2Field { id name } }
  }
}'

# 截止时间
gh api graphql -f query='
mutation {
  createProjectV2Field(input: {
    projectId: "'$PROJECT_ID'"
    dataType: DATE
    name: "截止时间"
  }) {
    projectV2Field { ... on ProjectV2Field { id name } }
  }
}'
```

### Step 7: 添加所有 open Issues

```bash
for url in $(gh issue list --state open --json url -q '.[].url'); do
  gh project item-add $PROJECT_NUM --owner $OWNER --url "$url"
  echo "Added: $url"
done
```

### Step 8: 输出结果

```
✅ 项目初始化完成！

Project: $REPO Development (#$PROJECT_NUM)
字段:
  - 状态（7 列：提案 → 待出方案 → 方案审核 → 正在工作 → 代码完成 → 测试完成 → Done）
  - 开始时间
  - 截止时间
Issues: 已添加 X 个

🔗 打开看板: gh project view $PROJECT_NUM --owner $OWNER --web

⚠️ 请手动配置:
1. 在 Web 上隐藏默认的 "Status" 字段
2. 配置 Workflows 自动化
3. 创建 Board 视图，按「状态」分组
```

---

## 2. 查看状态（/project status）

```bash
# 获取 Project 信息
OWNER=$(gh repo view --json owner -q '.owner.login')
PROJECT_NUM=$(gh project list --owner $OWNER --format json | jq '.projects[0].number')

# 列出所有 Items
gh project item-list $PROJECT_NUM --owner $OWNER --format json | jq '.items[] | {title: .content.title, status: .["状态"]}'

# 按状态统计
echo "=== 状态统计 ==="
gh project item-list $PROJECT_NUM --owner $OWNER --format json | jq -r '.items[].["状态"] // "未设置"' | sort | uniq -c
```

---

## 3. 移动状态（/project move）

将 Issue 移动到指定状态列。

### 状态流转规则

```
提案 → 待出方案 → 方案审核 → 正在工作 → 代码完成 → 测试完成 → Done
                              ↑
                      (小改动可跳过方案阶段)
```

### 操作步骤

**1. 获取字段和选项 ID：**
```bash
OWNER=$(gh repo view --json owner -q '.owner.login')
PROJECT_NUM=$(gh project list --owner $OWNER --format json | jq '.projects[0].number')

# 获取「状态」字段信息
gh project field-list $PROJECT_NUM --owner $OWNER --format json | jq '.fields[] | select(.name == "状态")'
```

**2. 获取 Item ID：**
```bash
ITEM_ID=$(gh project item-list $PROJECT_NUM --owner $OWNER --format json | jq -r '.items[] | select(.content.number == <ISSUE_NUMBER>) | .id')
```

**3. 更新状态：**
```bash
gh project item-edit \
  --project-id <PROJECT_ID> \
  --id $ITEM_ID \
  --field-id <STATUS_FIELD_ID> \
  --single-select-option-id <OPTION_ID>
```

### 状态选项 ID 参考

初始化后记录这些 ID，供后续使用：

| 状态 | 用途 |
|------|------|
| 提案 | 新任务 |
| 待出方案 | 需要技术方案 |
| 方案审核 | 等待审核 |
| 正在工作 | 开发中 |
| 代码完成 | push-to-dev 后 |
| 测试完成 | 测试通过 |
| Done | merge-pr 后 |

---

## 4. 添加 Issue（/project add）

```bash
OWNER=$(gh repo view --json owner -q '.owner.login')
PROJECT_NUM=$(gh project list --owner $OWNER --format json | jq '.projects[0].number')

# 添加单个 Issue
gh project item-add $PROJECT_NUM --owner $OWNER --url $(gh issue view <ISSUE_NUMBER> --json url -q .url)

# 添加所有 open Issues
for url in $(gh issue list --state open --json url -q '.[].url'); do
  gh project item-add $PROJECT_NUM --owner $OWNER --url "$url"
done
```

---

## 5. PR 关联 Issue（/project link）

创建 PR 时自动关联 Issue，合并后自动关闭。

### 查找相关 Issue

```bash
# 方法1: 按标签查找正在工作的 Issue
ISSUE_NUM=$(gh issue list --state open --label "正在工作" --json number -q '.[0].number')

# 方法2: 按分支名搜索
BRANCH=$(git branch --show-current)
ISSUE_NUM=$(gh issue list --state open --search "$BRANCH" --json number -q '.[0].number')
```

### 创建关联 PR

```bash
gh pr create --base dev --title "<标题>" --body "$(cat <<'EOF'
## Summary
<改动描述>

Closes #<ISSUE_NUMBER>

## Test Plan
- [ ] 本地测试通过
- [ ] 相关功能验证
EOF
)"
```

**关键词**（合并时自动关闭 Issue + 移动到 Done）：
- `Closes #123`
- `Fixes #123`
- `Resolves #123`

---

## 6. 出技术方案（/project design）

为 Issue 出技术方案，写到 Issue 评论里。对应 openspec 的 proposal + design 阶段。

### 流程

```
读取 Issue → AI 分析 → 生成技术方案 → 写到评论 → 移到「方案审核」
```

### Step 1: 读取 Issue 内容

```bash
ISSUE_NUM=<ISSUE_NUMBER>

# 获取 Issue 标题和内容
gh issue view $ISSUE_NUM --json title,body,labels
```

### Step 2: AI 分析并生成方案

分析 Issue 需求，生成技术方案，包含：

```markdown
## 技术方案

### 1. 需求理解
<对 Issue 需求的理解>

### 2. 实现思路
<整体技术方案>

### 3. 涉及文件
- `path/to/file1.py` - 说明
- `path/to/file2.ts` - 说明

### 4. 数据库变更（如有）
<表结构、字段变更>

### 5. API 变更（如有）
<新增/修改的接口>

### 6. 风险点
- 风险1：说明 + 应对方案
- 风险2：说明 + 应对方案

### 7. 预计拆分任务
- [ ] 任务1
- [ ] 任务2
- [ ] 任务3

---
请审核此方案 @reviewer
```

### Step 3: 写到 Issue 评论

```bash
gh issue comment $ISSUE_NUM --body "$DESIGN_CONTENT"
```

### Step 4: 更新状态

```bash
# 移到「方案审核」状态
# 调用 /project move
```

### 审核流程

- **AI 出方案** → 人审核
- **人出方案** → AI 审核（检查完整性、风险点）

审核通过后，执行 `/project split` 拆分任务。

---

## 7. 拆分子 Issues（/project split）

将大 Issue 拆分成可执行的子 Issues。

### 流程

```
读取父 Issue → 读取方案评论 → AI 拆分任务 → 创建子 Issues → 关联到父 Issue
```

### Step 1: 读取父 Issue 和方案

```bash
PARENT_ISSUE=<ISSUE_NUMBER>

# 获取 Issue 内容
gh issue view $PARENT_ISSUE --json title,body

# 获取评论（找技术方案）
gh issue view $PARENT_ISSUE --comments
```

### Step 2: AI 分析拆分任务

从技术方案的「预计拆分任务」或 AI 分析，生成 3-7 个子任务。

每个子任务包含：
- 标题（清晰、可执行）
- 描述（做什么、验收标准）
- 依赖关系

### Step 3: 创建子 Issues

```bash
# 获取仓库信息
OWNER=$(gh repo view --json owner -q '.owner.login')
REPO=$(gh repo view --json name -q '.name')

# 创建子 Issue
gh issue create \
  --title "子任务标题" \
  --body "$(cat <<'EOF'
## 任务描述
<具体要做什么>

## 父任务
- 关联 #$PARENT_ISSUE

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 依赖
- 依赖 #xx（如有）
EOF
)" \
  --label "提案"
```

### Step 4: 关联到父 Issue

在父 Issue 中添加子 Issue 列表：

```bash
gh issue comment $PARENT_ISSUE --body "$(cat <<'EOF'
## 子任务拆分完成

- [ ] #101 子任务1
- [ ] #102 子任务2
- [ ] #103 子任务3

所有子任务完成后，此 Issue 将自动关闭。
EOF
)"
```

### Step 5: 添加到 Project

```bash
# 添加所有新创建的子 Issues 到 Project
for issue_url in <新创建的 Issue URLs>; do
  gh project item-add $PROJECT_NUM --owner $OWNER --url "$issue_url"
done
```

### 完整示例

```
父 Issue #33: "实现用户认证系统"
    ↓
/project design 33 → 生成技术方案
    ↓
审核通过
    ↓
/project split 33
    ↓
创建子 Issues:
  #101: "创建 users 表"
  #102: "实现登录 API"
  #103: "实现注册 API"
  #104: "前端登录页面"
  #105: "前端注册页面"
    ↓
每个子 Issue 独立开发 → PR（Closes #101）
    ↓
所有子 Issue 完成 → 父 Issue #33 完成
```

---

## 供其他 Skills 调用

### push-to-dev 调用

```
在 Step 5 模式 B 中：
1. 调用 /project link 查找相关 Issue
2. 创建 PR 时自动添加 Closes #xx
3. 调用 /project move 将 Issue 移到「代码完成」
```

### merge-pr 调用

```
在 Step 6 中：
1. PR 合并后，GitHub 自动关闭关联的 Issue
2. Project 自动化将 Issue 移到 Done
```

---

## Quick Reference

| 操作 | 命令 | 说明 |
|------|------|------|
| 初始化项目 | `/project init` | 创建 Project + 字段 |
| 查看状态 | `/project status` | 查看看板状态 |
| 移动状态 | `/project move <issue> <状态>` | 更新 Issue 状态 |
| 添加 Issue | `/project add <issue>` | 添加到看板 |
| 关联 PR | `/project link <issue>` | PR 关联 Issue |
| **出方案** | `/project design <issue>` | AI 出技术方案 |
| **拆分** | `/project split <issue>` | 拆成子 Issues |

## 完整开发流程

```
1. 创建 Issue（提案）
   gh issue create --title "功能描述" --label "提案"
       ↓
2. /project design #33 → AI 出技术方案
       ↓
3. 方案审核（人审 AI 方案，或 AI 审人方案）
       ↓
4. /project split #33 → 拆成子 Issues
       ↓
5. 认领子 Issue → /project move #101 正在工作
       ↓
6. 开发 → /push-to-dev（创建 PR，Closes #101）
       ↓
7. Review → /merge-pr → 子 Issue 自动关闭
       ↓
8. 所有子 Issue 完成 → 父 Issue 完成
```

## 状态列颜色

| 状态 | 颜色 | 说明 |
|------|------|------|
| 提案 | 🟣 紫色 | 新任务等待处理 |
| 待出方案 | 🟠 橙色 | 需要先出技术方案 |
| 方案审核 | 🔵 蓝色 | 方案已出等待审核 |
| 正在工作 | 🟡 黄色 | 正在开发中 |
| 代码完成 | 🟢 绿色 | 代码开发完成 |
| 测试完成 | 🟢 绿色 | 测试验证通过 |
| Done | ⚪ 灰色 | 已部署完成 |

## 与 Spec 规格文档集成

项目保留 `openspec/specs/` 目录作为功能规格的 source of truth。

### 目录结构

```
openspec/
├── project.md        ← 项目概述
└── specs/            ← 功能规格（核心）
    ├── frontend-dashboard/spec.md
    ├── infrastructure/spec.md
    ├── kline-data-collection/spec.md
    ├── news-crawler/spec.md
    └── price-signals/spec.md
```

### AI 改代码前必须

**1. 查找相关 spec：**
```bash
ls openspec/specs/
# 或搜索关键词
grep -r "关键词" openspec/specs/
```

**2. 阅读 spec 了解需求：**
```bash
cat openspec/specs/<功能>/spec.md
```

**3. 按 spec 要求实现**

### 更新 spec

当功能变更时，同步更新 spec：
```bash
# 编辑对应的 spec.md
vim openspec/specs/<功能>/spec.md
```

---

## Red Flags

**Never:**
- 不授权就操作 Project
- 忘记在 PR 中写 `Closes #xx`
- 跳过方案直接开发大改动
- **改代码前不看 spec**

**Always:**
- 新项目先执行 `/project init`
- 创建 PR 时关联 Issue
- 状态变更通过此 skill 操作
- **改代码前先读 openspec/specs/xxx/spec.md**
