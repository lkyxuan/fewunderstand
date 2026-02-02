-- 05_klines_5m.sql
-- 5 分钟 K 线连续聚合视图 - 从 klines_raw 聚合

-- ============================================
-- klines_5m: 5分钟 K 线连续聚合
-- ============================================

CREATE MATERIALIZED VIEW IF NOT EXISTS klines_5m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', time) AS time,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume
FROM klines_raw
GROUP BY time_bucket('5 minutes', time), symbol
WITH NO DATA;

-- 添加刷新策略：每5分钟自动刷新，覆盖最近30分钟数据
SELECT add_continuous_aggregate_policy('klines_5m',
    start_offset => INTERVAL '30 minutes',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes',
    if_not_exists => TRUE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_klines_5m_symbol_time ON klines_5m (symbol, time DESC);

-- 添加 3 天数据保留策略
SELECT add_retention_policy('klines_5m', INTERVAL '3 days', if_not_exists => TRUE);

-- 首次刷新历史数据
CALL refresh_continuous_aggregate('klines_5m', NULL, NULL);

-- 验证
DO $$
BEGIN
    RAISE NOTICE 'klines_5m continuous aggregate created with 3-day retention';
END $$;
