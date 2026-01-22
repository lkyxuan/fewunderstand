# Tasks: add-kline-crawler

## Overview
实现币安 K-Line 爬虫，支持 30 天历史回填和增量采集。

## Task List

### Phase 1: 数据库准备

- [x] **Task 1.1: 创建 klines_raw 表**
  - 创建 `db/init/04_klines_raw.sql`
  - 定义表结构（time, symbol, open, high, low, close, volume, close_time, quote_volume, trades）
  - 设置 (time, symbol) 复合主键
  - 转为 TimescaleDB hypertable
  - 添加 30 天数据保留策略
  - **验证**: 本地数据库执行 SQL，确认表创建成功

### Phase 2: 爬虫核心实现

- [x] **Task 2.1: 创建爬虫目录结构**
  - 创建 `crawlers/binance_kline/` 目录
  - 文件：`__init__.py`, `config.py`, `crawler.py`, `main.py`, `Dockerfile`

- [x] **Task 2.2: 实现配置模块**
  - `config.py`：BINANCE_KLINE_URL, SYMBOLS, INTERVAL_SECONDS, HISTORY_DAYS
  - 支持环境变量覆盖

- [x] **Task 2.3: 实现 K-Line API 调用**
  - `crawler.py`：`fetch_klines(symbol, start_time, end_time)` 方法
  - 解析币安 K 线响应格式
  - 单次最多 1000 条
  - **验证**: 单元测试调用 API 返回正确数据

- [x] **Task 2.4: 实现历史回填逻辑**
  - `crawler.py`：`backfill_history(symbol, days=30)` 方法
  - 分批请求（每次 1000 条）
  - 请求间延迟 1 秒防限流
  - 使用 UPSERT 写入数据库
  - **验证**: 手动运行回填，确认数据写入

- [x] **Task 2.5: 实现增量采集逻辑**
  - `crawler.py`：`incremental_fetch(symbol)` 方法
  - 查询该 symbol 最新 time
  - 从最新时间到当前时间请求新数据
  - **验证**: 模拟缺失数据后运行，确认正确补齐

- [x] **Task 2.6: 实现主循环**
  - `main.py`：启动时先执行回填，然后循环增量采集
  - 支持 INTERVAL_SECONDS 配置采集间隔
  - 优雅退出（捕获 SIGTERM）

### Phase 3: 容器化部署

- [x] **Task 3.1: 创建 Dockerfile**
  - 基于 Python 3.12-slim（与现有爬虫一致）
  - 安装依赖（requests, psycopg2-binary）
  - 设置工作目录和入口

- [x] **Task 3.2: 更新 docker-compose.yml**
  - 添加 `binance-kline` 服务定义
  - 配置环境变量（DB_HOST, SYMBOLS 等）
  - 设置依赖 postgres
  - **验证**: `docker compose up binance-kline` 成功启动

### Phase 4: Hasura 配置

- [x] **Task 4.1: 配置 Hasura 元数据**
  - 在 Hasura 中 track `klines_raw` 表
  - 配置 anonymous 角色 select 权限
  - **验证**: GraphQL 查询返回数据

### Phase 5: 前端集成（跨 change 依赖）

- [ ] **Task 5.1: 更新前端 MVP 数据源**
  - 修改 `add-frontend-mvp` 的 GraphQL 查询，从 `klines` 改为 `klines_raw`
  - 添加 `volume` 字段支持
  - **验证**: 前端图表正确显示 K 线数据
  - **注意**: 此任务属于 `add-frontend-mvp` change，需协调实现

### Phase 6: 集成测试

- [ ] **Task 6.1: 端到端测试**
  - 启动完整服务栈
  - 确认 30 天历史数据正确回填
  - 确认增量采集每分钟更新
  - 确认 GraphQL API 可查询数据

## Dependencies

```
Task 1.1 (数据库表)
    ↓
Task 2.1-2.6 (爬虫实现) [可并行]
    ↓
Task 3.1-3.2 (容器化)
    ↓
Task 4.1 (Hasura 配置)
    ↓
Task 5.1 (前端集成) ← 依赖 add-frontend-mvp
    ↓
Task 6.1 (集成测试)
```

## Parallelizable Work
- Task 2.2 ~ 2.6 可在本地并行开发测试
- Task 3.1 可与 Task 2.x 并行（只需目录结构即可）
