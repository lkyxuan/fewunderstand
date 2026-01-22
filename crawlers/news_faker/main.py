"""
假新闻数据模拟器
每分钟往 news 表插入一条假新闻，用于测试前端信息流
"""
import os
import sys
import random
import time
from datetime import datetime, timezone
from uuid import uuid4

# 添加父目录到 path，以便导入 _base
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _base import db

# 配置
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))  # 默认每分钟

# 假新闻模板
SOURCES = ["coindesk", "cointelegraph", "theblock", "jinse", "blockbeats", "panews", "wublock"]
COINS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX"]
ACTIONS = ["突破", "下跌", "反弹", "横盘", "创新高", "回调", "上涨", "震荡"]
TOPICS = [
    "{coin} {action}，市场关注度上升",
    "分析师：{coin} 短期或将{action}",
    "{coin} 24小时{action} {pct}%",
    "链上数据显示 {coin} 巨鲸{action}",
    "{coin} 生态重大更新，社区反应热烈",
    "机构报告：{coin} 长期看涨",
    "{coin} 网络活跃度{action}",
    "交易所 {coin} 流入量{action}",
]


def generate_fake_news() -> dict:
    """生成一条假新闻"""
    coin = random.choice(COINS)
    action = random.choice(ACTIONS)
    pct = round(random.uniform(1, 15), 2)

    title_template = random.choice(TOPICS)
    title = title_template.format(coin=coin, action=action, pct=pct)

    return {
        "source": random.choice(SOURCES),
        "title": title,
        "link": f"https://example.com/news/{uuid4()}",
        "summary": f"这是一条关于 {coin} 的测试新闻。"
    }


def insert_news(news: dict):
    """插入新闻到数据库"""
    sql = """
    INSERT INTO news (time, source, title, link, summary)
    VALUES (NOW(), %s, %s, %s, %s)
    ON CONFLICT (source, link) DO NOTHING
    """
    db.execute(sql, (news["source"], news["title"], news["link"], news["summary"]))


def main():
    print(f"[{datetime.now(timezone.utc)}] 假新闻模拟器启动，间隔 {INTERVAL_SECONDS} 秒")

    while True:
        try:
            news = generate_fake_news()
            insert_news(news)
            print(f"[{datetime.now(timezone.utc)}] 插入: [{news['source']}] {news['title']}")
        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] 错误: {e}")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
