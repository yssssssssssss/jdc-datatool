from typing import Dict, Any, List
from .base_adapter import BaseVisualizationAdapter
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Scatter, Pie, Funnel, Radar, Gauge
from pyecharts.globals import ThemeType
import pandas as pd
import json

class EChartsAdapter(BaseVisualizationAdapter):
    """ECharts适配器实现"""
    
    def __init__(self):
        super().__init__("echarts")
        self.chart_mapping = {
            'line': self._create_line_chart,
            'bar': self._create_bar_chart,
            'scatter': self._create_scatter_chart,
            'pie': self._create_pie_chart,
            'funnel': self._create_funnel_chart,
            'radar': self._create_radar_chart,
            'gauge': self._create_gauge_chart
        }
        
    def get_supported_chart_types(self) -> List[str]:
        """获取支持的图表类型"""
        return list(self.chart_mapping.keys())
        
    def validate_data(self, chart_type: str, data: Dict[str, Any]) -> bool:
        """验证数据格式"""
        if chart_type not in self.chart_mapping:
            return False
            
        required_fields = self._get_required_fields(chart_type)
        return all(field in data for field in required_fields)
        
    def _get_required_fields(self, chart_type: str) -> List[str]:
        """获取图表类型所需的数据字段"""
        field_mapping = {
            'line': ['x', 'y'],
            'bar': ['x', 'y'],
            'scatter': ['x', 'y'],
            'pie': ['labels', 'values'],
            'funnel': ['labels', 'values'],
            'radar': ['indicators', 'values'],
            'gauge': ['value', 'max_value']
        }
        return field_mapping.get(chart_type, [])
        
    def create_chart(self, chart_type: str, data: Dict[str, Any], 
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建ECharts图表"""
        if chart_type not in self.chart_mapping:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
        config = config or {}
        chart_func = self.chart_mapping[chart_type]
        chart = chart_func(data, config)
        
        # 设置全局配置
        chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title=config.get('title', f'{chart_type.title()} Chart'),
                subtitle=config.get('subtitle', '')
            ),
            legend_opts=opts.LegendOpts(
                is_show=config.get('show_legend', True)
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=config.get('show_toolbox', True)
            ),
            datazoom_opts=opts.DataZoomOpts(
                is_show=config.get('show_datazoom', False)
            )
        )
        
        # 生成HTML
        html_content = chart.render_embed()
        
        # 获取图表配置JSON
        chart_json = chart.get_options()
        
        return {
            'html': html_content,
            'json': chart_json,
            'chart_type': chart_type,
            'adapter': self.name,
            'config': config
        }
        
    def _create_line_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建折线图"""
        chart = Line(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        x_data = data['x']
        y_data = data['y']
        
        chart.add_xaxis(x_data)
        
        if isinstance(y_data, dict):
            # 多系列数据
            for series_name, series_data in y_data.items():
                chart.add_yaxis(
                    series_name=series_name,
                    y_axis=series_data,
                    is_smooth=config.get('smooth', True),
                    markpoint_opts=opts.MarkPointOpts(
                        data=[opts.MarkPointItem(type_="max"), opts.MarkPointItem(type_="min")]
                    ) if config.get('show_markpoint', False) else None
                )
        else:
            # 单系列数据
            chart.add_yaxis(
                series_name=config.get('series_name', 'Series 1'),
                y_axis=y_data,
                is_smooth=config.get('smooth', True)
            )
            
        return chart
        
    def _create_bar_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建柱状图"""
        chart = Bar(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        x_data = data['x']
        y_data = data['y']
        
        chart.add_xaxis(x_data)
        
        if isinstance(y_data, dict):
            # 多系列数据
            for series_name, series_data in y_data.items():
                chart.add_yaxis(
                    series_name=series_name,
                    y_axis=series_data,
                    stack=config.get('stack', None)
                )
        else:
            # 单系列数据
            chart.add_yaxis(
                series_name=config.get('series_name', 'Series 1'),
                y_axis=y_data
            )
            
        return chart
        
    def _create_scatter_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建散点图"""
        chart = Scatter(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        x_data = data['x']
        y_data = data['y']
        
        # 组合x和y数据为散点数据
        scatter_data = list(zip(x_data, y_data))
        
        chart.add_xaxis(x_data)
        chart.add_yaxis(
            series_name=config.get('series_name', 'Scatter'),
            y_axis=scatter_data,
            symbol_size=config.get('symbol_size', 10)
        )
        
        return chart
        
    def _create_pie_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建饼图"""
        chart = Pie(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        labels = data['labels']
        values = data['values']
        
        pie_data = [list(z) for z in zip(labels, values)]
        
        chart.add(
            series_name=config.get('series_name', 'Pie'),
            data_pair=pie_data,
            radius=config.get('radius', ["30%", "75%"]),
            center=config.get('center', ["50%", "50%"])
        )
        
        return chart
        
    def _create_funnel_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建漏斗图"""
        chart = Funnel(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        labels = data['labels']
        values = data['values']
        
        funnel_data = [list(z) for z in zip(labels, values)]
        
        chart.add(
            series_name=config.get('series_name', 'Funnel'),
            data_pair=funnel_data
        )
        
        return chart
        
    def _create_radar_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建雷达图"""
        chart = Radar(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        indicators = data['indicators']  # [{'name': 'indicator1', 'max': 100}, ...]
        values = data['values']  # [[90, 80, 70, ...], ...]
        
        chart.add_schema(
            schema=[
                opts.RadarIndicatorItem(name=ind['name'], max_=ind.get('max', 100))
                for ind in indicators
            ]
        )
        
        if isinstance(values[0], list):
            # 多系列数据
            for i, series_values in enumerate(values):
                chart.add(
                    series_name=config.get('series_names', [f'Series {i+1}'])[i] if config.get('series_names') else f'Series {i+1}',
                    data=[series_values]
                )
        else:
            # 单系列数据
            chart.add(
                series_name=config.get('series_name', 'Radar'),
                data=[values]
            )
            
        return chart
        
    def _create_gauge_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建仪表盘图"""
        chart = Gauge(init_opts=opts.InitOpts(
            theme=config.get('theme', ThemeType.LIGHT),
            width=config.get('width', '800px'),
            height=config.get('height', '400px')
        ))
        
        value = data['value']
        max_value = data.get('max_value', 100)
        
        chart.add(
            series_name=config.get('series_name', 'Gauge'),
            data_pair=[(config.get('gauge_name', 'Value'), value)],
            max_=max_value,
            split_number=config.get('split_number', 10)
        )
        
        return chart