"""
新闻爬虫配置
"""
import os

# 采集间隔（秒）
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "300"))  # 默认 5 分钟

# RSS 源配置
# 格式: (source_name, rss_url)
RSS_FEEDS = [
    # === 英文加密货币媒体（官方 RSS，最稳定）===
    ("cointelegraph", "https://cointelegraph.com/rss"),
    ("decrypt", "https://decrypt.co/feed"),
    ("bitcoinmagazine", "https://bitcoinmagazine.com/feed"),
    ("coindesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("thedefiant", "https://thedefiant.io/feed/"),
    ("cryptopotato", "https://cryptopotato.com/feed/"),
    ("cryptoslate", "https://cryptoslate.com/feed/"),
    ("cryptonews", "https://cryptonews.com/news/feed/"),

    # === 中文加密/财经媒体（通过 RSSHub）===
    ("cls", "http://rsshub:1200/cls/telegraph"),              # 财联社快讯
    ("panews", "http://rsshub:1200/panewslab/news"),          # PANews
    ("foresightnews", "http://rsshub:1200/foresightnews/article"),  # Foresight News
    ("wallstreetcn", "http://rsshub:1200/wallstreetcn/live/global"),  # 华尔街见闻
    ("36kr", "http://rsshub:1200/36kr/newsflashes"),          # 36氪快讯
]

# RSSHub 地址（Docker 内部网络）
RSSHUB_HOST = os.getenv("RSSHUB_HOST", "rsshub")
RSSHUB_PORT = os.getenv("RSSHUB_PORT", "1200")

# 每次拉取最多保存的新闻数
MAX_NEWS_PER_FEED = int(os.getenv("MAX_NEWS_PER_FEED", "20"))
