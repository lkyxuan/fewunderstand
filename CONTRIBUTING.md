# 贡献指南

感谢你对 Few Understand 社区版的兴趣！

## 贡献流程

### 1. Fork 仓库

点击右上角的 **Fork** 按钮，将仓库复制到你的账户下。

### 2. Clone 到本地

```bash
git clone https://github.com/<你的用户名>/fuce.git
cd fuce
```

### 3. 创建分支

```bash
# 从 main 分支创建新分支
git checkout -b feature/你的功能名
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新

### 4. 开发

```bash
# 启动开发环境
./scripts/start.sh

# 进行开发...

# 运行测试
pytest tests/
```

### 5. 提交

```bash
git add .
git commit -m "feat: 添加xxx功能"
```

Commit 消息规范：
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建/工具

### 6. 推送并创建 PR

```bash
git push origin feature/你的功能名
```

然后在 GitHub 上创建 Pull Request。

## 开发规范

### 代码风格

- **Python**: 遵循 PEP 8，使用 type hints
- **SQL**: 表名小写复数形式（如 `prices`, `signals`）
- **配置**: 使用环境变量，不硬编码

### 测试要求

- 新功能需要有对应测试
- 所有测试必须通过
- `docker compose up` 可正常启动

### Constitution 原则

所有贡献必须符合项目宪法（`.specify/memory/constitution.md`）：

1. **数据库即 API** - 用 Hasura，不手写 REST API
2. **TDD 非谈判** - 先写测试
3. **简单优先** - 不过度工程
4. **本地优先** - Docker Compose 单机部署
5. **可观测性** - 结构化日志

## 报告问题

使用 GitHub Issues，选择对应的模板：
- **Bug Report** - 报告问题
- **Feature Request** - 提出新功能

## 提问

- 先搜索已有 Issues
- 提问时提供足够的上下文
- 附上错误日志和环境信息

## 行为准则

- 尊重他人
- 建设性讨论
- 欢迎新手

感谢你的贡献！
