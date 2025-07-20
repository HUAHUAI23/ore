"""
通用工作流执行引擎包

简化的可扩展工作流引擎框架
"""

from .workflow_types import (
    NodeType, NodeExecutor, DatabaseSearcher, ConditionChecker, ExecutionSummary
)
from .engines import TreeWorkflowEngine
from .base import BaseWorkflowEngine

__version__ = "1.0.0"
__author__ = "Workflow Engine Team"

__all__ = [
    # 基础类型
    'NodeType',
    'NodeExecutor',
    'DatabaseSearcher', 
    'ConditionChecker',
    'ExecutionSummary',
    
    # 引擎类
    'BaseWorkflowEngine',
    'TreeWorkflowEngine',
]

# 便利函数
def create_tree_workflow(config: dict) -> TreeWorkflowEngine:
    """创建树形工作流引擎的便利函数"""
    return TreeWorkflowEngine(config)

def get_supported_workflow_types() -> list[str]:
    """获取支持的工作流类型列表
    
    Returns:
        支持的工作流类型名称列表
    """
    return ["tree"]  # 未来会添加更多类型 