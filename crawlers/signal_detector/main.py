"""
信号检测 - 服务入口
"""
import time
import config
from detector import SignalDetector


def main():
    detector = SignalDetector()

    print("=" * 50)
    print(f"Signal Detector")
    print(f"Symbol: {config.SYMBOL}")
    print(f"Threshold: {config.SIGNAL_THRESHOLD}%")
    print(f"Interval: {config.INTERVAL_SECONDS}s")
    print("=" * 50)

    while True:
        detector.run()
        time.sleep(config.INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
