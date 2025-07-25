"""
工作流引擎基础类型定义模块

包含所有工作流类型都需要的基础类型：
- NodeType: 基础节点类型枚举
- 基础函数类型别名
- 配置类型定义
"""

from typing import Dict, Any, Callable, Optional, TypedDict, Coroutine, Awaitable
from enum import Enum
from dataclasses import dataclass

class NodeType(Enum):
    """基础节点类型枚举"""
    START = "start"
    PROCESS = "process"
    LEAF = "leaf"

class EventType(Enum):
    """执行事件类型枚举"""
    NODE_FAILED = "node_failed"
    NODE_SUCCESS = "node_success"

class LogEntry(TypedDict):
    """执行日志条目类型"""
    timestamp: float
    event_type: str
    data: Dict[str, Any]

# 基础配置类型定义
class BaseWorkflowConfig(TypedDict):
    """基础工作流配置类型
    
    所有工作流引擎都必须支持的基础配置字段
    """
    workflow_id: str
    name: str
    type: Optional[str]  # 工作流类型标识



# 基础执行摘要
