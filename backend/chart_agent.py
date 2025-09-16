# 图表生成代理 - 专门负责图表生成的独立服务
import json
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import os
import importlib.util

# 直接导入visualization.py文件
viz_spec = importlib.util.spec_from_file_location("visualization_module", os.path.join(os.path.dirname(__file__), "visualization.py"))
viz_module = importlib.util.module_from_spec(viz_spec)
viz_spec.loader.exec_module(viz_module)
VisualizationGenerator = viz_module.VisualizationGenerator

from llm_analyzer import LLMAnalyzer

class ChartAgent:
    """专门负责图表生成的智能代理"""
    
    def __init__(self):
        self.chart_generator = VisualizationGenerator()
        self.llm_analyzer = LLMAnalyzer()
        
    def analyze_and_generate_chart(self, user_question: str, df: pd.DataFrame, data_context: Dict, chat_history: List = None) -> Dict:
        """分析用户需求并自动生成图表"""
        try:
            # 第一步：使用LLM分析用户需求
            if chat_history is None:
                chat_history = []
            analysis_result = self.llm_analyzer.chat_with_data(user_question, data_context, chat_history)
            
            if not analysis_result.get('success'):
                return {
                    'success': False,
                    'error': analysis_result.get('error', '分析失败'),
                    'response': analysis_result.get('response', ''),
                    'chart': None
                }
            
            ai_response = analysis_result['response']
            visualization_config = analysis_result.get('visualization', {'needed': False})
            
            # 第二步：如果AI没有返回可视化配置，尝试智能推断
            if not visualization_config.get('needed', False):
                visualization_config = self._infer_visualization_from_question(user_question, data_context)
            
            # 第三步：生成图表
            chart_result = None
            if visualization_config.get('needed', False):
                chart_result = self._generate_chart_from_config(df, visualization_config)
                
                if chart_result:
                    # 添加图表说明到AI响应中
                    chart_description = visualization_config.get('description', '已生成相关图表')
                    ai_response += f"\n\n📊 {chart_description}"
            
            return {
                'success': True,
                'response': ai_response,
                'chart': chart_result,
                'visualization_config': visualization_config,
                'structured': analysis_result.get('structured', False)
            }
            
        except Exception as e:
            logging.error(f"图表代理处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"图表生成过程中出现错误：{str(e)}",
                'chart': None
            }
    
    def _infer_visualization_from_question(self, question: str, data_context: Dict) -> Dict:
        """从用户问题中智能推断可视化需求"""
        question_lower = question.lower()
        columns = data_context.get('columns', [])
        numeric_columns = data_context.get('numeric_columns', [])
        categorical_columns = data_context.get('categorical_columns', [])
        
        # 图表关键词映射
        chart_keywords = {
            'histogram': ['分布', '直方图', 'histogram', '频率'],
            'scatter': ['散点', '相关', 'scatter', '关系'],
            'line': ['折线', '趋势', 'line', '时间', '变化'],
            'bar': ['柱状', '条形', 'bar', '比较', '排名', '最高', '最低', 'top'],
            'pie': ['饼图', 'pie', '占比', '比例', '份额'],
            'box': ['箱线', 'box', '异常', '分位'],
            'heatmap': ['热力', 'heatmap', '相关性矩阵']
        }
        
        # 检测图表类型
        detected_chart_type = None
        for chart_type, keywords in chart_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                detected_chart_type = chart_type
                break
        
        # 如果没有明确的图表关键词，根据数据类型和问题内容推断
        if not detected_chart_type:
            if any(keyword in question_lower for keyword in ['最高', '最低', 'top', '排名', '比较']):
                detected_chart_type = 'bar'
            elif any(keyword in question_lower for keyword in ['趋势', '变化', '时间']):
                detected_chart_type = 'line'
            elif len(numeric_columns) >= 2:
                detected_chart_type = 'scatter'
            elif len(numeric_columns) == 1:
                detected_chart_type = 'histogram'
        
        # 如果仍然没有检测到，默认使用柱状图
        if not detected_chart_type:
            detected_chart_type = 'bar'
        
        # 智能选择列
        selected_columns = self._select_relevant_columns(question, columns, numeric_columns, categorical_columns, detected_chart_type)
        
        return {
            'needed': True,
            'chart_type': detected_chart_type,
            'columns': selected_columns,
            'title': f'{detected_chart_type.title()}图表分析',
            'description': f'基于问题"{question}"自动生成的{detected_chart_type}图表',
            'auto_generated': True
        }
    
    def _select_relevant_columns(self, question: str, columns: List[str], numeric_columns: List[str], categorical_columns: List[str], chart_type: str) -> List[str]:
        """智能选择相关列"""
        question_lower = question.lower()
        selected = []
        
        # 从问题中提取提到的列名
        mentioned_columns = [col for col in columns if col.lower() in question_lower]
        
        if mentioned_columns:
            selected.extend(mentioned_columns)
        else:
            # 根据图表类型选择默认列
            if chart_type in ['bar', 'pie']:
                # 需要一个分类列和一个数值列
                if categorical_columns and numeric_columns:
                    selected.append(categorical_columns[0])
                    selected.append(numeric_columns[0])
            elif chart_type == 'line':
                # 优先选择时间相关的列
                time_columns = [col for col in columns if any(time_word in col.lower() for time_word in ['date', 'time', '时间', '日期'])]
                if time_columns and numeric_columns:
                    selected.append(time_columns[0])
                    selected.append(numeric_columns[0])
                elif len(numeric_columns) >= 2:
                    selected.extend(numeric_columns[:2])
            elif chart_type == 'scatter':
                # 选择两个数值列
                if len(numeric_columns) >= 2:
                    selected.extend(numeric_columns[:2])
            elif chart_type == 'histogram':
                # 选择一个数值列
                if numeric_columns:
                    selected.append(numeric_columns[0])
        
        # 确保至少有一列
        if not selected and columns:
            selected.append(columns[0])
        
        return selected[:3]  # 最多选择3列
    
    def _generate_chart_from_config(self, df: pd.DataFrame, config: Dict) -> Optional[str]:
        """根据配置生成图表"""
        try:
            chart_type = config.get('chart_type')
            columns = config.get('columns', [])
            title = config.get('title', '数据图表')
            
            if not chart_type or not columns:
                return None
            
            # 验证列是否存在
            valid_columns = [col for col in columns if col in df.columns]
            if not valid_columns:
                return None
            
            # 调用图表生成器
            chart_config = {
                'chart_type': chart_type,
                'columns': valid_columns,
                'title': title
            }
            
            return self.chart_generator.generate_chart(df, chart_config)
            
        except Exception as e:
            logging.error(f"图表生成失败: {e}")
            return None
    
    def generate_chart_recommendations(self, df: pd.DataFrame, data_context: Dict) -> List[Dict]:
        """生成图表推荐"""
        recommendations = []
        numeric_columns = data_context.get('numeric_columns', [])
        categorical_columns = data_context.get('categorical_columns', [])
        
        # 推荐柱状图（如果有分类列和数值列）
        if categorical_columns and numeric_columns:
            recommendations.append({
                'chart_type': 'bar',
                'title': f'{categorical_columns[0]} vs {numeric_columns[0]}',
                'description': f'比较不同{categorical_columns[0]}的{numeric_columns[0]}值',
                'columns': [categorical_columns[0], numeric_columns[0]]
            })
        
        # 推荐散点图（如果有多个数值列）
        if len(numeric_columns) >= 2:
            recommendations.append({
                'chart_type': 'scatter',
                'title': f'{numeric_columns[0]} vs {numeric_columns[1]}',
                'description': f'分析{numeric_columns[0]}和{numeric_columns[1]}的相关性',
                'columns': numeric_columns[:2]
            })
        
        # 推荐直方图（对于数值列）
        for col in numeric_columns[:2]:
            recommendations.append({
                'chart_type': 'histogram',
                'title': f'{col}分布图',
                'description': f'查看{col}的数据分布情况',
                'columns': [col]
            })
        
        return recommendations[:5]  # 最多返回5个推荐