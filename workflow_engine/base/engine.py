"""
工作流引擎基类定义

提供所有工作流执行引擎的抽象基类，定义通用接口和行为。
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Set, Optional
import time

from ..workflow_types import (
    NodeExecutor, DatabaseSearcher, ConditionChecker, ExecutionSummary
)

class BaseWorkflowEngine(ABC):
    """工作流引擎抽象基类
    
    定义所有工作流引擎必须实现的接口和通用行为：
    1. 基础配置管理
    2. 执行状态管理  
    3. 执行器自定义接口
    4. 执行摘要生成
    """
    
    def __init__(self, workflow_config: Dict[str, Any]) -> None:
        """初始化工作流引擎基类"""
        # 基本配置 - 所有工作流都有的共同字段
        self.workflow_id: str = workflow_config.get('workflow_id', 'unknown')
        self.workflow_name: str = workflow_config.get('name', 'Unknown Workflow')
        self.workflow_type: str = workflow_config.get('type', 'generic')
        
        # 执行状态
        self.node_results: Dict[str, Any] = {}
        self.completed_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # 执行统计
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.execution_logs: List[Dict[str, Any]] = []
        
        # 可自定义的执行函数
        self.node_executor: NodeExecutor = self._default_node_executor
        self.database_searcher: DatabaseSearcher = self._default_database_searcher
        self.condition_checker: ConditionChecker = self._default_condition_checker
        
        # 子类可以重写来控制初始化流程
        self._initialize_from_config(workflow_config)
    
    @abstractmethod
    def _initialize_from_config(self, config: Dict[str, Any]) -> None:
        """从配置初始化引擎（子类实现具体逻辑）"""
        pass
    
    @abstractmethod
    async def execute_workflow(self) -> ExecutionSummary:
        """执行工作流（子类实现具体逻辑）"""
        pass
    
    # 通用的配置接口
    def set_node_executor(self, executor: NodeExecutor) -> None:
        """设置自定义节点执行器"""
        self.node_executor = executor
        
    def set_database_searcher(self, searcher: DatabaseSearcher) -> None:
        """设置自定义数据库检索器"""
        self.database_searcher = searcher
        
    def set_condition_checker(self, checker: ConditionChecker) -> None:
        """设置自定义条件检查器"""
        self.condition_checker = checker
    
    # 通用的状态管理方法
    def _mark_node_completed(self, node_id: str, result: Any) -> None:
        """标记节点完成"""
        self.completed_nodes.add(node_id)
        self.node_results[node_id] = result
        self._log_event("node_completed", {"node_id": node_id})
    
    def _mark_node_failed(self, node_id: str, error: Exception) -> None:
        """标记节点失败"""
        self.failed_nodes.add(node_id)
        self.node_results[node_id] = f"ERROR: {error}"
        self._log_event("node_failed", {"node_id": node_id, "error": str(error)})
    
    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """记录执行事件"""
        self.execution_logs.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        })
    
    # 默认实现方法
    async def _default_node_executor(self, node_id: str, input_data: Dict[str, Any]) -> Any:
        """默认节点执行器"""
        await asyncio.sleep(0.1)
        return f"RESULT_{node_id.upper()}"
    
    async def _default_database_searcher(self, connection: str, search_input: str) -> str:
        """默认数据库检索器"""
        await asyncio.sleep(0.05)
        return f"DB_RESULT_{connection}"
    
    def _default_condition_checker(self, condition: str, completed_node_id: str, results: Dict[str, Any]) -> bool:
        """默认条件检查器"""
        if condition == "true":
            return True
        try:
            context = {
                'completed_node': completed_node_id,
                'results': results
            }
            return eval(condition, {"__builtins__": {}}, context)
        except Exception:
            return False
    
    # 工作流状态查询接口
    @property
    def is_running(self) -> bool:
        """检查工作流是否正在运行"""
        return len(self.running_tasks) > 0
    
    @property
    def is_completed(self) -> bool:
        """检查工作流是否已完成"""
        return len(self.completed_nodes) > 0 and len(self.running_tasks) == 0
    
    @property
    def success_rate(self) -> float:
        """计算成功率"""
        total = len(self.completed_nodes) + len(self.failed_nodes)
        if total == 0:
            return 0.0
        return len(self.completed_nodes) / total
    
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
    
    def get_execution_logs(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取执行日志"""
        if event_type is None:
            return self.execution_logs.copy()
        return [log for log in self.execution_logs if log["event_type"] == event_type] 