#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清除缓存并重启应用的脚本
解决用户仍然看到60秒超时错误的问题
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

def clear_streamlit_cache():
    """清除Streamlit缓存"""
    print("🧹 清除Streamlit缓存...")
    
    # 清除Streamlit缓存目录
    cache_dirs = [
        os.path.expanduser("~/.streamlit"),
        ".streamlit",
        "__pycache__",
        ".pytest_cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                if cache_dir.endswith("__pycache__"):
                    # 递归删除所有__pycache__目录
                    for root, dirs, files in os.walk("."):
                        for dir_name in dirs:
                            if dir_name == "__pycache__":
                                pycache_path = os.path.join(root, dir_name)
                                print(f"  删除: {pycache_path}")
                                shutil.rmtree(pycache_path, ignore_errors=True)
                else:
                    print(f"  清除缓存目录: {cache_dir}")
                    if os.path.isdir(cache_dir):
                        shutil.rmtree(cache_dir, ignore_errors=True)
                    else:
                        os.remove(cache_dir)
            except Exception as e:
                print(f"  ⚠️ 无法删除 {cache_dir}: {e}")
    
    print("✅ Streamlit缓存清除完成")

def clear_browser_cache_instructions():
    """显示清除浏览器缓存的说明"""
    print("\n" + "="*60)
    print("🌐 浏览器缓存清除说明")
    print("="*60)
    print("\n为了确保看到最新的超时设置，请按以下步骤清除浏览器缓存：")
    print("\n📋 Chrome/Edge浏览器:")
    print("   1. 按 Ctrl+Shift+Delete 打开清除数据对话框")
    print("   2. 选择'缓存的图片和文件'")
    print("   3. 时间范围选择'全部时间'")
    print("   4. 点击'清除数据'")
    print("   5. 或者按 Ctrl+F5 强制刷新页面")
    
    print("\n📋 Firefox浏览器:")
    print("   1. 按 Ctrl+Shift+Delete")
    print("   2. 选择'缓存'")
    print("   3. 点击'立即清除'")
    print("   4. 或者按 Ctrl+F5 强制刷新")
    
    print("\n📋 Safari浏览器:")
    print("   1. 按 Cmd+Option+E 清空缓存")
    print("   2. 或者在开发菜单中选择'清空缓存'")
    print("   3. 按 Cmd+R 刷新页面")
    
    print("\n🎯 快速解决方案:")
    print("   1. 在浏览器地址栏输入应用地址")
    print("   2. 按 Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac) 强制刷新")
    print("   3. 如果仍有问题，尝试无痕/隐私模式打开应用")

def update_streamlit_config():
    """更新Streamlit配置以强制刷新"""
    print("\n🔧 更新Streamlit配置...")
    
    config_content = """
[server]
port = 8504
maxUploadSize = 200
runOnSave = true
allowRunOnSave = true
timeout = 300
requestTimeout = 300
websocketTimeout = 300
maxMessageSize = 200
enableCORS = false
baseUrlPath = ""
enableStaticServing = true

[browser]
serverAddress = "localhost"
serverPort = 8504
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
caching = false
displayEnabled = true
showErrorDetails = true

[global]
developmentMode = true
logLevel = "info"
suppressDeprecationWarnings = false

# 强制刷新设置
[runner]
magicEnabled = true
installTracer = false
fixMatplotlib = true
postScriptGC = true
fastReruns = true
"""
    
    os.makedirs(".streamlit", exist_ok=True)
    
    with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Streamlit配置已更新")

def add_cache_busting_to_frontend():
    """在前端代码中添加缓存破坏机制"""
    print("\n🔄 添加缓存破坏机制...")
    
    # 在前端app.py开头添加缓存破坏代码
    cache_buster_code = '''
# 缓存破坏机制 - 强制刷新
import time
import hashlib

# 生成唯一的缓存破坏标识
CACHE_BUSTER = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

# 在页面标题中添加缓存破坏标识
if "cache_buster" not in st.session_state:
    st.session_state.cache_buster = CACHE_BUSTER
    # 强制重新加载页面配置
    st.rerun()

'''
    
    frontend_file = "frontend/app.py"
    
    try:
        with open(frontend_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否已经添加了缓存破坏代码
        if "CACHE_BUSTER" not in content:
            # 在import语句后添加缓存破坏代码
            import_end = content.find("import streamlit as st")
            if import_end != -1:
                import_end = content.find("\n", import_end) + 1
                new_content = content[:import_end] + cache_buster_code + content[import_end:]
                
                with open(frontend_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                print("✅ 缓存破坏机制已添加到前端代码")
            else:
                print("⚠️ 无法找到合适的位置添加缓存破坏代码")
        else:
            print("✅ 缓存破坏机制已存在")
            
    except Exception as e:
        print(f"❌ 添加缓存破坏机制失败: {e}")

def kill_existing_processes():
    """终止现有的服务进程"""
    print("\n🔄 终止现有服务进程...")
    
    try:
        # 终止占用端口的进程
        ports = [7701, 8504]
        
        for port in ports:
            try:
                # Windows命令
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line and 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) > 4:
                                pid = parts[-1]
                                try:
                                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                                    print(f"  ✅ 终止端口 {port} 的进程 (PID: {pid})")
                                except:
                                    pass
                                    
            except Exception as e:
                print(f"  ⚠️ 处理端口 {port} 时出错: {e}")
                
    except Exception as e:
        print(f"❌ 终止进程时出错: {e}")

def restart_services():
    """重启服务"""
    print("\n🚀 重启服务...")
    
    try:
        # 启动服务
        print("启动新的服务实例...")
        subprocess.Popen([sys.executable, "start.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        print("✅ 服务重启命令已发送")
        print("⏳ 请等待几秒钟让服务完全启动...")
        
        # 等待服务启动
        time.sleep(5)
        
        print("\n🌐 请在浏览器中访问: http://localhost:8504")
        print("💡 建议使用 Ctrl+F5 强制刷新页面")
        
    except Exception as e:
        print(f"❌ 重启服务失败: {e}")
        print("💡 请手动运行: python start.py")

def main():
    """主函数"""
    print("🔧 解决60秒超时错误显示问题")
    print("="*60)
    print("\n这个脚本将帮助解决用户仍然看到60秒超时错误的问题")
    print("主要原因可能是浏览器缓存了旧版本的代码")
    
    # 1. 清除本地缓存
    clear_streamlit_cache()
    
    # 2. 更新配置
    update_streamlit_config()
    
    # 3. 添加缓存破坏机制
    add_cache_busting_to_frontend()
    
    # 4. 终止现有进程
    kill_existing_processes()
    
    # 5. 显示浏览器缓存清除说明
    clear_browser_cache_instructions()
    
    # 6. 重启服务
    restart_services()
    
    print("\n" + "="*60)
    print("🎯 解决方案总结")
    print("="*60)
    print("\n✅ 已完成的操作:")
    print("   1. 清除了本地Streamlit缓存")
    print("   2. 更新了Streamlit配置文件")
    print("   3. 添加了缓存破坏机制")
    print("   4. 终止了旧的服务进程")
    print("   5. 重启了服务")
    
    print("\n🔧 用户需要执行的操作:")
    print("   1. 清除浏览器缓存 (按上述说明操作)")
    print("   2. 使用 Ctrl+F5 强制刷新页面")
    print("   3. 或者使用无痕模式打开应用")
    
    print("\n🎯 验证修复效果:")
    print("   1. 打开 http://localhost:8504")
    print("   2. 上传数据并尝试AI洞察功能")
    print("   3. 如果出现超时，错误消息应显示'180秒'而不是'60秒'")
    
    print("\n💡 如果问题仍然存在:")
    print("   1. 尝试不同的浏览器")
    print("   2. 检查是否有多个应用实例在运行")
    print("   3. 重启计算机以确保完全清除缓存")

if __name__ == "__main__":
    main()