"""
树形工作流引擎使用示例 - 集成LangChain LLM

展示如何使用更新后的引擎进行AI驱动的工作流处理
"""

import asyncio
import json
import os
import traceback
from datetime import datetime
from pathlib import Path

from workflow_engine.engines.tree.engine import TreeWorkflowEngine
from workflow_engine.engines.tree.types import TreeWorkflowConfig


async def main():
    """主函数 - 演示AI驱动的内容生产工作流"""

    # 定义一个AI内容生产工作流配置
    workflow_config: TreeWorkflowConfig = {
        "workflow_id": "ai_content_workflow_001",
        "workflow_name": "AI内容生产工作流",
        "description": "基于LLM的智能内容创作和优化流程",
        "version": "1.0.0",
        "type": "tree",
        "nodes": {
            "start": {
                "id": "start",
                "name": "启动节点",
                "description": "工作流开始",
                "prompt": "",
                "node_type": "START",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "topic_analysis": {
                "id": "topic_analysis",
                "name": "话题分析",
                "description": "分析用户输入的话题，提取关键要素和目标受众",
                "prompt": "请分析以下话题，提取关键要素、目标受众和内容方向。要求输出结构化信息，包括：1. 核心主题 2. 目标受众 3. 内容角度 4. 关键词建议",
                "node_type": "INTERMEDIATE",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "content_outline": {
                "id": "content_outline",
                "name": "内容大纲",
                "description": "基于话题分析结果，生成详细的内容大纲",
                "prompt": "基于上述话题分析，请生成一个详细的内容大纲。包括：1. 标题建议 2. 主要章节 3. 每章节的核心要点 4. 预期字数分配",
                "node_type": "INTERMEDIATE",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "content_generation": {
                "id": "content_generation",
                "name": "内容生成",
                "description": "根据大纲生成完整的文章内容",
                "prompt": "根据以上大纲，请生成完整的文章内容。要求：1. 逻辑清晰 2. 语言流畅 3. 信息准确 4. 符合目标受众需求",
                "node_type": "INTERMEDIATE",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "seo_optimization": {
                "id": "seo_optimization",
                "name": "SEO优化",
                "description": "SEO优化建议和元数据生成",
                "prompt": "请为以上内容提供SEO优化建议，包括：1. 标题优化 2. 关键词密度调整 3. Meta描述 4. 内链建议 5. 图片alt标签建议",
                "node_type": "INTERMEDIATE",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "quality_review": {
                "id": "quality_review",
                "name": "质量审核",
                "description": "内容质量审核和改进建议",
                "prompt": "请对生成的内容进行质量审核，从以下维度评估：1. 内容准确性 2. 逻辑完整性 3. 语言质量 4. 用户体验 5. 改进建议",
                "node_type": "INTERMEDIATE",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "final_output": {
                "id": "final_output",
                "name": "最终输出",
                "description": "整合所有结果，生成最终的内容包",
                "prompt": "请整合以上所有内容，生成最终的内容交付包，包括：1. 最终文章 2. SEO元数据 3. 质量评估报告 4. 发布建议",
                "node_type": "LEAF",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
        },
        "edges": [
            {
                "from_node": "start",
                "to_node": "topic_analysis",
                "condition": None,
            },
            {
                "from_node": "topic_analysis",
                "to_node": "content_outline",
                "condition": None,
            },
            {
                "from_node": "content_outline",
                "to_node": "content_generation",
                "condition": None,
            },
            {
                "from_node": "content_generation",
                "to_node": "seo_optimization",
                "condition": None,
            },
            {
                "from_node": "content_generation",
                "to_node": "quality_review",
                "condition": None,
            },
            {
                "from_node": "seo_optimization",
                "to_node": "final_output",
                "condition": None,
            },
            {
                "from_node": "quality_review",
                "to_node": "final_output",
                "condition": None,
            },
        ],
    }

    try:
        print("=" * 60)
        print("🚀 启动AI驱动的树形工作流引擎")
        print("=" * 60)

        # 初始化工作流引擎
        engine = TreeWorkflowEngine(workflow_config)

        # 执行工作流
        print("\n🔄 开始执行工作流...")
        summary = await engine.execute_workflow()

        # 输出执行结果
        print("\n" + "=" * 60)
        print("📊 工作流执行摘要")
        print("=" * 60)
        print(f"工作流ID: {summary.workflow_id}")
        print(f"工作流名称: {summary.workflow_name}")
        print(
            f"完成率: {summary.success_rate:.1%} ({summary.completed_count}/{summary.total_count})"
        )
        print(f"执行状态: {'✅ 完全成功' if summary.is_complete else '⚠️ 部分完成'}")

        # 输出各节点结果
        print(f"\n📝 节点执行结果:")
        for node_id, result in summary.results.items():
            node_name = engine.nodes[node_id].name
            result_preview = (
                str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            )
            print(f"  • {node_name}: {result_preview}")

        # 如果有最终输出节点，单独显示
        if "final_output" in summary.results:
            print(f"\n🎯 最终内容包:")
            print("-" * 40)
            final_result = summary.results["final_output"]
            print(final_result)

        # 保存完整的工作流结构和摘要到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("workflow_outputs")
        output_dir.mkdir(exist_ok=True)

        # 保存工作流配置
        config_file = output_dir / f"ai_content_workflow_config_{timestamp}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(workflow_config, f, ensure_ascii=False, indent=2)

        # 保存执行摘要和结果
        summary_data = {
            "execution_info": {
                "workflow_id": summary.workflow_id,
                "workflow_name": summary.workflow_name,
                "execution_time": timestamp,
                "success_rate": summary.success_rate,
                "completed_count": summary.completed_count,
                "total_count": summary.total_count,
                "is_complete": summary.is_complete,
            },
            "node_results": {},
        }

        # 添加每个节点的详细结果
        for node_id, result in summary.results.items():
            node_name = engine.nodes[node_id].name
            summary_data["node_results"][node_id] = {
                "node_name": node_name,
                "result": str(result),
            }

        summary_file = output_dir / f"ai_content_workflow_summary_{timestamp}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 工作流数据已保存:")
        print(f"  • 配置文件: {config_file}")
        print(f"  • 摘要文件: {summary_file}")

    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        traceback.print_exc()


async def demo_conditional_workflow():
    """演示带条件分支的工作流"""

    conditional_config: TreeWorkflowConfig = {
        "workflow_id": "conditional_content_workflow",
        "workflow_name": "条件分支内容工作流",
        "description": "根据内容类型选择不同处理路径",
        "version": "1.0.0",
        "type": "tree",
        "nodes": {
            "start": {
                "id": "start",
                "name": "启动",
                "description": "工作流开始",
                "prompt": "",
                "node_type": "START",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "content_classifier": {
                "id": "content_classifier",
                "name": "内容分类器",
                "description": "分析内容类型并输出分类结果",
                "prompt": '请分析输入内容的类型，并明确输出分类结果。可能的类型：技术文章、营销文案、新闻报道、学术论文。请在回答开头明确说明："内容类型：[具体类型]"',
                "node_type": "INTERMEDIATE",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "technical_processor": {
                "id": "technical_processor",
                "name": "技术文章处理器",
                "description": "专门处理技术类内容",
                "prompt": "作为技术专家，请对以下技术内容进行深度分析和优化，包括技术准确性检查、代码示例优化、最佳实践建议等。",
                "node_type": "LEAF",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "marketing_processor": {
                "id": "marketing_processor",
                "name": "营销文案处理器",
                "description": "专门处理营销类内容",
                "prompt": "作为营销专家，请对以下营销内容进行优化，包括吸引力提升、转化率优化、受众定位分析等。",
                "node_type": "LEAF",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
            "general_processor": {
                "id": "general_processor",
                "name": "通用处理器",
                "description": "处理其他类型内容",
                "prompt": "请对以下内容进行通用优化，包括结构调整、语言润色、逻辑完善等。",
                "node_type": "LEAF",
                "input_config": {
                    "include_prompt": True,
                    "include_previous_output": True,
                },
            },
        },
        "edges": [
            {
                "from_node": "start",
                "to_node": "content_classifier",
                "condition": None,
            },
            {
                "from_node": "content_classifier",
                "to_node": "technical_processor",
                "condition": {
                    "match_target": "node_output",
                    "match_type": "contains",
                    "match_value": "技术文章",
                    "case_sensitive": False,
                },
            },
            {
                "from_node": "content_classifier",
                "to_node": "marketing_processor",
                "condition": {
                    "match_target": "node_output",
                    "match_type": "contains",
                    "match_value": "营销文案",
                    "case_sensitive": False,
                },
            },
            {
                "from_node": "content_classifier",
                "to_node": "general_processor",
                "condition": {
                    "match_target": "node_output",
                    "match_type": "not_contains",
                    "match_value": "技术文章",
                    "case_sensitive": False,
                },
            },
        ],
    }

    print("\n" + "=" * 60)
    print("🔀 演示条件分支工作流")
    print("=" * 60)

    try:
        engine = TreeWorkflowEngine(conditional_config)
        summary = await engine.execute_workflow()

        print(f"\n✅ 条件工作流完成，成功率: {summary.success_rate:.1%}")

        # 输出各节点结果
        print(f"\n📝 节点执行结果:")
        for node_id, result in summary.results.items():
            node_name = engine.nodes[node_id].name
            result_preview = (
                str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            )
            print(f"  • {node_name}: {result_preview}")

        # 保存完整的工作流结构和摘要到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("workflow_outputs")
        output_dir.mkdir(exist_ok=True)

        # 保存工作流配置
        config_file = output_dir / f"conditional_workflow_config_{timestamp}.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(conditional_config, f, ensure_ascii=False, indent=2)

        # 保存执行摘要和结果
        summary_data = {
            "execution_info": {
                "workflow_id": summary.workflow_id,
                "workflow_name": summary.workflow_name,
                "execution_time": timestamp,
                "success_rate": summary.success_rate,
                "completed_count": summary.completed_count,
                "total_count": summary.total_count,
                "is_complete": summary.is_complete,
            },
            "node_results": {},
        }

        # 添加每个节点的详细结果
        for node_id, result in summary.results.items():
            node_name = engine.nodes[node_id].name
            summary_data["node_results"][node_id] = {
                "node_name": node_name,
                "result": str(result),
            }

        summary_file = output_dir / f"conditional_workflow_summary_{timestamp}.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 条件工作流数据已保存:")
        print(f"  • 配置文件: {config_file}")
        print(f"  • 摘要文件: {summary_file}")

    except Exception as e:
        print(f"❌ 条件工作流失败: {e}")


# ====================================================================
# 新增的同步包装函数，作为命令行入口点
# ====================================================================
def cli_main():
    """
    同步的命令行入口函数。
    它负责检查环境并使用 asyncio.run() 来运行异步的演示函数。
    """

    try:
        # 运行主演示
        asyncio.run(main())

        # 运行条件分支演示
        print("\n" + "🔄 继续演示条件分支工作流...")
        asyncio.run(demo_conditional_workflow())

        print("\n🎉 所有演示完成！")
    except KeyboardInterrupt:
        print("\n操作被用户中断。")
    except Exception as e:
        print(f"\n❌ 脚本执行时发生未捕获的错误: {e}")
        traceback.print_exc()


# ====================================================================
# __main__ 块现在只调用同步的包装函数
# ====================================================================
if __name__ == "__main__":
    cli_main()
