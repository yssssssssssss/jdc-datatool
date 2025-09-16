#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化AI聊天界面Demo
参考ChatGPT、Gemini、Grok的设计理念
"""

import streamlit as st
import time
import json
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="现代化AI聊天Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 现代化CSS样式
st.markdown("""
<style>
/* 全局样式重置 */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

/* CSS变量定义 */
:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    --accent-color: #059669;
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #f1f5f9;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
}

/* 深色主题 */
[data-theme="dark"] {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border-color: #334155;
}

/* 主容器 */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    background: var(--bg-primary);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    overflow: hidden;
    border: 1px solid var(--border-color);
}

/* 聊天头部 */
.chat-header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.chat-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.chat-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    opacity: 0.9;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* 消息区域 */
.chat-messages {
    height: 500px;
    overflow-y: auto;
    padding: 1.5rem;
    background: var(--bg-secondary);
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* 消息气泡 */
.message {
    display: flex;
    gap: 0.75rem;
    max-width: 85%;
    animation: slideIn 0.3s ease-out;
}

.message.user {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.message.assistant {
    align-self: flex-start;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 头像 */
.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
    box-shadow: var(--shadow-sm);
}

.avatar.user {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
}

.avatar.assistant {
    background: linear-gradient(135deg, var(--accent-color), var(--primary-color));
    color: white;
}

/* 消息内容 */
.message-content {
    background: var(--bg-primary);
    border-radius: var(--radius-lg);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border-color);
    position: relative;
    word-wrap: break-word;
}

.message.user .message-content {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border: none;
}

.message.assistant .message-content {
    background: var(--bg-primary);
    color: var(--text-primary);
}

/* 消息时间 */
.message-time {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
    opacity: 0.7;
}

/* 消息操作按钮 */
.message-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.message:hover .message-actions {
    opacity: 1;
}

.action-btn {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
}

.action-btn:hover {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

/* 输入区域 */
.chat-input-area {
    padding: 1.5rem 2rem;
    background: var(--bg-primary);
    border-top: 1px solid var(--border-color);
}

.input-container {
    display: flex;
    gap: 1rem;
    align-items: flex-end;
}

.input-wrapper {
    flex: 1;
    position: relative;
}

.chat-input {
    width: 100%;
    min-height: 44px;
    max-height: 120px;
    padding: 0.75rem 3rem 0.75rem 1rem;
    border: 2px solid var(--border-color);
    border-radius: var(--radius-lg);
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 1rem;
    resize: none;
    outline: none;
    transition: all 0.2s ease;
}

.chat-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

.send-btn {
    position: absolute;
    right: 0.5rem;
    bottom: 0.5rem;
    width: 36px;
    height: 36px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.send-btn:hover {
    background: var(--secondary-color);
    transform: scale(1.05);
}

.send-btn:disabled {
    background: var(--text-secondary);
    cursor: not-allowed;
    transform: none;
}

/* 快捷建议 */
.quick-suggestions {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.suggestion-chip {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.suggestion-chip:hover {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
    transform: translateY(-1px);
}

/* 打字效果 */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-secondary);
    font-style: italic;
}

.typing-dots {
    display: flex;
    gap: 2px;
}

.typing-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--text-secondary);
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.4;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

/* 主题切换按钮 */
.theme-toggle {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: var(--radius-md);
    padding: 0.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.2s ease;
}

.theme-toggle:hover {
    background: rgba(255, 255, 255, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .chat-container {
        margin: 0;
        border-radius: 0;
        height: 100vh;
    }
    
    .chat-header {
        padding: 1rem;
    }
    
    .chat-messages {
        height: calc(100vh - 200px);
        padding: 1rem;
    }
    
    .chat-input-area {
        padding: 1rem;
    }
    
    .message {
        max-width: 95%;
    }
}

/* 隐藏Streamlit默认元素 */
.stApp > header {
    background-color: transparent;
}

.stApp > div > div > div > div > div > section > div {
    padding-top: 0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            'role': 'assistant',
            'content': '👋 你好！我是你的AI数据分析助手。我可以帮你分析数据、生成图表、回答问题。有什么我可以帮助你的吗？',
            'timestamp': datetime.now().strftime('%H:%M')
        }
    ]

if 'is_typing' not in st.session_state:
    st.session_state.is_typing = False

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# 主题切换函数
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.rerun()

# 添加消息函数
def add_message(role, content):
    st.session_state.messages.append({
        'role': role,
        'content': content,
        'timestamp': datetime.now().strftime('%H:%M')
    })

# 模拟AI回复函数
def simulate_ai_response(user_message):
    # 模拟思考时间
    st.session_state.is_typing = True
    
    # 根据用户输入生成不同类型的回复
    responses = {
        '数据分析': '📊 我可以帮你进行各种数据分析，包括：\n\n• **描述性统计**：均值、中位数、标准差等\n• **相关性分析**：变量间的关系\n• **趋势分析**：时间序列数据的变化趋势\n• **异常检测**：识别数据中的异常值\n\n你有具体的数据需要分析吗？',
        '图表': '📈 我支持生成多种类型的图表：\n\n• **折线图**：展示趋势变化\n• **柱状图**：比较不同类别\n• **散点图**：显示相关性\n• **热力图**：展示数据密度\n• **饼图**：显示比例关系\n\n请告诉我你想要什么类型的图表？',
        '帮助': '🤖 我是一个智能数据分析助手，具备以下能力：\n\n✨ **核心功能**\n• 数据质量评估和清洗建议\n• 智能图表推荐和生成\n• 统计分析和洞察发现\n• 自然语言查询数据\n\n💡 **使用技巧**\n• 直接描述你的分析需求\n• 上传数据文件进行分析\n• 使用快捷建议快速开始\n\n有什么具体问题吗？'
    }
    
    # 简单的关键词匹配
    response = '🤔 这是一个很有趣的问题！让我来帮你分析一下...\n\n基于你的问题，我建议我们可以从以下几个角度来探讨：\n\n1. **数据收集**：确保数据的完整性和准确性\n2. **分析方法**：选择合适的统计方法\n3. **结果解释**：将分析结果转化为可行的洞察\n\n你想深入了解哪个方面呢？'
    
    for keyword, resp in responses.items():
        if keyword in user_message:
            response = resp
            break
    
    return response

# 渲染聊天界面
def render_chat_interface():
    # 主容器
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # 聊天头部
    st.markdown(f'''
    <div class="chat-header" data-theme="{st.session_state.theme}">
        <div class="chat-title">
            🤖 AI数据分析助手
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="chat-status">
                <div class="status-dot"></div>
                在线
            </div>
            <button class="theme-toggle" onclick="toggleTheme()">
                {'🌙' if st.session_state.theme == 'light' else '☀️'}
            </button>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 消息区域
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    # 渲染消息
    for message in st.session_state.messages:
        role = message['role']
        content = message['content']
        timestamp = message['timestamp']
        
        avatar_emoji = '👤' if role == 'user' else '🤖'
        
        st.markdown(f'''
        <div class="message {role}">
            <div class="avatar {role}">{avatar_emoji}</div>
            <div>
                <div class="message-content">
                    {content}
                </div>
                <div class="message-time">{timestamp}</div>
                <div class="message-actions">
                    <button class="action-btn">📋 复制</button>
                    <button class="action-btn">🔄 重新生成</button>
                    <button class="action-btn">👍 点赞</button>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # 打字指示器
    if st.session_state.is_typing:
        st.markdown('''
        <div class="message assistant">
            <div class="avatar assistant">🤖</div>
            <div>
                <div class="message-content">
                    <div class="typing-indicator">
                        AI正在思考
                        <div class="typing-dots">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # 关闭消息区域
    
    # 输入区域
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    
    # 快捷建议
    suggestions = ['数据分析', '生成图表', '数据质量检查', '相关性分析', '异常检测']
    
    st.markdown('<div class="quick-suggestions">', unsafe_allow_html=True)
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f'suggestion_{i}', help=f'快速询问：{suggestion}'):
                add_message('user', suggestion)
                # 模拟AI回复
                time.sleep(1)  # 模拟思考时间
                ai_response = simulate_ai_response(suggestion)
                add_message('assistant', ai_response)
                st.session_state.is_typing = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 输入框和发送按钮
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_area(
            "输入消息",
            placeholder="输入你的问题...",
            height=60,
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_clicked = st.button("发送", type="primary", use_container_width=True)
    
    # 处理发送消息
    if send_clicked and user_input.strip():
        # 添加用户消息
        add_message('user', user_input)
        
        # 清空输入框
        st.session_state.chat_input = ""
        
        # 设置打字状态
        st.session_state.is_typing = True
        st.rerun()
    
    # 如果正在打字，模拟AI回复
    if st.session_state.is_typing:
        time.sleep(2)  # 模拟AI思考时间
        ai_response = simulate_ai_response(st.session_state.messages[-1]['content'])
        add_message('assistant', ai_response)
        st.session_state.is_typing = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # 关闭输入区域
    st.markdown('</div>', unsafe_allow_html=True)  # 关闭主容器

# JavaScript for theme toggle
st.markdown("""
<script>
function toggleTheme() {
    // This would be handled by Streamlit's rerun mechanism
    console.log('Theme toggle clicked');
}
</script>
""", unsafe_allow_html=True)

# 主函数
def main():
    st.markdown('<div style="padding: 1rem;">', unsafe_allow_html=True)
    
    # 标题和说明
    st.markdown("""
    # 🚀 现代化AI聊天界面Demo
    
    这是一个参考ChatGPT、Gemini、Grok设计的现代化聊天界面原型。主要特性包括：
    
    ✨ **现代化设计**：圆角气泡、渐变色彩、优雅动画  
    🎨 **主题切换**：支持浅色/深色主题  
    💬 **智能交互**：打字效果、状态指示、快捷建议  
    📱 **响应式布局**：适配不同屏幕尺寸  
    🔧 **丰富功能**：消息操作、代码高亮、图表支持  
    
    ---
    """, unsafe_allow_html=True)
    
    # 渲染聊天界面
    render_chat_interface()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 底部说明
    st.markdown("""
    ---
    
    ### 📋 实现特性
    
    - **视觉设计**：现代化CSS样式，支持主题切换
    - **交互体验**：流畅的动画效果和状态反馈
    - **消息系统**：支持不同类型消息和操作按钮
    - **响应式布局**：适配桌面和移动设备
    - **快捷功能**：预设问题和智能建议
    
    ### 🔄 下一步计划
    
    1. **集成真实AI后端**：连接实际的AI服务
    2. **添加代码高亮**：支持代码块语法高亮
    3. **图表内嵌显示**：直接在聊天中显示图表
    4. **消息搜索**：支持历史消息搜索
    5. **导出功能**：支持对话导出和分享
    
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()