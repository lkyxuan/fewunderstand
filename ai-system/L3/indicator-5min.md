# L3: indicator-5min 组件

## 职责

读取 `prices` 表，计算 5 分钟涨跌幅，写入 `indicators` 表。

## 配置

| 参数 | 环境变量 | 默认值 |
|-----|---------|-------|
| 交易对 | `SYMBOL` | BTCUSDT |
| 计算间隔 | `INTERVAL_SECONDS` | 60 |

## 计算逻辑

```
涨跌幅 = (当前价格 - 5分钟前价格) / 5分钟前价格 * 100
```

## 输入

从 `prices` 表读取：
- 最新价格
- 5 分钟前价格

## 输出

写入 `indicators` 表：

| 字段 | 类型 | 示例 |
|-----|------|------|
| time | timestamp | 2026-01-22T01:58:12+00:00 |
| symbol | varchar | BTCUSDT |
| change_5min_pct | numeric | 0.0662 |

## 文件结构

```
crawlers/indicator_5min/
├── Dockerfile
├── config.py      # 配置
├── calculator.py  # Indicator5minCalculator 类
└── main.py        # 入口
```

## 关键类

```python
class Indicator5minCalculator(BaseCalculator):
    def calculate(self) -> dict | None:
        # 查询价格，计算涨跌幅
```

## Docker

```yaml
indicator-5min:
  container_name: fuce-indicator-5min
  environment:
    SYMBOL: BTCUSDT
    INTERVAL_SECONDS: 60
```
