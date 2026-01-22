# Project Context

## Purpose
Few Understand 社区版 - 面向普通用户的加密货币信息平台。

**核心价值**：信号系统 + 新闻热点，让用户不用盯盘也能捕捉市场异动。

## 核心架构

```
┌─────────────────────────────────────┐
│         数据采集层（任意语言）         │
│                                     │
│  Python 爬虫    →  prices 表        │
│  Python/TS 计算 →  indicators 表    │
│  Python/TS 检测 →  signals 表       │
│                                     │
└──────────────┬──────────────────────┘
               ↓
         PostgreSQL + TimescaleDB
               ↓
           Hasura (GraphQL)
               ↓
      TypeScript 前端
```

### 架构原则

1. **数据库即 API**
   - 所有数据处理程序只需要读写数据库
   - Hasura 自动生成 GraphQL API + 实时订阅
   - 前端通过 GraphQL 获取数据，不关心数据怎么来的

2. **语言无关**
   - 数据采集/处理可以用任何语言（Python、TypeScript、Go、Rust）
   - 只要能连接 PostgreSQL 就行
   - 通过数据库解耦，各模块互不干扰

3. **简单计算，本地够用**
   - 目标用户是本地自托管，资源有限
   - 不做复杂的 ML/向量计算
   - 简单指标（涨跌幅、MA）用任何语言都能实现

## Tech Stack

| 层 | 技术 | 说明 |
|---|------|------|
| 数据库 | PostgreSQL 15 + TimescaleDB 2.x | 时序数据优化 |
| API | Hasura GraphQL Engine 2.x | 自动生成 API + 实时订阅 |
| 爬虫 | Python + requests | 数据采集 |
| 计算 | Python 或 TypeScript | 指标计算、信号检测 |
| 前端 | TypeScript（框架待定） | TradingView + Lightweight Charts |
| 部署 | Docker Compose | 本地自托管 |

## 目录结构

```
fuce/
├── docker-compose.yml      # 服务编排（postgres + hasura）
├── db/
│   └── init/               # 数据库初始化脚本
├── hasura/
│   └── metadata/           # Hasura 表配置
├── crawlers/               # Python 爬虫
│   ├── base_crawler.py     # 爬虫基类
│   ├── price_crawler.py    # 价格采集
│   ├── indicator_calculator.py  # 指标计算
│   └── signal_detector.py  # 信号检测
└── openspec/               # 规格说明
```

## 数据表设计

| 表 | 来源 | 内容 |
|---|------|------|
| prices | 爬虫 | 币安原始价格 |
| indicators | 计算 | 涨跌幅等指标 |
| signals | 检测 | 触发的信号 |
| news | 爬虫 | 新闻原文（Phase 2） |
| word_freq | 计算 | 词频热度（Phase 2） |

## Domain Context
- **信号**：价格异动（如5分钟涨跌超过1%）
- **热点**：新闻词频聚合（5分钟/1小时/24小时窗口）
- **K线标记**：在图表上标注信号和新闻时间点

## Important Constraints
- 本地自托管，不依赖云服务
- 数据保留期可配置（默认30天）
- 开源，供个人学习和使用
- 简单计算优先，不做重型 ML
