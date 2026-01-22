# Design: add-news-crawler (Phase 0)

## 架构概览

```
┌─────────────────────────────────┐
│     假数据模拟器 (Python)        │
│  news_faker/main.py             │
│  - 每 N 秒插入一条假新闻          │
└───────────────┬─────────────────┘
                ▼
        PostgreSQL/news 表
                │
                ▼
        Hasura GraphQL
        (Subscription)
                │
                ▼
        前端信息流
        (实时更新)
```

## 数据表设计

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

-- 去重索引（为后续真实爬虫准备）
CREATE UNIQUE INDEX idx_news_source_link ON news (source, link);
```

## 假数据模拟器

```python
# crawlers/news_faker/main.py
import random
import time
from uuid import uuid4
from datetime import datetime

SOURCES = ["coindesk", "cointelegraph", "theblock", "jinse", "blockbeats"]
INTERVAL_SECONDS = 60  # 每分钟一条

def generate_fake_news():
    return {
        "source": random.choice(SOURCES),
        "title": f"[测试] {random.choice(['BTC', 'ETH', 'SOL'])} 市场动态 - {datetime.now().strftime('%H:%M:%S')}",
        "link": f"https://example.com/news/{uuid4()}",
        "summary": "这是一条用于测试前端信息流的假新闻。"
    }

def main():
    while True:
        news = generate_fake_news()
        insert_to_db(news)
        print(f"[{datetime.now()}] 插入: {news['title']}")
        time.sleep(INTERVAL_SECONDS)
```

## 前端集成

```graphql
subscription NewNewsStream {
  news(order_by: {time: desc}, limit: 50) {
    id
    time
    source
    title
    link
  }
}
```

前端信息流：
- 新条目从顶部插入
- 高亮显示 3 秒
- 按时间倒序排列

## 后续扩展（Phase 1）

Phase 0 验证通过后，替换假数据模拟器为：
1. RSSHub 服务（自托管）
2. RSS 爬虫（解析真实新闻）
3. Playwright 扩展（无 RSS 网站）
