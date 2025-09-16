"""ECharts适配器测试

测试ECharts适配器的图表生成、配置验证和导出功能
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

from backend.visualization.adapters.echarts_adapter import EChartsAdapter
from backend.visualization.utils.performance import PerformanceMonitor


class TestEChartsAdapter(unittest.TestCase):
    """ECharts适配器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.adapter = EChartsAdapter()
        
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
            [10, 20, 5],
            [15, 25, 8],
            [20, 30, 12],
            [25, 35, 15]
        ]
    
    def test_initialization(self):
        """测试适配器初始化"""
        adapter = EChartsAdapter()
        
        # 检查基本属性
        self.assertIsNotNone(adapter.performance_monitor)
        self.assertIsInstance(adapter.performance_monitor, PerformanceMonitor)
        
        # 检查默认配置
        self.assertIsNotNone(adapter.default_config)
        self.assertIn("animation", adapter.default_config)
        self.assertIn("responsive", adapter.default_config)
    
    def test_get_library_version(self):
        """测试获取库版本"""
        version = self.adapter.get_library_version()
        self.assertIsInstance(version, str)
        self.assertGreater(len(version), 0)
    
    def test_get_supported_chart_types(self):
        """测试获取支持的图表类型"""
        chart_types = self.adapter.get_supported_chart_types()
        
        expected_types = [
            "line", "bar", "pie", "scatter", "area", "radar",
            "funnel", "gauge", "candlestick", "heatmap", "treemap",
            "sunburst", "parallel", "sankey", "graph", "boxplot"
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
        
        self.assertEqual(info["name"], "Apache ECharts")
        self.assertIsInstance(info["features"], list)
    
    def test_validate_config_valid(self):
        """测试有效配置验证"""
        valid_configs = [
            {"chart_type": "line", "data": self.line_data},
            {"chart_type": "bar", "data": self.test_data, "title": "测试图表"},
            {"chart_type": "pie", "data": self.test_data, "legend": True}
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
            [{"x": 1, "y": 2}],  # 单个数据点
            {"series1": [1, 2, 3], "series2": [4, 5, 6]}  # 字典格式
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
            123,
            [None, None]
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
        self.assertIn("option", chart)
        self.assertIn("metadata", chart)
        
        option = chart["option"]
        self.assertIn("series", option)
        self.assertIn("xAxis", option)
        self.assertIn("yAxis", option)
        self.assertIn("title", option)
        
        # 检查系列数据
        series = option["series"][0]
        self.assertEqual(series["type"], "line")
        self.assertIn("data", series)
    
    def test_generate_bar_chart(self):
        """测试生成柱状图"""
        chart = self.adapter.generate_chart(
            chart_type="bar",
            data=self.test_data,
            config={"title": "柱状图测试"}
        )
        
        self.assertIsNotNone(chart)
        option = chart["option"]
        
        # 检查系列类型
        series = option["series"][0]
        self.assertEqual(series["type"], "bar")
        
        # 检查数据格式
        self.assertIn("data", series)
        self.assertEqual(len(series["data"]), len(self.test_data))
    
    def test_generate_pie_chart(self):
        """测试生成饼图"""
        chart = self.adapter.generate_chart(
            chart_type="pie",
            data=self.test_data,
            config={"title": "饼图测试"}
        )
        
        self.assertIsNotNone(chart)
        option = chart["option"]
        
        # 检查系列类型
        series = option["series"][0]
        self.assertEqual(series["type"], "pie")
        
        # 饼图应该有半径设置
        self.assertIn("radius", series)
    
    def test_generate_scatter_chart(self):
        """测试生成散点图"""
        chart = self.adapter.generate_chart(
            chart_type="scatter",
            data=self.scatter_data,
            config={"title": "散点图测试"}
        )
        
        self.assertIsNotNone(chart)
        option = chart["option"]
        
        # 检查系列类型
        series = option["series"][0]
        self.assertEqual(series["type"], "scatter")
    
    def test_generate_unsupported_chart(self):
        """测试生成不支持的图表类型"""
        with self.assertRaises(ValueError) as context:
            self.adapter.generate_chart(
                chart_type="unsupported_type",
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
        
        # 检查数据是否已添加
        series_data = updated_chart["option"]["series"][0]["data"]
        self.assertEqual(len(series_data), len(self.line_data) + len(new_data))
    
    def test_set_global_options(self):
        """测试设置全局选项"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        global_options = {
            "backgroundColor": "#f0f0f0",
            "animation": False,
            "grid": {"left": "10%", "right": "10%"}
        }
        
        updated_chart = self.adapter.set_global_options(chart, global_options)
        option = updated_chart["option"]
        
        # 检查全局选项是否已设置
        self.assertEqual(option["backgroundColor"], "#f0f0f0")
        self.assertEqual(option["animation"], False)
        self.assertIn("grid", option)
    
    def test_export_chart_html(self):
        """测试导出HTML格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        html_output = self.adapter.export_chart(chart, "html")
        
        self.assertIsInstance(html_output, str)
        self.assertIn("<!DOCTYPE html>", html_output)
        self.assertIn("echarts", html_output.lower())
        self.assertIn("<script>", html_output)
    
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
        self.assertIn("option", parsed_json)
        self.assertIn("metadata", parsed_json)
    
    def test_export_chart_config(self):
        """测试导出配置格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        config_output = self.adapter.export_chart(chart, "config")
        
        self.assertIsInstance(config_output, str)
        
        # 验证配置格式
        parsed_config = json.loads(config_output)
        self.assertIn("series", parsed_config)
        self.assertIn("xAxis", parsed_config)
        self.assertIn("yAxis", parsed_config)
    
    def test_export_chart_unsupported_format(self):
        """测试导出不支持的格式"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        with self.assertRaises(ValueError) as context:
            self.adapter.export_chart(chart, "unsupported_format")
        
        self.assertIn("不支持的导出格式", str(context.exception))
    
    def test_performance_tracking(self):
        """测试性能跟踪"""
        # 生成图表并检查性能跟踪
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
            # 数组格式
            ([[1, 10], [2, 20]], "scatter"),
            # 命名值格式
            ([{"name": "A", "value": 10}], "bar")
        ]
        
        for data, chart_type in test_cases:
            with self.subTest(data=data, chart_type=chart_type):
                processed = self.adapter._preprocess_data(data, chart_type)
                self.assertIsNotNone(processed)
                self.assertIsInstance(processed, list)
    
    def test_theme_support(self):
        """测试主题支持"""
        themes = ["default", "dark", "light"]
        
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
    
    def test_responsive_configuration(self):
        """测试响应式配置"""
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={"responsive": True}
        )
        
        option = chart["option"]
        
        # 响应式图表应该有媒体查询配置
        self.assertIn("media", option)
        self.assertIsInstance(option["media"], list)
    
    def test_animation_configuration(self):
        """测试动画配置"""
        # 启用动画
        chart_with_animation = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={"animation": True}
        )
        
        self.assertTrue(chart_with_animation["option"]["animation"])
        
        # 禁用动画
        chart_without_animation = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data,
            config={"animation": False}
        )
        
        self.assertFalse(chart_without_animation["option"]["animation"])
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试各种错误情况
        error_cases = [
            # 空数据
            ("line", [], "数据不能为空"),
            # 无效数据格式
            ("line", "invalid_data", "数据格式无效"),
            # 不支持的图表类型
            ("invalid_type", self.line_data, "不支持的图表类型")
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
        mock_time.side_effect = [1000.0, 1000.1]  # 100ms渲染时间
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=self.line_data
        )
        
        # 检查渲染时间
        performance = chart["metadata"]["performance"]
        self.assertAlmostEqual(performance["render_time"], 100.0, places=1)
    
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
        num_workers = 5
        
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


