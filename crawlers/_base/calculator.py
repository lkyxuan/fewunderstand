"""
计算器基类
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from . import db


class BaseCalculator(ABC):
    """
    计算器基类 - 读取数据 -> 计算 -> 写入

    子类需要实现:
    - calculate(): 计算逻辑
    """

    def __init__(self, name: str, target_table: str):
        self.name = name
        self.target_table = target_table

    @abstractmethod
    def calculate(self) -> dict | None:
        """
        计算逻辑

        Returns:
            {
                "columns": ["col1", "col2", ...],
                "values": [val1, val2, ...],
                "extra": "日志信息（可选）"
            }
        """
        pass

    def run(self) -> dict | None:
        """执行：计算 -> 写入数据库"""
        now = datetime.now(timezone.utc)
        try:
            result = self.calculate()
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
        """写入数据库 - 子类可覆盖"""
        columns = data["columns"]
        values = data["values"]
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(columns)
        sql = f"INSERT INTO {self.target_table} ({column_names}) VALUES ({placeholders})"
        db.execute(sql, tuple(values))

    def _log(self, time: datetime, message: str):
        print(f"[{time}] {self.name}: {message}")
