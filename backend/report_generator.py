# 报告生成逻辑
import pandas as pd
import numpy as np
from datetime import datetime
from jinja2 import Template
import json
from typing import Dict, List, Any

class ReportGenerator:
    def __init__(self):
        self.report_template = self._get_html_template()
    
    def generate_data_report(self, data: pd.DataFrame, analysis_results: Dict,
                           charts: List[str], insights: str = "") -> str:
        """生成完整的数据分析报告"""
        
        # 基础统计信息
        basic_stats = self._get_basic_statistics(data)
        
        # 数据质量评估
        quality_assessment = self._assess_data_quality(data)
        
        # 生成报告内容
        report_data = {
            'title': '数据分析报告',
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'basic_stats': basic_stats,
            'quality_assessment': quality_assessment,
            'analysis_results': analysis_results,
            'charts': charts,
            'insights': insights,
            'recommendations': self._generate_recommendations(data, quality_assessment)
        }
        
        # 渲染HTML报告
        template = Template(self.report_template)
        html_report = template.render(**report_data)
        
        return html_report
    
    def generate_summary_report(self, data: pd.DataFrame) -> Dict:
        """生成数据摘要报告"""
        summary = {
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns),
                'memory_usage': f"{data.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
                'column_types': data.dtypes.value_counts().to_dict()
            },
            'missing_data': {
                'total_missing': data.isnull().sum().sum(),
                'missing_percentage': f"{(data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100:.2f}%",
                'columns_with_missing': data.columns[data.isnull().any()].tolist()
            },
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # 数值列摘要
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = {
                'columns': numeric_cols.tolist(),
                'statistics': data[numeric_cols].describe().to_dict()
            }
        
        # 分类列摘要
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            cat_summary = {}
            for col in categorical_cols:
                cat_summary[col] = {
                    'unique_values': data[col].nunique(),
                    'most_frequent': data[col].mode().iloc[0] if not data[col].mode().empty else 'N/A',
                    'top_categories': data[col].value_counts().head(5).to_dict()
                }
            summary['categorical_summary'] = cat_summary
        
        return summary
    
    def _get_basic_statistics(self, data: pd.DataFrame) -> Dict:
        """获取基础统计信息"""
        return {
            'shape': data.shape,
            'columns': data.columns.tolist(),
            'dtypes': data.dtypes.astype(str).to_dict(),
            'memory_usage': data.memory_usage(deep=True).to_dict(),
            'describe': data.describe(include='all').to_dict()
        }
    
    def _assess_data_quality(self, data: pd.DataFrame) -> Dict:
        """评估数据质量"""
        quality_issues = []
        
        # 检查缺失值
        missing_counts = data.isnull().sum()
        high_missing_cols = missing_counts[missing_counts > len(data) * 0.5].index.tolist()
        if high_missing_cols:
            quality_issues.append(f"高缺失率列: {', '.join(high_missing_cols)}")
        
        # 检查重复行
        duplicate_count = data.duplicated().sum()
        if duplicate_count > 0:
            quality_issues.append(f"发现 {duplicate_count} 行重复数据")
        
        # 检查数据类型一致性
        for col in data.columns:
            if data[col].dtype == 'object':
                try:
                    pd.to_numeric(data[col], errors='raise')
                    quality_issues.append(f"列 '{col}' 可能应该是数值类型")
                except:
                    pass
        
        return {
            'overall_score': max(0, 100 - len(quality_issues) * 10),
            'issues': quality_issues,
            'missing_data_percentage': (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100,
            'duplicate_rows': duplicate_count
        }
    
    def _generate_recommendations(self, data: pd.DataFrame, quality_assessment: Dict) -> List[str]:
        """生成数据处理建议"""
        recommendations = []
        
        if quality_assessment['missing_data_percentage'] > 10:
            recommendations.append("建议处理缺失值：可以考虑删除、填充或插值")
        
        if quality_assessment['duplicate_rows'] > 0:
            recommendations.append("建议删除重复行以提高数据质量")
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            recommendations.append("可以进行相关性分析，识别变量间的关系")
        
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            recommendations.append("分类变量可以进行编码处理，便于机器学习建模")
        
        if len(data) > 10000:
            recommendations.append("数据量较大，建议考虑采样或分批处理")
        
        return recommendations
    
    def _get_html_template(self) -> str:
        """获取HTML报告模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #6c757d;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .section h2 {
            color: #495057;
            border-bottom: 2px solid #6c757d;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #6c757d;
        }
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .recommendations {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #6c757d;
        }
        .quality-score {
            font-size: 2em;
            font-weight: bold;
            color: {% if quality_assessment.overall_score >= 80 %}#2c2c2c{% elif quality_assessment.overall_score >= 60 %}#495057{% else %}#6c757d{% endif %};
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>生成时间: {{ generated_time }}</p>
        </div>
        
        <div class="section">
            <h2>数据概览</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>数据维度</h4>
                    <p>{{ basic_stats.shape[0] }} 行 × {{ basic_stats.shape[1] }} 列</p>
                </div>
                <div class="stat-card">
                    <h4>数据质量评分</h4>
                    <p class="quality-score">{{ quality_assessment.overall_score }}/100</p>
                </div>
                <div class="stat-card">
                    <h4>缺失数据</h4>
                    <p>{{ "%.2f"|format(quality_assessment.missing_data_percentage) }}%</p>
                </div>
                <div class="stat-card">
                    <h4>重复行</h4>
                    <p>{{ quality_assessment.duplicate_rows }} 行</p>
                </div>
            </div>
        </div>
        
        {% if charts %}
        <div class="section">
            <h2>数据可视化</h2>
            {% for chart in charts %}
            <div class="chart-container">
                <img src="{{ chart }}" alt="数据图表">
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if insights %}
        <div class="section">
            <h2>数据洞察</h2>
            <div>{{ insights|safe }}</div>
        </div>
        {% endif %}
        
        {% if recommendations %}
        <div class="section">
            <h2>处理建议</h2>
            <div class="recommendations">
                <ul>
                {% for rec in recommendations %}
                    <li>{{ rec }}</li>
                {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>质量问题</h2>
            {% if quality_assessment.issues %}
            <ul>
            {% for issue in quality_assessment.issues %}
                <li>{{ issue }}</li>
            {% endfor %}
            </ul>
            {% else %}
            <p style="color: #2c2c2c;">未发现明显的数据质量问题</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
        """
    
    def export_to_json(self, report_data: Dict, filename: str) -> str:
        """导出报告数据为JSON格式"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            return f"报告已导出到: {filename}"
        except Exception as e:
            return f"导出失败: {str(e)}"