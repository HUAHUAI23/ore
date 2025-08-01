"""
树形工作流引擎实现 - 集成2025年最新LangChain LLM功能

支持多start节点，在图构建阶段进行环路检查
集成LangChain 0.3版本的最新LLM调用方式
"""

"""
简洁版树形工作流引擎 - 合理利用LangChain提示词模板

核心改进：
1. 使用input_variables进行变量替换而非字符串拼接
2. 利用partial_variables预设固定值
3. 保持代码简洁性，避免过度设计
"""

import asyncio
import os
from typing import Dict, List, Any, Set, Optional, Union, Callable, Awaitable
from collections import defaultdict
from datetime import datetime

# 统一配置管理
from config import workflow_settings

# LangChain 2025最新导入方式
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from pydantic import SecretStr

from ...base.engine import BaseWorkflowEngine
from ...workflow_types import NodeType
from .types import (
    TreeNode,
    TreeEdge,
    Condition,
    NodeInputData,
    ExecutionSummary,
    TreeCycleError,
    TreeWorkflowConfig,
    NodeExecutor,
    ConditionChecker,
)


class TreeWorkflowEngine(BaseWorkflowEngine):
    """树形工作流执行引擎 - 简洁利用LangChain提示词模板

    核心功能：
    1. 事件驱动的节点执行
    2. 自动依赖检查和并行执行
    3. 灵活的输入内容组合
    4. 多分叉输出支持
    5. 支持多个start节点
    6. 简洁利用LangChain提示词模板进行变量替换
    """

    node_executor: NodeExecutor
    condition_checker: ConditionChecker
    nodes: Dict[str, TreeNode]
    edges: List[TreeEdge]
    outgoing_edges: Dict[str, List[TreeEdge]]
    llm_model: Any  # LangChain ChatModel实例
    prompt_template: ChatPromptTemplate  # 统一的提示词模板

    def __init__(
        self,
        workflow_config: TreeWorkflowConfig,
        tracking_callbacks: Optional[Dict[str, Callable]] = None,
    ) -> None:
        """初始化树形工作流引擎

        Args:
            workflow_config: 工作流配置
            tracking_callbacks: 外部跟踪回调函数字典，可选参数
                - on_execution_start: (workflow_id, execution_id) -> None
                - on_node_completed: (execution_id, node_id, result) -> None
                - on_node_failed: (execution_id, node_id, error) -> None
                - on_execution_finished: (execution_id, summary) -> None
        """
        super().__init__(workflow_config)

        # 初始化LLM
        self._initialize_llm()

        # 创建统一的提示词模板
        self._create_prompt_template()

        self.node_executor = self._default_node_executor
        self.condition_checker = self._default_condition_checker

        # 存储外部跟踪回调函数
        self.tracking_callbacks = tracking_callbacks or {}

        # 执行ID，用于跟踪
        self.current_execution_id: Optional[int] = None

    def _initialize_llm(self) -> None:
        """初始化LangChain LLM模型"""
        # 使用统一配置管理
        config = workflow_settings.llm_config

        if not config.api_key:
            raise ValueError(
                f"未找到{config.provider.upper()}_API_KEY环境变量，请设置API密钥"
            )

        try:
            if config.provider == "openai":
                self.llm_model = ChatOpenAI(
                    model=config.model_name,
                    api_key=SecretStr(config.api_key),
                    base_url=config.api_base,
                    temperature=config.temperature,
                    max_completion_tokens=config.max_tokens,
                )
            else:
                raise ValueError(f"不支持的LLM提供商: {config.provider}")

            print(f"✅ LLM初始化成功: {config.provider}:{config.model_name}")

        except Exception as e:
            print(f"❌ LLM初始化失败: {e}")
            raise

    def _create_prompt_template(self) -> None:
        """创建统一的提示词模板 - 利用LangChain变量替换"""

        # 定义动态时间函数
        def get_current_time():
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 创建ChatPromptTemplate，使用input_variables和partial_variables
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                # 系统消息 - 使用模板变量
                (
                    "system",
                    """你是一个专业的AI工作流处理助手。

工作流信息：{workflow_name} (ID: {workflow_id})
当前时间：{current_time}
节点类型：{node_type}

任务描述：{node_description}

请根据输入内容进行处理，生成高质量的输出结果。""",
                ),
                # 人类消息 - 使用模板变量
                (
                    "human",
                    """节点名称：{node_name}

{task_prompt}

{input_content}

请处理以上内容。""",
                ),
            ]
        ).partial(
            # 使用partial_variables预设固定值和动态函数
            workflow_name=self.workflow_name,
            workflow_id=self.workflow_id,
            current_time=get_current_time,
        )

    def _prepare_template_variables(
        self, node: TreeNode, input_data: NodeInputData
    ) -> Dict[str, str]:
        """准备模板变量 - 简洁的变量组装"""
        variables = {
            "node_type": node.node_type.value,
            "node_name": node.name,
            "node_description": node.description or f"处理节点{node.name}的任务",
        }

        # 任务提示词
        if input_data.prompt:
            variables["task_prompt"] = f"任务提示：\n{input_data.prompt}"
        else:
            variables["task_prompt"] = "无特定任务提示"

        # 输入内容
        input_parts = []
        if input_data.previous_output:
            input_parts.append(f"前序输出：\n{input_data.previous_output}")
        else:
            input_parts.append("无前序输出")

        # 根据节点类型添加特殊说明
        if node.node_type == NodeType.LEAF:
            input_parts.append("\n注意：这是叶子节点，请生成最终结果。")

        variables["input_content"] = "\n".join(input_parts)

        return variables

    def _initialize_from_config(self, config: TreeWorkflowConfig) -> None:
        """从配置初始化树形引擎"""
        # 解析节点和边
        self.nodes = {
            node_id: TreeNode.from_dict(node_data)
            for node_id, node_data in config["nodes"].items()
        }
        self.edges = [TreeEdge.from_dict(edge_data) for edge_data in config["edges"]]

        # 构建执行图并检查环路
        self.outgoing_edges = self._build_execution_graph()

    def _build_execution_graph(self) -> Dict[str, List[TreeEdge]]:
        """构建执行图（邻接表）并检查环路"""
        graph: Dict[str, List[TreeEdge]] = defaultdict(list)
        for edge in self.edges:
            graph[edge.from_node].append(edge)

        # 在构建时检查环路
        if self._has_cycle(graph):
            raise TreeCycleError("检测到环路，树形工作流不允许环路")

        return dict(graph)

    def _has_cycle(self, graph: Dict[str, List[TreeEdge]]) -> bool:
        """检查是否有环路（DFS检测）"""
        # 状态：0-未访问，1-正在访问，2-已访问
        state = {node_id: 0 for node_id in self.nodes.keys()}

        def dfs(node_id: str) -> bool:
            if state[node_id] == 1:  # 正在访问中，发现回边
                return True
            if state[node_id] == 2:  # 已访问过
                return False

            state[node_id] = 1  # 标记为正在访问

            # 访问所有邻居
            for edge in graph.get(node_id, []):
                if dfs(edge.to_node):
                    return True

            state[node_id] = 2  # 标记为已访问
            return False

        # 对所有未访问的节点进行DFS
        for node_id in self.nodes.keys():
            if state[node_id] == 0:
                if dfs(node_id):
                    return True

        return False

    async def execute_workflow(self) -> ExecutionSummary:
        """执行树形工作流"""
        print(f"🚀 执行工作流: {self.workflow_name} ({self.workflow_id})")

        # 找到所有起始节点
        start_nodes = [
            node_id
            for node_id, node in self.nodes.items()
            if node.node_type == NodeType.START
        ]

        if not start_nodes:
            raise ValueError("未找到起始节点")

        print(f"🎯 起始节点: {[self.nodes[nid].name for nid in start_nodes]}")

        # 调用执行开始回调
        if (
            "on_execution_start" in self.tracking_callbacks
            and self.current_execution_id
        ):
            try:
                callback = self.tracking_callbacks["on_execution_start"]
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.workflow_id, self.current_execution_id)
                else:
                    callback(self.workflow_id, self.current_execution_id)
            except Exception as e:
                print(f"⚠️ 执行开始回调失败: {e}")

        # 启动所有起始节点
        for start_node_id in start_nodes:
            result = await self.node_executor(start_node_id, NodeInputData())
            self._mark_node_completed(start_node_id, result)
            # 调用节点完成的外部回调
            await self._call_node_completed_callback(start_node_id, result)
            await self._try_trigger_next_nodes(start_node_id)

        # 事件驱动循环
        await self._run_execution_loop()

        print("✅ 工作流执行完成！")

        # 生成执行摘要
        execution_summary = ExecutionSummary(
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            completed_count=len(self.completed_nodes),
            total_count=len(self.nodes),
            results=self.node_results,
        )

        # 调用执行完成回调
        if (
            "on_execution_finished" in self.tracking_callbacks
            and self.current_execution_id
        ):
            try:
                callback = self.tracking_callbacks["on_execution_finished"]
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_execution_id, execution_summary)
                else:
                    callback(self.current_execution_id, execution_summary)
            except Exception as e:
                print(f"⚠️ 执行完成回调失败: {e}")

        return execution_summary

    async def _run_execution_loop(self) -> None:
        """运行事件驱动的执行循环"""
        while self.running_tasks:
            completed_task_ids = []
            for node_id, task in self.running_tasks.items():
                if task.done():
                    completed_task_ids.append(node_id)

                    try:
                        result = await task
                        self._mark_node_completed(node_id, result)
                        # 调用节点完成的外部回调
                        await self._call_node_completed_callback(node_id, result)
                    except Exception as e:
                        print(f"❌ 节点 {self.nodes[node_id].name} 执行失败: {e}")
                        self._mark_node_failed(node_id, e)
                        # 调用节点失败的外部回调
                        await self._call_node_failed_callback(node_id, e)

            # 清理已完成的任务并触发后续节点
            for node_id in completed_task_ids:
                del self.running_tasks[node_id]
                await self._try_trigger_next_nodes(node_id)

            # 短暂休眠避免忙等待
            if self.running_tasks:
                await asyncio.sleep(0.1)

    async def _try_trigger_next_nodes(self, completed_node_id: str) -> None:
        """尝试触发后续节点"""
        outgoing_edges = self.outgoing_edges.get(completed_node_id, [])

        for edge in outgoing_edges:
            target_node_id = edge.to_node

            # 先检查是否所有前驱节点都已完成
            if not self._check_all_prerequisites_completed(target_node_id):
                print(f"⏳ 节点 {self.nodes[target_node_id].name} 等待前驱节点完成")
                continue

            # 然后检查条件是否满足
            if edge.condition is not None:
                if not self.condition_checker(
                    edge.condition, self.node_results[completed_node_id]
                ):
                    node_name = self.nodes[target_node_id].name
                    print(f"🚫 条件不满足，跳过节点: {node_name}")
                    continue

            # 避免重复执行
            if (
                target_node_id in self.running_tasks
                or target_node_id in self.completed_nodes
            ):
                continue

            # 准备输入数据并启动任务
            input_data = self._prepare_node_input(target_node_id, edge)
            task = asyncio.create_task(self.node_executor(target_node_id, input_data))
            self.running_tasks[target_node_id] = task

            node = self.nodes[target_node_id]
            print(f"🔄 启动节点: {node.name} ({node.description})")

    def _check_all_prerequisites_completed(self, node_id: str) -> bool:
        """检查节点的所有前驱是否都已完成"""
        prerequisites = set()

        # 收集所有指向该节点的前驱
        for edge in self.edges:
            if edge.to_node == node_id:
                prerequisites.add(edge.from_node)

        # 检查是否所有前驱都已完成
        missing_prereqs = prerequisites - self.completed_nodes
        if missing_prereqs:
            missing_names = [self.nodes[pid].name for pid in missing_prereqs]
            print(f"   等待前驱: {', '.join(missing_names)}")
            return False

        return True

    def _prepare_node_input(self, node_id: str, edge: TreeEdge) -> NodeInputData:
        """根据边配置准备节点输入"""
        node = self.nodes[node_id]
        input_config = edge.input_config

        # 1. 任务提示词
        prompt = node.prompt if input_config.include_prompt else None

        # 2. 收集所有直接前驱的输出
        previous_output = None
        if input_config.include_previous_output:
            all_predecessors = self._get_all_completed_predecessors(node_id)
            if all_predecessors:
                previous_output = self._combine_predecessor_outputs(all_predecessors)

        return NodeInputData(prompt=prompt, previous_output=previous_output)

    def _get_all_completed_predecessors(self, node_id: str) -> List[str]:
        """获取指定节点的所有已完成的直接前驱节点"""
        predecessors = []

        # 遍历所有边，找到指向目标节点的边
        for edge in self.edges:
            if edge.to_node == node_id and edge.from_node in self.completed_nodes:
                predecessors.append(edge.from_node)

        # 去重保持顺序
        seen = set()
        unique_predecessors = []
        for pred_id in predecessors:
            if pred_id not in seen:
                seen.add(pred_id)
                unique_predecessors.append(pred_id)

        return unique_predecessors

    def _combine_predecessor_outputs(self, predecessor_ids: List[str]) -> str:
        """组合多个前驱节点的输出结果"""
        if not predecessor_ids:
            return ""

        # 单个前驱，直接返回结果
        if len(predecessor_ids) == 1:
            return str(self.node_results[predecessor_ids[0]])

        # 多个前驱，用标识符组合
        combined_parts = []
        for pred_id in predecessor_ids:
            pred_name = self.nodes[pred_id].name
            pred_result = self.node_results[pred_id]
            combined_parts.append(f"[{pred_name}]: {pred_result}")

        return " | ".join(combined_parts)

    def _default_condition_checker(
        self, condition: Optional[Condition], node_output: Any
    ) -> bool:
        """默认条件检查器"""
        if condition is None:
            return True
        return condition.check(node_output)

    async def _default_node_executor(
        self, node_id: str, input_data: NodeInputData
    ) -> Any:
        """节点执行器 - 利用LangChain模板变量替换"""
        node = self.nodes[node_id]

        # 起始节点直接返回
        if node.node_type == NodeType.START:
            return f"工作流启动 - {self.workflow_name}"

        try:
            # 准备模板变量
            template_variables = self._prepare_template_variables(node, input_data)

            print(f"🤖 调用LLM处理节点: {node.name}")
            print(f"   节点类型: {node.node_type.value}")

            # 使用LangChain模板的invoke方法进行变量替换
            formatted_prompt = self.prompt_template.invoke(template_variables)
            messages = formatted_prompt.to_messages()

            print(f"   消息数量: {len(messages)}")

            # 异步调用LLM
            try:
                response = await self.llm_model.ainvoke(messages)
                result = (
                    response.content if hasattr(response, "content") else str(response)
                )
                print(f"✅ LLM响应完成，输出长度: {len(result)} 字符")
                return result

            except AttributeError:
                # 回退到同步调用
                print("⚠️  回退到同步模式")
                response = await asyncio.to_thread(self.llm_model.invoke, messages)
                result = (
                    response.content if hasattr(response, "content") else str(response)
                )
                print(f"✅ LLM响应完成，输出长度: {len(result)} 字符")
                return result

        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            # 降级到简单文本处理
            return await self._fallback_text_processing(node, input_data)

    async def _fallback_text_processing(
        self, node: TreeNode, input_data: NodeInputData
    ) -> str:
        """LLM调用失败时的降级处理"""
        print(f"🔄 降级到文本处理模式: {node.name}")

        # 组装处理输入
        input_parts = []

        if input_data.prompt is not None:
            input_parts.append(f"PROMPT: {input_data.prompt}")

        if input_data.previous_output is not None:
            input_parts.append(f"PREV: {input_data.previous_output}")

        # 根据节点类型进行不同的处理
        if node.node_type == NodeType.START:
            result = f"START[{node.name}]: 工作流已启动"
        elif node.node_type == NodeType.LEAF:
            full_input = " | ".join(input_parts)
            result = f"FINAL[{node.name}]: {full_input[:200]}..."
        else:
            full_input = " | ".join(input_parts)
            result = f"PROCESSED[{node.name}]: {full_input[:150]}..."

        # 模拟处理延迟
        await asyncio.sleep(0.2)

        return result

    async def _call_node_completed_callback(self, node_id: str, result: Any) -> None:
        """调用节点完成的外部回调"""
        if "on_node_completed" in self.tracking_callbacks and self.current_execution_id:
            try:
                callback = self.tracking_callbacks["on_node_completed"]
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_execution_id, node_id, result)
                else:
                    callback(self.current_execution_id, node_id, result)
            except Exception as e:
                print(f"⚠️ 节点完成回调失败: {e}")

    async def _call_node_failed_callback(self, node_id: str, error: Exception) -> None:
        """调用节点失败的外部回调"""
        if "on_node_failed" in self.tracking_callbacks and self.current_execution_id:
            try:
                callback = self.tracking_callbacks["on_node_failed"]
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.current_execution_id, node_id, error)
                else:
                    callback(self.current_execution_id, node_id, error)
            except Exception as e:
                print(f"⚠️ 节点失败回调失败: {e}")

    def set_execution_id(self, execution_id: int) -> None:
        """设置当前执行ID"""
        self.current_execution_id = execution_id

    def _mark_node_completed(self, node_id: str, result: Any) -> None:
        """重写以提供树形特有的日志"""
        super()._mark_node_completed(node_id, result)
        node = self.nodes[node_id]

        if node.node_type == NodeType.LEAF:
            print(f"🎯 叶子节点完成: {node.name}")
        elif node.node_type == NodeType.START:
            print(f"✓ 起始节点完成: {node.name}")
        else:
            print(f"✓ 节点完成: {node.name}")

    def _mark_node_failed(self, node_id: str, error: Exception) -> None:
        """重写以提供树形特有的日志"""
        super()._mark_node_failed(node_id, error)
        node = self.nodes[node_id]
        print(f"❌ 节点失败: {node.name}")
        print(f"   错误: {error}")
