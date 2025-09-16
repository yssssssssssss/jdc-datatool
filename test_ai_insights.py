#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI洞察功能测试脚本
用于诊断"AI分析需要一些时间，请稍后重试"的问题
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime

def test_backend_ai_chat():
    """测试后端AI聊天接口"""
    print("=== 测试后端AI聊天接口 ===")
    
    # 模拟前端发送的数据
    test_data = {
        'question': '请分析这个数据集的基本特征',
        'data_context': {
            'shape': [1000, 5],
            'columns': ['age', 'income', 'education', 'city', 'score'],
            'dtypes': {
                'age': 'int64',
                'income': 'float64', 
                'education': 'object',
                'city': 'object',
                'score': 'float64'
            },
            'missing_values': {
                'age': 5,
                'income': 12,
                'education': 3,
                'city': 0,
                'score': 8
            },
            'numeric_columns': ['age', 'income', 'score'],
            'categorical_columns': ['education', 'city']
        },
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    try:
        print(f"🚀 发送请求到: {backend_url}")
        print(f"📊 请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        start_time = time.time()
        
        # 设置较长的超时时间来测试
        response = requests.post(backend_url, json=test_data, timeout=180)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️ 响应时间: {response_time:.2f}秒")
        print(f"📈 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功")
            print(f"📝 响应结构: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print(f"🎉 AI分析成功")
                print(f"💬 AI响应: {result.get('response', '')[:200]}...")
                
                if result.get('chart'):
                    print(f"📊 生成了图表")
                else:
                    print(f"📊 未生成图表")
                    
                return True
            else:
                print(f"❌ AI分析失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ 请求超时（180秒）")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 连接失败，请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"💥 测试失败: {str(e)}")
        return False

def test_frontend_timeout_logic():
    """测试前端超时逻辑"""
    print("\n=== 测试前端超时逻辑 ===")
    
    # 模拟前端的超时设置
    frontend_timeout = 180  # 前端设置的180秒超时
    
    test_data = {
        'question': '分析数据分布',
        'data_context': {
            'shape': [100, 3],
            'columns': ['age', 'income', 'score'],
            'dtypes': {'age': 'int64', 'income': 'float64', 'score': 'float64'},
            'missing_values': {'age': 2, 'income': 3, 'score': 1},
            'numeric_columns': ['age', 'income', 'score'],
            'categorical_columns': []
        },
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    try:
        print(f"🚀 使用前端超时设置({frontend_timeout}秒)测试")
        
        start_time = time.time()
        
        # 使用前端相同的超时设置
        response = requests.post(backend_url, json=test_data, timeout=frontend_timeout)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️ 响应时间: {response_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 在前端超时限制内成功完成")
                return True
            else:
                print(f"❌ 后端返回错误: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ 触发前端超时({frontend_timeout}秒)")
        print(f"💡 这就是用户看到'AI分析请求超时'的原因")
        return False
    except Exception as e:
        print(f"💥 其他错误: {str(e)}")
        return False

def test_llm_direct_call():
    """直接测试LLM调用"""
    print("\n=== 直接测试LLM调用 ===")
    
    try:
        from backend.llm_analyzer import LLMAnalyzer
        
        analyzer = LLMAnalyzer()
        
        test_question = "请分析这个数据集"
        test_context = {
            'shape': [1000, 5],
            'columns': ['age', 'income', 'education', 'city', 'score'],
            'numeric_columns': ['age', 'income', 'score'],
            'categorical_columns': ['education', 'city']
        }
        
        print(f"🤖 直接调用LLMAnalyzer.chat_with_data")
        
        start_time = time.time()
        result = analyzer.chat_with_data(test_question, test_context)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"⏱️ LLM响应时间: {response_time:.2f}秒")
        
        if result.get('success'):
            print(f"✅ LLM调用成功")
            print(f"💬 响应长度: {len(result.get('response', ''))}字符")
            print(f"📊 可视化配置: {result.get('visualization', {})}")
            return True
        else:
            print(f"❌ LLM调用失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"💥 LLM测试失败: {str(e)}")
        return False

def check_backend_service():
    """检查后端服务状态"""
    print("=== 检查后端服务状态 ===")
    
    try:
        response = requests.get("http://localhost:7701/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 后端服务运行正常")
            return True
    except:
        pass
    
    # 如果health端点不存在，尝试其他端点
    try:
        response = requests.get("http://localhost:7701/", timeout=5)
        print(f"✅ 后端服务可访问 (状态码: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到后端服务 (http://localhost:7701)")
        return False
    except Exception as e:
        print(f"❌ 后端服务检查失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("AI洞察功能诊断工具")
    print("=" * 50)
    print(f"🕐 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试结果统计
    test_results = []
    
    # 1. 检查后端服务
    print("1️⃣ 检查后端服务状态")
    backend_ok = check_backend_service()
    test_results.append(("后端服务", backend_ok))
    
    if not backend_ok:
        print("\n❌ 后端服务未运行，请先启动后端服务")
        return
    
    print()
    
    # 2. 测试LLM直接调用
    print("2️⃣ 测试LLM直接调用")
    llm_ok = test_llm_direct_call()
    test_results.append(("LLM直接调用", llm_ok))
    
    # 3. 测试后端API
    print("3️⃣ 测试后端AI聊天接口")
    api_ok = test_backend_ai_chat()
    test_results.append(("后端API", api_ok))
    
    # 4. 测试前端超时逻辑
    print("4️⃣ 测试前端超时逻辑")
    timeout_ok = test_frontend_timeout_logic()
    test_results.append(("前端超时测试", timeout_ok))
    
    # 输出测试结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    # 分析问题
    print("\n🔍 问题分析")
    print("-" * 30)
    
    if not llm_ok:
        print("❌ LLM调用失败 - 检查OpenAI API配置")
    elif not api_ok:
        print("❌ 后端API失败 - 检查后端代码逻辑")
    elif not timeout_ok:
        print("⚠️ 前端超时问题 - AI响应时间超过180秒")
        print("💡 建议解决方案:")
        print("   1. 进一步优化LLM提示词，减少响应时间")
        print("   2. 考虑使用流式响应")
        print("   3. 添加更详细的进度提示")
    else:
        print("✅ 所有测试通过，AI洞察功能正常")
    
    print(f"\n🕐 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()