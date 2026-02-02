---
name: setup
description: Use when setting up project management skills in a new repository. Creates GitHub Project, labels, and generates config file.
---

# Project Setup

## Overview

初始化项目管理 skills，包括：
1. 创建 GitHub Project（8 列看板）
2. 创建状态标签
3. 生成配置文件

**只需在新项目中运行一次。**

**Announce at start:** "使用 setup skill 初始化项目管理。"

## Prerequisites

- `gh` CLI 已登录
- 仓库已创建

## The Process

### Step 1: 获取仓库信息

```bash
# 获取当前仓库的 owner 和 repo
REPO_INFO=$(gh repo view --json owner,name)
OWNER=$(echo $REPO_INFO | jq -r '.owner.login')
REPO=$(echo $REPO_INFO | jq -r '.name')
echo "仓库: $OWNER/$REPO"
```

### Step 2: 创建 GitHub Project

```bash
# 创建项目
PROJECT_URL=$(gh project create --owner $OWNER --title "$REPO 项目管理" --format json | jq -r '.url')
PROJECT_NUMBER=$(echo $PROJECT_URL | grep -oE '[0-9]+$')
echo "项目创建成功: $PROJECT_URL"
```

### Step 3: 获取 Project ID 和 Status Field ID

```bash
# 获取 Project ID
PROJECT_ID=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
      }
    }
  }
' -f owner="$OWNER" -F number=$PROJECT_NUMBER --jq '.data.user.projectV2.id')

# 获取 Status Field ID
STATUS_FIELD_ID=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            id
          }
        }
      }
    }
  }
' -f owner="$OWNER" -F number=$PROJECT_NUMBER --jq '.data.user.projectV2.field.id')

echo "Project ID: $PROJECT_ID"
echo "Status Field ID: $STATUS_FIELD_ID"
```

### Step 4: 创建 8 个状态选项

使用 GraphQL 创建状态选项：

```bash
# 定义状态列表
STATUSES=("问题" "待定方案" "待出设计" "设计审核" "开发中" "待测试" "待部署" "Done")

# 注意：GitHub Projects 默认有一些状态，需要先清理再创建
# 这里简化处理，假设手动在 UI 中创建状态列

echo "请在 GitHub Projects UI 中创建以下状态列："
for s in "${STATUSES[@]}"; do
  echo "  - $s"
done
```

### Step 5: 获取状态选项 ID

```bash
# 获取所有状态选项 ID
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        field(name: "Status") {
          ... on ProjectV2SingleSelectField {
            options {
              id
              name
            }
          }
        }
      }
    }
  }
' -f owner="$OWNER" -F number=$PROJECT_NUMBER --jq '.data.user.projectV2.field.options'
```

### Step 6: 创建标签

```bash
# 创建状态标签（主流程）
gh label create "问题" --color "8B5CF6" --description "发现问题/提出需求" || true
gh label create "待定方案" --color "F97316" --description "需要人想解决思路" || true
gh label create "待出设计" --color "38BDF8" --description "有思路了，需要详细设计" || true
gh label create "设计审核" --color "3B82F6" --description "设计完成，等待审核" || true
gh label create "开发中" --color "FACC15" --description "正在开发" || true
gh label create "待测试" --color "86EFAC" --description "代码完成，等待测试" || true
gh label create "待部署" --color "22C55E" --description "测试通过，等待部署" || true
gh label create "部署完成" --color "15803D" --description "已部署上线" || true

# 辅助标签
gh label create "阻塞" --color "EF4444" --description "遇到阻塞问题" || true

echo "✅ 标签创建完成"
```

### Step 7: 生成配置文件

将上面获取的信息写入配置文件：

```bash
cat > .claude/skills/_config/project.json << EOF
{
  "github": {
    "owner": "$OWNER",
    "repo": "$REPO",
    "project_number": $PROJECT_NUMBER
  },
  "project": {
    "id": "$PROJECT_ID",
    "status_field_id": "$STATUS_FIELD_ID"
  },
  "status_options": {
    "问题": "<从 Step 5 获取>",
    "待定方案": "<从 Step 5 获取>",
    "待出设计": "<从 Step 5 获取>",
    "设计审核": "<从 Step 5 获取>",
    "开发中": "<从 Step 5 获取>",
    "待测试": "<从 Step 5 获取>",
    "待部署": "<从 Step 5 获取>",
    "Done": "<从 Step 5 获取>"
  },
  "labels": {
    "status": ["问题", "待定方案", "待出设计", "设计审核", "开发中", "待测试", "待部署", "部署完成"],
    "auxiliary": ["阻塞"]
  },
  "branches": {
    "dev": "dev",
    "main": "main"
  }
}
EOF

echo "✅ 配置文件生成：.claude/skills/_config/project.json"
echo "⚠️ 请手动填入 status_options 的 ID（从 Step 5 输出复制）"
```

### Step 8: 启用项目自动添加

在 GitHub Projects Settings 中启用：
- **Auto-add to project** - 自动将新 Issue 添加到项目

### Step 9: 验证配置

```bash
# 测试创建一个 Issue 并设置状态
gh issue create --title "测试 Issue" --body "测试配置是否正确" --label "问题"

# 检查是否自动添加到项目
gh project item-list $PROJECT_NUMBER --owner $OWNER
```

## 输出

```
✅ 项目管理初始化完成！

GitHub Project: <project_url>
配置文件: .claude/skills/_config/project.json

已创建：
- 8 个状态标签
- 1 个辅助标签（阻塞）
- 配置文件

下一步：
1. 在 GitHub Projects UI 中创建 8 个状态列
2. 运行 Step 5 获取状态选项 ID
3. 填入配置文件
4. 开始使用 /project、/push-to-dev、/merge-pr
```

## 手动步骤（GitHub UI）

由于 GitHub API 对 Projects 状态列的创建支持有限，以下步骤需要手动完成：

1. 打开 Project URL
2. 点击 Status 列的 "+" 添加选项
3. 按顺序创建：问题、待定方案、待出设计、设计审核、开发中、待测试、待部署、Done
4. 删除默认的 Todo/In Progress/Done 选项
