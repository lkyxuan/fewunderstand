# Quick Start: 基础架构

**Branch**: `001-infrastructure` | **Date**: 2026-01-21

## 前置要求

- Docker Desktop 或 Docker Engine + Docker Compose
- 4GB 可用内存
- 10GB 可用磁盘空间

### 安装 Docker

**macOS**:
```bash
brew install --cask docker
```

**Windows**:
下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

**Linux (Ubuntu)**:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

## 快速开始

### 1. 克隆仓库

```bash
git clone <repository-url> lagos
cd lagos
```

### 2. 配置 (可选)

默认配置即可使用。如需自定义，编辑 `config/settings.yaml`:

```yaml
database:
  port: 5432      # 修改数据库端口
retention:
  days: 7         # 修改数据保留天数
```

### 3. 启动服务

```bash
./scripts/start.sh
# 或
docker compose up -d
```

**Windows (PowerShell)**:
```powershell
docker compose up -d
```

### 4. 验证服务

等待约 1 分钟，然后：

```bash
./scripts/health-check.sh
```

预期输出：
```
✓ PostgreSQL: healthy
✓ Hasura: healthy
All services are running!
```

### 5. 访问服务

| 服务 | URL | 说明 |
|------|-----|------|
| Hasura Console | http://localhost:8080 | GraphQL Playground + 管理界面 |
| PostgreSQL | localhost:5432 | 数据库连接 |

### 6. 测试 GraphQL

打开 http://localhost:8080/console，在 GraphiQL 中运行：

```graphql
query HealthCheck {
  __typename
}
```

## 停止服务

```bash
./scripts/stop.sh
# 或
docker compose down
```

**Windows (PowerShell)**:
```powershell
docker compose down
```

数据会保留在 Docker volumes 中。

## 完全清理

删除所有数据和容器：

```bash
docker compose down -v
```

> 警告：`-v` 会删除所有本地数据卷，重启后数据将无法恢复。

## 常见问题

### 端口被占用

```
Error: port 5432 is already in use
```

解决：
```bash
# 查找占用端口的进程
lsof -i :5432
# 或修改 config/settings.yaml 中的端口
```

### 仅限本地访问

服务默认绑定到 localhost（127.0.0.1），仅本机可访问，**本地使用无需修改默认密码**。如需对外网暴露，需自行修改 docker-compose.yml 的端口绑定。

### 内存不足

```
Error: Cannot allocate memory
```

解决：增加 Docker Desktop 的内存限制到 4GB 以上。

### 权限问题 (Linux)

```
Permission denied while trying to connect to Docker
```

解决：
```bash
sudo usermod -aG docker $USER
# 重新登录
```

## 开发流程

1. **修改数据库 schema**:
   - 在 `db/migrations/` 添加新的 SQL 文件
   - 重启服务或手动执行迁移

2. **验证 API 更新**:
   - 打开 Hasura Console
   - 检查 "Data" 标签页的表结构
   - 在 GraphiQL 测试新的查询

3. **写入数据**:
   ```bash
   # 使用 psql 连接
   docker compose exec postgres psql -U lagos -d lagos

   # 或使用任意 PostgreSQL 客户端连接 localhost:5432
   ```

## 下一步

基础架构启动后，可以开始开发：

- 价格爬虫 → 写入 `prices` 表
- 指标计算 → 写入 `indicators` 表
- 信号检测 → 写入 `signals` 表
- 新闻爬虫 → 写入 `news` 表

前端通过 GraphQL Subscription 实时接收数据更新。
