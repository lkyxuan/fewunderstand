-- 03_klines.sql
-- K 线数据视图 (OHLC) - 从 prices 聚合生成

-- ============================================
-- klines: 1分钟 K 线连续聚合视图
-- ============================================
-- 使用 TimescaleDB 连续聚合优化查询性能

CREATE MATERIALIZED VIEW IF NOT EXISTS klines
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS time,
    symbol,
    first(price, time) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, time) AS close,
    count(*) AS tick_count
FROM prices
GROUP BY time_bucket('1 minute', time), symbol
WITH NO DATA;

-- 添加刷新策略：每分钟自动刷新，覆盖最近10分钟数据
SELECT add_continuous_aggregate_policy('klines',
    start_offset => INTERVAL '10 minutes',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE
);

-- 创建索引加速查询
CREATE INDEX IF NOT EXISTS idx_klines_symbol_time ON klines (symbol, time DESC);

-- 注意：TimescaleDB 连续聚合不支持 COMMENT ON

-- 验证
DO $$
BEGIN
    RAISE NOTICE 'Klines continuous aggregate created with auto-refresh policy';
END $$;
