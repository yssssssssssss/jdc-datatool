#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI洞察API返回的图表数据格式
"""

import requests
import json

def test_ai_chart_response():
    """测试AI洞察API返回的图表数据格式"""
    print("=== 测试AI洞察API图表数据格式 ===")
    
    ai_test_data = {
        "question": "请分析这些产品的销售情况并生成柱状图",
        "data_context": {
            "shape": [3, 3],
            "columns": ["name", "sales", "profit"],
            "dtypes": {"name": "object", "sales": "int64", "profit": "int64"},
            "missing_values": {"name": 0, "sales": 0, "profit": 0},
            "numeric_columns": ["sales", "profit"],
            "categorical_columns": ["name"]
        },
        "chat_history": []
    }
    
    try:
        response = requests.post(
            "http://localhost:7701/api/ai/chat",
            json=ai_test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI洞察API调用成功")
            print(f"   - 成功标志: {result.get('success')}")
            print(f"   - 响应类型: {type(result.get('response'))}")
            
            # 检查可视化配置
            if 'visualization' in result:
                viz_config = result['visualization']
                print(f"   - 可视化配置: {viz_config}")
                print(f"   - 需要生成图表: {viz_config.get('needed', False)}")
            
            # 检查图表数据
            if 'chart' in result:
                chart_data = result['chart']
                print(f"   - 图表数据类型: {type(chart_data)}")
                
                if isinstance(chart_data, dict):
                    print(f"   - 图表数据字段: {list(chart_data.keys())}")
                    if 'chart_base64' in chart_data:
                        base64_data = chart_data['chart_base64']
                        print(f"   - Base64数据长度: {len(base64_data)}")
                        print(f"   - Base64前缀: {base64_data[:50]}...")
                        print("   ✅ 图表数据格式正确")
                    else:
                        print("   ❌ 缺少chart_base64字段")
                elif isinstance(chart_data, str):
                    print(f"   - 图表数据内容: {chart_data[:200]}...")
                    print("   ⚠️ 图表数据是字符串格式，可能需要解析")
                else:
                    print(f"   ❌ 未知的图表数据格式: {chart_data}")
            else:
                print("   ⚠️ 响应中没有图表数据")
            
            # 打印完整响应以便调试
            print("\n=== 完整响应内容 ===")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ AI洞察API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ AI洞察API调用异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_ai_chart_response()