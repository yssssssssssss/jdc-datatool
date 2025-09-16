# Flask 后端应用入口
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from dotenv import load_dotenv

# 加载环境变量 - 确保在导入其他模块前加载
load_dotenv()

from llm_analyzer import LLMAnalyzer
import sys
import os
import importlib.util

# 直接导入visualization.py文件
viz_spec = importlib.util.spec_from_file_location("visualization_module", os.path.join(os.path.dirname(__file__), "visualization.py"))
viz_module = importlib.util.module_from_spec(viz_spec)
viz_spec.loader.exec_module(viz_module)
VisualizationGenerator = viz_module.VisualizationGenerator
from chart_agent import ChartAgent
import pandas as pd
import numpy as np
import time
import sys
import os

# 添加可视化适配器路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'visualization'))
from adapters import adapter_manager, get_adapter_info, create_chart_with_adapter, compare_chart_adapters

app = Flask(__name__)

def create_sample_dataframe(data_context):
    """创建模拟数据框（实际应用中应该从数据源获取）"""
    # 如果有数据上下文，尝试创建相应的数据框
    if data_context.get('columns'):
        columns = data_context['columns']
        n_rows = 100  # 默认100行
        
        data = {}
        for col in columns:
            if col in data_context.get('numeric_columns', []):
                data[col] = np.random.randn(n_rows) * 100  # 放大数值范围
            else:
                data[col] = [f'SKU_{i%10}' for i in range(n_rows)]  # 模拟SKU数据
        
        return pd.DataFrame(data)
    else:
        # 默认示例数据
        return pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100),
            'category': [f'Cat_{i%3}' for i in range(100)]
        })
CORS(app)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return jsonify({"message": "JDC数据工具后端API"})

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """AI聊天接口"""
    import time
    start_time = time.time()
    
    try:
        app.logger.info("收到AI聊天请求")
        data = request.get_json()
        question = data.get('question', '')
        data_context = data.get('data_context', {})
        chat_history = data.get('chat_history', [])
        
        app.logger.info(f"问题: {question[:50]}...")
        app.logger.info(f"数据上下文: {data_context.get('shape', 'N/A')}")
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        # 创建模拟数据框
        df = create_sample_dataframe(data_context)
        app.logger.info(f"创建模拟数据框: {df.shape}")
        
        # 使用图表代理处理请求
        chart_agent = ChartAgent()
        app.logger.info("开始调用图表代理")
        result = chart_agent.analyze_and_generate_chart(question, df, data_context, chat_history)
        
        end_time = time.time()
        duration = end_time - start_time
        app.logger.info(f"AI聊天请求处理完成，总耗时: {duration:.2f}秒")
        
        return jsonify(result)
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        app.logger.error(f"AI聊天请求处理失败，耗时: {duration:.2f}秒，错误: {str(e)}")
        import traceback
        app.logger.error(f"详细错误信息: {traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f'处理请求时出现错误: {str(e)}'
        }), 500

@app.route('/api/ai/insights', methods=['POST'])
def ai_insights():
    """AI数据洞察接口"""
    try:
        data = request.get_json()
        
        # 获取数据文件路径或数据内容
        if 'file_path' in data:
            df = pd.read_csv(data['file_path'])
        elif 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            return jsonify({
                'success': False,
                'error': '缺少数据文件或数据内容'
            }), 400
        
        # 初始化LLM分析器
        analyzer = LLMAnalyzer()
        
        # 生成数据洞察
        insights = analyzer.analyze_data_insights({
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
        })
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI洞察生成失败: {str(e)}'
        }), 500

