from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import psutil
import os
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    render_time: float  # 渲染时间（秒）
    memory_usage: float  # 内存使用量（MB）
    file_size: Optional[int] = None  # 文件大小（字节）
    chart_complexity: Optional[int] = None  # 图表复杂度评分

class BaseVisualizationAdapter(ABC):
    """可视化适配器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.performance_metrics = None
        
    @abstractmethod
    def create_chart(self, chart_type: str, data: Dict[str, Any], 
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建图表
        
        Args:
            chart_type: 图表类型
            data: 图表数据
            config: 图表配置
            
        Returns:
            包含图表HTML/JSON和元数据的字典
        """
        pass
    
    @abstractmethod
    def get_supported_chart_types(self) -> List[str]:
        """获取支持的图表类型列表"""
        pass
    
    @abstractmethod
    def validate_data(self, chart_type: str, data: Dict[str, Any]) -> bool:
        """验证数据是否适合指定的图表类型"""
        pass
    
    def measure_performance(self, func, *args, **kwargs):
        """测量函数执行性能"""
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        self.performance_metrics = PerformanceMetrics(
            render_time=end_time - start_time,
            memory_usage=end_memory - start_memory
        )
        
        return result
    
    def get_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """获取最近一次的性能指标"""
        return self.performance_metrics
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """获取适配器信息"""
        return {
            'name': self.name,
            'supported_charts': self.get_supported_chart_types(),
            'performance_metrics': self.performance_metrics.__dict__ if self.performance_metrics else None
        }