"""
Integration tests for database operations.
Tests US2: Data write capability
"""
import os
from datetime import datetime, timezone
from decimal import Decimal

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
    """Create a database cursor with auto-rollback."""
    cursor = db_connection.cursor()
    yield cursor
    db_connection.rollback()  # Rollback any changes after test
    cursor.close()


class TestTableCreation:
    """Test that all required tables exist."""

    EXPECTED_TABLES = ['prices', 'klines', 'indicators', 'signals', 'news', 'word_freq']

    def test_all_tables_exist(self, db_cursor):
        """All 6 data tables should exist."""
        db_cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN %s
        """, (tuple(self.EXPECTED_TABLES),))
        tables = {row[0] for row in db_cursor.fetchall()}
        missing = set(self.EXPECTED_TABLES) - tables
        assert not missing, f"Missing tables: {missing}"

    def test_config_table_exists(self, db_cursor):
        """Configuration table should exist."""
        db_cursor.execute("""
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = '_config'
        """)
        assert db_cursor.fetchone() is not None, "_config table not found"


class TestDataWrite:
    """Test data write operations."""

    def test_insert_price(self, db_cursor, db_connection):
        """Should be able to insert price data."""
        now = datetime.now(timezone.utc)
        db_cursor.execute("""
            INSERT INTO prices (time, symbol, price, volume_24h, source)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING time, symbol
        """, (now, 'BTCUSDT', Decimal('50000.12345678'), Decimal('1000000.0'), 'test'))
        result = db_cursor.fetchone()
        assert result is not None
        assert result[1] == 'BTCUSDT'

    def test_insert_signal(self, db_cursor, db_connection):
        """Should be able to insert signal data."""
        now = datetime.now(timezone.utc)
        db_cursor.execute("""
            INSERT INTO signals (time, symbol, signal_type, change_pct, price)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (now, 'ETHUSDT', 'pump_5min', Decimal('5.25'), Decimal('3000.0')))
        result = db_cursor.fetchone()
        assert result is not None
        assert result[0] > 0  # Should have an auto-generated ID

    def test_insert_news(self, db_cursor, db_connection):
        """Should be able to insert news data."""
        now = datetime.now(timezone.utc)
        db_cursor.execute("""
            INSERT INTO news (time, source, title, url)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (now, 'test_source', 'Test News Title', 'https://example.com/test-unique-url'))
        result = db_cursor.fetchone()
        assert result is not None
        assert result[0] > 0

    def test_price_positive_constraint(self, db_cursor):
        """Price must be positive."""
        now = datetime.now(timezone.utc)
        with pytest.raises(psycopg2.errors.CheckViolation):
            db_cursor.execute("""
                INSERT INTO prices (time, symbol, price)
                VALUES (%s, %s, %s)
            """, (now, 'INVALID', Decimal('-1.0')))

    def test_news_url_unique_constraint(self, db_cursor, db_connection):
        """News URL must be unique."""
        now = datetime.now(timezone.utc)
        url = 'https://example.com/unique-test-url'

        # First insert should succeed
        db_cursor.execute("""
            INSERT INTO news (time, source, title, url)
            VALUES (%s, %s, %s, %s)
        """, (now, 'source1', 'Title 1', url))
        db_connection.commit()

        # Second insert with same URL should fail
        with pytest.raises(psycopg2.errors.UniqueViolation):
            db_cursor.execute("""
                INSERT INTO news (time, source, title, url)
                VALUES (%s, %s, %s, %s)
            """, (now, 'source2', 'Title 2', url))
