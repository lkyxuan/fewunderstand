#!/usr/bin/env python3
import schedule
import time
from sync_posts import sync_posts

def job():
    print(f"开始同步文章 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    sync_posts()
    print(f"同步完成 - {time.strftime('%Y-%m-%d %H:%M:%S')}")

# 每4小时执行一次
schedule.every(4).hours.do(job)

# 立即执行一次
job()

# 持续运行
while True:
    schedule.run_pending()
    time.sleep(60) 