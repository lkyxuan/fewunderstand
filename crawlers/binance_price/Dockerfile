FROM python:3.12-slim

WORKDIR /app

# 复制基类
COPY _base/ ./_base/

# 复制本服务
COPY binance_price/ ./binance_price/

# 安装依赖
RUN pip install --no-cache-dir requests psycopg2-binary

WORKDIR /app/binance_price

CMD ["python", "-u", "main.py"]
