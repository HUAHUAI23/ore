"""
Database models base configuration and utilities
统一的模型管理和工具函数
"""

from sqlmodel import SQLModel
from sqlalchemy.engine import Engine


# ============================================
# 模型导入 - 确保所有模型都被导入以注册到metadata
# ============================================

from .user import User
from .workflow import Workflow, WorkflowExecution, WorkflowStatus, ExecutionStatus

# ============================================
# 导出所有模型类
# ============================================

__all__ = [
    # 模型类
    "User",
    "Workflow",
    "WorkflowExecution",
    # 枚举类
    "WorkflowStatus",
    "ExecutionStatus",
    # 工具函数
    "get_all_models",
    "create_all_tables",
    "drop_all_tables",
    "target_metadata",
]


# ============================================
# 数据库元数据和工具函数
# ============================================


def get_all_models() -> list[type[SQLModel]]:
    """
    获取所有模型类，用于迁移和测试

    Returns:
        包含所有SQLModel类的列表
    """
    return [User, Workflow, WorkflowExecution]


def create_all_tables(engine: Engine) -> None:
    """
    创建所有表

    Args:
        engine: SQLAlchemy引擎实例
    """
    SQLModel.metadata.create_all(engine)


def drop_all_tables(engine: Engine) -> None:
    """
    删除所有表（慎用！）

    Args:
        engine: SQLAlchemy引擎实例
    """
    SQLModel.metadata.drop_all(engine)


def get_table_names() -> list[str]:
    """
    获取所有表名

    Returns:
        所有表名的列表
    """
    return [table.name for table in SQLModel.metadata.tables.values()]


def print_table_info() -> None:
    """打印所有表的信息，用于调试"""
    print("📋 数据库表信息:")
    for table_name, table in SQLModel.metadata.tables.items():
        print(f"  📄 {table_name}")
        for column in table.columns:
            nullable = "NULL" if column.nullable else "NOT NULL"
            print(f"    - {column.name}: {column.type} {nullable}")
        print()


# ============================================
# Alembic迁移支持
# ============================================

# 为Alembic提供的target_metadata
target_metadata = SQLModel.metadata

# 在alembic/env.py中导入方式：
# from backend.models.base import target_metadata

# ============================================
# 开发辅助函数
# ============================================


def reset_database(engine: Engine) -> None:
    """
    重置数据库（删除所有表后重新创建）
    ⚠️  仅用于开发环境！

    Args:
        engine: SQLAlchemy引擎实例
    """
    print("⚠️  正在重置数据库...")
    drop_all_tables(engine)
    create_all_tables(engine)
    print("✅ 数据库重置完成")


def get_model_by_name(model_name: str) -> type[SQLModel] | None:
    """
    根据名称获取模型类

    Args:
        model_name: 模型类名称

    Returns:
        模型类或None
    """
    models = get_all_models()
    for model in models:
        if model.__name__ == model_name:
            return model
    return None


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    # 验证模型
    # 打印表信息
    print_table_info()

    # 获取所有表名
    tables = get_table_names()
    print(f"📋 表名列表: {tables}")
