"""
树形工作流引擎类型定义

完全重构后的简化类型定义
"""

from typing import Any,  Callable, Coroutine, Dict, List, Optional, TypedDict
from dataclasses import dataclass
from enum import Enum

from ...workflow_types import NodeType,  BaseWorkflowConfig


# 具体实现类型别名
NodeExecutor = Callable[[str, Dict[str, Any]], Coroutine[Any, Any, Any]]
"""协程节点执行器函数类型 - 用于需要创建任务的场景"""

# 树形工作流配置类型定义
class TreeNodeConfig(TypedDict):
    """树形节点配置类型"""
    id: str
    name: str
    description: str
    prompt: str
    node_type: str  # NodeType枚举值的字符串形式

class TreeInputConfigDict(TypedDict):
    """树形输入配置字典类型"""
    include_prompt: bool
    include_previous_output: bool

class TreeEdgeConfig(TypedDict):
    """树形边配置类型"""
    from_node: str  # 源节点ID，使用from_node避免关键字冲突
    to_node: str    # 目标节点ID
    condition: str
    input_config: TreeInputConfigDict

class TreeWorkflowConfig(BaseWorkflowConfig):
    """树形工作流配置类型
    
    继承基础配置，扩展树形工作流特有字段
    """
    nodes: Dict[str, TreeNodeConfig]
    edges: List[TreeEdgeConfig]

@dataclass
class TreeInputConfig:
    """输入配置"""
    include_prompt: bool
    include_previous_output: bool
    
    @classmethod
    def from_dict(cls, data: TreeInputConfigDict) -> 'TreeInputConfig':
        return cls(
            include_prompt=data['include_prompt'],
            include_previous_output=data['include_previous_output'],
        )

@dataclass
class TreeNode:
    """树形节点"""
    id: str
    name: str
    description: str
    prompt: str
    node_type: NodeType
    database_connection: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: TreeNodeConfig) -> 'TreeNode':
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            prompt=data['prompt'],
            node_type=NodeType(data['node_type']),
            database_connection=data.get('database_connection')
        )

@dataclass
class TreeEdge:
    """树形边"""
    from_node: str
    to_node: str
    condition: str
    input_config: TreeInputConfig
    
    @classmethod
    def from_dict(cls, data: TreeEdgeConfig) -> 'TreeEdge':
        return cls(
            from_node=data['from_node'],
            to_node=data['to_node'],
            condition=data['condition'],
            input_config=TreeInputConfig.from_dict(data['input_config'])
        )

@dataclass
class ExecutionSummary:
    """基础执行摘要"""
    workflow_id: str
    workflow_name: str
    completed_count: int
    total_count: int
    results: Dict[str, Any]
    type: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.completed_count / self.total_count
    
    @property
    def is_complete(self) -> bool:
        return self.completed_count == self.total_count 

# 异常类
class TreeEngineError(Exception):
    """树形引擎错误"""
    pass

class TreeCycleError(TreeEngineError):
    """环路检测错误"""
    pass 