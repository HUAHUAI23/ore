"""
工作流相关数据库模型定义 - 使用纯 SQLModel 语法
"""

from datetime import datetime, timezone
from typing import Optional, Any, TYPE_CHECKING
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from pydantic.alias_generators import to_snake

# 导入工作流引擎类型
try:
    from workflow_engine.engines.tree.types import TreeWorkflowConfig
except ImportError:
    # 如果导入失败，定义一个简单的类型
    TreeWorkflowConfig = dict

if TYPE_CHECKING:
    from .user import User


class WorkflowStatus(str, Enum):
    """工作流状态枚举"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ExecutionStatus(str, Enum):
    """执行状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow(SQLModel, table=True):
    """工作流数据库模型 - 使用纯 SQLModel 语法"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)

    # 主键，同时作为 workflow_id
    id: Optional[int] = Field(default=None, primary_key=True, description="工作流ID")

    # TreeWorkflowConfig 核心字段平铺
    name: str = Field(max_length=200, index=True, description="工作流名称")

    description: str = Field(max_length=1000, description="工作流描述")

    version: str = Field(max_length=50, description="工作流版本")

    type: str = Field(default="tree", max_length=50, description="工作流类型")

    # TreeWorkflowConfig 的 nodes 和 edges 存储为 JSON
    nodes: dict[str, Any] = Field(
        default_factory=dict, description="工作流节点配置", sa_column=Column(JSON)
    )

    edges: list[dict[str, Any]] = Field(
        default_factory=list, description="工作流边配置", sa_column=Column(JSON)
    )

    # 扩展的数据库管理字段
    status: WorkflowStatus = Field(
        default=WorkflowStatus.ACTIVE, description="工作流状态"
    )

    # 用户关联
    created_by: int = Field(foreign_key="user.id", description="创建者ID")

    # 时间字段
    created_at: Optional[datetime] = Field(
        default=None,
        description="创建时间",
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now()
        ),  # timezone=True
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        description="更新时间",
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # 关系定义
    executions: list["WorkflowExecution"] = Relationship(back_populates="workflow")
    created_by_user: "User" = Relationship(back_populates="workflows")

    def to_tree_config(self) -> dict[str, Any]:
        """转换为 TreeWorkflowConfig 字典"""
        return {
            "workflow_id": str(self.id),
            "workflow_name": self.name,
            "description": self.description,
            "version": self.version,
            "type": self.type,
            "nodes": self.nodes,
            "edges": self.edges,
        }


class WorkflowExecution(SQLModel, table=True):
    """工作流执行历史数据库模型 - 使用纯 SQLModel 语法"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)

    id: Optional[int] = Field(default=None, primary_key=True, description="执行ID")

    # 关联工作流
    workflow_id: int = Field(foreign_key="workflow.id", description="工作流ID")

    # 执行状态和结果
    status: ExecutionStatus = Field(
        default=ExecutionStatus.PENDING, description="执行状态"
    )

    # 执行结果数据 - 存储节点执行结果
    result_data: Optional[dict[str, Any]] = Field(
        default=None, description="执行结果数据", sa_column=Column(JSON)
    )

    # 错误信息
    error_message: Optional[str] = Field(default=None, description="错误信息")

    # 执行统计
    total_nodes: int = Field(default=0, description="总节点数")

    completed_nodes: int = Field(default=0, description="已完成节点数")

    failed_nodes: int = Field(default=0, description="失败节点数")

    # 执行时间
    started_at: Optional[datetime] = Field(
        default=None,
        description="开始时间",
        sa_column=Column(
            DateTime(timezone=True),
        ),
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="完成时间",
        sa_column=Column(
            DateTime(timezone=True),
        ),
    )

    # 创建时间
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),  # 🔥 设置默认值
        description="创建时间",
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now()
        ),  # timezone=True
    )

    # 关系定义
    workflow: Workflow = Relationship(back_populates="executions")

    @property
    def execution_duration(self) -> Optional[float]:
        """计算执行时长（秒）"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def progress_percentage(self) -> float:
        """计算执行进度百分比"""
        if self.total_nodes == 0:
            return 0.0
        return (self.completed_nodes / self.total_nodes) * 100
