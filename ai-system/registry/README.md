# Registry - 注册表

系统中所有实体的结构化注册信息，供 AI 读取和对比。

## 文件列表

| 文件 | 内容 |
|-----|------|
| `tables.yaml` | 数据库表结构 |
| `services.yaml` | 运行服务列表 |
| `signals.yaml` | 信号类型定义 |
| `api.yaml` | API 端点信息 |

## 使用场景

- AI 需要了解有哪些表 → 读 `tables.yaml`
- AI 需要知道服务配置 → 读 `services.yaml`
- AI 需要理解信号含义 → 读 `signals.yaml`
- AI 需要调用 API → 读 `api.yaml`

## 维护原则

- 新增表/服务/信号时同步更新
- 保持 YAML 格式一致
- 字段说明用中文
