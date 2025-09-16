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
            
            # 构建系统提示（极简版本，最大化响应速度）
            system_prompt = f"""
数据分析专家。数据信息：{context_info}

图表：histogram,scatter,line,bar,pie,heatmap,box,violin

JSON格式：
{{"analysis":"分析","visualization":{{"needed":true/false,"chart_type":"类型","columns":["列"],"title":"标题","description":"说明","recommendations":["选项"],"insights":"洞察"}}}}

简洁中文回答。
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
            
            # 记录请求开始时间
            import time
            start_time = time.time()
            logging.info(f"开始OpenAI API调用，模型: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=float(os.getenv('OPENAI_TEMPERATURE', 0.7)),
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 800)),  # 增加最大token数
                timeout=120  # 增加到120秒超时，匹配前端设置
            )
            
            # 记录请求完成时间
            end_time = time.time()
            duration = end_time - start_time
            logging.info(f"OpenAI API调用完成，耗时: {duration:.2f}秒")
            
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
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"AI对话失败: {e}")
            logging.error(f"详细错误信息: {error_details}")
            
            # 根据错误类型提供更具体的错误信息
            if "timeout" in str(e).lower():
                error_msg = "OpenAI API请求超时，请稍后重试"
            elif "connection" in str(e).lower():
                error_msg = "无法连接到OpenAI API，请检查网络连接"
            elif "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                error_msg = "API密钥无效，请检查OpenAI API配置"
            else:
                error_msg = f"AI分析过程中出现错误：{str(e)}"
            
            return {
                "success": False,
                "error": str(e),
                "response": f"🤖 **{error_msg}**\n\n💡 **提示：** 请检查网络连接或API配置。"
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
                temperature=0.7,
                timeout=25  # 设置25秒超时
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
                temperature=0.5,
                timeout=25  # 设置25秒超时
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
                temperature=0.6,
                timeout=25  # 设置25秒超时
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"图表解释失败: {e}")
            return f"图表解释失败: {str(e)}"