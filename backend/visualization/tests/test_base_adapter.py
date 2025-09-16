"""BaseVisualizationAdapter基类测试

测试基础适配器的抽象方法和通用功能
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

from backend.visualization.core.base_adapter import BaseVisualizationAdapter
from backend.visualization.utils.performance import PerformanceMonitor, RenderPerformance


class MockVisualizationAdapter(BaseVisualizationAdapter):
    """测试用的具体适配器实现"""
    
    def __init__(self):
        super().__init__()
        self._library_version = "1.0.0"
        self._supported_charts = ["line", "bar", "scatter"]
        self._library_info = {
            "name": "TestLibrary",
            "version": "1.0.0",
            "description": "测试可视化库"
        }
    
    def get_library_version(self) -> str:
        return self._library_version
    
    def get_supported_chart_types(self) -> List[str]:
        return self._supported_charts
    
    def get_library_info(self) -> Dict[str, Any]:
        return self._library_info
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        required_fields = ['chart_type', 'data']
        return all(field in config for field in required_fields)
    
    def validate_data(self, data: Any) -> bool:
        return isinstance(data, (list, dict)) and len(data) > 0
    
    def generate_chart(self, chart_type: str, data: Any, config: Dict[str, Any] = None) -> Any:
        if not self.validate_data(data):
            raise ValueError("无效的数据")
        
        if chart_type not in self._supported_charts:
            raise ValueError(f"不支持的图表类型: {chart_type}")
        
        # 模拟图表生成
        chart_obj = {
            "type": chart_type,
            "data": data,
            "config": config or {},
            "timestamp": time.time()
        }
        
        return chart_obj
    
    def add_data_to_chart(self, chart_obj: Any, data: Any) -> Any:
        if not isinstance(chart_obj, dict):
            raise ValueError("无效的图表对象")
        
        chart_obj["data"] = data
        chart_obj["updated_at"] = time.time()
        return chart_obj
    
    def set_global_options(self, chart_obj: Any, options: Dict[str, Any]) -> Any:
        if not isinstance(chart_obj, dict):
            raise ValueError("无效的图表对象")
        
        chart_obj["global_options"] = options
        return chart_obj
    
    def export_chart(self, chart_obj: Any, format: str = "html", **kwargs) -> str:
        if not isinstance(chart_obj, dict):
            raise ValueError("无效的图表对象")
        
        if format == "html":
            return f"<div>Chart: {chart_obj['type']}</div>"
        elif format == "json":
            return json.dumps(chart_obj)
        else:
            raise ValueError(f"不支持的导出格式: {format}")


class TestBaseVisualizationAdapter(unittest.TestCase):
    """BaseVisualizationAdapter测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.adapter = MockVisualizationAdapter()
        self.test_data = [
            {"x": 1, "y": 10},
            {"x": 2, "y": 20},
            {"x": 3, "y": 15}
        ]
        self.test_config = {
            "chart_type": "line",
            "data": self.test_data,
            "title": "测试图表"
        }
    
    def test_initialization(self):
        """测试适配器初始化"""
        self.assertIsNotNone(self.adapter)
        self.assertIsInstance(self.adapter.performance_monitor, PerformanceMonitor)
        self.assertEqual(self.adapter.get_library_version(), "1.0.0")
        self.assertEqual(self.adapter.get_supported_chart_types(), ["line", "bar", "scatter"])
    
    def test_library_info(self):
        """测试库信息获取"""
        info = self.adapter.get_library_info()
        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertEqual(info["name"], "TestLibrary")
    
    def test_config_validation(self):
        """测试配置验证"""
        # 有效配置
        valid_config = {"chart_type": "line", "data": self.test_data}
        self.assertTrue(self.adapter.validate_config(valid_config))
        
        # 无效配置 - 缺少必需字段
        invalid_config = {"chart_type": "line"}
        self.assertFalse(self.adapter.validate_config(invalid_config))
    
    def test_data_validation(self):
        """测试数据验证"""
        # 有效数据
        self.assertTrue(self.adapter.validate_data(self.test_data))
        self.assertTrue(self.adapter.validate_data({"key": "value"}))
        
        # 无效数据
        self.assertFalse(self.adapter.validate_data([]))
        self.assertFalse(self.adapter.validate_data({}))
        self.assertFalse(self.adapter.validate_data(None))
        self.assertFalse(self.adapter.validate_data("string"))
    
    def test_chart_generation(self):
        """测试图表生成"""
        chart = self.adapter.generate_chart("line", self.test_data, self.test_config)
        
        self.assertIsInstance(chart, dict)
        self.assertEqual(chart["type"], "line")
        self.assertEqual(chart["data"], self.test_data)
        self.assertIn("timestamp", chart)
    
    def test_chart_generation_invalid_type(self):
        """测试不支持的图表类型"""
        with self.assertRaises(ValueError) as context:
            self.adapter.generate_chart("invalid_type", self.test_data)
        
        self.assertIn("不支持的图表类型", str(context.exception))
    
    def test_chart_generation_invalid_data(self):
        """测试无效数据的图表生成"""
        with self.assertRaises(ValueError) as context:
            self.adapter.generate_chart("line", [])
        
        self.assertIn("无效的数据", str(context.exception))
    
    def test_add_data_to_chart(self):
        """测试向图表添加数据"""
        chart = self.adapter.generate_chart("line", self.test_data)
        new_data = [{"x": 4, "y": 25}]
        
        updated_chart = self.adapter.add_data_to_chart(chart, new_data)
        
        self.assertEqual(updated_chart["data"], new_data)
        self.assertIn("updated_at", updated_chart)
    
    def test_set_global_options(self):
        """测试设置全局选项"""
        chart = self.adapter.generate_chart("line", self.test_data)
        options = {"theme": "dark", "animation": True}
        
        updated_chart = self.adapter.set_global_options(chart, options)
        
        self.assertEqual(updated_chart["global_options"], options)
    
    def test_export_chart_html(self):
        """测试HTML格式导出"""
        chart = self.adapter.generate_chart("line", self.test_data)
        html_output = self.adapter.export_chart(chart, "html")
        
        self.assertIsInstance(html_output, str)
        self.assertIn("Chart: line", html_output)
        self.assertIn("<div>", html_output)
    
    def test_export_chart_json(self):
        """测试JSON格式导出"""
        chart = self.adapter.generate_chart("line", self.test_data)
        json_output = self.adapter.export_chart(chart, "json")
        
        self.assertIsInstance(json_output, str)
        parsed_json = json.loads(json_output)
        self.assertEqual(parsed_json["type"], "line")
    
    def test_export_chart_invalid_format(self):
        """测试不支持的导出格式"""
        chart = self.adapter.generate_chart("line", self.test_data)
        
        with self.assertRaises(ValueError) as context:
            self.adapter.export_chart(chart, "invalid_format")
        
        self.assertIn("不支持的导出格式", str(context.exception))
    
    @patch('backend.visualization.core.base_adapter.time.time')
    def test_performance_tracking(self, mock_time):
        """测试性能跟踪"""
        # 模拟时间
        mock_time.side_effect = [1000.0, 1000.1]  # 100ms的渲染时间
        
        # 模拟性能监控器
        mock_monitor = Mock()
        self.adapter.performance_monitor = mock_monitor
        
        # 生成图表
        chart = self.adapter.generate_chart("line", self.test_data)
        
        # 验证性能记录被调用
        self.assertTrue(mock_monitor.record_render_performance.called)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效图表对象的操作
        with self.assertRaises(ValueError):
            self.adapter.add_data_to_chart("invalid_chart", self.test_data)
        
        with self.assertRaises(ValueError):
            self.adapter.set_global_options("invalid_chart", {})
        
        with self.assertRaises(ValueError):
            self.adapter.export_chart("invalid_chart", "html")
    
    def test_performance_metrics_collection(self):
        """测试性能指标收集"""
        # 创建真实的性能监控器
        monitor = PerformanceMonitor()
        self.adapter.performance_monitor = monitor
        
        # 生成多个图表
        for i in range(3):
            chart = self.adapter.generate_chart("line", self.test_data)
            self.adapter.export_chart(chart, "html")
        
        # 检查性能统计
        stats = monitor.get_current_stats()
        self.assertGreaterEqual(stats['total_renders'], 3)
    
    def test_chart_type_support(self):
        """测试图表类型支持"""
        supported_types = self.adapter.get_supported_chart_types()
        
        for chart_type in supported_types:
            chart = self.adapter.generate_chart(chart_type, self.test_data)
            self.assertEqual(chart["type"], chart_type)
    
    def test_config_merging(self):
        """测试配置合并"""
        base_config = {"title": "基础标题"}
        override_config = {"title": "覆盖标题", "theme": "dark"}
        
        chart = self.adapter.generate_chart("line", self.test_data, base_config)
        self.assertEqual(chart["config"]["title"], "基础标题")
        
        chart_with_override = self.adapter.generate_chart("line", self.test_data, override_config)
        self.assertEqual(chart_with_override["config"]["title"], "覆盖标题")
        self.assertEqual(chart_with_override["config"]["theme"], "dark")


