# ORE 项目文档索引

本文档提供了ORE项目所有文档的索引和概览，帮助开发者快速找到所需的信息。

## 文档结构

### 主要文档

| 文档 | 路径 | 描述 |
|------|------|------|
| **项目主文档** | [README.md](./README.md) | 项目概述、快速开始、核心特性 |
| **工作流引擎文档** | [workflow_engine/README.md](./workflow_engine/README.md) | 工作流引擎详细说明和使用指南 |
| **后端服务文档** | [backend/README.md](./backend/README.md) | FastAPI后端服务架构和开发指南 |
| **API使用指南** | [docs/API_GUIDE.md](./docs/API_GUIDE.md) | REST API完整使用说明和代码示例 |

### 配置文档

| 文件 | 路径 | 描述 |
|------|------|------|
| **项目配置** | [pyproject.toml](./pyproject.toml) | 项目依赖、构建配置、工具设置 |
| **环境配置示例** | [.env.example](./.env.example) | 环境变量配置示例 |

## 快速导航

### 🚀 新手入门

1. **项目概述** - 从 [README.md](./README.md) 开始
2. **安装配置** - 参考 [快速开始](./README.md#快速开始) 章节
3. **第一个工作流** - 查看 [基础示例](./README.md#第一个工作流)

### 🔧 开发指南

1. **工作流开发** - 详见 [workflow_engine/README.md](./workflow_engine/README.md)
2. **API开发** - 参考 [backend/README.md](./backend/README.md)
3. **客户端开发** - 查看 [docs/API_GUIDE.md](./docs/API_GUIDE.md)

### 📖 深入学习

1. **架构设计** - 工作流引擎架构原理
2. **扩展开发** - 自定义引擎和API端点
3. **最佳实践** - 性能优化和错误处理

## 核心概念

### 工作流引擎

- **BaseWorkflowEngine**: 所有工作流引擎的抽象基类
- **TreeWorkflowEngine**: 树形工作流引擎实现
- **节点类型**: START、PROCESS、LEAF
- **事件驱动**: 异步并行执行机制

### Web服务

- **FastAPI**: 现代Python Web框架
- **JWT认证**: 安全的用户认证机制
- **异常处理**: 分层异常和统一响应
- **中间件**: CORS、请求追踪、日志记录

### AI集成

- **LangChain**: 最新版本集成
- **提示词模板**: 变量替换和模板管理
- **多模型支持**: OpenAI、Anthropic等
- **优雅降级**: 失败场景处理

## 代码示例

### 创建简单工作流

```python
from workflow_engine.engines.tree import TreeWorkflowEngine

config = {
    "workflow_id": "demo-001",
    "workflow_name": "AI内容生成",
    "description": "演示工作流",
    "version": "1.0.0",
    "nodes": {
        "start": {
            "name": "开始",
            "node_type": "START"
        },
        "generate": {
            "name": "生成内容",
            "node_type": "LEAF",
            "prompt": "生成一篇AI技术文章"
        }
    },
    "edges": [
        {
            "from_node": "start",
            "to_node": "generate",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True
            }
        }
    ]
}

async def main():
    engine = TreeWorkflowEngine(config)
    result = await engine.execute_workflow()
    print(f"结果: {result.results}")

import asyncio
asyncio.run(main())
```

### API客户端使用

```python
import requests

# 用户注册
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "user@example.com",
    "password": "password123"
})

token = response.json()["data"]["access_token"]

# 使用认证令牌
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/workflows", headers=headers)
```

## 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/HUAHUAI23/ore.git
cd ore
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 基础安装
pip install -e .

# 开发环境
pip install -e ".[dev,test]"
```

### 4. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件设置API密钥
```

### 5. 启动服务

```bash
# 后端服务
workflow-server

# 工作流引擎
workflow-engine
```

## 测试

### 运行测试

```bash
# 所有测试
pytest

# 特定模块
pytest backend/tests/
pytest workflow_engine/tests/

# 覆盖率报告
pytest --cov=backend --cov=workflow_engine --cov-report=html
```

### 代码质量检查

```bash
# 格式化
black .
isort .

# 静态检查
mypy .
ruff check .
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t ore:latest .

# 运行容器
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ore:latest
```

### 生产部署

```bash
# 使用Gunicorn
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 常见问题

### 1. 安装问题

**问题**: 依赖安装失败
**解决**: 
- 检查Python版本(>=3.10)
- 升级pip: `pip install --upgrade pip`
- 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 2. 配置问题

**问题**: API密钥配置错误
**解决**:
- 检查`.env`文件格式
- 确认环境变量名称正确
- 验证API密钥有效性

### 3. 运行问题

**问题**: 服务启动失败
**解决**:
- 检查端口占用: `netstat -an | grep 8000`
- 查看错误日志
- 验证数据库连接

### 4. 工作流问题

**问题**: 工作流执行失败
**解决**:
- 检查节点配置格式
- 验证LLM API连接
- 查看执行日志

## 贡献指南

### 1. 开发流程

1. Fork项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 提交Pull Request

### 2. 代码规范

- 使用Black格式化代码
- 遵循PEP 8标准
- 编写完整的类型注解
- 添加文档字符串

### 3. 提交规范

- 使用语义化提交信息
- 包含测试用例
- 更新相关文档

## 支持与反馈

### 获取帮助

- **文档问题**: 查看对应模块的README
- **使用问题**: 参考API使用指南
- **开发问题**: 查看开发指南和最佳实践

### 问题反馈

- **GitHub Issues**: [https://github.com/HUAHUAI23/ore/issues](https://github.com/HUAHUAI23/ore/issues)
- **邮箱联系**: huahua1319873800@outlook.com

### 社区交流

- 欢迎提交Issue和Pull Request
- 分享使用经验和最佳实践
- 参与项目讨论和改进

## 更新日志

### v0.1.0 (2025-01-28)

- ✨ 初始版本发布
- 🌲 树形工作流引擎
- 🚀 FastAPI后端服务
- 🤖 LangChain集成
- 🔒 JWT认证系统
- 📚 完整文档体系

### 即将发布

- 📊 DAG工作流引擎
- 🎨 Web界面
- 📈 监控面板
- 🔄 分布式执行

---

**注意**: 本项目仍在积极开发中，API和功能可能会发生变化。建议定期查看文档更新。