class TestEChartsAdapterIntegration(unittest.TestCase):
    """ECharts适配器集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.adapter = EChartsAdapter()
    
    def test_complex_chart_generation(self):
        """测试复杂图表生成"""
        # 多系列数据
        multi_series_data = {
            "categories": ["Jan", "Feb", "Mar", "Apr", "May"],
            "series": [
                {"name": "Sales", "data": [100, 200, 150, 300, 250]},
                {"name": "Profit", "data": [50, 100, 75, 150, 125]}
            ]
        }
        
        chart = self.adapter.generate_chart(
            chart_type="line",
            data=multi_series_data,
            config={
                "title": "销售与利润对比",
                "legend": True,
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True}
            }
        )
        
        self.assertIsNotNone(chart)
        option = chart["option"]
        
        # 检查多系列
        self.assertEqual(len(option["series"]), 2)
        self.assertIn("legend", option)
    
    def test_chart_customization(self):
        """测试图表自定义"""
        custom_config = {
            "title": "自定义图表",
            "color": ["#ff6b6b", "#4ecdc4", "#45b7d1"],
            "grid": {
                "left": "10%",
                "right": "10%",
                "top": "15%",
                "bottom": "15%"
            },
            "xAxis": {
                "axisLabel": {"rotate": 45}
            },
            "yAxis": {
                "axisLabel": {"formatter": "{value}%"}
            }
        }
        
        chart = self.adapter.generate_chart(
            chart_type="bar",
            data=[{"name": "A", "value": 10}, {"name": "B", "value": 20}],
            config=custom_config
        )
        
        option = chart["option"]
        
        # 检查自定义配置
        self.assertEqual(option["color"], custom_config["color"])
        self.assertEqual(option["grid"], custom_config["grid"])
        self.assertEqual(option["xAxis"]["axisLabel"]["rotate"], 45)
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 1. 验证配置
        config = {
            "chart_type": "line",
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
        global_options = {"backgroundColor": "#f5f5f5"}
        final_chart = self.adapter.set_global_options(updated_chart, global_options)
        
        # 6. 导出图表
        html_output = self.adapter.export_chart(final_chart, "html")
        json_output = self.adapter.export_chart(final_chart, "json")
        
        # 验证最终结果
        self.assertIsInstance(html_output, str)
        self.assertIsInstance(json_output, str)
        self.assertIn("<!DOCTYPE html>", html_output)
        
        parsed_json = json.loads(json_output)
        self.assertIn("option", parsed_json)


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)