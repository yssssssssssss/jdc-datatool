#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制清除所有缓存并重启服务
解决用户仍看到60秒超时错误的问题
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

def kill_all_processes():
    """终止所有相关进程"""
    print("🔄 终止所有相关进程...")
    
    # 终止Python进程
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, text=True)
        print("   ✅ 已终止所有Python进程")
    except:
        print("   ⚠️ 无法终止Python进程")
    
    # 终止Streamlit进程
    try:
        subprocess.run(["taskkill", "/f", "/im", "streamlit.exe"], 
                      capture_output=True, text=True)
        print("   ✅ 已终止Streamlit进程")
    except:
        print("   ⚠️ 无法终止Streamlit进程")
    
    # 等待进程完全终止
    time.sleep(3)

def clear_streamlit_cache():
    """清除Streamlit缓存"""
    print("\n🧹 清除Streamlit缓存...")
    
    # Streamlit缓存目录
    cache_dirs = [
        os.path.expanduser("~/.streamlit"),
        os.path.expanduser("~/.cache/streamlit"),
        ".streamlit/cache",
        "__pycache__",
        ".pytest_cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                if os.path.isdir(cache_dir):
                    shutil.rmtree(cache_dir)
                    print(f"   ✅ 已删除缓存目录: {cache_dir}")
                else:
                    os.remove(cache_dir)
                    print(f"   ✅ 已删除缓存文件: {cache_dir}")
            except Exception as e:
                print(f"   ⚠️ 无法删除 {cache_dir}: {e}")
        else:
            print(f"   ℹ️ 缓存目录不存在: {cache_dir}")

def clear_python_cache():
    """清除Python缓存"""
    print("\n🐍 清除Python缓存...")
    
    # 递归删除所有__pycache__目录
    for root, dirs, files in os.walk("."):
        for dir_name in dirs[:]:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   ✅ 已删除: {cache_path}")
                    dirs.remove(dir_name)
                except Exception as e:
                    print(f"   ⚠️ 无法删除 {cache_path}: {e}")
    
    # 删除.pyc文件
    for root, dirs, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".pyc"):
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                    print(f"   ✅ 已删除: {file_path}")
                except Exception as e:
                    print(f"   ⚠️ 无法删除 {file_path}: {e}")

