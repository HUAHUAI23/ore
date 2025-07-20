# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在该代码库中工作时提供指导。

## 项目概述

这是一个用 Python 编写的**工作流引擎框架**，为执行复杂工作流提供了灵活、可扩展的系统。该项目实现了一个模块化的工作流执行引擎，支持不同的工作流类型，目前专注于基于树结构的工作流和事件驱动处理。

## 架构

代码库遵循分层架构模式：

```
workflow_engine/                    # 主包
├── base/                          # 抽象基类  
│   └── engine.py                  # BaseWorkflowEngine 抽象类
├── engines/                       # 具体引擎实现
│   └── tree/                     # 树工作流引擎（已实现）
├── examples/                      # 使用示例和演示
│   ├── configs/                  # 配置示例
│   └── tree_workflow_demo.py    # 主要演示
├── workflow_types.py             # 通用类型定义
└── __init__.py                  # 包入口点
```

### 核心组件

- **BaseWorkflowEngine** (`workflow_engine/base/engine.py`)：定义所有工作流引擎合约的抽象基类，具备状态管理和可插拔执行函数
- **TreeWorkflowEngine** (`workflow_engine/engines/tree/engine.py`)：基于树结构工作流的具体实现，支持事件驱动执行、循环检测和条件路由
- **配置系统**：通过结构化字典定义工作流，包含节点和边
- **类型系统** (`workflow_engine/engines/tree/types.py`)：TreeNode、TreeEdge、TreeInputConfig 和执行结果类型

## 运行和测试

### 运行演示
```bash
python workflow_engine/examples/tree_workflow_demo.py
```

### 运行单个示例
```python
# 在 Python shell 或脚本中
import asyncio
from workflow_engine import TreeWorkflowEngine, create_tree_workflow
from workflow_engine.examples.configs.tree_test_config import SIMPLE_CONFIG

# 方法 1：直接实例化  
engine = TreeWorkflowEngine(SIMPLE_CONFIG)
result = await engine.execute_workflow()

# 方法 2：便捷函数
engine = create_tree_workflow(SIMPLE_CONFIG)
result = await engine.execute_workflow()
```

### 测试配置示例
项目在 `workflow_engine/examples/configs/tree_test_config.py` 中包含三个测试配置：
- **SIMPLE_CONFIG**：线性管道（开始 → 处理 → 输出）
- **MULTI_START_CONFIG**：并行开始合并模式  
- **COMPLEX_BRANCH_CONFIG**：扇出模式多分支

## 工作流配置结构

工作流使用结构化字典定义：

```python
{
    "workflow_id": "唯一标识",
    "name": "人类可读名称",
    "nodes": {
        "node_id": {
            "id": "node_id", 
            "name": "显示名称",
            "description": "目的说明",
            "prompt": "任务指令",
            "node_type": "start|process|leaf",  # 来自 NodeType 枚举
            "database_connection": "可选数据库名称"
        }
    },
    "edges": [
        {
            "from": "源节点",
            "to": "目标节点",
            "condition": "路由表达式",  # Python 表达式
            "input_config": {
                "include_prompt": true,
                "include_previous_output": true, 
                "include_database_search": false,
                "database_search_input": "prompt|previous_output|prompt_and_previous"
            }
        }
    ]
}
```

## 核心特性

### 事件驱动执行模型
1. **初始化**：解析配置，构建执行图，检测循环
2. **启动阶段**：同时执行所有 START 节点  
3. **事件循环**：监控运行任务，在先决条件满足时触发依赖节点
4. **完成**：生成带统计信息的执行摘要

### 扩展点
- **自定义执行器**：可插拔的 `NodeExecutor`、`DatabaseSearcher` 和 `ConditionChecker` 函数
- **未来引擎**：计划支持 DAG 和 Graph 引擎（目录已存在但未实现）
- **输入组合**：用于组合提示、先前输出和数据库搜索的灵活系统
- **基于条件的路由**：使用运行时评估的 Python 表达式进行动态条件判断

### 内置验证
- **循环检测**：在图构建期间使用基于 DFS 的循环检测来防止无效工作流
- **类型安全**：整个代码库的全面类型提示
- **错误处理**：针对不同错误场景的自定义异常类

## 依赖关系

该项目使用纯 Python 和标准库，无需外部依赖。兼容 Python 3.7+（使用类型提示和 async/await）。

## 扩展指南  

添加新工作流引擎时：
1. 继承 `workflow_engine/base/engine.py` 中的 `BaseWorkflowEngine`
2. 实现工作流执行所需的抽象方法
3. 将引擎添加到 `workflow_engine/engines/__init__.py` 
4. 更新主 `__init__.py` 中的 `get_supported_workflow_types()`
5. 按照现有模式创建配置示例和演示