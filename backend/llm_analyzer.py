# 大模型交互逻辑
from openai import OpenAI
import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMAnalyzer:
    def __init__(self, api_key=None, model="gpt-4o-0806", base_url=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-0806')
        self.base_url = base_url or os.getenv('OPENAI_BASE_URL')
        
        # 初始化OpenAI客户端
        if self.api_key:
            if self.base_url:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            else:
                self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
        if not self.client:
            logging.warning("OpenAI API key not found. AI features will be disabled.")
    
    def chat_with_data(self, user_question: str, data_context: Dict, chat_history: List[Dict] = None) -> Dict:
        """与数据进行智能对话"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API未配置",
                "response": "抱歉，AI功能暂时不可用。请检查OpenAI API配置。"
            }
        
        try:
            # 构建数据上下文
            context_info = f"""
数据基本信息：
- 数据维度：{data_context.get('shape', 'N/A')}
- 列名：{', '.join(data_context.get('columns', []))}
- 数值型列：{', '.join(data_context.get('numeric_columns', []))}
- 分类型列：{', '.join(data_context.get('categorical_columns', []))}
- 缺失值情况：{data_context.get('missing_values', {})}
- 数据类型：{data_context.get('dtypes', {})}
"""
            
            # 构建系统提示
            system_prompt = f"""
你是一个专业的数据分析师，擅长分析各种类型的数据并提供深入的洞察。

当前数据信息：
{context_info}

请根据用户的问题，提供专业、准确的数据分析建议。

重要：请以JSON格式返回响应，包含以下字段：
{{
  "analysis": "详细的文字分析内容",
  "visualization": {{
    "needed": true/false,
    "chart_type": "histogram/scatter/line/bar/pie/heatmap/box",
    "columns": ["需要用于可视化的列名"],
    "title": "图表标题",
    "description": "图表说明"
  }}
}}

如果问题需要可视化展示（如分布分析、相关性分析、趋势分析等），请设置visualization.needed为true并提供相应配置。
如果只需要文字分析，请设置visualization.needed为false。

请用中文回答，语言要专业但易懂。
"""
            
            # 构建消息历史
            messages = [
                {
                    "role": "system", 
                    "content": system_prompt
                }
            ]
            
            # 添加聊天历史（最近5轮对话）
            if chat_history:
                recent_history = chat_history[-10:]  # 保留最近10条消息
                for msg in recent_history:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # 添加当前用户问题
            messages.append({
                "role": "user",
                "content": user_question
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=float(os.getenv('OPENAI_TEMPERATURE', 0.7)),
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 2000))
            )
            
            ai_response = response.choices[0].message.content
            
            # 尝试解析JSON响应
            try:
                # 清理响应文本，移除可能的markdown代码块标记
                clean_response = ai_response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                
                parsed_response = json.loads(clean_response)
                
                return {
                    "success": True,
                    "response": parsed_response.get('analysis', ai_response),
                    "visualization": parsed_response.get('visualization', {'needed': False}),
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "structured": True
                }
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本响应
                return {
                    "success": True,
                    "response": ai_response,
                    "visualization": {'needed': False},
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "structured": False
                }
            
            
        except Exception as e:
            logging.error(f"AI对话失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"AI分析过程中出现错误：{str(e)}\n\n请检查网络连接或API配置。"
            }
    
    def analyze_data_insights(self, data_summary: Dict) -> Dict:
        """分析数据洞察"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API未配置",
                "insights": "AI功能暂时不可用，请检查OpenAI API配置。"
            }
        
        try:
            prompt = f"""
            请分析以下数据摘要，提供数据洞察和建议：
            
            数据形状: {data_summary.get('shape', 'N/A')}
            列名: {data_summary.get('columns', [])}
            数据类型: {data_summary.get('dtypes', {})}
            缺失值: {data_summary.get('missing_values', {})}
            
            请提供：
            1. 数据质量评估
            2. 潜在的数据问题
            3. 建议的处理步骤
            4. 可能的分析方向
            
            请以结构化的中文回复。
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的数据分析师，擅长数据质量评估和洞察分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return {
                "success": True,
                "insights": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logging.error(f"LLM分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": "分析失败，请检查API配置"
            }
    
    def generate_analysis_suggestions(self, data_columns: List[str]) -> Dict:
        """生成分析建议"""
        if not self.client:
            return {
                "success": False,
                "error": "OpenAI API未配置",
                "suggestions": "AI功能暂时不可用，请检查OpenAI API配置。"
            }
        
        try:
            prompt = f"""
            基于以下数据列，建议合适的分析方法和可视化类型：
            
            数据列: {data_columns}
            
            请为每个列或列组合推荐：
            1. 适合的统计分析方法
            2. 推荐的可视化图表类型
            3. 可能的业务洞察角度
            
            请以结构化的中文回复。
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个数据可视化和分析专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            return {
                "success": True,
                "suggestions": response.choices[0].message.content
            }
            
        except Exception as e:
            logging.error(f"建议生成失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def explain_chart(self, chart_data: Dict, chart_type: str) -> str:
        """解释图表含义"""
        if not self.client:
            return "AI功能暂时不可用，请检查OpenAI API配置。"
        
        try:
            prompt = f"""
            请解释以下{chart_type}图表的含义和洞察：
            
            图表数据: {json.dumps(chart_data, ensure_ascii=False)}
            
            请提供：
            1. 图表显示的主要趋势
            2. 关键数据点的解释
            3. 可能的业务含义
            4. 进一步分析建议
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个数据解读专家，擅长从图表中提取业务洞察。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"图表解释失败: {e}")
            return f"图表解释失败: {str(e)}"