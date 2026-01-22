"""
数据库连接工具
"""
import os
import psycopg2
from contextlib import contextmanager

# 从环境变量读取配置，支持每个服务独立配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fuce")
DB_USER = os.getenv("DB_USER", "fuce")
DB_PASSWORD = os.getenv("DB_PASSWORD", "fuce_dev_password")


@contextmanager
def get_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        yield conn
    finally:
        conn.close()


def execute(sql: str, params: tuple = None):
    """执行 SQL（INSERT/UPDATE/DELETE）"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()


def query(sql: str, params: tuple = None) -> list:
    """查询并返回结果"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
