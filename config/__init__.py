"""
统一配置管理模块

提供项目中所有服务的配置管理，包括：
- Backend API 服务配置
- Workflow Engine 配置
- 共享的基础配置

使用方式:
    # Backend 服务
    from config import backend_settings
    
    # Workflow Engine
    from config import workflow_settings
    
    # 获取配置实例
    from config import get_backend_config, get_workflow_config
"""

from .base import BaseConfig
from .backend_config import BackendConfig, settings as backend_settings
from .workflow_config import WorkflowConfig, settings as workflow_settings

# 导出主要配置类和实例
__all__ = [
    # 配置类
    "BaseConfig",
    "BackendConfig", 
    "WorkflowConfig",
    
    # 配置实例
    "backend_settings",
    "workflow_settings",
    
    # 便捷函数
    "get_backend_config",
    "get_workflow_config",
]


def get_backend_config() -> BackendConfig:
    """获取 Backend 配置实例"""
    return backend_settings


def get_workflow_config() -> WorkflowConfig:
    """获取 Workflow Engine 配置实例"""
    return workflow_settings 