@app.route('/api/generate_chart', methods=['POST'])
def generate_chart():
    """根据可视化配置生成图表"""
    try:
        data = request.get_json()
        
        # 获取数据
        if 'data' not in data:
            return jsonify({
                'success': False,
                'error': '缺少数据'
            }), 400
        
        df = pd.DataFrame(data['data'])
        viz_config = data.get('visualization', {})
        
        if not viz_config.get('needed', False):
            return jsonify({
                'success': False,
                'error': '不需要生成图表'
            }), 400
        
        # 初始化可视化生成器
        viz_generator = VisualizationGenerator()
        
        chart_type = viz_config.get('chart_type', 'histogram')
        columns = viz_config.get('columns', [])
        title = viz_config.get('title', '数据可视化')
        
        # 根据图表类型生成相应的图表
        chart_base64 = None
        
        # 支持更多图表类型
        if chart_type == 'histogram' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_histogram(df[columns[0]], title)
        elif chart_type == 'scatter' and len(columns) >= 2:
            chart_base64 = viz_generator.generate_scatter_plot(df[columns[0]], df[columns[1]], title)
        elif chart_type == 'line' and len(columns) >= 2:
            chart_base64 = viz_generator.generate_line_chart(df, columns[0], columns[1], title)
        elif chart_type == 'bar' and len(columns) >= 1:
            # 如果是分类数据，需要进行分组统计
            if df[columns[0]].dtype == 'object' or df[columns[0]].dtype.name == 'category':
                # 对于分类数据，计算每个类别的计数或平均值
                if len(columns) >= 2 and df[columns[1]].dtype in ['int64', 'float64']:
                    # 如果有第二列数值数据，计算分组平均值
                    grouped_data = df.groupby(columns[0])[columns[1]].mean()
                else:
                    # 否则计算计数
                    grouped_data = df[columns[0]].value_counts()
                chart_base64 = viz_generator.generate_bar_chart(grouped_data, title)
            else:
                # 对于数值数据，直接使用
                chart_base64 = viz_generator.generate_bar_chart(df[columns[0]], title)
        elif chart_type == 'pie' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_pie_chart(df[columns[0]], title)
        elif chart_type == 'heatmap':
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                chart_base64 = viz_generator.generate_heatmap(numeric_df, title)
        elif chart_type == 'box' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_box_plot(df, columns[0], title)
        elif chart_type == 'violin' and len(columns) >= 1:
            # 小提琴图（使用箱线图作为替代）
            chart_base64 = viz_generator.generate_box_plot(df, columns[0], title)
        elif chart_type == 'area' and len(columns) >= 2:
            # 面积图（使用折线图作为替代）
            chart_base64 = viz_generator.generate_line_chart(df, columns[0], columns[1], title)
        elif chart_type == 'radar' and len(columns) >= 3:
            # 雷达图（使用散点图矩阵作为替代）
            numeric_df = df[columns].select_dtypes(include=['number'])
            if not numeric_df.empty:
                chart_base64 = viz_generator.generate_heatmap(numeric_df.corr(), f"{title} - 相关性分析")
        
        if chart_base64:
            return jsonify({
                'success': True,
                'chart_base64': chart_base64,
                'chart_type': chart_type,
                'title': title,
                'description': viz_config.get('description', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': f'无法生成{chart_type}类型的图表，请检查数据和列配置'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'图表生成失败: {str(e)}'
        }), 500

@app.route('/api/chart/recommendations', methods=['POST'])
def get_chart_recommendations():
    """获取图表类型推荐"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 获取数据上下文
        data_context = data.get('data_context', {})
        analysis_goal = data.get('analysis_goal', '数据探索')
        
        # 基于数据特征推荐图表类型
        recommendations = []
        
        numeric_columns = data_context.get('numeric_columns', [])
        categorical_columns = data_context.get('categorical_columns', [])
        total_columns = len(data_context.get('columns', []))
        
        # 基于数据类型推荐
        if len(numeric_columns) >= 2:
            recommendations.extend([
                {
                    'chart_type': 'scatter',
                    'name': '散点图',
                    'icon': '🔵',
                    'description': '分析两个数值变量之间的相关性',
                    'suitable_for': ['相关性分析', '趋势识别'],
                    'priority': 'high'
                },
                {
                    'chart_type': 'heatmap',
                    'name': '热力图',
                    'icon': '🔥',
                    'description': '展示多变量相关性矩阵',
                    'suitable_for': ['相关性分析', '模式识别'],
                    'priority': 'medium'
                }
            ])
        
        if len(numeric_columns) >= 1:
            recommendations.extend([
                {
                    'chart_type': 'histogram',
                    'name': '直方图',
                    'icon': '📊',
                    'description': '显示数值变量的分布情况',
                    'suitable_for': ['分布分析', '异常值检测'],
                    'priority': 'high'
                },
                {
                    'chart_type': 'box',
                    'name': '箱线图',
                    'icon': '📦',
                    'description': '展示数据分布和异常值',
                    'suitable_for': ['异常值检测', '分布比较'],
                    'priority': 'medium'
                }
            ])
        
        if len(categorical_columns) >= 1:
            recommendations.extend([
                {
                    'chart_type': 'bar',
                    'name': '柱状图',
                    'icon': '📊',
                    'description': '比较不同类别的数值',
                    'suitable_for': ['类别比较', '排名分析'],
                    'priority': 'high'
                },
                {
                    'chart_type': 'pie',
                    'name': '饼图',
                    'icon': '🥧',
                    'description': '显示各部分占整体的比例',
                    'suitable_for': ['占比分析', '构成分析'],
                    'priority': 'medium'
                }
            ])
        
        # 时间序列检测（简单启发式）
        time_related_columns = [col for col in data_context.get('columns', []) 
                               if any(keyword in col.lower() for keyword in ['time', 'date', '时间', '日期'])]
        
        if time_related_columns and len(numeric_columns) >= 1:
            recommendations.append({
                'chart_type': 'line',
                'name': '折线图',
                'icon': '📈',
                'description': '展示数据随时间的变化趋势',
                'suitable_for': ['趋势分析', '时间序列'],
                'priority': 'high'
            })
        
        # 根据分析目标调整推荐优先级
        if '相关' in analysis_goal:
            for rec in recommendations:
                if rec['chart_type'] in ['scatter', 'heatmap']:
                    rec['priority'] = 'high'
        elif '分布' in analysis_goal:
            for rec in recommendations:
                if rec['chart_type'] in ['histogram', 'box']:
                    rec['priority'] = 'high'
        elif '趋势' in analysis_goal:
            for rec in recommendations:
                if rec['chart_type'] == 'line':
                    rec['priority'] = 'high'
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 2))
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'data_summary': {
                'numeric_columns': len(numeric_columns),
                'categorical_columns': len(categorical_columns),
                'total_columns': total_columns,
                'has_time_series': len(time_related_columns) > 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取推荐失败: {str(e)}'
        }), 500

@app.route('/api/multi_lib/adapters', methods=['GET'])
def get_adapters():
    """获取可用的可视化适配器列表"""
    try:
        adapters = get_adapter_info()
        return jsonify({
            'success': True,
            'adapters': adapters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取适配器列表失败: {str(e)}'
        }), 500

@app.route('/api/multi_lib/generate_chart', methods=['POST'])
def generate_multi_lib_chart():
    """使用指定的可视化库生成图表"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['data', 'chart_type', 'adapter_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        df = pd.DataFrame(data['data'])
        chart_type = data['chart_type']
        adapter_name = data['adapter_name']
        chart_config = data.get('config', {})
        
        # 使用适配器生成图表
        result = create_chart_with_adapter(
            adapter_name=adapter_name,
            chart_type=chart_type,
            data=df,
            config=chart_config
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'chart_html': result['chart_html'],
                'performance': result['performance'],
                'adapter_info': result['adapter_info']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'多库图表生成失败: {str(e)}'
        }), 500

