FROM python:3.12-slim

WORKDIR /app

COPY _base/ ./_base/
COPY indicator_5min/ ./indicator_5min/

RUN pip install --no-cache-dir psycopg2-binary

WORKDIR /app/indicator_5min

CMD ["python", "-u", "main.py"]
