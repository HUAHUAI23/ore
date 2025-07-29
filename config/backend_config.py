"""
Backend配置解决方案 - 使用配置类获得最佳IDE支持
"""
from typing import List, Union, Optional
from pydantic import Field, field_validator
from functools import lru_cache
from .base import BaseConfig


class FastAPIConfig:
    """FastAPI配置类 - 提供最佳的IDE支持和类型安全"""
    
    def __init__(
        self,
        title: str,
        description: str,
        version: str,
        debug: bool,
        docs_url: Optional[str] = None,
        redoc_url: Optional[str] = None,
    ):
        self.title = title
        self.description = description
        self.version = version
        self.debug = debug
        self.docs_url = docs_url
        self.redoc_url = redoc_url

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"FastAPIConfig(title='{self.title}', "
            f"version='{self.version}', "
            f"debug={self.debug})"
        )

    def to_dict(self) -> dict:
        """转换为字典用于FastAPI初始化"""
        return {
            "title": self.title,
            "description": self.description,
            "version": self.version,
            "debug": self.debug,
            "docs_url": self.docs_url,
            "redoc_url": self.redoc_url,
        }


class JWTConfig:
    """JWT配置类"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"JWTConfig(algorithm='{self.algorithm}', "
            f"expire_minutes={self.access_token_expire_minutes})"
        )

    @property
    def is_secure(self) -> bool:
        """检查JWT配置是否安全"""
        return (
            len(self.secret_key) >= 32 and
            self.secret_key != "your-secret-key-here-change-in-production"
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
        }


class CORSConfig:
    """CORS配置类"""
    
    def __init__(self, allowed_origins: List[str]):
        self.allowed_origins = allowed_origins

    def __repr__(self) -> str:
        """字符串表示"""
        return f"CORSConfig(origins={len(self.allowed_origins)} entries)"

    @property
    def allows_all(self) -> bool:
        """检查是否允许所有来源"""
        return "*" in self.allowed_origins

    @property
    def is_development_mode(self) -> bool:
        """检查是否是开发模式（包含localhost）"""
        return any("localhost" in origin for origin in self.allowed_origins)

    def add_origin(self, origin: str) -> None:
        """添加新的允许来源"""
        if origin not in self.allowed_origins:
            self.allowed_origins.append(origin)

    def remove_origin(self, origin: str) -> None:
        """移除允许来源"""
        if origin in self.allowed_origins:
            self.allowed_origins.remove(origin)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {"allowed_origins": self.allowed_origins}


class BackendConfig(BaseConfig):
    """Backend 服务配置 - 改进版"""
    
    # =============================================================================
    # FastAPI 应用配置
    # =============================================================================
    app_name: str = Field(default="FastAPI Backend", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_description: str = Field(
        default="FastAPI Backend with JWT Auth", description="应用描述"
    )
    
    # =============================================================================
    # 数据库配置
    # =============================================================================
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/dbname", 
        description="PostgreSQL数据库连接URL"
    )
    database_pool_size: int = Field(default=5, ge=1, description="数据库连接池大小")
    database_max_overflow: int = Field(default=10, ge=0, description="数据库连接池最大溢出")
    database_echo: bool = Field(default=False, description="是否输出SQL语句")
    
    # =============================================================================
    # 安全配置
    # =============================================================================
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production", description="应用密钥"
    )
    
    # =============================================================================
    # JWT 认证配置
    # =============================================================================
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(
        default=30, gt=0, description="访问令牌过期时间（分钟）"
    )
    
    # =============================================================================
    # CORS 配置
    # =============================================================================
    allowed_origins: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="允许的跨域来源",
    )
    
    # =============================================================================
    # 验证器
    # =============================================================================
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """解析允许的来源"""
        if isinstance(v, str):
            # 处理逗号分隔的字符串
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            # 如果已经是列表，直接返回
            return v
        else:
            # 其他情况，尝试转换
            return [str(v)] if v else []
    
    # =============================================================================
    # 配置对象属性 - 使用配置类获得最佳IDE支持
    # =============================================================================
    
    @property
    def fastapi_config(self) -> FastAPIConfig:
        """获取 FastAPI 配置对象 - 完美的IDE支持"""
        return FastAPIConfig(
            title=self.app_name,
            description=self.app_description,
            version=self.app_version,
            debug=self.is_debug_enabled,
            docs_url="/docs" if self.is_development else None,
            redoc_url="/redoc" if self.is_development else None,
        )
    
    @property
    def jwt_config(self) -> JWTConfig:
        """获取 JWT 配置对象"""
        return JWTConfig(
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            access_token_expire_minutes=self.access_token_expire_minutes,
        )
    
    @property
    def cors_config(self) -> CORSConfig:
        """获取 CORS 配置对象"""
        # 确保 allowed_origins 是列表类型
        origins = self.allowed_origins
        if isinstance(origins, str):
            origins = [origins]
        return CORSConfig(allowed_origins=origins)

    # =============================================================================
    # 验证方法
    # =============================================================================
    
    def validate_security_config(self) -> bool:
        """验证安全配置是否完整"""
        jwt_config = self.jwt_config
        return jwt_config.is_secure

    def get_config_summary(self) -> str:
        """获取配置摘要"""
        jwt_config = self.jwt_config
        cors_config = self.cors_config
        
        return (
            f"BackendConfig(\n"
            f"  App: {self.app_name} v{self.app_version}\n"
            f"  JWT: {jwt_config.algorithm}, {jwt_config.access_token_expire_minutes}min\n"
            f"  CORS: {len(cors_config.allowed_origins)} origins\n"
            f"  Security: {'✓' if jwt_config.is_secure else '⚠️  INSECURE'}\n"
            f"  Mode: {'Development' if self.is_development else 'Production'}\n"
            f")"
        )


# =============================================================================
# 单例配置管理
# =============================================================================

@lru_cache()
def get_backend_settings() -> BackendConfig:
    """获取Backend配置单例"""
    return BackendConfig()


# 创建全局配置实例
settings = get_backend_settings()