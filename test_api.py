import requests
import json
import time

def test_ai_chat_api():
    """测试AI聊天API"""
    url = 'http://localhost:7701/api/ai/chat'
    data = {
        'question': '请分析这个数据集的基本统计信息',
        'data_context': {
            'shape': [100, 5],
            'columns': ['A', 'B', 'C', 'D', 'E'],
            'numeric_columns': ['A', 'B', 'C'],
            'categorical_columns': ['D', 'E']
        },
        'chat_history': []
    }
    
    print("开始测试AI聊天API...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=data, timeout=180)
        end_time = time.time()
        
        print(f"请求耗时: {end_time - start_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"请求成功: {result.get('success')}")
            print(f"响应内容: {result.get('response', '')[:300]}...")
            if result.get('chart'):
                print("生成了图表")
        else:
            print(f"请求失败: {response.text}")
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        print(f"请求超时，耗时: {end_time - start_time:.2f}秒")
    except Exception as e:
        end_time = time.time()
        print(f"请求异常，耗时: {end_time - start_time:.2f}秒，错误: {str(e)}")

if __name__ == '__main__':
    test_ai_chat_api()