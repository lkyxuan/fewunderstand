---
name: project
description: Use when managing GitHub Projects and Issues - view board, move status, create issues, split into sub-issues. This is the unified project management skill with strict state transitions.
---

# Project Management

## Overview

GitHub Projects + Issues 统一管理 skill，负责项目进度追踪和协调。

**所有状态变更都通过此 skill 完成。** 其他 skill（push-to-dev、merge-pr）调用此 skill 来更新状态。

**与 openspec 的分工：**
- **project** - 项目管理（看板、Issue 状态、进度追踪）
- **openspec** - 技术设计（proposal、design、tasks）

**Announce at start:** "使用 project skill 管理 GitHub Projects。"

## 配置文件

**配置位置：** `.claude/skills/_config/project.json`

**执行操作前，先读取配置：**

```bash
CONFIG=".claude/skills/_config/project.json"
OWNER=$(jq -r '.github.owner' $CONFIG)
PROJECT_NUM=$(jq -r '.github.project_number' $CONFIG)
PROJECT_ID=$(jq -r '.project.id' $CONFIG)
STATUS_FIELD_ID=$(jq -r '.project.status_field_id' $CONFIG)

# 获取状态选项 ID
get_status_id() {
  jq -r ".status_options[\"$1\"]" $CONFIG
}
```

**重要：状态需要同时更新两个地方！**

| 系统 | 命令 | 用途 |
|------|------|------|
| Issue 标签 | `gh issue edit --add-label` | Issue 页面显示 |
| Project Status | `gh project item-edit` | 看板列显示 |

### 获取 Issue 的 Project Item ID

```bash
ITEM_ID=$(gh project item-list $PROJECT_NUM --owner $OWNER --format json | jq -r ".items[] | select(.content.number == <N>) | .id")
```

### 更新 Project Status

```bash
gh project item-edit \
  --project-id $PROJECT_ID \
  --id $ITEM_ID \
  --field-id $STATUS_FIELD_ID \
  --single-select-option-id $(get_status_id "目标状态")
```

## 8 个状态（统一流程）

所有改动都走同一套流程，没有"小改动跳过"：

```
问题 → 待定方案 → 待出设计 → 设计审核 → 开发中 → 待测试 → 待部署 → Done
  1        2          3          4         5        6        7       8
                                  ↑
                                  └── 打回修改（唯一例外）
```

| # | 状态 | 含义 | 谁做 | 产出 | 下一步 |
|---|------|------|------|------|--------|
| 1 | `问题` | 发现问题/提出需求 | 任何人 | Issue 描述 | → 待定方案 |
| 2 | `待定方案` | 需要人想解决思路 | 人 | 评论里写思路 | → 待出设计 |
| 3 | `待出设计` | 有思路了，需要详细设计 | AI (openspec) | proposal/design/tasks | → 设计审核 |
| 4 | `设计审核` | 设计完成，等待审核 | 人审 AI | 审核意见 | → 开发中 或 → 待出设计(打回) |
| 5 | `开发中` | 按 tasks.md 开发 | AI/人 | 代码 + PR | → 待测试 |
| 6 | `待测试` | 代码完成，等待测试 | 人/QA | 测试结果 | → 待部署 |
| 7 | `待部署` | 测试通过，等待部署 | 运维/人 | 部署确认 | → Done |
| 8 | `Done` | 已部署上线 | - | openspec archive | (结束) |

**辅助标签：** `阻塞`（任何阶段遇到问题时，可叠加）

## 状态转换规则（严格）

**只允许以下转换，不允许跳步骤：**

| 当前状态 | 可转换到 | 触发条件 | 触发方式 |
|---------|---------|----------|----------|
| 问题 | 待定方案 | 确认要处理这个问题 | `/project claim <N>` |
| 待定方案 | 待出设计 | 人写完方案思路 | `/project idea <N>` |
| 待出设计 | 设计审核 | AI 用 openspec 出完设计 | `/project design <N>` |
| 设计审核 | 开发中 | 审核通过 | `/project approve <N>` |
| 设计审核 | 待出设计 | 审核不通过，打回 | `/project reject <N>` |
| 开发中 | 待测试 | PR 创建完成 | `/push-to-dev` 自动调用 |
| 待测试 | 待部署 | PR merge 到 dev | `/merge-pr` 自动调用 |
| 待部署 | Done | PR merge 到 main | `/merge-pr` 自动调用 |

**非法转换示例（会被拒绝）：**
- 问题 → 开发中（必须先经过方案阶段）
- 待测试 → Done（必须先经过待部署）
- 开发中 → 待定方案（不能倒退，除了设计审核打回）

