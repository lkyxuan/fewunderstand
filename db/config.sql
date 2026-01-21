-- config.sql
-- Database configuration values
-- This file defines all configurable parameters used by init scripts

-- ============================================
-- Data Retention Configuration
-- ============================================
-- Default retention period for time-series data
-- Can be overridden by setting RETENTION_DAYS environment variable
\set retention_days 30

-- ============================================
-- Table Configuration
-- ============================================
-- Symbol field max length
\set symbol_max_length 20

-- Price precision (total digits, decimal places)
\set price_precision_total 20
\set price_precision_decimal 8

-- Volume precision
\set volume_precision_total 30
\set volume_precision_decimal 8

-- Percentage precision
\set pct_precision_total 10
\set pct_precision_decimal 4

-- ============================================
-- TimescaleDB Chunk Configuration
-- ============================================
-- Chunk time interval (default: 1 day)
\set chunk_time_interval '1 day'

-- ============================================
-- Logging
-- ============================================
\echo 'Database configuration loaded:'
\echo '  - Retention days: ' :retention_days
\echo '  - Symbol max length: ' :symbol_max_length
\echo '  - Chunk interval: ' :chunk_time_interval
