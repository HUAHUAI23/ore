"""
树形工作流演示

完全重构后的演示代码
"""

import asyncio
from workflow_engine.engines.tree import TreeWorkflowEngine
from workflow_engine.examples.configs.tree_test_config import SIMPLE_CONFIG, MULTI_START_CONFIG, COMPLEX_BRANCH_CONFIG

# 默认模拟节点执行函数
# async def mock_node_executor(node_id: str, input_data: dict) -> str:
#     """模拟节点执行"""
#     print(f"  ⚡ 执行节点 {node_id}, 输入: {input_data}")
#     await asyncio.sleep(0.1)  # 模拟执行时间
#     return f"来自节点 {node_id} 的结果"

# 不同类型的节点执行函数
async def mock_database_executor(node_id: str, input_data: dict) -> str:
    """模拟数据库节点执行"""
    print(f"  🗄️ 数据库节点 {node_id}, 输入: {input_data}")
    await asyncio.sleep(0.2)
    return f"来自数据库节点 {node_id} 的查询结果"

async def run_simple_workflow():
    """运行简单工作流"""
    print("\n" + "="*50)
    print("🔥 简单工作流演示")
    print("="*50)
    
    # engine = TreeWorkflowEngine(SIMPLE_CONFIG, mock_node_executor)
    engine = TreeWorkflowEngine(SIMPLE_CONFIG)
    result = await engine.execute_workflow()
    
    print(f"✅ 完成度: {result.base_summary.completed_count}/{result.base_summary.total_count}")
    print(f"📊 成功率: {result.success_rate:.1%}")
    
    return result

async def run_multi_start_workflow():
    """运行多起始节点工作流"""
    print("\n" + "="*50)
    print("🚀 多起始节点工作流演示")
    print("="*50)
    
    engine = TreeWorkflowEngine(MULTI_START_CONFIG, mock_database_executor)
    result = await engine.execute_workflow()
    
    print(f"✅ 完成度: {result.base_summary.completed_count}/{result.base_summary.total_count}")
    print(f"📊 成功率: {result.success_rate:.1%}")
    
    return result

async def run_complex_branch_workflow():
    """运行复杂分支工作流"""
    print("\n" + "="*50)
    print("🌳 复杂分支工作流演示")
    print("="*50)
    
    engine = TreeWorkflowEngine(COMPLEX_BRANCH_CONFIG, mock_database_executor)
    result = await engine.execute_workflow()
    
    print(f"✅ 完成度: {result.base_summary.completed_count}/{result.base_summary.total_count}")
    print(f"📊 成功率: {result.success_rate:.1%}")
    
    return result

async def test_cycle_detection():
    """测试环路检测"""
    print("\n" + "="*50)
    print("🔄 环路检测测试")
    print("="*50)
    
    # 创建有环路的配置
    cycle_config = {
        "workflow_id": "cycle_test",
        "name": "环路测试",
        "nodes": {
            "a": {"id": "a", "name": "节点A", "description": "节点A", "prompt": "A", "node_type": "start"},
            "b": {"id": "b", "name": "节点B", "description": "节点B", "prompt": "B", "node_type": "process"},
            "c": {"id": "c", "name": "节点C", "description": "节点C", "prompt": "C", "node_type": "leaf"}
        },
        "edges": [
            {"from_node": "a", "to_node": "b", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": False, "include_database_search": False, "database_search_input": "prompt"}},
            {"from_node": "b", "to_node": "c", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}},
            {"from_node": "c", "to_node": "a", "condition": "true", "input_config": {"include_prompt": True, "include_previous_output": True, "include_database_search": False, "database_search_input": "prompt"}}  # 环路
        ]
    }
    
    try:
        # engine = TreeWorkflowEngine(cycle_config, mock_node_executor)
        engine = TreeWorkflowEngine(cycle_config)
        print("❌ 环路检测失败！")
    except Exception as e:
        print(f"✅ 环路检测成功: {e}")

async def main():
    """主函数"""
    print("🎯 树形工作流引擎演示")
    print("完全重构版本")
    
    # 运行所有演示
    await run_simple_workflow()
    await run_multi_start_workflow()
    await run_complex_branch_workflow()
    await test_cycle_detection()
    
    print("\n" + "="*50)
    print("🎉 所有演示完成！")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main()) 