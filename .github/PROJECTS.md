# GitHub Projects 配置指南

## 创建 Project

1. 进入仓库页面 → **Projects** 标签 → **New project**
2. 选择 **Board** 模板（看板视图）
3. 命名为 `Lagos Development`

## 推荐的列设置

| 列名 | 说明 |
|------|------|
| Backlog | 待办事项，未开始 |
| Todo | 本周/本迭代计划要做的 |
| In Progress | 正在进行中 |
| Review | 等待 review |
| Done | 已完成 |

## 自动化规则

在 Project Settings → Workflows 中启用：

1. **Item added to project** → 自动设为 `Backlog`
2. **Pull request merged** → 自动移到 `Done`
3. **Issue closed** → 自动移到 `Done`

## 与 Issues 关联

在 Issue 中添加到 Project：
- 右侧边栏 → **Projects** → 选择 `Lagos Development`

## 标签规划

建议创建以下标签：

| 标签 | 颜色 | 说明 |
|------|------|------|
| `bug` | 红色 | Bug 修复 |
| `enhancement` | 蓝色 | 新功能 |
| `documentation` | 绿色 | 文档更新 |
| `infrastructure` | 紫色 | 基础设施 |
| `crawler` | 橙色 | 爬虫相关 |
| `signal` | 黄色 | 信号系统 |
| `frontend` | 青色 | 前端相关 |
| `priority:high` | 红色 | 高优先级 |
| `priority:medium` | 黄色 | 中优先级 |
| `priority:low` | 灰色 | 低优先级 |

## 里程碑

建议按版本创建里程碑：

- `v0.1.0 - 基础架构` - 目标日期：[设置]
- `v0.2.0 - 信号系统` - 目标日期：[设置]
- `v0.3.0 - 新闻热点` - 目标日期：[设置]
- `v1.0.0 - 正式发布` - 目标日期：[设置]
