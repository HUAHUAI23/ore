# ORE - AI工作流引擎和Web后端

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1%2B-green.svg)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0%2B-orange.svg)](https://langchain.readthedocs.io)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

## 项目简介

ORE是一个现代化的AI工作流引擎，集成了LangChain和FastAPI，为企业级AI应用提供完整的解决方案。项目包含以下核心功能：

- 🌲 **树形工作流引擎** - 支持复杂的AI任务编排和执行
- 🚀 **FastAPI Web后端** - 现代化的RESTful API服务
- 🤖 **LangChain集成** - 支持多种AI模型和提示词模板
- 🔒 **企业级安全** - JWT认证、Argon2密码哈希、现代化加密
- 📊 **实时监控** - 完整的执行日志和状态管理
- 🔄 **异步执行** - 高性能的并发任务处理

## 核心特性

### 工作流引擎

- **多引擎支持**: 树形、DAG、图形等多种工作流类型
- **智能调度**: 自动依赖检查和并行执行
- **条件分支**: 支持复杂的业务逻辑判断
- **环路检测**: 构建时自动检查和防止环路
- **多起始点**: 支持多个入口节点并行启动

### AI集成

- **LangChain 0.3**: 最新版本的LangChain集成
- **统一模板**: 智能的提示词模板和变量替换
- **多模型支持**: OpenAI、Anthropic等主流AI服务
- **异步调用**: 高性能的AI模型异步调用
- **优雅降级**: AI服务不可用时的备用方案

### Web服务

- **FastAPI框架**: 现代化的Python Web框架
- **自动文档**: Swagger/OpenAPI自动生成
- **JWT认证**: 安全的用户认证和授权
- **CORS支持**: 跨域资源共享配置
- **异常处理**: 完善的错误处理和响应

## 快速开始

### 环境要求

- Python 3.10+
- pip 或 poetry
- 支持的AI服务API密钥

### 安装

```bash
# 克隆仓库
git clone https://github.com/HUAHUAI23/ore.git
cd ore

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev,test]"
```

### 配置

1. **复制环境配置文件**

```bash
cp .env.example .env
```

2. **配置API密钥**

```bash
# 编辑 .env 文件
OPENAI_API_KEY=your_openai_api_key
# 或者其他AI服务的API密钥
```

3. **配置数据库（可选）**

```bash
DATABASE_URL=sqlite:///./app.db
```

### 运行

#### 启动Web服务器

```bash
# 开发模式
workflow-server

# 或者直接运行
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### 运行工作流引擎

```bash
# 使用命令行工具
workflow-engine

# 或者运行示例
python -m workflow_engine.examples.tree_workflow
```

### 第一个工作流

创建一个简单的AI内容生成工作流：

```python
from workflow_engine.engines.tree import TreeWorkflowEngine
from workflow_engine.workflow_types import NodeType

# 配置工作流
config = {
    "workflow_id": "demo-001",
    "workflow_name": "AI内容生成示例",
    "description": "演示AI工作流的基本功能",
    "version": "1.0.0",
    "nodes": {
        "start": {
            "name": "开始",
            "node_type": "START",
            "description": "工作流入口"
        },
        "generate": {
            "name": "内容生成",
            "node_type": "PROCESS",
            "prompt": "生成一篇关于AI技术发展的简短文章",
            "description": "使用AI生成内容"
        },
        "end": {
            "name": "完成",
            "node_type": "LEAF",
            "prompt": "总结和输出最终结果",
            "description": "工作流结束"
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
        },
        {
            "from_node": "generate", 
            "to_node": "end",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True
            }
        }
    ]
}

# 执行工作流
async def main():
    engine = TreeWorkflowEngine(config)
    result = await engine.execute_workflow()
    print(f"工作流完成: {result.workflow_name}")
    print(f"执行结果: {result.results}")

