#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI图表显示功能
验证AI能否正确生成并显示图表
"""

import requests
import json
import pandas as pd

def test_ai_chart_display():
    """测试AI图表显示功能"""
    print("🧪 测试AI图表显示功能...")
    
    # 模拟数据
    test_data = {
        'age': [25, 30, 35, 40, 45, 50, 55, 60],
        'salary': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000],
        'department': ['IT', 'HR', 'Finance', 'IT', 'HR', 'Finance', 'IT', 'HR']
    }
    
    df = pd.DataFrame(test_data)
    
    # 准备数据上下文
    data_context = {
        'shape': list(df.shape),
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
    }
    
    # 测试问题
    test_questions = [
        "分析年龄和薪资的关系，并生成散点图",
        "显示薪资分布情况",
        "创建部门薪资对比图表"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试问题 {i}: {question}")
        
        # 调用AI聊天API
        try:
            response = requests.post(
                'http://localhost:7701/api/ai/chat',
                json={
                    'question': question,
                    'data_context': data_context,
                    'chat_history': []
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ AI响应成功")
                    print(f"📄 响应内容: {result['response'][:100]}...")
                    
                    # 检查是否有可视化配置
                    viz_config = result.get('visualization', {})
                    if viz_config.get('needed', False):
                        print(f"📊 推荐图表类型: {viz_config.get('chart_type', 'N/A')}")
                        print(f"📋 图表标题: {viz_config.get('title', 'N/A')}")
                        
                        # 测试图表生成
                        chart_response = requests.post(
                            'http://localhost:7701/api/generate_chart',
                            json={
                                'data': df.to_dict('records'),
                                'visualization': viz_config
                            },
                            timeout=30
                        )
                        
                        if chart_response.status_code == 200:
                            chart_result = chart_response.json()
                            if chart_result.get('success'):
                                print(f"🎨 图表生成成功: {chart_result.get('title', 'N/A')}")
                                print(f"📏 图表数据大小: {len(chart_result.get('chart_base64', ''))} 字符")
                            else:
                                print(f"❌ 图表生成失败: {chart_result.get('error', 'Unknown error')}")
                        else:
                            print(f"❌ 图表生成API调用失败: {chart_response.status_code}")
                    else:
                        print("ℹ️ AI未推荐生成图表")
                else:
                    print(f"❌ AI分析失败: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print("\n🎉 测试完成！")

if __name__ == '__main__':
    test_ai_chart_display()