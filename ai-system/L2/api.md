# L2: API 层

## 职责

自动将数据库表暴露为 GraphQL API，供前端查询。

## 技术选型

| 项 | 选择 |
|---|------|
| 引擎 | Hasura GraphQL Engine v2.36.0 |
| 协议 | GraphQL |
| 认证 | Admin Secret |

## 端点

| 端点 | 地址 |
|-----|------|
| GraphQL | `http://46.224.5.136:8080/v1/graphql` |
| Console | `http://46.224.5.136:8080` |
| Admin Secret | `fuce_admin_secret` |

## 可用查询

### prices
```graphql
query {
  prices(order_by: {time: desc}, limit: 10) {
    time
    symbol
    price
  }
}
```

### indicators
```graphql
query {
  indicators(order_by: {time: desc}, limit: 10) {
    time
    symbol
    change_5min_pct
  }
}
```

### signals
```graphql
query {
  signals(order_by: {time: desc}, limit: 20) {
    id
    time
    symbol
    signal_type
    change_pct
  }
}
```

## HTTP 请求示例

```bash
curl -X POST http://46.224.5.136:8080/v1/graphql \
  -H "Content-Type: application/json" \
  -H "x-hasura-admin-secret: fuce_admin_secret" \
  -d '{"query": "{ prices(limit: 5, order_by: {time: desc}) { time symbol price } }"}'
```

## 配置文件

```
hasura/
├── config.yaml
└── metadata/
    └── databases/default/tables/tables.yaml
```
