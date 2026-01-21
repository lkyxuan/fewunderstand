-- 00_init.sql
-- Initialize database with TimescaleDB extension
-- This file runs automatically on first PostgreSQL start

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Confirm extension is enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        RAISE EXCEPTION 'TimescaleDB extension failed to install';
    END IF;
    RAISE NOTICE 'TimescaleDB extension enabled successfully';
END $$;
