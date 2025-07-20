"""
树形工作流引擎类型定义

完全重构后的简化类型定义
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ...workflow_types import NodeType, ExecutionSummary

class DatabaseSearchInput(Enum):
    """数据库检索输入类型"""
    PROMPT = "prompt"
    PREVIOUS_OUTPUT = "previous_output"
    PROMPT_AND_PREVIOUS = "prompt_and_previous"

class TreeExecutionStrategy(Enum):
    """树形执行策略"""
    EVENT_DRIVEN = "event_driven"

@dataclass
class TreeInputConfig:
    """输入配置"""
    include_prompt: bool
    include_previous_output: bool
    include_database_search: bool
    database_search_input: DatabaseSearchInput
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeInputConfig':
        return cls(
            include_prompt=data['include_prompt'],
            include_previous_output=data['include_previous_output'],
            include_database_search=data['include_database_search'],
            database_search_input=DatabaseSearchInput(data['database_search_input'])
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
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeNode':
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
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeEdge':
        return cls(
            from_node=data['from'],
            to_node=data['to'],
            condition=data['condition'],
            input_config=TreeInputConfig.from_dict(data['input_config'])
        )

@dataclass
class TreeExecutionStats:
    """执行统计"""
    total_nodes: int = 0
    executed_nodes: int = 0

@dataclass 
class TreeExecutionSummary:
    """执行摘要"""
    base_summary: ExecutionSummary
    stats: TreeExecutionStats
    execution_strategy: TreeExecutionStrategy = TreeExecutionStrategy.EVENT_DRIVEN
    
    @property
    def workflow_id(self) -> str:
        return self.base_summary.workflow_id
    
    @property
    def workflow_name(self) -> str:
        return self.base_summary.workflow_name
    
    @property
    def success_rate(self) -> float:
        return self.base_summary.success_rate
    
    @property
    def is_complete(self) -> bool:
        return self.base_summary.is_complete

# 异常类
class TreeEngineError(Exception):
    """树形引擎错误"""
    pass

class TreeCycleError(TreeEngineError):
    """环路检测错误"""
    pass 