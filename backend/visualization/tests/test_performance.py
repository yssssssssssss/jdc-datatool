"""性能监控模块测试

测试性能监控模块的指标记录、分析和报告功能
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.visualization.utils.performance import (
    PerformanceMetric,
    RenderPerformance,
    PerformanceMonitor,
    performance_timer,
    get_global_monitor,
    set_global_monitor
)


class TestPerformanceMetric(unittest.TestCase):
    """性能指标数据类测试"""
    
    def test_metric_creation(self):
        """测试指标创建"""
        metric = PerformanceMetric(
            operation="test_operation",
            duration=1.5,
            memory_usage=1024,
            data_points=100
        )
        
        self.assertEqual(metric.operation, "test_operation")
        self.assertEqual(metric.duration, 1.5)
        self.assertEqual(metric.memory_usage, 1024)
        self.assertEqual(metric.data_points, 100)
        self.assertIsNotNone(metric.timestamp)
    
    def test_metric_to_dict(self):
        """测试指标转换为字典"""
        metric = PerformanceMetric(
            operation="chart_generation",
            duration=2.0,
            memory_usage=2048,
            data_points=200,
            metadata={"chart_type": "line"}
        )
        
        metric_dict = metric.to_dict()
        
        self.assertIsInstance(metric_dict, dict)
        self.assertEqual(metric_dict["operation"], "chart_generation")
        self.assertEqual(metric_dict["duration"], 2.0)
        self.assertEqual(metric_dict["memory_usage"], 2048)
        self.assertEqual(metric_dict["data_points"], 200)
        self.assertIn("timestamp", metric_dict)
        self.assertIn("metadata", metric_dict)
        self.assertEqual(metric_dict["metadata"]["chart_type"], "line")
    
    def test_metric_from_dict(self):
        """测试从字典创建指标"""
        metric_dict = {
            "operation": "data_processing",
            "duration": 0.5,
            "memory_usage": 512,
            "data_points": 50,
            "timestamp": time.time(),
            "metadata": {"library": "bokeh"}
        }
        
        metric = PerformanceMetric.from_dict(metric_dict)
        
        self.assertEqual(metric.operation, "data_processing")
        self.assertEqual(metric.duration, 0.5)
        self.assertEqual(metric.memory_usage, 512)
        self.assertEqual(metric.data_points, 50)
        self.assertIsNotNone(metric.timestamp)
        self.assertEqual(metric.metadata["library"], "bokeh")


class TestRenderPerformance(unittest.TestCase):
    """渲染性能数据类测试"""
    
    def test_render_performance_creation(self):
        """测试渲染性能创建"""
        render_perf = RenderPerformance(
            chart_type="scatter",
            library="echarts",
            data_points=1000,
            render_time=3.2,
            memory_usage=4096
        )
        
        self.assertEqual(render_perf.chart_type, "scatter")
        self.assertEqual(render_perf.library, "echarts")
        self.assertEqual(render_perf.data_points, 1000)
        self.assertEqual(render_perf.render_time, 3.2)
        self.assertEqual(render_perf.memory_usage, 4096)
        self.assertIsNotNone(render_perf.timestamp)
    
    def test_render_performance_to_dict(self):
        """测试渲染性能转换为字典"""
        render_perf = RenderPerformance(
            chart_type="bar",
            library="bokeh",
            data_points=500,
            render_time=1.8,
            memory_usage=2048,
            config_complexity=0.7
        )
        
        perf_dict = render_perf.to_dict()
        
        self.assertIsInstance(perf_dict, dict)
        self.assertEqual(perf_dict["chart_type"], "bar")
        self.assertEqual(perf_dict["library"], "bokeh")
        self.assertEqual(perf_dict["data_points"], 500)
        self.assertEqual(perf_dict["render_time"], 1.8)
        self.assertEqual(perf_dict["memory_usage"], 2048)
        self.assertEqual(perf_dict["config_complexity"], 0.7)
        self.assertIn("timestamp", perf_dict)
    
    def test_render_performance_from_dict(self):
        """测试从字典创建渲染性能"""
        perf_dict = {
            "chart_type": "line",
            "library": "echarts",
            "data_points": 800,
            "render_time": 2.5,
            "memory_usage": 3072,
            "timestamp": time.time(),
            "config_complexity": 0.5
        }
        
        render_perf = RenderPerformance.from_dict(perf_dict)
        
        self.assertEqual(render_perf.chart_type, "line")
        self.assertEqual(render_perf.library, "echarts")
        self.assertEqual(render_perf.data_points, 800)
        self.assertEqual(render_perf.render_time, 2.5)
        self.assertEqual(render_perf.memory_usage, 3072)
        self.assertEqual(render_perf.config_complexity, 0.5)
        self.assertIsNotNone(render_perf.timestamp)


class TestPerformanceMonitor(unittest.TestCase):
    """性能监控器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.monitor = PerformanceMonitor()
    
    def test_monitor_initialization(self):
        """测试监控器初始化"""
        monitor = PerformanceMonitor()
        
        self.assertIsInstance(monitor.metrics, list)
        self.assertIsInstance(monitor.render_performances, list)
        self.assertEqual(len(monitor.metrics), 0)
        self.assertEqual(len(monitor.render_performances), 0)
        self.assertEqual(monitor.max_metrics, 1000)
    
    def test_monitor_with_custom_settings(self):
        """测试自定义设置的监控器"""
        monitor = PerformanceMonitor(max_metrics=500)
        
        self.assertEqual(monitor.max_metrics, 500)
    
    def test_record_metric(self):
        """测试记录指标"""
        # 记录单个指标
        self.monitor.record_metric(
            operation="test_operation",
            duration=1.0,
            memory_usage=1024,
            data_points=100
        )
        
        self.assertEqual(len(self.monitor.metrics), 1)
        
        metric = self.monitor.metrics[0]
        self.assertEqual(metric.operation, "test_operation")
        self.assertEqual(metric.duration, 1.0)
        self.assertEqual(metric.memory_usage, 1024)
        self.assertEqual(metric.data_points, 100)
    
    def test_record_render_performance(self):
        """测试记录渲染性能"""
        self.monitor.record_render_performance(
            chart_type="line",
            library="echarts",
            data_points=500,
            render_time=2.0,
            memory_usage=2048
        )
        
        self.assertEqual(len(self.monitor.render_performances), 1)
        
        render_perf = self.monitor.render_performances[0]
        self.assertEqual(render_perf.chart_type, "line")
        self.assertEqual(render_perf.library, "echarts")
        self.assertEqual(render_perf.data_points, 500)
        self.assertEqual(render_perf.render_time, 2.0)
        self.assertEqual(render_perf.memory_usage, 2048)
    
    def test_get_recent_metrics(self):
        """测试获取最近指标"""
        # 记录多个指标
        for i in range(5):
            self.monitor.record_metric(
                operation=f"operation_{i}",
                duration=i * 0.5,
                memory_usage=1024 * (i + 1),
                data_points=100 * (i + 1)
            )
            time.sleep(0.01)  # 确保时间戳不同
        
        # 获取最近3个指标
        recent_metrics = self.monitor.get_recent_metrics(limit=3)
        
        self.assertEqual(len(recent_metrics), 3)
        # 应该按时间倒序排列
        self.assertEqual(recent_metrics[0].operation, "operation_4")
        self.assertEqual(recent_metrics[1].operation, "operation_3")
        self.assertEqual(recent_metrics[2].operation, "operation_2")
    
    def test_get_recent_renders(self):
        """测试获取最近渲染性能"""
        # 记录多个渲染性能
        chart_types = ["line", "bar", "scatter"]
        for i, chart_type in enumerate(chart_types):
            self.monitor.record_render_performance(
                chart_type=chart_type,
                library="echarts",
                data_points=100 * (i + 1),
                render_time=(i + 1) * 0.5,
                memory_usage=1024 * (i + 1)
            )
            time.sleep(0.01)
        
        # 获取最近2个渲染性能
        recent_renders = self.monitor.get_recent_renders(limit=2)
        
        self.assertEqual(len(recent_renders), 2)
        self.assertEqual(recent_renders[0].chart_type, "scatter")
        self.assertEqual(recent_renders[1].chart_type, "bar")
    
    def test_get_metrics_by_operation(self):
        """测试按操作获取指标"""
        # 记录不同操作的指标
        operations = ["chart_generation", "data_processing", "chart_generation"]
        for operation in operations:
            self.monitor.record_metric(
                operation=operation,
                duration=1.0,
                memory_usage=1024,
                data_points=100
            )
        
        # 获取特定操作的指标
        chart_metrics = self.monitor.get_metrics_by_operation("chart_generation")
        processing_metrics = self.monitor.get_metrics_by_operation("data_processing")
        
        self.assertEqual(len(chart_metrics), 2)
        self.assertEqual(len(processing_metrics), 1)
        
        for metric in chart_metrics:
            self.assertEqual(metric.operation, "chart_generation")
    
    def test_get_performance_by_chart_type(self):
        """测试按图表类型获取性能"""
        # 记录不同图表类型的性能
        chart_types = ["line", "bar", "line", "scatter"]
        for chart_type in chart_types:
            self.monitor.record_render_performance(
                chart_type=chart_type,
                library="echarts",
                data_points=100,
                render_time=1.0,
                memory_usage=1024
            )
        
        # 获取特定图表类型的性能
        line_performances = self.monitor.get_performance_by_chart_type("line")
        bar_performances = self.monitor.get_performance_by_chart_type("bar")
        
        self.assertEqual(len(line_performances), 2)
        self.assertEqual(len(bar_performances), 1)
        
        for perf in line_performances:
            self.assertEqual(perf.chart_type, "line")
    
    def test_get_performance_by_library(self):
        """测试按库获取性能"""
        # 记录不同库的性能
        libraries = ["echarts", "bokeh", "echarts"]
        for library in libraries:
            self.monitor.record_render_performance(
                chart_type="line",
                library=library,
                data_points=100,
                render_time=1.0,
                memory_usage=1024
            )
        
        # 获取特定库的性能
        echarts_performances = self.monitor.get_performance_by_library("echarts")
        bokeh_performances = self.monitor.get_performance_by_library("bokeh")
        
        self.assertEqual(len(echarts_performances), 2)
        self.assertEqual(len(bokeh_performances), 1)
        
        for perf in echarts_performances:
            self.assertEqual(perf.library, "echarts")
    
    def test_calculate_average_performance(self):
        """测试计算平均性能"""
        # 记录多个性能数据
        render_times = [1.0, 2.0, 3.0]
        memory_usages = [1024, 2048, 3072]
        
        for i, (render_time, memory_usage) in enumerate(zip(render_times, memory_usages)):
            self.monitor.record_render_performance(
                chart_type="line",
                library="echarts",
                data_points=100 * (i + 1),
                render_time=render_time,
                memory_usage=memory_usage
            )
        
        # 计算平均性能
        avg_performance = self.monitor.calculate_average_performance(
            chart_type="line",
            library="echarts"
        )
        
        self.assertIsNotNone(avg_performance)
        self.assertAlmostEqual(avg_performance["avg_render_time"], 2.0, places=2)
        self.assertAlmostEqual(avg_performance["avg_memory_usage"], 2048.0, places=2)
        self.assertAlmostEqual(avg_performance["avg_data_points"], 200.0, places=2)
    
    def test_get_performance_summary(self):
        """测试获取性能摘要"""
        # 记录多种性能数据
        test_data = [
            ("line", "echarts", 100, 1.0, 1024),
            ("line", "bokeh", 150, 1.5, 1536),
            ("bar", "echarts", 200, 2.0, 2048),
            ("scatter", "bokeh", 300, 3.0, 3072)
        ]
        
        for chart_type, library, data_points, render_time, memory_usage in test_data:
            self.monitor.record_render_performance(
                chart_type=chart_type,
                library=library,
                data_points=data_points,
                render_time=render_time,
                memory_usage=memory_usage
            )
        
        # 获取性能摘要
        summary = self.monitor.get_performance_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn("total_renders", summary)
        self.assertIn("avg_render_time", summary)
        self.assertIn("avg_memory_usage", summary)
        self.assertIn("by_chart_type", summary)
        self.assertIn("by_library", summary)
        
        self.assertEqual(summary["total_renders"], 4)
        self.assertAlmostEqual(summary["avg_render_time"], 1.875, places=2)
    
    def test_clear_metrics(self):
        """测试清除指标"""
        # 记录一些指标
        for i in range(3):
            self.monitor.record_metric(
                operation=f"operation_{i}",
                duration=1.0,
                memory_usage=1024,
                data_points=100
            )
        
        self.assertEqual(len(self.monitor.metrics), 3)
        
        # 清除指标
        self.monitor.clear_metrics()
        
        self.assertEqual(len(self.monitor.metrics), 0)
    
    def test_clear_render_performances(self):
        """测试清除渲染性能"""
        # 记录一些渲染性能
        for i in range(3):
            self.monitor.record_render_performance(
                chart_type="line",
                library="echarts",
                data_points=100,
                render_time=1.0,
                memory_usage=1024
            )
        
        self.assertEqual(len(self.monitor.render_performances), 3)
        
        # 清除渲染性能
        self.monitor.clear_render_performances()
        
        self.assertEqual(len(self.monitor.render_performances), 0)
    
    def test_max_metrics_limit(self):
        """测试最大指标限制"""
        # 创建限制为5的监控器
        monitor = PerformanceMonitor(max_metrics=5)
        
        # 记录10个指标
        for i in range(10):
            monitor.record_metric(
                operation=f"operation_{i}",
                duration=1.0,
                memory_usage=1024,
                data_points=100
            )
        
        # 应该只保留最近的5个
        self.assertEqual(len(monitor.metrics), 5)
        
        # 检查保留的是最新的指标
        operations = [metric.operation for metric in monitor.metrics]
        expected_operations = [f"operation_{i}" for i in range(5, 10)]
        self.assertEqual(operations, expected_operations)
    
    def test_export_metrics(self):
        """测试导出指标"""
        # 记录一些指标
        for i in range(3):
            self.monitor.record_metric(
                operation=f"operation_{i}",
                duration=i * 0.5,
                memory_usage=1024 * (i + 1),
                data_points=100 * (i + 1)
            )
        
        # 导出指标
        exported_metrics = self.monitor.export_metrics()
        
        self.assertIsInstance(exported_metrics, list)
        self.assertEqual(len(exported_metrics), 3)
        
        for i, metric_dict in enumerate(exported_metrics):
            self.assertIsInstance(metric_dict, dict)
            self.assertEqual(metric_dict["operation"], f"operation_{i}")
            self.assertIn("timestamp", metric_dict)
    
    def test_import_metrics(self):
        """测试导入指标"""
        # 准备导入数据
        import_data = [
            {
                "operation": "imported_operation_1",
                "duration": 1.5,
                "memory_usage": 1536,
                "data_points": 150,
                "timestamp": time.time()
            },
            {
                "operation": "imported_operation_2",
                "duration": 2.5,
                "memory_usage": 2560,
                "data_points": 250,
                "timestamp": time.time()
            }
        ]
        
        # 导入指标
        self.monitor.import_metrics(import_data)
        
        self.assertEqual(len(self.monitor.metrics), 2)
        
        # 验证导入的指标
        operations = [metric.operation for metric in self.monitor.metrics]
        self.assertIn("imported_operation_1", operations)
        self.assertIn("imported_operation_2", operations)
    
    @patch('psutil.Process')
    def test_get_system_info(self, mock_process):
        """测试获取系统信息"""
        # 模拟psutil.Process
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value = Mock(rss=1024*1024*100)  # 100MB
        mock_process_instance.cpu_percent.return_value = 15.5
        mock_process.return_value = mock_process_instance
        
        system_info = self.monitor.get_system_info()
        
        self.assertIsInstance(system_info, dict)
        self.assertIn("memory_usage_mb", system_info)
        self.assertIn("cpu_percent", system_info)
        self.assertEqual(system_info["memory_usage_mb"], 100.0)
        self.assertEqual(system_info["cpu_percent"], 15.5)
    
    def test_concurrent_metric_recording(self):
        """测试并发指标记录"""
        import threading
        
        def record_metrics_worker(worker_id, num_metrics):
            for i in range(num_metrics):
                self.monitor.record_metric(
                    operation=f"worker_{worker_id}_operation_{i}",
                    duration=1.0,
                    memory_usage=1024,
                    data_points=100
                )
        
        # 启动多个线程
        threads = []
        num_workers = 3
        metrics_per_worker = 5
        
        for worker_id in range(num_workers):
            thread = threading.Thread(
                target=record_metrics_worker,
                args=(worker_id, metrics_per_worker)
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        total_expected_metrics = num_workers * metrics_per_worker
        self.assertEqual(len(self.monitor.metrics), total_expected_metrics)
        
        # 验证所有指标都被记录
        operations = [metric.operation for metric in self.monitor.metrics]
        for worker_id in range(num_workers):
            for i in range(metrics_per_worker):
                expected_operation = f"worker_{worker_id}_operation_{i}"
                self.assertIn(expected_operation, operations)


class TestPerformanceTimer(unittest.TestCase):
    """性能计时器装饰器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.monitor = PerformanceMonitor()
        set_global_monitor(self.monitor)
    
    def test_performance_timer_decorator(self):
        """测试性能计时器装饰器"""
        @performance_timer("test_function")
        def test_function(duration=0.1):
            time.sleep(duration)
            return "test_result"
        
        # 执行被装饰的函数
        result = test_function(duration=0.05)
        
        # 验证函数返回值
        self.assertEqual(result, "test_result")
        
        # 验证性能指标被记录
        self.assertEqual(len(self.monitor.metrics), 1)
        
        metric = self.monitor.metrics[0]
        self.assertEqual(metric.operation, "test_function")
        self.assertGreaterEqual(metric.duration, 50)  # 至少50ms
        self.assertLessEqual(metric.duration, 100)  # 不超过100ms
    
    def test_performance_timer_with_exception(self):
        """测试带异常的性能计时器"""
        @performance_timer("failing_function")
        def failing_function():
            raise ValueError("测试异常")
        
        # 执行会抛出异常的函数
        with self.assertRaises(ValueError):
            failing_function()
        
        # 验证即使有异常，性能指标也被记录
        self.assertEqual(len(self.monitor.metrics), 1)
        
        metric = self.monitor.metrics[0]
        self.assertEqual(metric.operation, "failing_function")
        self.assertGreater(metric.duration, 0)
    
    def test_performance_timer_with_metadata(self):
        """测试带元数据的性能计时器"""
        @performance_timer("function_with_metadata")
        def function_with_metadata(chart_type="line"):
            time.sleep(0.01)
            return {"chart_type": chart_type}
        
        # 执行函数
        result = function_with_metadata(chart_type="scatter")
        
        # 验证结果
        self.assertEqual(result["chart_type"], "scatter")
        
        # 验证性能指标
        self.assertEqual(len(self.monitor.metrics), 1)
        metric = self.monitor.metrics[0]
        self.assertEqual(metric.operation, "function_with_metadata")
    
    def test_nested_performance_timers(self):
        """测试嵌套性能计时器"""
        @performance_timer("outer_function")
        def outer_function():
            time.sleep(0.01)
            return inner_function()
        
        @performance_timer("inner_function")
        def inner_function():
            time.sleep(0.01)
            return "inner_result"
        
        # 执行嵌套函数
        result = outer_function()
        
        # 验证结果
        self.assertEqual(result, "inner_result")
        
        # 验证两个性能指标都被记录
        self.assertEqual(len(self.monitor.metrics), 2)
        
        operations = [metric.operation for metric in self.monitor.metrics]
        self.assertIn("outer_function", operations)
        self.assertIn("inner_function", operations)


class TestGlobalMonitor(unittest.TestCase):
    """全局监控器测试"""
    
    def test_get_global_monitor(self):
        """测试获取全局监控器"""
        monitor = get_global_monitor()
        
        self.assertIsInstance(monitor, PerformanceMonitor)
    
    def test_set_global_monitor(self):
        """测试设置全局监控器"""
        custom_monitor = PerformanceMonitor(max_metrics=100)
        
        set_global_monitor(custom_monitor)
        
        retrieved_monitor = get_global_monitor()
        self.assertEqual(retrieved_monitor.max_metrics, 100)
    
    def test_global_monitor_persistence(self):
        """测试全局监控器持久性"""
        # 获取全局监控器并记录指标
        monitor1 = get_global_monitor()
        monitor1.record_metric(
            operation="test_operation",
            duration=1.0,
            memory_usage=1024,
            data_points=100
        )
        
        # 再次获取全局监控器
        monitor2 = get_global_monitor()
        
        # 应该是同一个实例
        self.assertIs(monitor1, monitor2)
        self.assertEqual(len(monitor2.metrics), 1)


class TestPerformanceIntegration(unittest.TestCase):
    """性能监控集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.monitor = PerformanceMonitor()
    
    def test_complete_performance_workflow(self):
        """测试完整性能监控工作流"""
        # 1. 记录多种类型的性能数据
        test_scenarios = [
            ("line", "echarts", 100, 1.0, 1024),
            ("line", "bokeh", 150, 1.5, 1536),
            ("bar", "echarts", 200, 2.0, 2048),
            ("scatter", "bokeh", 300, 2.5, 3072)
        ]
        
        for chart_type, library, data_points, render_time, memory_usage in test_scenarios:
            self.monitor.record_render_performance(
                chart_type=chart_type,
                library=library,
                data_points=data_points,
                render_time=render_time,
                memory_usage=memory_usage
            )
        
        # 2. 分析性能数据
        summary = self.monitor.get_performance_summary()
        
        # 验证摘要数据
        self.assertEqual(summary["total_renders"], 4)
        self.assertAlmostEqual(summary["avg_render_time"], 1.75, places=2)
        
        # 3. 按图表类型分析
        line_performances = self.monitor.get_performance_by_chart_type("line")
        self.assertEqual(len(line_performances), 2)
        
        # 4. 按库分析
        echarts_performances = self.monitor.get_performance_by_library("echarts")
        bokeh_performances = self.monitor.get_performance_by_library("bokeh")
        
        self.assertEqual(len(echarts_performances), 2)
        self.assertEqual(len(bokeh_performances), 2)
        
        # 5. 计算平均性能
        echarts_avg = self.monitor.calculate_average_performance(
            library="echarts"
        )
        bokeh_avg = self.monitor.calculate_average_performance(
            library="bokeh"
        )
        
        self.assertIsNotNone(echarts_avg)
        self.assertIsNotNone(bokeh_avg)
        
        # 6. 导出和导入数据
        exported_data = self.monitor.export_metrics()
        
        new_monitor = PerformanceMonitor()
        new_monitor.import_metrics(exported_data)
        
        # 验证导入结果
        self.assertEqual(len(new_monitor.metrics), len(exported_data))
    
    def test_performance_comparison_analysis(self):
        """测试性能对比分析"""
        # 记录不同库的相同图表类型性能
        libraries = ["echarts", "bokeh"]
        data_sizes = [100, 500, 1000]
        
        for library in libraries:
            for data_size in data_sizes:
                # 模拟不同库的性能特征
                if library == "echarts":
                    render_time = data_size * 0.001  # ECharts更快
                    memory_usage = data_size * 2
                else:  # bokeh
                    render_time = data_size * 0.002  # Bokeh稍慢
                    memory_usage = data_size * 1.5  # 但内存使用更少
                
                self.monitor.record_render_performance(
                    chart_type="line",
                    library=library,
                    data_points=data_size,
                    render_time=render_time,
                    memory_usage=memory_usage
                )
        
        # 分析性能对比
        echarts_avg = self.monitor.calculate_average_performance(
            chart_type="line",
            library="echarts"
        )
        bokeh_avg = self.monitor.calculate_average_performance(
            chart_type="line",
            library="bokeh"
        )
        
        # 验证性能特征
        self.assertLess(
            echarts_avg["avg_render_time"],
            bokeh_avg["avg_render_time"]
        )
        self.assertGreater(
            echarts_avg["avg_memory_usage"],
            bokeh_avg["avg_memory_usage"]
        )
    
    def test_performance_monitoring_with_timer(self):
        """测试结合计时器的性能监控"""
        # 设置全局监控器
        set_global_monitor(self.monitor)
        
        @performance_timer("chart_generation")
        def generate_chart(chart_type, data_size):
            # 模拟图表生成时间
            time.sleep(data_size * 0.0001)
            return f"{chart_type}_chart_with_{data_size}_points"
        
        # 生成多个图表
        chart_types = ["line", "bar", "scatter"]
        data_sizes = [100, 500, 1000]
        
        for chart_type in chart_types:
            for data_size in data_sizes:
                result = generate_chart(chart_type, data_size)
                self.assertIn(chart_type, result)
                self.assertIn(str(data_size), result)
        
        # 验证性能指标
        total_charts = len(chart_types) * len(data_sizes)
        self.assertEqual(len(self.monitor.metrics), total_charts)
        
        # 分析性能趋势
        chart_metrics = self.monitor.get_metrics_by_operation("chart_generation")
        self.assertEqual(len(chart_metrics), total_charts)
        
        # 验证渲染时间随数据量增加
        durations = [metric.duration for metric in chart_metrics]
        self.assertGreater(max(durations), min(durations))


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)