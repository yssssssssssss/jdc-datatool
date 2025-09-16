#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端超时问题诊断脚本
模拟用户在前端界面的实际操作
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime

def test_frontend_ai_insight_with_different_timeouts():
    """测试不同超时设置下的AI洞察功能"""
    print("=== 测试前端AI洞察超时问题 ===")
    print(f"🕐 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 模拟前端发送的数据
    test_data = {
        'question': '请分析这个数据集的主要特征和分布情况，并生成相应的可视化图表',
        'data_context': {
            'shape': [1000, 10],  # 更大的数据集
            'columns': ['age', 'income', 'score', 'category', 'region', 'date', 'value1', 'value2', 'value3', 'status'],
            'dtypes': {
                'age': 'int64', 'income': 'float64', 'score': 'float64',
                'category': 'object', 'region': 'object', 'date': 'datetime64[ns]',
                'value1': 'float64', 'value2': 'float64', 'value3': 'float64', 'status': 'object'
            },
            'missing_values': {'age': 10, 'income': 15, 'score': 5, 'category': 0, 'region': 2, 'date': 0, 'value1': 8, 'value2': 12, 'value3': 6, 'status': 3},
            'numeric_columns': ['age', 'income', 'score', 'value1', 'value2', 'value3'],
            'categorical_columns': ['category', 'region', 'status']
        },
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    # 测试不同的超时设置
    timeout_settings = [30, 60, 90, 120, 180]  # 30秒到3分钟
    
    for timeout in timeout_settings:
        print(f"\n📊 测试超时设置: {timeout}秒")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            response = requests.post(backend_url, json=test_data, timeout=timeout)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️ 实际响应时间: {duration:.2f}秒")
            print(f"📈 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 请求成功 (超时设置: {timeout}秒)")
                    print(f"💬 AI响应长度: {len(result.get('response', ''))}字符")
                    
                    if result.get('chart'):
                        print(f"📊 包含图表数据")
                    
                    # 如果这个超时设置成功，记录为推荐设置
                    if duration < timeout * 0.8:  # 如果响应时间小于超时时间的80%
                        print(f"💡 推荐超时设置: {timeout}秒 (响应时间: {duration:.2f}秒)")
                        return timeout
                else:
                    print(f"❌ API返回失败: {result.get('error', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.Timeout:
            end_time = time.time()
            duration = end_time - start_time
            print(f"⏰ 超时 ({timeout}秒) - 实际耗时: {duration:.2f}秒")
            print(f"💡 这就是用户看到超时错误的原因")
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"💥 其他错误: {str(e)} - 耗时: {duration:.2f}秒")
    
    return None

def test_streamlit_timeout_behavior():
    """测试Streamlit的超时行为"""
    print("\n=== 测试Streamlit超时行为 ===")
    
    # 检查Streamlit配置
    try:
        import streamlit as st
        print(f"📦 Streamlit版本: {st.__version__}")
        
        # 检查是否有相关的超时配置
        print("🔍 检查Streamlit配置...")
        
        # Streamlit的一些默认超时设置
        print("💡 Streamlit可能的超时设置:")
        print("   - 默认请求超时: 通常由requests库控制")
        print("   - 浏览器超时: 通常为60-120秒")
        print("   - 代理超时: 可能存在反向代理超时")
        
    except ImportError:
        print("❌ 无法导入Streamlit")

def check_system_timeout_settings():
    """检查系统级别的超时设置"""
    print("\n=== 检查系统超时设置 ===")
    
    # 检查环境变量中的超时设置
    import os
    
    timeout_env_vars = [
        'REQUESTS_TIMEOUT',
        'HTTP_TIMEOUT', 
        'STREAMLIT_TIMEOUT',
        'OPENAI_TIMEOUT'
    ]
    
    print("🔍 检查环境变量:")
    for var in timeout_env_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: {value}")
        else:
            print(f"   {var}: 未设置")
    
    # 检查requests的默认超时
    print("\n📦 检查requests库默认设置:")
    try:
        import requests
        print(f"   requests版本: {requests.__version__}")
        print(f"   默认超时: None (无限制)")
        print(f"   建议设置: 明确指定超时时间")
    except ImportError:
        print("   ❌ 无法导入requests")

def main():
    """主测试函数"""
    print("前端超时问题诊断工具")
    print("=" * 60)
    
    # 1. 测试不同超时设置
    recommended_timeout = test_frontend_ai_insight_with_different_timeouts()
    
    # 2. 测试Streamlit行为
    test_streamlit_timeout_behavior()
    
    # 3. 检查系统设置
    check_system_timeout_settings()
    
    # 总结和建议
    print("\n" + "=" * 60)
    print("📋 诊断总结和建议")
    print("=" * 60)
    
    if recommended_timeout:
        print(f"✅ 推荐的超时设置: {recommended_timeout}秒")
        print(f"💡 建议将前端超时时间调整为: {recommended_timeout + 30}秒 (增加30秒缓冲)")
    else:
        print("⚠️ 所有超时设置都失败，建议:")
        print("   1. 检查后端服务是否正常运行")
        print("   2. 检查OpenAI API配置")
        print("   3. 考虑优化AI提示词以减少响应时间")
        print("   4. 考虑使用流式响应")
    
    print("\n🔧 修复建议:")
    print("   1. 将前端超时时间从120秒调整为180秒")
    print("   2. 添加更详细的进度提示")
    print("   3. 考虑实现请求取消功能")
    print("   4. 添加重试机制")
    
    print(f"\n🕐 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()