# L2: 数据库

## 职责

存储所有业务数据，使用 TimescaleDB 优化时序查询。

## 技术选型

| 项 | 选择 |
|---|------|
| 数据库 | PostgreSQL 15 |
| 时序扩展 | TimescaleDB 2.x |
| 连接信息 | `fuce:fuce_dev_password@postgres:5432/fuce` |

## 表结构

| 表 | 说明 | 文档 |
|---|------|------|
| prices | 实时价格 | [database-schema.md](database-schema.md#1-prices---实时价格) |
| indicators | 技术指标 | [database-schema.md](database-schema.md#2-indicators---技术指标) |
| signals | 交易信号 | [database-schema.md](database-schema.md#3-signals---交易信号) |

## 数据保留

所有表启用 TimescaleDB hypertable，支持自动压缩和数据保留策略。

## 初始化脚本

```
db/init/
├── 00_init.sql      # 启用 TimescaleDB
├── 01_tables.sql    # 创建表
└── 02_timescale.sql # 配置 hypertable
```

## 访问方式

- **应用内**: 通过环境变量 `DB_HOST`, `DB_PORT` 等连接
- **外部**: 通过 Hasura GraphQL API 查询
