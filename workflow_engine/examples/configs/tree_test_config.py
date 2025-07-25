"""
树形工作流配置

完全重构后的简化配置格式
"""

# 多起始节点工作流配置
MULTI_START_CONFIG = {
    "workflow_id": "multi_start_001",
    "name": "多起始节点工作流",
    "nodes": {
        "start1": {"id": "start1", "name": "开始1", "description": "起始点1", "prompt": "", "node_type": "start"},
        "start2": {"id": "start2", "name": "开始2", "description": "起始点2", "prompt": "", "node_type": "start"},
        "process_a": {"id": "process_a", "name": "处理A", "description": "处理节点A", "prompt": "执行任务A", "node_type": "process", "database_connection": "db_a"},
        "process_b": {"id": "process_b", "name": "处理B", "description": "处理节点B", "prompt": "执行任务B", "node_type": "process", "database_connection": "db_b"},
        "merge": {"id": "merge", "name": "合并", "description": "合并结果", "prompt": "整合A和B的结果", "node_type": "process"},
        "output1": {"id": "output1", "name": "输出1", "description": "最终输出1", "prompt": "生成输出1", "node_type": "leaf"},
        "output2": {"id": "output2", "name": "输出2", "description": "最终输出2", "prompt": "生成输出2", "node_type": "leaf", "database_connection": "db_output"}
    },
    "edges": [
        {"from_node": "start1", "to_node": "process_a", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": False, "include_database_search": True, "database_search_input": "prompt"}},
        {"from_node": "start2", "to_node": "process_b", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": False, "include_database_search": True, "database_search_input": "prompt"}},
        {"from_node": "process_a", "to_node": "merge", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "process_b", "to_node": "merge", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "merge", "to_node": "output1", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "merge", "to_node": "output2", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": True, "database_search_input": "prompt_and_previous"}}
    ]
}

# 简单线性工作流配置
SIMPLE_CONFIG = {
    "workflow_id": "simple_001",
    "name": "简单工作流",
    "nodes": {
        "start": {"id": "start", "name": "开始", "description": "起始点", "prompt": "", "node_type": "start"},
        "process": {"id": "process", "name": "处理", "description": "处理节点", "prompt": "执行处理", "node_type": "process"},
        "output": {"id": "output", "name": "输出", "description": "输出节点", "prompt": "生成输出", "node_type": "leaf"}
    },
    "edges": [
        {"from_node": "start", "to_node": "process", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": False, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "process", "to_node": "output", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}}
    ]
}

# 复杂分支工作流配置
COMPLEX_BRANCH_CONFIG = {
    "workflow_id": "complex_branch_001", 
    "name": "复杂分支工作流",
    "nodes": {
        "start": {"id": "start", "name": "开始", "description": "起始点", "prompt": "", "node_type": "start"},
        "analyze": {"id": "analyze", "name": "分析", "description": "数据分析", "prompt": "分析输入数据", "node_type": "process", "database_connection": "analytics_db"},
        "branch_a": {"id": "branch_a", "name": "分支A", "description": "处理路径A", "prompt": "处理路径A", "node_type": "process"},
        "branch_b": {"id": "branch_b", "name": "分支B", "description": "处理路径B", "prompt": "处理路径B", "node_type": "process"},
        "branch_c": {"id": "branch_c", "name": "分支C", "description": "处理路径C", "prompt": "处理路径C", "node_type": "process"},
        "final_a": {"id": "final_a", "name": "结果A", "description": "最终结果A", "prompt": "生成结果A", "node_type": "leaf"},
        "final_b": {"id": "final_b", "name": "结果B", "description": "最终结果B", "prompt": "生成结果B", "node_type": "leaf"},
        "final_c": {"id": "final_c", "name": "结果C", "description": "最终结果C", "prompt": "生成结果C", "node_type": "leaf"}
    },
    "edges": [
        {"from_node": "start", "to_node": "analyze", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": False, "include_database_search": True, "database_search_input": "prompt"}},
        {"from_node": "analyze", "to_node": "branch_a", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "analyze", "to_node": "branch_b", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "analyze", "to_node": "branch_c", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "branch_a", "to_node": "final_a", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "branch_b", "to_node": "final_b", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
        {"from_node": "branch_c", "to_node": "final_c", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}}
    ]
}

# 为了保持向上兼容，提供旧名称的别名
TREE_TEST_CONFIG = MULTI_START_CONFIG
SIMPLE_TREE_CONFIG = SIMPLE_CONFIG 