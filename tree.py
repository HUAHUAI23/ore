import json
import asyncio
from typing import Dict, List, Any, Set
from collections import defaultdict

class TreeWorkflowEngine:
    """通用树形工作流执行引擎
    
    核心功能：
    1. 事件驱动的节点执行
    2. 自动依赖检查和并行执行  
    3. 灵活的输入内容组合
    4. 多分叉输出支持
    """
    
    def __init__(self, workflow_config: Dict):
        self.workflow_id = workflow_config.get('workflow_id', 'unknown')
        self.workflow_name = workflow_config.get('name', 'Unknown Workflow')
        self.nodes = workflow_config['nodes']
        self.branches = workflow_config['branches']
        
        # 构建图：from_node -> [branches]
        self.outgoing_branches = self._build_outgoing_graph()
        
        # 执行状态
        self.node_results = {}        # 每个节点的执行结果  
        self.completed_nodes = set()  # 已完成的节点集合
        self.running_tasks = {}       # 正在运行的异步任务
        
    def _build_outgoing_graph(self) -> Dict[str, List[Dict]]:
        """构建从每个节点出发的分支列表（邻接表）"""
        graph = defaultdict(list)
        for branch in self.branches:
            graph[branch['from']].append(branch)
        return dict(graph)
    
    async def execute_workflow(self):
        """执行完整工作流"""
        # 1. 找到并执行起始节点
        start_nodes = [node_id for node_id, node in self.nodes.items() 
                      if node['node_type'] == 'start']
        if not start_nodes:
            raise ValueError("未找到起始节点")
        for start_node_id in start_nodes:
            await self._execute_node(start_node_id, {})
            self._mark_node_completed(start_node_id, f"工作流{self.workflow_id}已启动")
            await self._try_trigger_next_nodes(start_node_id)
        
        # 2. 事件驱动循环：等待任务完成并触发后续节点
        while self.running_tasks:
            completed_task_ids = []
            for node_id, task in self.running_tasks.items():
                if task.done():
                    completed_task_ids.append(node_id)
                    
                    try:
                        result = await task
                        self._mark_node_completed(node_id, result)
                    except Exception as e:
                        print(f"❌ 节点 {self.nodes[node_id]['name']} 执行失败: {e}")
            
            # 清理已完成的任务并触发后续节点
            for node_id in completed_task_ids:
                del self.running_tasks[node_id]
                await self._try_trigger_next_nodes(node_id)
            
            # 短暂休眠避免忙等待
            if self.running_tasks:
                await asyncio.sleep(0.1)
        
        return 
    
    
    def _mark_node_completed(self, node_id: str, result: Any):
        """标记节点完成并保存结果"""
        self.completed_nodes.add(node_id)
        self.node_results[node_id] = result
    
    async def _try_trigger_next_nodes(self, completed_node_id: str):
        """尝试触发后续节点"""
        outgoing_branches = self.outgoing_branches.get(completed_node_id, [])
        
        for branch in outgoing_branches:
            target_node_id = branch['to']
            
            # 检查条件是否满足
            if not self._check_condition(branch['condition'], completed_node_id):
                continue
                
            # 检查是否所有前驱节点都已完成
            if not self._check_all_prerequisites_completed(target_node_id):
                continue
                
            # 避免重复执行
            if target_node_id in self.running_tasks or target_node_id in self.completed_nodes:
                continue
            
            # 准备输入数据并启动任务
            input_data = self._prepare_node_input(target_node_id, branch)
            task = asyncio.create_task(self._execute_node(target_node_id, input_data))
            self.running_tasks[target_node_id] = task
            
    
    def _check_all_prerequisites_completed(self, node_id: str) -> bool:
        """检查节点的所有前驱是否都已完成"""
        prerequisites = set()
        
        # 收集所有指向该节点的前驱
        for branch in self.branches:
            if branch['to'] == node_id:
                prerequisites.add(branch['from'])
        
        # 检查是否所有前驱都已完成
        # 使用集合运算符检查,集合差运算，prerequisites - self.completed_nodes 表示 prerequisites 中不在 self.completed_nodes 中的元素
        missing_prereqs = prerequisites - self.completed_nodes
        if missing_prereqs:
            return False
        
        return True
    
    def _prepare_node_input(self, node_id: str, branch: Dict) -> Dict[str, Any]:
        """根据分支配置准备节点输入"""
        node = self.nodes[node_id]
        input_config = branch['input_config']
        input_data = {}
        
        # 1. 任务提示词
        if input_config['include_prompt']:
            input_data['prompt'] = node['prompt']
        
        # 2. 上一个节点的输出
        if input_config['include_previous_output']:
            from_node_id = branch['from']
            if from_node_id in self.node_results:
                input_data['previous_output'] = self.node_results[from_node_id]
        
        # 3. 数据库检索
        if input_config['include_database_search']:
            if 'database_connection' in node:
                search_input = self._prepare_database_search_input(
                    input_config['database_search_input'],
                    input_data.get('prompt', ''),
                    input_data.get('previous_output', '')
                )
                input_data['database_search'] = {
                    'connection': node['database_connection'],
                    'search_input': search_input
                }
        
        return input_data
    
    def _prepare_database_search_input(self, search_type: str, prompt: str, previous_output: str) -> str:
        """准备数据库检索的输入内容"""
        if search_type == 'prompt':
            return prompt
        elif search_type == 'previous_output':
            return str(previous_output)
        elif search_type == 'prompt_and_previous':
            parts = []
            if prompt:
                parts.append(f"指令: {prompt}")
            if previous_output:
                parts.append(f"上下文: {previous_output}")
            return " | ".join(parts)
        else:
            return prompt
    
    async def _execute_node(self, node_id: str, input_data: Dict[str, Any]) -> Any:
        """执行单个节点"""
        node = self.nodes[node_id]
        
        # 起始节点直接返回
        if node['node_type'] == 'start':
            return f"START_{self.workflow_id}"
        
        # 组装处理输入
        input_parts = []
        
        if 'prompt' in input_data:
            input_parts.append(f"PROMPT: {input_data['prompt']}")
        
        if 'previous_output' in input_data:
            input_parts.append(f"PREV: {input_data['previous_output']}")
        
        if 'database_search' in input_data:
            db_result = await self._mock_database_search(
                input_data['database_search']['connection'],
                input_data['database_search']['search_input']
            )
            input_parts.append(f"DB: {db_result}")
        
        # 调用处理函数
        full_input = " | ".join(input_parts)
        return await self._mock_llm_call(node_id, full_input)
    
    async def _mock_database_search(self, connection: str, search_input: str) -> str:
        """模拟数据库检索"""
        print(f"   🔍 DB查询: {connection}")
        # 模拟检索延迟
        await asyncio.sleep(0.2)
        return f"DB_RESULT_{connection}"
    
    async def _mock_llm_call(self, node_id: str, input_text: str) -> str:
        """模拟LLM调用"""
        node_name = self.nodes[node_id]['name']
        print(f"   🤖 处理中: {node_name}")
        
        # 模拟处理延迟
        await asyncio.sleep(0.5)
        
        return f"OUTPUT_{node_id.upper()}"
    
    def _check_condition(self, condition: str, completed_node_id: str) -> bool:
        """检查分支条件"""
        if condition == "true":
            return True
        
        try:
            context = {
                'completed_node': completed_node_id,
                'results': self.node_results
            }
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    

