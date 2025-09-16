"""多可视化库集成系统

这个模块提供了一个统一的接口来使用多个可视化库，包括：
- ECharts (通过 pyecharts)
- Bokeh
- Matplotlib (通过基础适配器扩展)
- Plotly (通过基础适配器扩展)

主要组件：
- BaseVisualizationAdapter: 所有适配器的基类
- MultiVisualizationManager: 多库管理器，提供统一接口
- EChartsAdapter: ECharts适配器实现
- BokehAdapter: Bokeh适配器实现
- ConfigManager: 配置管理
- PerformanceMonitor: 性能监控

使用示例：
    from backend.visualization import MultiVisualizationManager
    
    # 创建管理器实例
    manager = MultiVisualizationManager()
    
    # 生成图表
    chart = manager.create_chart(
        chart_type='line',
        data={'x': [1, 2, 3], 'y': [1, 4, 2]},
        library='echarts'
    )
"""

from .core.base_adapter import BaseVisualizationAdapter
from .core.multi_manager import MultiVisualizationManager
from .adapters.echarts_adapter import EChartsAdapter
from .adapters.bokeh_adapter import BokehAdapter
from .utils.config import ConfigManager, VisualizationConfig
from .utils.performance import PerformanceMonitor, performance_timer

# 版本信息
__version__ = '1.0.0'
__author__ = 'JDC DataTool Team'
__description__ = '多可视化库集成系统'

# 导出的公共接口
__all__ = [
    # 核心类
    'BaseVisualizationAdapter',
    'MultiVisualizationManager',
    
    # 适配器
    'EChartsAdapter',
    'BokehAdapter',
    
    # 工具类
    'ConfigManager',
    'VisualizationConfig',
    'PerformanceMonitor',
    'performance_timer',
    
    # 元信息
    '__version__',
    '__author__',
    '__description__',
]

# 默认配置
DEFAULT_CONFIG = {
    'echarts': {
        'theme': 'default',
        'width': 800,
        'height': 600,
        'animation': True,
        'toolbox': True,
        'legend': True,
    },
    'bokeh': {
        'theme': 'caliber',
        'width': 800,
        'height': 600,
        'toolbar_location': 'above',
        'tools': 'pan,wheel_zoom,box_zoom,reset,save',
    },
    'performance': {
        'enable_monitoring': True,
        'cache_size': 100,
        'log_level': 'INFO',
    }
}

# 支持的图表类型
SUPPORTED_CHART_TYPES = {
    'echarts': [
        'line', 'bar', 'scatter', 'pie', 'radar', 'gauge',
        'funnel', 'sankey', 'heatmap', 'treemap', 'sunburst',
        'graph', 'parallel', 'candlestick', 'boxplot'
    ],
    'bokeh': [
        'line', 'scatter', 'bar', 'histogram', 'heatmap',
        'box', 'violin', 'area', 'step', 'multi_line'
    ]
}

# 支持的导出格式
SUPPORTED_EXPORT_FORMATS = {
    'echarts': ['html', 'png', 'jpg', 'svg', 'pdf'],
    'bokeh': ['html', 'png', 'svg']
}

def get_version():
    """获取版本信息"""
    return __version__

def get_supported_libraries():
    """获取支持的可视化库列表"""
    return list(SUPPORTED_CHART_TYPES.keys())

def get_supported_chart_types(library=None):
    """获取支持的图表类型
    
    Args:
        library: 指定库名，如果为None则返回所有库的图表类型
        
    Returns:
        dict or list: 图表类型信息
    """
    if library:
        return SUPPORTED_CHART_TYPES.get(library, [])
    return SUPPORTED_CHART_TYPES

def get_supported_export_formats(library=None):
    """获取支持的导出格式
    
    Args:
        library: 指定库名，如果为None则返回所有库的导出格式
        
    Returns:
        dict or list: 导出格式信息
    """
    if library:
        return SUPPORTED_EXPORT_FORMATS.get(library, [])
    return SUPPORTED_EXPORT_FORMATS

def create_manager(config=None):
    """创建多库管理器实例的便捷函数
    
    Args:
        config: 配置字典，如果为None则使用默认配置
        
    Returns:
        MultiVisualizationManager: 管理器实例
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    manager = MultiVisualizationManager()
    
    # 注册默认适配器
    manager.register_adapter('echarts', EChartsAdapter(config.get('echarts', {})))
    manager.register_adapter('bokeh', BokehAdapter(config.get('bokeh', {})))
    
    return manager