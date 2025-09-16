from typing import Dict, Any, List
from .base_adapter import BaseVisualizationAdapter
from bokeh.plotting import figure, save, output_file
from bokeh.models import HoverTool, ColumnDataSource, ColorBar
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256, Category20
from bokeh.embed import file_html, components
from bokeh.resources import CDN
from bokeh.layouts import column, row
import pandas as pd
import numpy as np
import tempfile
import os

class BokehAdapter(BaseVisualizationAdapter):
    """Bokeh适配器实现"""
    
    def __init__(self):
        super().__init__("bokeh")
        self.chart_mapping = {
            'line': self._create_line_chart,
            'bar': self._create_bar_chart,
            'scatter': self._create_scatter_chart,
            'heatmap': self._create_heatmap,
            'histogram': self._create_histogram,
            'box': self._create_box_plot,
            'area': self._create_area_chart
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
            'heatmap': ['x', 'y', 'values'],
            'histogram': ['values'],
            'box': ['groups', 'values'],
            'area': ['x', 'y']
        }
        return field_mapping.get(chart_type, [])
        
    def create_chart(self, chart_type: str, data: Dict[str, Any], 
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建Bokeh图表"""
        if chart_type not in self.chart_mapping:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
        config = config or {}
        chart_func = self.chart_mapping[chart_type]
        plot = chart_func(data, config)
        
        # 生成HTML
        html_content = file_html(plot, CDN, config.get('title', f'{chart_type.title()} Chart'))
        
        # 获取组件（script和div）
        script, div = components(plot)
        
        return {
            'html': html_content,
            'script': script,
            'div': div,
            'chart_type': chart_type,
            'adapter': self.name,
            'config': config
        }
        
    def _create_line_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建折线图"""
        p = figure(
            title=config.get('title', 'Line Chart'),
            x_axis_label=config.get('x_label', 'X'),
            y_axis_label=config.get('y_label', 'Y'),
            width=config.get('width', 800),
            height=config.get('height', 400),
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        x_data = data['x']
        y_data = data['y']
        
        if isinstance(y_data, dict):
            # 多系列数据
            colors = Category20[min(len(y_data), 20)]
            for i, (series_name, series_data) in enumerate(y_data.items()):
                source = ColumnDataSource(data=dict(
                    x=x_data,
                    y=series_data,
                    series=[series_name] * len(x_data)
                ))
                
                line = p.line(
                    'x', 'y', source=source,
                    legend_label=series_name,
                    line_width=config.get('line_width', 2),
                    color=colors[i % len(colors)]
                )
                
                if config.get('show_circles', True):
                    p.circle(
                        'x', 'y', source=source,
                        size=config.get('circle_size', 6),
                        color=colors[i % len(colors)],
                        alpha=0.7
                    )
                    
                # 添加悬停工具
                if config.get('show_hover', True):
                    hover = HoverTool(
                        tooltips=[
                            ('Series', '@series'),
                            ('X', '@x'),
                            ('Y', '@y')
                        ],
                        renderers=[line]
                    )
                    p.add_tools(hover)
        else:
            # 单系列数据
            source = ColumnDataSource(data=dict(x=x_data, y=y_data))
            
            line = p.line(
                'x', 'y', source=source,
                legend_label=config.get('series_name', 'Series 1'),
                line_width=config.get('line_width', 2),
                color=config.get('color', 'blue')
            )
            
            if config.get('show_circles', True):
                p.circle(
                    'x', 'y', source=source,
                    size=config.get('circle_size', 6),
                    color=config.get('color', 'blue'),
                    alpha=0.7
                )
                
            # 添加悬停工具
            if config.get('show_hover', True):
                hover = HoverTool(
                    tooltips=[('X', '@x'), ('Y', '@y')],
                    renderers=[line]
                )
                p.add_tools(hover)
                
        p.legend.location = config.get('legend_location', 'top_left')
        p.legend.click_policy = "hide"
        
        return p
        
    def _create_bar_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建柱状图"""
        x_data = data['x']
        y_data = data['y']
        
        if isinstance(y_data, dict):
            # 多系列柱状图
            from bokeh.models import FactorRange
            from bokeh.transform import dodge
            
            series_names = list(y_data.keys())
            factors = [(str(x), series) for x in x_data for series in series_names]
            
            p = figure(
                x_range=FactorRange(*factors),
                title=config.get('title', 'Bar Chart'),
                width=config.get('width', 800),
                height=config.get('height', 400),
                tools="pan,wheel_zoom,box_zoom,reset,save"
            )
            
            colors = Category20[min(len(series_names), 20)]
            
            for i, (series_name, series_data) in enumerate(y_data.items()):
                source = ColumnDataSource(data=dict(
                    x=[str(x) for x in x_data],
                    y=series_data,
                    series=[series_name] * len(x_data)
                ))
                
                p.vbar(
                    x=dodge('x', -0.25 + i * 0.5 / len(series_names), range=p.x_range),
                    top='y',
                    width=0.4 / len(series_names),
                    source=source,
                    color=colors[i % len(colors)],
                    legend_label=series_name
                )
        else:
            # 单系列柱状图
            p = figure(
                x_range=[str(x) for x in x_data],
                title=config.get('title', 'Bar Chart'),
                x_axis_label=config.get('x_label', 'X'),
                y_axis_label=config.get('y_label', 'Y'),
                width=config.get('width', 800),
                height=config.get('height', 400),
                tools="pan,wheel_zoom,box_zoom,reset,save"
            )
            
            source = ColumnDataSource(data=dict(
                x=[str(x) for x in x_data],
                y=y_data
            ))
            
            p.vbar(
                x='x', top='y', width=0.8, source=source,
                color=config.get('color', 'blue'),
                alpha=0.7
            )
            
            # 添加悬停工具
            if config.get('show_hover', True):
                hover = HoverTool(tooltips=[('X', '@x'), ('Y', '@y')])
                p.add_tools(hover)
                
        p.xgrid.grid_line_color = None
        p.legend.location = config.get('legend_location', 'top_left')
        p.legend.orientation = "horizontal"
        
        return p
        
    def _create_scatter_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建散点图"""
        p = figure(
            title=config.get('title', 'Scatter Plot'),
            x_axis_label=config.get('x_label', 'X'),
            y_axis_label=config.get('y_label', 'Y'),
            width=config.get('width', 800),
            height=config.get('height', 400),
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        x_data = data['x']
        y_data = data['y']
        
        # 支持颜色映射
        if 'colors' in data:
            colors = data['colors']
            mapper = linear_cmap(field_name='colors', palette=Viridis256, 
                               low=min(colors), high=max(colors))
            
            source = ColumnDataSource(data=dict(
                x=x_data,
                y=y_data,
                colors=colors
            ))
            
            scatter = p.circle(
                'x', 'y', source=source,
                size=config.get('size', 10),
                color=mapper,
                alpha=config.get('alpha', 0.7)
            )
            
            # 添加颜色条
            color_bar = ColorBar(color_mapper=mapper['transform'], 
                               width=8, location=(0,0))
            p.add_layout(color_bar, 'right')
        else:
            source = ColumnDataSource(data=dict(x=x_data, y=y_data))
            
            scatter = p.circle(
                'x', 'y', source=source,
                size=config.get('size', 10),
                color=config.get('color', 'blue'),
                alpha=config.get('alpha', 0.7)
            )
            
        # 添加悬停工具
        if config.get('show_hover', True):
            tooltips = [('X', '@x'), ('Y', '@y')]
            if 'colors' in data:
                tooltips.append(('Value', '@colors'))
            hover = HoverTool(tooltips=tooltips, renderers=[scatter])
            p.add_tools(hover)
            
        return p
        
    def _create_heatmap(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建热力图"""
        from bokeh.models import LinearColorMapper
        from bokeh.palettes import RdYlBu11
        
        x_data = data['x']
        y_data = data['y']
        values = data['values']
        
        # 创建数据源
        source = ColumnDataSource(data=dict(
            x=x_data,
            y=y_data,
            values=values
        ))
        
        p = figure(
            title=config.get('title', 'Heatmap'),
            x_axis_label=config.get('x_label', 'X'),
            y_axis_label=config.get('y_label', 'Y'),
            width=config.get('width', 800),
            height=config.get('height', 400),
            tools="pan,wheel_zoom,box_zoom,reset,save",
            x_range=list(set(x_data)),
            y_range=list(set(y_data))
        )
        
        # 颜色映射
        mapper = LinearColorMapper(
            palette=config.get('palette', RdYlBu11),
            low=min(values),
            high=max(values)
        )
        
        p.rect(
            x='x', y='y', width=1, height=1,
            source=source,
            fill_color={'field': 'values', 'transform': mapper},
            line_color=None
        )
        
        # 添加颜色条
        color_bar = ColorBar(color_mapper=mapper, width=8, location=(0,0))
        p.add_layout(color_bar, 'right')
        
        # 添加悬停工具
        if config.get('show_hover', True):
            hover = HoverTool(tooltips=[('X', '@x'), ('Y', '@y'), ('Value', '@values')])
            p.add_tools(hover)
            
        return p
        
    def _create_histogram(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建直方图"""
        values = data['values']
        bins = config.get('bins', 30)
        
        hist, edges = np.histogram(values, bins=bins)
        
        p = figure(
            title=config.get('title', 'Histogram'),
            x_axis_label=config.get('x_label', 'Value'),
            y_axis_label=config.get('y_label', 'Frequency'),
            width=config.get('width', 800),
            height=config.get('height', 400),
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        p.quad(
            top=hist, bottom=0, left=edges[:-1], right=edges[1:],
            fill_color=config.get('color', 'blue'),
            line_color="white",
            alpha=0.7
        )
        
        return p
        
    def _create_box_plot(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建箱线图"""
        # 简化的箱线图实现
        groups = data['groups']
        values = data['values']
        
        # 计算统计量
        df = pd.DataFrame({'group': groups, 'value': values})
        stats = df.groupby('group')['value'].describe()
        
        p = figure(
            title=config.get('title', 'Box Plot'),
            x_range=list(stats.index),
            x_axis_label=config.get('x_label', 'Group'),
            y_axis_label=config.get('y_label', 'Value'),
            width=config.get('width', 800),
            height=config.get('height', 400),
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        # 绘制箱线图的各个部分
        for i, (group, group_stats) in enumerate(stats.iterrows()):
            # 箱体
            p.quad(
                top=group_stats['75%'], bottom=group_stats['25%'],
                left=i-0.2, right=i+0.2,
                fill_color='blue', alpha=0.7
            )
            
            # 中位线
            p.line([i-0.2, i+0.2], [group_stats['50%'], group_stats['50%']], 
                  line_color='red', line_width=2)
            
            # 须线
            p.line([i, i], [group_stats['25%'], group_stats['min']], line_color='black')
            p.line([i, i], [group_stats['75%'], group_stats['max']], line_color='black')
            
        return p
        
    def _create_area_chart(self, data: Dict[str, Any], config: Dict[str, Any]):
        """创建面积图"""
        p = figure(
            title=config.get('title', 'Area Chart'),
            x_axis_label=config.get('x_label', 'X'),
            y_axis_label=config.get('y_label', 'Y'),
            width=config.get('width', 800),
            height=config.get('height', 400),
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        
        x_data = data['x']
        y_data = data['y']
        
        if isinstance(y_data, dict):
            # 堆叠面积图
            colors = Category20[min(len(y_data), 20)]
            y_stack = np.zeros(len(x_data))
            
            for i, (series_name, series_data) in enumerate(y_data.items()):
                y_top = y_stack + series_data
                
                p.patch(
                    x=list(x_data) + list(reversed(x_data)),
                    y=list(y_top) + list(reversed(y_stack)),
                    color=colors[i % len(colors)],
                    alpha=0.7,
                    legend_label=series_name
                )
                
                y_stack = y_top
        else:
            # 单系列面积图
            y_bottom = [0] * len(x_data)
            
            p.patch(
                x=list(x_data) + list(reversed(x_data)),
                y=list(y_data) + list(reversed(y_bottom)),
                color=config.get('color', 'blue'),
                alpha=0.7
            )
            
        p.legend.location = config.get('legend_location', 'top_left')
        
        return p