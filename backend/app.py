# Flask 后端应用入口
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from llm_analyzer import LLMAnalyzer
from visualization import VisualizationGenerator

app = Flask(__name__)
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
    """AI对话接口"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "请求数据为空"
            }), 400
        
        question = data.get('question')
        data_context = data.get('data_context', {})
        chat_history = data.get('chat_history', [])
        
        if not question:
            return jsonify({
                "success": False,
                "error": "问题不能为空"
            }), 400
        
        # 初始化LLM分析器
        analyzer = LLMAnalyzer()
        
        # 调用AI分析
        result = analyzer.chat_with_data(
            user_question=question,
            data_context=data_context,
            chat_history=chat_history
        )
        
        # 检查返回结果是否为字典（包含可视化配置）
        if isinstance(result, dict):
            return jsonify({
                'success': True,
                'response': result.get('analysis', result.get('response', str(result))),
                'visualization': result.get('visualization', {'needed': False})
            })
        else:
            # 如果是字符串，则按原来的方式处理
            return jsonify({
                'success': True,
                'response': result,
                'visualization': {'needed': False}
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "response": f"AI分析过程中出现错误：{str(e)}"
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
        
        if chart_type == 'histogram' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_histogram(df[columns[0]], title)
        elif chart_type == 'scatter' and len(columns) >= 2:
            chart_base64 = viz_generator.generate_scatter_plot(df[columns[0]], df[columns[1]], title)
        elif chart_type == 'line' and len(columns) >= 2:
            chart_base64 = viz_generator.generate_line_chart(df, columns[0], columns[1], title)
        elif chart_type == 'bar' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_bar_chart(df[columns[0]], title)
        elif chart_type == 'pie' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_pie_chart(df[columns[0]], title)
        elif chart_type == 'heatmap':
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                chart_base64 = viz_generator.generate_heatmap(numeric_df, title)
        elif chart_type == 'box' and len(columns) >= 1:
            chart_base64 = viz_generator.generate_box_plot(df, columns[0], title)
        
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7701)