@app.route('/api/multi_lib/compare', methods=['POST'])
def compare_multi_lib_charts():
    """比较多个可视化库的图表生成性能"""
    try:
        data = request.get_json()
        
        # 验证必需参数
        required_fields = ['data', 'chart_type', 'adapters']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        df = pd.DataFrame(data['data'])
        chart_type = data['chart_type']
        adapters = data['adapters']  # 适配器名称列表
        chart_config = data.get('config', {})
        
        # 比较多个适配器
        comparison_result = compare_chart_adapters(
            adapters=adapters,
            chart_type=chart_type,
            data=df,
            config=chart_config
        )
        
        if comparison_result['success']:
            return jsonify({
                'success': True,
                'results': comparison_result['results'],
                'summary': comparison_result['summary']
            })
        else:
            return jsonify({
                'success': False,
                'error': comparison_result['error']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'多库比较失败: {str(e)}'
        }), 500

@app.route('/api/multi_lib/performance', methods=['POST'])
def get_performance_metrics():
    """获取指定适配器的性能指标"""
    try:
        data = request.get_json()
        
        adapter_name = data.get('adapter_name')
        if not adapter_name:
            return jsonify({
                'success': False,
                'error': '缺少适配器名称'
            }), 400
        
        # 获取适配器实例
        adapter = adapter_manager.get_adapter(adapter_name)
        if not adapter:
            return jsonify({
                'success': False,
                'error': f'未找到适配器: {adapter_name}'
            }), 404
        
        # 获取性能指标
        metrics = adapter.get_performance_metrics()
        
        return jsonify({
            'success': True,
            'adapter_name': adapter_name,
            'metrics': {
                'avg_render_time': metrics.avg_render_time,
                'total_charts_created': metrics.total_charts_created,
                'avg_file_size': metrics.avg_file_size,
                'error_count': metrics.error_count,
                'last_updated': metrics.last_updated.isoformat() if metrics.last_updated else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取性能指标失败: {str(e)}'
        }), 500

@app.route('/api/multi_lib/chart_types', methods=['GET'])
def get_supported_chart_types():
    """获取所有适配器支持的图表类型"""
    try:
        adapter_name = request.args.get('adapter')
        
        if adapter_name:
            # 获取特定适配器支持的图表类型
            adapter = adapter_manager.get_adapter(adapter_name)
            if not adapter:
                return jsonify({
                    'success': False,
                    'error': f'未找到适配器: {adapter_name}'
                }), 404
            
            chart_types = adapter.get_supported_chart_types()
            return jsonify({
                'success': True,
                'adapter': adapter_name,
                'chart_types': chart_types
            })
        else:
            # 获取所有适配器支持的图表类型
            all_chart_types = {}
            for name, adapter in adapter_manager.adapters.items():
                all_chart_types[name] = adapter.get_supported_chart_types()
            
            return jsonify({
                'success': True,
                'chart_types_by_adapter': all_chart_types
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取图表类型失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7701, threaded=True)