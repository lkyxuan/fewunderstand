"""
币安 K 线爬虫 - 历史回填 + 增量采集
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import requests
from datetime import datetime, timezone, timedelta
from _base import db
import config


class BinanceKlineCrawler:
    """币安 K 线数据采集"""

    def __init__(self):
        self.name = "BinanceKline"
        self.target_table = "klines_raw"

    def fetch_klines(self, symbol: str, start_time: int, end_time: int) -> list[dict] | None:
        """
        获取指定时间范围的 K 线数据

        Args:
            symbol: 交易对，如 BTCUSDT
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）

        Returns:
            K 线数据列表，每条包含 OHLCV 信息
        """
        params = {
            "symbol": symbol,
            "interval": config.KLINE_INTERVAL,
            "startTime": start_time,
            "endTime": end_time,
            "limit": config.MAX_KLINES_PER_REQUEST
        }

        resp = requests.get(config.BINANCE_KLINE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return None

        results = []
        for kline in data:
            # 币安 K 线格式：
            # [0] Open time, [1] Open, [2] High, [3] Low, [4] Close, [5] Volume,
            # [6] Close time, [7] Quote volume, [8] Trades, [9-11] Ignore
            results.append({
                "time": datetime.fromtimestamp(kline[0] / 1000, tz=timezone.utc),
                "symbol": symbol,
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": datetime.fromtimestamp(kline[6] / 1000, tz=timezone.utc),
                "quote_volume": float(kline[7]),
                "trades": int(kline[8])
            })

        return results

    def backfill_history(self, symbol: str, days: int = 30) -> int:
        """
        回填历史 K 线数据

        Args:
            symbol: 交易对
            days: 回填天数

        Returns:
            写入的记录数
        """
        now = datetime.now(timezone.utc)
        end_time = int(now.timestamp() * 1000)
        start_time = int((now - timedelta(days=days)).timestamp() * 1000)

        total_written = 0
        current_start = start_time

        self._log(now, f"Backfilling {days} days for {symbol}...")

        while current_start < end_time:
            # 每次请求最多 1000 条（约 16.6 小时的 1 分钟 K 线）
            batch_end = min(current_start + config.MAX_KLINES_PER_REQUEST * 60 * 1000, end_time)

            try:
                klines = self.fetch_klines(symbol, current_start, batch_end)
                if klines:
                    self._write_batch(klines)
                    total_written += len(klines)
                    self._log(now, f"  Written {len(klines)} klines, total: {total_written}")

                current_start = batch_end + 1
                time.sleep(config.REQUEST_DELAY)  # 防限流

            except Exception as e:
                self._log(now, f"  Error fetching batch: {e}")
                time.sleep(config.REQUEST_DELAY * 2)
                continue

        self._log(now, f"Backfill complete: {total_written} klines for {symbol}")
        return total_written

    def get_latest_time(self, symbol: str) -> datetime | None:
        """获取数据库中该交易对的最新 K 线时间"""
        sql = "SELECT MAX(time) FROM klines_raw WHERE symbol = %s"
        result = db.query(sql, (symbol,))
        if result and result[0][0]:
            return result[0][0]
        return None

    def incremental_fetch(self, symbol: str) -> int:
        """
        增量采集最新 K 线

        Args:
            symbol: 交易对

        Returns:
            写入的记录数
        """
        now = datetime.now(timezone.utc)
        latest_time = self.get_latest_time(symbol)

        if latest_time is None:
            # 无数据，执行完整回填
            return self.backfill_history(symbol, config.HISTORY_DAYS)

        # 从最新时间开始请求到当前时间
        start_time = int(latest_time.timestamp() * 1000) + 60000  # +1分钟
        end_time = int(now.timestamp() * 1000)

        if start_time >= end_time:
            self._log(now, f"{symbol}: Already up to date")
            return 0

        try:
            klines = self.fetch_klines(symbol, start_time, end_time)
            if klines:
                self._write_batch(klines)
                self._log(now, f"{symbol}: +{len(klines)} klines")
                return len(klines)
            else:
                self._log(now, f"{symbol}: No new klines")
                return 0
        except Exception as e:
            self._log(now, f"{symbol}: Error - {e}")
            return 0

    def _write_batch(self, records: list[dict]):
        """批量写入数据库（UPSERT）"""
        sql = """
            INSERT INTO klines_raw (time, symbol, open, high, low, close, volume, close_time, quote_volume, trades)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (time, symbol) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                close_time = EXCLUDED.close_time,
                quote_volume = EXCLUDED.quote_volume,
                trades = EXCLUDED.trades
        """
        values = [
            (r["time"], r["symbol"], r["open"], r["high"], r["low"],
             r["close"], r["volume"], r["close_time"], r["quote_volume"], r["trades"])
            for r in records
        ]
        db.execute_many(sql, values)

    def _log(self, time: datetime, message: str):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {self.name}: {message}")
