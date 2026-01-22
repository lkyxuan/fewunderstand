"""
币安价格爬虫 - 服务入口
"""
import time
import config
from crawler import BinancePriceCrawler


def main():
    crawler = BinancePriceCrawler()

    print("=" * 50)
    print(f"Binance Price Crawler (All USDT pairs)")
    print(f"Interval: {config.INTERVAL_SECONDS}s")
    print("=" * 50)

    while True:
        crawler.run()
        time.sleep(config.INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
