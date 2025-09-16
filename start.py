#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JDC数据分析工具 - 一键启动脚本
同时启动前端Streamlit和后端Flask服务
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"

# 服务配置
FRONTEND_PORT = 8504
BACKEND_PORT = 7701

# 全局进程列表
processes = []

def signal_handler(sig, frame):
    """信号处理器，用于优雅关闭服务"""
    print("\n正在关闭服务...")
    for process in processes:
        if process.poll() is None:  # 进程仍在运行
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    print("所有服务已关闭")
    sys.exit(0)

def check_port(port):
    """检查端口是否被占用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False  # 端口未被占用
        except OSError:
            return True   # 端口被占用

def wait_for_service(port, service_name, timeout=30):
    """等待服务启动"""
    import socket
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    print(f"✅ {service_name} 服务已启动 (端口: {port})")
                    return True
        except:
            pass
        time.sleep(1)
    print(f"❌ {service_name} 服务启动超时")
    return False

def start_backend():
    """启动后端Flask服务"""
    print("🚀 启动后端服务...")
    
    # 检查后端目录和文件
    if not BACKEND_DIR.exists():
        print(f"❌ 后端目录不存在: {BACKEND_DIR}")
        return None
    
    backend_app = BACKEND_DIR / "app.py"
    if not backend_app.exists():
        print(f"❌ 后端应用文件不存在: {backend_app}")
        return None
    
    # 检查端口
    if check_port(BACKEND_PORT):
        print(f"⚠️  端口 {BACKEND_PORT} 已被占用，后端服务可能已在运行")
        return None
    
    # 启动后端服务
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(PROJECT_ROOT)
        
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=str(BACKEND_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        processes.append(process)
        print(f"📡 后端服务启动中... (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端Streamlit服务"""
    print("🎨 启动前端服务...")
    
    # 检查前端目录和文件
    if not FRONTEND_DIR.exists():
        print(f"❌ 前端目录不存在: {FRONTEND_DIR}")
        return None
    
    frontend_app = FRONTEND_DIR / "app.py"
    if not frontend_app.exists():
        print(f"❌ 前端应用文件不存在: {frontend_app}")
        return None
    
    # 检查端口
    if check_port(FRONTEND_PORT):
        print(f"⚠️  端口 {FRONTEND_PORT} 已被占用，前端服务可能已在运行")
        return None
    
    # 启动前端服务
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(PROJECT_ROOT)
        
        process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(FRONTEND_PORT),
                "--server.address", "localhost",
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ],
            cwd=str(FRONTEND_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        processes.append(process)
        print(f"🌐 前端服务启动中... (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ 前端服务启动失败: {e}")
        return None

def monitor_processes():
    """监控进程状态"""
    while True:
        time.sleep(5)
        for i, process in enumerate(processes[:]):
            if process.poll() is not None:
                print(f"⚠️  进程 {process.pid} 已退出 (返回码: {process.returncode})")
                # 读取错误输出
                if process.stderr:
                    stderr_output = process.stderr.read()
                    if stderr_output:
                        print(f"错误输出: {stderr_output}")
                processes.remove(process)
        
        if not processes:
            print("所有服务已停止")
            break

def main():
    """主函数"""
    print("="*60)
    print("🚀 JDC数据分析工具 - 一键启动")
    print("="*60)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查Python环境
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 项目根目录: {PROJECT_ROOT}")
    
    # 启动后端服务
    backend_process = start_backend()
    if backend_process:
        # 等待后端服务启动
        if wait_for_service(BACKEND_PORT, "后端Flask", timeout=30):
            print(f"🔗 后端API地址: http://localhost:{BACKEND_PORT}")
        else:
            print("❌ 后端服务启动失败，退出")
            return
    
    # 启动前端服务
    frontend_process = start_frontend()
    if frontend_process:
        # 等待前端服务启动
        if wait_for_service(FRONTEND_PORT, "前端Streamlit", timeout=180):
            print(f"🌐 前端访问地址: http://localhost:{FRONTEND_PORT}")
        else:
            print("❌ 前端服务启动失败")
    
    if not processes:
        print("❌ 没有服务成功启动")
        return
    
    print("\n" + "="*60)
    print("✅ 服务启动完成!")
    print(f"📊 前端界面: http://localhost:{FRONTEND_PORT}")
    print(f"🔧 后端API: http://localhost:{BACKEND_PORT}")
    print("\n按 Ctrl+C 停止所有服务")
    print("="*60)
    
    # 启动进程监控
    monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
    monitor_thread.start()
    
    # 主线程等待
    try:
        while processes:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()