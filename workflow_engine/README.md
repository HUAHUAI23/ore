# 工作流引擎模块

## 概述

工作流引擎模块是ORE项目的核心组件，提供灵活的AI工作流编排和执行能力。支持多种工作流类型，包括树形工作流、DAG工作流和图形工作流，为复杂的AI任务提供强大的调度和管理功能。

## 模块结构

```text
workflow_engine/
├── README.md               # 模块文档
├── __init__.py
├── workflow_types.py       # 工作流类型定义
├── base/                   # 基础抽象类
│   ├── __init__.py
│   └── engine.py           # 工作流引擎基类
├── engines/                # 具体引擎实现
│   ├── __init__.py
│   ├── tree/               # 树形工作流引擎
│   │   ├── __init__.py
│   │   ├── engine.py       # 树形引擎实现
│   │   └── types.py        # 树形工作流类型
│   ├── dag/                # DAG工作流引擎（计划中）
│   └── graph/              # 图形工作流引擎（计划中）
└── examples/               # 示例代码
    └── tree_workflow.py    # 树形工作流示例
```

## 核心特性

### 1. 多引擎支持

- **树形工作流**: 支持层次化的工作流结构，适合步骤明确的任务流程
- **DAG工作流**: 支持有向无环图结构，适合复杂的并行执行场景
- **图形工作流**: 支持更复杂的图结构，包含环路检测和处理

### 2. 智能调度

- **自动依赖检查**: 自动分析节点间的依赖关系
- **并行执行**: 支持无依赖节点的并行执行
- **条件分支**: 基于执行结果的条件跳转
- **错误处理**: 完善的错误恢复和重试机制

### 3. AI集成

- **LangChain集成**: 深度集成LangChain框架
- **多模型支持**: 支持OpenAI、Anthropic等主流AI服务
- **提示词管理**: 灵活的提示词模板和变量替换
- **异步调用**: 高性能的异步AI模型调用

### 4. 可扩展性

- **插件架构**: 易于扩展的插件系统
- **自定义节点**: 支持自定义节点类型和处理逻辑
- **配置驱动**: 基于配置文件的工作流定义
- **热更新**: 支持运行时配置更新

## 工作流引擎基类 (base/engine.py)

### 抽象接口

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from workflow_engine.workflow_types import WorkflowResult, NodeType

class BaseWorkflowEngine(ABC):
    """工作流引擎基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.workflow_id = config.get("workflow_id")
        self.workflow_name = config.get("workflow_name", "Unnamed Workflow")
        self._initialize_from_config(config)
    
    @abstractmethod
    def _initialize_from_config(self, config: Dict[str, Any]) -> None:
        """从配置初始化引擎"""
        pass
    
    @abstractmethod
    async def execute_workflow(self) -> WorkflowResult:
        """执行工作流"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置有效性"""
        pass
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "status": "initialized"
        }
```

### 生命周期管理

```python
class WorkflowLifecycle:
    """工作流生命周期管理"""
    
    def __init__(self, engine: BaseWorkflowEngine):
        self.engine = engine
        self.status = "created"
        self.start_time = None
        self.end_time = None
    
    async def start(self):
        """启动工作流"""
        self.status = "running"
        self.start_time = datetime.now()
        logger.info(f"工作流 {self.engine.workflow_id} 开始执行")
    
    async def complete(self, result: WorkflowResult):
        """完成工作流"""
        self.status = "completed"
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        logger.info(f"工作流 {self.engine.workflow_id} 执行完成，耗时: {duration}")
    
    async def fail(self, error: Exception):
        """工作流失败"""
        self.status = "failed"
        self.end_time = datetime.now()
        logger.error(f"工作流 {self.engine.workflow_id} 执行失败: {str(error)}")
```

## 树形工作流引擎 (engines/tree/engine.py)

### 引擎实现

```python
from workflow_engine.base.engine import BaseWorkflowEngine
from workflow_engine.engines.tree.types import TreeNode, TreeWorkflowConfig
from langchain.llms import OpenAI
from typing import Dict, List, Any

