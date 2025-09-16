"""MultiVisualizationManager多库管理器测试

测试多库管理器的适配器管理、图表生成和性能对比功能
"""

import unittest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.visualization.core.multi_manager import MultiVisualizationManager
from backend.visualization.core.base_adapter import BaseVisualizationAdapter
from backend.visualization.utils.performance import PerformanceMonitor


class MockAdapter(BaseVisualizationAdapter):
    """模拟适配器用于测试"""
    
    def __init__(self, name: str, supported_charts: List[str] = None):
        super().__init__()
        self.name = name
        self._supported_charts = supported_charts or ["line", "bar", "scatter"]
        self._library_version = "1.0.0"
        self._render_time = 100  # 模拟渲染时间（毫秒）
    
    def get_library_version(self) -> str:
        return self._library_version
    
    def get_supported_chart_types(self) -> List[str]:
        return self._supported_charts
    
    def get_library_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self._library_version,
            "description": f"模拟{self.name}可视化库"
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return "chart_type" in config and "data" in config
    
    def validate_data(self, data: Any) -> bool:
        return isinstance(data, (list, dict)) and len(data) > 0
    
    def generate_chart(self, chart_type: str, data: Any, config: Dict[str, Any] = None) -> Any:
        if chart_type not in self._supported_charts:
            raise ValueError(f"不支持的图表类型: {chart_type}")
        
        # 模拟渲染时间
        time.sleep(self._render_time / 1000)
        
        return {
            "library": self.name,
            "type": chart_type,
            "data": data,
            "config": config or {},
            "timestamp": time.time()
        }
    
    def add_data_to_chart(self, chart_obj: Any, data: Any) -> Any:
        chart_obj["data"] = data
        return chart_obj
    
    def set_global_options(self, chart_obj: Any, options: Dict[str, Any]) -> Any:
        chart_obj["global_options"] = options
        return chart_obj
    
    def export_chart(self, chart_obj: Any, format: str = "html", **kwargs) -> str:
        if format == "html":
            return f"<div>{self.name} Chart: {chart_obj['type']}</div>"
        elif format == "json":
            return json.dumps(chart_obj)
        else:
            raise ValueError(f"不支持的导出格式: {format}")


