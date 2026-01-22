"""
币安 K 线爬虫 - 服务入口
"""
import signal
import sys
import time
import config
from crawler import BinanceKlineCrawler


# 优雅退出标志
shutdown_requested = False


def signal_handler(signum, frame):
    global shutdown_requested
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown_requested = True


def main():
    # 注册信号处理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    crawler = BinanceKlineCrawler()

    print("=" * 50)
    print("Binance K-Line Crawler")
    print(f"Symbols: {', '.join(config.SYMBOLS)}")
    print(f"History: {config.HISTORY_DAYS} days")
    print(f"Interval: {config.INTERVAL_SECONDS}s")
    print("=" * 50)

    # 启动时为每个交易对检查并回填数据
    for symbol in config.SYMBOLS:
        if shutdown_requested:
            break
        latest = crawler.get_latest_time(symbol)
        if latest is None:
            print(f"No data for {symbol}, starting backfill...")
            crawler.backfill_history(symbol, config.HISTORY_DAYS)
        else:
            print(f"{symbol} has data up to {latest}, checking for gaps...")
            crawler.incremental_fetch(symbol)

    print("Initial sync complete, entering incremental mode...")

    # 主循环：增量采集
    while not shutdown_requested:
        for symbol in config.SYMBOLS:
            if shutdown_requested:
                break
            crawler.incremental_fetch(symbol)

        # 等待下一个采集周期
        for _ in range(config.INTERVAL_SECONDS):
            if shutdown_requested:
                break
            time.sleep(1)

    print("Shutdown complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
