from .base_adapter import BaseVisualizationAdapter, PerformanceMetrics
from .adapter_manager import AdapterManager, adapter_manager
from .echarts_adapter import EChartsAdapter
from .bokeh_adapter import BokehAdapter
from .adapter_registry import (
    register_all_adapters,
    get_adapter_info,
    create_chart_with_adapter,
    compare_chart_adapters
)

# 自动注册所有适配器
register_all_adapters()

__all__ = [
    'BaseVisualizationAdapter',
    'PerformanceMetrics', 
    'AdapterManager',
    'adapter_manager',
    'EChartsAdapter',
    'BokehAdapter',
    'register_all_adapters',
    'get_adapter_info',
    'create_chart_with_adapter',
    'compare_chart_adapters'
]