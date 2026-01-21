-- 01_tables.sql
-- Create all database tables
-- Configuration is loaded from environment variables

-- ============================================
-- Create database tables
-- ============================================

-- ============================================
-- Table: prices (价格数据)
-- ============================================
CREATE TABLE IF NOT EXISTS prices (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20,8) NOT NULL CHECK (price > 0),
    volume_24h DECIMAL(30,8),
    source VARCHAR(50),
    PRIMARY KEY (time, symbol)
);

COMMENT ON TABLE prices IS '实时价格快照，用于计算指标';

-- ============================================
-- Table: klines (K线数据)
-- ============================================
CREATE TABLE IF NOT EXISTS klines (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8),
    PRIMARY KEY (time, symbol),
    CONSTRAINT klines_price_check CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

COMMENT ON TABLE klines IS '1分钟K线数据，用于图表展示';

-- ============================================
-- Table: indicators (指标数据)
-- ============================================
CREATE TABLE IF NOT EXISTS indicators (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    change_5min DECIMAL(10,4),
    change_15min DECIMAL(10,4),
    change_1h DECIMAL(10,4),
    volume_change DECIMAL(10,4),
    PRIMARY KEY (time, symbol)
);

COMMENT ON TABLE indicators IS '计算后的技术指标';

-- ============================================
-- Table: signals (信号数据)
-- ============================================
CREATE TABLE IF NOT EXISTS signals (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    change_pct DECIMAL(10,4),
    price DECIMAL(20,8),
    metadata JSONB,
    PRIMARY KEY (time, id)
);

CREATE INDEX IF NOT EXISTS idx_signals_time ON signals (time DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_time ON signals (symbol, time DESC);

COMMENT ON TABLE signals IS '触发的交易信号';

-- ============================================
-- Table: news (新闻数据)
-- ============================================
CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL UNIQUE,
    time TIMESTAMPTZ NOT NULL,
    source VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    content TEXT,
    crawled_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (time, id)
);

CREATE INDEX IF NOT EXISTS idx_news_time ON news (time DESC);
CREATE INDEX IF NOT EXISTS idx_news_source_time ON news (source, time DESC);

COMMENT ON TABLE news IS '爬取的新闻文章';

-- ============================================
-- Table: word_freq (词频统计)
-- ============================================
CREATE TABLE IF NOT EXISTS word_freq (
    time TIMESTAMPTZ NOT NULL,
    time_window VARCHAR(20) NOT NULL,
    word VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL,
    latest_news_id BIGINT REFERENCES news(id),
    PRIMARY KEY (time, time_window, word)
);

CREATE INDEX IF NOT EXISTS idx_word_freq_window_count ON word_freq (time_window, count DESC);

COMMENT ON TABLE word_freq IS '新闻词频聚合结果';

-- ============================================
-- Verify tables created
-- ============================================
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('prices', 'klines', 'indicators', 'signals', 'news', 'word_freq');

    IF table_count = 6 THEN
        RAISE NOTICE 'All 6 tables created successfully';
    ELSE
        RAISE EXCEPTION 'Expected 6 tables, found %', table_count;
    END IF;
END $$;
