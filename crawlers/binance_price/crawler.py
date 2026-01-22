"""
币安价格爬虫
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime, timezone
from _base import BaseCrawler
import config


class BinancePriceCrawler(BaseCrawler):
    """币安实时价格采集"""

    def __init__(self, symbol: str = None):
        self.symbol = symbol or config.SYMBOL
        super().__init__(
            name=f"BinancePrice.{self.symbol}",
            target_table="prices"
        )

    def fetch(self) -> dict | None:
        resp = requests.get(
            config.BINANCE_TICKER_URL,
            params={"symbol": self.symbol},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        price = float(data["price"])
        now = datetime.now(timezone.utc)

        return {
            "columns": ["time", "symbol", "price"],
            "values": [now, self.symbol, price],
            "extra": f"{price}"
        }
