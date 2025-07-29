# 后端服务模块

## 概述

后端服务模块基于FastAPI构建，提供现代化的RESTful API服务。集成了企业级的安全认证、异常处理、日志管理等功能，为工作流引擎提供Web接口和用户管理能力。

## 模块结构

```text
backend/
├── README.md               # 模块文档
├── cli.py                  # 命令行启动工具
├── main.py                # FastAPI应用主入口
├── api/                   # API路由层
│   ├── __init__.py
│   ├── deps.py            # 依赖注入
│   ├── deps/              # 依赖模块
│   └── v1/                # API v1版本
│       ├── __init__.py
│       └── auth.py        # 认证相关API
├── core/                  # 核心功能模块
│   ├── __init__.py
│   ├── auth.py            # 认证核心逻辑
│   ├── config.py          # 配置管理
│   └── security.py        # 安全工具
├── models/                # 数据模型
│   └── __init__.py
├── schemas/               # Pydantic数据模式
│   ├── __init__.py
│   ├── auth.py            # 认证相关模式
│   └── common.py          # 通用模式
├── services/              # 业务逻辑层
│   └── __init__.py
└── utils/                 # 工具函数
    ├── __init__.py
    ├── exceptions.py      # 异常处理
    └── logger.py          # 日志工具
└── tests/                 # 测试用例
    └── __init__.py
```

## 核心特性

### 1. 现代化架构

- **FastAPI框架**: 高性能异步Python Web框架
- **自动文档**: Swagger/OpenAPI自动生成
- **类型注解**: 完整的Python类型提示
- **异步支持**: 原生async/await支持

### 2. 企业级安全

- **JWT认证**: 基于JSON Web Token的认证机制
- **Argon2哈希**: 现代化的密码哈希算法
- **CORS支持**: 跨域资源共享配置
- **安全头设置**: 自动添加安全HTTP头

### 3. 完善的错误处理

- **分层异常**: 业务异常和HTTP异常分离
- **统一响应**: 标准化的API响应格式
- **错误追踪**: 详细的错误日志和追踪

### 4. 可观测性

- **结构化日志**: JSON格式的结构化日志输出
- **请求追踪**: 自动记录请求处理时间
- **健康检查**: 服务健康状态监控端点

## FastAPI 应用主入口 (main.py)

### 应用配置

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)
```

### 中间件配置

#### CORS中间件

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 请求时间中间件

```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.4f}s")
    return response
```

### 异常处理器

```python
# 自定义异常处理
app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
```

### 生命周期事件

```python
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.app_name}")
```

## 认证系统

### JWT认证流程

1. **用户注册/登录** → 验证凭据
2. **生成JWT令牌** → 包含用户信息和过期时间
3. **客户端存储** → 令牌存储在客户端
4. **请求认证** → 每次请求携带令牌
5. **令牌验证** → 服务端验证令牌有效性

### 核心组件

#### 密码哈希 (security.py)

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    """使用Argon2哈希密码"""
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    try:
        ph.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False
```

#### JWT令牌管理 (auth.py)

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
```

### 认证API端点

#### 用户注册

```python
@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(user_data: UserRegister):
    """用户注册"""
    # 检查用户是否已存在
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise BusinessException("用户已存在")
    
    # 创建新用户
    hashed_password = hash_password(user_data.password)
    user = await create_user(user_data.email, hashed_password)
    
    # 生成访问令牌
    access_token = create_access_token(data={"sub": user.email})
    
    return ApiResponse(
        data=TokenResponse(access_token=access_token, token_type="bearer"),
        message="注册成功"
    )
```

#### 用户登录

```python
@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(credentials: UserLogin):
    """用户登录"""
    # 验证用户凭据
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise BusinessException("邮箱或密码错误")
    
    # 生成访问令牌
    access_token = create_access_token(data={"sub": user.email})
    
    return ApiResponse(
        data=TokenResponse(access_token=access_token, token_type="bearer"),
        message="登录成功"
    )
```

### 依赖注入

#### 获取当前用户

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        username = verify_token(credentials.credentials)
        if username is None:
            raise credentials_exception
            
        user = await get_user_by_email(username)
        if user is None:
            raise credentials_exception
            
        return user
    except JWTError:
        raise credentials_exception
```

## 数据模式 (Schemas)

### 认证相关模式

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """用户注册模式"""
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        return v

