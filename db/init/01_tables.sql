-- 01_tables.sql
-- MVP 信号系统 - 三张核心表

-- ============================================
-- prices: 币安原始价格数据
-- ============================================
CREATE TABLE IF NOT EXISTS prices (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    PRIMARY KEY (time, symbol)
);

COMMENT ON TABLE prices IS '币安实时价格快照';

-- ============================================
-- indicators: 计算指标
-- ============================================
CREATE TABLE IF NOT EXISTS indicators (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    change_5min_pct DECIMAL(10,4),
    PRIMARY KEY (time, symbol)
);

COMMENT ON TABLE indicators IS '5分钟涨跌幅等指标';

-- ============================================
-- signals: 触发的信号
-- ============================================
CREATE TABLE IF NOT EXISTS signals (
    id BIGSERIAL,
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    change_pct DECIMAL(10,4),
    PRIMARY KEY (time, id)
);

CREATE INDEX IF NOT EXISTS idx_signals_time ON signals (time DESC);

COMMENT ON TABLE signals IS '价格异动信号（涨跌幅超过阈值）';

-- 验证
DO $$
BEGIN
    RAISE NOTICE 'MVP tables created: prices, indicators, signals';
END $$;
