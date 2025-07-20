"""
工作流引擎基础类型定义模块

只包含所有工作流类型都需要的最基础类型：
- NodeType: 基础节点类型枚举
- 基础函数类型别名
"""

from typing import Dict, List, Any, Callable, Awaitable
from enum import Enum

class NodeType(Enum):
    """基础节点类型枚举"""
    START = "start"
    PROCESS = "process"
    LEAF = "leaf"

# 基础函数类型别名
NodeExecutor = Callable[[str, Dict[str, Any]], Awaitable[Any]]
"""节点执行器函数类型"""

DatabaseSearcher = Callable[[str, str], Awaitable[str]]
"""数据库检索器函数类型"""

ConditionChecker = Callable[[str, str, Dict[str, Any]], bool]
"""条件检查器函数类型"""

# 基础执行摘要
class ExecutionSummary:
    """基础执行摘要"""
    def __init__(self, workflow_id: str, workflow_name: str, 
                 completed_count: int, total_count: int, results: Dict[str, Any]):
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.completed_count = completed_count
        self.total_count = total_count
        self.results = results
    
    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.completed_count / self.total_count
    
    @property
    def is_complete(self) -> bool:
        return self.completed_count == self.total_count 