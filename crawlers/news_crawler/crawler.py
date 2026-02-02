"""
新闻爬虫 - 从 RSS 源拉取新闻
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import html
import feedparser
from datetime import datetime, timezone
from time import mktime
from _base import db
import config


def strip_html(text: str) -> str:
    """去除 HTML 标签，返回纯文本"""
    if not text:
        return None
    # 移除 HTML 标签
    clean = re.sub(r'<[^>]+>', '', text)
    # 解码 HTML 实体 (&amp; -> &, &lt; -> <, etc.)
    clean = html.unescape(clean)
    # 压缩空白字符
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean if clean else None


class NewsCrawler:
    """RSS 新闻采集器"""

    def __init__(self):
        self.name = "NewsCrawler"
        self.target_table = "news"

    def fetch_feed(self, source: str, url: str) -> list[dict]:
        """从单个 RSS 源获取新闻"""
        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                self._log(datetime.now(timezone.utc), f"{source}: Parse error - {feed.bozo_exception}")
                return []

            results = []
            for entry in feed.entries[:config.MAX_NEWS_PER_FEED]:
                # 解析发布时间
                pub_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_time = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_time = datetime.fromtimestamp(mktime(entry.updated_parsed), tz=timezone.utc)
                else:
                    pub_time = datetime.now(timezone.utc)

                # 获取摘要（清理 HTML 标签）
                summary = None
                raw_summary = None
                if hasattr(entry, 'summary'):
                    raw_summary = entry.summary
                elif hasattr(entry, 'description'):
                    raw_summary = entry.description
                if raw_summary:
                    summary = strip_html(raw_summary)
                    if summary and len(summary) > 500:
                        summary = summary[:500] + "..."

                results.append({
                    "time": pub_time,
                    "source": source,
                    "title": entry.title if hasattr(entry, 'title') else "No title",
                    "link": entry.link if hasattr(entry, 'link') else None,
                    "summary": summary
                })

            return results

        except Exception as e:
            self._log(datetime.now(timezone.utc), f"{source}: Fetch error - {e}")
            return []

    def run(self) -> int:
        """执行：从所有 RSS 源拉取新闻 -> 批量写入数据库"""
        now = datetime.now(timezone.utc)
        total_count = 0

        for source, url in config.RSS_FEEDS:
            results = self.fetch_feed(source, url)
            if results:
                written = self._write_batch(results)
                self._log(now, f"{source}: {written} new / {len(results)} fetched")
                total_count += written

        self._log(now, f"Total: {total_count} new articles")
        return total_count

    def _write_batch(self, records: list[dict]) -> int:
        """批量写入数据库（去重）"""
        sql = """
            INSERT INTO news (time, source, title, link, summary)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source, link) DO NOTHING
        """
        values = [
            (r["time"], r["source"], r["title"], r["link"], r["summary"])
            for r in records
        ]

        with db.get_connection() as conn:
            with conn.cursor() as cur:
                written = 0
                for v in values:
                    cur.execute(sql, v)
                    written += cur.rowcount
                conn.commit()
                return written

    def _log(self, time: datetime, message: str):
        print(f"[{time}] {self.name}: {message}")
