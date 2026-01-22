"""
5分钟涨跌幅计算
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from _base import BaseCalculator, db
import config


class Indicator5minCalculator(BaseCalculator):
    """5分钟涨跌幅计算"""

    def __init__(self, symbol: str = None):
        self.symbol = symbol or config.SYMBOL
        super().__init__(
            name=f"Indicator5min.{self.symbol}",
            target_table="indicators"
        )

    def calculate(self) -> dict | None:
        now = datetime.now(timezone.utc)
        five_min_ago = now - timedelta(minutes=5)

        old_prices = db.query(
            "SELECT price FROM prices WHERE symbol = %s AND time <= %s ORDER BY time DESC LIMIT 1",
            (self.symbol, five_min_ago)
        )
        new_prices = db.query(
            "SELECT price FROM prices WHERE symbol = %s ORDER BY time DESC LIMIT 1",
            (self.symbol,)
        )

        if not old_prices or not new_prices:
            return None

        old_price = float(old_prices[0][0])
        new_price = float(new_prices[0][0])
        change_pct = ((new_price - old_price) / old_price) * 100

        return {
            "columns": ["time", "symbol", "change_5min_pct"],
            "values": [now, self.symbol, change_pct],
            "extra": f"{old_price:.2f} -> {new_price:.2f} ({change_pct:+.4f}%)"
        }

    def _write_to_db(self, data: dict):
        db.execute(
            """INSERT INTO indicators (time, symbol, change_5min_pct) VALUES (%s, %s, %s)
               ON CONFLICT (time, symbol) DO UPDATE SET change_5min_pct = EXCLUDED.change_5min_pct""",
            tuple(data["values"])
        )
