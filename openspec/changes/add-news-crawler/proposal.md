# Proposal: add-news-crawler

## Summary

新增新闻数据表和假数据模拟器，快速验证前端右侧信息流的"流逝"效果。

## Motivation

- 快速测试前端信息流能否不断有新内容涌入
- 验证 Hasura Subscription 的实时推送效果
- 为后续真实爬虫打基础

## Approach

### Phase 0: 假数据模拟器（本次实现）

1. 创建 `news` 表
2. 写一个简单脚本，每 N 秒往表里插入一条假新闻
3. 前端订阅 `news` 表，验证信息流效果

```python
# 假数据模拟器核心逻辑
while True:
    insert_fake_news(
        source=random.choice(["coindesk", "jinse", "theblock"]),
        title=f"测试新闻 {datetime.now()}",
        link=f"https://example.com/{uuid4()}"
    )
    time.sleep(interval_seconds)
```

### Phase 1: 真实爬虫（后续）

预留 RSSHub + Playwright 的扩展能力，验证效果后再接入。

## Data Model

```sql
CREATE TABLE news (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    link TEXT,
    summary TEXT,
    PRIMARY KEY (time, id)
);

CREATE UNIQUE INDEX idx_news_source_link ON news (source, link);
```

## Out of Scope (Phase 0)

- RSSHub 部署
- 真实 RSS 爬虫
- Playwright 爬虫
- 词频热度分析
