"""
指标计算 - 服务入口
"""
import time
import config
from calculator import Indicator5minCalculator


def main():
    calculator = Indicator5minCalculator()

    print("=" * 50)
    print(f"Indicator 5min Calculator")
    print(f"Symbol: {config.SYMBOL}")
    print(f"Interval: {config.INTERVAL_SECONDS}s")
    print("=" * 50)

    while True:
        calculator.run()
        time.sleep(config.INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
