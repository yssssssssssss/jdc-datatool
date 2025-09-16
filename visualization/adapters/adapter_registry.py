from .adapter_manager import adapter_manager
from .echarts_adapter import EChartsAdapter
from .bokeh_adapter import BokehAdapter
import logging

logger = logging.getLogger(__name__)

def register_all_adapters():
    """注册所有可用的适配器"""
    try:
        # 注册ECharts适配器
        echarts_adapter = EChartsAdapter()
        adapter_manager.register_adapter(echarts_adapter)
        logger.info("ECharts adapter registered successfully")
        
        # 注册Bokeh适配器
        bokeh_adapter = BokehAdapter()
        adapter_manager.register_adapter(bokeh_adapter)
        logger.info("Bokeh adapter registered successfully")
        
        logger.info(f"Total adapters registered: {len(adapter_manager.get_available_adapters())}")
        
    except Exception as e:
        logger.error(f"Error registering adapters: {e}")
        raise

def get_adapter_info():
    """获取所有已注册适配器的信息"""
    return adapter_manager.get_adapter_stats()

def create_chart_with_adapter(adapter_name: str, chart_type: str, 
                             data: dict, config: dict = None):
    """使用指定适配器创建图表的便捷函数"""
    return adapter_manager.create_chart(adapter_name, chart_type, data, config)

def compare_chart_adapters(chart_type: str, data: dict, config: dict = None):
    """比较不同适配器创建同一图表的便捷函数"""
    return adapter_manager.compare_adapters(chart_type, data, config)

# 自动注册所有适配器
register_all_adapters()