"""
基础配置类 - 包含所有服务的共享配置
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    """基础配置类 - 所有服务共享"""
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.development", ".env.production"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # =============================================================================
    # 项目基础信息
    # =============================================================================
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=True, description="调试模式")
    
    # =============================================================================
    # 日志配置 (共享)
    # =============================================================================
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    
    # =============================================================================
    # 验证器
    # =============================================================================
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        """验证环境配置"""
        allowed = ['development', 'staging', 'production']
        if v.lower() not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v.lower()
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """验证日志级别"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of: {allowed}')
        return v.upper()
    
    # =============================================================================
    # 属性方法
    # =============================================================================
    @property
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.environment == 'development'
    
    @property
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return self.environment == 'production'
    
    @property
    def is_debug_enabled(self) -> bool:
        """判断是否启用调试模式"""
        return self.debug and self.is_development