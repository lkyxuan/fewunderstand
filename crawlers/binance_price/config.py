"""
币安价格爬虫配置
"""
import os

# 币安 API
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"

# 采集配置
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "10"))

# 只采集 USDT 交易对（过滤掉杠杆代币等）
QUOTE_ASSET = "USDT"
EXCLUDE_PATTERNS = ["UP", "DOWN", "BEAR", "BULL"]  # 排除杠杆代币
