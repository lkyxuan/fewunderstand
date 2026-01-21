"""
Integration tests for TimescaleDB features.
Tests US4: Time-series data optimization
"""
import os
from datetime import datetime, timezone

import psycopg2
import pytest


# Load config from environment
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "lagos")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "lagos_dev_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "lagos")


@pytest.fixture
def db_connection():
    """Create a database connection."""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB
    )
    yield conn
    conn.close()


@pytest.fixture
def db_cursor(db_connection):
    """Create a database cursor."""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()


class TestTimescaleDBExtension:
    """Test TimescaleDB extension is properly configured."""

    def test_timescaledb_extension_enabled(self, db_cursor):
        """TimescaleDB extension should be enabled."""
        db_cursor.execute("""
            SELECT extname FROM pg_extension WHERE extname = 'timescaledb'
        """)
        result = db_cursor.fetchone()
        assert result is not None, "TimescaleDB extension not found"
        assert result[0] == 'timescaledb'


class TestHypertables:
    """Test hypertable configuration."""

    EXPECTED_HYPERTABLES = ['prices', 'klines', 'indicators', 'signals', 'news', 'word_freq']

    def test_hypertables_created(self, db_cursor):
        """All data tables should be hypertables."""
        db_cursor.execute("""
            SELECT hypertable_name
            FROM timescaledb_information.hypertables
            WHERE hypertable_schema = 'public'
        """)
        hypertables = {row[0] for row in db_cursor.fetchall()}

        for table in self.EXPECTED_HYPERTABLES:
            assert table in hypertables, f"{table} is not a hypertable"

    def test_hypertable_dimensions(self, db_cursor):
        """Hypertables should be partitioned by time."""
        db_cursor.execute("""
            SELECT hypertable_name, column_name
            FROM timescaledb_information.dimensions
            WHERE hypertable_schema = 'public'
        """)
        dimensions = {row[0]: row[1] for row in db_cursor.fetchall()}

        for table in self.EXPECTED_HYPERTABLES:
            assert table in dimensions, f"{table} has no dimension"
            assert dimensions[table] == 'time', f"{table} is not partitioned by 'time'"


class TestRetentionPolicies:
    """Test retention policy configuration."""

    TABLES_WITH_RETENTION = ['prices', 'klines', 'signals', 'news']

    def test_retention_policies_exist(self, db_cursor):
        """Retention policies should be configured for main tables."""
        db_cursor.execute("""
            SELECT hypertable_name
            FROM timescaledb_information.jobs
            WHERE proc_name = 'policy_retention'
        """)
        tables_with_policies = {row[0] for row in db_cursor.fetchall()}

        for table in self.TABLES_WITH_RETENTION:
            assert table in tables_with_policies, f"{table} has no retention policy"

    def test_config_table_has_retention_days(self, db_cursor):
        """Config table should have retention_days setting."""
        db_cursor.execute("""
            SELECT value FROM _config WHERE key = 'retention_days'
        """)
        result = db_cursor.fetchone()
        assert result is not None, "retention_days config not found"
        retention_days = int(result[0])
        assert retention_days > 0, "retention_days should be positive"


class TestTimeSeriesPerformance:
    """Test time-series query performance characteristics."""

    def test_time_index_used(self, db_cursor):
        """Queries filtered by time should use index."""
        db_cursor.execute("""
            EXPLAIN (FORMAT JSON)
            SELECT * FROM prices
            WHERE time > NOW() - INTERVAL '1 hour'
            LIMIT 100
        """)
        result = db_cursor.fetchone()
        plan = result[0]
        # TimescaleDB should use chunk exclusion for time-based queries
        # The plan should not be a full sequential scan
        plan_str = str(plan)
        # Should see index scan or chunk append, not just Seq Scan
        assert 'Seq Scan' not in plan_str or 'Chunk Append' in plan_str or 'Index' in plan_str
