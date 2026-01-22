# AI System

供 AI 辅助开发的分层文档系统。

## 使用方式

| 场景 | 读取文档 |
|-----|---------|
| 新 AI 了解项目 | `L1/overview.md` |
| 开发某个模块 | `L2/对应模块.md` |
| 修改某个组件 | `L3/对应组件.md` |
| 查询表/服务/信号定义 | `registry/*.yaml` |

## 目录结构

```
ai-system/
├── README.md           # 本文件
├── L1/                 # 项目全貌
│   └── overview.md
├── L2/                 # 模块级
│   ├── crawlers.md
│   ├── database.md
│   └── api.md
├── L3/                 # 组件级
│   ├── binance-price.md
│   ├── indicator-5min.md
│   └── signal-detector.md
└── registry/           # 注册表（YAML 格式）
    ├── tables.yaml     # 数据库表
    ├── services.yaml   # 运行服务
    ├── signals.yaml    # 信号类型
    └── api.yaml        # API 端点
```

## 层级说明

| 层级 | 粒度 | 内容 |
|-----|------|------|
| L1 | 项目 | 架构、技术栈、API 端点 |
| L2 | 模块 | 职责、边界、数据流 |
| L3 | 组件 | 配置、逻辑、文件结构 |
| registry | 注册表 | 结构化数据，供 AI 解析对比 |

## 维护原则

- 代码变更时同步更新对应文档
- 保持精简，只写"是什么"和"怎么用"
- 不记录历史决策，避免上下文膨胀
- registry 使用 YAML 格式，便于程序解析
