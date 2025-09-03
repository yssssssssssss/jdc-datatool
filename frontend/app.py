# Streamlit 前端应用入口
import streamlit as st
import pandas as pd
import requests
import json
from io import StringIO
import base64
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 页面配置
st.set_page_config(
    page_title="JDC数据分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
    border-radius: 10px;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}
.upload-section {
    border: 2px dashed #1f77b4;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    # 主标题
    st.markdown('<div class="main-header">📊 JDC数据分析工具</div>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 功能菜单")
        page = st.selectbox(
            "选择功能",
            ["数据上传", "数据预览", "数据分析", "可视化生成", "报告生成", "AI洞察"]
        )
        
        st.markdown("---")
        st.markdown("### 📋 使用说明")
        st.markdown("""
        1. **数据上传**: 上传CSV或Excel文件
        2. **数据预览**: 查看数据基本信息
        3. **数据分析**: 进行统计分析
        4. **可视化生成**: 创建各种图表
        5. **报告生成**: 生成分析报告
        6. **AI洞察**: 获取智能分析建议
        """)
    
    # 主内容区域
    if page == "数据上传":
        show_upload_page()
    elif page == "数据预览":
        show_preview_page()
    elif page == "数据分析":
        show_analysis_page()
    elif page == "可视化生成":
        show_visualization_page()
    elif page == "报告生成":
        show_report_page()
    elif page == "AI洞察":
        show_ai_insights_page()

def show_upload_page():
    st.header("📁 数据上传")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "选择数据文件",
            type=['csv', 'xlsx', 'xls'],
            help="支持CSV和Excel格式文件"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # 保存上传的文件到session state
            st.session_state['uploaded_file'] = uploaded_file
            
            # 显示文件信息
            st.success(f"✅ 文件上传成功: {uploaded_file.name}")
            
            # 读取并预览数据
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state['dataframe'] = df
                
                st.subheader("📋 数据预览")
                st.dataframe(df.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ 文件读取失败: {str(e)}")
    
    with col2:
        st.markdown("### 📊 文件要求")
        st.info("""
        **支持格式:**
        - CSV (.csv)
        - Excel (.xlsx, .xls)
        
        **文件大小:**
        - 最大 200MB
        
        **数据要求:**
        - 第一行为列名
        - 数据格式规范
        - 避免特殊字符
        """)

def show_preview_page():
    st.header("👀 数据预览")
    
    if 'dataframe' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return
    
    df = st.session_state['dataframe']
    
    # 数据基本信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("数据行数", len(df))
    with col2:
        st.metric("数据列数", len(df.columns))
    with col3:
        st.metric("缺失值", df.isnull().sum().sum())
    with col4:
        st.metric("内存使用", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # 数据表格
    st.subheader("📋 数据表格")
    st.dataframe(df, use_container_width=True)
    
    # 数据类型信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 数据类型")
        dtype_df = pd.DataFrame({
            '列名': df.columns,
            '数据类型': df.dtypes.astype(str),
            '非空值数量': df.count()
        })
        st.dataframe(dtype_df, use_container_width=True)
    
    with col2:
        st.subheader("📈 基础统计")
        st.dataframe(df.describe(), use_container_width=True)

def show_analysis_page():
    st.header("🔍 数据分析")
    
    if 'dataframe' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return
    
    df = st.session_state['dataframe']
    
    # 分析选项
    analysis_type = st.selectbox(
        "选择分析类型",
        ["描述性统计", "相关性分析", "缺失值分析", "异常值检测"]
    )
    
    if analysis_type == "描述性统计":
        st.subheader("📊 描述性统计分析")
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.write("**数值列统计:**")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            st.write("**分类列统计:**")
            for col in categorical_cols:
                st.write(f"**{col}:**")
                st.write(df[col].value_counts().head(10))
    
    elif analysis_type == "相关性分析":
        st.subheader("🔗 相关性分析")
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            st.dataframe(corr_matrix, use_container_width=True)
        else:
            st.warning("需要至少2个数值列进行相关性分析")
    
    elif analysis_type == "缺失值分析":
        st.subheader("❓ 缺失值分析")
        missing_data = df.isnull().sum()
        missing_percent = (missing_data / len(df)) * 100
        
        missing_df = pd.DataFrame({
            '列名': missing_data.index,
            '缺失数量': missing_data.values,
            '缺失百分比': missing_percent.values
        })
        missing_df = missing_df[missing_df['缺失数量'] > 0].sort_values('缺失数量', ascending=False)
        
        if len(missing_df) > 0:
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.success("✅ 数据中没有缺失值")
    
    elif analysis_type == "异常值检测":
        st.subheader("🚨 异常值检测")
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            selected_col = st.selectbox("选择要检测的列", numeric_cols)
            
            # 使用IQR方法检测异常值
            Q1 = df[selected_col].quantile(0.25)
            Q3 = df[selected_col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]
            
            st.write(f"**{selected_col} 列异常值检测结果:**")
            st.write(f"- 下界: {lower_bound:.2f}")
            st.write(f"- 上界: {upper_bound:.2f}")
            st.write(f"- 异常值数量: {len(outliers)}")
            
            if len(outliers) > 0:
                st.dataframe(outliers, use_container_width=True)
        else:
            st.warning("没有数值列可供异常值检测")

def show_visualization_page():
    st.header("📈 可视化生成")
    
    if 'dataframe' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return
    
    df = st.session_state['dataframe']
    
    # 图表类型选择
    chart_type = st.selectbox(
        "选择图表类型",
        ["直方图", "散点图", "折线图", "柱状图", "箱线图", "相关性热力图"]
    )
    
    if chart_type == "直方图":
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            selected_col = st.selectbox("选择列", numeric_cols)
            fig = px.histogram(df, x=selected_col, title=f"{selected_col} 分布直方图")
            st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "散点图":
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X轴", numeric_cols)
            with col2:
                y_col = st.selectbox("Y轴", numeric_cols)
            
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
            st.plotly_chart(fig, use_container_width=True)
    
    # 其他图表类型的实现...
    st.info("更多图表类型正在开发中...")

def show_report_page():
    st.header("📄 报告生成")
    
    if 'dataframe' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return
    
    df = st.session_state['dataframe']
    
    # 报告配置选项
    st.subheader("📋 报告配置")
    col1, col2 = st.columns(2)
    
    with col1:
        report_title = st.text_input("报告标题", value="数据分析报告")
        include_charts = st.checkbox("包含图表", value=True)
        include_insights = st.checkbox("包含AI洞察", value=True)
    
    with col2:
        report_format = st.selectbox("报告格式", ["HTML", "JSON摘要"])
        chart_types = st.multiselect(
            "选择图表类型",
            ["数据概览", "缺失值分析", "相关性热力图", "分布图"],
            default=["数据概览", "缺失值分析"]
        )
    
    if st.button("🚀 生成报告", type="primary"):
        with st.spinner("正在生成报告..."):
            try:
                # 基础统计信息
                basic_stats = {
                    'shape': df.shape,
                    'columns': df.columns.tolist(),
                    'dtypes': df.dtypes.astype(str).to_dict(),
                    'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                    'missing_values': df.isnull().sum().to_dict()
                }
                
                # 数据质量评估
                missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                duplicate_rows = df.duplicated().sum()
                
                quality_score = max(0, 100 - missing_percentage * 2 - duplicate_rows / len(df) * 10)
                
                quality_assessment = {
                    'overall_score': round(quality_score, 1),
                    'missing_data_percentage': round(missing_percentage, 2),
                    'duplicate_rows': duplicate_rows,
                    'issues': []
                }
                
                if missing_percentage > 10:
                    quality_assessment['issues'].append(f"缺失值比例较高: {missing_percentage:.2f}%")
                if duplicate_rows > 0:
                    quality_assessment['issues'].append(f"存在 {duplicate_rows} 行重复数据")
                
                # 生成图表
                charts_data = []
                if include_charts and "数据概览" in chart_types:
                    # 数据类型分布图
                    dtype_counts = df.dtypes.value_counts()
                    fig = px.pie(values=dtype_counts.values, names=dtype_counts.index, 
                               title="数据类型分布")
                    charts_data.append(fig)
                
                if include_charts and "缺失值分析" in chart_types:
                    # 缺失值分析图
                    missing_data = df.isnull().sum()
                    missing_data = missing_data[missing_data > 0]
                    if len(missing_data) > 0:
                        fig = px.bar(x=missing_data.index, y=missing_data.values,
                                   title="各列缺失值数量")
                        charts_data.append(fig)
                
                if include_charts and "相关性热力图" in chart_types:
                    # 相关性热力图
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 1:
                        corr_matrix = df[numeric_cols].corr()
                        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                                      title="数值变量相关性热力图")
                        charts_data.append(fig)
                
                # 显示报告内容
                st.success("✅ 报告生成成功！")
                
                # 报告摘要
                st.subheader("📊 报告摘要")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("数据行数", f"{df.shape[0]:,}")
                with col2:
                    st.metric("数据列数", df.shape[1])
                with col3:
                    st.metric("数据质量评分", f"{quality_assessment['overall_score']}/100")
                with col4:
                    st.metric("缺失值比例", f"{quality_assessment['missing_data_percentage']:.1f}%")
                
                # 显示图表
                if charts_data:
                    st.subheader("📈 数据可视化")
                    for i, fig in enumerate(charts_data):
                        st.plotly_chart(fig, use_container_width=True)
                
                # 数据质量问题
                if quality_assessment['issues']:
                    st.subheader("⚠️ 数据质量问题")
                    for issue in quality_assessment['issues']:
                        st.warning(issue)
                
                # 处理建议
                st.subheader("💡 处理建议")
                recommendations = []
                if quality_assessment['missing_data_percentage'] > 10:
                    recommendations.append("建议处理缺失值：可以考虑删除、填充或插值")
                if quality_assessment['duplicate_rows'] > 0:
                    recommendations.append("建议删除重复行以提高数据质量")
                
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 1:
                    recommendations.append("可以进行相关性分析，识别变量间的关系")
                
                if len(recommendations) == 0:
                    st.success("数据质量良好，无明显问题")
                else:
                    for rec in recommendations:
                        st.info(rec)
                
                # 导出选项
                st.subheader("📥 导出报告")
                if report_format == "JSON摘要":
                    report_json = {
                        'title': report_title,
                        'basic_stats': basic_stats,
                        'quality_assessment': quality_assessment,
                        'recommendations': recommendations
                    }
                    st.download_button(
                        label="下载JSON报告",
                        data=json.dumps(report_json, ensure_ascii=False, indent=2),
                        file_name=f"{report_title}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"报告生成失败: {str(e)}")
                st.exception(e)

def show_ai_insights_page():
    st.header("🤖 AI洞察")
    
    if 'dataframe' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return
    
    df = st.session_state['dataframe']
    
    # 初始化聊天历史
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # 数据概览
    st.subheader("📊 数据概览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("数据行数", f"{df.shape[0]:,}")
    with col2:
        st.metric("数据列数", df.shape[1])
    with col3:
        numeric_cols = len(df.select_dtypes(include=['number']).columns)
        st.metric("数值列数", numeric_cols)
    with col4:
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric("缺失值比例", f"{missing_pct:.1f}%")
    
    # AI对话界面
    st.subheader("💬 与AI对话")
    
    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state['chat_history']):
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    
                    # 只在最新的AI回复中显示图表
                    is_latest_ai_message = (i == len(st.session_state['chat_history']) - 1)
                    if (is_latest_ai_message and 
                        'current_chart' in st.session_state and 
                        st.session_state['current_chart']):
                        
                        chart_data = st.session_state['current_chart']
                        if chart_data.get('chart_base64'):
                            st.markdown(f"**{chart_data.get('title', '数据可视化')}**")
                            
                            # 显示图表
                            import base64
                            chart_base64 = chart_data['chart_base64']
                            # 去掉data:image/png;base64,前缀
                            if chart_base64.startswith('data:image/png;base64,'):
                                chart_base64 = chart_base64.replace('data:image/png;base64,', '')
                            chart_bytes = base64.b64decode(chart_base64)
                            st.image(chart_bytes, use_column_width=True)
                            
                            if chart_data.get('description'):
                                st.caption(chart_data['description'])
                            
                            # 清除图表数据，避免重复显示
                            st.session_state['current_chart'] = None
    
    # 预设问题
    st.subheader("🎯 快速提问")
    quick_questions = [
        "分析这个数据集的主要特征",
        "找出数据中的异常值",
        "推荐适合的可视化方法",
        "数据质量如何？有什么问题？",
        "哪些变量之间可能存在相关性？"
    ]
    
    cols = st.columns(len(quick_questions))
    for i, question in enumerate(quick_questions):
        with cols[i]:
            if st.button(question, key=f"quick_q_{i}"):
                # 添加用户问题到聊天历史
                st.session_state['chat_history'].append({
                    'role': 'user',
                    'content': question
                })
                
                # 生成AI回答
                ai_response = generate_ai_insight(df, question)
                st.session_state['chat_history'].append({
                    'role': 'assistant',
                    'content': ai_response
                })
                
                st.rerun()
    
    # 用户输入
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input:
        # 添加用户消息
        st.session_state['chat_history'].append({
            'role': 'user',
            'content': user_input
        })
        
        # 生成AI回答
        with st.spinner("AI正在分析中..."):
            ai_response = generate_ai_insight(df, user_input)
            st.session_state['chat_history'].append({
                'role': 'assistant',
                'content': ai_response
            })
        
        st.rerun()
    
    # 清除聊天历史
    if st.button("🗑️ 清除对话历史"):
        st.session_state['chat_history'] = []
        st.rerun()

def generate_ai_insight(df, question):
    """通过后端API调用大模型生成AI洞察回答"""
    try:
        # 准备数据上下文
        data_context = {
            'shape': list(df.shape),
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
        }
        
        # 获取聊天历史
        chat_history = st.session_state.get('chat_history', [])
        
        # 准备请求数据
        request_data = {
            'question': question,
            'data_context': data_context,
            'chat_history': chat_history
        }
        
        # 调用后端AI API
        backend_url = "http://localhost:7701/api/ai/chat"
        response = requests.post(backend_url, json=request_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                ai_response = result['response']
                visualization_config = result.get('visualization', {'needed': False})
                
                # 如果需要生成图表
                if visualization_config.get('needed', False):
                    chart_result = generate_chart_from_config(df, visualization_config)
                    if chart_result:
                        # 将图表信息添加到session state中，供显示使用
                        if 'current_chart' not in st.session_state:
                            st.session_state['current_chart'] = {}
                        st.session_state['current_chart'] = chart_result
                        
                        # 在AI响应中添加图表说明
                        chart_description = visualization_config.get('description', '已生成相关图表')
                        ai_response += f"\n\n📊 {chart_description}"
                
                return ai_response
            else:
                # 如果API调用失败，返回错误信息
                return f"🤖 **AI服务暂时不可用**\n\n{result.get('response', result.get('error', '未知错误'))}\n\n💡 **提示：** 请检查网络连接和API配置。"
        else:
            return f"🤖 **后端服务连接失败**\n\n状态码：{response.status_code}\n\n💡 **提示：** 请确保后端服务正在运行（端口7701）。"
        
    except requests.exceptions.ConnectionError:
        return f"🤖 **无法连接到后端服务**\n\n💡 **提示：** 请确保后端服务正在运行（http://localhost:7701）。"
    except requests.exceptions.Timeout:
        return f"🤖 **请求超时**\n\n💡 **提示：** AI分析需要一些时间，请稍后重试。"
    except Exception as e:
        return f"❌ AI分析过程中出现错误：{str(e)}\n\n请检查系统配置或稍后重试。"

def generate_chart_from_config(df, visualization_config):
    """根据可视化配置生成图表"""
    try:
        # 调用后端图表生成API
        response = requests.post(
            'http://localhost:7701/api/generate_chart',
            json={
                'data': df.to_dict('records'),
                'visualization': visualization_config
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return {
                    'chart_base64': result['chart_base64'],
                    'chart_type': result['chart_type'],
                    'title': result['title'],
                    'description': result.get('description', '')
                }
        
        return None
        
    except Exception as e:
        st.error(f"图表生成失败: {str(e)}")
        return None

if __name__ == "__main__":
    main()