FROM python:3.12-slim

WORKDIR /app

# 复制基类
COPY _base/ ./_base/

# 复制本服务
COPY news_crawler/ ./news_crawler/

# 安装依赖
RUN pip install --no-cache-dir feedparser psycopg2-binary

WORKDIR /app/news_crawler

CMD ["python", "-u", "main.py"]
