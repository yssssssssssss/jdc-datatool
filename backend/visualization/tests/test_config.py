"""配置管理模块测试

测试配置管理模块的配置加载、验证、更新和保存功能
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from typing import Dict, Any
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.visualization.utils.config import (
    VisualizationConfig,
    ConfigManager,
    DEFAULT_CONFIG
)


class TestVisualizationConfig(unittest.TestCase):
    """可视化配置数据类测试"""
    
    def test_default_config_creation(self):
        """测试默认配置创建"""
        config = VisualizationConfig()
        
        # 检查默认值
        self.assertEqual(config.default_width, 800)
        self.assertEqual(config.default_height, 600)
        self.assertEqual(config.default_theme, "default")
        self.assertIsInstance(config.color_palettes, dict)
        self.assertIsInstance(config.performance_settings, dict)
        self.assertIsInstance(config.export_settings, dict)
        self.assertIsInstance(config.library_settings, dict)
    
    def test_custom_config_creation(self):
        """测试自定义配置创建"""
        custom_palettes = {
            "custom": ["#ff0000", "#00ff00", "#0000ff"]
        }
        
        config = VisualizationConfig(
            default_width=1000,
            default_height=800,
            default_theme="dark",
            color_palettes=custom_palettes
        )
        
        self.assertEqual(config.default_width, 1000)
        self.assertEqual(config.default_height, 800)
        self.assertEqual(config.default_theme, "dark")
        self.assertEqual(config.color_palettes, custom_palettes)
    
    def test_config_to_dict(self):
        """测试配置转换为字典"""
        config = VisualizationConfig(
            default_width=900,
            default_height=700
        )
        
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["default_width"], 900)
        self.assertEqual(config_dict["default_height"], 700)
        self.assertIn("color_palettes", config_dict)
        self.assertIn("performance_settings", config_dict)
    
    def test_config_from_dict(self):
        """测试从字典创建配置"""
        config_dict = {
            "default_width": 1200,
            "default_height": 900,
            "default_theme": "light",
            "color_palettes": {
                "test": ["#123456", "#789abc"]
            }
        }
        
        config = VisualizationConfig.from_dict(config_dict)
        
        self.assertEqual(config.default_width, 1200)
        self.assertEqual(config.default_height, 900)
        self.assertEqual(config.default_theme, "light")
        self.assertIn("test", config.color_palettes)
    
    def test_config_validation(self):
        """测试配置验证"""
        # 有效配置
        valid_config = VisualizationConfig(
            default_width=800,
            default_height=600
        )
        self.assertTrue(valid_config.validate())
        
        # 无效宽度
        invalid_width_config = VisualizationConfig(
            default_width=0,
            default_height=600
        )
        self.assertFalse(invalid_width_config.validate())
        
        # 无效高度
        invalid_height_config = VisualizationConfig(
            default_width=800,
            default_height=-100
        )
        self.assertFalse(invalid_height_config.validate())
    
    def test_config_merge(self):
        """测试配置合并"""
        base_config = VisualizationConfig(
            default_width=800,
            default_height=600,
            color_palettes={"base": ["#000000"]}
        )
        
        override_config = VisualizationConfig(
            default_width=1000,
            color_palettes={"override": ["#ffffff"]}
        )
        
        merged_config = base_config.merge(override_config)
        
        # 检查合并结果
        self.assertEqual(merged_config.default_width, 1000)  # 被覆盖
        self.assertEqual(merged_config.default_height, 600)  # 保持原值
        self.assertIn("base", merged_config.color_palettes)  # 保留原有
        self.assertIn("override", merged_config.color_palettes)  # 添加新的


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.manager = ConfigManager(config_file=self.config_file)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        manager = ConfigManager()
        
        self.assertIsNotNone(manager.config)
        self.assertIsInstance(manager.config, VisualizationConfig)
        self.assertIsNotNone(manager.config_file)
    
    def test_load_default_config(self):
        """测试加载默认配置"""
        # 配置文件不存在时应该加载默认配置
        config = self.manager.load_config()
        
        self.assertIsInstance(config, VisualizationConfig)
        self.assertEqual(config.default_width, DEFAULT_CONFIG["default_width"])
        self.assertEqual(config.default_height, DEFAULT_CONFIG["default_height"])
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        # 创建自定义配置
        custom_config = VisualizationConfig(
            default_width=1000,
            default_height=800,
            default_theme="dark"
        )
        
        # 保存配置
        self.manager.config = custom_config
        self.manager.save_config()
        
        # 验证文件存在
        self.assertTrue(os.path.exists(self.config_file))
        
        # 创建新管理器并加载配置
        new_manager = ConfigManager(config_file=self.config_file)
        loaded_config = new_manager.load_config()
        
        # 验证加载的配置
        self.assertEqual(loaded_config.default_width, 1000)
        self.assertEqual(loaded_config.default_height, 800)
        self.assertEqual(loaded_config.default_theme, "dark")
    
    def test_update_config(self):
        """测试更新配置"""
        # 初始配置
        initial_width = self.manager.config.default_width
        
        # 更新配置
        updates = {
            "default_width": 1200,
            "default_theme": "custom"
        }
        
        self.manager.update_config(updates)
        
        # 验证更新
        self.assertEqual(self.manager.config.default_width, 1200)
        self.assertEqual(self.manager.config.default_theme, "custom")
        self.assertNotEqual(self.manager.config.default_width, initial_width)
    
    def test_get_config_value(self):
        """测试获取配置值"""
        # 获取存在的配置值
        width = self.manager.get_config_value("default_width")
        self.assertEqual(width, self.manager.config.default_width)
        
        # 获取嵌套配置值
        performance_cache = self.manager.get_config_value(
            "performance_settings.enable_cache"
        )
        self.assertIsInstance(performance_cache, bool)
        
        # 获取不存在的配置值（使用默认值）
        non_existent = self.manager.get_config_value(
            "non_existent_key", 
            default="default_value"
        )
        self.assertEqual(non_existent, "default_value")
    
    def test_set_config_value(self):
        """测试设置配置值"""
        # 设置简单配置值
        self.manager.set_config_value("default_width", 1500)
        self.assertEqual(self.manager.config.default_width, 1500)
        
        # 设置嵌套配置值
        self.manager.set_config_value(
            "performance_settings.cache_size", 
            2000
        )
        self.assertEqual(
            self.manager.config.performance_settings["cache_size"], 
            2000
        )
    
    def test_validate_config(self):
        """测试配置验证"""
        # 有效配置
        self.assertTrue(self.manager.validate_config())
        
        # 设置无效配置
        self.manager.config.default_width = -100
        self.assertFalse(self.manager.validate_config())
        
        # 恢复有效配置
        self.manager.config.default_width = 800
        self.assertTrue(self.manager.validate_config())
    
    def test_reset_to_default(self):
        """测试重置为默认配置"""
        # 修改配置
        self.manager.config.default_width = 1500
        self.manager.config.default_theme = "custom"
        
        # 重置为默认
        self.manager.reset_to_default()
        
        # 验证重置结果
        self.assertEqual(
            self.manager.config.default_width, 
            DEFAULT_CONFIG["default_width"]
        )
        self.assertEqual(
            self.manager.config.default_theme, 
            DEFAULT_CONFIG["default_theme"]
        )
    
    def test_get_library_config(self):
        """测试获取库配置"""
        # 获取ECharts配置
        echarts_config = self.manager.get_library_config("echarts")
        self.assertIsInstance(echarts_config, dict)
        
        # 获取Bokeh配置
        bokeh_config = self.manager.get_library_config("bokeh")
        self.assertIsInstance(bokeh_config, dict)
        
        # 获取不存在的库配置
        unknown_config = self.manager.get_library_config("unknown")
        self.assertEqual(unknown_config, {})
    
    def test_update_library_config(self):
        """测试更新库配置"""
        # 更新ECharts配置
        echarts_updates = {
            "animation": False,
            "responsive": True
        }
        
        self.manager.update_library_config("echarts", echarts_updates)
        
        # 验证更新
        echarts_config = self.manager.get_library_config("echarts")
        self.assertFalse(echarts_config["animation"])
        self.assertTrue(echarts_config["responsive"])
    
    def test_get_color_palette(self):
        """测试获取颜色调色板"""
        # 获取默认调色板
        default_palette = self.manager.get_color_palette("default")
        self.assertIsInstance(default_palette, list)
        self.assertGreater(len(default_palette), 0)
        
        # 获取不存在的调色板（返回默认）
        unknown_palette = self.manager.get_color_palette("unknown")
        self.assertEqual(unknown_palette, default_palette)
    
    def test_add_color_palette(self):
        """测试添加颜色调色板"""
        custom_palette = ["#ff0000", "#00ff00", "#0000ff"]
        
        self.manager.add_color_palette("custom", custom_palette)
        
        # 验证添加结果
        retrieved_palette = self.manager.get_color_palette("custom")
        self.assertEqual(retrieved_palette, custom_palette)
    
    def test_export_config(self):
        """测试导出配置"""
        exported_config = self.manager.export_config()
        
        self.assertIsInstance(exported_config, dict)
        self.assertIn("default_width", exported_config)
        self.assertIn("default_height", exported_config)
        self.assertIn("color_palettes", exported_config)
        self.assertIn("library_settings", exported_config)
    
    def test_import_config(self):
        """测试导入配置"""
        # 准备导入配置
        import_config = {
            "default_width": 1600,
            "default_height": 1200,
            "default_theme": "imported",
            "color_palettes": {
                "imported": ["#123456", "#789abc"]
            }
        }
        
        # 导入配置
        self.manager.import_config(import_config)
        
        # 验证导入结果
        self.assertEqual(self.manager.config.default_width, 1600)
        self.assertEqual(self.manager.config.default_height, 1200)
        self.assertEqual(self.manager.config.default_theme, "imported")
        self.assertIn("imported", self.manager.config.color_palettes)
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"invalid": "json"}')
    def test_load_invalid_json(self, mock_file):
        """测试加载无效JSON配置"""
        with patch('os.path.exists', return_value=True):
            # 应该回退到默认配置
            config = self.manager.load_config()
            self.assertIsInstance(config, VisualizationConfig)
    
    @patch('builtins.open', side_effect=IOError("文件读取错误"))
    def test_load_config_io_error(self, mock_file):
        """测试配置文件读取错误"""
        with patch('os.path.exists', return_value=True):
            # 应该回退到默认配置
            config = self.manager.load_config()
            self.assertIsInstance(config, VisualizationConfig)
    
    @patch('builtins.open', side_effect=IOError("文件写入错误"))
    def test_save_config_io_error(self, mock_file):
        """测试配置文件写入错误"""
        # 应该抛出异常
        with self.assertRaises(IOError):
            self.manager.save_config()
    
    def test_config_backup_and_restore(self):
        """测试配置备份和恢复"""
        # 修改配置
        original_width = self.manager.config.default_width
        self.manager.config.default_width = 1800
        
        # 创建备份
        backup = self.manager.create_backup()
        
        # 进一步修改配置
        self.manager.config.default_width = 2000
        
        # 恢复备份
        self.manager.restore_backup(backup)
        
        # 验证恢复结果
        self.assertEqual(self.manager.config.default_width, 1800)
    
    def test_config_versioning(self):
        """测试配置版本控制"""
        # 检查配置版本
        version = self.manager.get_config_version()
        self.assertIsInstance(version, str)
        
        # 更新配置版本
        new_version = "2.0.0"
        self.manager.set_config_version(new_version)
        
        # 验证版本更新
        updated_version = self.manager.get_config_version()
        self.assertEqual(updated_version, new_version)
    
    def test_config_migration(self):
        """测试配置迁移"""
        # 模拟旧版本配置
        old_config = {
            "width": 800,  # 旧字段名
            "height": 600,  # 旧字段名
            "theme": "default"
        }
        
        # 执行迁移
        migrated_config = self.manager.migrate_config(old_config, "1.0.0")
        
        # 验证迁移结果
        self.assertIn("default_width", migrated_config)
        self.assertIn("default_height", migrated_config)
        self.assertEqual(migrated_config["default_width"], 800)
        self.assertEqual(migrated_config["default_height"], 600)


class TestConfigIntegration(unittest.TestCase):
    """配置管理集成测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "integration_config.json")
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
    
    def test_complete_config_workflow(self):
        """测试完整配置工作流"""
        # 1. 创建配置管理器
        manager = ConfigManager(config_file=self.config_file)
        
        # 2. 加载默认配置
        config = manager.load_config()
        self.assertIsInstance(config, VisualizationConfig)
        
        # 3. 更新配置
        updates = {
            "default_width": 1200,
            "default_height": 900,
            "default_theme": "dark"
        }
        manager.update_config(updates)
        
        # 4. 添加自定义调色板
        custom_palette = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
        manager.add_color_palette("custom", custom_palette)
        
        # 5. 更新库配置
        echarts_config = {
            "animation": True,
            "responsive": True,
            "theme": "dark"
        }
        manager.update_library_config("echarts", echarts_config)
        
        # 6. 保存配置
        manager.save_config()
        
        # 7. 验证配置文件存在
        self.assertTrue(os.path.exists(self.config_file))
        
        # 8. 创建新管理器并加载配置
        new_manager = ConfigManager(config_file=self.config_file)
        loaded_config = new_manager.load_config()
        
        # 9. 验证所有配置都正确加载
        self.assertEqual(loaded_config.default_width, 1200)
        self.assertEqual(loaded_config.default_height, 900)
        self.assertEqual(loaded_config.default_theme, "dark")
        
        # 验证自定义调色板
        loaded_palette = new_manager.get_color_palette("custom")
        self.assertEqual(loaded_palette, custom_palette)
        
        # 验证库配置
        loaded_echarts_config = new_manager.get_library_config("echarts")
        self.assertTrue(loaded_echarts_config["animation"])
        self.assertTrue(loaded_echarts_config["responsive"])
        self.assertEqual(loaded_echarts_config["theme"], "dark")
    
    def test_config_validation_workflow(self):
        """测试配置验证工作流"""
        manager = ConfigManager(config_file=self.config_file)
        
        # 测试有效配置
        valid_updates = {
            "default_width": 1000,
            "default_height": 800
        }
        manager.update_config(valid_updates)
        self.assertTrue(manager.validate_config())
        
        # 测试无效配置
        invalid_updates = {
            "default_width": -100  # 无效宽度
        }
        manager.update_config(invalid_updates)
        self.assertFalse(manager.validate_config())
        
        # 重置为默认配置
        manager.reset_to_default()
        self.assertTrue(manager.validate_config())
    
    def test_config_backup_restore_workflow(self):
        """测试配置备份恢复工作流"""
        manager = ConfigManager(config_file=self.config_file)
        
        # 设置初始配置
        initial_config = {
            "default_width": 800,
            "default_height": 600,
            "default_theme": "light"
        }
        manager.update_config(initial_config)
        
        # 创建备份
        backup = manager.create_backup()
        
        # 修改配置
        modified_config = {
            "default_width": 1200,
            "default_height": 900,
            "default_theme": "dark"
        }
        manager.update_config(modified_config)
        
        # 验证修改
        self.assertEqual(manager.config.default_width, 1200)
        self.assertEqual(manager.config.default_theme, "dark")
        
        # 恢复备份
        manager.restore_backup(backup)
        
        # 验证恢复
        self.assertEqual(manager.config.default_width, 800)
        self.assertEqual(manager.config.default_theme, "light")
    
    def test_multiple_managers_same_file(self):
        """测试多个管理器使用同一配置文件"""
        # 创建第一个管理器并设置配置
        manager1 = ConfigManager(config_file=self.config_file)
        manager1.update_config({"default_width": 1000})
        manager1.save_config()
        
        # 创建第二个管理器并加载配置
        manager2 = ConfigManager(config_file=self.config_file)
        config2 = manager2.load_config()
        
        # 验证配置同步
        self.assertEqual(config2.default_width, 1000)
        
        # 第二个管理器修改配置
        manager2.update_config({"default_height": 800})
        manager2.save_config()
        
        # 第一个管理器重新加载配置
        config1_reloaded = manager1.load_config()
        
        # 验证配置同步
        self.assertEqual(config1_reloaded.default_height, 800)
        self.assertEqual(config1_reloaded.default_width, 1000)


if __name__ == '__main__':
    # 配置日志
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    unittest.main(verbosity=2)