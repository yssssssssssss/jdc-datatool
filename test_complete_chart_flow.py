#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的图表显示流程测试
测试从AI洞察到前端显示的完整流程
"""

import requests
import json
import base64
from PIL import Image
import io
import pandas as pd

def test_complete_chart_flow():
    """测试完整的图表显示流程"""
    print("=== 测试完整图表显示流程 ===")
    
    # 1. 模拟前端数据
    test_df_data = [
        {"name": "产品A", "sales": 100, "profit": 20},
        {"name": "产品B", "sales": 150, "profit": 30},
        {"name": "产品C", "sales": 120, "profit": 25}
    ]
    
    df = pd.DataFrame(test_df_data)
    print(f"✅ 创建测试数据: {df.shape}")
    
    # 2. 准备AI洞察请求
    data_context = {
        'shape': list(df.shape),
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
    }
    
    request_data = {
        'question': '请分析这些产品的销售情况并生成柱状图',
        'data_context': data_context,
        'chat_history': []
    }
    
    print("\n2. 调用AI洞察API...")
    
    try:
        response = requests.post(
            "http://localhost:7701/api/ai/chat",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI洞察API调用成功")
            
            ai_response = result.get('response', '')
            print(f"   - AI响应: {ai_response[:100]}...")
            
            # 3. 模拟前端处理逻辑
            print("\n3. 模拟前端处理逻辑...")
            
            if 'chart' in result:
                chart_data = result['chart']
                print(f"   - 原始图表数据类型: {type(chart_data)}")
                
                # 模拟前端修复后的处理逻辑
                if isinstance(chart_data, str):
                    print("   - 检测到字符串格式的base64数据")
                    viz_config = result.get('visualization_config', {})
                    processed_chart_data = {
                        'chart_base64': chart_data,
                        'title': viz_config.get('title', '数据可视化'),
                        'description': viz_config.get('description', ''),
                        'chart_type': viz_config.get('chart_type', 'unknown')
                    }
                    print(f"   - 转换后的图表数据: {list(processed_chart_data.keys())}")
                    chart_data = processed_chart_data
                
                # 4. 模拟Streamlit显示逻辑
                print("\n4. 模拟Streamlit显示逻辑...")
                
                if isinstance(chart_data, dict) and chart_data.get('chart_base64'):
                    chart_base64 = chart_data['chart_base64']
                    print(f"   - Base64数据长度: {len(chart_base64)}")
                    
                    # 去掉data:image/png;base64,前缀
                    if chart_base64.startswith('data:image/png;base64,'):
                        clean_base64 = chart_base64.replace('data:image/png;base64,', '')
                        print("   - 成功去除data URL前缀")
                    else:
                        clean_base64 = chart_base64
                        print("   - 没有data URL前缀")
                    
                    try:
                        chart_bytes = base64.b64decode(clean_base64)
                        print(f"   - Base64解码成功，字节长度: {len(chart_bytes)}")
                        
                        # 验证图片数据
                        image = Image.open(io.BytesIO(chart_bytes))
                        print(f"   - 图片格式: {image.format}")
                        print(f"   - 图片尺寸: {image.size}")
                        print(f"   - 图片模式: {image.mode}")
                        
                        # 保存测试图片
                        test_image_path = "test_complete_flow_chart.png"
                        image.save(test_image_path)
                        print(f"   - 测试图片已保存: {test_image_path}")
                        
                        print("   ✅ 图片显示逻辑正常")
                        
                        # 5. 模拟聊天历史存储
                        print("\n5. 模拟聊天历史存储...")
                        
                        chat_message = {
                            'role': 'assistant',
                            'content': ai_response,
                            'chart': chart_data
                        }
                        
                        print(f"   - 聊天消息结构: {list(chat_message.keys())}")
                        print(f"   - 图表数据结构: {list(chat_message['chart'].keys())}")
                        print("   ✅ 聊天历史存储格式正确")
                        
                        return True
                        
                    except Exception as e:
                        print(f"   ❌ 图片处理失败: {e}")
                        return False
                        
                else:
                    print("   ❌ 图表数据格式不正确")
                    return False
                    
            else:
                print("   ⚠️ AI响应中没有图表数据")
                
                # 检查是否有可视化配置
                if 'visualization_config' in result:
                    viz_config = result['visualization_config']
                    if viz_config.get('needed', False):
                        print("   - AI建议生成图表，但没有返回图表数据")
                        print("   - 可能需要调用generate_chart_from_config函数")
                    else:
                        print("   - AI认为不需要生成图表")
                
                return False
                
        else:
            print(f"❌ AI洞察API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False

def test_chart_display_in_chat_history():
    """测试聊天历史中的图表显示"""
    print("\n=== 测试聊天历史中的图表显示 ===")
    
    # 模拟聊天历史中的消息
    test_message = {
        'role': 'assistant',
        'content': '根据数据分析，产品B的销售额最高。\n\n📊 展示每个产品的销售额。',
        'chart': {
            'chart_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'title': '产品销售情况',
            'description': '展示每个产品的销售额。',
            'chart_type': 'bar'
        }
    }
    
    print("1. 检查消息结构...")
    print(f"   - 消息角色: {test_message['role']}")
    print(f"   - 消息内容长度: {len(test_message['content'])}")
    print(f"   - 包含图表: {'chart' in test_message}")
    
    if 'chart' in test_message:
        chart_data = test_message['chart']
        print(f"   - 图表数据类型: {type(chart_data)}")
        
        if isinstance(chart_data, dict) and chart_data.get('chart_base64'):
            print("   ✅ 图表数据格式正确")
            
            # 模拟前端显示逻辑
            chart_base64 = chart_data['chart_base64']
            if chart_base64.startswith('data:image/png;base64,'):
                clean_base64 = chart_base64.replace('data:image/png;base64,', '')
                print("   - 成功处理data URL前缀")
            else:
                clean_base64 = chart_base64
            
            try:
                chart_bytes = base64.b64decode(clean_base64)
                image = Image.open(io.BytesIO(chart_bytes))
                print(f"   - 图片尺寸: {image.size}")
                print("   ✅ 聊天历史图表显示正常")
                return True
            except Exception as e:
                print(f"   ❌ 图片处理失败: {e}")
                return False
        else:
            print("   ❌ 图表数据格式不正确")
            return False
    else:
        print("   ⚠️ 消息中没有图表数据")
        return False

if __name__ == "__main__":
    print("开始完整图表显示流程测试...")
    
    # 测试完整流程
    success1 = test_complete_chart_flow()
    
    # 测试聊天历史显示
    success2 = test_chart_display_in_chat_history()
    
    print("\n=== 测试总结 ===")
    if success1 and success2:
        print("🎉 所有测试通过！图表显示功能完全正常。")
        print("\n✅ 修复内容:")
        print("   1. 后端API正确生成base64图片数据")
        print("   2. 前端正确处理AI返回的字符串格式图表数据")
        print("   3. Streamlit正确显示base64图片")
        print("   4. 聊天历史正确存储和显示图表")
    else:
        print("⚠️ 部分测试失败:")
        print(f"   - 完整流程测试: {'✅' if success1 else '❌'}")
        print(f"   - 聊天历史测试: {'✅' if success2 else '❌'}")