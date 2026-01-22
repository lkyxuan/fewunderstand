# Capability: kline-data-collection

## Overview
币安 K-Line 数据采集能力，支持历史回填和增量采集。

## ADDED Requirements

### Requirement: klines_raw 数据表
The system MUST provide a `klines_raw` table to store raw K-line data from Binance API.

#### Scenario: 查询最近 K 线
- Given: klines_raw 表中有 BTCUSDT 的数据
- When: 执行 `SELECT * FROM klines_raw WHERE symbol = 'BTCUSDT' ORDER BY time DESC LIMIT 10`
- Then: 返回最近 10 条 K 线，每条包含 time, symbol, open, high, low, close, volume 字段

#### Scenario: K 线数据唯一性
- Given: 已存在 (time='2026-01-22 10:00:00', symbol='BTCUSDT') 的记录
- When: 再次插入相同 time 和 symbol 的数据
- Then: 使用 UPSERT 更新而非报错

---

### Requirement: 历史数据回填
The crawler MUST automatically backfill 30 days of historical K-line data on first startup.

#### Scenario: 空表首次启动
- Given: klines_raw 表为空
- When: binance-kline 容器启动
- Then: 自动下载最近 30 天的 1 分钟 K 线数据
- And: 完成后 klines_raw 表约有 43,200 条 BTCUSDT 记录

#### Scenario: 部分数据后重启
- Given: klines_raw 表有 7 天前至今的数据
- When: binance-kline 容器重启
- Then: 自动回补缺失的 23 天数据
- And: 不重复插入已有数据

---

### Requirement: 增量采集
The crawler MUST continuously collect the latest K-line data after startup.

#### Scenario: 正常增量采集
- Given: binance-kline 容器正在运行
- And: 当前时间为 10:05:30
- When: 增量采集执行
- Then: 获取 10:04:00 和 10:05:00 的 K 线（已闭合）
- And: 写入 klines_raw 表

#### Scenario: 采集间隔
- Given: 爬虫配置 INTERVAL_SECONDS=60
- When: 容器持续运行
- Then: 每 60 秒执行一次增量采集

---

### Requirement: 多交易对支持
The crawler MUST support specifying trading pairs via configuration.

#### Scenario: 默认单交易对
- Given: 未设置 SYMBOLS 环境变量
- When: 容器启动
- Then: 仅采集 BTCUSDT

#### Scenario: 多交易对配置
- Given: 设置 SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT
- When: 容器启动
- Then: 采集所有指定交易对的 K 线数据

---

### Requirement: Docker 容器化
The K-Line crawler MUST run as an independent Docker service.

#### Scenario: 服务定义
- Given: docker-compose.yml 中定义了 binance-kline 服务
- When: 执行 `docker compose up -d binance-kline`
- Then: 服务启动并开始采集数据

#### Scenario: 依赖管理
- Given: binance-kline 依赖 postgres 服务
- When: postgres 未就绪时启动 binance-kline
- Then: binance-kline 等待 postgres 就绪后再开始工作

---

### Requirement: GraphQL 暴露
The klines_raw table MUST be exposed via Hasura GraphQL API.

#### Scenario: 查询 K 线
- Given: Hasura 已配置 klines_raw 表
- When: 执行 GraphQL 查询
  ```graphql
  query {
    klines_raw(
      where: {symbol: {_eq: "BTCUSDT"}},
      order_by: {time: desc},
      limit: 100
    ) {
      time open high low close volume
    }
  }
  ```
- Then: 返回最近 100 条 BTCUSDT K 线数据