# 运行
import asyncio
asyncio.run(main())
```

## 项目结构

```text
ore/
├── backend/                 # Web后端服务
│   ├── api/                # API路由
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型  
│   ├── schemas/            # Pydantic模式
│   ├── services/           # 业务逻辑
│   ├── utils/              # 工具函数
│   ├── cli.py              # 命令行入口
│   ├── main.py             # FastAPI应用主入口
│   └── tests/              # 测试用例
├── workflow_engine/         # 工作流引擎
│   ├── base/               # 基础抽象类
│   ├── engines/            # 具体引擎实现
│   │   ├── tree/          # 树形工作流
│   │   ├── dag/           # DAG工作流 
│   │   └── graph/         # 图形工作流
│   ├── examples/           # 示例代码
│   └── workflow_types.py   # 类型定义
├── config/                  # 配置模块
├── pyproject.toml          # 项目配置
└── README.md               # 项目文档
```

## API文档

### 认证API

#### 用户注册

```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}
```

#### 用户登录  

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "user@example.com", 
    "password": "secure_password"
}
```

#### 响应格式

```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    },
    "message": "操作成功",
    "timestamp": "2025-01-20T10:30:00Z"
}
```

### 健康检查

```http
GET /health

Response:
{
    "success": true,
    "data": {
        "status": "healthy",
        "timestamp": "2025-01-20T10:30:00Z",
        "version": "0.1.0"
    }
}
```

### API文档地址

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | - | 是 |
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./app.db` | 否 |
| `SECRET_KEY` | JWT签名密钥 | 随机生成 | 否 |
| `APP_ENV` | 运行环境 | `development` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `CORS_ORIGINS` | 允许的CORS源 | `["*"]` | 否 |

### LLM配置

支持以下AI服务提供商：

- **OpenAI**: `OPENAI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY` 
- **自定义端点**: 设置 `API_BASE_URL`

### 工作流配置

```python
# config/workflow_config.py
from pydantic_settings import BaseSettings

class WorkflowSettings(BaseSettings):
    llm_provider: str = "openai"
    llm_model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    class Config:
        env_prefix = "WORKFLOW_"
```

## 开发指南

### 开发环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装pre-commit hooks
pre-commit install

# 运行代码格式化
black .
isort .

# 运行静态检查
mypy .
ruff check .
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest backend/tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest --cov=backend --cov-report=html
```

### 添加新的工作流引擎

1. **创建引擎目录**

```bash
mkdir workflow_engine/engines/your_engine
```

2. **实现基础接口**

```python
from workflow_engine.base.engine import BaseWorkflowEngine

class YourWorkflowEngine(BaseWorkflowEngine):
    def _initialize_from_config(self, config):
        # 实现配置初始化
        pass
        
    async def execute_workflow(self):
        # 实现工作流执行逻辑
        pass
```

3. **注册引擎**

```python
# workflow_engine/engines/__init__.py
from .your_engine import YourWorkflowEngine

ENGINES = {
    "tree": TreeWorkflowEngine,
    "your_engine": YourWorkflowEngine,
}
```

### 添加新的API端点

1. **创建路由文件**

```python
# backend/api/v1/your_endpoint.py
from fastapi import APIRouter, Depends
from backend.schemas.common import ApiResponse

router = APIRouter()

@router.get("/")
async def your_endpoint():
    return ApiResponse(data={"message": "Hello World"})
```

2. **注册路由**

```python
# backend/main.py
from backend.api.v1 import your_endpoint

app.include_router(your_endpoint.router, prefix="/api/v1/your-endpoint")
```

## 部署

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000
CMD ["workflow-server"]
```

```bash
# 构建镜像
docker build -t ore:latest .

# 运行容器
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ore:latest
```

### 生产部署

```bash
# 使用Gunicorn
pip install -e ".[prod]"
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 故障排除

### 常见问题

1. **LLM调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看API配额和限制

2. **工作流执行异常**
   - 检查节点配置是否正确
   - 确认没有环路依赖
   - 查看执行日志

3. **数据库连接问题**
   - 检查数据库URL配置
   - 确认数据库服务状态
   - 检查权限和网络

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看工作流执行日志
tail -f logs/workflow.log
```

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 代码规范

- 使用Black进行代码格式化
- 使用isort整理导入
- 使用mypy进行类型检查
- 使用ruff进行代码质量检查
- 编写单元测试覆盖新功能

## 许可证

本项目采用 Apache License 2.0 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 联系方式

- **作者**: lim
- **邮箱**: <huahua1319873800@outlook.com>
- **项目主页**: <https://github.com/HUAHUAI23/ore>
- **问题反馈**: <https://github.com/HUAHUAI23/ore/issues>

## 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [LangChain](https://langchain.readthedocs.io/) - 强大的AI应用开发框架
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证和设置管理
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包