class TestPerformanceIntegration(unittest.TestCase):
    """性能监控集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.adapter = TestVisualizationAdapter()
        self.test_data = [{"x": i, "y": i * 2} for i in range(100)]  # 更大的数据集
    
    def test_performance_monitoring_integration(self):
        """测试性能监控集成"""
        monitor = self.adapter.performance_monitor
        
        # 记录初始状态
        initial_stats = monitor.get_current_stats()
        
        # 执行一些操作
        chart = self.adapter.generate_chart("line", self.test_data)
        html_output = self.adapter.export_chart(chart, "html")
        
        # 检查性能统计更新
        final_stats = monitor.get_current_stats()
        self.assertGreaterEqual(final_stats['total_renders'], initial_stats['total_renders'])
    
    def test_memory_usage_tracking(self):
        """测试内存使用跟踪"""
        monitor = self.adapter.performance_monitor
        
        # 生成大量图表以测试内存跟踪
        charts = []
        for i in range(10):
            chart = self.adapter.generate_chart("line", self.test_data)
            charts.append(chart)
        
        # 检查是否有性能记录
        recent_renders = monitor.get_recent_renders(limit=10)
        self.assertGreater(len(recent_renders), 0)
        
        # 检查内存使用记录
        for render in recent_renders:
            self.assertIsInstance(render.memory_usage, int)
            self.assertGreaterEqual(render.memory_usage, 0)


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)