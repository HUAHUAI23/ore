"""
工作流引擎基类定义
提供所有工作流执行引擎的抽象基类，定义通用接口和行为。
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Set, Optional
import time
from ..workflow_types import BaseWorkflowConfig, EventType, LogEntry


class BaseWorkflowEngine(ABC):
    """工作流引擎抽象基类

    定义所有工作流引擎必须实现的接口和通用行为：
    1. 基础配置管理
    2. 执行状态管理
    3. 执行器自定义接口
    4. 执行摘要生成
    """

    # 类属性声明,类型注解 - 提供更好的IDE支持
    workflow_id: str
    workflow_name: str
    workflow_description: str
    workflow_version: str
    workflow_type: str
    node_results: Dict[str, Any]
    completed_nodes: Set[str]
    failed_nodes: Set[str]
    running_tasks: Dict[str, asyncio.Task]
    start_time: Optional[float]
    end_time: Optional[float]
    execution_logs: List[LogEntry]
    node_executor: Any

    def __init__(self, workflow_config: BaseWorkflowConfig) -> None:
        """初始化工作流引擎基类"""
        # 基本配置 - 所有工作流都有的共同字段
        # 移除类型注解，只赋值（避免重复声明）
        self.workflow_id = workflow_config["workflow_id"]
        self.workflow_name = workflow_config["workflow_name"]
        self.workflow_description = workflow_config["description"]
        self.workflow_version = workflow_config["version"]
        self.workflow_type = workflow_config.get("type") or "generic"

        # 执行状态
        self.node_results = {}
        self.completed_nodes = set()
        self.failed_nodes = set()
        self.running_tasks = {}

        # 执行统计
        self.start_time = None
        self.end_time = None
        self.execution_logs = []

        # 子类可以重写来控制初始化流程
        self._initialize_from_config(workflow_config)

    @abstractmethod
    def _initialize_from_config(self, config: BaseWorkflowConfig) -> None:
        """从配置初始化引擎（子类实现具体逻辑）"""
        pass

    @abstractmethod
    async def execute_workflow(self) -> Any:
        """执行工作流（子类实现具体逻辑）"""
        pass

    # 通用的状态管理方法
    def _mark_node_completed(self, node_id: str, result: Any) -> None:
        """标记节点完成"""
        self.completed_nodes.add(node_id)
        self.node_results[node_id] = result
        self._log_event(
            EventType.NODE_SUCCESS.value, {"node_id": node_id, "result": result}
        )

    def _mark_node_failed(self, node_id: str, error: Exception) -> None:
        """标记节点失败"""
        self.failed_nodes.add(node_id)
        self.node_results[node_id] = f"ERROR: {error}"
        self._log_event(
            EventType.NODE_FAILED.value, {"node_id": node_id, "error": str(error)}
        )

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """记录执行事件"""
        self.execution_logs.append(
            {"timestamp": time.time(), "event_type": event_type, "data": data}
        )

    # 工作流状态查询接口
    @property
    def is_running(self) -> bool:
        """检查工作流是否正在运行"""
        return len(self.running_tasks) > 0

    @property
    def is_completed(self) -> bool:
        """检查工作流是否已完成"""
        return len(self.completed_nodes) > 0 and len(self.running_tasks) == 0

    def get_node_status(self, node_id: str) -> str:
        """获取节点状态"""
        if node_id in self.completed_nodes:
            return "completed"
        elif node_id in self.failed_nodes:
            return "failed"
        elif node_id in self.running_tasks:
            return "running"
        else:
            return "pending"

    def get_execution_logs(self, event_type: Optional[str] = None) -> List[LogEntry]:
        """获取执行日志"""
        if event_type is None:
            return self.execution_logs.copy()
        return [log for log in self.execution_logs if log["event_type"] == event_type]
