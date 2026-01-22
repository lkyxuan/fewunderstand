FROM python:3.12-slim

WORKDIR /app

COPY _base/ ./_base/
COPY signal_detector/ ./signal_detector/

RUN pip install --no-cache-dir psycopg2-binary

WORKDIR /app/signal_detector

CMD ["python", "-u", "main.py"]
