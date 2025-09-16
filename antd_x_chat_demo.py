import streamlit as st
import time
import random
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="Ant Design X 风格聊天界面",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ant Design X 风格的CSS样式
st.markdown("""
<style>
/* 全局样式 - 基于Ant Design X设计规范 */
.main {
    padding: 0;
    background: #f5f5f5;
}

/* 聊天容器 - 遵循RICH设计范式 */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* 头部区域 - 符合Ant Design规范 */
.chat-header {
    padding: 16px 24px;
    border-bottom: 1px solid #f0f0f0;
    background: white;
    border-radius: 8px 8px 0 0;
}

.chat-title {
    font-size: 16px;
    font-weight: 500;
    color: #262626;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.status-indicator {
    width: 8px;
    height: 8px;
    background: #52c41a;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* 消息区域 - Bubble组件风格 */
.messages-container {
    flex: 1;
    padding: 16px 24px;
    overflow-y: auto;
    background: #fafafa;
}

/* 消息气泡 - 基于Ant Design X Bubble组件 */
.message-bubble {
    margin-bottom: 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.message-bubble.user {
    flex-direction: row-reverse;
}

.message-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 500;
    flex-shrink: 0;
}

.message-avatar.user {
    background: #1677ff;
    color: white;
}

.message-avatar.assistant {
    background: #f0f0f0;
    color: #595959;
}

.message-content {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
}

.message-bubble.user .message-content {
    background: #1677ff;
    color: white;
    border-bottom-right-radius: 4px;
}

.message-bubble.assistant .message-content {
    background: white;
    color: #262626;
    border: 1px solid #f0f0f0;
    border-bottom-left-radius: 4px;
}

.message-time {
    font-size: 12px;
    color: #8c8c8c;
    margin-top: 4px;
    text-align: center;
}

/* 输入区域 - Sender组件风格 */
.input-container {
    padding: 16px 24px;
    border-top: 1px solid #f0f0f0;
    background: white;
    border-radius: 0 0 8px 8px;
}

/* 快捷建议 - Suggestion组件风格 */
.suggestions-container {
    margin-bottom: 12px;
}

.suggestion-chip {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px 8px 4px 0;
    background: #f6f6f6;
    border: 1px solid #d9d9d9;
    border-radius: 16px;
    font-size: 12px;
    color: #595959;
    cursor: pointer;
    transition: all 0.2s;
}

.suggestion-chip:hover {
    background: #e6f4ff;
    border-color: #91caff;
    color: #1677ff;
}

/* 思维链 - ThoughtChain组件风格 */
.thought-chain {
    background: #f6ffed;
    border: 1px solid #b7eb8f;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 12px;
    color: #389e0d;
}

/* 欢迎界面 - Welcome组件风格 */
.welcome-container {
    text-align: center;
    padding: 40px 24px;
    color: #8c8c8c;
}

.welcome-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.welcome-title {
    font-size: 18px;
    font-weight: 500;
    color: #262626;
    margin-bottom: 8px;
}

.welcome-subtitle {
    font-size: 14px;
    color: #8c8c8c;
    margin-bottom: 24px;
}

/* 提示集 - Prompts组件风格 */
.prompts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 16px;
}

.prompt-card {
    padding: 16px;
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.prompt-card:hover {
    border-color: #1677ff;
    box-shadow: 0 2px 4px rgba(22, 119, 255, 0.1);
}

.prompt-title {
    font-size: 14px;
    font-weight: 500;
    color: #262626;
    margin-bottom: 4px;
}

.prompt-description {
    font-size: 12px;
    color: #8c8c8c;
}

/* 加载状态 */
.loading-dots {
    display: inline-flex;
    gap: 4px;
}

.loading-dot {
    width: 6px;
    height: 6px;
    background: #8c8c8c;
    border-radius: 50%;
    animation: loading 1.4s infinite ease-in-out;
}

.loading-dot:nth-child(1) { animation-delay: -0.32s; }
.loading-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes loading {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* 响应式设计 */
@media (max-width: 768px) {
    .chat-container {
        margin: 0;
        border-radius: 0;
        height: 100vh;
    }
    
    .message-content {
        max-width: 85%;
    }
    
    .prompts-grid {
        grid-template-columns: 1fr;
    }
}

/* 隐藏Streamlit默认元素 */
.stApp > header {
    background-color: transparent;
}

.stApp {
    margin-top: -80px;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'is_thinking' not in st.session_state:
    st.session_state.is_thinking = False

# 预设提示集 - 基于Ant Design X Prompts组件
PROMPT_SUGGESTIONS = [
    {"title": "数据分析", "description": "帮我分析数据趋势", "prompt": "请帮我分析当前数据的趋势和模式"},
    {"title": "图表生成", "description": "创建可视化图表", "prompt": "根据数据生成合适的可视化图表"},
    {"title": "洞察报告", "description": "生成分析报告", "prompt": "为我生成详细的数据洞察报告"},
    {"title": "智能建议", "description": "获取优化建议", "prompt": "基于数据分析给出优化建议"}
]

# 快捷建议 - 基于Ant Design X Suggestion组件
QUICK_SUGGESTIONS = [
    "解释这个趋势",
    "生成图表", 
    "数据摘要",
    "导出报告"
]

def add_message(role, content, show_thought=False):
    """添加消息到会话历史"""
    timestamp = datetime.now().strftime("%H:%M")
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp,
        "show_thought": show_thought
    }
    st.session_state.messages.append(message)

def simulate_ai_response(user_input):
    """模拟AI响应 - 基于RICH设计范式"""
    # 模拟思维链过程
    st.session_state.is_thinking = True
    
    # 根据输入生成不同类型的响应
    responses = {
        "数据": "我正在分析您的数据，发现了一些有趣的模式。让我为您详细解释...",
        "图表": "我将为您生成合适的可视化图表。基于数据特征，建议使用柱状图来展示趋势。",
        "分析": "根据数据分析，我发现以下几个关键洞察：1) 数据呈现上升趋势 2) 存在季节性波动 3) 异常值较少",
        "报告": "我已经为您准备了详细的分析报告，包含数据概览、趋势分析和建议措施。"
    }
    
    # 简单的关键词匹配
    response = "我理解您的需求，让我来帮助您分析和处理这些信息。"
    for key, value in responses.items():
        if key in user_input:
            response = value
            break
    
    return response

def render_welcome_screen():
    """渲染欢迎界面 - 基于Ant Design X Welcome组件"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🤖</div>
        <div class="welcome-title">AI 数据分析助手</div>
        <div class="welcome-subtitle">基于 Ant Design X 设计规范构建</div>
        
        <div class="prompts-grid">
    """, unsafe_allow_html=True)
    
    # 渲染提示集
    cols = st.columns(2)
    for i, prompt in enumerate(PROMPT_SUGGESTIONS):
        with cols[i % 2]:
            if st.button(f"📊 {prompt['title']}", key=f"prompt_{i}", help=prompt['description']):
                add_message("user", prompt['prompt'])
                st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_message_bubble(message):
    """渲染消息气泡 - 基于Ant Design X Bubble组件"""
    role_class = "user" if message["role"] == "user" else "assistant"
    avatar_text = "U" if message["role"] == "user" else "AI"
    
    # 思维链显示
    thought_chain = ""
    if message.get("show_thought") and message["role"] == "assistant":
        thought_chain = '<div class="thought-chain">🧠 正在思考和分析您的问题...</div>'
    
    st.markdown(f"""
    <div class="message-bubble {role_class}">
        <div class="message-avatar {role_class}">{avatar_text}</div>
        <div>
            {thought_chain}
            <div class="message-content">{message['content']}</div>
            <div class="message-time">{message['timestamp']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_interface():
    """渲染聊天界面主体"""
    # 聊天容器开始
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # 头部区域
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">
            <span class="status-indicator"></span>
            AI 数据分析助手 - Ant Design X 风格
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 消息区域
    st.markdown('<div class="messages-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        render_welcome_screen()
    else:
        # 渲染消息历史
        for message in st.session_state.messages:
            render_message_bubble(message)
        
        # 显示AI思考状态
        if st.session_state.is_thinking:
            st.markdown("""
            <div class="message-bubble assistant">
                <div class="message-avatar assistant">AI</div>
                <div>
                    <div class="message-content">
                        <div class="loading-dots">
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                            <div class="loading-dot"></div>
                        </div>
                        正在思考中...
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # 消息区域结束
    
    # 输入区域
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # 快捷建议
    if st.session_state.messages:
        st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
        suggestion_cols = st.columns(len(QUICK_SUGGESTIONS))
        for i, suggestion in enumerate(QUICK_SUGGESTIONS):
            with suggestion_cols[i]:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    add_message("user", suggestion)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 输入框 - 基于Ant Design X Sender组件
    user_input = st.text_area(
        "输入消息",
        placeholder="请输入您的问题或需求...",
        height=80,
        key="user_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        send_button = st.button("发送", type="primary", use_container_width=True)
    with col2:
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.is_thinking = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # 输入区域结束
    st.markdown('</div>', unsafe_allow_html=True)  # 聊天容器结束
    
    # 处理发送消息
    if send_button and user_input.strip():
        # 添加用户消息
        add_message("user", user_input.strip())
        
        # 清空输入框
        st.session_state.user_input = ""
        
        # 模拟AI响应
        with st.spinner("AI正在思考..."):
            time.sleep(1)  # 模拟处理时间
            response = simulate_ai_response(user_input)
            add_message("assistant", response, show_thought=True)
        
        st.session_state.is_thinking = False
        st.rerun()

def main():
    """主函数"""
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: white; margin-bottom: 20px;">
        <h1 style="color: #1677ff; margin: 0;">🎨 Ant Design X 风格聊天界面</h1>
        <p style="color: #8c8c8c; margin: 5px 0 0 0;">基于 RICH 设计范式 | Bubble • Sender • Conversations • Prompts</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_chat_interface()
    
    # 显示设计规范信息
    with st.expander("📋 Ant Design X 设计规范说明"):
        st.markdown("""
        ### RICH 设计范式
        - **Intention (意图)**: AI理解用户模糊意图，协助完成方案计划
        - **Role (角色)**: AI扮演特定角色，如助手、老师等
        - **Conversation (对话)**: 自然语言对话，逐步澄清意图
        - **Hybrid UI (混合界面)**: 结合传统GUI和新交互模式
        
        ### 核心组件
        - **Bubble**: 对话气泡组件，支持用户和AI消息展示
        - **Sender**: 输入框组件，支持文本输入和发送
        - **Conversations**: 对话管理组件，处理会话历史
        - **Prompts**: 提示集组件，提供预设问题模板
        - **Suggestion**: 快捷指令组件，提供常用操作
        - **ThoughtChain**: 思维链组件，展示AI思考过程
        - **Welcome**: 欢迎界面组件，引导用户开始对话
        
        ### 设计原则
        1. **信息充分且真实**: 提供准确、可信的信息
        2. **话术清晰易懂**: 使用简洁、易理解的表达
        3. **自然流畅**: 模拟人际交流的自然性
        """)

if __name__ == "__main__":
    main()