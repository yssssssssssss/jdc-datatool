"""ECharts可视化适配器

基于pyecharts库实现的ECharts图表生成适配器
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import json
import time
import psutil
import os
from pyecharts import options as opts
from pyecharts.charts import (
    Bar, Line, Pie, Scatter, Radar, Funnel, Gauge, 
    WordCloud, HeatMap, TreeMap, Sankey, Graph, 
    Parallel, ThemeRiver, Calendar, Sunburst
)
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from ..core.base_adapter import BaseVisualizationAdapter


class EChartsAdapter(BaseVisualizationAdapter):
    """ECharts适配器
    
    使用pyecharts库生成ECharts图表，支持多种图表类型和交互功能
    """
    
    def __init__(self, config: Dict = None):
        """初始化ECharts适配器
        
        Args:
            config: 配置字典
        """
        super().__init__()
        self.config = config or {}
        self.library_name = "echarts"
        self.library_version = self.get_library_version()
        self.default_theme = self.config.get('theme', 'default')
        self.default_width = self.config.get('width', 800)
        self.default_height = self.config.get('height', 600)
        
        # 支持的图表类型映射
        self.chart_type_mapping = {
            'bar': Bar,
            'line': Line,
            'pie': Pie,
            'scatter': Scatter,
            'radar': Radar,
            'funnel': Funnel,
            'gauge': Gauge,
            'wordcloud': WordCloud,
            'heatmap': HeatMap,
            'treemap': TreeMap,
            'sankey': Sankey,
            'graph': Graph,
            'parallel': Parallel,
            'themeriver': ThemeRiver,
            'calendar': Calendar,
            'sunburst': Sunburst
        }
        
        # 主题映射
        self.theme_mapping = {
            'default': ThemeType.WHITE,
            'dark': ThemeType.DARK,
            'vintage': ThemeType.VINTAGE,
            'westeros': ThemeType.WESTEROS,
            'essos': ThemeType.ESSOS,
            'wonderland': ThemeType.WONDERLAND,
            'walden': ThemeType.WALDEN,
            'chalk': ThemeType.CHALK,
            'infographic': ThemeType.INFOGRAPHIC,
            'macarons': ThemeType.MACARONS,
            'roma': ThemeType.ROMA,
            'shine': ThemeType.SHINE,
            'purple_passion': ThemeType.PURPLE_PASSION
        }
        
        # 设置默认主题
        self.default_theme = self.theme_mapping.get(
            self.config.get('theme', 'default'), 
            ThemeType.WHITE
        )
    
    def get_library_name(self) -> str:
        """获取库名称"""
        return "echarts"
    
    def get_library_version(self) -> str:
        """获取ECharts库版本"""
        try:
            import pyecharts
            return pyecharts.__version__
        except ImportError:
            return "未安装"
    
    def get_supported_charts(self) -> List[str]:
        """获取支持的图表类型
        
        Returns:
            List[str]: 支持的图表类型列表
        """
        return list(self.chart_type_mapping.keys())
    
    def get_library_info(self) -> Dict:
        """获取库信息
        
        Returns:
            Dict: 库信息字典
        """
        return {
            'name': self.library_name,
            'version': self.library_version,
            'description': 'Apache ECharts Python binding',
            'features': [
                '丰富的图表类型',
                '强大的交互功能',
                '优秀的渲染性能',
                'Web友好的输出格式',
                '主题和样式定制',
                '动画效果支持'
            ],
            'supported_formats': ['html', 'json', 'png', 'jpg', 'svg', 'pdf'],
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
        if chart_type not in self.chart_type_mapping:
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
        if chart_type in ['bar', 'line']:
            # 需要至少一个数值列
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) == 0:
                self.logger.error("柱状图和折线图需要至少一个数值列")
                return False
        
        elif chart_type == 'pie':
            # 需要数值列和标签列
            if len(data.columns) < 2:
                self.logger.error("饼图需要至少两列数据（标签和数值）")
                return False
        
        elif chart_type == 'scatter':
            # 需要至少两个数值列
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) < 2:
                self.logger.error("散点图需要至少两个数值列")
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
            chart_class = self.chart_type_mapping[chart_type]
            
            # 创建图表实例
            chart = self._create_chart_instance(chart_class, config)
            
            # 添加数据
            self._add_data_to_chart(chart, data, config)
            
            # 设置全局选项
            self._set_global_options(chart, config)
            
            # 生成HTML
            html_content = chart.render_embed()
            
            # 获取图表选项（JSON格式）
            chart_options = chart.get_options()
            
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
                'options': chart_options,
                'config': config,
                'performance': self.performance_metrics.copy()
            }
            
        except Exception as e:
            self.logger.error(f"生成ECharts图表失败: {e}")
            raise
    
    def _create_chart_instance(self, chart_class, config: Dict):
        """创建图表实例
        
        Args:
            chart_class: 图表类
            config: 配置字典
        
        Returns:
            图表实例
        """
        # 获取主题
        theme = self.theme_mapping.get(
            config.get('theme', 'default'),
            self.default_theme
        )
        
        # 创建图表实例
        init_opts = opts.InitOpts(
            width=config.get('width', '800px'),
            height=config.get('height', '600px'),
            theme=theme,
            bg_color=config.get('bg_color', 'white'),
            animation_opts=opts.AnimationOpts(
                animation=config.get('animation', True),
                animation_duration=config.get('animation_duration', 1000)
            )
        )
        
        return chart_class(init_opts=init_opts)
    
    def _add_data_to_chart(self, chart, data: pd.DataFrame, config: Dict):
        """向图表添加数据
        
        Args:
            chart: 图表实例
            data: 数据DataFrame
            config: 配置字典
        """
        chart_type = config['chart_type']
        
        if chart_type in ['bar', 'line']:
            self._add_bar_line_data(chart, data, config)
        elif chart_type == 'pie':
            self._add_pie_data(chart, data, config)
        elif chart_type == 'scatter':
            self._add_scatter_data(chart, data, config)
        elif chart_type == 'radar':
            self._add_radar_data(chart, data, config)
        elif chart_type == 'heatmap':
            self._add_heatmap_data(chart, data, config)
        elif chart_type == 'wordcloud':
            self._add_wordcloud_data(chart, data, config)
        else:
            # 默认处理方式
            self._add_default_data(chart, data, config)
    
    def _add_bar_line_data(self, chart, data: pd.DataFrame, config: Dict):
        """添加柱状图/折线图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_columns = config.get('y_columns', [col for col in data.columns if col != x_column])
        
        # 设置X轴数据
        x_data = data[x_column].tolist()
        chart.add_xaxis(x_data)
        
        # 添加Y轴数据系列
        for y_col in y_columns:
            if y_col in data.columns:
                y_data = data[y_col].tolist()
                series_config = config.get('series_config', {}).get(y_col, {})
                
                chart.add_yaxis(
                    series_name=series_config.get('name', y_col),
                    y_axis=y_data,
                    label_opts=opts.LabelOpts(
                        is_show=series_config.get('show_label', False)
                    ),
                    itemstyle_opts=opts.ItemStyleOpts(
                        color=series_config.get('color')
                    )
                )
    
    def _add_pie_data(self, chart, data: pd.DataFrame, config: Dict):
        """添加饼图数据"""
        label_column = config.get('label_column', data.columns[0])
        value_column = config.get('value_column', data.columns[1])
        
        pie_data = [
            [row[label_column], row[value_column]] 
            for _, row in data.iterrows()
        ]
        
        chart.add(
            series_name=config.get('series_name', '数据'),
            data_pair=pie_data,
            radius=config.get('radius', ['30%', '70%']),
            center=config.get('center', ['50%', '50%']),
            label_opts=opts.LabelOpts(
                formatter="{b}: {c} ({d}%)"
            )
        )
    
    def _add_scatter_data(self, chart, data: pd.DataFrame, config: Dict):
        """添加散点图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        
        scatter_data = [
            [row[x_column], row[y_column]] 
            for _, row in data.iterrows()
        ]
        
        chart.add_xaxis([str(x) for x in data[x_column].unique()])
        chart.add_yaxis(
            series_name=config.get('series_name', '散点'),
            y_axis=scatter_data,
            symbol_size=config.get('symbol_size', 10)
        )
    
    def _add_radar_data(self, chart, data: pd.DataFrame, config: Dict):
        """添加雷达图数据"""
        # 雷达图需要特殊的数据结构
        indicators = config.get('indicators', [])
        if not indicators:
            # 自动生成指标
            numeric_cols = data.select_dtypes(include=['number']).columns
            indicators = [{'name': col, 'max': data[col].max()} for col in numeric_cols]
        
        chart.add_schema(schema=indicators)
        
        # 添加数据系列
        for idx, row in data.iterrows():
            values = [row[ind['name']] for ind in indicators if ind['name'] in row]
            chart.add(
                series_name=f"系列{idx+1}",
                data=[values]
            )
    
    def _add_heatmap_data(self, chart, data: pd.DataFrame, config: Dict):
        """添加热力图数据"""
        x_column = config.get('x_column', data.columns[0])
        y_column = config.get('y_column', data.columns[1])
        value_column = config.get('value_column', data.columns[2])
        
        # 准备数据
        heatmap_data = []
        for _, row in data.iterrows():
            heatmap_data.append([row[x_column], row[y_column], row[value_column]])
        
        x_data = sorted(data[x_column].unique())
        y_data = sorted(data[y_column].unique())
        
        chart.add_xaxis(x_data)
        chart.add_yaxis(
            series_name=config.get('series_name', '热力图'),
            yaxis_data=y_data,
            value=heatmap_data
        )
    
    def _add_wordcloud_data(self, chart, data: pd.DataFrame, config: Dict):
        """添加词云数据"""
        word_column = config.get('word_column', data.columns[0])
        weight_column = config.get('weight_column', data.columns[1] if len(data.columns) > 1 else None)
        
        if weight_column:
            wordcloud_data = [
                (row[word_column], row[weight_column]) 
                for _, row in data.iterrows()
            ]
        else:
            wordcloud_data = [
                (row[word_column], 1) 
                for _, row in data.iterrows()
            ]
        
        chart.add(
            series_name=config.get('series_name', '词云'),
            data_pair=wordcloud_data,
            word_size_range=config.get('word_size_range', [12, 60]),
            shape=config.get('shape', 'circle')
        )
    
    def _add_default_data(self, chart, data: pd.DataFrame, config: Dict):
        """默认数据添加方式"""
        # 简单的默认处理
        if hasattr(chart, 'add_xaxis') and hasattr(chart, 'add_yaxis'):
            x_data = data.iloc[:, 0].tolist()
            y_data = data.iloc[:, 1].tolist() if len(data.columns) > 1 else [1] * len(data)
            
            chart.add_xaxis(x_data)
            chart.add_yaxis('数据', y_data)
    
    def _set_global_options(self, chart, config: Dict):
        """设置全局选项
        
        Args:
            chart: 图表实例
            config: 配置字典
        """
        # 标题配置
        title_opts = opts.TitleOpts(
            title=config.get('title', ''),
            subtitle=config.get('subtitle', ''),
            pos_left=config.get('title_pos', 'center')
        )
        
        # 图例配置
        legend_opts = opts.LegendOpts(
            is_show=config.get('show_legend', True),
            pos_top=config.get('legend_pos', '5%')
        )
        
        # 工具箱配置
        toolbox_opts = opts.ToolboxOpts(
            is_show=config.get('show_toolbox', True),
            feature={
                'saveAsImage': {},
                'dataView': {'readOnly': False},
                'magicType': {'type': ['line', 'bar']},
                'restore': {},
                'dataZoom': {}
            }
        )
        
        # 数据缩放配置
        datazoom_opts = []
        if config.get('enable_datazoom', False):
            datazoom_opts = [
                opts.DataZoomOpts(type_="slider", range_start=0, range_end=100),
                opts.DataZoomOpts(type_="inside")
            ]
        
        # 应用全局选项
        chart.set_global_opts(
            title_opts=title_opts,
            legend_opts=legend_opts,
            toolbox_opts=toolbox_opts,
            datazoom_opts=datazoom_opts,
            xaxis_opts=opts.AxisOpts(
                name=config.get('x_axis_name', ''),
                type_=config.get('x_axis_type', 'category')
            ),
            yaxis_opts=opts.AxisOpts(
                name=config.get('y_axis_name', ''),
                type_=config.get('y_axis_type', 'value')
            )
        )
    
    def export_chart(self, chart_data: Any, format: str, options: Dict = None) -> bytes:
        """导出图表
        
        Args:
            chart_data: 图表数据（HTML字符串或图表实例）
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
                    return chart_data.render_embed().encode('utf-8')
            
            elif format.lower() == 'json':
                if hasattr(chart_data, 'get_options'):
                    options_dict = chart_data.get_options()
                    return json.dumps(options_dict, ensure_ascii=False, indent=2).encode('utf-8')
                else:
                    return json.dumps({'error': '无法获取图表选项'}).encode('utf-8')
            
            elif format.lower() in ['png', 'jpg', 'jpeg', 'svg', 'pdf']:
                # 对于图片格式，需要使用额外的工具
                self.logger.warning(f"ECharts适配器暂不直接支持{format}格式导出，建议使用HTML格式")
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
        return f"EChartsAdapter(version={self.library_version})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"EChartsAdapter(library={self.library_name}, version={self.library_version}, charts={len(self.chart_type_mapping)})"