## Sub-Issue 拆分

**时机：** 设计审核通过后，如果 tasks.md 有多个任务，可以拆分成 sub-issues。

```
父 Issue #10 "添加用户认证"
    │
    ├── Sub-Issue #11 "实现登录 API"
    ├── Sub-Issue #12 "实现注册 API"
    └── Sub-Issue #13 "添加 JWT 验证"
```

**规则：**
- 每个 sub-issue 独立走流程：`开发中 → 待测试 → 待部署 → Done`
- 父 Issue 等所有 sub-issues 完成后才能关闭
- Sub-issue 跳过方案阶段（设计已在父 Issue 完成）

## 操作列表

### 1. status - 查看看板状态

```bash
# 查看所有 Issues
gh project item-list 2 --owner lkyxuan

# 按状态筛选
gh issue list --state open --label "问题"
gh issue list --state open --label "开发中"
gh issue list --state open --label "待测试"
```

### 2. create - 创建 Issue

```bash
# 1. 创建 Issue
ISSUE_URL=$(gh issue create \
  --title "<标题>" \
  --body "$(cat <<'EOF'
## 问题描述
<描述问题或需求>

## 期望结果
<期望的解决效果>
EOF
)" \
  --label "问题")

# 提取 Issue 编号
ISSUE_NUM=$(echo $ISSUE_URL | grep -oE '[0-9]+$')

# 2. 等待 Issue 自动添加到 Project（约 1-2 秒）
sleep 2

# 3. 更新 Project Status 为 "问题"
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r ".items[] | select(.content.number == $ISSUE_NUM) | .id")
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id 6025e8f4

echo "✅ Issue #$ISSUE_NUM 已创建，状态：问题"
```

### 3. claim - 认领 Issue（问题 → 待定方案）

```bash
# 1. 更新 Issue 标签
gh issue edit <N> --add-assignee @me
gh issue edit <N> --remove-label "问题" --add-label "待定方案"
gh issue comment <N> --body "已认领，开始思考解决方案"

# 2. 更新 Project Status（同步看板）
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r '.items[] | select(.content.number == <N>) | .id')
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id 3e5e366c
```

### 4. idea - 提交方案思路（待定方案 → 待出设计）

```bash
# 1. 更新 Issue
gh issue comment <N> --body "$(cat <<'EOF'
## 方案思路

### 解决方向
<高层次的解决思路，几句话描述>

### 大致步骤
1. <步骤1>
2. <步骤2>
3. <步骤3>

---
思路确定，请用 openspec 出详细设计
EOF
)"
gh issue edit <N> --remove-label "待定方案" --add-label "待出设计"

# 2. 更新 Project Status
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r '.items[] | select(.content.number == <N>) | .id')
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id 4f07b88d
```

### 5. design - 提交设计（待出设计 → 设计审核）

用 openspec 出详细设计后：

```bash
# 1. 更新 Issue
gh issue edit <N> --remove-label "待出设计" --add-label "设计审核"
gh issue comment <N> --body "$(cat <<'EOF'
## OpenSpec 设计完成

设计文档位置：`openspec/changes/<feature>/`

- proposal.md - 变更说明
- design.md - 技术设计
- tasks.md - 实现任务

请审核设计方案。
EOF
)"

# 2. 更新 Project Status
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r '.items[] | select(.content.number == <N>) | .id')
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id dc9c1608
```

### 6. approve - 审核通过（设计审核 → 开发中）

```bash
# 1. 更新 Issue
gh issue edit <N> --remove-label "设计审核" --add-label "开发中"
gh issue comment <N> --body "设计审核通过，开始开发"

# 2. 更新 Project Status
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r '.items[] | select(.content.number == <N>) | .id')
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id faca3795
```

### 7. reject - 审核不通过（设计审核 → 待出设计）

```bash
# 1. 更新 Issue
gh issue edit <N> --remove-label "设计审核" --add-label "待出设计"
gh issue comment <N> --body "设计需要修改：<具体原因>"

# 2. 更新 Project Status
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r '.items[] | select(.content.number == <N>) | .id')
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id 4f07b88d
```

### 8. split - 拆分 Sub-Issues（设计审核通过后）

根据 `openspec/changes/<feature>/tasks.md` 创建 sub-issues：

```bash
# 为每个任务创建 sub-issue
gh issue create \
  --title "[Sub] <任务标题>" \
  --body "$(cat <<'EOF'
## 父 Issue
#<PARENT_ISSUE_NUMBER>

## 任务来源
openspec/changes/<feature>/tasks.md

## 任务描述
<从 tasks.md 提取的具体任务>

## 完成标准
<验收条件>
EOF
)" \
  --label "开发中"

# 在父 Issue 中记录
gh issue comment <PARENT> --body "已拆分 sub-issues: #11, #12, #13"
```

