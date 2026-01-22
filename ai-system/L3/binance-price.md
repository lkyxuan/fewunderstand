# L3: binance-price 组件

## 职责

从币安 API 采集实时价格，写入 `prices` 表。

## 配置

| 参数 | 环境变量 | 默认值 |
|-----|---------|-------|
| 交易对 | `SYMBOL` | BTCUSDT |
| 采集间隔 | `INTERVAL_SECONDS` | 10 |

## 数据源

- API: `https://api.binance.com/api/v3/ticker/price`
- 参数: `?symbol=BTCUSDT`

## 输出

写入 `prices` 表：

| 字段 | 类型 | 示例 |
|-----|------|------|
| time | timestamp | 2026-01-22T01:58:35+00:00 |
| symbol | varchar | BTCUSDT |
| price | numeric | 90122.44000000 |

## 文件结构

```
crawlers/binance_price/
├── Dockerfile
├── config.py    # 配置
├── crawler.py   # BinancePriceCrawler 类
└── main.py      # 入口
```

## 关键类

```python
class BinancePriceCrawler(BaseCrawler):
    def fetch(self) -> dict | None:
        # 调用币安 API，返回价格数据
```

## Docker

```yaml
binance-price:
  container_name: fuce-binance-price
  environment:
    SYMBOL: BTCUSDT
    INTERVAL_SECONDS: 10
```
