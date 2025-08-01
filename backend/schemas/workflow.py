"""
工作流相关的 Pydantic 模式定义
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator

from backend.models.workflow import WorkflowStatus, ExecutionStatus

# 导入工作流引擎类型，如果导入失败则使用基础类型
from workflow_engine.engines.tree.types import TreeNodeConfig, TreeEdgeConfig


# 工作流相关模式
class WorkflowCreateRequest(BaseModel):
    """创建工作流请求"""

    name: str = Field(..., max_length=200, description="工作流名称")
    description: str = Field(..., max_length=1000, description="工作流描述")
    version: str = Field(..., max_length=50, description="工作流版本")
    type: str = Field(default="tree", description="工作流类型")
    nodes: Dict[str, TreeNodeConfig] = Field(..., description="工作流节点配置")
    edges: List[TreeEdgeConfig] = Field(..., description="工作流边配置")

    @field_validator("nodes")
    @classmethod
    def validate_nodes(cls, v):
        """验证节点配置"""
        if not isinstance(v, dict) or not v:
            raise ValueError("nodes 必须是非空字典")

        # 检查是否有 START 节点
        start_nodes = [node for node in v.values() if node.get("node_type") == "START"]
        if not start_nodes:
            raise ValueError("必须至少包含一个 START 类型的节点")

        return v

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, v):
        """验证边配置"""
        if not isinstance(v, list):
            raise ValueError("edges 必须是列表类型")
        return v


class WorkflowUpdateRequest(BaseModel):
    """更新工作流请求"""

    name: Optional[str] = Field(None, max_length=200, description="工作流名称")
    description: Optional[str] = Field(None, max_length=1000, description="工作流描述")
    version: Optional[str] = Field(None, max_length=50, description="工作流版本")
    nodes: Optional[Dict[str, TreeNodeConfig]] = Field(
        None, description="工作流节点配置"
    )
    edges: Optional[List[TreeEdgeConfig]] = Field(None, description="工作流边配置")
    status: Optional[WorkflowStatus] = Field(None, description="工作流状态")


class WorkflowResponse(BaseModel):
    """工作流响应模式"""

    id: int
    name: str
    description: str
    version: str
    type: str
    nodes: Dict[str, Any]
    edges: List[Any]
    status: WorkflowStatus
    created_by: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkflowListItem(BaseModel):
    """工作流列表项（简化版）"""

    id: int
    name: str
    description: str
    version: str
    type: str
    status: WorkflowStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 工作流执行相关模式
class WorkflowExecuteRequest(BaseModel):
    """执行工作流请求"""

    workflow_id: int = Field(..., description="工作流ID")


class WorkflowExecutionResponse(BaseModel):
    """工作流执行响应模式"""

    id: int
    workflow_id: int
    status: ExecutionStatus
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    total_nodes: int
    completed_nodes: int
    failed_nodes: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowExecutionListItem(BaseModel):
    """工作流执行列表项（简化版）"""

    id: int
    workflow_id: int
    status: ExecutionStatus
    total_nodes: int
    completed_nodes: int
    failed_nodes: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowExecutionStats(BaseModel):
    """工作流执行统计"""

    execution_id: int
    success_rate: float
    duration_seconds: Optional[float]
    is_finished: bool
