# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Workflow Engine Framework** written in Python that provides a flexible, extensible system for executing complex workflows. The project implements a modular workflow execution engine with support for different workflow types, currently focusing on tree-based workflows with event-driven processing.

## Architecture

The codebase follows a layered architecture pattern:

```
workflow_engine/                    # Main package
├── base/                          # Abstract base classes  
│   └── engine.py                  # BaseWorkflowEngine abstract class
├── engines/                       # Concrete engine implementations
│   └── tree/                     # Tree workflow engine (implemented)
├── examples/                      # Usage examples and demos
│   ├── configs/                  # Configuration examples
│   └── tree_workflow_demo.py    # Main demonstration
├── workflow_types.py             # Common type definitions
└── __init__.py                  # Package entry point
```

### Key Components

- **BaseWorkflowEngine** (`workflow_engine/base/engine.py`): Abstract base class defining the contract for all workflow engines with state management and pluggable execution functions
- **TreeWorkflowEngine** (`workflow_engine/engines/tree/engine.py`): Concrete implementation for tree-based workflows with event-driven execution, cycle detection, and conditional routing
- **Configuration System**: Workflows defined via structured dictionaries with nodes and edges
- **Type System** (`workflow_engine/engines/tree/types.py`): TreeNode, TreeEdge, TreeInputConfig, and execution result types

## Running and Testing

### Run the Demo
```bash
python workflow_engine/examples/tree_workflow_demo.py
```

### Run Individual Examples
```python
# In Python shell or scripts
import asyncio
from workflow_engine import TreeWorkflowEngine, create_tree_workflow
from workflow_engine.examples.configs.tree_test_config import SIMPLE_CONFIG

# Method 1: Direct instantiation  
engine = TreeWorkflowEngine(SIMPLE_CONFIG)
result = await engine.execute_workflow()

# Method 2: Convenience function
engine = create_tree_workflow(SIMPLE_CONFIG)
result = await engine.execute_workflow()
```

### Test Configuration Examples
The project includes three test configurations in `workflow_engine/examples/configs/tree_test_config.py`:
- **SIMPLE_CONFIG**: Linear pipeline (Start → Process → Output)
- **MULTI_START_CONFIG**: Parallel start with merge pattern  
- **COMPLEX_BRANCH_CONFIG**: Fan-out pattern with multiple branches

## Workflow Configuration Structure

Workflows are defined using structured dictionaries:

```python
{
    "workflow_id": "unique_id",
    "name": "Human readable name",
    "nodes": {
        "node_id": {
            "id": "node_id", 
            "name": "Display name",
            "description": "Purpose description",
            "prompt": "Task instructions",
            "node_type": "start|process|leaf",  # from NodeType enum
            "database_connection": "optional_db_name"
        }
    },
    "edges": [
        {
            "from": "source_node",
            "to": "target_node",
            "condition": "routing_expression",  # Python expression
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

## Core Features

### Event-Driven Execution Model
1. **Initialization**: Parse configuration, build execution graph, detect cycles
2. **Start Phase**: Execute all START nodes simultaneously  
3. **Event Loop**: Monitor running tasks, trigger dependent nodes when prerequisites are met
4. **Completion**: Generate execution summary with statistics

### Extensibility Points
- **Custom Executors**: Pluggable `NodeExecutor`, `DatabaseSearcher`, and `ConditionChecker` functions
- **Future Engines**: DAG and Graph engines planned (directories exist but not implemented)
- **Input Composition**: Flexible system for combining prompts, previous outputs, and database searches
- **Condition-Based Routing**: Dynamic conditions using Python expressions evaluated at runtime

### Built-in Validation
- **Cycle Detection**: DFS-based cycle detection during graph construction prevents invalid workflows
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Error Handling**: Custom exception classes for different error scenarios

## Dependencies

The project uses pure Python with standard library only - no external dependencies are required. Compatible with Python 3.7+ (uses type hints and async/await).

## Extension Guidelines  

When adding new workflow engines:
1. Inherit from `BaseWorkflowEngine` in `workflow_engine/base/engine.py`
2. Implement required abstract methods for workflow execution
3. Add engine to `workflow_engine/engines/__init__.py` 
4. Update `get_supported_workflow_types()` in main `__init__.py`
5. Create configuration examples and demos following existing patterns