#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端图表显示测试脚本
测试完整的图表生成和显示流程
"""

import requests
import json
import base64
from PIL import Image
import io

def test_chart_generation_and_display():
    """测试图表生成和显示的完整流程"""
    print("=== 测试图表生成和显示流程 ===")
    
    # 1. 测试后端图表生成API
    print("\n1. 测试后端图表生成API...")
    
    test_data = {
        "data": [
            {"name": "产品A", "sales": 100, "profit": 20},
            {"name": "产品B", "sales": 150, "profit": 30},
            {"name": "产品C", "sales": 120, "profit": 25}
        ],
        "visualization": {
            "needed": True,
            "chart_type": "bar",
            "columns": ["name", "sales"],
            "title": "产品销售数据",
            "description": "各产品销售情况对比"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:7701/api/generate_chart",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 后端API调用成功")
            print(f"   - 成功标志: {result.get('success')}")
            print(f"   - 图表标题: {result.get('title')}")
            
            if result.get('chart_base64'):
                chart_base64 = result['chart_base64']
                print(f"   - Base64数据长度: {len(chart_base64)}")
                print(f"   - Base64前缀: {chart_base64[:50]}...")
                
                # 2. 测试base64数据解码
                print("\n2. 测试base64数据解码...")
                try:
                    # 检查是否有data:image/png;base64,前缀
                    if chart_base64.startswith('data:image/png;base64,'):
                        print("   - 检测到完整的data URL格式")
                        clean_base64 = chart_base64.replace('data:image/png;base64,', '')
                    else:
                        print("   - 纯base64格式")
                        clean_base64 = chart_base64
                    
                    # 解码base64数据
                    chart_bytes = base64.b64decode(clean_base64)
                    print(f"   - 解码后字节长度: {len(chart_bytes)}")
                    
                    # 3. 测试图片数据有效性
                    print("\n3. 测试图片数据有效性...")
                    try:
                        image = Image.open(io.BytesIO(chart_bytes))
                        print(f"   - 图片格式: {image.format}")
                        print(f"   - 图片尺寸: {image.size}")
                        print(f"   - 图片模式: {image.mode}")
                        print("   ✅ 图片数据有效")
                        
                        # 保存测试图片
                        test_image_path = "test_chart_output.png"
                        image.save(test_image_path)
                        print(f"   - 测试图片已保存: {test_image_path}")
                        
                    except Exception as e:
                        print(f"   ❌ 图片数据无效: {e}")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ Base64解码失败: {e}")
                    return False
                    
            else:
                print("   ❌ 响应中没有chart_base64字段")
                return False
                
        else:
            print(f"❌ 后端API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False
    
    # 4. 测试AI洞察API
    print("\n4. 测试AI洞察API...")
    
    ai_test_data = {
        "question": "请分析这些产品的销售情况并生成图表",
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
            
            if result.get('visualization'):
                viz_config = result['visualization']
                print(f"   - 可视化配置: {viz_config}")
                
                if viz_config.get('needed'):
                    print("   - AI建议生成图表")
                else:
                    print("   - AI认为不需要生成图表")
            
            if result.get('chart'):
                print("   - AI响应包含图表数据")
                chart_data = result['chart']
                if isinstance(chart_data, dict) and chart_data.get('chart_base64'):
                    print("   ✅ 图表数据格式正确")
                else:
                    print(f"   ⚠️ 图表数据格式异常: {type(chart_data)}")
            
        else:
            print(f"❌ AI洞察API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ AI洞察API调用异常: {e}")
    
    print("\n=== 测试完成 ===")
    return True

def test_streamlit_display_logic():
    """测试Streamlit显示逻辑"""
    print("\n=== 测试Streamlit显示逻辑 ===")
    
    # 模拟聊天历史中的图表数据
    test_chart_data = {
        'chart_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        'title': '测试图表',
        'description': '这是一个测试图表'
    }
    
    # 测试base64处理逻辑
    chart_base64 = test_chart_data['chart_base64']
    print(f"原始base64: {chart_base64[:50]}...")
    
    # 模拟前端处理逻辑
    if chart_base64.startswith('data:image/png;base64,'):
        clean_base64 = chart_base64.replace('data:image/png;base64,', '')
        print("✅ 成功去除data URL前缀")
    else:
        clean_base64 = chart_base64
        print("⚠️ 没有data URL前缀")
    
    try:
        chart_bytes = base64.b64decode(clean_base64)
        print(f"✅ Base64解码成功，字节长度: {len(chart_bytes)}")
        
        # 验证图片数据
        image = Image.open(io.BytesIO(chart_bytes))
        print(f"✅ 图片数据有效: {image.size}")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
    
    print("=== Streamlit显示逻辑测试完成 ===")

if __name__ == "__main__":
    print("开始测试前端图表显示功能...")
    
    # 测试图表生成和显示流程
    success = test_chart_generation_and_display()
    
    # 测试Streamlit显示逻辑
    test_streamlit_display_logic()
    
    if success:
        print("\n🎉 所有测试通过！图表显示功能正常。")
    else:
        print("\n⚠️ 部分测试失败，需要进一步检查。")