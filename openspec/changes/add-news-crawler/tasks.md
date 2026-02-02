# Tasks: add-news-crawler (Phase 0 - 假数据验证)

## 数据库

- [ ] **T1**: 创建 `db/init/04_news.sql`，定义 `news` 表
- [ ] **T2**: 在 Hasura 中追踪 `news` 表

**验证**: Hasura Console 可查询 `news` 表

## 假数据模拟器

- [ ] **T3**: 创建 `crawlers/news_faker/main.py`，每 N 秒插入假新闻
- [ ] **T4**: 本地运行模拟器，确认数据写入

**验证**: `SELECT * FROM news ORDER BY time DESC LIMIT 5;` 有数据

## 前端验证

- [ ] **T5**: 确认前端 Subscription 能收到新 `news` 数据
- [ ] **T6**: 验证右侧信息流不断有新条目出现

**验证**: 前端信息流每分钟有新新闻涌入

---

## 依赖关系

```
T1 → T2 → T3 → T4 → T5 → T6
```

总计 6 个任务，预计可快速完成。
