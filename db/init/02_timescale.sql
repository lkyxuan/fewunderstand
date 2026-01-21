-- 02_timescale.sql
-- Convert tables to hypertables and set retention policies
-- Retention period is read from RETENTION_DAYS environment variable

\set ON_ERROR_STOP on

-- ============================================
-- Create configuration table for runtime settings
-- ============================================
CREATE TABLE IF NOT EXISTS _config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default retention days (can be overridden)
INSERT INTO _config (key, value, description)
VALUES ('retention_days', '30', 'Data retention period in days')
ON CONFLICT (key) DO NOTHING;

-- ============================================
-- Convert to Hypertables
-- ============================================

-- prices: partition by day
SELECT create_hypertable('prices', 'time', if_not_exists => TRUE);

-- klines: partition by day
SELECT create_hypertable('klines', 'time', if_not_exists => TRUE);

-- indicators: partition by day
SELECT create_hypertable('indicators', 'time', if_not_exists => TRUE);

-- signals: partition by day (using time column, not id)
SELECT create_hypertable('signals', 'time', if_not_exists => TRUE);

-- news: partition by day
SELECT create_hypertable('news', 'time', if_not_exists => TRUE);

-- word_freq: partition by day
SELECT create_hypertable('word_freq', 'time', if_not_exists => TRUE);

-- ============================================
-- Retention Policies (using config table)
-- ============================================

-- Function to get retention interval from config
CREATE OR REPLACE FUNCTION get_retention_interval() RETURNS INTERVAL AS $$
DECLARE
    retention_days INTEGER;
BEGIN
    SELECT value::INTEGER INTO retention_days
    FROM _config
    WHERE key = 'retention_days';

    IF retention_days IS NULL THEN
        retention_days := 30;  -- fallback default
    END IF;

    RETURN (retention_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Add retention policies using configured value
DO $$
DECLARE
    retention_interval INTERVAL;
BEGIN
    retention_interval := get_retention_interval();

    -- Add policies for all hypertables (if_not_exists requires TimescaleDB 2.0+)
    PERFORM add_retention_policy('prices', retention_interval, if_not_exists => TRUE);
    PERFORM add_retention_policy('klines', retention_interval, if_not_exists => TRUE);
    PERFORM add_retention_policy('indicators', retention_interval, if_not_exists => TRUE);
    PERFORM add_retention_policy('signals', retention_interval, if_not_exists => TRUE);
    PERFORM add_retention_policy('news', retention_interval, if_not_exists => TRUE);
    PERFORM add_retention_policy('word_freq', retention_interval, if_not_exists => TRUE);

    RAISE NOTICE 'Retention policies set to % for all 6 tables', retention_interval;
END $$;

-- ============================================
-- Verify hypertables
-- ============================================
DO $$
DECLARE
    hypertable_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO hypertable_count
    FROM timescaledb_information.hypertables
    WHERE hypertable_schema = 'public';

    IF hypertable_count >= 6 THEN
        RAISE NOTICE 'All hypertables created successfully (count: %)', hypertable_count;
    ELSE
        RAISE WARNING 'Expected 6 hypertables, found %', hypertable_count;
    END IF;
END $$;
