# L3: signal-detector 组件

## 职责

读取 `indicators` 表，检测超过阈值的异动，写入 `signals` 表。

## 配置

| 参数 | 环境变量 | 默认值 |
|-----|---------|-------|
| 交易对 | `SYMBOL` | BTCUSDT |
| 检测间隔 | `INTERVAL_SECONDS` | 60 |
| 阈值 | `SIGNAL_THRESHOLD` | 1.0 (%) |

## 检测逻辑

```
如果 change_5min_pct >= 1.0  → 触发 pump_5min 信号
如果 change_5min_pct <= -1.0 → 触发 dump_5min 信号
```

## 输入

从 `indicators` 表读取：
- 最新的 `change_5min_pct`

## 输出

写入 `signals` 表（仅当触发时）：

| 字段 | 类型 | 示例 |
|-----|------|------|
| id | bigint | 1 |
| time | timestamp | 2026-01-22T02:30:00+00:00 |
| symbol | varchar | BTCUSDT |
| signal_type | varchar | pump_5min |
| change_pct | numeric | 1.2500 |

## 信号类型

| 类型 | 含义 |
|-----|------|
| `pump_5min` | 5 分钟内上涨超过阈值 |
| `dump_5min` | 5 分钟内下跌超过阈值 |

## 文件结构

```
crawlers/signal_detector/
├── Dockerfile
├── config.py    # 配置
├── detector.py  # SignalDetector 类
└── main.py      # 入口
```

## 关键类

```python
class SignalDetector(BaseCalculator):
    def calculate(self) -> dict | None:
        # 读取涨跌幅，判断是否触发信号
```

## Docker

```yaml
signal-detector:
  container_name: fuce-signal-detector
  environment:
    SYMBOL: BTCUSDT
    INTERVAL_SECONDS: 60
    SIGNAL_THRESHOLD: 1.0
```
