"""
5分钟涨跌幅计算 - 批量计算所有币种
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from _base import db


class Indicator5minCalculator:
    """5分钟涨跌幅批量计算"""

    def __init__(self):
        self.name = "Indicator5min"
        self.target_table = "indicators"

    def get_active_symbols(self) -> list[str]:
        """获取最近有价格数据的币种列表"""
        five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        rows = db.query(
            "SELECT DISTINCT symbol FROM prices WHERE time >= %s",
            (five_min_ago,)
        )
        return [row[0] for row in rows]

    def calculate_for_symbol(self, symbol: str) -> dict | None:
        """计算单个币种的5分钟涨跌幅"""
        now = datetime.now(timezone.utc)
        five_min_ago = now - timedelta(minutes=5)

        old_prices = db.query(
            "SELECT price FROM prices WHERE symbol = %s AND time <= %s ORDER BY time DESC LIMIT 1",
            (symbol, five_min_ago)
        )
        new_prices = db.query(
            "SELECT price FROM prices WHERE symbol = %s ORDER BY time DESC LIMIT 1",
            (symbol,)
        )

        if not old_prices or not new_prices:
            return None

        old_price = float(old_prices[0][0])
        new_price = float(new_prices[0][0])
        change_pct = ((new_price - old_price) / old_price) * 100

        return {
            "time": now,
            "symbol": symbol,
            "change_5min_pct": change_pct
        }

    def run(self) -> int:
        """执行：计算所有币种的指标"""
        now = datetime.now(timezone.utc)
        try:
            symbols = self.get_active_symbols()
            if not symbols:
                self._log(now, "No active symbols")
                return 0

            results = []
            for symbol in symbols:
                result = self.calculate_for_symbol(symbol)
                if result:
                    results.append(result)

            if results:
                self._write_batch(results)
                self._log(now, f"OK | {len(results)} symbols")
            else:
                self._log(now, "No data to calculate")

            return len(results)

        except Exception as e:
            self._log(now, f"Error - {e}")
            return 0

    def _write_batch(self, records: list[dict]):
        """批量写入数据库"""
        sql = """INSERT INTO indicators (time, symbol, change_5min_pct) VALUES (%s, %s, %s)
                 ON CONFLICT (time, symbol) DO UPDATE SET change_5min_pct = EXCLUDED.change_5min_pct"""
        values = [(r["time"], r["symbol"], r["change_5min_pct"]) for r in records]
        db.execute_many(sql, values)

    def _log(self, time: datetime, message: str):
        print(f"[{time}] {self.name}: {message}")