class TestMultiVisualizationManager(unittest.TestCase):
    """MultiVisualizationManager测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.manager = MultiVisualizationManager()
        
        # 创建模拟适配器
        self.echarts_adapter = MockAdapter("ECharts", ["line", "bar", "pie", "scatter"])
        self.bokeh_adapter = MockAdapter("Bokeh", ["line", "scatter", "histogram"])
        self.plotly_adapter = MockAdapter("Plotly", ["line", "bar", "3d_scatter"])
        
        # 注册适配器
        self.manager.register_adapter("echarts", self.echarts_adapter)
        self.manager.register_adapter("bokeh", self.bokeh_adapter)
        self.manager.register_adapter("plotly", self.plotly_adapter)
        
        # 测试数据
        self.test_data = [
            {"x": 1, "y": 10},
            {"x": 2, "y": 20},
            {"x": 3, "y": 15},
            {"x": 4, "y": 25}
        ]
        
        self.test_config = {
            "chart_type": "line",
            "data": self.test_data,
            "title": "测试图表"
        }
    
    def test_initialization(self):
        """测试管理器初始化"""
        manager = MultiVisualizationManager()
        self.assertIsInstance(manager.performance_monitor, PerformanceMonitor)
        self.assertEqual(len(manager.get_available_libraries()), 0)
    
    def test_adapter_registration(self):
        """测试适配器注册"""
        # 检查注册的适配器
        libraries = self.manager.get_available_libraries()
        expected_libraries = ["echarts", "bokeh", "plotly"]
        
        for lib in expected_libraries:
            self.assertIn(lib, libraries)
        
        # 检查适配器信息
        for lib_name in expected_libraries:
            adapter_info = self.manager.get_adapter_info(lib_name)
            self.assertIsNotNone(adapter_info)
            self.assertIn("name", adapter_info)
            self.assertIn("version", adapter_info)
    
    def test_adapter_unregistration(self):
        """测试适配器注销"""
        # 注销一个适配器
        self.manager.unregister_adapter("bokeh")
        
        libraries = self.manager.get_available_libraries()
        self.assertNotIn("bokeh", libraries)
        self.assertIn("echarts", libraries)
        self.assertIn("plotly", libraries)
    
    def test_duplicate_registration(self):
        """测试重复注册适配器"""
        # 尝试重复注册
        new_adapter = MockAdapter("NewECharts")
        
        with self.assertRaises(ValueError) as context:
            self.manager.register_adapter("echarts", new_adapter)
        
        self.assertIn("已存在", str(context.exception))
    
    def test_get_supported_chart_types(self):
        """测试获取支持的图表类型"""
        # 获取所有库支持的图表类型
        all_types = self.manager.get_supported_chart_types()
        expected_types = {"line", "bar", "pie", "scatter", "histogram", "3d_scatter"}
        
        self.assertEqual(set(all_types), expected_types)
        
        # 获取特定库支持的图表类型
        echarts_types = self.manager.get_supported_chart_types("echarts")
        self.assertEqual(set(echarts_types), {"line", "bar", "pie", "scatter"})
    
    def test_get_libraries_for_chart_type(self):
        """测试获取支持特定图表类型的库"""
        # 测试通用图表类型
        line_libraries = self.manager.get_libraries_for_chart_type("line")
        self.assertEqual(set(line_libraries), {"echarts", "bokeh", "plotly"})
        
        # 测试特定库独有的图表类型
        pie_libraries = self.manager.get_libraries_for_chart_type("pie")
        self.assertEqual(set(pie_libraries), {"echarts"})
        
        # 测试不存在的图表类型
        unknown_libraries = self.manager.get_libraries_for_chart_type("unknown")
        self.assertEqual(len(unknown_libraries), 0)
    
    def test_generate_chart_single_library(self):
        """测试单库图表生成"""
        chart = self.manager.generate_chart(
            chart_type="line",
            data=self.test_data,
            library="echarts",
            config=self.test_config
        )
        
        self.assertIsNotNone(chart)
        self.assertEqual(chart["library"], "ECharts")
        self.assertEqual(chart["type"], "line")
        self.assertEqual(chart["data"], self.test_data)
    
    def test_generate_chart_invalid_library(self):
        """测试使用无效库生成图表"""
        with self.assertRaises(ValueError) as context:
            self.manager.generate_chart(
                chart_type="line",
                data=self.test_data,
                library="invalid_library"
            )
        
        self.assertIn("未注册的库", str(context.exception))
    
    def test_generate_chart_unsupported_type(self):
        """测试生成不支持的图表类型"""
        with self.assertRaises(ValueError) as context:
            self.manager.generate_chart(
                chart_type="pie",
                data=self.test_data,
                library="bokeh"  # Bokeh不支持pie图
            )
        
        self.assertIn("不支持的图表类型", str(context.exception))
    
    def test_generate_multi_library_charts(self):
        """测试多库图表生成"""
        results = self.manager.generate_multi_library_charts(
            chart_type="line",
            data=self.test_data,
            libraries=["echarts", "bokeh"],
            config=self.test_config
        )
        
        self.assertEqual(len(results), 2)
        self.assertIn("echarts", results)
        self.assertIn("bokeh", results)
        
        # 检查每个结果
        for lib_name, result in results.items():
            self.assertIn("chart", result)
            self.assertIn("performance", result)
            self.assertIn("success", result)
            self.assertTrue(result["success"])
    
    def test_generate_multi_library_charts_with_error(self):
        """测试多库图表生成时的错误处理"""
        # 使用一个不支持的图表类型
        results = self.manager.generate_multi_library_charts(
            chart_type="pie",
            data=self.test_data,
            libraries=["echarts", "bokeh"],  # bokeh不支持pie
            config=self.test_config
        )
        
        self.assertEqual(len(results), 2)
        
        # ECharts应该成功
        self.assertTrue(results["echarts"]["success"])
        
        # Bokeh应该失败
        self.assertFalse(results["bokeh"]["success"])
        self.assertIn("error", results["bokeh"])
    
    def test_generate_comparison_charts(self):
        """测试生成对比图表"""
        comparison = self.manager.generate_comparison_charts(
            chart_type="line",
            data=self.test_data,
            config=self.test_config
        )
        
        self.assertIn("charts", comparison)
        self.assertIn("performance_comparison", comparison)
        self.assertIn("recommendations", comparison)
        
        # 检查图表数量（应该包含所有支持line图的库）
        charts = comparison["charts"]
        expected_libraries = {"echarts", "bokeh", "plotly"}
        self.assertEqual(set(charts.keys()), expected_libraries)
        
        # 检查性能对比
        perf_comparison = comparison["performance_comparison"]
        self.assertIn("render_times", perf_comparison)
        self.assertIn("memory_usage", perf_comparison)
        self.assertIn("fastest_library", perf_comparison)
    
    def test_export_chart(self):
        """测试图表导出"""
        chart = self.manager.generate_chart(
            chart_type="line",
            data=self.test_data,
            library="echarts"
        )
        
        # 导出为HTML
        html_output = self.manager.export_chart(chart, "echarts", "html")
        self.assertIsInstance(html_output, str)
        self.assertIn("ECharts Chart", html_output)
        
        # 导出为JSON
        json_output = self.manager.export_chart(chart, "echarts", "json")
        self.assertIsInstance(json_output, str)
        parsed_json = json.loads(json_output)
        self.assertEqual(parsed_json["type"], "line")
    
    def test_performance_caching(self):
        """测试性能缓存"""
        # 生成相同的图表多次
        for _ in range(3):
            self.manager.generate_chart(
                chart_type="line",
                data=self.test_data,
                library="echarts"
            )
        
        # 检查性能统计
        stats = self.manager.get_performance_stats()
        self.assertIn("total_renders", stats)
        self.assertGreaterEqual(stats["total_renders"], 3)
    
    def test_get_performance_stats(self):
        """测试获取性能统计"""
        # 生成一些图表
        self.manager.generate_chart("line", self.test_data, "echarts")
        self.manager.generate_chart("bar", self.test_data, "echarts")
        self.manager.generate_chart("line", self.test_data, "bokeh")
        
        stats = self.manager.get_performance_stats()
        
        self.assertIn("total_renders", stats)
        self.assertIn("by_library", stats)
        self.assertIn("by_chart_type", stats)
        
        # 检查按库分组的统计
        by_library = stats["by_library"]
        self.assertIn("echarts", by_library)
        self.assertIn("bokeh", by_library)
        
        # 检查按图表类型分组的统计
        by_type = stats["by_chart_type"]
        self.assertIn("line", by_type)
        self.assertIn("bar", by_type)
    
    def test_generate_recommendations(self):
        """测试生成推荐"""
        # 生成一些性能数据
        self.manager.generate_comparison_charts("line", self.test_data)
        
        recommendations = self.manager.generate_recommendations(
            chart_type="line",
            data_size=len(self.test_data),
            priority="performance"
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # 检查推荐结构
        for rec in recommendations:
            self.assertIn("library", rec)
            self.assertIn("score", rec)
            self.assertIn("reasons", rec)
    
    def test_clear_cache(self):
        """测试清除缓存"""
        # 生成一些图表
        self.manager.generate_chart("line", self.test_data, "echarts")
        
        # 检查有性能数据
        stats_before = self.manager.get_performance_stats()
        self.assertGreater(stats_before["total_renders"], 0)
        
        # 清除缓存
        self.manager.clear_cache()
        
        # 检查缓存已清除
        stats_after = self.manager.get_performance_stats()
        self.assertEqual(stats_after["total_renders"], 0)
    
    @patch('time.time')
    def test_performance_tracking(self, mock_time):
        """测试性能跟踪"""
        # 模拟时间序列
        mock_time.side_effect = [1000.0, 1000.1, 1000.2, 1000.3]
        
        chart = self.manager.generate_chart(
            chart_type="line",
            data=self.test_data,
            library="echarts"
        )
        
        # 检查性能监控器是否记录了数据
        monitor = self.manager.performance_monitor
        recent_renders = monitor.get_recent_renders(limit=1)
        
        self.assertGreater(len(recent_renders), 0)
        render_data = recent_renders[-1]
        self.assertEqual(render_data.library, "ECharts")
        self.assertEqual(render_data.chart_type, "line")
    
    def test_concurrent_chart_generation(self):
        """测试并发图表生成"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def generate_chart_worker(library):
            try:
                chart = self.manager.generate_chart(
                    chart_type="line",
                    data=self.test_data,
                    library=library
                )
                results.put((library, chart, None))
            except Exception as e:
                results.put((library, None, e))
        
        # 启动多个线程
        threads = []
        libraries = ["echarts", "bokeh", "plotly"]
        
        for lib in libraries:
            thread = threading.Thread(target=generate_chart_worker, args=(lib,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        generated_charts = {}
        while not results.empty():
            lib, chart, error = results.get()
            if error is None:
                generated_charts[lib] = chart
            else:
                self.fail(f"图表生成失败 {lib}: {error}")
        
        self.assertEqual(len(generated_charts), len(libraries))


class TestMultiManagerIntegration(unittest.TestCase):
    """多库管理器集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.manager = MultiVisualizationManager()
        
        # 注册多个适配器
        adapters = {
            "fast_lib": MockAdapter("FastLib", ["line", "bar"]),
            "slow_lib": MockAdapter("SlowLib", ["line", "scatter"]),
            "memory_lib": MockAdapter("MemoryLib", ["line", "pie"])
        }
        
        # 设置不同的性能特征
        adapters["fast_lib"]._render_time = 50  # 快速渲染
        adapters["slow_lib"]._render_time = 200  # 慢速渲染
        adapters["memory_lib"]._render_time = 100  # 中等渲染
        
        for name, adapter in adapters.items():
            self.manager.register_adapter(name, adapter)
        
        self.test_data = [{"x": i, "y": i * 2} for i in range(50)]
    
    def test_performance_based_recommendations(self):
        """测试基于性能的推荐"""
        # 生成对比数据
        comparison = self.manager.generate_comparison_charts(
            chart_type="line",
            data=self.test_data
        )
        
        # 获取性能推荐
        recommendations = self.manager.generate_recommendations(
            chart_type="line",
            data_size=len(self.test_data),
            priority="performance"
        )
        
        # 验证推荐结果
        self.assertGreater(len(recommendations), 0)
        
        # 最快的库应该排在前面
        fastest_rec = recommendations[0]
        self.assertEqual(fastest_rec["library"], "fast_lib")
    
    def test_library_capability_analysis(self):
        """测试库能力分析"""
        # 分析各库的能力
        capabilities = {}
        
        for lib in self.manager.get_available_libraries():
            capabilities[lib] = {
                "supported_types": self.manager.get_supported_chart_types(lib),
                "info": self.manager.get_adapter_info(lib)
            }
        
        # 验证能力分析结果
        self.assertEqual(len(capabilities), 3)
        
        for lib, cap in capabilities.items():
            self.assertIn("supported_types", cap)
            self.assertIn("info", cap)
            self.assertGreater(len(cap["supported_types"]), 0)
    
    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 1. 查询可用库
        libraries = self.manager.get_available_libraries()
        self.assertGreater(len(libraries), 0)
        
        # 2. 查询支持特定图表类型的库
        line_libraries = self.manager.get_libraries_for_chart_type("line")
        self.assertGreater(len(line_libraries), 0)
        
        # 3. 生成多库对比图表
        comparison = self.manager.generate_comparison_charts(
            chart_type="line",
            data=self.test_data
        )
        
        self.assertIn("charts", comparison)
        self.assertIn("performance_comparison", comparison)
        
        # 4. 获取推荐
        recommendations = self.manager.generate_recommendations(
            chart_type="line",
            data_size=len(self.test_data)
        )
        
        self.assertGreater(len(recommendations), 0)
        
        # 5. 使用推荐的库生成最终图表
        best_library = recommendations[0]["library"]
        final_chart = self.manager.generate_chart(
            chart_type="line",
            data=self.test_data,
            library=best_library
        )
        
        self.assertIsNotNone(final_chart)
        
        # 6. 导出图表
        exported = self.manager.export_chart(final_chart, best_library, "html")
        self.assertIsInstance(exported, str)
        self.assertGreater(len(exported), 0)


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)