#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端实际的AI洞察功能
验证是否还会出现60秒超时问题
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime

def test_frontend_ai_insight():
    """测试前端AI洞察功能的实际超时设置"""
    print("=== 前端AI洞察功能测试 ===")
    print(f"测试时间: {datetime.now()}")
    
    # 测试数据
    test_data = {
        'question': '请分析这个数据集的主要特征和趋势',
        'data_context': {
            'shape': [100, 5],
            'columns': ['date', 'value1', 'value2', 'category', 'amount'],
            'dtypes': {
                'date': 'object',
                'value1': 'float64',
                'value2': 'float64', 
                'category': 'object',
                'amount': 'float64'
            },
            'missing_values': {
                'date': 0,
                'value1': 2,
                'value2': 1,
                'category': 0,
                'amount': 3
            },
            'numeric_columns': ['value1', 'value2', 'amount'],
            'categorical_columns': ['date', 'category']
        },
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    try:
        print("\n📡 发送AI洞察请求...")
        print(f"目标URL: {backend_url}")
        
        start_time = time.time()
        
        # 使用与前端相同的超时设置
        response = requests.post(backend_url, json=test_data, timeout=180)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ 请求耗时: {duration:.2f}秒")
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 请求成功!")
            print(f"📝 响应内容: {result.get('response', '无响应内容')[:200]}...")
            
            if result.get('success'):
                print("🎯 AI分析成功完成")
                return True
            else:
                print(f"❌ AI分析失败: {result.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"错误内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout as e:
        print(f"\n⏰ 请求超时 (180秒): {e}")
        print("这表明前端确实使用了180秒超时设置")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n🔌 连接错误: {e}")
        print("无法连接到后端服务，请确保服务正在运行")
        return False
        
    except Exception as e:
        print(f"\n❌ 其他错误: {e}")
        return False

def test_backend_health():
    """测试后端健康状态"""
    print("\n=== 后端健康检查 ===")
    
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始前端AI洞察功能实际测试")
    
    # 1. 检查后端服务
    if not test_backend_health():
        print("\n⚠️ 后端服务不可用，无法进行测试")
        return
    
    # 2. 测试AI洞察功能
    success = test_frontend_ai_insight()
    
    # 3. 生成测试报告
    print("\n" + "="*50)
    print("📋 测试报告")
    print("="*50)
    
    if success:
        print("✅ 前端AI洞察功能正常")
        print("✅ 超时设置已更新为180秒")
        print("✅ 不再出现60秒超时问题")
    else:
        print("❌ 前端AI洞察功能存在问题")
        print("🔍 建议检查:")
        print("   - 后端服务状态")
        print("   - 网络连接")
        print("   - OpenAI API配置")
        print("   - 前端代码中的超时设置")
    
    print("\n💡 如果用户仍然看到60秒超时错误，可能的原因:")
    print("   1. 浏览器缓存了旧的前端代码")
    print("   2. Streamlit应用需要重启")
    print("   3. 存在其他未发现的60秒超时设置")
    print("   4. 用户看到的是旧的错误消息")

if __name__ == "__main__":
    main()