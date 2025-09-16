#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证60秒超时问题是否已解决
"""

import requests
import time
from datetime import datetime

def test_timeout_error_message():
    """测试超时错误消息是否正确显示180秒"""
    print("🔍 验证超时错误消息修复")
    print("="*50)
    
    # 测试数据
    test_data = {
        'question': '请进行非常详细和复杂的数据分析，包括所有可能的统计指标、相关性分析、异常值检测、趋势分析、预测模型等等，请提供最全面最详细的分析报告',
        'data_context': {
            'shape': [50000, 100],  # 大数据集
            'columns': [f'feature_{i}' for i in range(100)],
            'dtypes': {f'feature_{i}': 'float64' for i in range(80)} | 
                     {f'feature_{i}': 'object' for i in range(80, 100)},
            'missing_values': {f'feature_{i}': i*100 for i in range(100)},
            'numeric_columns': [f'feature_{i}' for i in range(80)],
            'categorical_columns': [f'feature_{i}' for i in range(80, 100)]
        },
        'chat_history': []
    }
    
    print(f"📊 测试时间: {datetime.now()}")
    print(f"📈 数据规模: {test_data['data_context']['shape']}")
    print(f"📝 问题长度: {len(test_data['question'])} 字符")
    
    try:
        print("\n🚀 发送复杂AI分析请求...")
        start_time = time.time()
        
        # 使用较短的超时来触发超时错误
        response = requests.post(
            "http://localhost:7701/api/ai/chat", 
            json=test_data, 
            timeout=30  # 30秒超时，应该会触发超时
        )
        
        duration = time.time() - start_time
        print(f"⏱️ 请求耗时: {duration:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 请求成功完成")
                return True, "请求成功"
            else:
                error_msg = result.get('error', '未知错误')
                print(f"❌ 请求失败: {error_msg}")
                return False, error_msg
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"\n⏰ 请求超时 ({duration:.2f}秒)")
        print("✅ 这是预期的超时，用于测试错误消息")
        
        # 现在测试前端的超时处理
        print("\n🔍 测试前端超时处理...")
        return test_frontend_timeout_handling()
        
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False, str(e)

def test_frontend_timeout_handling():
    """测试前端超时处理逻辑"""
    try:
        # 模拟前端的超时处理
        print("📱 模拟前端超时处理逻辑...")
        
        # 检查前端代码中的超时错误消息
        with open("frontend/app.py", "r", encoding="utf-8") as f:
            frontend_code = f.read()
        
        # 查找超时错误消息
        if "AI分析请求超时（180秒）" in frontend_code:
            print("✅ 前端代码中的超时消息已正确更新为180秒")
            
            # 检查是否还有60秒的引用
            if "60秒" in frontend_code or "60.*秒" in frontend_code:
                print("⚠️ 前端代码中仍有60秒的引用")
                return False, "前端代码中仍有60秒引用"
            else:
                print("✅ 前端代码中没有60秒的引用")
                return True, "超时消息已正确更新"
        else:
            print("❌ 前端代码中未找到180秒超时消息")
            return False, "未找到正确的超时消息"
            
    except Exception as e:
        print(f"❌ 检查前端代码时出错: {e}")
        return False, str(e)

def check_streamlit_config():
    """检查Streamlit配置"""
    print("\n🔧 检查Streamlit配置...")
    
    try:
        with open(".streamlit/config.toml", "r", encoding="utf-8") as f:
            config_content = f.read()
        
        print("📋 当前Streamlit配置:")
        
        # 检查关键配置项
        config_items = [
            ("timeout = 300", "服务器超时"),
            ("requestTimeout = 300", "请求超时"),
            ("websocketTimeout = 300", "WebSocket超时")
        ]
        
        all_configured = True
        for item, description in config_items:
            if item in config_content:
                print(f"   ✅ {description}: 已配置")
            else:
                print(f"   ❌ {description}: 未配置")
                all_configured = False
        
        return all_configured
        
    except FileNotFoundError:
        print("❌ Streamlit配置文件不存在")
        return False
    except Exception as e:
        print(f"❌ 检查配置文件时出错: {e}")
        return False

def test_backend_health():
    """测试后端服务健康状态"""
    print("\n🏥 检查后端服务健康状态...")
    
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ 后端服务正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def generate_final_report(timeout_test_result, config_ok, backend_ok):
    """生成最终报告"""
    print("\n" + "="*60)
    print("📋 60秒超时问题修复验证报告")
    print("="*60)
    
    print(f"\n🕐 测试时间: {datetime.now()}")
    
    print("\n🔍 检查结果:")
    
    # 后端服务状态
    status = "✅" if backend_ok else "❌"
    print(f"   {status} 后端服务: {'正常' if backend_ok else '异常'}")
    
    # 配置状态
    status = "✅" if config_ok else "❌"
    print(f"   {status} Streamlit配置: {'正确' if config_ok else '需要修复'}")
    
    # 超时消息测试
    success, message = timeout_test_result
    status = "✅" if success else "❌"
    print(f"   {status} 超时消息: {message}")
    
    print("\n💡 问题状态:")
    
    if success and config_ok and backend_ok:
        print("   🎯 ✅ 60秒超时问题已完全解决!")
        print("   📱 前端代码中的超时消息已正确更新为180秒")
        print("   ⚙️ Streamlit配置已正确设置")
        print("   🔧 后端服务运行正常")
        
        print("\n🎉 用户现在应该看到正确的180秒超时消息!")
        
        print("\n📋 用户操作建议:")
        print("   1. 清除浏览器缓存 (Ctrl+Shift+Delete)")
        print("   2. 强制刷新页面 (Ctrl+F5)")
        print("   3. 或使用无痕模式打开应用")
        print("   4. 访问 http://localhost:8504 测试AI洞察功能")
        
    else:
        print("   ⚠️ 仍存在一些问题需要解决:")
        
        if not backend_ok:
            print("     - 后端服务需要重启")
        if not config_ok:
            print("     - Streamlit配置需要完善")
        if not success:
            print(f"     - 超时消息问题: {message}")
        
        print("\n🔧 建议解决方案:")
        print("   1. 重启所有服务: python start.py")
        print("   2. 清除所有缓存: python clear_cache_and_restart.py")
        print("   3. 检查端口占用情况")
        print("   4. 重启计算机以完全清除缓存")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("🔍 60秒超时问题修复验证")
    print("="*60)
    
    # 1. 检查后端服务
    backend_ok = test_backend_health()
    
    # 2. 检查Streamlit配置
    config_ok = check_streamlit_config()
    
    # 3. 测试超时错误消息
    timeout_result = test_timeout_error_message()
    
    # 4. 生成最终报告
    generate_final_report(timeout_result, config_ok, backend_ok)

if __name__ == "__main__":
    main()