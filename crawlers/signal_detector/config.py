"""
信号检测配置
"""
import os

INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "60"))
SIGNAL_THRESHOLD = float(os.getenv("SIGNAL_THRESHOLD", "1.0"))  # 涨跌幅阈值 %