### 9. move - 通用状态移动

**只在特殊情况下使用，正常流程用上面的专用命令。**

```bash
# 获取 Item ID（所有 move 操作都需要）
ITEM_ID=$(gh project item-list 2 --owner lkyxuan --format json | jq -r '.items[] | select(.content.number == <N>) | .id')

# 开发中 → 待测试（通常由 /push-to-dev 自动调用）
gh issue edit <N> --remove-label "开发中" --add-label "待测试"
gh issue comment <N> --body "代码完成，等待测试"
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id 8c02b904

# 待测试 → 待部署（通常由 /merge-pr 到 dev 自动调用）
gh issue edit <N> --remove-label "待测试" --add-label "待部署"
gh issue comment <N> --body "测试通过，等待部署到生产"
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id a7db81bf

# 待部署 → Done（通常由 /merge-pr 到 main 自动调用）
gh issue edit <N> --remove-label "待部署" --add-label "部署完成"
gh issue close <N> --comment "已部署到生产环境"
gh project item-edit --project-id PVT_kwHOBNDkTM4BN_Zk --id $ITEM_ID --field-id PVTSSF_lAHOBNDkTM4BN_Zkzg80v3U --single-select-option-id 80b26af7
```

### 10. block / unblock - 阻塞管理

```bash
# 标记阻塞（可在任何状态叠加）
gh issue edit <N> --add-label "阻塞"
gh issue comment <N> --body "阻塞原因：<问题描述>"

# 解除阻塞
gh issue edit <N> --remove-label "阻塞"
gh issue comment <N> --body "阻塞已解除：<解决方案>"
```

## 直接模式命令

用户可以直接指定操作：

| 命令 | 作用 | 状态变更 |
|------|------|----------|
| `/project status` | 查看看板 | - |
| `/project create "标题"` | 创建 Issue | → 问题 |
| `/project claim <N>` | 认领 Issue | 问题 → 待定方案 |
| `/project idea <N>` | 提交方案思路 | 待定方案 → 待出设计 |
| `/project design <N>` | 提交设计 | 待出设计 → 设计审核 |
| `/project approve <N>` | 审核通过 | 设计审核 → 开发中 |
| `/project reject <N>` | 审核不通过 | 设计审核 → 待出设计 |
| `/project split <N>` | 拆分 sub-issues | - |
| `/project block <N>` | 标记阻塞 | +阻塞标签 |
| `/project unblock <N>` | 解除阻塞 | -阻塞标签 |

## 与其他 Skill 的协作

| Skill | 调用 project 的功能 |
|-------|---------------------|
| `/push-to-dev` | `move <N> 待测试` |
| `/merge-pr` (到 dev) | `move <N> 待部署` |
| `/merge-pr` (到 main) | `move <N> Done` |

## 完整工作流示例

```
1. 发现问题
   /project create "用户无法登录"
   → Issue #10 创建，状态：问题

2. 认领并思考方案
   /project claim 10
   → 状态：待定方案

3. 写方案思路
   /project idea 10
   → 状态：待出设计

4. AI 出详细设计
   openspec proposal/design/tasks
   /project design 10
   → 状态：设计审核

5. 人审核设计
   /project approve 10
   → 状态：开发中

6. (可选) 拆分任务
   /project split 10
   → 创建 sub-issues #11, #12, #13

7. 开发完成
   /push-to-dev
   → 状态：待测试（自动）

8. 测试通过，合并到 dev
   /merge-pr
   → 状态：待部署（自动）

9. 部署到生产，合并到 main
   /merge-pr
   → 状态：Done（自动关闭）
```

## 标签列表

**主流程（8 个，互斥）：**
- `问题` - 紫色
- `待定方案` - 橙色
- `待出设计` - 浅蓝
- `设计审核` - 蓝色
- `开发中` - 黄色
- `待测试` - 浅绿
- `待部署` - 绿色
- `部署完成` - 深绿

**辅助（可叠加）：**
- `阻塞` - 红色

## Red Flags

**Never:**
- 跳过状态（必须按顺序走）
- 设计没审核就开始写代码
- 忘记更新状态（其他人不知道进度）
- 同一任务多人同时做（先检查看板）

**Always:**
- 开始前检查看板，避免重复
- 状态变更时添加评论说明
- 人出思路 → AI 出设计 → 人审核
- 复杂功能拆分 sub-issues
