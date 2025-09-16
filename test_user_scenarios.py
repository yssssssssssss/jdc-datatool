#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户常见使用场景测试
验证修复后的AI洞察功能在实际使用中的表现
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime

def create_realistic_test_data():
    """创建更贴近实际使用的测试数据"""
    import numpy as np
    
    # 创建一个适中大小的数据集（模拟用户常见的数据规模）
    np.random.seed(42)
    n_rows = 100  # 减少数据量，模拟用户常见场景
    
    data = {
        'age': np.random.randint(18, 65, n_rows),
        'salary': np.random.normal(60000, 20000, n_rows),
        'experience': np.random.randint(0, 20, n_rows),
        'department': np.random.choice(['IT', 'Sales', 'Marketing', 'HR'], n_rows),
        'performance_score': np.random.normal(80, 10, n_rows)
    }
    
    df = pd.DataFrame(data)
    
    # 确保数据合理性
    df['salary'] = df['salary'].clip(lower=30000, upper=150000)
    df['performance_score'] = df['performance_score'].clip(lower=50, upper=100)
    
    return df

def test_common_user_questions(df):
    """测试用户常见的问题类型"""
    
    # 用户常见问题（从简单到复杂）
    common_questions = [
        {
            'question': '这个数据集有多少行多少列？',
            'type': '基础信息查询',
            'expected_time': 5
        },
        {
            'question': '显示年龄的分布情况',
            'type': '简单统计分析',
            'expected_time': 8
        },
        {
            'question': '分析薪资和工作经验的关系',
            'type': '相关性分析',
            'expected_time': 10
        },
        {
            'question': '按部门分析平均薪资',
            'type': '分组分析',
            'expected_time': 12
        },
        {
            'question': '找出薪资异常值',
            'type': '异常检测',
            'expected_time': 15
        },
        {
            'question': '生成薪资分布的直方图',
            'type': '可视化请求',
            'expected_time': 12
        }
    ]
    
    print("=== 用户常见使用场景测试 ===")
    print(f"📊 测试数据: {df.shape[0]}行 x {df.shape[1]}列")
    print(f"🕐 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    results = []
    
    for i, scenario in enumerate(common_questions, 1):
        print(f"\n{'='*50}")
        print(f"📋 测试 {i}/{len(common_questions)}: {scenario['type']}")
        print(f"❓ 问题: {scenario['question']}")
        print(f"⏱️ 预期时间: {scenario['expected_time']}秒")
        print(f"{'='*50}")
        
        success, duration, error_msg = send_ai_request(scenario['question'], df)
        
        result = {
            'question': scenario['question'],
            'type': scenario['type'],
            'success': success,
            'duration': duration,
            'expected_time': scenario['expected_time'],
            'error_msg': error_msg
        }
        
        results.append(result)
        
        # 分析结果
        if success:
            if duration <= scenario['expected_time']:
                print(f"🎉 测试通过 - 响应时间优秀 ({duration:.2f}s)")
            elif duration <= 30:
                print(f"✅ 测试通过 - 响应时间良好 ({duration:.2f}s)")
            elif duration <= 60:
                print(f"⚠️ 测试通过 - 响应时间较慢 ({duration:.2f}s)")
            else:
                print(f"🐌 测试通过 - 响应时间很慢 ({duration:.2f}s)")
        else:
            print(f"❌ 测试失败 - {error_msg}")
            
            # 检查是否是60秒超时问题
            if '60' in error_msg and 'timeout' in error_msg.lower():
                print(f"🚨 发现60秒超时问题！")
        
        # 短暂等待
        if i < len(common_questions):
            time.sleep(2)
    
    return results

def send_ai_request(question, df, timeout_seconds=180):
    """发送AI请求"""
    
    # 准备数据上下文
    data_context = {
        'shape': list(df.shape),
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
    }
    
    request_data = {
        'question': question,
        'data_context': data_context,
        'chat_history': []
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    start_time = time.time()
    
    try:
        response = requests.post(backend_url, json=request_data, timeout=timeout_seconds)
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return True, duration, "成功"
            else:
                error_msg = result.get('error', '未知错误')
                return False, duration, f"API错误: {error_msg}"
        else:
            return False, duration, f"HTTP错误: {response.status_code}"
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        return False, duration, f"请求超时({timeout_seconds}秒)"
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        return False, duration, f"其他错误: {str(e)}"

def generate_user_scenario_report(results):
    """生成用户场景测试报告"""
    print(f"\n{'='*60}")
    print("📊 用户常见场景测试报告")
    print(f"{'='*60}")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"📈 总体统计:")
    print(f"   总测试数: {total_tests}")
    print(f"   成功: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"   失败: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    # 检查60秒超时问题
    timeout_60_issues = [r for r in results if not r['success'] and '60' in r['error_msg']]
    if timeout_60_issues:
        print(f"\n🚨 发现60秒超时问题:")
        for issue in timeout_60_issues:
            print(f"   - {issue['type']}: {issue['error_msg']}")
        print(f"\n❌ 用户反馈的60秒超时问题仍然存在！")
    else:
        print(f"\n✅ 未发现60秒超时问题 - 修复成功！")
    
    if successful_tests > 0:
        successful_durations = [r['duration'] for r in results if r['success']]
        avg_duration = sum(successful_durations) / len(successful_durations)
        max_duration = max(successful_durations)
        min_duration = min(successful_durations)
        
        print(f"\n⏱️ 响应时间统计 (成功的请求):")
        print(f"   平均响应时间: {avg_duration:.2f}秒")
        print(f"   最快响应时间: {min_duration:.2f}秒")
        print(f"   最慢响应时间: {max_duration:.2f}秒")
        
        # 用户体验评估
        fast_responses = sum(1 for d in successful_durations if d <= 10)
        medium_responses = sum(1 for d in successful_durations if 10 < d <= 30)
        slow_responses = sum(1 for d in successful_durations if d > 30)
        
        print(f"\n🚀 用户体验分析:")
        print(f"   快速响应 (≤10秒): {fast_responses} ({fast_responses/successful_tests*100:.1f}%)")
        print(f"   中等响应 (10-30秒): {medium_responses} ({medium_responses/successful_tests*100:.1f}%)")
        print(f"   较慢响应 (>30秒): {slow_responses} ({slow_responses/successful_tests*100:.1f}%)")
    
    print(f"\n📋 详细结果:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"   {i}. {status} {result['type']}")
        print(f"      问题: {result['question']}")
        print(f"      响应时间: {result['duration']:.2f}s")
        if not result['success']:
            print(f"      错误: {result['error_msg']}")
    
    # 最终评估
    print(f"\n🎯 修复效果评估:")
    if timeout_60_issues:
        print(f"   ❌ 修复失败！用户仍会遇到60秒超时问题")
        print(f"   🔧 需要进一步检查前端或其他组件的超时设置")
    elif failed_tests == 0:
        print(f"   🎉 修复完美！所有常见用户场景都正常工作")
    elif successful_tests >= total_tests * 0.8:
        print(f"   ✅ 修复良好！大部分用户场景正常，用户体验显著改善")
    else:
        print(f"   ⚠️ 修复部分有效，但仍需优化")
    
    print(f"\n💡 用户使用建议:")
    if timeout_60_issues:
        print(f"   - 避免过于复杂的分析请求")
        print(f"   - 分步骤进行复杂分析")
    else:
        print(f"   - 可以正常使用AI洞察功能")
        print(f"   - 简单查询响应很快，复杂分析可能需要等待")
        print(f"   - 建议从简单问题开始，逐步深入分析")

def main():
    """主测试函数"""
    print("用户常见场景测试 - 验证60秒超时问题修复效果")
    print("=" * 60)
    
    # 检查后端服务
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        return
    
    # 创建测试数据
    df = create_realistic_test_data()
    print(f"📊 测试数据创建完成: {df.shape[0]}行 x {df.shape[1]}列")
    
    # 运行测试
    results = test_common_user_questions(df)
    
    # 生成报告
    generate_user_scenario_report(results)
    
    print(f"\n🕐 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()