def update_cache_buster():
    """更新缓存破坏机制"""
    print("\n🔄 更新缓存破坏机制...")
    
    # 在前端代码中添加时间戳
    frontend_file = "frontend/app.py"
    
    try:
        with open(frontend_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 添加或更新缓存破坏时间戳
        import time
        timestamp = int(time.time())
        
        # 在文件开头添加时间戳注释
        cache_buster = f"# Cache Buster: {timestamp}\n"
        
        # 如果已存在缓存破坏注释，替换它
        lines = content.split('\n')
        new_lines = []
        found_cache_buster = False
        
        for line in lines:
            if line.startswith("# Cache Buster:"):
                new_lines.append(cache_buster.strip())
                found_cache_buster = True
            else:
                new_lines.append(line)
        
        # 如果没有找到缓存破坏注释，在文件开头添加
        if not found_cache_buster:
            new_lines.insert(0, cache_buster.strip())
        
        # 写回文件
        with open(frontend_file, "w", encoding="utf-8") as f:
            f.write('\n'.join(new_lines))
        
        print(f"   ✅ 已更新缓存破坏时间戳: {timestamp}")
        
    except Exception as e:
        print(f"   ⚠️ 无法更新缓存破坏机制: {e}")

def force_reload_modules():
    """强制重新加载模块"""
    print("\n🔄 强制重新加载模块...")
    
    # 清除sys.modules中的相关模块
    modules_to_remove = []
    for module_name in sys.modules.keys():
        if any(keyword in module_name.lower() for keyword in ['frontend', 'backend', 'app']):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        try:
            del sys.modules[module_name]
            print(f"   ✅ 已卸载模块: {module_name}")
        except:
            pass

def restart_services():
    """重启服务"""
    print("\n🚀 重启服务...")
    
    # 等待一段时间确保所有进程完全终止
    print("   ⏳ 等待进程完全终止...")
    time.sleep(5)
    
    # 启动服务
    try:
        print("   🚀 启动新的服务实例...")
        process = subprocess.Popen(
            ["python", "start.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待服务启动
        time.sleep(10)
        
        print("   ✅ 服务已重新启动")
        print("   📊 前端地址: http://localhost:8504")
        print("   🔧 后端地址: http://localhost:7701")
        
        return process
        
    except Exception as e:
        print(f"   ❌ 启动服务失败: {e}")
        return None

def verify_fix():
    """验证修复效果"""
    print("\n🔍 验证修复效果...")
    
    import requests
    
    # 等待服务完全启动
    print("   ⏳ 等待服务完全启动...")
    time.sleep(15)
    
    # 测试后端健康状态
    try:
        response = requests.get("http://localhost:7701/api/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print(f"   ❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 无法连接后端服务: {e}")
        return False
    
    # 检查前端代码中的超时设置
    try:
        with open("frontend/app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "timeout=180" in content and "AI分析请求超时（180秒）" in content:
            print("   ✅ 前端超时设置正确 (180秒)")
        else:
            print("   ❌ 前端超时设置异常")
            return False
            
        if "60秒" in content:
            print("   ⚠️ 前端代码中仍有60秒引用")
            return False
        else:
            print("   ✅ 前端代码中无60秒引用")
            
    except Exception as e:
        print(f"   ❌ 检查前端代码失败: {e}")
        return False
    
    return True

def show_user_instructions():
    """显示用户操作说明"""
    print("\n" + "="*60)
    print("📋 用户操作说明 - 彻底解决60秒超时问题")
    print("="*60)
    
    print("\n🌐 浏览器缓存清理 (必须执行):")
    print("   1. 打开浏览器")
    print("   2. 按 Ctrl + Shift + Delete")
    print("   3. 选择 '全部时间'")
    print("   4. 勾选所有选项 (缓存、Cookie、历史记录等)")
    print("   5. 点击 '清除数据'")
    
    print("\n🔄 强制刷新 (推荐):")
    print("   1. 访问 http://localhost:8504")
    print("   2. 按 Ctrl + F5 (强制刷新)")
    print("   3. 或按 Ctrl + Shift + R")
    
    print("\n🕵️ 无痕模式测试 (验证):")
    print("   1. 打开无痕/隐私浏览模式")
    print("   2. 访问 http://localhost:8504")
    print("   3. 测试AI洞察功能")
    
    print("\n🧪 测试步骤:")
    print("   1. 上传数据文件")
    print("   2. 进入AI洞察页面")
    print("   3. 提问一个复杂问题")
    print("   4. 观察是否还显示60秒超时错误")
    
    print("\n✅ 预期结果:")
    print("   - 如果超时，应显示 '180秒' 而不是 '60秒'")
    print("   - 错误消息应为: 'AI分析请求超时（180秒）'")
    
    print("\n🆘 如果问题仍然存在:")
    print("   1. 重启计算机")
    print("   2. 重新运行此脚本")
    print("   3. 使用不同的浏览器测试")
    print("   4. 检查是否有多个应用实例在运行")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("🔧 强制清除所有缓存并重启服务")
    print("解决60秒超时错误问题")
    print("="*60)
    
    try:
        # 1. 终止所有进程
        kill_all_processes()
        
        # 2. 清除各种缓存
        clear_streamlit_cache()
        clear_python_cache()
        
        # 3. 更新缓存破坏机制
        update_cache_buster()
        
        # 4. 强制重新加载模块
        force_reload_modules()
        
        # 5. 重启服务
        process = restart_services()
        
        if process:
            # 6. 验证修复效果
            if verify_fix():
                print("\n🎉 缓存清理和服务重启完成!")
                print("✅ 60秒超时问题应该已经解决")
            else:
                print("\n⚠️ 验证失败，可能需要手动检查")
            
            # 7. 显示用户操作说明
            show_user_instructions()
            
        else:
            print("\n❌ 服务重启失败，请手动启动")
            
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        print("请尝试手动重启服务: python start.py")

if __name__ == "__main__":
    main()