# Streamlit 前端应用入口
import streamlit as st
import pandas as pd
import numpy as np
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

# 自定义CSS样式 - 黑白灰配色方案
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #2c2c2c;
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: linear-gradient(90deg, #f8f9fa, #e9ecef);
    border-radius: 10px;
    border: 1px solid #dee2e6;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
    border: 1px solid #e9ecef;
}
.upload-section {
    border: 2px dashed #6c757d;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
    background-color: #f8f9fa;
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
    # 初始化可视化组件选择器状态
    if 'selected_chart_type' not in st.session_state:
        st.session_state['selected_chart_type'] = 'auto'
    if 'viz_components' not in st.session_state:
        st.session_state['viz_components'] = get_available_viz_components()
    
    if 'dataframe' not in st.session_state:
        st.warning("⚠️ 请先上传数据文件")
        return
    
    df = st.session_state['dataframe']
    
    # 初始化聊天历史
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    
    # 侧边栏：可视化组件选择器
    with st.sidebar:
        st.markdown("### 🎨 可视化设置")
        
        # 图表类型选择
        chart_types = {
            'auto': '🤖 智能推荐',
            'line': '📈 折线图',
            'bar': '📊 柱状图',
            'scatter': '🔵 散点图',
            'histogram': '📊 直方图',
            'box': '📦 箱线图',
            'heatmap': '🔥 热力图',
            'pie': '🥧 饼图'
        }
        
        st.session_state['selected_chart_type'] = st.selectbox(
            "默认图表类型",
            options=list(chart_types.keys()),
            format_func=lambda x: chart_types[x],
            index=0
        )
        
        # 智能图表推荐
        st.markdown("### 🤖 智能推荐")
        
        if st.button("获取图表推荐", use_container_width=True):
            with st.spinner("正在分析数据特征..."):
                recommendations = get_chart_recommendations(df)
                if recommendations:
                    st.session_state['chart_recommendations'] = recommendations
                    st.success("已获取图表推荐！")
                else:
                    st.error("获取推荐失败")
        
        # 显示推荐结果
        if 'chart_recommendations' in st.session_state:
            st.markdown("**推荐图表:**")
            for rec in st.session_state['chart_recommendations'][:3]:  # 显示前3个推荐
                priority_color = {
                    'high': '🔴',
                    'medium': '🟡', 
                    'low': '🟢'
                }.get(rec.get('priority', 'medium'), '🟡')
                
                if st.button(
                    f"{priority_color} {rec['icon']} {rec['name']}",
                    key=f"rec_{rec['chart_type']}",
                    help=rec['description'],
                    use_container_width=True
                ):
                    st.session_state['selected_chart_type'] = rec['chart_type']
                    st.success(f"已选择: {rec['name']}")
                    st.rerun()
         
        # 可视化组件管理
        st.markdown("### ⚙️ 组件管理")
        
        # 组件分类显示
        component_categories = {}
        for component in st.session_state['viz_components']:
            category = component.get('category', 'other')
            if category not in component_categories:
                component_categories[category] = []
            component_categories[category].append(component)
        
        # 显示组件分类
        category_names = {
            'ai': '🤖 AI智能',
            'trend': '📈 趋势分析',
            'comparison': '📊 对比分析',
            'correlation': '🔗 关联分析',
            'distribution': '📊 分布分析',
            'proportion': '🥧 比例分析',
            'multivariate': '🎯 多元分析',
            'summary': '📋 汇总展示',
            'raw_data': '📊 原始数据',
            'custom': '🎨 自定义',
            'other': '📁 其他'
        }
        
        for category, components in component_categories.items():
            with st.expander(f"{category_names.get(category, category)} ({len(components)})"):
                for component in components:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.text(f"{component['icon']} {component['name']}")
                    with col2:
                        st.caption(component.get('description', '无描述'))
                    with col3:
                        if component.get('custom', False):
                            if st.button("🗑️", key=f"del_{component['id']}", help="删除组件"):
                                if remove_viz_component(component['id']):
                                    st.rerun()
        
        # 添加新组件
        with st.expander("➕ 添加自定义组件"):
            col1, col2 = st.columns(2)
            with col1:
                new_component_name = st.text_input("组件名称")
                new_component_type = st.selectbox("组件类型", ['chart', 'table', 'metric', 'widget'])
                new_component_category = st.selectbox("组件分类", list(category_names.keys()))
            
            with col2:
                new_component_icon = st.text_input("图标 (emoji)", "🎨")
                new_component_description = st.text_input("描述")
                new_component_persistent = st.checkbox("持久化保存", value=True)
            
            new_component_config = st.text_area(
                "配置 (JSON格式)", 
                '{"color": "blue", "style": "modern"}',
                help="组件的配置参数，必须是有效的JSON格式"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("添加组件", type="primary", use_container_width=True):
                    if new_component_name:
                        if add_custom_viz_component(
                            new_component_name, 
                            new_component_type, 
                            new_component_config,
                            new_component_category,
                            new_component_description,
                            new_component_icon,
                            new_component_persistent
                        ):
                            st.success(f"已添加组件: {new_component_name}")
                            st.rerun()
                    else:
                        st.error("请输入组件名称")
            
            with col2:
                if st.button("重置表单", use_container_width=True):
                    st.rerun()
        
        # 组件导入导出
        with st.expander("📦 组件导入导出"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**导出组件**")
                if st.button("导出所有自定义组件", use_container_width=True):
                    export_data = export_custom_components()
                    if export_data:
                        st.download_button(
                            label="下载组件配置文件",
                            data=export_data,
                            file_name=f"viz_components_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
            
            with col2:
                st.markdown("**导入组件**")
                uploaded_config = st.file_uploader(
                    "选择组件配置文件",
                    type=['json'],
                    help="上传之前导出的组件配置文件"
                )
                
                if uploaded_config is not None:
                    if st.button("导入组件", use_container_width=True):
                        if import_custom_components(uploaded_config):
                            st.success("组件导入成功！")
                            st.rerun()
                        else:
                            st.error("组件导入失败")
    
    # AI对话界面
    
    # 显示聊天历史 - 自适应高度
    chat_container = st.container()
    with chat_container:
            for i, message in enumerate(st.session_state['chat_history']):
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                else:
                    with st.chat_message("assistant"):
                        st.write(message['content'])
                        
                        # 如果消息包含图表数据，显示图表
                        if 'chart' in message and message['chart']:
                            chart_data = message['chart']
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
    
    # 数据概览卡片
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #495057 0%, #343a40 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 30px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <h3 style="margin: 0 0 15px 0; font-size: 1.2em;">📊 数据概览</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 1.8em; font-weight: bold;">{}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">总行数</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8em; font-weight: bold;">{}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">总列数</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8em; font-weight: bold;">{}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">数值列</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8em; font-weight: bold;">{:.1f}%</div>
                <div style="font-size: 0.9em; opacity: 0.9;">缺失值</div>
            </div>
        </div>
    </div>
    """.format(
        len(df),
        len(df.columns),
        len(df.select_dtypes(include=[np.number]).columns),
        (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    ), unsafe_allow_html=True)
    
    # Grok风格的预设问题布局
    st.markdown("### 🎯 智能提问")
    
    # 预设问题分类
    question_categories = {
        "🔍 数据探索": [
            "分析这个数据集的主要特征",
            "数据质量如何？有什么问题？",
            "找出数据中的异常值"
        ],
        "📊 可视化建议": [
            "推荐适合的可视化方法",
            "创建数据分布图表",
            "生成相关性热力图"
        ],
        "🔗 关系分析": [
            "哪些变量之间可能存在相关性？",
            "识别数据中的模式和趋势",
            "分析变量间的因果关系"
        ]
    }
    
    # 使用标签页显示不同类别的问题
    tabs = st.tabs(list(question_categories.keys()))
    
    for tab, (category, questions) in zip(tabs, question_categories.items()):
        with tab:
            # 使用网格布局显示问题按钮
            cols = st.columns(2)
            for i, question in enumerate(questions):
                with cols[i % 2]:
                    if st.button(question, key=f"quick_q_{category}_{i}", use_container_width=True):
                        # 添加用户问题到聊天历史
                        st.session_state['chat_history'].append({
                            'role': 'user',
                            'content': question
                        })
                        
                        # 生成AI回答
                        ai_response = generate_ai_insight(df, question)
                        
                        # 处理AI响应（可能包含图表数据）
                        if isinstance(ai_response, dict) and 'chart' in ai_response:
                            # 如果响应包含图表数据，分别保存文本和图表
                            st.session_state['chat_history'].append({
                                'role': 'assistant',
                                'content': ai_response['text'],
                                'chart': ai_response['chart']
                            })
                        else:
                            # 普通文本响应
                            st.session_state['chat_history'].append({
                                'role': 'assistant',
                                'content': ai_response
                            })
                        
                        st.rerun()
    
    # 用户输入区域
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.chat_input("💭 请输入您的问题...")
    
    with col2:
        if st.button("🗑️ 清除历史", use_container_width=True):
            st.session_state['chat_history'] = []
            st.rerun()
    
    if user_input:
        # 添加用户消息
        st.session_state['chat_history'].append({
            'role': 'user',
            'content': user_input
        })
        
        # 生成AI回答
        with st.spinner("🤖 AI正在分析中..."):
            ai_response = generate_ai_insight(df, user_input)
            
            # 处理AI响应（可能包含图表数据）
            if isinstance(ai_response, dict) and 'chart' in ai_response:
                # 如果响应包含图表数据，分别保存文本和图表
                st.session_state['chat_history'].append({
                    'role': 'assistant',
                    'content': ai_response['text'],
                    'chart': ai_response['chart']
                })
            else:
                # 普通文本响应
                st.session_state['chat_history'].append({
                    'role': 'assistant',
                    'content': ai_response
                })
        
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
                        # 在AI响应中添加图表说明
                        chart_description = visualization_config.get('description', '已生成相关图表')
                        ai_response += f"\n\n📊 {chart_description}"
                        
                        # 将图表数据保存到AI响应中，以便在聊天历史中持久显示
                        return {
                            'text': ai_response,
                            'chart': chart_result
                        }
                
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

def get_available_viz_components():
    """获取可用的可视化组件列表"""
    default_components = [
        {
            'id': 'smart_recommend',
            'name': '智能推荐',
            'icon': '🤖',
            'type': 'chart',
            'category': 'ai',
            'description': 'AI智能推荐最适合的图表类型',
            'config': {'auto_select': True, 'priority': 'high'},
            'persistent': False
        },
        {
            'id': 'line_chart',
            'name': '折线图',
            'icon': '📈',
            'type': 'chart',
            'category': 'trend',
            'description': '显示数据随时间的变化趋势',
            'config': {'chart_type': 'line', 'color': 'blue', 'line_width': 2, 'show_markers': True},
            'persistent': True
        },
        {
            'id': 'bar_chart',
            'name': '柱状图',
            'icon': '📊',
            'type': 'chart',
            'category': 'comparison',
            'description': '比较不同类别的数值大小',
            'config': {'chart_type': 'bar', 'color': 'green', 'orientation': 'vertical', 'show_values': True},
            'persistent': True
        },
        {
            'id': 'scatter_plot',
            'name': '散点图',
            'icon': '🔵',
            'type': 'chart',
            'category': 'correlation',
            'description': '显示两个变量之间的关系',
            'config': {'chart_type': 'scatter', 'color': 'red', 'size': 8, 'show_trend': True, 'alpha': 0.7},
            'persistent': True
        },
        {
            'id': 'pie_chart',
            'name': '饼图',
            'icon': '🥧',
            'type': 'chart',
            'category': 'proportion',
            'description': '显示各部分占整体的比例',
            'config': {'chart_type': 'pie', 'show_percentage': True, 'explode_max': True, 'color_palette': 'Set3'},
            'persistent': True
        },
        {
            'id': 'heatmap',
            'name': '热力图',
            'icon': '🔥',
            'type': 'chart',
            'category': 'correlation',
            'description': '显示数据的密度分布或相关性',
            'config': {'chart_type': 'heatmap', 'colormap': 'viridis', 'show_values': True, 'center': 0},
            'persistent': True
        },
        {
            'id': 'histogram',
            'name': '直方图',
            'icon': '📊',
            'type': 'chart',
            'category': 'distribution',
            'description': '显示数据的分布情况',
            'config': {'chart_type': 'histogram', 'bins': 30, 'density': False, 'alpha': 0.8},
            'persistent': True
        },
        {
            'id': 'box_plot',
            'name': '箱线图',
            'icon': '📦',
            'type': 'chart',
            'category': 'distribution',
            'description': '显示数据的分布和异常值',
            'config': {'chart_type': 'box', 'show_outliers': True, 'notch': False, 'color': 'lightblue'},
            'persistent': True
        },
        {
            'id': 'violin_plot',
            'name': '小提琴图',
            'icon': '🎻',
            'type': 'chart',
            'category': 'distribution',
            'description': '结合箱线图和密度图的优势',
            'config': {'chart_type': 'violin', 'show_density': True, 'inner': 'box', 'palette': 'muted'},
            'persistent': True
        },
        {
            'id': 'area_chart',
            'name': '面积图',
            'icon': '🏔️',
            'type': 'chart',
            'category': 'trend',
            'description': '强调数量随时间的累积变化',
            'config': {'chart_type': 'area', 'fill_alpha': 0.7, 'stacked': False, 'color': 'skyblue'},
            'persistent': True
        },
        {
            'id': 'radar_chart',
            'name': '雷达图',
            'icon': '🎯',
            'type': 'chart',
            'category': 'multivariate',
            'description': '多维数据的综合展示',
            'config': {'chart_type': 'radar', 'fill_area': True, 'line_width': 2, 'alpha': 0.25},
            'persistent': True
        },
        {
            'id': 'metric_card',
            'name': '指标卡片',
            'icon': '📋',
            'type': 'metric',
            'category': 'summary',
            'description': '显示关键指标和KPI',
            'config': {'show_delta': True, 'color_coding': True, 'format': 'auto'},
            'persistent': True
        },
        {
            'id': 'data_table',
            'name': '数据表格',
            'icon': '📊',
            'type': 'table',
            'category': 'raw_data',
            'description': '以表格形式展示原始数据',
            'config': {'pagination': True, 'sortable': True, 'searchable': True, 'max_rows': 100},
            'persistent': True
        }
    ]
    
    # 从持久化存储加载自定义组件
    custom_components = load_custom_components()
    
    # 从session state获取临时组件
    temp_components = st.session_state.get('temp_viz_components', [])
    
    return default_components + custom_components + temp_components

def add_custom_viz_component(name, component_type, config_str, category='custom', description='', icon='🎨', persistent=True):
    """添加自定义可视化组件"""
    try:
        import json
        import uuid
        from datetime import datetime
        
        config = json.loads(config_str)
        
        # 生成唯一ID
        component_id = f"custom_{uuid.uuid4().hex[:8]}_{name.lower().replace(' ', '_').replace('-', '_')}"
        
        new_component = {
            'id': component_id,
            'name': name,
            'icon': icon,
            'type': component_type,
            'category': category,
            'description': description,
            'config': config,
            'custom': True,
            'persistent': persistent,
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        if persistent:
            # 保存到持久化存储
            save_custom_component(new_component)
        else:
            # 保存到临时session state
            if 'temp_viz_components' not in st.session_state:
                st.session_state['temp_viz_components'] = []
            st.session_state['temp_viz_components'].append(new_component)
        
        # 更新可视化组件列表
        st.session_state['viz_components'] = get_available_viz_components()
        
        return True
        
    except json.JSONDecodeError:
        st.error("配置格式错误，请输入有效的JSON格式")
        return False
    except Exception as e:
        st.error(f"添加组件失败: {str(e)}")
        return False

def remove_viz_component(component_id):
    """删除可视化组件"""
    try:
        # 从持久化存储删除
        if delete_custom_component(component_id):
            st.success(f"已删除组件: {component_id}")
        
        # 从临时组件删除
        if 'temp_viz_components' in st.session_state:
            st.session_state['temp_viz_components'] = [
                comp for comp in st.session_state['temp_viz_components']
                if comp['id'] != component_id
            ]
        
        # 更新可视化组件列表
        st.session_state['viz_components'] = get_available_viz_components()
        
        return True
        
    except Exception as e:
        st.error(f"删除组件失败: {str(e)}")
        return False

def get_chart_recommendations(df):
    """获取图表推荐"""
    try:
        import numpy as np
        
        # 构建数据上下文
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        data_context = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': numeric_columns,
            'categorical_columns': categorical_columns,
            'column_info': {
                col: {
                    'type': str(df[col].dtype),
                    'unique_values': df[col].nunique(),
                    'null_count': df[col].isnull().sum()
                } for col in df.columns
            }
        }
        
        # 调用后端推荐API
        response = requests.post(
            'http://localhost:7701/api/chart/recommendations',
            json={
                'data_context': data_context,
                'analysis_goal': 'general_exploration'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('recommendations', [])
        else:
            st.error(f"推荐API调用失败: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {str(e)}")
        return None
    except Exception as e:
        st.error(f"获取推荐时出错: {str(e)}")
        return None

def generate_chart_from_config(df, visualization_config):
    """根据可视化配置生成图表"""
    try:
        # 如果用户选择了特定的图表类型，覆盖AI推荐
        if (st.session_state.get('selected_chart_type') and 
            st.session_state['selected_chart_type'] != 'auto'):
            visualization_config['chart_type'] = st.session_state['selected_chart_type']
        
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

def load_custom_components():
    """从持久化存储加载自定义组件"""
    try:
        import os
        import json
        
        config_dir = os.path.expanduser("~/.jdc_data_tool")
        config_file = os.path.join(config_dir, "custom_components.json")
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                components_data = json.load(f)
                return components_data.get('components', [])
        
        return []
        
    except Exception as e:
        st.error(f"加载自定义组件失败: {str(e)}")
        return []

def save_custom_component(component):
    """保存自定义组件到持久化存储"""
    try:
        import os
        import json
        
        config_dir = os.path.expanduser("~/.jdc_data_tool")
        os.makedirs(config_dir, exist_ok=True)
        config_file = os.path.join(config_dir, "custom_components.json")
        
        # 加载现有组件
        components = load_custom_components()
        
        # 检查是否已存在同ID组件
        existing_index = None
        for i, comp in enumerate(components):
            if comp['id'] == component['id']:
                existing_index = i
                break
        
        if existing_index is not None:
            components[existing_index] = component
        else:
            components.append(component)
        
        # 保存到文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'components': components,
                'last_updated': pd.Timestamp.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        st.error(f"保存组件失败: {str(e)}")
        return False

def delete_custom_component(component_id):
    """从持久化存储删除自定义组件"""
    try:
        import os
        import json
        
        config_dir = os.path.expanduser("~/.jdc_data_tool")
        config_file = os.path.join(config_dir, "custom_components.json")
        
        if not os.path.exists(config_file):
            return False
        
        # 加载现有组件
        components = load_custom_components()
        
        # 过滤掉要删除的组件
        original_count = len(components)
        components = [comp for comp in components if comp['id'] != component_id]
        
        if len(components) == original_count:
            return False  # 没有找到要删除的组件
        
        # 保存更新后的组件列表
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                'components': components,
                'last_updated': pd.Timestamp.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        st.error(f"删除组件失败: {str(e)}")
        return False

def export_custom_components():
    """导出所有自定义组件"""
    try:
        import json
        
        components = load_custom_components()
        
        export_data = {
            'version': '1.0',
            'export_time': pd.Timestamp.now().isoformat(),
            'components': components,
            'metadata': {
                'total_components': len(components),
                'export_source': 'JDC Data Analysis Tool'
            }
        }
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)
        
    except Exception as e:
        st.error(f"导出组件失败: {str(e)}")
        return None

def import_custom_components(uploaded_file):
    """导入自定义组件"""
    try:
        import json
        
        # 读取上传的文件
        content = uploaded_file.read().decode('utf-8')
        import_data = json.loads(content)
        
        # 验证文件格式
        if 'components' not in import_data:
            st.error("无效的组件配置文件格式")
            return False
        
        imported_components = import_data['components']
        
        # 逐个导入组件
        success_count = 0
        for component in imported_components:
            # 为导入的组件生成新的ID以避免冲突
            import uuid
            original_id = component['id']
            component['id'] = f"imported_{uuid.uuid4().hex[:8]}_{original_id}"
            component['imported'] = True
            component['import_time'] = pd.Timestamp.now().isoformat()
            
            if save_custom_component(component):
                success_count += 1
        
        st.success(f"成功导入 {success_count}/{len(imported_components)} 个组件")
        return True
        
    except json.JSONDecodeError:
        st.error("文件格式错误，请确保是有效的JSON文件")
        return False
    except Exception as e:
        st.error(f"导入组件失败: {str(e)}")
        return False

if __name__ == "__main__":
    main()