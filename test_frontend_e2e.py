#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端测试脚本 - 验证前端AI洞察功能修复效果
模拟用户在前端界面的实际操作流程
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
import threading
import sys

def create_test_data():
    """创建测试数据集"""
    import numpy as np
    
    # 创建一个中等大小的测试数据集
    np.random.seed(42)
    n_rows = 500
    
    data = {
        'age': np.random.randint(18, 80, n_rows),
        'income': np.random.normal(50000, 15000, n_rows),
        'score': np.random.normal(75, 15, n_rows),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_rows),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_rows),
        'value1': np.random.exponential(2, n_rows),
        'value2': np.random.gamma(2, 2, n_rows),
        'status': np.random.choice(['Active', 'Inactive', 'Pending'], n_rows)
    }
    
    df = pd.DataFrame(data)
    
    # 添加一些缺失值
    df.loc[np.random.choice(df.index, 20, replace=False), 'income'] = np.nan
    df.loc[np.random.choice(df.index, 10, replace=False), 'score'] = np.nan
    
    return df

def simulate_frontend_request(question, df, timeout_seconds=180):
    """模拟前端发送的AI洞察请求"""
    
    # 准备数据上下文（模拟前端generate_ai_insight函数的逻辑）
    data_context = {
        'shape': list(df.shape),
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
    }
    
    # 模拟聊天历史
    chat_history = []
    
    # 准备请求数据
    request_data = {
        'question': question,
        'data_context': data_context,
        'chat_history': chat_history
    }
    
    backend_url = "http://localhost:7701/api/ai/chat"
    
    print(f"📤 发送请求: {question[:50]}...")
    print(f"⏱️ 超时设置: {timeout_seconds}秒")
    print(f"📊 数据规模: {df.shape[0]}行 x {df.shape[1]}列")
    
    start_time = time.time()
    
    try:
        response = requests.post(backend_url, json=request_data, timeout=timeout_seconds)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 请求完成")
        print(f"⏱️ 响应时间: {duration:.2f}秒")
        print(f"📈 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"💬 AI响应长度: {len(result.get('response', ''))}字符")
                if result.get('chart'):
                    print(f"📊 包含图表数据")
                return True, duration, "成功"
            else:
                error_msg = result.get('error', '未知错误')
                print(f"❌ API返回失败: {error_msg}")
                return False, duration, f"API错误: {error_msg}"
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False, duration, f"HTTP错误: {response.status_code}"
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏰ 请求超时 ({timeout_seconds}秒)")
        print(f"⏱️ 实际耗时: {duration:.2f}秒")
        return False, duration, "超时"
        
    except requests.exceptions.ConnectionError:
        end_time = time.time()
        duration = end_time - start_time
        print(f"🔌 连接错误")
        return False, duration, "连接错误"
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"💥 其他错误: {str(e)}")
        return False, duration, f"其他错误: {str(e)}"

