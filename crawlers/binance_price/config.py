"""
币安价格爬虫配置
"""
import os

# 数据库（从环境变量读取，支持 Docker）
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fuce")
DB_USER = os.getenv("DB_USER", "fuce")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fuce_dev_password")

# 币安 API
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"

# 采集配置
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "10"))
