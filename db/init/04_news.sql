-- 04_news.sql
-- 新闻数据表

CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    link TEXT,
    summary TEXT,
    PRIMARY KEY (time, id)
);

-- 去重索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_news_source_link ON news (source, link);

-- 时间索引
CREATE INDEX IF NOT EXISTS idx_news_time ON news (time DESC);

COMMENT ON TABLE news IS '新闻数据（Phase 0: 假数据验证）';

-- 验证
DO $$
BEGIN
    RAISE NOTICE 'News table created';
END $$;
