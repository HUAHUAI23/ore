#!/usr/bin/env python3
"""
LangChain 简单测试脚本
快速验证环境配置是否正确
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    print("🧪 LangChain 简单测试")
    print("=" * 40)
    
    # 1. 检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE', 'https://aiproxy.usw.sealos.io/v1')
    model_name = os.getenv('OPENAI_MODEL', 'claude-3-5-haiku-20241022')
    
    print(f"API密钥: {'✅ 已设置' if api_key else '❌ 未设置'}")
    print(f"API端点: {api_base}")
    print(f"模型名称: {model_name}")
    print()
    
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 2. 导入 LangChain
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        print("✅ LangChain 导入成功")
    except ImportError as e:
        print(f"❌ LangChain 导入失败: {e}")
        return
    
    # 3. 创建客户端
    try:
        
        client = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=api_base,
            temperature=0.7,
            max_tokens=100,
            timeout=30.0
        )
        print("✅ 客户端创建成功")
        print(f"   使用端点: {api_base}")
    except Exception as e:
        print(f"❌ 客户端创建失败: {e}")
        return
    
    # 4. 测试 API 调用
    try:
        print("\n🚀 测试 API 调用...")
        
        message = HumanMessage(content="Hello, please respond with 'OK' to confirm the connection.")
        response = client.invoke([message])
        
        print("✅ API 调用成功!")
        print(f"响应: {response.content}")
        print("\n🎉 所有测试通过! LangChain 配置正确。")
        
    except Exception as e:
        print(f"❌ API 调用失败: {e}")
        
        # 简单的错误分析
        error_str = str(e).lower()
        if "404" in error_str:
            print("\n💡 建议:")
            print("- 检查 API 端点 URL 是否正确")
            print("- 确保 .env 文件中没有多余的注释")
            print("- 验证模型名称是否被支持")
        elif "401" in error_str or "unauthorized" in error_str:
            print("\n💡 建议:")
            print("- 检查 API 密钥是否正确")
            print("- 确认密钥是否有权限访问该模型")

if __name__ == "__main__":
    main() 