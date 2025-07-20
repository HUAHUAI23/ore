"""
树形工作流引擎实现

基于原始简单版本重构，支持多start节点，在图构建阶段进行环路检查
"""

import asyncio
import os
from typing import Dict, List, Any, Set, Optional
from collections import defaultdict

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    from langchain_core.prompts import ChatPromptTemplate
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError as e:
    # Fallback if langchain or dotenv not installed
    ChatOpenAI = None
    HumanMessage = None
    ChatPromptTemplate = None
    load_dotenv = None
    print(f"⚠️ 导入警告: {e}")
    print("请安装依赖: pip install langchain-openai python-dotenv")

from ...base.engine import BaseWorkflowEngine
from ...workflow_types import NodeType, ExecutionSummary, NodeExecutor
from .types import (
    TreeNode, TreeEdge, TreeInputConfig, DatabaseSearchInput,
    TreeExecutionStats, TreeExecutionSummary, TreeExecutionStrategy,
    TreeCycleError
)

class TreeWorkflowEngine(BaseWorkflowEngine):
    """树形工作流执行引擎
    
    核心功能：
    1. 事件驱动的节点执行
    2. 自动依赖检查和并行执行  
    3. 灵活的输入内容组合
    4. 多分叉输出支持
    5. 支持多个start节点
    """
    
    def __init__(self, workflow_config: Dict[str, Any], node_executor: Optional[NodeExecutor] = None) -> None:
        """初始化树形工作流引擎"""
        super().__init__(workflow_config)
        if node_executor:
            self.set_node_executor(node_executor)
        
        # 初始化LLM客户端
        self._init_llm_client()
    
    def _initialize_from_config(self, config: Dict[str, Any]) -> None:
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
    
    def _init_llm_client(self) -> None:
        """初始化LLM客户端 - 2025年最新版本"""
        self.llm_client = None
        
        if ChatOpenAI is not None:
            # 检查环境变量中是否有API密钥
            api_key = os.getenv('OPENAI_API_KEY')
            api_base = os.getenv('OPENAI_API_BASE', 'https://aiproxy.usw.sealos.io/v1')
            model_name = os.getenv('OPENAI_MODEL', 'claude-3-5-haiku-20241022')
            
            # 清理URL，移除可能的注释
            api_base = api_base.split('#')[0].strip()
            
            if api_key:
                try:
                    self.llm_client = ChatOpenAI(
                        temperature=0.7,
                        model=model_name,  # 使用环境变量配置的模型
                        max_tokens=500,
                        api_key=api_key,
                        base_url=api_base,  # 使用清理后的端点
                        timeout=30.0  # 添加超时设置
                    )
                    print("✅ LangChain OpenAI客户端初始化成功 (2025版本)")
                    print(f"   模型: {model_name}")
                    print(f"   API端点: {api_base}")
                    print("   使用Sealos代理 - Claude模型")
                except Exception as e:
                    print(f"⚠️ LangChain OpenAI客户端初始化失败: {e}")
                    print("   将使用模拟LLM调用")
            else:
                print("⚠️ 未找到OPENAI_API_KEY环境变量")
                print("   请在.env文件中设置或运行: export OPENAI_API_KEY='your-key'")
                print("   将使用模拟LLM调用")
        else:
            print("⚠️ 未安装langchain-openai包")
            print("   请运行: pip install -r requirements.txt")
            print("   将使用模拟LLM调用")
    
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
    
    async def execute_workflow(self) -> TreeExecutionSummary:
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
            result = await self.node_executor(start_node_id, {})
            self._mark_node_completed(start_node_id, result)
            await self._try_trigger_next_nodes(start_node_id)
        
        # 事件驱动循环
        await self._run_execution_loop()
        
        print("✅ 工作流执行完成！")
        
        # 生成执行摘要
        base_summary = ExecutionSummary(
            workflow_id=self.workflow_id,
            workflow_name=self.workflow_name,
            completed_count=len(self.completed_nodes),
            total_count=len(self.nodes),
            results=self.node_results
        )
        
        return TreeExecutionSummary(
            base_summary=base_summary,
            stats=TreeExecutionStats(),
            execution_strategy=TreeExecutionStrategy.EVENT_DRIVEN
        )
    
    async def _run_execution_loop(self):
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
    
    async def _try_trigger_next_nodes(self, completed_node_id: str):
        """尝试触发后续节点"""
        outgoing_edges = self.outgoing_edges.get(completed_node_id, [])
        
        for edge in outgoing_edges:
            target_node_id = edge.to_node
            
            # 检查条件是否满足
            if not self.condition_checker(edge.condition, completed_node_id, self.node_results):
                continue
                
            # 检查是否所有前驱节点都已完成
            if not self._check_all_prerequisites_completed(target_node_id):
                print(f"⏳ 节点 {self.nodes[target_node_id].name} 等待前驱节点完成")
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
    
    def _prepare_node_input(self, node_id: str, edge: TreeEdge) -> Dict[str, Any]:
        """根据边配置准备节点输入"""
        node = self.nodes[node_id]
        input_config = edge.input_config
        input_data = {}
        
        # 1. 任务提示词
        if input_config.include_prompt:
            input_data['prompt'] = node.prompt
        
         # 2. 收集所有直接前驱的输出 - 关键修正
        if input_config.include_previous_output:
            # ✅ 新逻辑：根据node_id收集所有前驱
            all_predecessors = self._get_all_completed_predecessors(node_id)
            # TODO: 如果没获取到 all_predecessors 需要报错
            if all_predecessors:
                input_data['previous_output'] = self._combine_predecessor_outputs(all_predecessors)
        
        # 3. 数据库检索
        if input_config.include_database_search:
            if node.database_connection:
                search_input = self._prepare_database_search_input(
                    input_config.database_search_input,
                    input_data.get('prompt', ''),
                    input_data.get('previous_output', '')
                )
                input_data['database_search'] = {
                    'connection': node.database_connection,
                    'search_input': search_input
                }
        
        return input_data

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
    
    def _prepare_database_search_input(self, search_type: DatabaseSearchInput, 
                                     prompt: str, previous_output: str) -> str:
        """准备数据库检索的输入内容"""
        if search_type == DatabaseSearchInput.PROMPT:
            return prompt
        elif search_type == DatabaseSearchInput.PREVIOUS_OUTPUT:
            return str(previous_output)
        elif search_type == DatabaseSearchInput.PROMPT_AND_PREVIOUS:
            parts = []
            if prompt:
                parts.append(f"指令: {prompt}")
            if previous_output:
                parts.append(f"上下文: {previous_output}")
            return " | ".join(parts)
        else:
            return prompt
    
    async def _default_node_executor(self, node_id: str, input_data: Dict[str, Any]) -> Any:
        """默认节点执行器"""
        node = self.nodes[node_id]
        
        # 起始节点直接返回
        if node.node_type == NodeType.START:
            return f"START_{self.workflow_id}"
        
        # 组装处理输入
        input_parts = []
        
        if 'prompt' in input_data:
            input_parts.append(f"PROMPT: {input_data['prompt']}")
        
        if 'previous_output' in input_data:
            input_parts.append(f"PREV: {input_data['previous_output']}")
        
        if 'database_search' in input_data:
            db_result = await self.database_searcher(
                input_data['database_search']['connection'],
                input_data['database_search']['search_input']
            )
            input_parts.append(f"DB: {db_result}")
        
        # 调用处理函数
        full_input = " | ".join(input_parts)
        return await self._mock_llm_call(node_id, full_input)
    
    async def _mock_llm_call(self, node_id: str, input_text: str) -> str:
        """智能LLM调用 - 支持真实OpenAI调用和模拟调用"""
        node_name = self.nodes[node_id].name
        print(f"   🤖 处理中: {node_name}")
        
        # 如果有真实的LLM客户端，使用真实调用
        if self.llm_client and HumanMessage:
            try:
                # 构建优化的提示词模板 (2025年最佳实践)
                system_prompt = f"""你是一个智能工作流节点处理器。

任务环境:
- 工作流名称: {self.workflow_name}
- 节点名称: {node_name}
- 节点ID: {node_id}
- 节点描述: {self.nodes[node_id].description}

请根据输入数据进行处理，生成简洁、准确且有价值的输出结果。"""

                user_prompt = f"输入数据: {input_text}"
                
                # 使用最新的ChatPromptTemplate (如果可用)
                if ChatPromptTemplate:
                    prompt_template = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("user", user_prompt)
                    ])
                    messages = prompt_template.format_messages()
                    response = self.llm_client.invoke(messages)
                else:
                    # 备用方法：直接使用HumanMessage
                    full_prompt = f"{system_prompt}\n\n{user_prompt}"
                    response = self.llm_client.invoke([HumanMessage(content=full_prompt)])
                
                result = response.content.strip()
                
                # 记录调用统计
                token_count = len(result.split())
                print(f"   ✅ OpenAI调用成功 (~{token_count} tokens)")
                print(f"   📄 结果预览: {result[:80]}..." if len(result) > 80 else f"   📄 完整结果: {result}")
                
                return result
                
            except Exception as e:
                print(f"   ❌ OpenAI调用失败: {e}")
                print(f"   🔄 自动降级到模拟调用")
                # 降级到模拟调用
                pass
        
        # 模拟LLM调用
        await asyncio.sleep(0.5)
        
        # 生成更智能的模拟响应
        node = self.nodes[node_id]
        if node.node_type == NodeType.START:
            return f"已启动工作流: {self.workflow_name}"
        elif node.node_type == NodeType.LEAF:
            return f"最终结果来自{node_name}: 基于输入'{input_text[:30]}...' 的处理结果"
        else:
            return f"{node_name}处理结果: 基于'{input_text[:30]}...' 生成的中间输出"
    
    async def _default_database_searcher(self, connection: str, search_input: str) -> str:
        """默认数据库检索器"""
        print(f"   🔍 DB查询: {connection}")
        await asyncio.sleep(0.2)
        return f"DB_RESULT_{connection}"
    
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