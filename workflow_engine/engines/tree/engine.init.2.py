"""
树形工作流引擎实现 - 集成2025年最新LangChain LLM功能

支持多start节点，在图构建阶段进行环路检查
集成LangChain 0.3版本的最新LLM调用方式
"""

import asyncio
import os
from typing import Dict, List, Any, Set, Optional, Union
from collections import defaultdict

# 环境变量支持
from dotenv import load_dotenv

# LangChain 2025最新导入方式
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from ...base.engine import BaseWorkflowEngine
from ...workflow_types import NodeType
from .types import (
    TreeNode, TreeEdge, Condition, NodeInputData,
    ExecutionSummary,
    TreeCycleError, TreeWorkflowConfig, NodeExecutor, ConditionChecker
)

class TreeWorkflowEngine(BaseWorkflowEngine):
    """树形工作流执行引擎 - 集成LangChain LLM
    
    核心功能：
    1. 事件驱动的节点执行
    2. 自动依赖检查和并行执行  
    3. 灵活的输入内容组合
    4. 多分叉输出支持
    5. 支持多个start节点
    6. 集成LangChain LLM调用能力（优化版）
    """
    node_executor: NodeExecutor
    condition_checker: ConditionChecker
    nodes: Dict[str, TreeNode]
    edges: List[TreeEdge]
    outgoing_edges: Dict[str, List[TreeEdge]]
    llm_model: Any  # LangChain ChatModel实例
    prompt_templates: Dict[str, ChatPromptTemplate]  # 节点提示词模板缓存

    
    def __init__(self, workflow_config: TreeWorkflowConfig) -> None:
        """初始化树形工作流引擎"""
        super().__init__(workflow_config)
        
        # 初始化LLM
        self._initialize_llm()
        
        # 初始化提示词模板缓存
        self.prompt_templates = {}
        
        self.node_executor: NodeExecutor = self._default_node_executor
        self.condition_checker: ConditionChecker = self._default_condition_checker
    
    def _initialize_llm(self) -> None:
        """初始化LangChain LLM模型"""
        # 加载环境变量
        load_dotenv()
        
        # 从环境变量获取配置
        llm_provider = os.getenv('LLM_PROVIDER', 'openai')  # 默认使用OpenAI
        llm_model_name = os.getenv('LLM_MODEL_NAME', 'gpt-3.5-turbo')
        api_key = os.getenv('OPENAI_API_KEY')  # 或其他对应的API_KEY
        api_base = os.getenv('API_BASE')  # 可选的API端点
        
        if not api_key:
            raise ValueError(f"未找到{llm_provider.upper()}_API_KEY环境变量，请设置API密钥")
        
        try:
            # 使用2025年最新的init_chat_model方式
            # 支持多种provider：openai, anthropic, google_vertexai, ollama等
            model_identifier = f"{llm_provider}:{llm_model_name}"
            
            # 构建LLM初始化参数
            llm_kwargs = {
                'temperature': float(os.getenv('LLM_TEMPERATURE', '0.7')),
                'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '1000')),
            }
            
            # 如果有自定义API端点
            if api_base:
                llm_kwargs['base_url'] = api_base
            
            # 初始化LLM模型
            self.llm_model = init_chat_model(
                model_identifier,
                **llm_kwargs
            )
            
            print(f"✅ LLM初始化成功: {model_identifier}")
            print(f"   Temperature: {llm_kwargs['temperature']}")
            print(f"   Max Tokens: {llm_kwargs['max_tokens']}")
            
        except Exception as e:
            print(f"❌ LLM初始化失败: {e}")
            print("🔧 请检查以下环境变量配置:")
            print("   - OPENAI_API_KEY (或对应provider的API_KEY)")
            print("   - LLM_PROVIDER (可选，默认openai)")
            print("   - LLM_MODEL_NAME (可选，默认gpt-3.5-turbo)")
            print("   - API_BASE (可选，自定义API端点)")
            raise
    
    def _create_prompt_template(self, node: TreeNode, input_data: NodeInputData) -> ChatPromptTemplate:
        """创建或获取节点的提示词模板
        
        Args:
            node: 节点信息
            input_data: 输入数据
            
        Returns:
            ChatPromptTemplate实例
        """
        # 使用节点ID作为缓存键
        cache_key = f"{node.id}_{hash(str(input_data.prompt))}"
        
        if cache_key in self.prompt_templates:
            return self.prompt_templates[cache_key]
        
        # 构建消息模板列表
        messages = []
        
        # 1. 系统消息：设置AI角色和任务描述
        system_content_parts = []
        
        # 基础角色设定
        system_content_parts.append("你是一个专业的AI工作流处理助手。")
        
        # 节点特定描述
        if node.description:
            system_content_parts.append(f"当前任务：{node.description}")
        
        # 节点类型特定指令
        if node.node_type == NodeType.START:
            system_content_parts.append("这是工作流的起始节点，请初始化相关信息。")
        elif node.node_type == NodeType.LEAF:
            system_content_parts.append("这是工作流的叶子节点，请产生最终结果。")
        else:
            system_content_parts.append("请处理输入信息并生成高质量的输出。")
        
        # 输出格式要求
        system_content_parts.append("请提供清晰、准确且有用的回复。")
        
        system_content = "\n".join(system_content_parts)
        messages.append(SystemMessage(content=system_content))
        
        # 2. 人类消息：组合任务提示和前序输出
        user_content_parts = []
        
        # 任务提示词（如果有）
        if input_data.prompt:
            user_content_parts.append(f"**任务指令：**\n{input_data.prompt}")
        
        # 前序节点输出（如果有）
        if input_data.previous_output:
            user_content_parts.append(f"**前序结果：**\n{input_data.previous_output}")
        
        # 如果没有具体内容，使用节点名称作为默认任务
        if not user_content_parts:
            user_content_parts.append(f"**处理任务：**\n{node.name}")
        
        # 添加处理指引
        user_content_parts.append("**请求：**\n请基于以上信息进行处理并提供结果。")
        
        user_content = "\n\n".join(user_content_parts)
        messages.append(HumanMessage(content=user_content))
        
        # 3. 创建ChatPromptTemplate
        template = ChatPromptTemplate.from_messages(messages)
        
        # 缓存模板
        self.prompt_templates[cache_key] = template
        
        return template
    
    def _initialize_from_config(self, config: TreeWorkflowConfig) -> None:
        """从配置初始化树形引擎"""
        # 解析节点和边
        self.nodes: Dict[str, TreeNode] = {
            node_id: TreeNode.from_dict(node_data) 
            for node_id, node_data in config['nodes'].items()
        }
        self.edges: List[TreeEdge] = [
            TreeEdge.from_dict(edge_data) 
            for edge_data in config['edges']
        ]
        
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
        start_nodes = [node_id for node_id, node in self.nodes.items() 
                      if node.node_type == NodeType.START]
        
        if not start_nodes:
            raise ValueError("未找到起始节点")
        
        print(f"🎯 起始节点: {[self.nodes[nid].name for nid in start_nodes]}")
        
        # 启动所有起始节点
        for start_node_id in start_nodes:
            result = await self.node_executor(start_node_id, NodeInputData())
            self._mark_node_completed(start_node_id, result)
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
            results=self.node_results
        )
        
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
                    except Exception as e:
                        print(f"❌ 节点 {self.nodes[node_id].name} 执行失败: {e}")
                        self._mark_node_failed(node_id, e)
            
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
                if not self.condition_checker(edge.condition, self.node_results[completed_node_id]):
                    node_name = self.nodes[target_node_id].name
                    print(f"🚫 条件不满足，跳过节点: {node_name}")
                    continue
                
            # 避免重复执行
            if target_node_id in self.running_tasks or target_node_id in self.completed_nodes:
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
        
        # 2. 收集所有直接前驱的输出 - 关键修正
        previous_output = None
        if input_config.include_previous_output:
            # ✅ 新逻辑：根据node_id收集所有前驱
            all_predecessors = self._get_all_completed_predecessors(node_id)
            if all_predecessors:
                previous_output = self._combine_predecessor_outputs(all_predecessors)
        
        return NodeInputData(prompt=prompt, previous_output=previous_output)

    def _get_all_completed_predecessors(self, node_id: str) -> List[str]:
        """获取指定节点的所有已完成的直接前驱节点
        
        Args:
            node_id: 目标节点ID
            
        Returns:
            已完成的前驱节点ID列表
        """
        predecessors = []
        
        # 遍历所有边，找到指向目标节点的边
        for edge in self.edges:
            if (edge.to_node == node_id and 
                edge.from_node in self.completed_nodes):
                predecessors.append(edge.from_node)
        
        # 去重保持顺序（避免重复边的情况）
        seen = set()
        unique_predecessors = []
        for pred_id in predecessors:
            if pred_id not in seen:
                seen.add(pred_id)
                unique_predecessors.append(pred_id)
        
        return unique_predecessors
    
    def _combine_predecessor_outputs(self, predecessor_ids: List[str]) -> str:
        """组合多个前驱节点的输出结果
        
        Args:
            predecessor_ids: 前驱节点ID列表
            
        Returns:
            组合后的输出字符串
        """
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
    
    def _default_condition_checker(self, condition: Optional[Condition], node_output: Any) -> bool:
        """默认条件检查器"""
        if condition is None:
            return True
        return condition.check(node_output)
    
    async def _default_node_executor(self, node_id: str, input_data: NodeInputData) -> Any:
        """优化版节点执行器 - 集成ChatPromptTemplate和最新LangChain语法"""
        node = self.nodes[node_id]
        
        # 起始节点直接返回
        if node.node_type == NodeType.START:
            return f"START_{self.workflow_id}"
        
        try:
            # 创建提示词模板
            prompt_template = self._create_prompt_template(node, input_data)
            
            print(f"🤖 调用LLM处理节点: {node.name}")
            print(f"   节点类型: {node.node_type.value}")
            
            # 格式化提示词模板
            formatted_prompt = prompt_template.invoke({})
            
            # 显示输入信息
            total_input_length = sum(len(msg.content) for msg in formatted_prompt.to_messages())
            print(f"   输入消息数: {len(formatted_prompt.to_messages())}")
            print(f"   总输入长度: {total_input_length} 字符")
            
            # 使用异步调用LLM - 2025年最新语法
            try:
                # 优先使用ainvoke进行异步调用
                response = await self.llm_model.ainvoke(formatted_prompt.to_messages())
                
                # 提取响应内容
                if hasattr(response, 'content'):
                    result = response.content
                else:
                    result = str(response)
                
                print(f"✅ LLM异步响应完成，输出长度: {len(result)} 字符")
                
                # 对特定节点类型添加额外处理
                if node.node_type == NodeType.LEAF:
                    result = f"[FINAL RESULT] {result}"
                
                return result
                
            except AttributeError:
                # 如果模型不支持ainvoke，回退到同步调用
                print("⚠️  模型不支持异步调用，回退到同步模式")
                response = await asyncio.to_thread(
                    self.llm_model.invoke, 
                    formatted_prompt.to_messages()
                )
                
                if hasattr(response, 'content'):
                    result = response.content
                else:
                    result = str(response)
                
                print(f"✅ LLM同步响应完成，输出长度: {len(result)} 字符")
                return result
            
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            
            # 降级到简单文本处理
            return await self._fallback_text_processing(node, input_data)
    
    async def _fallback_text_processing(self, node: TreeNode, input_data: NodeInputData) -> str:
        """LLM调用失败时的降级处理 - 增强版"""
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
        
    def get_prompt_template_info(self, node_id: str) -> Dict[str, Any]:
        """获取节点的提示词模板信息（调试用）
        
        Args:
            node_id: 节点ID
            
        Returns:
            模板信息字典
        """
        if node_id not in self.nodes:
            return {"error": "节点不存在"}
        
        node = self.nodes[node_id]
        dummy_input = NodeInputData(
            prompt=node.prompt,
            previous_output="[示例前序输出]"
        )
        
        template = self._create_prompt_template(node, dummy_input)
        formatted = template.invoke({})
        
        return {
            "node_name": node.name,
            "node_type": node.node_type.value,
            "template_messages": len(formatted.to_messages()),
            "messages": [
                {
                    "role": msg.__class__.__name__,
                    "content": str(msg.content)[:200] + "..." if len(str(msg.content)) > 200 else str(msg.content)
                }
                for msg in formatted.to_messages()
            ]
        }