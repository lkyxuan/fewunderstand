-- 02_timescale.sql
-- 转换为 hypertable + 配置数据保留策略

-- ============================================
-- 转换为 Hypertables（时序优化）
-- ============================================
SELECT create_hypertable('prices', 'time', if_not_exists => TRUE);
SELECT create_hypertable('indicators', 'time', if_not_exists => TRUE);
SELECT create_hypertable('signals', 'time', if_not_exists => TRUE);

-- ============================================
-- 数据保留策略（默认 30 天）
-- ============================================
SELECT add_retention_policy('prices', INTERVAL '30 days', if_not_exists => TRUE);
SELECT add_retention_policy('indicators', INTERVAL '30 days', if_not_exists => TRUE);
SELECT add_retention_policy('signals', INTERVAL '30 days', if_not_exists => TRUE);

-- 验证
DO $$
DECLARE
    hypertable_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO hypertable_count
    FROM timescaledb_information.hypertables
    WHERE hypertable_schema = 'public';

    RAISE NOTICE 'Hypertables created: %', hypertable_count;
END $$;
