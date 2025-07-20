"""
LangChain集成演示

展示如何在工作流引擎中使用真实的LLM调用
"""

import asyncio
import os
from workflow_engine import TreeWorkflowEngine
from workflow_engine.examples.configs.tree_test_config import SIMPLE_CONFIG, COMPLEX_BRANCH_CONFIG

# 智能工作流配置示例
INTELLIGENT_WORKFLOW_CONFIG = {
    "workflow_id": "intelligent_analysis",
    "name": "智能分析工作流",
    "nodes": {
        "start": {
            "id": "start", 
            "name": "数据收集", 
            "description": "收集待分析的数据",
            "prompt": "请收集用户输入的数据进行分析",
            "node_type": "start"
        },
        "analysis": {
            "id": "analysis",
            "name": "数据分析", 
            "description": "分析收集到的数据",
            "prompt": "请对以下数据进行深入分析，识别关键模式和趋势",
            "node_type": "process"
        },
        "summary": {
            "id": "summary",
            "name": "生成摘要",
            "description": "生成分析摘要报告", 
            "prompt": "请根据分析结果生成简洁明了的摘要报告",
            "node_type": "leaf"
        },
        "recommendations": {
            "id": "recommendations", 
            "name": "生成建议",
            "description": "基于分析结果提供建议",
            "prompt": "请基于分析结果提供具体的行动建议和改进方案",
            "node_type": "leaf"
        }
    },
    "edges": [
        {
            "from": "start",
            "to": "analysis", 
            "condition": "true",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True,
                "include_database_search": False,
                "database_search_input": "prompt"
            }
        },
        {
            "from": "analysis",
            "to": "summary",
            "condition": "true", 
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True,
                "include_database_search": False,
                "database_search_input": "prompt"
            }
        },
        {
            "from": "analysis", 
            "to": "recommendations",
            "condition": "true",
            "input_config": {
                "include_prompt": True,
                "include_previous_output": True,
                "include_database_search": False,
                "database_search_input": "prompt"
            }
        }
    ]
}

async def demo_with_mock_llm():
    """使用模拟LLM演示"""
    print("\n" + "="*60)
    print("📋 模拟LLM演示 (无需API密钥)")
    print("="*60)
    
    engine = TreeWorkflowEngine(SIMPLE_CONFIG)
    result = await engine.execute_workflow()
    
    print(f"\n✅ 执行完成: {result.base_summary.completed_count}/{result.base_summary.total_count}")
    print(f"📊 成功率: {result.success_rate:.1%}")
    
    return result

async def demo_with_real_llm():
    """使用真实LLM演示"""
    print("\n" + "="*60)
    print("🤖 真实LLM演示 (需要OPENAI_API_KEY)")
    print("="*60)
    
    # 检查API密钥
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ 未设置OPENAI_API_KEY环境变量")
        print("请设置API密钥后重试:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return None
    
    # 运行智能工作流
    engine = TreeWorkflowEngine(INTELLIGENT_WORKFLOW_CONFIG)
    result = await engine.execute_workflow()
    
    print(f"\n✅ 智能工作流执行完成!")
    print(f"📊 执行统计: {result.base_summary.completed_count}/{result.base_summary.total_count}")
    print(f"🎯 成功率: {result.success_rate:.1%}")
    
    # 显示所有节点的结果
    print("\n🔍 节点执行结果:")
    for node_id, result_data in result.base_summary.results.items():
        node_name = engine.nodes[node_id].name
        print(f"  📄 {node_name}: {result_data}")
    
    return result

async def demo_installation_guide():
    """安装指南演示"""
    print("\n" + "="*60)
    print("📦 LangChain安装指南")
    print("="*60)
    
    print("要使用真实的LLM调用，请安装以下依赖:")
    print()
    print("1. 安装LangChain OpenAI包:")
    print("   pip install langchain-openai")
    print()
    print("2. 设置OpenAI API密钥:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print()
    print("3. 或者在Python中设置:")
    print("   import os")
    print("   os.environ['OPENAI_API_KEY'] = 'your-api-key-here'")
    print()
    print("4. 获取API密钥:")
    print("   访问 https://platform.openai.com/api-keys")
    print()

async def main():
    """主演示函数"""
    print("🚀 LangChain集成工作流引擎演示")
    print("支持真实LLM调用和模拟调用")
    
    # 显示安装指南
    await demo_installation_guide()
    
    # 运行模拟LLM演示
    await demo_with_mock_llm()
    
    # 尝试运行真实LLM演示
    await demo_with_real_llm()
    
    print("\n" + "="*60)
    print("🎉 演示完成!")
    print("="*60)
    print()
    print("💡 使用说明:")
    print("- 设置OPENAI_API_KEY后可使用真实的GPT模型")
    print("- 未设置API密钥时自动降级到模拟调用")
    print("- 支持所有LangChain兼容的LLM模型")

if __name__ == "__main__":
    asyncio.run(main())