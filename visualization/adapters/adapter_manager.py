from typing import Dict, List, Any, Optional
from .base_adapter import BaseVisualizationAdapter, PerformanceMetrics
import logging

class AdapterManager:
    """可视化适配器管理器"""
    
    def __init__(self):
        self.adapters: Dict[str, BaseVisualizationAdapter] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_adapter(self, adapter: BaseVisualizationAdapter):
        """注册适配器"""
        self.adapters[adapter.name] = adapter
        self.logger.info(f"Registered adapter: {adapter.name}")
        
    def unregister_adapter(self, adapter_name: str):
        """注销适配器"""
        if adapter_name in self.adapters:
            del self.adapters[adapter_name]
            self.logger.info(f"Unregistered adapter: {adapter_name}")
        
    def get_adapter(self, adapter_name: str) -> Optional[BaseVisualizationAdapter]:
        """获取指定适配器"""
        return self.adapters.get(adapter_name)
        
    def get_available_adapters(self) -> List[str]:
        """获取可用适配器列表"""
        return list(self.adapters.keys())
        
    def get_supported_chart_types(self, adapter_name: str = None) -> Dict[str, List[str]]:
        """获取支持的图表类型
        
        Args:
            adapter_name: 指定适配器名称，如果为None则返回所有适配器的支持类型
            
        Returns:
            适配器名称到支持图表类型列表的映射
        """
        if adapter_name:
            adapter = self.get_adapter(adapter_name)
            if adapter:
                return {adapter_name: adapter.get_supported_chart_types()}
            return {}
        
        return {
            name: adapter.get_supported_chart_types() 
            for name, adapter in self.adapters.items()
        }
        
    def create_chart(self, adapter_name: str, chart_type: str, 
                    data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用指定适配器创建图表"""
        adapter = self.get_adapter(adapter_name)
        if not adapter:
            raise ValueError(f"Adapter '{adapter_name}' not found")
            
        if chart_type not in adapter.get_supported_chart_types():
            raise ValueError(f"Chart type '{chart_type}' not supported by adapter '{adapter_name}'")
            
        if not adapter.validate_data(chart_type, data):
            raise ValueError(f"Invalid data for chart type '{chart_type}'")
            
        return adapter.measure_performance(adapter.create_chart, chart_type, data, config)
        
    def compare_adapters(self, chart_type: str, data: Dict[str, Any], 
                        config: Dict[str, Any] = None) -> Dict[str, Any]:
        """比较不同适配器的性能和结果"""
        results = {}
        
        for adapter_name, adapter in self.adapters.items():
            if chart_type in adapter.get_supported_chart_types():
                try:
                    chart_result = self.create_chart(adapter_name, chart_type, data, config)
                    performance = adapter.get_performance_metrics()
                    
                    results[adapter_name] = {
                        'chart': chart_result,
                        'performance': performance.__dict__ if performance else None,
                        'success': True
                    }
                except Exception as e:
                    results[adapter_name] = {
                        'error': str(e),
                        'success': False
                    }
                    self.logger.error(f"Error creating chart with {adapter_name}: {e}")
                    
        return results
        
    def get_best_adapter(self, chart_type: str, criteria: str = 'speed') -> Optional[str]:
        """根据指定标准获取最佳适配器
        
        Args:
            chart_type: 图表类型
            criteria: 评判标准 ('speed', 'memory', 'quality')
            
        Returns:
            最佳适配器名称
        """
        suitable_adapters = []
        
        for adapter_name, adapter in self.adapters.items():
            if chart_type in adapter.get_supported_chart_types():
                metrics = adapter.get_performance_metrics()
                if metrics:
                    suitable_adapters.append((adapter_name, metrics))
                    
        if not suitable_adapters:
            return None
            
        if criteria == 'speed':
            return min(suitable_adapters, key=lambda x: x[1].render_time)[0]
        elif criteria == 'memory':
            return min(suitable_adapters, key=lambda x: x[1].memory_usage)[0]
        else:
            # 默认返回第一个
            return suitable_adapters[0][0]
            
    def get_adapter_stats(self) -> Dict[str, Any]:
        """获取所有适配器的统计信息"""
        stats = {
            'total_adapters': len(self.adapters),
            'adapters': {}
        }
        
        for name, adapter in self.adapters.items():
            stats['adapters'][name] = adapter.get_adapter_info()
            
        return stats

# 全局适配器管理器实例
adapter_manager = AdapterManager()