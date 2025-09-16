"""可视化适配器基类

定义所有可视化库适配器的统一接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import time
import psutil
import os


class BaseVisualizationAdapter(ABC):
    """可视化适配器基类
    
    所有可视化库适配器都必须继承此基类并实现抽象方法
    """
    
    def __init__(self):
        """初始化适配器"""
        self._performance_metrics = {
            'render_time': 0,
            'memory_usage': 0,
            'file_size': 0,
            'chart_count': 0
        }
        self._start_time = None
        self._start_memory = None
    
    @abstractmethod
    def get_library_name(self) -> str:
        """返回可视化库名称"""
        pass
    
    @abstractmethod
    def get_supported_charts(self) -> List[str]:
        """返回支持的图表类型列表"""
        pass
    
    @abstractmethod
    def generate_chart(self, data: pd.DataFrame, chart_config: Dict) -> Dict:
        """生成图表
        
        Args:
            data: 数据DataFrame
            chart_config: 图表配置字典
                - chart_type: 图表类型
                - title: 图表标题
                - x_column: X轴列名
                - y_column: Y轴列名
                - color_column: 颜色分组列名（可选）
                - width: 图表宽度（可选）
                - height: 图表高度（可选）
                - 其他库特定配置
        
        Returns:
            Dict: 包含图表数据和元信息的字典
                - type: 输出类型（html/json/base64等）
                - data: 图表数据
                - render_time: 渲染时间（毫秒）
                - file_size: 文件大小（字节）
                - metadata: 其他元数据（可选）
        """
        pass
    
    @abstractmethod
    def export_chart(self, chart_data: Any, format: str, options: Dict = None) -> bytes:
        """导出图表
        
        Args:
            chart_data: 图表数据对象
            format: 导出格式（png/svg/html/pdf/json等）
            options: 导出选项（尺寸、质量等）
        
        Returns:
            bytes: 导出的文件内容
        """
        pass
    
    def validate_config(self, chart_config: Dict) -> bool:
        """验证图表配置
        
        Args:
            chart_config: 图表配置字典
        
        Returns:
            bool: 配置是否有效
        """
        required_fields = ['chart_type', 'title']
        
        # 检查必需字段
        for field in required_fields:
            if field not in chart_config:
                return False
        
        # 检查图表类型是否支持
        if chart_config['chart_type'] not in self.get_supported_charts():
            return False
        
        return True
    
    def validate_data(self, data: pd.DataFrame, chart_config: Dict) -> bool:
        """验证数据是否符合图表要求
        
        Args:
            data: 数据DataFrame
            chart_config: 图表配置字典
        
        Returns:
            bool: 数据是否有效
        """
        if data.empty:
            return False
        
        # 检查必需的列是否存在
        required_columns = []
        if 'x_column' in chart_config:
            required_columns.append(chart_config['x_column'])
        if 'y_column' in chart_config:
            required_columns.append(chart_config['y_column'])
        
        for col in required_columns:
            if col not in data.columns:
                return False
        
        return True
    
    def start_performance_tracking(self):
        """开始性能跟踪"""
        self._start_time = time.time()
        process = psutil.Process(os.getpid())
        self._start_memory = process.memory_info().rss
    
    def stop_performance_tracking(self, file_size: int = 0):
        """停止性能跟踪并更新指标
        
        Args:
            file_size: 生成文件的大小（字节）
        """
        if self._start_time is not None:
            self._performance_metrics['render_time'] = (time.time() - self._start_time) * 1000
        
        if self._start_memory is not None:
            process = psutil.Process(os.getpid())
            current_memory = process.memory_info().rss
            self._performance_metrics['memory_usage'] = current_memory - self._start_memory
        
        self._performance_metrics['file_size'] = file_size
        self._performance_metrics['chart_count'] += 1
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标
        
        Returns:
            Dict: 性能指标字典
                - render_time: 渲染时间（毫秒）
                - memory_usage: 内存使用量（字节）
                - file_size: 文件大小（字节）
                - chart_count: 生成图表数量
        """
        return self._performance_metrics.copy()
    
    def reset_performance_metrics(self):
        """重置性能指标"""
        self._performance_metrics = {
            'render_time': 0,
            'memory_usage': 0,
            'file_size': 0,
            'chart_count': 0
        }
    
    def get_library_info(self) -> Dict:
        """获取库信息
        
        Returns:
            Dict: 库信息字典
                - name: 库名称
                - supported_charts: 支持的图表类型
                - output_formats: 支持的输出格式
        """
        return {
            'name': self.get_library_name(),
            'supported_charts': self.get_supported_charts(),
            'output_formats': self.get_supported_export_formats()
        }
    
    def get_supported_export_formats(self) -> List[str]:
        """获取支持的导出格式
        
        子类可以重写此方法以提供特定的导出格式
        
        Returns:
            List[str]: 支持的导出格式列表
        """
        return ['png', 'svg', 'html', 'json']
    
    def preprocess_data(self, data: pd.DataFrame, chart_config: Dict) -> pd.DataFrame:
        """数据预处理
        
        子类可以重写此方法以实现特定的数据预处理逻辑
        
        Args:
            data: 原始数据DataFrame
            chart_config: 图表配置字典
        
        Returns:
            pd.DataFrame: 预处理后的数据
        """
        # 基础预处理：删除空值
        processed_data = data.copy()
        
        # 如果指定了特定列，只保留这些列的非空行
        columns_to_check = []
        if 'x_column' in chart_config and chart_config['x_column'] in processed_data.columns:
            columns_to_check.append(chart_config['x_column'])
        if 'y_column' in chart_config and chart_config['y_column'] in processed_data.columns:
            columns_to_check.append(chart_config['y_column'])
        
        if columns_to_check:
            processed_data = processed_data.dropna(subset=columns_to_check)
        
        return processed_data
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}({self.get_library_name()})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"{self.__class__.__name__}(library='{self.get_library_name()}', charts={self.get_supported_charts()})"