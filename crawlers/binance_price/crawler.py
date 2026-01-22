"""
币安价格爬虫 - 批量获取所有 USDT 交易对
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime, timezone
from _base import db
import config


class BinancePriceCrawler:
    """币安实时价格批量采集"""

    def __init__(self):
        self.name = "BinancePrice"
        self.target_table = "prices"

    def fetch(self) -> list[dict] | None:
        """批量获取所有 USDT 交易对价格"""
        resp = requests.get(config.BINANCE_TICKER_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        now = datetime.now(timezone.utc)
        results = []

        for item in data:
            symbol = item["symbol"]
            # 只保留 USDT 交易对
            if not symbol.endswith(config.QUOTE_ASSET):
                continue
            # 排除杠杆代币
            if any(pattern in symbol for pattern in config.EXCLUDE_PATTERNS):
                continue

            price = float(item["price"])
            results.append({
                "time": now,
                "symbol": symbol,
                "price": price
            })

        return results if results else None

    def run(self) -> int:
        """执行：获取数据 -> 批量写入数据库"""
        now = datetime.now(timezone.utc)
        try:
            results = self.fetch()
            if results is None:
                self._log(now, "No data")
                return 0

            self._write_batch(results)
            self._log(now, f"OK | {len(results)} symbols")
            return len(results)

        except Exception as e:
            self._log(now, f"Error - {e}")
            return 0

    def _write_batch(self, records: list[dict]):
        """批量写入数据库"""
        sql = "INSERT INTO prices (time, symbol, price) VALUES (%s, %s, %s)"
        values = [(r["time"], r["symbol"], r["price"]) for r in records]
        db.execute_many(sql, values)

    def _log(self, time: datetime, message: str):
        print(f"[{time}] {self.name}: {message}")
