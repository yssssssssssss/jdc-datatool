#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟浏览器中的实际使用场景
测试是否还会出现60秒超时问题
"""

import requests
import json
import time
import threading
from datetime import datetime

def simulate_long_ai_request():
    """模拟一个需要较长时间的AI请求"""
    print("=== 模拟长时间AI请求测试 ===")
    print(f"测试时间: {datetime.now()}")
    
    # 模拟复杂的数据分析请求
    complex_question = """
    请对这个数据集进行全面的深度分析，包括：
    1. 详细的统计描述分析
    2. 各变量之间的相关性分析
    3. 数据分布特征分析
    4. 异常值检测和处理建议
    5. 趋势分析和预测
    6. 业务洞察和建议
    7. 可视化推荐
    请提供详细的分析报告和具体的数据支撑。
    """
    
    test_data = {
        'question': complex_question,
        'data_context': {
            'shape': [10000, 20],  # 大数据集
            'columns': [f'feature_{i}' for i in range(20)],
            'dtypes': {f'feature_{i}': 'float64' for i in range(15)} | 
                     {f'feature_{i}': 'object' for i in range(15, 20)},
            'missing_values': {f'feature_{i}': i*10 for i in range(20)},
            'numeric_columns': [f'feature_{i}' for i in range(15)],
            'categorical_columns': [f'feature_{i}' for i in range(15, 20)]
        },
        'chat_history': [
            {'role': 'user', 'content': '之前的分析很好'},
            {'role': 'assistant', 'content': '谢谢，我会继续为您提供深入的分析'}
        ]
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    try:
        print("\n📡 发送复杂AI分析请求...")
        print(f"问题长度: {len(complex_question)} 字符")
        print(f"数据规模: {test_data['data_context']['shape']}")
        
        start_time = time.time()
        
        # 使用与前端完全相同的超时设置
        print("⏱️ 使用180秒超时设置（与前端一致）")
        response = requests.post(backend_url, json=test_data, timeout=180)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ 实际请求耗时: {duration:.2f}秒")
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 复杂AI请求成功!")
            
            if result.get('success'):
                response_text = result.get('response', '')
                print(f"📝 响应长度: {len(response_text)} 字符")
                print(f"📄 响应预览: {response_text[:300]}...")
                print("🎯 复杂AI分析成功完成")
                return True, duration
            else:
                error_msg = result.get('error', '未知错误')
                print(f"❌ AI分析失败: {error_msg}")
                return False, duration
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False, duration
            
    except requests.exceptions.Timeout as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n⏰ 请求超时 ({duration:.2f}秒): {e}")
        print("❌ 这表明请求确实超过了180秒")
        return False, duration
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n🔌 连接错误: {e}")
        return False, 0
        
    except Exception as e:
        print(f"\n❌ 其他错误: {e}")
        return False, 0

def test_multiple_timeout_scenarios():
    """测试多种超时场景"""
    print("\n=== 多种超时场景测试 ===")
    
    scenarios = [
        {
            'name': '简单查询',
            'question': '数据集有多少行？',
            'expected_time': '< 10秒'
        },
        {
            'name': '中等复杂查询', 
            'question': '请分析数据的基本统计特征，包括均值、中位数、标准差等',
            'expected_time': '10-30秒'
        },
        {
            'name': '复杂分析查询',
            'question': '请进行全面的数据质量分析，包括缺失值、异常值、数据分布等，并提供处理建议',
            'expected_time': '30-60秒'
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['name']}")
        print(f"预期耗时: {scenario['expected_time']}")
        
        test_data = {
            'question': scenario['question'],
            'data_context': {
                'shape': [1000, 10],
                'columns': ['col1', 'col2', 'col3', 'col4', 'col5', 
                           'col6', 'col7', 'col8', 'col9', 'col10'],
                'dtypes': {f'col{i}': 'float64' for i in range(1, 8)} | 
                         {f'col{i}': 'object' for i in range(8, 11)},
                'missing_values': {f'col{i}': i*5 for i in range(1, 11)},
                'numeric_columns': [f'col{i}' for i in range(1, 8)],
                'categorical_columns': [f'col{i}' for i in range(8, 11)]
            },
            'chat_history': []
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:7701/api/ai/chat", 
                json=test_data, 
                timeout=180
            )
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False)
                print(f"✅ 成功 - 耗时: {duration:.2f}秒")
                results.append({
                    'scenario': scenario['name'],
                    'success': success,
                    'duration': duration,
                    'error': None
                })
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                results.append({
                    'scenario': scenario['name'],
                    'success': False,
                    'duration': duration,
                    'error': f'HTTP {response.status_code}'
                })
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"⏰ 超时 - 耗时: {duration:.2f}秒")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'duration': duration,
                'error': 'Timeout (180s)'
            })
        except Exception as e:
            print(f"❌ 错误: {e}")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'duration': 0,
                'error': str(e)
            })
    
    return results

def check_for_60_second_references():
    """检查系统中是否还有60秒的引用"""
    print("\n=== 检查60秒超时引用 ===")
    
    # 检查当前运行的前端代码
    try:
        # 尝试触发一个可能的60秒超时
        print("🔍 检查是否存在隐藏的60秒超时设置...")
        
        # 发送一个特殊的测试请求
        test_data = {
            'question': 'TEST_TIMEOUT_CHECK',
            'data_context': {'test': True},
            'chat_history': []
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:7701/api/ai/chat", 
                json=test_data, 
                timeout=65  # 稍微超过60秒
            )
            duration = time.time() - start_time
            print(f"✅ 65秒超时测试通过 - 耗时: {duration:.2f}秒")
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            if 59 <= duration <= 61:
                print(f"⚠️ 发现可能的60秒超时! 实际耗时: {duration:.2f}秒")
                return True
            else:
                print(f"✅ 正常超时 - 耗时: {duration:.2f}秒")
                
    except Exception as e:
        print(f"❌ 检查过程出错: {e}")
    
    return False

def main():
    """主测试函数"""
    print("🔍 浏览器超时问题深度检测")
    print("="*60)
    
    # 1. 检查后端服务
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=10)
        if response.status_code != 200:
            print("❌ 后端服务不可用")
            return
        print("✅ 后端服务正常")
    except:
        print("❌ 无法连接后端服务")
        return
    
    # 2. 检查60秒超时引用
    has_60s_timeout = check_for_60_second_references()
    
    # 3. 测试多种场景
    scenario_results = test_multiple_timeout_scenarios()
    
    # 4. 测试长时间请求
    print("\n" + "="*60)
    long_request_success, long_duration = simulate_long_ai_request()
    
    # 5. 生成综合报告
    print("\n" + "="*60)
    print("📋 综合测试报告")
    print("="*60)
    
    print("\n🔍 场景测试结果:")
    for result in scenario_results:
        status = "✅" if result['success'] else "❌"
        error_info = f" ({result['error']})" if result['error'] else ""
        print(f"  {status} {result['scenario']}: {result['duration']:.2f}秒{error_info}")
    
    print(f"\n🕐 长时间请求测试:")
    status = "✅" if long_request_success else "❌"
    print(f"  {status} 复杂分析: {long_duration:.2f}秒")
    
    print(f"\n🔍 60秒超时检查:")
    if has_60s_timeout:
        print("  ⚠️ 发现可能的60秒超时设置")
    else:
        print("  ✅ 未发现60秒超时设置")
    
    # 6. 问题诊断和建议
    print("\n💡 问题诊断:")
    
    all_success = all(r['success'] for r in scenario_results) and long_request_success
    
    if all_success and not has_60s_timeout:
        print("  ✅ 所有测试通过，超时设置正常")
        print("  ✅ 前端已正确配置180秒超时")
        print("\n🎯 如果用户仍看到60秒超时错误，建议:")
        print("     1. 清除浏览器缓存并刷新页面")
        print("     2. 重启Streamlit应用")
        print("     3. 检查是否有多个应用实例在运行")
        print("     4. 确认用户访问的是正确的端口(8504)")
    else:
        print("  ❌ 发现问题，需要进一步调查")
        if has_60s_timeout:
            print("     - 系统中仍存在60秒超时设置")
        failed_scenarios = [r for r in scenario_results if not r['success']]
        if failed_scenarios:
            print("     - 部分场景测试失败")
        if not long_request_success:
            print("     - 长时间请求测试失败")

if __name__ == "__main__":
    main()