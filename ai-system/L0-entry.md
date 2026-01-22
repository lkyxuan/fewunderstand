# AI 入口

你正在参与 **FUCE (Few Understand Community Edition)** 项目的开发。

这是一个加密货币实时价格监控与异动信号检测系统。

## 根据你的任务，选择读取路径

### 我是新来的，需要了解项目
```
1. 读 L1/overview.md     → 项目全貌
2. 读 registry/tables.yaml → 了解数据结构
```

### 我要开发前端
```
1. 读 L1/overview.md         → 了解架构
2. 读 registry/api.yaml      → API 端点和查询示例
3. 读 registry/tables.yaml   → 表结构
4. 读 registry/signals.yaml  → 信号类型（用于展示）
```

### 我要开发/修改爬虫
```
1. 读 L2/crawlers.md             → 爬虫模块概览
2. 读 L3/对应组件.md             → 具体组件
3. 读 registry/services.yaml     → 服务配置
```

### 我要添加新的数据表
```
1. 读 L2/database.md         → 数据库模块
2. 读 registry/tables.yaml   → 现有表结构（参考格式）
3. 改完后更新 registry/tables.yaml
```

### 我要添加新的信号类型
```
1. 读 L3/signal-detector.md  → 信号检测逻辑
2. 读 registry/signals.yaml  → 现有信号定义
3. 改完后更新 registry/signals.yaml
```

### 我要调试/排查问题
```
1. 读 registry/services.yaml → 服务列表和依赖关系
2. 读 L3/对应组件.md         → 组件详情
```

## 文档结构速查

| 路径 | 内容 |
|-----|------|
| `L1/` | 项目全貌 |
| `L2/` | 模块级（crawlers, database, api） |
| `L3/` | 组件级（各个服务） |
| `registry/` | 注册表（YAML 格式，可解析） |

## 重要原则

1. **先读文档，再读代码** — 文档是代码的摘要
2. **改代码后更新文档** — 保持同步
3. **registry 是真相来源** — 表/服务/信号的定义以 YAML 为准
