# 可视化生成逻辑
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免线程问题
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
import io
from typing import Dict, List, Any, Optional

class VisualizationGenerator:
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_style("whitegrid")
    
    def generate_histogram(self, data: pd.Series, title: str = "直方图") -> str:
        """生成直方图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data.dropna(), bins=30, alpha=0.7, color='#6c757d', edgecolor='black')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('数值', fontsize=12)
        ax.set_ylabel('频次', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def generate_scatter_plot(self, x_data: pd.Series, y_data: pd.Series, 
                            title: str = "散点图") -> str:
        """生成散点图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x_data, y_data, alpha=0.6, color='#495057')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_data.name or 'X轴', fontsize=12)
        ax.set_ylabel(y_data.name or 'Y轴', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def generate_line_chart(self, data: pd.DataFrame, x_col: str, y_col: str,
                          title: str = "折线图") -> str:
        """生成折线图"""
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data[x_col], data[y_col], marker='o', linewidth=2, markersize=4, color='#495057')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_col, fontsize=12)
        ax.set_ylabel(y_col, fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def generate_bar_chart(self, data: pd.Series, title: str = "柱状图") -> str:
        """生成柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        data.plot(kind='bar', ax=ax, color='#6c757d', alpha=0.8)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('类别', fontsize=12)
        ax.set_ylabel('数值', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def generate_pie_chart(self, data: pd.Series, title: str = "饼图") -> str:
        """生成饼图"""
        fig, ax = plt.subplots(figsize=(8, 8))
        # 使用黑白灰色调
        colors = ['#2c2c2c', '#495057', '#6c757d', '#adb5bd', '#dee2e6', '#f8f9fa'] * (len(data) // 6 + 1)
        colors = colors[:len(data)]
        wedges, texts, autotexts = ax.pie(data.values, labels=data.index, 
                                         autopct='%1.1f%%', colors=colors,
                                         startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def generate_heatmap(self, data: pd.DataFrame, title: str = "热力图") -> str:
        """生成热力图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(data.corr(), annot=True, cmap='gray', center=0,
                   square=True, ax=ax, cbar_kws={'shrink': 0.8})
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def generate_box_plot(self, data: pd.DataFrame, column: str, 
                         title: str = "箱线图") -> str:
        """生成箱线图"""
        fig, ax = plt.subplots(figsize=(8, 6))
        bp = data.boxplot(column=column, ax=ax, patch_artist=True)
        # 设置箱线图颜色为黑白灰
        for patch in ax.findobj(plt.matplotlib.patches.PathPatch):
            patch.set_facecolor('#6c757d')
            patch.set_edgecolor('#2c2c2c')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('数值', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def generate_interactive_plot(self, data: pd.DataFrame, chart_type: str,
                                x_col: str, y_col: str = None) -> Dict:
        """生成交互式图表"""
        try:
            # 定义黑白灰色调
            color_discrete_sequence = ['#2c2c2c', '#495057', '#6c757d', '#adb5bd']
            
            if chart_type == 'scatter':
                fig = px.scatter(data, x=x_col, y=y_col, 
                               title=f'{x_col} vs {y_col} 散点图',
                               color_discrete_sequence=color_discrete_sequence)
            elif chart_type == 'line':
                fig = px.line(data, x=x_col, y=y_col,
                            title=f'{x_col} vs {y_col} 折线图',
                            color_discrete_sequence=color_discrete_sequence)
            elif chart_type == 'bar':
                fig = px.bar(data, x=x_col, y=y_col,
                           title=f'{x_col} 柱状图',
                           color_discrete_sequence=color_discrete_sequence)
            elif chart_type == 'histogram':
                fig = px.histogram(data, x=x_col,
                                 title=f'{x_col} 直方图',
                                 color_discrete_sequence=color_discrete_sequence)
            else:
                return {"error": "不支持的图表类型"}
            
            return {"html": fig.to_html(include_plotlyjs='cdn')}
            
        except Exception as e:
            return {"error": f"生成交互式图表失败: {str(e)}"}
    
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图表转换为base64字符串"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"
    
    def generate_chart(self, df: pd.DataFrame, config: Dict) -> Optional[str]:
        """统一的图表生成入口方法"""
        import logging
        
        chart_type = config.get('chart_type')
        columns = config.get('columns', [])
        title = config.get('title', '数据图表')
        
        if not chart_type or not columns:
            logging.warning(f"图表配置不完整: chart_type={chart_type}, columns={columns}")
            return None
        
        # 验证列是否存在于数据框中
        valid_columns = [col for col in columns if col in df.columns]
        if not valid_columns:
            logging.warning(f"指定的列不存在于数据框中: {columns}")
            return None
        
        try:
            if chart_type == 'histogram' and len(valid_columns) >= 1:
                return self.generate_histogram(df[valid_columns[0]], title)
                
            elif chart_type == 'scatter' and len(valid_columns) >= 2:
                return self.generate_scatter_plot(df[valid_columns[0]], df[valid_columns[1]], title)
                
            elif chart_type == 'line' and len(valid_columns) >= 2:
                return self.generate_line_chart(df, valid_columns[0], valid_columns[1], title)
                
            elif chart_type == 'bar' and len(valid_columns) >= 1:
                # 处理分类数据的分组统计
                if df[valid_columns[0]].dtype == 'object' or df[valid_columns[0]].dtype.name == 'category':
                    if len(valid_columns) >= 2 and df[valid_columns[1]].dtype in ['int64', 'float64']:
                        # 如果有第二列数值数据，计算分组平均值
                        grouped_data = df.groupby(valid_columns[0])[valid_columns[1]].mean()
                    else:
                        # 否则计算计数
                        grouped_data = df[valid_columns[0]].value_counts()
                    return self.generate_bar_chart(grouped_data, title)
                else:
                    # 对于数值数据，直接使用
                    return self.generate_bar_chart(df[valid_columns[0]], title)
                    
            elif chart_type == 'pie' and len(valid_columns) >= 1:
                # 饼图需要分类数据或计数数据
                if df[valid_columns[0]].dtype == 'object' or df[valid_columns[0]].dtype.name == 'category':
                    pie_data = df[valid_columns[0]].value_counts()
                else:
                    # 对于数值数据，创建分组
                    pie_data = pd.cut(df[valid_columns[0]], bins=5).value_counts()
                return self.generate_pie_chart(pie_data, title)
                
            elif chart_type == 'heatmap':
                # 热力图需要多个数值列
                numeric_df = df[valid_columns].select_dtypes(include=['number'])
                if not numeric_df.empty and len(numeric_df.columns) > 1:
                    return self.generate_heatmap(numeric_df, title)
                else:
                    logging.warning("热力图需要至少2个数值列")
                    return None
                    
            elif chart_type == 'box' and len(valid_columns) >= 1:
                return self.generate_box_plot(df, valid_columns[0], title)
                
            elif chart_type == 'violin' and len(valid_columns) >= 1:
                # 小提琴图暂时用箱线图替代
                return self.generate_box_plot(df, valid_columns[0], title)
                
            elif chart_type == 'area' and len(valid_columns) >= 2:
                # 面积图暂时用折线图替代
                return self.generate_line_chart(df, valid_columns[0], valid_columns[1], title)
                
            elif chart_type == 'radar' and len(valid_columns) >= 3:
                # 雷达图暂时用相关性热力图替代
                numeric_df = df[valid_columns].select_dtypes(include=['number'])
                if not numeric_df.empty:
                    return self.generate_heatmap(numeric_df.corr(), f"{title} - 相关性分析")
                else:
                    logging.warning("雷达图需要数值列")
                    return None
            else:
                logging.warning(f"不支持的图表类型或列数不足: {chart_type}, 列数: {len(valid_columns)}")
                return None
                
        except Exception as e:
            logging.error(f"图表生成失败: {e}, 配置: {config}")
            return None

    def get_chart_suggestions(self, data: pd.DataFrame) -> List[Dict]:
        """根据数据类型推荐图表"""
        suggestions = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
        
        # 数值列建议
        for col in numeric_cols:
            suggestions.append({
                "column": col,
                "chart_type": "histogram",
                "description": f"{col}的分布直方图"
            })
            suggestions.append({
                "column": col,
                "chart_type": "box",
                "description": f"{col}的箱线图"
            })
        
        # 分类列建议
        for col in categorical_cols:
            suggestions.append({
                "column": col,
                "chart_type": "bar",
                "description": f"{col}的计数柱状图"
            })
            suggestions.append({
                "column": col,
                "chart_type": "pie",
                "description": f"{col}的分布饼图"
            })
        
        # 相关性热力图
        if len(numeric_cols) > 1:
            suggestions.append({
                "columns": numeric_cols,
                "chart_type": "heatmap",
                "description": "数值变量相关性热力图"
            })
        
        # 散点图建议
        if len(numeric_cols) >= 2:
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    suggestions.append({
                        "columns": [numeric_cols[i], numeric_cols[j]],
                        "chart_type": "scatter",
                        "description": f"{numeric_cols[i]} vs {numeric_cols[j]} 散点图"
                    })
        
        return suggestions
