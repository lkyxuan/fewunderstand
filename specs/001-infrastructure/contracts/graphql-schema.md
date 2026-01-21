# GraphQL Schema Contract

**Branch**: `001-infrastructure` | **Date**: 2026-01-21

## Overview

Hasura 自动从数据库表生成 GraphQL schema。本文档记录预期的 API 契约，用于前端开发参考。

## Type Definitions

### prices

```graphql
type prices {
  time: timestamptz!
  symbol: String!
  price: numeric!
  volume_24h: numeric
  source: String
}

type prices_aggregate {
  aggregate: prices_aggregate_fields
  nodes: [prices!]!
}
```

### klines

```graphql
type klines {
  time: timestamptz!
  symbol: String!
  open: numeric!
  high: numeric!
  low: numeric!
  close: numeric!
  volume: numeric
}
```

### indicators

```graphql
type indicators {
  time: timestamptz!
  symbol: String!
  change_5min: numeric
  change_15min: numeric
  change_1h: numeric
  volume_change: numeric
}
```

### signals

```graphql
type signals {
  id: bigint!
  time: timestamptz!
  symbol: String!
  signal_type: String!
  change_pct: numeric
  price: numeric
  metadata: jsonb
}
```

### news

```graphql
type news {
  id: bigint!
  time: timestamptz!
  source: String!
  title: String!
  url: String
  content: String
  crawled_at: timestamptz!
}
```

### word_freq

```graphql
type word_freq {
  time: timestamptz!
  window: String!
  word: String!
  count: Int!
  latest_news_id: bigint
  # Relationship
  latest_news: news
}
```

## Query Operations

### 获取最新信号

```graphql
query GetLatestSignals($limit: Int = 10) {
  signals(order_by: {time: desc}, limit: $limit) {
    id
    time
    symbol
    signal_type
    change_pct
    price
  }
}
```

### 按币种查询信号

```graphql
query GetSignalsBySymbol($symbol: String!, $limit: Int = 20) {
  signals(
    where: {symbol: {_eq: $symbol}}
    order_by: {time: desc}
    limit: $limit
  ) {
    id
    time
    signal_type
    change_pct
    price
  }
}
```

### 获取最新新闻

```graphql
query GetLatestNews($limit: Int = 20) {
  news(order_by: {time: desc}, limit: $limit) {
    id
    time
    source
    title
    url
  }
}
```

### 获取热门词频

```graphql
query GetHotWords($window: String!) {
  word_freq(
    where: {window: {_eq: $window}}
    order_by: {count: desc}
    limit: 10
  ) {
    word
    count
    latest_news {
      title
      url
    }
  }
}
```

### 获取 K 线数据

```graphql
query GetKlines($symbol: String!, $start: timestamptz!, $end: timestamptz!) {
  klines(
    where: {
      symbol: {_eq: $symbol}
      time: {_gte: $start, _lte: $end}
    }
    order_by: {time: asc}
  ) {
    time
    open
    high
    low
    close
    volume
  }
}
```

## Subscription Operations

### 实时信号推送

```graphql
subscription OnNewSignal {
  signals(order_by: {time: desc}, limit: 1) {
    id
    time
    symbol
    signal_type
    change_pct
    price
  }
}
```

### 实时新闻推送

```graphql
subscription OnNewNews {
  news(order_by: {time: desc}, limit: 1) {
    id
    time
    source
    title
    url
  }
}
```

### 实时价格更新

```graphql
subscription OnPriceUpdate($symbol: String!) {
  prices(
    where: {symbol: {_eq: $symbol}}
    order_by: {time: desc}
    limit: 1
  ) {
    time
    price
    volume_24h
  }
}
```

## Mutation Operations

> **Note**: 写入操作主要由后台程序通过直接数据库连接执行，不通过 GraphQL。
> Hasura 会自动生成 mutation，但前端通常只读。

### 示例：插入新闻 (后台使用)

```graphql
mutation InsertNews($objects: [news_insert_input!]!) {
  insert_news(
    objects: $objects
    on_conflict: {
      constraint: news_url_key
      update_columns: []
    }
  ) {
    affected_rows
  }
}
```

## Error Handling

Hasura 返回标准 GraphQL 错误格式：

```json
{
  "errors": [
    {
      "message": "field \"nonexistent\" not found in type: 'signals'",
      "extensions": {
        "path": "$.selectionSet.signals.selectionSet.nonexistent",
        "code": "validation-failed"
      }
    }
  ]
}
```

常见错误码：
- `validation-failed`: 查询语法错误
- `constraint-violation`: 唯一约束冲突
- `permission-error`: 权限不足

## Health Check

```graphql
query HealthCheck {
  __typename
}
```

返回 `{"data": {"__typename": "query_root"}}` 表示 API 正常。
