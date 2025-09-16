"""Bokeh可视化适配器

基于Bokeh库实现的交互式图表生成适配器
"""

from typing import Dict, List, Any, Optional, Union
import pandas as pd
import json
import time
import psutil
import os
import io
from bokeh.plotting import figure, save, output_file
from bokeh.models import (
    HoverTool, PanTool, WheelZoomTool, BoxZoomTool, ResetTool, SaveTool,
    ColumnDataSource, ColorBar, LinearColorMapper, BasicTicker, PrintfTickFormatter,
    Legend, LegendItem, Title, Div
)
from bokeh.layouts import column, row, gridplot
from bokeh.palettes import Category20, Viridis256, Spectral6
from bokeh.transform import cumsum, factor_cmap
from bokeh.embed import file_html, components
from bokeh.resources import CDN
from bokeh.io import export_png, export_svgs
from bokeh.themes import Theme
import numpy as np
from math import pi
from ..core.base_adapter import BaseVisualizationAdapter


class BokehAdapter(BaseVisualizationAdapter):
    """Bokeh适配器
    
    使用Bokeh库生成交互式图表，支持多种图表类型和丰富的交互功能
    """
    
    def __init__(self, config: Dict = None):
        """初始化Bokeh适配器
        
        Args:
            config: 配置字典
        """
        super().__init__()
        self.config = config or {}
        self.library_name = "bokeh"
        self.library_version = self.get_library_version()
        self.default_width = self.config.get('width', 800)
        self.default_height = self.config.get('height', 600)
        
        # 支持的图表类型
        self.supported_chart_types = [
            'line', 'scatter', 'bar', 'histogram', 'box', 'heatmap',
            'area', 'step', 'circle', 'square', 'triangle', 'diamond',
            'hex', 'multi_line', 'patch', 'quad', 'rect', 'segment',
            'wedge', 'annular_wedge', 'arc', 'bezier', 'image', 'image_rgba'
        ]
        
        # 默认工具
        self.default_tools = [
            PanTool(), WheelZoomTool(), BoxZoomTool(), ResetTool(), SaveTool()
        ]
        
        # 颜色调色板
        self.color_palettes = {
            'category20': Category20[20],
            'viridis': Viridis256,
            'spectral': Spectral6
        }
        
        # 设置默认主题
        self.default_theme = self._get_theme()
    
    def get_library_name(self) -> str:
        """获取库名称"""
        return "bokeh"
    
    def get_library_version(self) -> str:
        """获取Bokeh库版本"""
        try:
            import bokeh
            return bokeh.__version__
        except ImportError:
            return "未安装"
    
    def _get_library_version(self) -> str:
        """获取库版本"""
        try:
            import bokeh
            return bokeh.__version__
        except:
            return "unknown"
    
    def _get_theme(self) -> Optional[Theme]:
        """获取主题配置"""
        theme_name = self.config.get('theme', 'caliber')
        
        # 自定义主题配置
        theme_configs = {
            'caliber': {
                'attrs': {
                    'Figure': {
                        'background_fill_color': '#f5f5f5',
                        'border_fill_color': 'white',
                        'outline_line_color': '#444444'
                    },
                    'Axis': {
                        'axis_line_color': '#444444',
                        'major_tick_line_color': '#444444',
                        'minor_tick_line_color': '#444444'
                    },
                    'Grid': {
                        'grid_line_color': 'white',
                        'grid_line_width': 1
                    }
                }
            },
            'dark': {
                'attrs': {
                    'Figure': {
                        'background_fill_color': '#2F2F2F',
                        'border_fill_color': '#2F2F2F',
                        'outline_line_color': '#444444'
                    },
                    'Axis': {
                        'axis_line_color': 'white',
                        'major_tick_line_color': 'white',
                        'minor_tick_line_color': 'white',
                        'axis_label_text_color': 'white',
                        'major_label_text_color': 'white'
                    },
                    'Grid': {
                        'grid_line_color': '#444444',
                        'grid_line_alpha': 0.3
                    },
                    'Title': {
                        'text_color': 'white'
                    }
                }
            }
        }
        
        if theme_name in theme_configs:
            return Theme(json=theme_configs[theme_name])
        return None
    
    def get_supported_charts(self) -> List[str]:
        """获取支持的图表类型
        
        Returns:
            List[str]: 支持的图表类型列表
        """
        return self.supported_chart_types.copy()
    
    def get_library_info(self) -> Dict:
        """获取库信息
        
        Returns:
            Dict: 库信息字典
        """
        return {
            'name': self.library_name,
            'version': self.library_version,
            'description': 'Interactive visualization library for modern web browsers',
            'features': [
                '强大的交互功能',
                '高性能大数据支持',
                '丰富的图表类型',
                '服务器集成友好',
                '自定义能力强',
                '响应式布局支持'
            ],
            'supported_formats': ['html', 'json', 'png', 'svg'],
            'chart_types': self.get_supported_charts()
        }
    
    def validate_config(self, config: Dict) -> bool:
        """验证图表配置
        
        Args:
            config: 图表配置字典
        
        Returns:
            bool: 配置是否有效
        """
        required_fields = ['chart_type']
        
        # 检查必需字段
        for field in required_fields:
            if field not in config:
                self.logger.error(f"缺少必需字段: {field}")
                return False
        
        # 检查图表类型
        chart_type = config['chart_type']
        if chart_type not in self.supported_chart_types:
            self.logger.error(f"不支持的图表类型: {chart_type}")
            return False
        
        return True
    
    def validate_data(self, data: pd.DataFrame, config: Dict) -> bool:
        """验证数据
        
        Args:
            data: 数据DataFrame
            config: 图表配置
        
        Returns:
            bool: 数据是否有效
        """
        if data.empty:
            self.logger.error("数据为空")
            return False
        
        chart_type = config['chart_type']
        
        # 根据图表类型验证数据结构
        if chart_type in ['line', 'scatter', 'circle']:
            # 需要至少两列数据
            if len(data.columns) < 2:
                self.logger.error(f"{chart_type}图需要至少两列数据")
                return False
        
        elif chart_type == 'bar':
            # 需要分类列和数值列
            if len(data.columns) < 2:
                self.logger.error("柱状图需要至少两列数据（分类和数值）")
                return False
        
        elif chart_type == 'histogram':
            # 需要至少一个数值列
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) == 0:
                self.logger.error("直方图需要至少一个数值列")
                return False
        
        elif chart_type == 'heatmap':
            # 需要至少三列数据（x, y, value）
            if len(data.columns) < 3:
                self.logger.error("热力图需要至少三列数据（x, y, value）")
                return False
        
        return True
    
    def generate_chart(self, data: pd.DataFrame, config: Dict) -> Dict:
        """生成图表
        
        Args:
            data: 数据DataFrame
            config: 图表配置
        
        Returns:
            Dict: 图表结果
        """
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            chart_type = config['chart_type']
            
            # 创建图表
            plot = self._create_plot(data, config)
            
            # 添加数据
            self._add_data_to_plot(plot, data, config)
            
            # 设置样式和选项
            self._configure_plot(plot, config)
            
            # 生成HTML
            html_content = self._generate_html(plot, config)
            
            # 计算性能指标
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            # 更新性能指标
            self.performance_metrics.update({
                'render_time': (end_time - start_time) * 1000,  # 毫秒
                'memory_usage': end_memory - start_memory,
                'file_size': len(html_content.encode('utf-8')),
                'chart_type': chart_type,
                'data_points': len(data)
            })
            
            return {
                'chart_type': chart_type,
                'library': self.library_name,
                'html': html_content,
                'plot_object': plot,
                'config': config,
                'performance': self.performance_metrics.copy()
            }
            
        except Exception as e:
            self.logger.error(f"生成Bokeh图表失败: {e}")
            raise
    
    def _create_plot(self, data: pd.DataFrame, config: Dict):
        """创建基础图表对象
        
        Args:
            data: 数据DataFrame
            config: 配置字典
        
        Returns:
            Bokeh图表对象
        """
        # 获取图表尺寸
        width = config.get('width', 800)
        height = config.get('height', 600)
        
        # 获取工具列表
        tools = config.get('tools', self.default_tools)
        if isinstance(tools, list) and all(isinstance(t, str) for t in tools):
            # 如果是字符串列表，转换为工具对象
            tool_map = {
                'pan': PanTool(),
                'wheel_zoom': WheelZoomTool(),
                'box_zoom': BoxZoomTool(),
                'reset': ResetTool(),
                'save': SaveTool(),
                'hover': HoverTool()
            }
            tools = [tool_map.get(t, t) for t in tools if t in tool_map]
        
        # 创建图表
        plot = figure(
            width=width,
            height=height,
            title=config.get('title', ''),
            tools=tools,
            x_axis_label=config.get('x_axis_label', ''),
            y_axis_label=config.get('y_axis_label', ''),
            toolbar_location=config.get('toolbar_location', 'above')
        )
        
        # 应用主题
        if self.default_theme:
            plot.theme = self.default_theme
        
        return plot
    
    def _add_data_to_plot(self, plot, data: pd.DataFrame, config: Dict):
        """向图表添加数据
        
        Args:
            plot: Bokeh图表对象
            data: 数据DataFrame
            config: 配置字典
        """
        chart_type = config['chart_type']
        
        if chart_type == 'line':
            self._add_line_data(plot, data, config)
        elif chart_type == 'scatter':
            self._add_scatter_data(plot, data, config)
        elif chart_type == 'bar':
            self._add_bar_data(plot, data, config)
        elif chart_type == 'histogram':
            self._add_histogram_data(plot, data, config)
        elif chart_type == 'heatmap':
            self._add_heatmap_data(plot, data, config)
        elif chart_type == 'area':
            self._add_area_data(plot, data, config)
        elif chart_type in ['circle', 'square', 'triangle', 'diamond']:
            self._add_marker_data(plot, data, config)
        else:
            # 默认处理为散点图
            self._add_scatter_data(plot, data, config)
    
    def _add_line_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加折线图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_columns = config.get('y_columns', [col for col in data.columns if col != x_column])
        
        colors = self._get_colors(len(y_columns), config)
        
        for i, y_col in enumerate(y_columns):
            if y_col in data.columns:
                source = ColumnDataSource(data={
                    'x': data[x_column],
                    'y': data[y_col]
                })
                
                line = plot.line(
                    'x', 'y', source=source,
                    legend_label=config.get('series_config', {}).get(y_col, {}).get('name', y_col),
                    line_width=config.get('line_width', 2),
                    color=colors[i % len(colors)],
                    alpha=config.get('alpha', 1.0)
                )
                
                # 添加悬停工具
                if config.get('show_hover', True):
                    hover = HoverTool(
                        tooltips=[(x_column, '@x'), (y_col, '@y')],
                        renderers=[line]
                    )
                    plot.add_tools(hover)
    
    def _add_scatter_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加散点图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        
        source = ColumnDataSource(data={
            'x': data[x_column],
            'y': data[y_column]
        })
        
        # 添加额外的数据列用于悬停显示
        for col in data.columns:
            if col not in ['x', 'y']:
                source.data[col] = data[col]
        
        scatter = plot.scatter(
            'x', 'y', source=source,
            size=config.get('size', 10),
            color=config.get('color', 'blue'),
            alpha=config.get('alpha', 0.7)
        )
        
        # 添加悬停工具
        if config.get('show_hover', True):
            tooltips = [(x_column, '@x'), (y_column, '@y')]
            # 添加其他列的悬停信息
            for col in data.columns:
                if col not in [x_column, y_column]:
                    tooltips.append((col, f'@{col}'))
            
            hover = HoverTool(tooltips=tooltips, renderers=[scatter])
            plot.add_tools(hover)
    
    def _add_bar_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加柱状图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        
        # 处理分类数据
        if data[x_column].dtype == 'object':
            x_range = data[x_column].unique().tolist()
            plot.x_range.factors = x_range
            x_data = data[x_column]
        else:
            x_data = data[x_column]
        
        source = ColumnDataSource(data={
            'x': x_data,
            'y': data[y_column]
        })
        
        bars = plot.vbar(
            x='x', top='y', source=source,
            width=config.get('bar_width', 0.8),
            color=config.get('color', 'blue'),
            alpha=config.get('alpha', 0.8)
        )
        
        # 添加悬停工具
        if config.get('show_hover', True):
            hover = HoverTool(
                tooltips=[(x_column, '@x'), (y_column, '@y')],
                renderers=[bars]
            )
            plot.add_tools(hover)
    
    def _add_histogram_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加直方图数据"""
        column = config.get('column', data.columns[0])
        bins = config.get('bins', 30)
        
        # 计算直方图
        hist, edges = np.histogram(data[column], bins=bins)
        
        source = ColumnDataSource(data={
            'top': hist,
            'left': edges[:-1],
            'right': edges[1:]
        })
        
        bars = plot.quad(
            top='top', bottom=0, left='left', right='right',
            source=source,
            fill_color=config.get('color', 'blue'),
            line_color='white',
            alpha=config.get('alpha', 0.7)
        )
        
        # 添加悬停工具
        if config.get('show_hover', True):
            hover = HoverTool(
                tooltips=[('区间', '@left - @right'), ('频数', '@top')],
                renderers=[bars]
            )
            plot.add_tools(hover)
    
    def _add_heatmap_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加热力图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        value_column = config.get('value_column', data.columns[2])
        
        # 创建数据透视表
        pivot_data = data.pivot_table(
            values=value_column,
            index=y_column,
            columns=x_column,
            fill_value=0
        )
        
        # 准备热力图数据
        x_labels = pivot_data.columns.tolist()
        y_labels = pivot_data.index.tolist()
        
        # 创建网格数据
        x_grid, y_grid = np.meshgrid(range(len(x_labels)), range(len(y_labels)))
        x_flat = x_grid.flatten()
        y_flat = y_grid.flatten()
        values_flat = pivot_data.values.flatten()
        
        # 颜色映射
        mapper = LinearColorMapper(
            palette=config.get('palette', Viridis256),
            low=values_flat.min(),
            high=values_flat.max()
        )
        
        source = ColumnDataSource(data={
            'x': x_flat,
            'y': y_flat,
            'values': values_flat,
            'x_labels': [x_labels[i] for i in x_flat],
            'y_labels': [y_labels[i] for i in y_flat]
        })
        
        rects = plot.rect(
            x='x', y='y', width=1, height=1,
            source=source,
            fill_color={'field': 'values', 'transform': mapper},
            line_color=None
        )
        
        # 设置轴标签
        plot.xaxis.ticker = list(range(len(x_labels)))
        plot.xaxis.major_label_overrides = {i: label for i, label in enumerate(x_labels)}
        plot.yaxis.ticker = list(range(len(y_labels)))
        plot.yaxis.major_label_overrides = {i: label for i, label in enumerate(y_labels)}
        
        # 添加颜色条
        if config.get('show_colorbar', True):
            color_bar = ColorBar(
                color_mapper=mapper,
                width=8,
                location=(0, 0),
                ticker=BasicTicker(desired_num_ticks=10),
                formatter=PrintfTickFormatter(format="%0.2f")
            )
            plot.add_layout(color_bar, 'right')
        
        # 添加悬停工具
        if config.get('show_hover', True):
            hover = HoverTool(
                tooltips=[
                    (x_column, '@x_labels'),
                    (y_column, '@y_labels'),
                    (value_column, '@values')
                ],
                renderers=[rects]
            )
            plot.add_tools(hover)
    
    def _add_area_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加面积图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        
        source = ColumnDataSource(data={
            'x': data[x_column],
            'y': data[y_column]
        })
        
        area = plot.varea(
            x='x', y1=0, y2='y',
            source=source,
            color=config.get('color', 'blue'),
            alpha=config.get('alpha', 0.5)
        )
        
        # 添加边界线
        if config.get('show_line', True):
            plot.line(
                'x', 'y', source=source,
                line_width=config.get('line_width', 2),
                color=config.get('line_color', 'blue')
            )
    
    def _add_marker_data(self, plot, data: pd.DataFrame, config: Dict):
        """添加标记点数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        chart_type = config['chart_type']
        
        source = ColumnDataSource(data={
            'x': data[x_column],
            'y': data[y_column]
        })
        
        marker_kwargs = {
            'x': 'x',
            'y': 'y',
            'source': source,
            'size': config.get('size', 10),
            'color': config.get('color', 'blue'),
            'alpha': config.get('alpha', 0.7)
        }
        
        if chart_type == 'circle':
            markers = plot.circle(**marker_kwargs)
        elif chart_type == 'square':
            markers = plot.square(**marker_kwargs)
        elif chart_type == 'triangle':
            markers = plot.triangle(**marker_kwargs)
        elif chart_type == 'diamond':
            markers = plot.diamond(**marker_kwargs)
        else:
            markers = plot.circle(**marker_kwargs)
        
        # 添加悬停工具
        if config.get('show_hover', True):
            hover = HoverTool(
                tooltips=[(x_column, '@x'), (y_column, '@y')],
                renderers=[markers]
            )
            plot.add_tools(hover)
    
    def _configure_plot(self, plot, config: Dict):
        """配置图表样式和选项
        
        Args:
            plot: Bokeh图表对象
            config: 配置字典
        """
        # 设置标题
        if config.get('title'):
            plot.title.text = config['title']
            plot.title.text_font_size = config.get('title_font_size', '16pt')
            plot.title.align = config.get('title_align', 'center')
        
        # 设置轴标签
        if config.get('x_axis_label'):
            plot.xaxis.axis_label = config['x_axis_label']
            plot.xaxis.axis_label_text_font_size = config.get('axis_label_font_size', '12pt')
        
        if config.get('y_axis_label'):
            plot.yaxis.axis_label = config['y_axis_label']
            plot.yaxis.axis_label_text_font_size = config.get('axis_label_font_size', '12pt')
        
        # 设置网格
        if not config.get('show_grid', True):
            plot.grid.visible = False
        else:
            plot.grid.grid_line_alpha = config.get('grid_alpha', 0.3)
        
        # 设置图例
        if config.get('show_legend', True):
            plot.legend.location = config.get('legend_location', 'top_right')
            plot.legend.click_policy = config.get('legend_click_policy', 'hide')
        else:
            plot.legend.visible = False
        
        # 设置背景
        if config.get('background_color'):
            plot.background_fill_color = config['background_color']
        
        if config.get('border_color'):
            plot.border_fill_color = config['border_color']
    
    def _generate_html(self, plot, config: Dict) -> str:
        """生成HTML内容
        
        Args:
            plot: Bokeh图表对象
            config: 配置字典
        
        Returns:
            str: HTML内容
        """
        # 创建布局
        layout = plot
        
        # 如果有多个图表，创建网格布局
        if config.get('subplot_config'):
            layout = self._create_subplot_layout(plot, config)
        
        # 生成HTML
        html = file_html(layout, CDN, config.get('title', 'Bokeh Plot'))
        
        return html
    
    def _create_subplot_layout(self, plot, config: Dict):
        """创建子图布局
        
        Args:
            plot: 主图表对象
            config: 配置字典
        
        Returns:
            布局对象
        """
        subplot_config = config.get('subplot_config', {})
        layout_type = subplot_config.get('type', 'grid')
        
        if layout_type == 'grid':
            ncols = subplot_config.get('ncols', 2)
            return gridplot([[plot]], ncols=ncols)
        elif layout_type == 'column':
            return column([plot])
        elif layout_type == 'row':
            return row([plot])
        else:
            return plot
    
    def _get_colors(self, n_colors: int, config: Dict) -> List[str]:
        """获取颜色列表
        
        Args:
            n_colors: 需要的颜色数量
            config: 配置字典
        
        Returns:
            List[str]: 颜色列表
        """
        palette_name = config.get('color_palette', 'category20')
        
        if palette_name in self.color_palettes:
            palette = self.color_palettes[palette_name]
            if isinstance(palette, list):
                return palette[:n_colors] if len(palette) >= n_colors else palette * ((n_colors // len(palette)) + 1)
            else:
                # 对于连续调色板，取样本
                step = len(palette) // n_colors
                return [palette[i * step] for i in range(n_colors)]
        else:
            # 默认颜色
            default_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            return default_colors[:n_colors] if len(default_colors) >= n_colors else default_colors * ((n_colors // len(default_colors)) + 1)
    
    def export_chart(self, chart_data: Any, format: str, options: Dict = None) -> bytes:
        """导出图表
        
        Args:
            chart_data: 图表数据（HTML字符串或图表对象）
            format: 导出格式
            options: 导出选项
        
        Returns:
            bytes: 导出的文件内容
        """
        options = options or {}
        
        try:
            if format.lower() == 'html':
                if isinstance(chart_data, str):
                    return chart_data.encode('utf-8')
                else:
                    html = file_html(chart_data, CDN, options.get('title', 'Bokeh Plot'))
                    return html.encode('utf-8')
            
            elif format.lower() == 'json':
                if hasattr(chart_data, 'to_json'):
                    return chart_data.to_json().encode('utf-8')
                else:
                    return json.dumps({'error': '无法获取图表JSON'}).encode('utf-8')
            
            elif format.lower() == 'png':
                # 需要安装selenium和geckodriver/chromedriver
                try:
                    png_buffer = io.BytesIO()
                    export_png(chart_data, filename=png_buffer)
                    return png_buffer.getvalue()
                except Exception as e:
                    self.logger.warning(f"PNG导出失败，可能需要安装selenium: {e}")
                    return self.export_chart(chart_data, 'html', options)
            
            elif format.lower() == 'svg':
                try:
                    svg_buffer = io.StringIO()
                    export_svgs(chart_data, filename=svg_buffer)
                    return svg_buffer.getvalue().encode('utf-8')
                except Exception as e:
                    self.logger.warning(f"SVG导出失败: {e}")
                    return self.export_chart(chart_data, 'html', options)
            
            else:
                raise ValueError(f"不支持的导出格式: {format}")
                
        except Exception as e:
            self.logger.error(f"导出图表失败: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict:
        """获取性能指标
        
        Returns:
            Dict: 性能指标字典
        """
        return self.performance_metrics.copy()
    
    def clear_performance_metrics(self):
        """清除性能指标"""
        self.performance_metrics = {
            'render_time': 0,
            'memory_usage': 0,
            'file_size': 0,
            'chart_type': '',
            'data_points': 0
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"BokehAdapter(version={self.library_version})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"BokehAdapter(library={self.library_name}, version={self.library_version}, charts={len(self.supported_chart_types)})"