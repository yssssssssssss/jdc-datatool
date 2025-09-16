"""配置管理模块

提供可视化系统的配置管理功能，包括配置加载、验证、更新等
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import shutil
from datetime import datetime

# 默认配置常量
DEFAULT_CONFIG = {
    'echarts': {
        'theme': 'default',
        'width': 800,
        'height': 600,
        'animation': True,
        'toolbox': True,
        'legend': True,
    },
    'bokeh': {
        'theme': 'caliber',
        'width': 800,
        'height': 600,
        'toolbar_location': 'above',
        'tools': 'pan,wheel_zoom,box_zoom,reset,save',
    },
    'performance': {
        'enable_monitoring': True,
        'cache_size': 100,
        'log_level': 'INFO',
    }
}


@dataclass
class VisualizationConfig:
    """可视化配置数据类"""
    
    # 基础配置
    default_library: str = "echarts"
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    max_data_points: int = 10000  # 最大数据点数
    
    # 性能配置
    performance_monitoring: bool = True
    memory_limit_mb: int = 512  # 内存限制（MB）
    render_timeout: int = 30  # 渲染超时时间（秒）
    
    # 导出配置
    export_formats: List[str] = None
    export_quality: str = "high"  # low, medium, high
    export_dpi: int = 300
    
    # 主题配置
    default_theme: str = "default"
    custom_themes: Dict[str, Dict] = None
    
    # 库特定配置
    echarts_config: Dict[str, Any] = None
    bokeh_config: Dict[str, Any] = None
    
    # 安全配置
    allowed_file_types: List[str] = None
    max_file_size_mb: int = 100
    
    def __post_init__(self):
        """初始化后处理"""
        if self.export_formats is None:
            self.export_formats = ["html", "png", "svg", "json"]
        
        if self.custom_themes is None:
            self.custom_themes = {}
        
        if self.echarts_config is None:
            self.echarts_config = {
                "animation": True,
                "animationDuration": 1000,
                "responsive": True,
                "locale": "zh"
            }
        
        if self.bokeh_config is None:
            self.bokeh_config = {
                "tools": ["pan", "wheel_zoom", "box_zoom", "reset", "save"],
                "toolbar_location": "above",
                "sizing_mode": "stretch_width"
            }
        
        if self.allowed_file_types is None:
            self.allowed_file_types = [".csv", ".xlsx", ".json", ".parquet"]


class ConfigManager:
    """配置管理器
    
    负责加载、验证、更新和保存可视化系统配置
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.logger = logging.getLogger(__name__)
        
        # 设置配置文件路径
        if config_path is None:
            self.config_path = self._get_default_config_path()
        else:
            self.config_path = Path(config_path)
        
        # 初始化配置
        self._config = VisualizationConfig()
        self._config_cache = {}
        
        # 加载配置
        self.load_config()
    
    def _get_default_config_path(self) -> Path:
        """获取默认配置文件路径
        
        Returns:
            Path: 默认配置文件路径
        """
        # 优先级：环境变量 > 项目根目录 > 用户目录
        
        # 1. 检查环境变量
        env_path = os.getenv('VISUALIZATION_CONFIG_PATH')
        if env_path:
            return Path(env_path)
        
        # 2. 检查项目根目录
        project_root = Path.cwd()
        while project_root.parent != project_root:
            config_file = project_root / 'visualization_config.yaml'
            if config_file.exists():
                return config_file
            project_root = project_root.parent
        
        # 3. 使用当前目录
        return Path.cwd() / 'visualization_config.yaml'
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            bool: 是否成功加载
        """
        if config_path:
            self.config_path = Path(config_path)
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                        config_data = yaml.safe_load(f)
                    elif self.config_path.suffix.lower() == '.json':
                        config_data = json.load(f)
                    else:
                        self.logger.warning(f"不支持的配置文件格式: {self.config_path.suffix}")
                        return False
                
                # 更新配置
                self._update_config_from_dict(config_data)
                self.logger.info(f"成功加载配置文件: {self.config_path}")
                return True
            else:
                self.logger.info(f"配置文件不存在，使用默认配置: {self.config_path}")
                # 创建默认配置文件
                self.save_config()
                return True
                
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """从字典更新配置
        
        Args:
            config_data: 配置数据字典
        """
        # 验证配置数据
        if not self.validate_config(config_data):
            self.logger.warning("配置数据验证失败，使用默认配置")
            return
        
        # 更新配置对象
        for key, value in config_data.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                self.logger.warning(f"未知的配置项: {key}")
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """保存配置文件
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            bool: 是否成功保存
        """
        if config_path:
            self.config_path = Path(config_path)
        
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为字典
            config_dict = asdict(self._config)
            
            # 保存文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                elif self.config_path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                else:
                    # 默认使用YAML格式
                    self.config_path = self.config_path.with_suffix('.yaml')
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"成功保存配置文件: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False
    
    def validate_config(self, config_data: Dict[str, Any]) -> bool:
        """验证配置数据
        
        Args:
            config_data: 配置数据字典
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 检查必需的配置项
            required_fields = ['default_library']
            for field in required_fields:
                if field not in config_data:
                    self.logger.error(f"缺少必需的配置项: {field}")
                    return False
            
            # 验证数据类型
            type_checks = {
                'default_library': str,
                'cache_enabled': bool,
                'cache_ttl': int,
                'max_data_points': int,
                'performance_monitoring': bool,
                'memory_limit_mb': int,
                'render_timeout': int,
                'export_formats': list,
                'export_quality': str,
                'export_dpi': int,
                'default_theme': str,
                'max_file_size_mb': int
            }
            
            for field, expected_type in type_checks.items():
                if field in config_data and not isinstance(config_data[field], expected_type):
                    self.logger.error(f"配置项 {field} 类型错误，期望 {expected_type.__name__}")
                    return False
            
            # 验证取值范围
            if 'default_library' in config_data:
                valid_libraries = ['echarts', 'bokeh']
                if config_data['default_library'] not in valid_libraries:
                    self.logger.error(f"不支持的默认库: {config_data['default_library']}")
                    return False
            
            if 'export_quality' in config_data:
                valid_qualities = ['low', 'medium', 'high']
                if config_data['export_quality'] not in valid_qualities:
                    self.logger.error(f"不支持的导出质量: {config_data['export_quality']}")
                    return False
            
            # 验证数值范围
            range_checks = {
                'cache_ttl': (1, 86400),  # 1秒到1天
                'max_data_points': (1, 1000000),  # 1到100万
                'memory_limit_mb': (64, 8192),  # 64MB到8GB
                'render_timeout': (1, 300),  # 1秒到5分钟
                'export_dpi': (72, 600),  # 72到600 DPI
                'max_file_size_mb': (1, 1024)  # 1MB到1GB
            }
            
            for field, (min_val, max_val) in range_checks.items():
                if field in config_data:
                    value = config_data[field]
                    if not (min_val <= value <= max_val):
                        self.logger.error(f"配置项 {field} 超出范围 [{min_val}, {max_val}]: {value}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
    
    def get_config(self) -> VisualizationConfig:
        """获取配置对象
        
        Returns:
            VisualizationConfig: 配置对象的副本
        """
        return deepcopy(self._config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            Any: 配置值
        """
        # 支持点号分隔的嵌套键
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except:
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        
        Returns:
            bool: 是否成功设置
        """
        try:
            # 支持点号分隔的嵌套键
            keys = key.split('.')
            
            if len(keys) == 1:
                # 直接设置顶级属性
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                    return True
                else:
                    self.logger.warning(f"未知的配置项: {key}")
                    return False
            else:
                # 设置嵌套属性
                obj = self._config
                for k in keys[:-1]:
                    if hasattr(obj, k):
                        obj = getattr(obj, k)
                    else:
                        self.logger.warning(f"配置路径不存在: {'.'.join(keys[:-1])}")
                        return False
                
                if isinstance(obj, dict):
                    obj[keys[-1]] = value
                    return True
                else:
                    self.logger.warning(f"无法设置配置项: {key}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"设置配置失败: {e}")
            return False
    
    def update(self, config_dict: Dict[str, Any]) -> bool:
        """批量更新配置
        
        Args:
            config_dict: 配置字典
        
        Returns:
            bool: 是否成功更新
        """
        try:
            # 验证配置
            if not self.validate_config(config_dict):
                return False
            
            # 更新配置
            self._update_config_from_dict(config_dict)
            return True
            
        except Exception as e:
            self.logger.error(f"批量更新配置失败: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """重置为默认配置
        
        Returns:
            bool: 是否成功重置
        """
        try:
            self._config = VisualizationConfig()
            self.logger.info("配置已重置为默认值")
            return True
        except Exception as e:
            self.logger.error(f"重置配置失败: {e}")
            return False
    
    def get_library_config(self, library_name: str) -> Dict[str, Any]:
        """获取特定库的配置
        
        Args:
            library_name: 库名称
        
        Returns:
            Dict[str, Any]: 库配置字典
        """
        config_key = f"{library_name}_config"
        return self.get(config_key, {})
    
    def set_library_config(self, library_name: str, config: Dict[str, Any]) -> bool:
        """设置特定库的配置
        
        Args:
            library_name: 库名称
            config: 库配置字典
        
        Returns:
            bool: 是否成功设置
        """
        config_key = f"{library_name}_config"
        return self.set(config_key, config)
    
    def get_theme_config(self, theme_name: str) -> Dict[str, Any]:
        """获取主题配置
        
        Args:
            theme_name: 主题名称
        
        Returns:
            Dict[str, Any]: 主题配置字典
        """
        custom_themes = self.get('custom_themes', {})
        return custom_themes.get(theme_name, {})
    
    def set_theme_config(self, theme_name: str, theme_config: Dict[str, Any]) -> bool:
        """设置主题配置
        
        Args:
            theme_name: 主题名称
            theme_config: 主题配置字典
        
        Returns:
            bool: 是否成功设置
        """
        try:
            if not hasattr(self._config, 'custom_themes'):
                self._config.custom_themes = {}
            
            self._config.custom_themes[theme_name] = theme_config
            return True
        except Exception as e:
            self.logger.error(f"设置主题配置失败: {e}")
            return False
    
    def export_config(self, format: str = 'yaml') -> str:
        """导出配置为字符串
        
        Args:
            format: 导出格式 ('yaml' 或 'json')
        
        Returns:
            str: 配置字符串
        """
        config_dict = asdict(self._config)
        
        if format.lower() == 'json':
            return json.dumps(config_dict, indent=2, ensure_ascii=False)
        else:
            return yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)
    
    def import_config(self, config_str: str, format: str = 'yaml') -> bool:
        """从字符串导入配置
        
        Args:
            config_str: 配置字符串
            format: 配置格式 ('yaml' 或 'json')
        
        Returns:
            bool: 是否成功导入
        """
        try:
            if format.lower() == 'json':
                config_data = json.loads(config_str)
            else:
                config_data = yaml.safe_load(config_str)
            
            return self.update(config_data)
            
        except Exception as e:
            self.logger.error(f"导入配置失败: {e}")
            return False
    
    def reload_config(self) -> bool:
        """重新加载配置文件
        
        Returns:
            bool: 是否成功重新加载
        """
        return self.load_config()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ConfigManager(config_path={self.config_path})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"ConfigManager(config_path={self.config_path}, default_library={self._config.default_library})"


# 全局配置管理器实例
_global_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例
    
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def get_config() -> VisualizationConfig:
    """获取全局配置对象
    
    Returns:
        VisualizationConfig: 配置对象
    """
    return get_config_manager().get_config()


def set_config_path(config_path: str) -> bool:
    """设置全局配置文件路径
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        bool: 是否成功设置
    """
    global _global_config_manager
    _global_config_manager = ConfigManager(config_path)
    return True