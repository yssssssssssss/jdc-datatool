#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表显示测试脚本
测试后端base64图片生成和前端显示逻辑
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image
import pandas as pd

def test_backend_chart_generation():
    """测试后端图表生成API"""
    print("=== 测试后端图表生成 ===")
    
    # 测试数据
    test_data = {
        "chart_type": "bar",
        "data": {
            "categories": ["A", "B", "C", "D"],
            "values": [10, 20, 15, 25]
        },
        "config": {
            "title": "测试柱状图",
            "x_label": "类别",
            "y_label": "数值"
        }
    }
    
    try:
        # 调用后端API
        response = requests.post(
            "http://localhost:7701/api/generate_chart",
            json=test_data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据键: {list(result.keys())}")
            
            if 'chart_data' in result:
                chart_data = result['chart_data']
                print(f"图表数据类型: {type(chart_data)}")
                print(f"图表数据长度: {len(chart_data) if chart_data else 0}")
                
                # 检查base64格式
                if chart_data and chart_data.startswith('data:image/'):
                    print("✓ 图表数据格式正确 (data:image/...)")
                    
                    # 提取base64数据
                    base64_data = chart_data.split(',')[1]
                    print(f"Base64数据长度: {len(base64_data)}")
                    
                    # 验证base64数据是否可以解码为图片
                    try:
                        image_data = base64.b64decode(base64_data)
                        image = Image.open(BytesIO(image_data))
                        print(f"✓ 图片解码成功: {image.size} {image.format}")
                        return True, chart_data
                    except Exception as e:
                        print(f"✗ 图片解码失败: {e}")
                        return False, None
                else:
                    print(f"✗ 图表数据格式错误: {chart_data[:100] if chart_data else 'None'}...")
                    return False, None
            else:
                print("✗ 响应中没有chart_data字段")
                return False, None
        else:
            print(f"✗ API调用失败: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        return False, None

def test_ai_insight_chart():
    """测试AI洞察图表生成"""
    print("\n=== 测试AI洞察图表生成 ===")
    
    # 模拟数据上下文
    data_context = {
        "columns": ["销售额", "月份", "产品类别"],
        "data_types": {"销售额": "numeric", "月份": "categorical", "产品类别": "categorical"},
        "sample_data": [
            {"销售额": 1000, "月份": "1月", "产品类别": "电子产品"},
            {"销售额": 1200, "月份": "2月", "产品类别": "服装"},
            {"销售额": 800, "月份": "3月", "产品类别": "食品"}
        ]
    }
    
    test_data = {
        "question": "显示各月份的销售额趋势",
        "data_context": data_context
    }
    
    try:
        response = requests.post(
            "http://localhost:7701/api/ai/chat",
            json=test_data,
            timeout=60
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据键: {list(result.keys())}")
            
            if 'chart_data' in result and result['chart_data']:
                chart_data = result['chart_data']
                print(f"✓ AI生成图表数据: {len(chart_data)} 字符")
                
                # 检查格式
                if chart_data.startswith('data:image/'):
                    print("✓ AI图表数据格式正确")
                    return True, chart_data
                else:
                    print(f"✗ AI图表数据格式错误: {chart_data[:100]}...")
                    return False, None
            else:
                print("AI响应中没有图表数据")
                return True, None  # 可能只是文本回答
        else:
            print(f"✗ AI API调用失败: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"✗ AI请求异常: {e}")
        return False, None

def save_test_image(chart_data, filename):
    """保存测试图片到文件"""
    if chart_data and chart_data.startswith('data:image/'):
        try:
            base64_data = chart_data.split(',')[1]
            image_data = base64.b64decode(base64_data)
            
            with open(filename, 'wb') as f:
                f.write(image_data)
            print(f"✓ 测试图片已保存: {filename}")
            return True
        except Exception as e:
            print(f"✗ 保存图片失败: {e}")
            return False
    return False

def main():
    """主测试函数"""
    print("开始图表显示测试...\n")
    
    # 测试1: 后端图表生成
    success1, chart_data1 = test_backend_chart_generation()
    if success1 and chart_data1:
        save_test_image(chart_data1, "test_chart_backend.png")
    
    # 测试2: AI洞察图表生成
    success2, chart_data2 = test_ai_insight_chart()
    if success2 and chart_data2:
        save_test_image(chart_data2, "test_chart_ai.png")
    
    # 总结
    print("\n=== 测试总结 ===")
    print(f"后端图表生成: {'✓ 通过' if success1 else '✗ 失败'}")
    print(f"AI洞察图表生成: {'✓ 通过' if success2 else '✗ 失败'}")
    
    if success1 or success2:
        print("\n建议检查前端Streamlit显示逻辑:")
        print("1. 确认st.image()正确处理base64数据")
        print("2. 检查图片显示的容器和布局")
        print("3. 验证浏览器控制台是否有错误")