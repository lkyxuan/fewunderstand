"""
信号检测 - 批量检测所有币种
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from _base import db
import config


class SignalDetector:
    """价格异动信号批量检测"""

    def __init__(self, threshold: float = None):
        self.threshold = threshold or config.SIGNAL_THRESHOLD
        self.name = "SignalDetector"
        self.target_table = "signals"

    def get_latest_indicators(self) -> list[dict]:
        """获取所有币种最新的指标数据"""
        # 获取每个币种最新的一条指标
        rows = db.query("""
            SELECT DISTINCT ON (symbol) symbol, change_5min_pct, time
            FROM indicators
            WHERE time >= NOW() - INTERVAL '2 minutes'
            ORDER BY symbol, time DESC
        """)
        return [{"symbol": r[0], "change_5min_pct": float(r[1]), "time": r[2]} for r in rows]

    def detect_for_indicator(self, indicator: dict) -> dict | None:
        """检测单个币种是否触发信号"""
        now = datetime.now(timezone.utc)
        change_pct = indicator["change_5min_pct"]
        symbol = indicator["symbol"]

        signal_type = None
        if change_pct >= self.threshold:
            signal_type = "pump_5min"
        elif change_pct <= -self.threshold:
            signal_type = "dump_5min"

        if signal_type:
            return {
                "time": now,
                "symbol": symbol,
                "signal_type": signal_type,
                "change_pct": change_pct
            }
        return None

    def run(self) -> int:
        """执行：检测所有币种的信号"""
        now = datetime.now(timezone.utc)
        try:
            indicators = self.get_latest_indicators()
            if not indicators:
                self._log(now, "No indicators available")
                return 0

            signals = []
            for indicator in indicators:
                signal = self.detect_for_indicator(indicator)
                if signal:
                    signals.append(signal)

            if signals:
                self._write_batch(signals)
                for s in signals:
                    print(f"  🚨 {s['symbol']}: {s['signal_type']} | {s['change_pct']:+.4f}%")
                self._log(now, f"OK | {len(signals)} signals from {len(indicators)} symbols")
            else:
                self._log(now, f"No signals | {len(indicators)} symbols checked")

            return len(signals)

        except Exception as e:
            self._log(now, f"Error - {e}")
            return 0

    def _write_batch(self, records: list[dict]):
        """批量写入数据库"""
        sql = "INSERT INTO signals (time, symbol, signal_type, change_pct) VALUES (%s, %s, %s, %s)"
        values = [(r["time"], r["symbol"], r["signal_type"], r["change_pct"]) for r in records]
        db.execute_many(sql, values)

    def _log(self, time: datetime, message: str):
        print(f"[{time}] {self.name}: {message}")
