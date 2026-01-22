#!/usr/bin/env python3
"""
币安历史 K 线数据下载器
从 data.binance.vision 下载月度 K 线 CSV 并导入数据库
"""
import os
import sys
import requests
import zipfile
import io
import csv
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

# 数据库连接配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fuce")
DB_USER = os.getenv("DB_USER", "fuce")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fuce_dev_password")

# 下载配置
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
MONTHS_BACK = int(os.getenv("MONTHS_BACK", "12"))  # 默认 12 个月
INTERVAL = "1m"  # 1 分钟 K 线

# 币安数据下载 URL
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"


def get_db_connection():
    import psycopg2
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def download_month(symbol: str, year: int, month: int) -> list[dict] | None:
    """下载指定月份的 K 线数据"""
    filename = f"{symbol}-{INTERVAL}-{year}-{month:02d}.zip"
    url = f"{BASE_URL}/{symbol}/{INTERVAL}/{filename}"

    print(f"  Downloading {filename}...", end=" ", flush=True)

    try:
        resp = requests.get(url, timeout=60)
        if resp.status_code == 404:
            print("Not available yet")
            return None
        resp.raise_for_status()

        # 解压 ZIP
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            csv_name = filename.replace(".zip", ".csv")
            with zf.open(csv_name) as f:
                reader = csv.reader(io.TextIOWrapper(f, 'utf-8'))
                klines = []
                for row in reader:
                    # CSV 格式：Open time, Open, High, Low, Close, Volume, Close time, ...
                    # 注意：币安历史数据使用微秒时间戳（16位），需要除以 1000000
                    open_time = int(row[0])
                    close_time = int(row[6])
                    # 判断是毫秒还是微秒
                    if open_time > 9999999999999:  # 超过 13 位，是微秒
                        open_time = open_time // 1000
                        close_time = close_time // 1000
                    klines.append({
                        "time": datetime.fromtimestamp(open_time / 1000, tz=timezone.utc),
                        "symbol": symbol,
                        "open": float(row[1]),
                        "high": float(row[2]),
                        "low": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5]),
                        "close_time": datetime.fromtimestamp(close_time / 1000, tz=timezone.utc),
                        "quote_volume": float(row[7]),
                        "trades": int(row[8])
                    })
                print(f"{len(klines)} klines")
                return klines
    except Exception as e:
        print(f"Error: {e}")
        return None


def insert_klines(conn, klines: list[dict]):
    """批量插入 K 线数据"""
    sql = """
        INSERT INTO klines_raw (time, symbol, open, high, low, close, volume, close_time, quote_volume, trades)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (time, symbol) DO NOTHING
    """
    with conn.cursor() as cur:
        values = [
            (k["time"], k["symbol"], k["open"], k["high"], k["low"],
             k["close"], k["volume"], k["close_time"], k["quote_volume"], k["trades"])
            for k in klines
        ]
        cur.executemany(sql, values)
        conn.commit()


def main():
    print("=" * 50)
    print("Binance Historical K-Line Downloader")
    print(f"Symbol: {SYMBOL}")
    print(f"Period: {MONTHS_BACK} months back")
    print("=" * 50)

    conn = get_db_connection()

    # 计算要下载的月份列表
    now = datetime.now()
    months = []
    for i in range(1, MONTHS_BACK + 1):
        date = now - relativedelta(months=i)
        months.append((date.year, date.month))

    # 从最早的月份开始下载
    months.reverse()

    total_klines = 0
    for year, month in months:
        klines = download_month(SYMBOL, year, month)
        if klines:
            insert_klines(conn, klines)
            total_klines += len(klines)

    conn.close()

    print("=" * 50)
    print(f"Done! Imported {total_klines} klines")
    print("=" * 50)


if __name__ == "__main__":
    main()
