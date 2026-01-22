# FUCE - Few Understand Community Edition

## 一句话描述

加密货币实时价格监控与异动信号检测系统。

## 技术栈

| 层 | 技术 |
|---|------|
| 数据采集 | Python + requests |
| 数据库 | PostgreSQL 15 + TimescaleDB |
| API | Hasura GraphQL Engine |
| 部署 | Docker Compose |
| 前端 | 待开发 |

## 架构图

```
币安 API ──→ [爬虫] ──→ PostgreSQL ──→ [Hasura] ──→ 前端
              │              │
              ↓              ↓
         prices 表      GraphQL API
              │         (自动生成)
              ↓
        [计算器] ──→ indicators 表
              │
              ↓
        [检测器] ──→ signals 表
```

## 模块列表

| 模块 | 文档 | 说明 |
|-----|------|------|
| 爬虫系统 | [../L2/crawlers.md](../L2/crawlers.md) | 数据采集与计算 |
| 数据库 | [../L2/database.md](../L2/database.md) | 表结构与存储 |
| API | [../L2/api.md](../L2/api.md) | GraphQL 接口 |

## API 端点

| 端点 | 地址 |
|-----|------|
| GraphQL | `http://46.224.5.136:8080/v1/graphql` |
| Hasura Console | `http://46.224.5.136:8080` |
| Admin Secret | `fuce_admin_secret` |
