"""多可视化库管理器

统一管理多个可视化库适配器，提供统一的接口和性能对比功能
"""

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import time
import logging
import psutil
import os
from .base_adapter import BaseVisualizationAdapter


class MultiVisualizationManager:
    """多可视化库管理器
    
    负责管理所有可视化库适配器，提供统一的图表生成接口，
    支持多库对比和性能分析功能
    """
    
    def __init__(self, config: Dict = None):
        """初始化管理器
        
        Args:
            config: 配置字典，包含各种设置选项
        """
        self.config = config or {}
        self.adapters: Dict[str, BaseVisualizationAdapter] = {}
        self.performance_cache: Dict[str, List[Dict]] = {}
        self.logger = logging.getLogger(__name__)
        
        # 设置日志级别
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # 初始化适配器
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """初始化所有可用的适配器"""
        adapter_configs = {
            'matplotlib': {'backend': 'Agg', 'dpi': 300},
            'plotly': {'theme': 'plotly_white'},
            'echarts': {'theme': 'default'},
            'bokeh': {'theme': 'caliber'}
        }
        
        # 尝试导入并初始化各个适配器
        for adapter_name, adapter_config in adapter_configs.items():
            try:
                if adapter_name == 'matplotlib':
                    from ..adapters.matplotlib_adapter import MatplotlibAdapter
                    self.adapters[adapter_name] = MatplotlibAdapter(adapter_config)
                elif adapter_name == 'plotly':
                    from ..adapters.plotly_adapter import PlotlyAdapter
                    self.adapters[adapter_name] = PlotlyAdapter(adapter_config)
                elif adapter_name == 'echarts':
                    from ..adapters.echarts_adapter import EChartsAdapter
                    self.adapters[adapter_name] = EChartsAdapter(adapter_config)
                elif adapter_name == 'bokeh':
                    from ..adapters.bokeh_adapter import BokehAdapter
                    self.adapters[adapter_name] = BokehAdapter(adapter_config)
                
                self.logger.info(f"成功初始化 {adapter_name} 适配器")
                
            except ImportError as e:
                self.logger.warning(f"无法导入 {adapter_name} 适配器: {e}")
            except Exception as e:
                self.logger.error(f"初始化 {adapter_name} 适配器失败: {e}")
        
        self.logger.info(f"已成功初始化 {len(self.adapters)} 个可视化适配器")
    
    def register_adapter(self, name: str, adapter: BaseVisualizationAdapter):
        """注册新的适配器
        
        Args:
            name: 适配器名称
            adapter: 适配器实例
        """
        if not isinstance(adapter, BaseVisualizationAdapter):
            raise TypeError("适配器必须继承自 BaseVisualizationAdapter")
        
        self.adapters[name] = adapter
        self.logger.info(f"已注册适配器: {name}")
    
    def unregister_adapter(self, name: str):
        """注销适配器
        
        Args:
            name: 适配器名称
        """
        if name in self.adapters:
            del self.adapters[name]
            self.logger.info(f"已注销适配器: {name}")
    
    def get_available_libraries(self) -> List[str]:
        """获取可用的可视化库列表
        
        Returns:
            List[str]: 可用库名称列表
        """
        return list(self.adapters.keys())
    
    def get_supported_charts(self, library: str = None) -> Union[List[str], Dict[str, List[str]]]:
        """获取支持的图表类型
        
        Args:
            library: 指定库名称，如果为None则返回所有库的支持情况
        
        Returns:
            Union[List[str], Dict[str, List[str]]]: 图表类型列表或字典
        """
        if library:
            if library not in self.adapters:
                raise ValueError(f"不支持的可视化库: {library}")
            return self.adapters[library].get_supported_charts()
        else:
            return {name: adapter.get_supported_charts() 
                   for name, adapter in self.adapters.items()}
    
    def get_library_info(self, library: str = None) -> Union[Dict, Dict[str, Dict]]:
        """获取库信息
        
        Args:
            library: 指定库名称，如果为None则返回所有库的信息
        
        Returns:
            Union[Dict, Dict[str, Dict]]: 库信息字典
        """
        if library:
            if library not in self.adapters:
                raise ValueError(f"不支持的可视化库: {library}")
            return self.adapters[library].get_library_info()
        else:
            return {name: adapter.get_library_info() 
                   for name, adapter in self.adapters.items()}
    
    def generate_chart(self, library: str, data: pd.DataFrame, chart_config: Dict) -> Dict:
        """使用指定库生成单个图表
        
        Args:
            library: 可视化库名称
            data: 数据DataFrame
            chart_config: 图表配置
        
        Returns:
            Dict: 图表结果
        """
        if library not in self.adapters:
            raise ValueError(f"不支持的可视化库: {library}")
        
        adapter = self.adapters[library]
        
        # 验证配置和数据
        if not adapter.validate_config(chart_config):
            raise ValueError(f"无效的图表配置: {chart_config}")
        
        if not adapter.validate_data(data, chart_config):
            raise ValueError("数据不符合图表要求")
        
        # 生成图表
        try:
            result = adapter.generate_chart(data, chart_config)
            
            # 缓存性能数据
            self._cache_performance_data(library, adapter.get_performance_metrics())
            
            return result
        except Exception as e:
            self.logger.error(f"生成图表失败 [{library}]: {e}")
            raise
    
    def generate_multi_charts(self, 
                            data: pd.DataFrame,
                            chart_configs: List[Dict],
                            libraries: List[str],
                            comparison_mode: bool = False) -> Dict:
        """生成多库图表对比
        
        Args:
            data: 数据DataFrame
            chart_configs: 图表配置列表
            libraries: 要使用的库列表
            comparison_mode: 是否启用对比模式
        
        Returns:
            Dict: 包含所有库结果的字典
                - results: 各库的图表结果
                - performance_comparison: 性能对比（如果启用）
                - recommendations: 推荐建议
        """
        results = {}
        performance_data = {}
        
        for library in libraries:
            if library not in self.adapters:
                self.logger.warning(f"跳过不支持的库: {library}")
                continue
            
            library_results = {}
            library_performance = []
            
            for i, chart_config in enumerate(chart_configs):
                try:
                    # 添加图表ID
                    chart_id = chart_config.get('chart_id', f"chart_{i}")
                    
                    # 生成图表
                    result = self.generate_chart(library, data, chart_config)
                    
                    # 收集性能数据
                    adapter = self.adapters[library]
                    performance = adapter.get_performance_metrics()
                    performance['chart_id'] = chart_id
                    
                    library_results[chart_id] = result
                    library_performance.append(performance)
                    
                except Exception as e:
                    self.logger.error(f"生成图表失败 [{library}][{chart_id}]: {e}")
                    continue
            
            if library_results:
                results[library] = library_results
                performance_data[library] = library_performance
        
        # 生成对比和推荐
        response = {'results': results}
        
        if comparison_mode and performance_data:
            response['performance_comparison'] = self._generate_performance_comparison(performance_data)
        
        if performance_data:
            response['recommendations'] = self._generate_recommendations(performance_data, chart_configs)
        
        return response
    
    def export_chart(self, library: str, chart_data: Any, format: str, options: Dict = None) -> bytes:
        """导出图表
        
        Args:
            library: 可视化库名称
            chart_data: 图表数据
            format: 导出格式
            options: 导出选项
        
        Returns:
            bytes: 导出的文件内容
        """
        if library not in self.adapters:
            raise ValueError(f"不支持的可视化库: {library}")
        
        return self.adapters[library].export_chart(chart_data, format, options or {})
    
    def _cache_performance_data(self, library: str, metrics: Dict):
        """缓存性能数据
        
        Args:
            library: 库名称
            metrics: 性能指标
        """
        if library not in self.performance_cache:
            self.performance_cache[library] = []
        
        # 添加时间戳
        metrics_with_timestamp = metrics.copy()
        metrics_with_timestamp['timestamp'] = time.time()
        
        self.performance_cache[library].append(metrics_with_timestamp)
        
        # 保持缓存大小限制（最多100条记录）
        if len(self.performance_cache[library]) > 100:
            self.performance_cache[library] = self.performance_cache[library][-100:]
    
    def _generate_performance_comparison(self, performance_data: Dict) -> Dict:
        """生成性能对比数据
        
        Args:
            performance_data: 各库的性能数据
        
        Returns:
            Dict: 性能对比结果
        """
        if not performance_data:
            return {}
        
        # 计算各库的平均性能
        avg_performance = {}
        for library, metrics_list in performance_data.items():
            if metrics_list:
                avg_performance[library] = {
                    'avg_render_time': sum(m['render_time'] for m in metrics_list) / len(metrics_list),
                    'avg_file_size': sum(m['file_size'] for m in metrics_list) / len(metrics_list),
                    'avg_memory_usage': sum(m['memory_usage'] for m in metrics_list) / len(metrics_list),
                    'chart_count': len(metrics_list)
                }
        
        if not avg_performance:
            return {}
        
        # 找出最佳表现
        fastest_render = min(avg_performance.items(), key=lambda x: x[1]['avg_render_time'])[0]
        smallest_size = min(avg_performance.items(), key=lambda x: x[1]['avg_file_size'])[0]
        lowest_memory = min(avg_performance.items(), key=lambda x: x[1]['avg_memory_usage'])[0]
        
        return {
            'fastest_render': fastest_render,
            'smallest_size': smallest_size,
            'lowest_memory': lowest_memory,
            'detailed_metrics': avg_performance
        }
    
    def _generate_recommendations(self, performance_data: Dict, chart_configs: List[Dict]) -> List[Dict]:
        """生成库选择推荐
        
        Args:
            performance_data: 性能数据
            chart_configs: 图表配置
        
        Returns:
            List[Dict]: 推荐列表
        """
        recommendations = []
        
        for library in performance_data.keys():
            score = self._calculate_library_score(library, performance_data[library], chart_configs)
            reasons = self._get_recommendation_reasons(library, performance_data[library])
            
            recommendations.append({
                'library': library,
                'score': round(score, 1),
                'reasons': reasons
            })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def _calculate_library_score(self, library: str, performance: List[Dict], configs: List[Dict]) -> float:
        """计算库的推荐分数
        
        Args:
            library: 库名称
            performance: 性能数据列表
            configs: 图表配置列表
        
        Returns:
            float: 推荐分数（0-10）
        """
        # 基础分数
        base_scores = {
            'matplotlib': 7.0,
            'plotly': 8.5,
            'echarts': 9.0,
            'bokeh': 7.5
        }
        
        score = base_scores.get(library, 5.0)
        
        # 根据性能调整分数
        if performance:
            avg_render_time = sum(p['render_time'] for p in performance) / len(performance)
            avg_file_size = sum(p['file_size'] for p in performance) / len(performance)
            avg_memory_usage = sum(p['memory_usage'] for p in performance) / len(performance)
            
            # 渲染时间越短分数越高
            if avg_render_time < 100:
                score += 1.0
            elif avg_render_time > 500:
                score -= 1.0
            
            # 文件大小越小分数越高
            if avg_file_size < 10000:  # 10KB
                score += 0.5
            elif avg_file_size > 100000:  # 100KB
                score -= 0.5
            
            # 内存使用越少分数越高
            if avg_memory_usage < 1024 * 1024:  # 1MB
                score += 0.3
            elif avg_memory_usage > 10 * 1024 * 1024:  # 10MB
                score -= 0.3
        
        return min(10.0, max(0.0, score))
    
    def _get_recommendation_reasons(self, library: str, performance: List[Dict]) -> List[str]:
        """获取推荐理由
        
        Args:
            library: 库名称
            performance: 性能数据列表
        
        Returns:
            List[str]: 推荐理由列表
        """
        reasons = []
        
        # 库特性
        library_features = {
            'matplotlib': ['静态图表质量高', '导出格式丰富', '内存使用低'],
            'plotly': ['交互性强', '图表美观', 'Web友好'],
            'echarts': ['渲染速度快', '文件体积小', '适合Web展示'],
            'bokeh': ['大数据支持好', '服务器集成佳', '自定义能力强']
        }
        
        reasons.extend(library_features.get(library, ['功能完善']))
        
        # 根据性能添加动态理由
        if performance:
            avg_render_time = sum(p['render_time'] for p in performance) / len(performance)
            avg_file_size = sum(p['file_size'] for p in performance) / len(performance)
            
            if avg_render_time < 100:
                reasons.append('渲染速度优秀')
            if avg_file_size < 10000:
                reasons.append('文件体积小')
        
        return reasons[:3]  # 最多返回3个理由
    
    def get_performance_summary(self) -> Dict:
        """获取性能摘要
        
        Returns:
            Dict: 性能摘要数据
        """
        summary = {}
        
        for library, metrics_list in self.performance_cache.items():
            if metrics_list:
                recent_metrics = metrics_list[-10:]  # 最近10次
                summary[library] = {
                    'total_charts': len(metrics_list),
                    'avg_render_time': sum(m['render_time'] for m in recent_metrics) / len(recent_metrics),
                    'avg_file_size': sum(m['file_size'] for m in recent_metrics) / len(recent_metrics),
                    'avg_memory_usage': sum(m['memory_usage'] for m in recent_metrics) / len(recent_metrics)
                }
        
        return summary
    
    def clear_performance_cache(self, library: str = None):
        """清除性能缓存
        
        Args:
            library: 指定库名称，如果为None则清除所有缓存
        """
        if library:
            if library in self.performance_cache:
                self.performance_cache[library] = []
        else:
            self.performance_cache = {}
        
        self.logger.info(f"已清除性能缓存: {library or '全部'}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"MultiVisualizationManager(libraries={list(self.adapters.keys())})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"MultiVisualizationManager(adapters={len(self.adapters)}, cached_metrics={sum(len(v) for v in self.performance_cache.values())})"