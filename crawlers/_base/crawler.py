"""
爬虫基类
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from . import db


class BaseCrawler(ABC):
    """
    爬虫基类 - 采集外部数据写入数据库

    子类需要实现:
    - fetch(): 获取数据
    """

    def __init__(self, name: str, target_table: str):
        self.name = name
        self.target_table = target_table

    @abstractmethod
    def fetch(self) -> dict | None:
        """
        获取数据

        Returns:
            {
                "columns": ["col1", "col2", ...],
                "values": [val1, val2, ...],
                "extra": "日志信息（可选）"
            }
        """
        pass

    def run(self) -> dict | None:
        """执行：获取数据 -> 写入数据库"""
        now = datetime.now(timezone.utc)
        try:
            result = self.fetch()
            if result is None:
                self._log(now, "No data")
                return None

            self._write_to_db(result)
            self._log(now, f"OK | {result.get('extra', '')}")
            return result

        except Exception as e:
            self._log(now, f"Error - {e}")
            return None

    def _write_to_db(self, data: dict):
        """写入数据库"""
        columns = data["columns"]
        values = data["values"]
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(columns)
        sql = f"INSERT INTO {self.target_table} ({column_names}) VALUES ({placeholders})"
        db.execute(sql, tuple(values))

    def _log(self, time: datetime, message: str):
        print(f"[{time}] {self.name}: {message}")