# 测试配置
TEST_WORKFLOW_CONFIG = {
    "workflow_id": "tree_test_001",
    "name": "树形工作流测试",
    "nodes": {
        "start": {"id": "start", "name": "开始", "description": "起始点", "prompt": "", "node_type": "start"},
        "node_a": {"id": "node_a", "name": "节点A", "description": "第一层处理", "prompt": "执行任务A", "node_type": "process", "database_connection": "db_a"},
        "node_b": {"id": "node_b", "name": "节点B", "description": "第二层处理B", "prompt": "执行任务B", "node_type": "process", "database_connection": "db_b"},
        "node_c": {"id": "node_c", "name": "节点C", "description": "第二层处理C", "prompt": "执行任务C", "node_type": "process", "database_connection": "db_c"},
        "node_d": {"id": "node_d", "name": "节点D", "description": "汇聚节点", "prompt": "整合B和C的结果", "node_type": "process", "database_connection": "db_d"},
        "leaf_1": {"id": "leaf_1", "name": "输出1", "description": "第一个输出", "prompt": "生成结果1", "node_type": "leaf"},
        "leaf_2": {"id": "leaf_2", "name": "输出2", "description": "第二个输出", "prompt": "生成结果2", "node_type": "leaf", "database_connection": "db_leaf"},
        "leaf_3": {"id": "leaf_3", "name": "输出3", "description": "第三个输出", "prompt": "生成结果3", "node_type": "leaf"},
        "leaf_4": {"id": "leaf_4", "name": "输出4", "description": "扩展输出4", "prompt": "基于输出1的扩展", "node_type": "leaf", "database_connection": "db_ext"},
        "leaf_5": {"id": "leaf_5", "name": "输出5", "description": "扩展输出5", "prompt": "基于输出1的另一扩展", "node_type": "leaf"}
    },
    "branches": [
        {"from": "start", "to": "node_a", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": False, "include_database_search": True, "database_search_input": "prompt"}},
        {"from": "node_a", "to": "node_b", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "prompt_and_previous"}},
        {"from": "node_a", "to": "node_c", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "prompt_and_previous"}},
        {"from": "node_b", "to": "node_d", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "prompt_and_previous"}},
        {"from": "node_c", "to": "node_d", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "prompt_and_previous"}},
        {"from": "node_d", "to": "leaf_1", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from": "node_d", "to": "leaf_2", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "prompt_and_previous"}},
        {"from": "node_d", "to": "leaf_3", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from": "leaf_1", "to": "leaf_4", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "previous_output"}},
        {"from": "leaf_1", "to": "leaf_5", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}}
    ]
}

async def main():
    """运行工作流测试"""
    engine = TreeWorkflowEngine(TEST_WORKFLOW_CONFIG)
    await engine.execute_workflow()

if __name__ == "__main__":
    asyncio.run(main())