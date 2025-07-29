"""
最终推荐的配置解决方案 - 使用配置类获得最佳IDE支持
"""

from typing import Optional
from pydantic import Field
from functools import lru_cache
from .base import BaseConfig


class LLMConfig:
    """LLM配置类 - 提供最佳的IDE支持和类型安全"""

    def __init__(
        self,
        provider: str,
        model_name: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.api_key = api_key
        self.api_base = api_base

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"LLMConfig(provider='{self.provider}', "
            f"model='{self.model_name}', "
            f"temperature={self.temperature})"
        )


class EngineConfig:
    """引擎配置类"""

    def __init__(self, max_concurrent: int, timeout: int):
        self.max_concurrent = max_concurrent
        self.timeout = timeout

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"EngineConfig(max_concurrent={self.max_concurrent}, "
            f"timeout={self.timeout})"
        )


class WorkflowConfig(BaseConfig):
    """Workflow Engine 服务配置 - 改进版"""

    # =============================================================================
    # AI/LLM 配置
    # =============================================================================
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    llm_provider: str = Field(default="openai", description="LLM提供商")
    llm_model_name: str = Field(default="gpt-3.5-turbo", description="LLM模型名称")
    llm_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM温度参数"
    )
    llm_max_tokens: int = Field(default=1000, gt=0, description="LLM最大token数")
    llm_request_timeout: int = Field(
        default=60, gt=0, description="LLM请求超时时间（秒）"
    )
    api_base: Optional[str] = Field(default=None, description="LLM API端点")

    # =============================================================================
    # 工作流引擎核心配置
    # =============================================================================
    max_concurrent: int = Field(default=5, ge=1, le=50, description="最大并发执行数")
    timeout: int = Field(default=300, gt=0, description="工作流超时时间（秒）")

    # =============================================================================
    # 配置对象属性
    # =============================================================================

    @property
    def llm_config(self) -> LLMConfig:
        """获取 LLM 配置对象 - 完美的IDE支持"""
        return LLMConfig(
            provider=self.llm_provider,
            model_name=self.llm_model_name,
            temperature=self.llm_temperature,
            max_tokens=self.llm_max_tokens,
            timeout=self.llm_request_timeout,
            api_key=self.openai_api_key,
            api_base=self.api_base,
        )

    @property
    def engine_config(self) -> EngineConfig:
        """获取引擎配置对象"""
        return EngineConfig(
            max_concurrent=self.max_concurrent,
            timeout=self.timeout,
        )

    # =============================================================================
    # 验证方法
    # =============================================================================

    def validate_llm_config(self) -> bool:
        """验证LLM配置是否完整"""
        if not self.openai_api_key and self.llm_provider == "openai":
            return False
        return True

    def get_config_summary(self) -> str:
        """获取配置摘要"""
        return (
            f"WorkflowConfig(\n"
            f"  LLM: {self.llm_provider}:{self.llm_model_name}\n"
            f"  Engine: {self.max_concurrent} concurrent, {self.timeout}s timeout\n"
            f"  API Key: {'✓' if self.openai_api_key else '✗'}\n"
            f")"
        )


# =============================================================================
# 单例配置管理
# =============================================================================


@lru_cache()
def get_workflow_settings() -> WorkflowConfig:
    """获取Workflow配置单例"""
    return WorkflowConfig()


# 创建全局配置实例
settings = get_workflow_settings()
