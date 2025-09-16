#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多库可视化API
"""

import requests
import json

def test_multi_lib_api():
    """测试多库可视化API"""
    base_url = "http://localhost:7701"
    
    print("🔍 测试多库可视化API...")
    
    # 1. 测试获取适配器列表
    print("\n1. 测试获取适配器列表")
    try:
        response = requests.get(f"{base_url}/api/multi_lib/adapters")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            adapters = response.json()
            print(f"可用适配器: {json.dumps(adapters, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取图表类型
    print("\n2. 测试获取图表类型")
    try:
        response = requests.get(f"{base_url}/api/multi_lib/chart_types", 
                              params={'adapter': 'echarts'})
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            chart_types = response.json()
            print(f"ECharts支持的图表类型: {json.dumps(chart_types, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试生成图表
    print("\n3. 测试生成图表")
    try:
        test_data = {
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        }
        
        payload = {
            'adapter_name': 'echarts',
            'chart_type': 'line',
            'data': test_data,
            'config': {
                'title': 'Test Line Chart',
                'width': 800,
                'height': 600
            }
        }
        
        response = requests.post(f"{base_url}/api/multi_lib/generate_chart", 
                               json=payload)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"图表生成成功: {result.get('success', False)}")
            if 'performance' in result:
                perf = result['performance']
                print(f"性能指标: 渲染时间={perf.get('render_time', 0):.3f}s, "
                      f"文件大小={perf.get('file_size', 0):.2f}KB")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_multi_lib_api()