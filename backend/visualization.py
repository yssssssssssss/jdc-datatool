# 可视化生成逻辑
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
import io
from typing import Dict, List, Any

class VisualizationGenerator:
    def __init__(self):
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_style("whitegrid")
    
    def generate_histogram(self, data: pd.Series, title: str = "直方图") -> str:
        """生成直方图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data.dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('数值', fontsize=12)
        ax.set_ylabel('频次', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def generate_scatter_plot(self, x_data: pd.Series, y_data: pd.Series, 
                            title: str = "散点图") -> str:
        """生成散点图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x_data, y_data, alpha=0.6, color='coral')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_data.name or 'X轴', fontsize=12)
        ax.set_ylabel(y_data.name or 'Y轴', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def generate_line_chart(self, data: pd.DataFrame, x_col: str, y_col: str,
                          title: str = "折线图") -> str:
        """生成折线图"""
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(data[x_col], data[y_col], marker='o', linewidth=2, markersize=4)
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
        data.plot(kind='bar', ax=ax, color='lightgreen', alpha=0.8)
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
        colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
        wedges, texts, autotexts = ax.pie(data.values, labels=data.index, 
                                         autopct='%1.1f%%', colors=colors,
                                         startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def generate_heatmap(self, data: pd.DataFrame, title: str = "热力图") -> str:
        """生成热力图"""
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(data.corr(), annot=True, cmap='coolwarm', center=0,
                   square=True, ax=ax, cbar_kws={'shrink': 0.8})
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def generate_box_plot(self, data: pd.DataFrame, column: str, 
                         title: str = "箱线图") -> str:
        """生成箱线图"""
        fig, ax = plt.subplots(figsize=(8, 6))
        data.boxplot(column=column, ax=ax)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('数值', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._fig_to_base64(fig)
    
    def generate_interactive_plot(self, data: pd.DataFrame, chart_type: str,
                                x_col: str, y_col: str = None) -> Dict:
        """生成交互式图表"""
        try:
            if chart_type == 'scatter':
                fig = px.scatter(data, x=x_col, y=y_col, 
                               title=f'{x_col} vs {y_col} 散点图')
            elif chart_type == 'line':
                fig = px.line(data, x=x_col, y=y_col,
                            title=f'{x_col} vs {y_col} 折线图')
            elif chart_type == 'bar':
                fig = px.bar(data, x=x_col, y=y_col,
                           title=f'{x_col} 柱状图')
            elif chart_type == 'histogram':
                fig = px.histogram(data, x=x_col,
                                 title=f'{x_col} 直方图')
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