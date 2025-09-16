#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型连接测试案例
基于项目中的LLMAnalyzer类进行最小化测试
"""

import os
import sys
import json
from typing import Dict, Any
from dotenv import load_dotenv

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared'))

try:
    from backend.llm_analyzer import LLMAnalyzer
    from shared.config import config
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

class LLMConnectionTester:
    """大模型连接测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.test_results = []
        self.analyzer = None
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        # 实时输出测试结果
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
        print()
    
    def test_environment_setup(self) -> bool:
        """测试环境配置"""
        print("=== 环境配置测试 ===")
        
        # 测试.env文件加载
        try:
            load_dotenv()
            self.log_test(
                "环境变量加载", 
                True, 
                "成功加载.env文件"
            )
        except Exception as e:
            self.log_test(
                "环境变量加载", 
                False, 
                f"加载.env文件失败: {str(e)}"
            )
        
        # 测试配置获取
        try:
            api_config = config.get_config('api')
            api_key = api_config.get('openai_api_key')
            base_url = api_config.get('openai_base_url')
            model = api_config.get('openai_model')
            
            details = {
                "API Key": "已配置" if api_key else "未配置",
                "Base URL": base_url or "默认",
                "Model": model or "默认",
                "API Key前缀": api_key[:10] + "..." if api_key and len(api_key) > 10 else "N/A"
            }
            
            success = bool(api_key)
            message = "配置完整" if success else "缺少API Key配置"
            
            self.log_test(
                "配置检查", 
                success, 
                message,
                details
            )
            
            return success
            
        except Exception as e:
            self.log_test(
                "配置检查", 
                False, 
                f"配置检查失败: {str(e)}"
            )
            return False
    
    def test_analyzer_initialization(self) -> bool:
        """测试LLMAnalyzer初始化"""
        print("=== LLMAnalyzer初始化测试 ===")
        
        try:
            # 使用配置中的参数初始化
            api_config = config.get_config('api')
            
            self.analyzer = LLMAnalyzer(
                api_key=api_config.get('openai_api_key'),
                model=api_config.get('openai_model'),
                base_url=api_config.get('openai_base_url')
            )
            
            # 检查初始化状态
            has_client = self.analyzer.client is not None
            
            details = {
                "Client对象": "已创建" if has_client else "未创建",
                "API Key": "已设置" if self.analyzer.api_key else "未设置",
                "Model": self.analyzer.model,
                "Base URL": self.analyzer.base_url or "默认OpenAI"
            }
            
            message = "初始化成功" if has_client else "初始化失败，缺少API配置"
            
            self.log_test(
                "LLMAnalyzer初始化", 
                has_client, 
                message,
                details
            )
            
            return has_client
            
        except Exception as e:
            self.log_test(
                "LLMAnalyzer初始化", 
                False, 
                f"初始化异常: {str(e)}"
            )
            return False
    
    def test_basic_chat(self) -> bool:
        """测试基本对话功能"""
        print("=== 基本对话功能测试 ===")
        
        if not self.analyzer or not self.analyzer.client:
            self.log_test(
                "基本对话测试", 
                False, 
                "跳过测试，LLMAnalyzer未正确初始化"
            )
            return False
        
        # 准备测试数据
        test_question = "你好，请简单介绍一下你的功能"
        test_data_context = {
            'shape': [100, 5],
            'columns': ['name', 'age', 'salary', 'department', 'join_date'],
            'numeric_columns': ['age', 'salary'],
            'categorical_columns': ['name', 'department'],
            'missing_values': {'age': 0, 'salary': 2},
            'dtypes': {'name': 'object', 'age': 'int64', 'salary': 'float64'}
        }
        
        try:
            # 执行对话测试
            response = self.analyzer.chat_with_data(
                user_question=test_question,
                data_context=test_data_context
            )
            
            success = response.get('success', False)
            
            if success:
                details = {
                    "响应长度": len(response.get('response', '')),
                    "结构化响应": response.get('structured', False),
                    "Token使用": response.get('usage', {}).get('total_tokens', 'N/A'),
                    "可视化建议": response.get('visualization', {}).get('needed', False)
                }
                
                # 显示部分响应内容
                response_preview = response.get('response', '')[:100] + "..." if len(response.get('response', '')) > 100 else response.get('response', '')
                details["响应预览"] = response_preview
                
                self.log_test(
                    "基本对话测试", 
                    True, 
                    "对话成功",
                    details
                )
            else:
                error_msg = response.get('error', '未知错误')
                self.log_test(
                    "基本对话测试", 
                    False, 
                    f"对话失败: {error_msg}"
                )
            
            return success
            
        except Exception as e:
            self.log_test(
                "基本对话测试", 
                False, 
                f"测试异常: {str(e)}"
            )
            return False
    
    def test_data_insights(self) -> bool:
        """测试数据洞察功能"""
        print("=== 数据洞察功能测试 ===")
        
        if not self.analyzer or not self.analyzer.client:
            self.log_test(
                "数据洞察测试", 
                False, 
                "跳过测试，LLMAnalyzer未正确初始化"
            )
            return False
        
        # 准备测试数据摘要
        test_data_summary = {
            'shape': [1000, 8],
            'columns': ['user_id', 'age', 'income', 'education', 'city', 'purchase_amount', 'category', 'date'],
            'dtypes': {
                'user_id': 'int64',
                'age': 'int64', 
                'income': 'float64',
                'education': 'object',
                'city': 'object',
                'purchase_amount': 'float64',
                'category': 'object',
                'date': 'datetime64'
            },
            'missing_values': {
                'age': 5,
                'income': 12,
                'education': 3
            }
        }
        
        try:
            # 执行数据洞察测试
            response = self.analyzer.analyze_data_insights(test_data_summary)
            
            success = response.get('success', False)
            
            if success:
                insights = response.get('insights', '')
                usage = response.get('usage', {})
                
                details = {
                    "洞察长度": len(insights),
                    "Token使用": usage.get('total_tokens', 'N/A'),
                    "洞察预览": insights[:150] + "..." if len(insights) > 150 else insights
                }
                
                self.log_test(
                    "数据洞察测试", 
                    True, 
                    "洞察生成成功",
                    details
                )
            else:
                error_msg = response.get('error', '未知错误')
                self.log_test(
                    "数据洞察测试", 
                    False, 
                    f"洞察生成失败: {error_msg}"
                )
            
            return success
            
        except Exception as e:
            self.log_test(
                "数据洞察测试", 
                False, 
                f"测试异常: {str(e)}"
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始大模型连接测试...\n")
        
        # 执行所有测试
        env_ok = self.test_environment_setup()
        init_ok = self.test_analyzer_initialization()
        chat_ok = self.test_basic_chat()
        insights_ok = self.test_data_insights()
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        # 生成测试报告
        print("=== 测试结果汇总 ===")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        # 显示失败的测试
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        # 总体状态
        overall_success = env_ok and init_ok and (chat_ok or insights_ok)
        
        if overall_success:
            print("\n🎉 大模型连接测试通过！系统可以正常使用AI功能。")
        else:
            print("\n⚠️  大模型连接测试未完全通过，请检查配置。")
            
            # 提供修复建议
            if not env_ok:
                print("   建议: 检查.env文件和OPENAI_API_KEY配置")
            if not init_ok:
                print("   建议: 检查API密钥和网络连接")
            if not chat_ok and not insights_ok:
                print("   建议: 检查API服务可用性和模型配置")
        
        return {
            'overall_success': overall_success,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests/total_tests*100,
            'test_details': self.test_results
        }

def main():
    """主函数"""
    print("大模型连接测试工具")
    print("=" * 50)
    
    # 创建测试器并运行测试
    tester = LLMConnectionTester()
    results = tester.run_all_tests()
    
    # 保存测试结果到文件
    try:
        with open('llm_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细测试结果已保存到: llm_test_results.json")
    except Exception as e:
        print(f"\n⚠️  保存测试结果失败: {e}")
    
    # 返回退出码
    return 0 if results['overall_success'] else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)