class UserLogin(BaseModel):
    """用户登录模式"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """令牌响应模式"""
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    """用户模式"""
    id: int
    email: str
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 通用响应模式

```python
from typing import TypeVar, Generic, Optional
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """标准API响应模式"""
    success: bool = True
    data: Optional[T] = None
    message: str = "操作成功"
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheck(BaseModel):
    """健康检查模式"""
    status: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    """错误响应模式"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

## 异常处理系统

### 异常类型定义

```python
from fastapi import HTTPException

class BusinessException(Exception):
    """业务逻辑异常"""
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class CustomHTTPException(HTTPException):
    """自定义HTTP异常"""
    def __init__(self, status_code: int, message: str, error_code: str = "HTTP_ERROR"):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=message)
```

### 异常处理器

```python
from fastapi import Request
from fastapi.responses import JSONResponse

async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理器"""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message
        ).dict()
    )

async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """自定义HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.detail
        ).dict()
    )

async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="服务器内部错误"
        ).dict()
    )
```

## 日志系统

### 日志配置

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外信息
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def get_logger(name: str) -> logging.Logger:
    """获取配置好的日志器"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    return logger
```

### 日志使用示例

```python
logger = get_logger(__name__)

# 基本日志
logger.info("用户登录成功", extra={"user_id": "123", "email": "user@example.com"})

# 错误日志
try:
    risky_operation()
except Exception as e:
    logger.error("操作失败", exc_info=True, extra={"operation": "risky_operation"})

# 性能日志
start_time = time.time()
result = expensive_operation()
duration = time.time() - start_time
logger.info("操作完成", extra={"operation": "expensive", "duration": duration})
```

## 配置管理

### 配置类定义

```python
from pydantic_settings import BaseSettings
from typing import List

class BackendSettings(BaseSettings):
    """后端配置"""
    
    # 应用基本信息
    app_name: str = "ORE Backend API"
    app_description: str = "AI工作流引擎后端服务"
    app_version: str = "0.1.0"
    
    # 运行环境
    environment: str = "development"
    debug: bool = True
    
    # 安全配置
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 数据库配置
    database_url: str = "sqlite:///./app.db"
    
    # CORS配置
    allowed_origins: List[str] = ["*"]
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        env_prefix = "BACKEND_"

# 全局配置实例
backend_settings = BackendSettings()
```

### 环境变量

| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `BACKEND_APP_NAME` | 应用名称 | `ORE Backend API` | `MyApp API` |
| `BACKEND_DEBUG` | 调试模式 | `True` | `False` |
| `BACKEND_SECRET_KEY` | JWT密钥 | 随机生成 | `your-secret-key` |
| `BACKEND_DATABASE_URL` | 数据库URL | `sqlite:///./app.db` | `postgresql://...` |
| `BACKEND_ALLOWED_ORIGINS` | CORS源 | `["*"]` | `["http://localhost:3000"]` |
| `BACKEND_LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG` |

## 开发指南

### 开发环境设置

```bash
# 进入项目目录
cd ore/backend

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
pytest backend/tests/

# 运行特定测试文件
pytest backend/tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest backend/tests/ --cov=backend --cov-report=html
```

### 添加新的API端点

1. **创建路由文件**

```python
# backend/api/v1/your_endpoint.py
from fastapi import APIRouter, Depends
from backend.schemas.common import ApiResponse
from backend.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=ApiResponse[List[YourDataResponse]])
async def list_your_data(user: User = Depends(get_current_user)):
    """获取用户数据列表"""
    data = await get_user_data(user.id)
    return ApiResponse(data=data)

@router.post("/", response_model=ApiResponse[YourDataResponse])
async def create_your_data(
    data: YourDataCreate,
    user: User = Depends(get_current_user)
):
    """创建新数据"""
    result = await create_data(data, user.id)
    return ApiResponse(data=result, message="创建成功")
```

2. **注册路由**

```python
# backend/main.py
from backend.api.v1 import your_endpoint

app.include_router(
    your_endpoint.router, 
    prefix="/api/v1/your-endpoint", 
    tags=["Your Endpoint"]
)
```

3. **创建数据模式**

```python
# backend/schemas/your_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class YourDataBase(BaseModel):
    name: str
    description: Optional[str] = None

class YourDataCreate(YourDataBase):
    pass

class YourDataResponse(YourDataBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 部署

### 开发环境

```bash
# 启动开发服务器
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 或使用CLI工具
workflow-server --reload
```

### 生产环境

```bash
# 使用Gunicorn部署
pip install -e ".[prod]"
gunicorn backend.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

### Docker部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY pyproject.toml .
RUN pip install -e .

# 复制代码
COPY backend/ backend/
COPY config/ config/

# 设置环境变量
ENV BACKEND_ENVIRONMENT=production
ENV BACKEND_DEBUG=false

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
EXPOSE 8000
CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 环境配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BACKEND_DATABASE_URL=postgresql://user:pass@db:5432/ore
      - BACKEND_SECRET_KEY=${SECRET_KEY}
      - BACKEND_DEBUG=false
      - BACKEND_ALLOWED_ORIGINS=["http://localhost:3000"]
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ore
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 监控和可观测性

### 健康检查

```python
@app.get("/health", response_model=ApiResponse[HealthCheck])
async def health_check():
    """健康检查端点"""
    health_data = HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version=settings.app_version
    )
    return ApiResponse(data=health_data)

@app.get("/readiness")
async def readiness_check():
    """就绪检查"""
    try:
        # 检查数据库连接等依赖服务
        await check_database_connection()
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")
```

### 指标收集

```python
from prometheus_fastapi_instrumentator import Instrumentator

# 添加Prometheus指标
Instrumentator().instrument(app).expose(app)

# 自定义指标
from prometheus_client import Counter, Histogram

auth_attempts = Counter(
    'auth_attempts_total', 
    'Total authentication attempts', 
    ['result']
)
request_duration = Histogram(
    'request_duration_seconds', 
    'Request duration'
)

@router.post("/login")
async def login(credentials: UserLogin):
    start_time = time.time()
    try:
        # 登录逻辑
        result = await authenticate_user(credentials.email, credentials.password)
        auth_attempts.labels(result='success').inc()
        return result
    except Exception:
        auth_attempts.labels(result='failure').inc()
        raise
    finally:
        request_duration.observe(time.time() - start_time)
```

## 最佳实践

### 1. 安全性

- **输入验证**: 使用Pydantic严格验证所有输入
- **输出清理**: 避免在响应中泄露敏感信息
- **速率限制**: 实施API调用频率限制
- **HTTPS强制**: 生产环境强制使用HTTPS

### 2. 性能优化

- **异步处理**: 充分利用FastAPI的异步特性
- **连接池**: 使用数据库连接池
- **缓存策略**: 合理使用Redis等缓存
- **响应压缩**: 启用gzip压缩

### 3. 代码质量

- **类型注解**: 使用完整的类型提示
- **文档字符串**: 为所有公共API编写文档
- **单元测试**: 保持高测试覆盖率
- **代码审查**: 建立代码审查流程

### 4. 运维友好

- **结构化日志**: 使用JSON格式的结构化日志
- **健康检查**: 实施完善的健康检查机制
- **配置外部化**: 通过环境变量管理配置
- **优雅关闭**: 实现优雅的服务关闭

## 故障排除

### 常见问题

1. **JWT令牌验证失败**
   - 检查SECRET_KEY配置
   - 确认令牌格式正确
   - 验证令牌是否过期

2. **CORS错误**
   - 检查allowed_origins配置
   - 确认请求头设置正确
   - 验证预检请求处理

3. **数据库连接失败**
   - 检查DATABASE_URL配置
   - 确认数据库服务状态
   - 验证连接权限

4. **服务启动失败**
   - 检查端口占用情况
   - 验证环境变量配置
   - 查看详细错误日志

### 调试技巧

```python
# 启用详细日志
import logging
logging.getLogger("uvicorn").setLevel(logging.DEBUG)

# 添加调试中间件
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    print(f"Response: {response.status_code}")
    return response

# 查看配置
print("当前配置:", backend_settings.dict())
```

## 扩展开发

### 集成第三方服务

```python
# backend/services/external.py
import httpx
from backend.core.config import backend_settings

class ExternalAPIService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=backend_settings.external_api_url,
            headers={"Authorization": f"Bearer {backend_settings.external_api_key}"}
        )
    
    async def call_external_api(self, data: dict):
        response = await self.client.post("/endpoint", json=data)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        await self.client.aclose()

# 依赖注入
async def get_external_service():
    service = ExternalAPIService()
    try:
        yield service
    finally:
        await service.close()
```

### 数据库集成

```python
# backend/db/base.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import backend_settings

engine = create_engine(backend_settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

这个后端服务模块为整个ORE项目提供了坚实的Web服务基础，支持现代化的API设计模式和企业级的安全与运维要求。