class TreeWorkflowEngine(BaseWorkflowEngine):
    """树形工作流引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.nodes: Dict[str, TreeNode] = {}
        self.edges: List[Dict[str, Any]] = []
        self.execution_order: List[str] = []
        self.llm = None
    
    def _initialize_from_config(self, config: Dict[str, Any]) -> None:
        """从配置初始化树形引擎"""
        # 初始化节点
        for node_id, node_config in config.get("nodes", {}).items():
            self.nodes[node_id] = TreeNode(
                node_id=node_id,
                name=node_config.get("name"),
                node_type=NodeType(node_config.get("node_type")),
                prompt=node_config.get("prompt"),
                description=node_config.get("description")
            )
        
        # 初始化边
        self.edges = config.get("edges", [])
        
        # 初始化LLM
        self._initialize_llm(config.get("llm_config", {}))
        
        # 计算执行顺序
        self._calculate_execution_order()
    
    def _initialize_llm(self, llm_config: Dict[str, Any]) -> None:
        """初始化LLM"""
        llm_provider = llm_config.get("provider", "openai")
        
        if llm_provider == "openai":
            self.llm = OpenAI(
                model_name=llm_config.get("model", "gpt-3.5-turbo"),
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 2000)
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {llm_provider}")
    
    def _calculate_execution_order(self) -> None:
        """计算节点执行顺序（拓扑排序）"""
        # 构建依赖图
        dependencies = {node_id: [] for node_id in self.nodes.keys()}
        for edge in self.edges:
            from_node = edge["from_node"]
            to_node = edge["to_node"]
            dependencies[to_node].append(from_node)
        
        # 拓扑排序
        visited = set()
        temp_visited = set()
        self.execution_order = []
        
        def dfs(node_id: str):
            if node_id in temp_visited:
                raise ValueError(f"检测到环路，包含节点: {node_id}")
            if node_id in visited:
                return
            
            temp_visited.add(node_id)
            for dep in dependencies[node_id]:
                dfs(dep)
            temp_visited.remove(node_id)
            visited.add(node_id)
            self.execution_order.append(node_id)
        
        for node_id in self.nodes.keys():
            if node_id not in visited:
                dfs(node_id)
    
    async def execute_workflow(self) -> WorkflowResult:
        """执行树形工作流"""
        results = {}
        execution_log = []
        
        try:
            for node_id in self.execution_order:
                node = self.nodes[node_id]
                logger.info(f"执行节点: {node_id} - {node.name}")
                
                # 准备输入
                node_input = await self._prepare_node_input(node_id, results)
                
                # 执行节点
                if node.node_type == NodeType.START:
                    result = await self._execute_start_node(node, node_input)
                elif node.node_type == NodeType.PROCESS:
                    result = await self._execute_process_node(node, node_input)
                elif node.node_type == NodeType.LEAF:
                    result = await self._execute_leaf_node(node, node_input)
                else:
                    raise ValueError(f"不支持的节点类型: {node.node_type}")
                
                results[node_id] = result
                execution_log.append({
                    "node_id": node_id,
                    "node_name": node.name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"节点 {node_id} 执行完成")
            
            return WorkflowResult(
                workflow_id=self.workflow_id,
                workflow_name=self.workflow_name,
                status="completed",
                results=results,
                execution_log=execution_log,
                start_time=datetime.now(),
                end_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            return WorkflowResult(
                workflow_id=self.workflow_id,
                workflow_name=self.workflow_name,
                status="failed",
                results=results,
                execution_log=execution_log,
                error=str(e),
                start_time=datetime.now(),
                end_time=datetime.now()
            )
    
    async def _prepare_node_input(self, node_id: str, results: Dict[str, Any]) -> str:
        """准备节点输入"""
        node = self.nodes[node_id]
        input_parts = []
        
        # 添加节点提示词
        if node.prompt:
            input_parts.append(node.prompt)
        
        # 添加前置节点输出
        for edge in self.edges:
            if edge["to_node"] == node_id:
                from_node = edge["from_node"]
                input_config = edge.get("input_config", {})
                
                if input_config.get("include_previous_output", True) and from_node in results:
                    input_parts.append(f"前置节点输出: {results[from_node]}")
        
        return "\n\n".join(input_parts)
    
    async def _execute_start_node(self, node: TreeNode, node_input: str) -> str:
        """执行起始节点"""
        return f"工作流 '{self.workflow_name}' 开始执行"
    
    async def _execute_process_node(self, node: TreeNode, node_input: str) -> str:
        """执行处理节点"""
        if not self.llm:
            raise ValueError("LLM未初始化")
        
        response = await self.llm.agenerate([node_input])
        return response.generations[0][0].text.strip()
    
    async def _execute_leaf_node(self, node: TreeNode, node_input: str) -> str:
        """执行叶子节点"""
        if not self.llm:
            return f"节点 '{node.name}' 处理完成"
        
        response = await self.llm.agenerate([node_input])
        return response.generations[0][0].text.strip()
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        # 检查必需字段
        if not self.workflow_id or not self.workflow_name:
            return False
        
        # 检查节点
        if not self.nodes:
            return False
        
        # 检查是否有起始节点
        start_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.START]
        if not start_nodes:
            return False
        
        # 检查边的有效性
        for edge in self.edges:
            from_node = edge.get("from_node")
            to_node = edge.get("to_node")
            if from_node not in self.nodes or to_node not in self.nodes:
                return False
        
        return True
```

### 节点类型定义

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class NodeType(Enum):
    """节点类型枚举"""
    START = "START"          # 起始节点
    PROCESS = "PROCESS"      # 处理节点
    LEAF = "LEAF"           # 叶子节点
    CONDITION = "CONDITION"  # 条件节点
    PARALLEL = "PARALLEL"    # 并行节点

@dataclass
class TreeNode:
    """树形工作流节点"""
    node_id: str
    name: str
    node_type: NodeType
    prompt: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}

@dataclass
class TreeWorkflowConfig:
    """树形工作流配置"""
    workflow_id: str
    workflow_name: str
    description: str
    version: str
    nodes: Dict[str, Dict[str, Any]]
    edges: List[Dict[str, Any]]
    llm_config: Optional[Dict[str, Any]] = None
```

## 工作流类型定义 (workflow_types.py)

### 通用类型

```python
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class WorkflowStatus(Enum):
    """工作流状态"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    workflow_name: str
    status: str
    results: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    start_time: datetime
    end_time: datetime
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NodeExecutionResult:
    """节点执行结果"""
    node_id: str
    node_name: str
    status: str
    output: Any
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ExecutionContext:
    """执行上下文"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.variables: Dict[str, Any] = {}
        self.node_results: Dict[str, NodeExecutionResult] = {}
        self.execution_stack: List[str] = []
    
    def set_variable(self, key: str, value: Any) -> None:
        """设置变量"""
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """获取变量"""
        return self.variables.get(key, default)
    
    def add_node_result(self, result: NodeExecutionResult) -> None:
        """添加节点执行结果"""
        self.node_results[result.node_id] = result
    
    def get_node_result(self, node_id: str) -> Optional[NodeExecutionResult]:
        """获取节点执行结果"""
        return self.node_results.get(node_id)
```

## 使用示例

### 基本树形工作流

```python
from workflow_engine.engines.tree import TreeWorkflowEngine
import asyncio

# 工作流配置
config = {
    "workflow_id": "ai-content-generation",
    "workflow_name": "AI内容生成工作流",
    "description": "使用AI生成和优化内容",
    "version": "1.0.0",
    "nodes": {
        "start": {
            "name": "开始",
            "node_type": "START",
            "description": "工作流起点"
        },
        "generate_outline": {
            "name": "生成大纲",
            "node_type": "PROCESS",
            "prompt": "请为以下主题生成一个详细的内容大纲：AI技术在教育领域的应用",
            "description": "生成内容大纲"
        },
        "write_content": {
            "name": "编写内容",
            "node_type": "PROCESS",
            "prompt": "根据以下大纲，编写一篇详细的文章",
            "description": "基于大纲编写内容"
        },
        "review_content": {
            "name": "内容审核",
            "node_type": "LEAF",
            "prompt": "请审核以下内容的质量，并提供改进建议",
            "description": "审核和优化内容"
        }
    },
    "edges": [
        {
            "from_node": "start",
            "to_node": "generate_outline",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": False
            }
        },
        {
            "from_node": "generate_outline",
            "to_node": "write_content",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True
            }
        },
        {
            "from_node": "write_content",
            "to_node": "review_content",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True
            }
        }
    ],
    "llm_config": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2000
    }
}

# 执行工作流
async def main():
    engine = TreeWorkflowEngine(config)
    
    # 验证配置
    if not engine.validate_config():
        print("配置验证失败")
        return
    
    # 执行工作流
    result = await engine.execute_workflow()
    
    print(f"工作流执行状态: {result.status}")
    print(f"执行结果: {result.results}")
    
    if result.error:
        print(f"错误信息: {result.error}")

# 运行示例
if __name__ == "__main__":
    asyncio.run(main())
```

### 条件分支工作流

```python
# 带条件分支的工作流配置
conditional_config = {
    "workflow_id": "conditional-workflow",
    "workflow_name": "条件分支工作流",
    "description": "根据条件执行不同分支",
    "version": "1.0.0",
    "nodes": {
        "start": {
            "name": "开始",
            "node_type": "START"
        },
        "analyze_input": {
            "name": "分析输入",
            "node_type": "PROCESS",
            "prompt": "分析以下输入内容的类型和特征，判断是技术文档还是营销文案"
        },
        "tech_processing": {
            "name": "技术处理",
            "node_type": "PROCESS",
            "prompt": "这是技术文档，请进行技术性优化和完善"
        },
        "marketing_processing": {
            "name": "营销处理",
            "node_type": "PROCESS",
            "prompt": "这是营销文案，请进行营销性优化和完善"
        },
        "final_review": {
            "name": "最终审核",
            "node_type": "LEAF",
            "prompt": "对处理后的内容进行最终审核和总结"
        }
    },
    "edges": [
        {"from_node": "start", "to_node": "analyze_input"},
        {"from_node": "analyze_input", "to_node": "tech_processing", "condition": "is_technical"},
        {"from_node": "analyze_input", "to_node": "marketing_processing", "condition": "is_marketing"},
        {"from_node": "tech_processing", "to_node": "final_review"},
        {"from_node": "marketing_processing", "to_node": "final_review"}
    ]
}
```

## 开发指南

### 添加新的引擎类型

1. **创建引擎目录**

```bash
mkdir workflow_engine/engines/your_engine
```

2. **实现引擎类**

```python
# workflow_engine/engines/your_engine/engine.py
from workflow_engine.base.engine import BaseWorkflowEngine

class YourWorkflowEngine(BaseWorkflowEngine):
    def _initialize_from_config(self, config):
        # 实现配置初始化
        pass
        
    async def execute_workflow(self):
        # 实现工作流执行逻辑
        pass
        
    def validate_config(self):
        # 实现配置验证
        pass
```

3. **注册引擎**

```python
# workflow_engine/engines/__init__.py
from .tree.engine import TreeWorkflowEngine
from .your_engine.engine import YourWorkflowEngine

ENGINES = {
    "tree": TreeWorkflowEngine,
    "your_engine": YourWorkflowEngine,
}
```

### 自定义节点类型

```python
from workflow_engine.engines.tree.types import TreeNode
from workflow_engine.workflow_types import NodeExecutionResult

class CustomNode(TreeNode):
    """自定义节点类型"""
    
    def __init__(self, *args, custom_param: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_param = custom_param
    
    async def execute(self, context: ExecutionContext) -> NodeExecutionResult:
        """自定义执行逻辑"""
        # 实现自定义处理逻辑
        result = f"自定义处理结果: {self.custom_param}"
        
        return NodeExecutionResult(
            node_id=self.node_id,
            node_name=self.name,
            status="completed",
            output=result,
            execution_time=0.1
        )
```

### 扩展输入处理

```python
class EnhancedInputProcessor:
    """增强的输入处理器"""
    
    def __init__(self, template_engine=None):
        self.template_engine = template_engine
    
    def process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """处理模板变量"""
        if self.template_engine:
            return self.template_engine.render(template, **variables)
        
        # 简单变量替换
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def merge_inputs(self, inputs: List[str], separator: str = "\n\n") -> str:
        """合并多个输入"""
        return separator.join(filter(None, inputs))
```

## 配置管理

### 配置文件结构

```yaml
# workflow_config.yaml
workflow:
  id: "example-workflow"
  name: "示例工作流"
  description: "这是一个示例工作流"
  version: "1.0.0"
  
nodes:
  start:
    name: "开始"
    type: "START"
    description: "工作流起点"
  
  process1:
    name: "处理步骤1"
    type: "PROCESS"
    prompt: "执行第一个处理步骤"
    config:
      timeout: 30
      retries: 3

edges:
  - from: "start"
    to: "process1"
    config:
      include_prompt: true
      include_previous_output: false

llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 2000
```

### 配置验证器

```python
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional

class NodeConfig(BaseModel):
    """节点配置模型"""
    name: str
    type: str
    prompt: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    @validator('type')
    def validate_node_type(cls, v):
        allowed_types = ["START", "PROCESS", "LEAF", "CONDITION"]
        if v not in allowed_types:
            raise ValueError(f"节点类型必须是 {allowed_types} 之一")
        return v

class EdgeConfig(BaseModel):
    """边配置模型"""
    from_node: str = Field(alias='from')
    to_node: str = Field(alias='to')
    condition: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class WorkflowConfig(BaseModel):
    """工作流配置模型"""
    workflow_id: str = Field(alias='workflow.id')
    workflow_name: str = Field(alias='workflow.name')
    description: str = Field(alias='workflow.description')
    version: str = Field(alias='workflow.version')
    nodes: Dict[str, NodeConfig]
    edges: List[EdgeConfig]
    llm_config: Optional[Dict[str, Any]] = Field(alias='llm')
    
    @validator('nodes')
    def validate_nodes(cls, v):
        if not v:
            raise ValueError("至少需要定义一个节点")
        
        # 检查是否有起始节点
        start_nodes = [node for node in v.values() if node.type == "START"]
        if not start_nodes:
            raise ValueError("必须定义至少一个START类型的节点")
        
        return v
```

## 性能优化

### 并行执行

```python
import asyncio
from typing import Set

class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_concurrency: int = 5):
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
    
    async def execute_parallel_nodes(self, nodes: List[TreeNode], context: ExecutionContext) -> Dict[str, Any]:
        """并行执行无依赖的节点"""
        async def execute_single_node(node: TreeNode) -> tuple[str, Any]:
            async with self.semaphore:
                result = await self._execute_node(node, context)
                return node.node_id, result
        
        # 创建并发任务
        tasks = [execute_single_node(node) for node in nodes]
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        node_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"节点执行失败: {result}")
                continue
            
            node_id, output = result
            node_results[node_id] = output
        
        return node_results
```

### 缓存机制

```python
from functools import wraps
import hashlib
import json

class WorkflowCache:
    """工作流缓存"""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    def _generate_cache_key(self, node_id: str, input_data: str) -> str:
        """生成缓存键"""
        content = f"{node_id}:{input_data}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, node_id: str, input_data: str) -> Optional[Any]:
        """获取缓存结果"""
        key = self._generate_cache_key(node_id, input_data)
        return self.cache.get(key)
    
    def set(self, node_id: str, input_data: str, result: Any) -> None:
        """设置缓存结果"""
        key = self._generate_cache_key(node_id, input_data)
        self.cache[key] = result
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()

def cached_execution(cache: WorkflowCache):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, node: TreeNode, input_data: str, *args, **kwargs):
            # 尝试从缓存获取
            cached_result = cache.get(node.node_id, input_data)
            if cached_result is not None:
                logger.info(f"使用缓存结果: {node.node_id}")
                return cached_result
            
            # 执行函数
            result = await func(self, node, input_data, *args, **kwargs)
            
            # 缓存结果
            cache.set(node.node_id, input_data, result)
            
            return result
        return wrapper
    return decorator
```

## 监控和调试

### 执行监控

```python
from dataclasses import dataclass
from typing import List
import time

@dataclass
class ExecutionMetrics:
    """执行指标"""
    node_id: str
    node_name: str
    start_time: float
    end_time: float
    execution_time: float
    memory_usage: float
    success: bool
    error_message: Optional[str] = None

class WorkflowMonitor:
    """工作流监控器"""
    
    def __init__(self):
        self.metrics: List[ExecutionMetrics] = []
        self.current_execution: Dict[str, float] = {}
    
    def start_node_execution(self, node_id: str) -> None:
        """开始节点执行监控"""
        self.current_execution[node_id] = time.time()
    
    def end_node_execution(self, node_id: str, node_name: str, success: bool, error: str = None) -> None:
        """结束节点执行监控"""
        if node_id not in self.current_execution:
            return
        
        start_time = self.current_execution.pop(node_id)
        end_time = time.time()
        
        metrics = ExecutionMetrics(
            node_id=node_id,
            node_name=node_name,
            start_time=start_time,
            end_time=end_time,
            execution_time=end_time - start_time,
            memory_usage=self._get_memory_usage(),
            success=success,
            error_message=error
        )
        
        self.metrics.append(metrics)
    
    def _get_memory_usage(self) -> float:
        """获取内存使用情况"""
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        if not self.metrics:
            return {}
        
        total_time = sum(m.execution_time for m in self.metrics)
        success_count = sum(1 for m in self.metrics if m.success)
        
        return {
            "total_nodes": len(self.metrics),
            "successful_nodes": success_count,
            "failed_nodes": len(self.metrics) - success_count,
            "total_execution_time": total_time,
            "average_execution_time": total_time / len(self.metrics),
            "max_memory_usage": max(m.memory_usage for m in self.metrics),
            "metrics": [asdict(m) for m in self.metrics]
        }
```

### 调试工具

```python
class WorkflowDebugger:
    """工作流调试器"""
    
    def __init__(self, enable_debug: bool = False):
        self.enable_debug = enable_debug
        self.execution_trace: List[Dict[str, Any]] = []
    
    def trace_node_execution(self, node: TreeNode, input_data: str, output: str) -> None:
        """跟踪节点执行"""
        if not self.enable_debug:
            return
        
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "node_id": node.node_id,
            "node_name": node.name,
            "node_type": node.node_type.value,
            "input_length": len(input_data),
            "output_length": len(output),
            "input_preview": input_data[:200] + "..." if len(input_data) > 200 else input_data,
            "output_preview": output[:200] + "..." if len(output) > 200 else output
        }
        
        self.execution_trace.append(trace_entry)
    
    def export_trace(self, filename: str) -> None:
        """导出执行跟踪"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.execution_trace, f, ensure_ascii=False, indent=2)
    
    def print_trace_summary(self) -> None:
        """打印跟踪摘要"""
        if not self.execution_trace:
            print("没有执行跟踪数据")
            return
        
        print("=== 工作流执行跟踪摘要 ===")
        for trace in self.execution_trace:
            print(f"节点: {trace['node_name']} ({trace['node_id']})")
            print(f"  类型: {trace['node_type']}")
            print(f"  输入长度: {trace['input_length']}")
            print(f"  输出长度: {trace['output_length']}")
            print(f"  时间: {trace['timestamp']}")
            print("---")
```

## 最佳实践

### 1. 工作流设计

- **单一职责**: 每个节点应该有明确的单一职责
- **松耦合**: 节点间应该通过明确的接口进行通信
- **可重用**: 设计通用的节点类型，提高复用性
- **可测试**: 每个节点都应该是可独立测试的

### 2. 性能优化

- **并行执行**: 充分利用并行执行能力
- **缓存策略**: 合理使用缓存减少重复计算
- **资源管理**: 注意内存和计算资源的使用
- **异步处理**: 使用异步模式提高性能

### 3. 错误处理

- **优雅降级**: 实现错误时的优雅降级策略
- **重试机制**: 对临时性错误实施重试
- **详细日志**: 记录详细的错误信息和执行路径
- **回滚机制**: 支持工作流的回滚操作

### 4. 可维护性

- **配置外部化**: 将配置从代码中分离
- **版本管理**: 为工作流配置实施版本管理
- **文档完善**: 为每个工作流和节点编写清晰的文档
- **监控告警**: 实施完善的监控和告警机制

这个工作流引擎模块为ORE项目提供了强大而灵活的AI工作流编排能力，支持复杂的任务流程管理和智能化的执行调度。