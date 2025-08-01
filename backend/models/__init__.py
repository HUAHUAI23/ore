"""
Database models for the backend application.
只包含数据库模型，DTO模型在 schemas/ 目录下
"""

from .base import (
    # 模型类
    User,
    Workflow,
    WorkflowExecution,
    # 枚举类
    WorkflowStatus,
    ExecutionStatus,
    # 工具函数
    get_all_models,
    create_all_tables,
    drop_all_tables,
    target_metadata,
    print_table_info,
    reset_database,
    get_model_by_name,
)

# 为了保持向后兼容，也可以直接从具体模块导入
from .user import User
from .workflow import Workflow, WorkflowExecution, WorkflowStatus, ExecutionStatus

# 导出列表
__all__ = [
    # === 模型类 ===
    "User",
    "Workflow",
    "WorkflowExecution",
    # === 枚举类 ===
    "WorkflowStatus",
    "ExecutionStatus",
    # === 工具函数 ===
    "get_all_models",  # 获取所有模型类
    "create_all_tables",  # 创建所有表
    "drop_all_tables",  # 删除所有表
    "target_metadata",  # Alembic迁移用的metadata
    "print_table_info",  # 打印表结构信息
    "reset_database",  # 重置数据库（开发用）
    "get_model_by_name",  # 根据名称获取模型
]

# 版本信息
__version__ = "1.0.0"


# 模型统计信息
def get_models_info() -> dict:
    """获取模型统计信息"""
    models = get_all_models()
    return {
        "total_models": len(models),
        "model_names": [model.__name__ for model in models],
        "table_names": [getattr(model, "__tablename__", "unknown") for model in models],
    }


# 添加到导出列表
__all__.append("get_models_info")
