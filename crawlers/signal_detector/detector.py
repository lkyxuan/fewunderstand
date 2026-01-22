"""
信号检测
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from _base import BaseCalculator, db
import config


class SignalDetector(BaseCalculator):
    """价格异动信号检测"""

    def __init__(self, symbol: str = None, threshold: float = None):
        self.symbol = symbol or config.SYMBOL
        self.threshold = threshold or config.SIGNAL_THRESHOLD
        super().__init__(
            name=f"Signal.{self.symbol}",
            target_table="signals"
        )

    def calculate(self) -> dict | None:
        now = datetime.now(timezone.utc)

        indicators = db.query(
            "SELECT change_5min_pct FROM indicators WHERE symbol = %s ORDER BY time DESC LIMIT 1",
            (self.symbol,)
        )

        if not indicators:
            return None

        change_pct = float(indicators[0][0])

        signal_type = None
        if change_pct >= self.threshold:
            signal_type = "pump_5min"
        elif change_pct <= -self.threshold:
            signal_type = "dump_5min"

        if signal_type:
            return {
                "columns": ["time", "symbol", "signal_type", "change_pct"],
                "values": [now, self.symbol, signal_type, change_pct],
                "extra": f"🚨 {signal_type} | {change_pct:+.4f}%"
            }
        else:
            print(f"[{now}] {self.name}: No signal | {change_pct:+.4f}%")
            return None
