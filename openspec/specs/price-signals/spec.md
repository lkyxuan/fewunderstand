# Price Signals Spec Delta

## ADDED Requirements

### Requirement: 实时价格采集
系统 SHALL 从 Binance API 采集加密货币实时价格。

#### Scenario: 定时采集
- **WHEN** 爬虫服务运行
- **THEN** 每 10 秒从 Binance 获取 BTC/USDT 价格
- **AND** 写入 `prices` 表

#### Scenario: 数据格式
- **WHEN** 价格数据写入数据库
- **THEN** 包含 `time`（时间戳）、`symbol`（交易对）、`price`（价格）字段

### Requirement: 涨跌幅指标计算
系统 SHALL 基于历史价格计算涨跌幅指标。

#### Scenario: 5分钟涨跌幅
- **WHEN** 指标计算任务执行
- **THEN** 计算过去 5 分钟的价格变化百分比
- **AND** 结果写入 `indicators` 表

#### Scenario: 计算频率
- **WHEN** 爬虫服务运行
- **THEN** 每分钟执行一次指标计算

### Requirement: K 线 OHLC 视图
系统 SHALL 提供 1 分钟粒度的 OHLC 视图供图表查询。

#### Scenario: 视图可查询
- **WHEN** 客户端通过 GraphQL 查询 `klines`
- **THEN** 返回 `time`、`symbol`、`open`、`high`、`low`、`close` 字段

#### Scenario: 聚合粒度
- **WHEN** 视图基于 `prices` 聚合
- **THEN** 每条记录代表 1 分钟 K 线区间

### Requirement: 价格异动信号检测
系统 SHALL 检测价格异动并生成信号。

#### Scenario: 暴涨信号
- **WHEN** 5 分钟涨幅超过 1%
- **THEN** 生成 `pump_5min` 类型信号
- **AND** 记录涨幅百分比

#### Scenario: 暴跌信号
- **WHEN** 5 分钟跌幅超过 1%
- **THEN** 生成 `dump_5min` 类型信号
- **AND** 记录跌幅百分比

#### Scenario: 信号存储
- **WHEN** 信号生成
- **THEN** 写入 `signals` 表
- **AND** 包含 `time`、`symbol`、`signal_type`、`change_pct` 字段

### Requirement: 信号实时推送
系统 SHALL 通过 GraphQL Subscription 实时推送新信号。

#### Scenario: 订阅接收
- **WHEN** 客户端订阅 `signals` 表
- **AND** 新信号插入数据库
- **THEN** 客户端立即收到信号数据
