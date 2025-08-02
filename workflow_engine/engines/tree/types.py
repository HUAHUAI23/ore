"""
树形工作流引擎类型定义

完全重构后的简化类型定义
"""

from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    TypedDict,
    Union,
    NotRequired,
)
from dataclasses import dataclass, field
from enum import Enum
import re

from ...workflow_types import NodeType, BaseWorkflowConfig


@dataclass
class NodeInputData:
    """节点输入数据类型安全结构"""

    prompt: Optional[str] = None
    previous_output: Optional[str] = None


# 具体实现类型别名
NodeExecutor = Callable[[str, "NodeInputData"], Coroutine[Any, Any, Any]]
"""协程节点执行器函数类型 - 用于需要创建任务的场景"""

ConditionChecker = Callable[[Optional["Condition"], Any], bool]
"""条件检查器函数类型"""


class ConditionConfig(TypedDict):
    """条件配置类型 - 用于数据库存储"""

    match_target: str  # 匹配目标: "node_output"
    match_type: str  # 匹配方式: "contains", "not_contains", "fuzzy", "regex"
    match_value: str  # 匹配值
    case_sensitive: bool  # 是否区分大小写


class TreeInputConfigDict(TypedDict):
    """树形输入配置字典类型"""

    include_prompt: bool
    include_previous_output: bool


# 树形工作流配置类型定义
class TreeNodeConfig(TypedDict):
    """树形节点配置类型"""

    id: str
    name: str
    description: str
    prompt: str
    node_type: str  # NodeType枚举值的字符串形式
    conditions: NotRequired[
        List[ConditionConfig]
    ]  # 仅作记录用于同步前端可视化编排需要，执行过程中条件判断是根据边 (Edge) 的 condition 字段 来决定的
    input_config: TreeInputConfigDict


class TreeEdgeConfig(TypedDict):
    """树形边配置类型"""

    from_node: str  # 源节点ID，使用from_node避免关键字冲突
    to_node: str  # 目标节点ID
    condition: Optional[ConditionConfig]  # 改为结构化条件


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
    def from_dict(cls, data: TreeInputConfigDict) -> "TreeInputConfig":
        return cls(
            include_prompt=data["include_prompt"],
            include_previous_output=data["include_previous_output"],
        )


@dataclass
class TreeNode:
    """树形节点"""

    id: str
    name: str
    description: str
    prompt: str
    node_type: NodeType
    input_config: TreeInputConfig
    database_connection: Optional[str] = None

    @classmethod
    def from_dict(cls, data: TreeNodeConfig) -> "TreeNode":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            prompt=data["prompt"],
            node_type=NodeType(data["node_type"]),
            database_connection=data.get("database_connection"),
            input_config=TreeInputConfig.from_dict(data["input_config"]),
        )


@dataclass
class Condition:
    """条件数据类"""

    match_target: str
    match_type: str
    match_value: str
    case_sensitive: bool = True

    @classmethod
    def from_dict(cls, data: ConditionConfig) -> "Condition":
        return cls(
            match_target=data["match_target"],
            match_type=data["match_type"],
            match_value=data["match_value"],
            case_sensitive=data.get("case_sensitive", True),
        )

    def check(self, node_output: Any) -> bool:
        """检查条件是否满足"""
        if self.match_target != "node_output":
            return False

        output_str = str(node_output)
        match_value = self.match_value

        # 处理大小写敏感性
        if not self.case_sensitive:
            output_str = output_str.lower()
            match_value = match_value.lower()

        if self.match_type == "contains":
            return match_value in output_str
        elif self.match_type == "not_contains":
            return match_value not in output_str
        elif self.match_type == "fuzzy":
            # 简单模糊匹配：移除空格后检查包含关系
            clean_output = re.sub(r"\s+", "", output_str)
            clean_match = re.sub(r"\s+", "", match_value)
            return clean_match in clean_output
        elif self.match_type == "regex":
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(match_value, output_str, flags))
            except re.error:
                return False
        else:
            return False


@dataclass
class TreeEdge:
    """树形边"""

    from_node: str
    to_node: str
    condition: Optional[Condition]

    @classmethod
    def from_dict(cls, data: TreeEdgeConfig) -> "TreeEdge":
        condition = None
        condition_data = data.get("condition")
        if condition_data is not None:
            condition = Condition.from_dict(condition_data)

        return cls(
            from_node=data["from_node"],
            to_node=data["to_node"],
            condition=condition,
        )


@dataclass
class ExecutionSummary:
    """基础执行摘要"""

    workflow_id: str
    workflow_name: str
    completed_count: int
    failed_count: int = 0  # 失败的节点数
    skipped_count: int = 0  # 因条件不满足而跳过的节点数
    total_count: int = 0  # 总节点数
    results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None  # 整体错误信息
    type: Optional[str] = None  # 兼容性字段

    @property
    def executed_count(self) -> int:
        """实际执行的节点数（完成 + 失败）"""
        return self.completed_count + self.failed_count

    @property
    def success_rate(self) -> float:
        """成功率（基于实际执行的节点）"""
        if self.executed_count == 0:
            return 0.0
        return self.completed_count / self.executed_count

    @property
    def execution_rate(self) -> float:
        """执行率（实际执行节点数 / 总节点数）"""
        if self.total_count == 0:
            return 0.0
        return self.executed_count / self.total_count

    @property
    def is_complete(self) -> bool:
        """判断工作流是否成功完成

        成功的条件：
        1. 没有失败的节点 (failed_count == 0)
        2. 没有整体错误信息 (error_message is None)
        3. 至少有一个节点被成功执行 (completed_count > 0)

        注意：跳过的节点不影响成功状态，因为这是条件分支的正常行为
        """
        return (
            self.failed_count == 0
            and self.error_message is None
            and self.completed_count > 0
        )

    @property
    def is_failed(self) -> bool:
        """判断工作流是否失败"""
        return self.failed_count > 0 or self.error_message is not None

    def get_status_description(self) -> str:
        """获取状态描述"""
        if self.is_complete:
            return f"成功完成 ({self.completed_count}/{self.total_count} 节点)"
        elif self.is_failed:
            return f"执行失败 (完成:{self.completed_count}, 失败:{self.failed_count})"
        else:
            return f"执行中 ({self.executed_count}/{self.total_count} 节点)"


# 异常类
class TreeEngineError(Exception):
    """树形引擎错误"""

    pass


class TreeCycleError(TreeEngineError):
    """环路检测错误"""

    pass


class ConditionError(TreeEngineError):
    """条件检查错误"""

    pass
