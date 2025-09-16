#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终的60秒超时问题测试和修复验证
"""

import requests
import time
import os
import subprocess
from datetime import datetime

def test_all_timeout_sources():
    """测试所有可能的超时源"""
    print("🔍 全面检查所有超时设置")
    print("="*60)
    
    issues_found = []
    
    # 1. 检查前端代码中的超时设置
    print("\n1️⃣ 检查前端代码...")
    try:
        with open("frontend/app.py", "r", encoding="utf-8") as f:
            frontend_code = f.read()
        
        # 查找timeout参数
        if "timeout=180" in frontend_code:
            print("   ✅ 前端requests超时设置: 180秒")
        else:
            print("   ❌ 前端requests超时设置异常")
            issues_found.append("前端requests超时设置")
        
        # 查找错误消息
        if "AI分析请求超时（180秒）" in frontend_code:
            print("   ✅ 前端超时错误消息: 180秒")
        else:
            print("   ❌ 前端超时错误消息异常")
            issues_found.append("前端超时错误消息")
        
        # 检查是否还有60秒引用
        if "60秒" in frontend_code or "timeout=60" in frontend_code:
            print("   ❌ 前端代码中仍有60秒引用")
            issues_found.append("前端代码60秒引用")
        else:
            print("   ✅ 前端代码中无60秒引用")
            
    except Exception as e:
        print(f"   ❌ 检查前端代码失败: {e}")
        issues_found.append("前端代码检查失败")
    
    # 2. 检查Streamlit配置
    print("\n2️⃣ 检查Streamlit配置...")
    try:
        with open(".streamlit/config.toml", "r", encoding="utf-8") as f:
            config_content = f.read()
        
        if "timeout = 300" in config_content:
            print("   ✅ Streamlit服务器超时: 300秒")
        else:
            print("   ❌ Streamlit服务器超时设置异常")
            issues_found.append("Streamlit服务器超时")
        
        if "requestTimeout = 300" in config_content:
            print("   ✅ Streamlit请求超时: 300秒")
        else:
            print("   ❌ Streamlit请求超时设置异常")
            issues_found.append("Streamlit请求超时")
            
    except Exception as e:
        print(f"   ❌ 检查Streamlit配置失败: {e}")
        issues_found.append("Streamlit配置检查失败")
    
    # 3. 检查测试文件中的超时设置
    print("\n3️⃣ 检查测试文件...")
    test_files = [
        "test_ai_insights.py",
        "test_api.py",
        "start.py"
    ]
    
    for test_file in test_files:
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "timeout=60" in content:
                print(f"   ❌ {test_file} 中仍有60秒超时")
                issues_found.append(f"{test_file}中的60秒超时")
            else:
                print(f"   ✅ {test_file} 中无60秒超时")
                
        except Exception as e:
            print(f"   ⚠️ 无法检查 {test_file}: {e}")
    
    return issues_found

def test_actual_ai_request():
    """测试实际的AI请求"""
    print("\n4️⃣ 测试实际AI请求...")
    
    # 准备测试数据
    test_data = {
        'question': '请分析这个数据集的基本统计信息',
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
            'missing_values': {'age': 5, 'income': 3, 'education': 0, 'city': 2, 'score': 1},
            'numeric_columns': ['age', 'income', 'score'],
            'categorical_columns': ['education', 'city']
        },
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    try:
        print("   🚀 发送AI分析请求...")
        start_time = time.time()
        
        # 使用180秒超时
        response = requests.post(backend_url, json=test_data, timeout=180)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ⏱️ 请求耗时: {duration:.2f}秒")
        print(f"   📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ AI请求成功完成")
                return True, f"成功，耗时{duration:.2f}秒"
            else:
                error_msg = result.get('error', '未知错误')
                print(f"   ❌ AI请求失败: {error_msg}")
                return False, error_msg
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        print("   ⏰ 请求超时（180秒）")
        return False, "180秒超时"
    except requests.exceptions.ConnectionError:
        print("   🔌 连接失败，后端服务可能未运行")
        return False, "连接失败"
    except Exception as e:
        print(f"   💥 其他错误: {str(e)}")
        return False, str(e)

def test_backend_health():
    """测试后端健康状态"""
    print("\n🏥 检查后端服务健康状态...")
    
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ 后端服务正常运行")
            return True
        else:
            print(f"   ❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 无法连接后端服务: {e}")
        return False

def simulate_frontend_timeout_scenario():
    """模拟前端超时场景"""
    print("\n5️⃣ 模拟前端超时场景...")
    
    # 发送一个可能导致超时的复杂请求
    complex_data = {
        'question': '请进行深度数据分析，包括相关性分析、异常值检测、聚类分析、预测建模，并生成详细的可视化图表和报告',
        'data_context': {
            'shape': [10000, 20],
            'columns': [f'feature_{i}' for i in range(20)],
            'dtypes': {f'feature_{i}': 'float64' for i in range(20)},
            'missing_values': {f'feature_{i}': i*10 for i in range(20)},
            'numeric_columns': [f'feature_{i}' for i in range(20)],
            'categorical_columns': []
        },
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    try:
        print("   🚀 发送复杂AI分析请求（可能耗时较长）...")
        start_time = time.time()
        
        # 使用较短的超时来测试超时处理
        response = requests.post(backend_url, json=complex_data, timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   ⏱️ 请求耗时: {duration:.2f}秒")
        print(f"   📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 复杂请求在30秒内完成")
            return True, "30秒内完成"
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"   ⏰ 请求超时（30秒），实际耗时: {duration:.2f}秒")
        print("   💡 这种情况下，前端应该显示180秒超时消息")
        return False, "30秒超时（正常）"
    except Exception as e:
        print(f"   💥 其他错误: {str(e)}")
        return False, str(e)

def generate_final_report(issues, ai_test_result, backend_ok, timeout_test_result):
    """生成最终报告"""
    print("\n" + "="*80)
    print("📋 60秒超时问题最终修复验证报告")
    print("="*80)
    
    print(f"\n🕐 测试时间: {datetime.now()}")
    
    print("\n🔍 检查结果:")
    
    # 配置检查结果
    if not issues:
        print("   ✅ 所有超时配置检查通过")
    else:
        print("   ❌ 发现配置问题:")
        for issue in issues:
            print(f"     - {issue}")
    
    # 后端服务状态
    status = "✅" if backend_ok else "❌"
    print(f"   {status} 后端服务: {'正常' if backend_ok else '异常'}")
    
    # AI请求测试结果
    ai_success, ai_message = ai_test_result
    status = "✅" if ai_success else "❌"
    print(f"   {status} AI请求测试: {ai_message}")
    
    # 超时场景测试结果
    timeout_success, timeout_message = timeout_test_result
    status = "✅" if not timeout_success else "⚠️"  # 超时是预期的
    print(f"   {status} 超时场景测试: {timeout_message}")
    
    print("\n🎯 修复效果评估:")
    
    if not issues and backend_ok and ai_success:
        print("   🎉 完美！60秒超时问题已完全解决!")
        print("   ✅ 所有配置正确，AI功能正常")
        print("   ✅ 用户应该不再看到60秒超时错误")
        
        print("\n💡 用户操作建议:")
        print("   1. 清除浏览器缓存（Ctrl+Shift+Delete）")
        print("   2. 强制刷新页面（Ctrl+F5）")
        print("   3. 重新测试AI洞察功能")
        print("   4. 如果仍有问题，尝试无痕模式")
        
    else:
        print("   ⚠️ 仍存在一些问题需要解决:")
        
        if issues:
            print("     - 配置问题需要修复")
        if not backend_ok:
            print("     - 后端服务需要重启")
        if not ai_success:
            print("     - AI功能需要检查")
        
        print("\n🔧 建议解决方案:")
        print("   1. 重启所有服务: python start.py")
        print("   2. 检查网络连接和API配置")
        print("   3. 查看详细错误日志")
        print("   4. 如有必要，重启计算机")
    
    print("\n" + "="*80)

def main():
    """主函数"""
    print("🔧 60秒超时问题最终修复验证")
    print("解决用户仍看到60秒超时错误的问题")
    print("="*80)
    
    try:
        # 1. 全面检查所有超时设置
        issues = test_all_timeout_sources()
        
        # 2. 检查后端服务
        backend_ok = test_backend_health()
        
        # 3. 测试实际AI请求
        ai_test_result = (False, "后端服务不可用")
        if backend_ok:
            ai_test_result = test_actual_ai_request()
        
        # 4. 模拟超时场景
        timeout_test_result = (False, "后端服务不可用")
        if backend_ok:
            timeout_test_result = simulate_frontend_timeout_scenario()
        
        # 5. 生成最终报告
        generate_final_report(issues, ai_test_result, backend_ok, timeout_test_result)
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")

if __name__ == "__main__":
    main()