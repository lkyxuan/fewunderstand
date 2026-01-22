"""
指标计算配置
"""
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fuce")
DB_USER = os.getenv("DB_USER", "fuce")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fuce_dev_password")

SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))
