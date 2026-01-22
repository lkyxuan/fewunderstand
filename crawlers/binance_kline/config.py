"""
币安 K 线爬虫配置
"""
import os

# 币安 K 线 API
BINANCE_KLINE_URL = "https://api.binance.com/api/v3/klines"

# 采集配置
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))  # 采集间隔（秒）
HISTORY_DAYS = int(os.getenv("HISTORY_DAYS", "30"))  # 历史回填天数

# 交易对配置
SYMBOLS = os.getenv("SYMBOLS", "BTCUSDT").split(",")  # 支持逗号分隔多个

# K 线时间级别
KLINE_INTERVAL = "1m"  # 1 分钟

# API 限制
MAX_KLINES_PER_REQUEST = 1000  # 单次最多 1000 条
REQUEST_DELAY = 1.0  # 请求间隔（秒），防止限流
