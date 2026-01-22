FROM python:3.12-slim

WORKDIR /app

# 复制基类
COPY _base/ ./_base/

# 复制本服务
COPY binance_kline/ ./binance_kline/

# 安装依赖
RUN pip install --no-cache-dir requests psycopg2-binary

WORKDIR /app/binance_kline

CMD ["python", "-u", "main.py"]
