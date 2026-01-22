# MVP 信号系统 - 实现任务

## Phase 1: 数据库
- [ ] 1.1 启动 PostgreSQL + TimescaleDB + Hasura
- [ ] 1.2 创建三张表：`prices`、`indicators`、`signals`

## Phase 2: 价格采集
- [ ] 2.1 实现 `price_crawler.py`（调用币安 API）
- [ ] 2.2 验证数据写入 `prices` 表

## Phase 3: 指标计算
- [ ] 3.1 实现 `indicator_calculator.py`（5分钟涨跌幅）
- [ ] 3.2 验证数据写入 `indicators` 表

## Phase 4: 信号检测
- [ ] 4.1 实现 `signal_detector.py`（阈值 > 1%）
- [ ] 4.2 验证数据写入 `signals` 表

## Phase 5: 定时调度
- [ ] 5.1 实现 `main.py`（APScheduler 整合所有任务）
- [ ] 5.2 验证自动采集 → 计算 → 检测流程

## 完成标准
- [ ] 完整数据流：prices → indicators → signals