def test_different_scenarios():
    """测试不同的使用场景"""
    print("=== 端到端测试：不同使用场景 ===")
    print(f"🕐 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试数据
    df = create_test_data()
    print(f"📊 测试数据创建完成: {df.shape[0]}行 x {df.shape[1]}列")
    
    # 定义测试场景
    test_scenarios = [
        {
            'name': '简单数据概览',
            'question': '请分析这个数据集的基本统计信息',
            'expected_time': 10
        },
        {
            'name': '复杂数据分析',
            'question': '请深入分析年龄、收入和评分之间的关系，并生成相应的可视化图表，包括散点图、相关性热力图和分布直方图',
            'expected_time': 15
        },
        {
            'name': '多维度分析',
            'question': '请按地区和类别分析收入分布情况，识别异常值，并提供详细的统计洞察和业务建议',
            'expected_time': 20
        },
        {
            'name': '综合报告生成',
            'question': '请生成一份完整的数据分析报告，包括数据质量评估、趋势分析、异常检测、相关性分析和业务洞察，并为每个发现生成相应的可视化图表',
            'expected_time': 30
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"📋 测试场景 {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"❓ 问题: {scenario['question']}")
        print(f"⏱️ 预期时间: {scenario['expected_time']}秒")
        print(f"{'='*60}")
        
        success, duration, error_msg = simulate_frontend_request(
            scenario['question'], 
            df, 
            timeout_seconds=180  # 使用修复后的超时时间
        )
        
        result = {
            'scenario': scenario['name'],
            'success': success,
            'duration': duration,
            'expected_time': scenario['expected_time'],
            'error_msg': error_msg,
            'timeout_setting': 180
        }
        
        results.append(result)
        
        # 分析结果
        if success:
            if duration <= scenario['expected_time']:
                print(f"🎉 测试通过 - 响应时间优秀 ({duration:.2f}s <= {scenario['expected_time']}s)")
            elif duration <= 60:
                print(f"✅ 测试通过 - 响应时间良好 ({duration:.2f}s)")
            elif duration <= 120:
                print(f"⚠️ 测试通过 - 响应时间较慢 ({duration:.2f}s)")
            else:
                print(f"🐌 测试通过 - 响应时间很慢 ({duration:.2f}s)")
        else:
            print(f"❌ 测试失败 - {error_msg}")
        
        # 等待一下再进行下一个测试
        if i < len(test_scenarios):
            print("⏳ 等待5秒后进行下一个测试...")
            time.sleep(5)
    
    return results

def generate_test_report(results):
    """生成测试报告"""
    print(f"\n{'='*80}")
    print("📊 测试报告")
    print(f"{'='*80}")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"📈 总体统计:")
    print(f"   总测试数: {total_tests}")
    print(f"   成功: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"   失败: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    
    if successful_tests > 0:
        successful_durations = [r['duration'] for r in results if r['success']]
        avg_duration = sum(successful_durations) / len(successful_durations)
        max_duration = max(successful_durations)
        min_duration = min(successful_durations)
        
        print(f"\n⏱️ 响应时间统计 (成功的请求):")
        print(f"   平均响应时间: {avg_duration:.2f}秒")
        print(f"   最快响应时间: {min_duration:.2f}秒")
        print(f"   最慢响应时间: {max_duration:.2f}秒")
        
        # 检查是否还有60秒超时问题
        timeout_issues = [r for r in results if not r['success'] and '60' in r['error_msg']]
        if timeout_issues:
            print(f"\n⚠️ 发现60秒超时问题:")
            for issue in timeout_issues:
                print(f"   - {issue['scenario']}: {issue['error_msg']}")
        else:
            print(f"\n✅ 未发现60秒超时问题")
    
    print(f"\n📋 详细结果:")
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"   {i}. {status} {result['scenario']}")
        print(f"      响应时间: {result['duration']:.2f}s")
        if not result['success']:
            print(f"      错误: {result['error_msg']}")
    
    # 修复效果评估
    print(f"\n🔧 修复效果评估:")
    if failed_tests == 0:
        print(f"   🎉 完美！所有测试都通过了")
    elif successful_tests >= total_tests * 0.8:
        print(f"   ✅ 良好！大部分测试通过，修复基本有效")
    elif successful_tests >= total_tests * 0.5:
        print(f"   ⚠️ 一般！部分测试通过，需要进一步优化")
    else:
        print(f"   ❌ 较差！大部分测试失败，需要重新检查修复方案")
    
    # 建议
    print(f"\n💡 建议:")
    if successful_tests == total_tests:
        print(f"   - 修复成功！用户应该不再遇到60秒超时问题")
        print(f"   - 建议监控生产环境的实际使用情况")
    else:
        print(f"   - 考虑进一步增加超时时间")
        print(f"   - 优化后端AI处理逻辑")
        print(f"   - 添加请求取消和重试机制")
        print(f"   - 考虑使用流式响应")

def main():
    """主测试函数"""
    print("前端AI洞察功能 - 端到端测试")
    print("=" * 80)
    
    # 检查后端服务是否可用
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        print("请确保后端服务正在运行 (http://localhost:7701)")
        return
    
    # 运行测试
    results = test_different_scenarios()
    
    # 生成报告
    generate_test_report(results)
    
    print(f"\n🕐 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()