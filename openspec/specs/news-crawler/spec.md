## ADDED Requirements

### Requirement: news 数据表
系统 MUST 提供 `news` 表存储新闻数据，包含时间、来源、标题、链接、摘要字段。

#### Scenario: 表结构
- **WHEN** 数据库初始化完成
- **THEN** `news` 表存在且包含 `id`, `time`, `source`, `title`, `link`, `summary` 字段

#### Scenario: 去重约束
- **WHEN** 插入相同 `(source, link)` 的新闻
- **THEN** 不产生重复记录

### Requirement: Hasura GraphQL 集成
系统 MUST 通过 Hasura 自动追踪 `news` 表并提供 GraphQL 查询和订阅。

#### Scenario: 查询新闻
- **WHEN** 发起 GraphQL Query `news(limit: 50, order_by: {time: desc})`
- **THEN** 返回最新50条新闻

#### Scenario: 实时订阅
- **WHEN** `news` 表插入新记录
- **THEN** GraphQL Subscription 推送新数据给订阅者

### Requirement: 假数据模拟器
系统 MUST 提供假数据模拟器，用于验证前端信息流效果。

#### Scenario: 定时插入
- **WHEN** 模拟器启动
- **THEN** 每 N 秒向 `news` 表插入一条假新闻

#### Scenario: 随机来源
- **WHEN** 插入假新闻
- **THEN** 随机选择来源（coindesk/jinse/theblock 等）
