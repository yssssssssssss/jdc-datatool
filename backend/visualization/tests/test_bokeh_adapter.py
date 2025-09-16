"""Bokeh适配器测试

测试Bokeh适配器的图表生成、配置验证和导出功能
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.visualization.adapters.bokeh_adapter import BokehAdapter
from backend.visualization.utils.performance import PerformanceMonitor


class TestBokehAdapter(unittest.TestCase):
    """Bokeh适配器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.adapter = BokehAdapter()
        
        # 测试数据
        self.test_data = [
            {"name": "Jan", "value": 100},
            {"name": "Feb", "value": 200},
            {"name": "Mar", "value": 150},
            {"name": "Apr", "value": 300},
            {"name": "May", "value": 250}
        ]
        
        self.line_data = [
            {"x": 1, "y": 10},
            {"x": 2, "y": 20},
            {"x": 3, "y": 15},
            {"x": 4, "y": 25},
            {"x": 5, "y": 30}
        ]
        
        self.scatter_data = [
            {"x": 10, "y": 20, "size": 5},
            {"x": 15, "y": 25, "size": 8},
            {"x": 20, "y": 30, "size": 12},
            {"x": 25, "y": 35, "size": 15}
        ]
        
        self.histogram_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6]
    
    def test_initialization(self):
        """测试适配器初始化"""
        adapter = BokehAdapter()
        
        # 检查基本属性
        self.assertIsNotNone(adapter.performance_monitor)
        self.assertIsInstance(adapter.performance_monitor, PerformanceMonitor)
        
        # 检查默认配置
        self.assertIsNotNone(adapter.default_config)
        self.assertIn("width", adapter.default_config)
        self.assertIn("height", adapter.default_config)
        self.assertIn("tools", adapter.default_config)
    
    def test_get_library_version(self):
        """测试获取库版本"""
        version = self.adapter.get_library_version()
        self.assertIsInstance(version, str)
        self.assertGreater(len(version), 0)
    
    def test_get_supported_chart_types(self):
        """测试获取支持的图表类型"""
        chart_types = self.adapter.get_supported_chart_types()
        
        expected_types = [
            "line", "scatter", "bar", "histogram", "area",
            "heatmap", "box", "violin", "step", "multi_line"
        ]
        
        for chart_type in expected_types:
            self.assertIn(chart_type, chart_types)
    
    def test_get_library_info(self):
        """测试获取库信息"""
        info = self.adapter.get_library_info()
        
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("description", info)
        self.assertIn("features", info)
        
        self.assertEqual(info["name"], "Bokeh")
        self.assertIsInstance(info["features"], list)
    
    def test_validate_config_valid(self):
        """测试有效配置验证"""
        valid_configs = [
            {"chart_type": "line", "data": self.line_data},
            {"chart_type": "scatter", "data": self.scatter_data, "title": "测试图表"},
            {"chart_type": "histogram", "data": self.histogram_data, "bins": 10}
        ]
        
        for config in valid_configs:
            with self.subTest(config=config):
                self.assertTrue(self.adapter.validate_config(config))
    
    def test_validate_config_invalid(self):
        """测试无效配置验证"""
        invalid_configs = [
            {},  # 空配置
            {"chart_type": "line"},  # 缺少数据
            {"data": self.test_data},  # 缺少图表类型
            {"chart_type": "invalid_type", "data": self.test_data},  # 无效图表类型
            {"chart_type": "line", "data": []},  # 空数据
        ]
        
        for config in invalid_configs:
            with self.subTest(config=config):
                self.assertFalse(self.adapter.validate_config(config))
    
    def test_validate_data_valid(self):
        """测试有效数据验证"""
        valid_data = [
            self.test_data,
            self.line_data,
            self.scatter_data,
            self.histogram_data,
            [{"x": 1, "y": 2}],  # 单个数据点
            {"x": [1, 2, 3], "y": [4, 5, 6]}  # 字典格式
        ]
        
        for data in valid_data:
            with self.subTest(data=data):
                self.assertTrue(self.adapter.validate_data(data))
    
    def test_validate_data_invalid(self):
        """测试无效数据验证"""
        invalid_data = [
            None,
            [],
            {},
            "",
            123
        ]
        
        for data in invalid_data:
            with self.subTest(data=data):
                self.assertFalse(self.adapter.validate_data(data))
    
    def test_generate_line_chart(self):
        """测试生成折线图"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={"title": "折线图测试"}
        )
        
        self.assertIsNotNone(chart)
        self.assertIn("plot", chart)
        self.assertIn("metadata", chart)
        
        # 检查图表对象类型
        plot = chart["plot"]
        self.assertIsNotNone(plot)
        
        # 检查元数据
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "line")
        self.assertEqual(metadata["library"], "Bokeh")
    
    def test_generate_scatter_chart(self):
        """测试生成散点图"""
        chart = self.adapter.generate_chart(
            chart_type="scatter",
            data=self.scatter_data,
            config={"title": "散点图测试"}
        )
        
        self.assertIsNotNone(chart)
        plot = chart["plot"]
        metadata = chart["metadata"]
        
        self.assertEqual(metadata["chart_type"], "scatter")
        self.assertIn("data_points", metadata["performance"])
    
    def test_generate_bar_chart(self):
        """测试生成柱状图"""
        chart = self.adapter.generate_chart(
            chart_type="bar",
            data=self.test_data,
            config={"title": "柱状图测试"}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "bar")
    
    def test_generate_histogram_chart(self):
        """测试生成直方图"""
        chart = self.adapter.generate_chart(
            chart_type="histogram",
            data=self.histogram_data,
            config={"title": "直方图测试", "bins": 5}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "histogram")
    
    def test_generate_area_chart(self):
        """测试生成面积图"""
        chart = self.adapter.generate_chart(
            chart_type="area",
            data=self.line_data,
            config={"title": "面积图测试"}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "area")
    
    def test_generate_unsupported_chart(self):
        """测试生成不支持的图表类型"""
        with self.assertRaises(ValueError) as context:
            self.adapter.generate_chart(
                chart_type="pie",  # Bokeh不支持饼图
                data=self.test_data
            )
        
        self.assertIn("不支持的图表类型", str(context.exception))
    
    def test_add_data_to_chart(self):
        """测试向图表添加数据"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        new_data = [{"x": 6, "y": 35}, {"x": 7, "y": 40}]
        updated_chart = self.adapter.add_data_to_chart(chart, new_data)
        
        self.assertIsNotNone(updated_chart)
        # 检查数据是否已添加到元数据中
        metadata = updated_chart["metadata"]
        self.assertIn("additional_data", metadata)
    
    def test_set_global_options(self):
        """测试设置全局选项"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        global_options = {
            "background_fill_color": "#f0f0f0",
            "border_fill_color": "white",
            "width": 800,
            "height": 600
        }
        
        updated_chart = self.adapter.set_global_options(chart, global_options)
        
        self.assertIsNotNone(updated_chart)
        # 检查全局选项是否已设置到元数据中
        metadata = updated_chart["metadata"]
        self.assertIn("global_options", metadata)
    
    def test_export_chart_html(self):
        """测试导出HTML格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        html_output = self.adapter.export_chart(chart, "html")
        
        self.assertIsInstance(html_output, str)
        self.assertIn("<!DOCTYPE html>", html_output)
        self.assertIn("bokeh", html_output.lower())
    
    def test_export_chart_json(self):
        """测试导出JSON格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        json_output = self.adapter.export_chart(chart, "json")
        
        self.assertIsInstance(json_output, str)
        
        # 验证JSON格式
        parsed_json = json.loads(json_output)
        self.assertIn("metadata", parsed_json)
        self.assertIn("chart_type", parsed_json["metadata"])
    
    def test_export_chart_png(self):
        """测试导出PNG格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        # 注意：实际的PNG导出需要额外的依赖，这里只测试接口
        try:
            png_output = self.adapter.export_chart(chart, "png")
            self.assertIsInstance(png_output, (str, bytes))
        except ImportError:
            # 如果缺少PNG导出依赖，跳过测试
            self.skipTest("PNG导出需要额外的依赖")
    
    def test_export_chart_unsupported_format(self):
        """测试导出不支持的格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        with self.assertRaises(ValueError) as context:
            self.adapter.export_chart(chart, "unsupported_format")
        
        self.assertIn("不支持的导出格式", str(context.exception))
    
    def test_theme_configuration(self):
        """测试主题配置"""
        themes = ["default", "dark_minimal", "light_minimal", "night_sky"]
        
        for theme in themes:
            with self.subTest(theme=theme):
                chart = self.adapter.generate_chart(
                    chart_type="line",
                    data=self.line_data,
                    config={"theme": theme}
                )
                
                self.assertIsNotNone(chart)
                # 主题信息应该在元数据中
                self.assertEqual(chart["metadata"]["theme"], theme)
    
    def test_tools_configuration(self):
        """测试工具配置"""
        custom_tools = "pan,wheel_zoom,box_zoom,reset,save"
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={"tools": custom_tools}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertIn("tools", metadata)
    
    def test_performance_tracking(self):
        """测试性能跟踪"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        # 检查元数据中的性能信息
        metadata = chart["metadata"]
        self.assertIn("performance", metadata)
        
        performance = metadata["performance"]
        self.assertIn("render_time", performance)
        self.assertIn("data_points", performance)
        self.assertIn("memory_usage", performance)
        
        # 检查性能监控器
        recent_renders = self.adapter.performance_monitor.get_recent_renders(limit=1)
        self.assertGreater(len(recent_renders), 0)
    
    def test_data_preprocessing(self):
        """测试数据预处理"""
        # 测试不同格式的数据预处理
        test_cases = [
            # 标准格式
            ([{"x": 1, "y": 10}], "line"),
            # 数组格式（直方图）
            ([1, 2, 3, 4, 5], "histogram"),
            # 字典格式
            ({"x": [1, 2, 3], "y": [10, 20, 30]}, "scatter")
        ]
        
        for data, chart_type in test_cases:
            with self.subTest(data=data, chart_type=chart_type):
                processed = self.adapter._preprocess_data(data, chart_type)
                self.assertIsNotNone(processed)
    
    def test_color_palette_configuration(self):
        """测试颜色调色板配置"""
        custom_colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"]
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={"color_palette": custom_colors}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertIn("color_palette", metadata)
    
    def test_responsive_configuration(self):
        """测试响应式配置"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={
                "responsive": True,
                "sizing_mode": "stretch_width"
            }
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertIn("responsive", metadata)
        self.assertTrue(metadata["responsive"])
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试各种错误情况
        error_cases = [
            # 空数据
            ("line", [], "数据不能为空"),
            # 无效数据格式
            ("line", "invalid_data", "数据格式无效"),
            # 不支持的图表类型
            ("pie", self.line_data, "不支持的图表类型")
        ]
        
        for chart_type, data, expected_error in error_cases:
            with self.subTest(chart_type=chart_type, data=data):
                with self.assertRaises(ValueError) as context:
                    self.adapter.generate_chart(chart_type, data)
                
                self.assertIn(expected_error, str(context.exception))
    
    def test_memory_usage_tracking(self):
        """测试内存使用跟踪"""
        # 生成大量数据的图表
        large_data = [{"x": i, "y": i * 2} for i in range(1000)]
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=large_data
        )
        
        # 检查内存使用信息
        performance = chart["metadata"]["performance"]
        self.assertIn("memory_usage", performance)
        self.assertGreater(performance["memory_usage"], 0)
    
    @patch('time.time')
    def test_render_time_measurement(self, mock_time):
        """测试渲染时间测量"""
        # 模拟时间序列
        mock_time.side_effect = [1000.0, 1000.15]  # 150ms渲染时间
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        # 检查渲染时间
        performance = chart["metadata"]["performance"]
        self.assertAlmostEqual(performance["render_time"], 150.0, places=1)
    
    def test_multi_line_chart(self):
        """测试多线图表"""
        multi_line_data = {
            "x": [1, 2, 3, 4, 5],
            "y1": [10, 20, 15, 25, 30],
            "y2": [5, 15, 10, 20, 25],
            "y3": [15, 25, 20, 30, 35]
        }
        
        chart = self.adapter.generate_chart(
            chart_type="multi_line",
            data=multi_line_data,
            config={"title": "多线图测试"}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "multi_line")
    
    def test_heatmap_chart(self):
        """测试热力图"""
        heatmap_data = [
            {"x": "A", "y": "1", "value": 10},
            {"x": "A", "y": "2", "value": 20},
            {"x": "B", "y": "1", "value": 15},
            {"x": "B", "y": "2", "value": 25}
        ]
        
        chart = self.adapter.generate_chart(
            chart_type="heatmap",
            data=heatmap_data,
            config={"title": "热力图测试"}
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "heatmap")
    
    def test_concurrent_chart_generation(self):
        """测试并发图表生成"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def generate_chart_worker(worker_id):
            try:
                chart = self.adapter.generate_chart(
                    chart_type="line",
                    data=self.line_data
                )
                results.put((worker_id, chart, None))
            except Exception as e:
                results.put((worker_id, None, e))
        
        # 启动多个线程
        threads = []
        num_workers = 3
        
        for i in range(num_workers):
            thread = threading.Thread(target=generate_chart_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        successful_charts = 0
        while not results.empty():
            worker_id, chart, error = results.get()
            if error is None:
                successful_charts += 1
                self.assertIsNotNone(chart)
            else:
                self.fail(f"Worker {worker_id} failed: {error}")
        
        self.assertEqual(successful_charts, num_workers)


class TestBokehAdapterIntegration(unittest.TestCase):
    """Bokeh适配器集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.adapter = BokehAdapter()
    
    def test_complex_scatter_plot(self):
        """测试复杂散点图"""
        complex_data = [
            {"x": i, "y": i**2, "size": i*2, "color": f"C{i%3}"}
            for i in range(1, 21)
        ]
        
        chart = self.adapter.generate_chart(
            chart_type="scatter",
            data=complex_data,
            config={
                "title": "复杂散点图",
                "x_axis_label": "X轴",
                "y_axis_label": "Y轴",
                "size_column": "size",
                "color_column": "color"
            }
        )
        
        self.assertIsNotNone(chart)
        metadata = chart["metadata"]
        self.assertEqual(metadata["chart_type"], "scatter")
        self.assertIn("performance", metadata)
    
    def test_chart_customization(self):
        """测试图表自定义"""
        custom_config = {
            "title": "自定义Bokeh图表",
            "width": 800,
            "height": 600,
            "background_fill_color": "#f5f5f5",
            "border_fill_color": "white",
            "tools": "pan,wheel_zoom,box_zoom,reset,save",
            "x_axis_label": "时间",
            "y_axis_label": "数值"
        }
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=[{"x": i, "y": i*2} for i in range(10)],
            config=custom_config
        )
        
        metadata = chart["metadata"]
        
        # 检查自定义配置
        self.assertEqual(metadata["width"], 800)
        self.assertEqual(metadata["height"], 600)
        self.assertIn("tools", metadata)
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 1. 验证配置
        config = {
            "chart_type": "scatter",
            "data": [{"x": 1, "y": 10}, {"x": 2, "y": 20}],
            "title": "端到端测试"
        }
        
        self.assertTrue(self.adapter.validate_config(config))
        
        # 2. 验证数据
        self.assertTrue(self.adapter.validate_data(config["data"]))
        
        # 3. 生成图表
        chart = self.adapter.generate_chart(
            chart_type=config["chart_type"],
            data=config["data"],
            config=config
        )
        
        self.assertIsNotNone(chart)
        
        # 4. 添加数据
        additional_data = [{"x": 3, "y": 30}]
        updated_chart = self.adapter.add_data_to_chart(chart, additional_data)
        
        # 5. 设置全局选项
        global_options = {"background_fill_color": "#f0f0f0"}
        final_chart = self.adapter.set_global_options(updated_chart, global_options)
        
        # 6. 导出图表
        html_output = self.adapter.export_chart(final_chart, "html")
        json_output = self.adapter.export_chart(final_chart, "json")
        
        # 验证最终结果
        self.assertIsInstance(html_output, str)
        self.assertIsInstance(json_output, str)
        self.assertIn("<!DOCTYPE html>", html_output)
        
        parsed_json = json.loads(json_output)
        self.assertIn("metadata", parsed_json)
    
    def test_performance_comparison(self):
        """测试性能对比"""
        # 生成不同大小的数据集
        small_data = [{"x": i, "y": i} for i in range(100)]
        large_data = [{"x": i, "y": i} for i in range(1000)]
        
        # 测试小数据集
        small_chart = self.adapter.generate_chart(
            chart_type="line",
            data=small_data
        )
        
        # 测试大数据集
        large_chart = self.adapter.generate_chart(
            chart_type="line",
            data=large_data
        )
        
        # 比较性能
        small_perf = small_chart["metadata"]["performance"]
        large_perf = large_chart["metadata"]["performance"]
        
        self.assertLess(small_perf["data_points"], large_perf["data_points"])
        self.assertLessEqual(small_perf["render_time"], large_perf["render_time"])


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)