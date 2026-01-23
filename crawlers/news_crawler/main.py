"""
新闻爬虫 - 服务入口
"""
import time
import config
from crawler import NewsCrawler


def main():
    crawler = NewsCrawler()

    print("=" * 50)
    print("News Crawler (RSS Feeds)")
    print(f"Interval: {config.INTERVAL_SECONDS}s")
    print(f"Sources: {[name for name, _ in config.RSS_FEEDS]}")
    print("=" * 50)

    while True:
        crawler.run()
        time.sleep(config.INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
