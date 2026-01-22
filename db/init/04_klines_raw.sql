-- 04_klines_raw.sql
-- 币安 K 线原始数据表 - 从 API 直接获取的精确 OHLCV 数据

-- ============================================
-- klines_raw: 1分钟 K 线原始数据
-- ============================================

CREATE TABLE IF NOT EXISTS klines_raw (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume DECIMAL(30,8) NOT NULL,
    close_time TIMESTAMPTZ NOT NULL,
    quote_volume DECIMAL(30,8),
    trades INTEGER,
    PRIMARY KEY (time, symbol)
);

COMMENT ON TABLE klines_raw IS '币安 K 线原始数据（1分钟级别）';
COMMENT ON COLUMN klines_raw.time IS 'K 线开盘时间';
COMMENT ON COLUMN klines_raw.close_time IS 'K 线收盘时间';
COMMENT ON COLUMN klines_raw.volume IS '成交量（基础货币）';
COMMENT ON COLUMN klines_raw.quote_volume IS '成交额（报价货币）';
COMMENT ON COLUMN klines_raw.trades IS '成交笔数';

-- 转为 TimescaleDB hypertable
SELECT create_hypertable('klines_raw', 'time', if_not_exists => TRUE);

-- 添加 30 天数据保留策略
SELECT add_retention_policy('klines_raw', INTERVAL '30 days', if_not_exists => TRUE);

-- 创建索引加速查询
CREATE INDEX IF NOT EXISTS idx_klines_raw_symbol_time ON klines_raw (symbol, time DESC);

-- 验证
DO $$
BEGIN
    RAISE NOTICE 'klines_raw table created with 30-day retention policy';
END $$;
