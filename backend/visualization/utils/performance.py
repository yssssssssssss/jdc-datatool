"""性能监控模块

提供可视化系统的性能监控功能，包括渲染时间、内存使用、缓存命中率等指标的监控和分析
"""

import time
import psutil
import threading
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics
from functools import wraps
import gc
import tracemalloc
from pathlib import Path


@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    
    timestamp: float
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class RenderPerformance:
    """渲染性能数据类"""
    
    chart_type: str
    library: str
    data_points: int
    render_time: float  # 毫秒
    memory_usage: int  # 字节
    file_size: int  # 字节
    timestamp: float
    success: bool = True
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class PerformanceMonitor:
    """性能监控器
    
    监控和记录可视化系统的各种性能指标
    """
    
    def __init__(self, max_history: int = 1000, enable_memory_profiling: bool = False):
        """初始化性能监控器
        
        Args:
            max_history: 最大历史记录数
            enable_memory_profiling: 是否启用内存分析
        """
        self.logger = logging.getLogger(__name__)
        self.max_history = max_history
        self.enable_memory_profiling = enable_memory_profiling
        
        # 性能指标存储
        self.metrics_history: deque = deque(maxlen=max_history)
        self.render_history: deque = deque(maxlen=max_history)
        
        # 实时统计
        self.current_stats = {
            'total_renders': 0,
            'successful_renders': 0,
            'failed_renders': 0,
            'total_render_time': 0.0,
            'total_memory_usage': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # 按类型分组的统计
        self.stats_by_type = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'total_memory': 0,
            'avg_time': 0.0,
            'avg_memory': 0.0
        })
        
        # 按库分组的统计
        self.stats_by_library = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'total_memory': 0,
            'avg_time': 0.0,
            'avg_memory': 0.0
        })
        
        # 系统资源监控
        self.system_monitor_enabled = False
        self.system_monitor_thread = None
        self.system_metrics = deque(maxlen=max_history)
        
        # 内存分析
        if self.enable_memory_profiling:
            tracemalloc.start()
        
        # 锁
        self._lock = threading.Lock()
    
    def start_system_monitoring(self, interval: float = 5.0):
        """启动系统资源监控
        
        Args:
            interval: 监控间隔（秒）
        """
        if self.system_monitor_enabled:
            return
        
        self.system_monitor_enabled = True
        self.system_monitor_thread = threading.Thread(
            target=self._system_monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.system_monitor_thread.start()
        self.logger.info(f"系统资源监控已启动，间隔: {interval}秒")
    
    def stop_system_monitoring(self):
        """停止系统资源监控"""
        self.system_monitor_enabled = False
        if self.system_monitor_thread:
            self.system_monitor_thread.join(timeout=1.0)
        self.logger.info("系统资源监控已停止")
    
    def _system_monitor_loop(self, interval: float):
        """系统监控循环
        
        Args:
            interval: 监控间隔
        """
        while self.system_monitor_enabled:
            try:
                # 获取系统指标
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # 获取当前进程指标
                process = psutil.Process()
                process_memory = process.memory_info()
                process_cpu = process.cpu_percent()
                
                # 记录指标
                timestamp = time.time()
                
                system_metric = {
                    'timestamp': timestamp,
                    'cpu_percent': cpu_percent,
                    'memory_total': memory.total,
                    'memory_used': memory.used,
                    'memory_percent': memory.percent,
                    'disk_total': disk.total,
                    'disk_used': disk.used,
                    'disk_percent': (disk.used / disk.total) * 100,
                    'process_memory_rss': process_memory.rss,
                    'process_memory_vms': process_memory.vms,
                    'process_cpu_percent': process_cpu
                }
                
                with self._lock:
                    self.system_metrics.append(system_metric)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"系统监控错误: {e}")
                time.sleep(interval)
    
    def record_metric(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
        """记录性能指标
        
        Args:
            name: 指标名称
            value: 指标值
            unit: 单位
            tags: 标签
        """
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        with self._lock:
            self.metrics_history.append(metric)
    
    def record_render_performance(self, performance_data: RenderPerformance):
        """记录渲染性能
        
        Args:
            performance_data: 渲染性能数据
        """
        with self._lock:
            # 添加到历史记录
            self.render_history.append(performance_data)
            
            # 更新总体统计
            self.current_stats['total_renders'] += 1
            if performance_data.success:
                self.current_stats['successful_renders'] += 1
                self.current_stats['total_render_time'] += performance_data.render_time
                self.current_stats['total_memory_usage'] += performance_data.memory_usage
            else:
                self.current_stats['failed_renders'] += 1
            
            # 更新按类型统计
            type_stats = self.stats_by_type[performance_data.chart_type]
            type_stats['count'] += 1
            if performance_data.success:
                type_stats['total_time'] += performance_data.render_time
                type_stats['total_memory'] += performance_data.memory_usage
                type_stats['avg_time'] = type_stats['total_time'] / type_stats['count']
                type_stats['avg_memory'] = type_stats['total_memory'] / type_stats['count']
            
            # 更新按库统计
            lib_stats = self.stats_by_library[performance_data.library]
            lib_stats['count'] += 1
            if performance_data.success:
                lib_stats['total_time'] += performance_data.render_time
                lib_stats['total_memory'] += performance_data.memory_usage
                lib_stats['avg_time'] = lib_stats['total_time'] / lib_stats['count']
                lib_stats['avg_memory'] = lib_stats['total_memory'] / lib_stats['count']
    
    def record_cache_hit(self):
        """记录缓存命中"""
        with self._lock:
            self.current_stats['cache_hits'] += 1
        self.record_metric('cache_hit', 1, 'count')
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        with self._lock:
            self.current_stats['cache_misses'] += 1
        self.record_metric('cache_miss', 1, 'count')
    
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        with self._lock:
            stats = self.current_stats.copy()
            
            # 计算派生指标
            total_renders = stats['total_renders']
            if total_renders > 0:
                stats['success_rate'] = stats['successful_renders'] / total_renders
                stats['failure_rate'] = stats['failed_renders'] / total_renders
                
                if stats['successful_renders'] > 0:
                    stats['avg_render_time'] = stats['total_render_time'] / stats['successful_renders']
                    stats['avg_memory_usage'] = stats['total_memory_usage'] / stats['successful_renders']
                else:
                    stats['avg_render_time'] = 0.0
                    stats['avg_memory_usage'] = 0
            else:
                stats['success_rate'] = 0.0
                stats['failure_rate'] = 0.0
                stats['avg_render_time'] = 0.0
                stats['avg_memory_usage'] = 0
            
            # 缓存命中率
            total_cache_requests = stats['cache_hits'] + stats['cache_misses']
            if total_cache_requests > 0:
                stats['cache_hit_rate'] = stats['cache_hits'] / total_cache_requests
            else:
                stats['cache_hit_rate'] = 0.0
            
            return stats
    
    def get_stats_by_type(self) -> Dict[str, Dict[str, Any]]:
        """获取按图表类型分组的统计信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 按类型分组的统计信息
        """
        with self._lock:
            return dict(self.stats_by_type)
    
    def get_stats_by_library(self) -> Dict[str, Dict[str, Any]]:
        """获取按库分组的统计信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 按库分组的统计信息
        """
        with self._lock:
            return dict(self.stats_by_library)
    
    def get_recent_metrics(self, metric_name: str = None, limit: int = 100) -> List[PerformanceMetric]:
        """获取最近的性能指标
        
        Args:
            metric_name: 指标名称过滤
            limit: 返回数量限制
        
        Returns:
            List[PerformanceMetric]: 性能指标列表
        """
        with self._lock:
            metrics = list(self.metrics_history)
        
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        return metrics[-limit:] if limit else metrics
    
    def get_recent_renders(self, limit: int = 100) -> List[RenderPerformance]:
        """获取最近的渲染性能记录
        
        Args:
            limit: 返回数量限制
        
        Returns:
            List[RenderPerformance]: 渲染性能记录列表
        """
        with self._lock:
            renders = list(self.render_history)
        
        return renders[-limit:] if limit else renders
    
    def get_system_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取系统资源指标
        
        Args:
            limit: 返回数量限制
        
        Returns:
            List[Dict[str, Any]]: 系统指标列表
        """
        with self._lock:
            metrics = list(self.system_metrics)
        
        return metrics[-limit:] if limit else metrics
    
    def analyze_performance(self, time_window: int = 3600) -> Dict[str, Any]:
        """分析性能趋势
        
        Args:
            time_window: 时间窗口（秒）
        
        Returns:
            Dict[str, Any]: 性能分析结果
        """
        current_time = time.time()
        start_time = current_time - time_window
        
        # 过滤时间窗口内的数据
        with self._lock:
            recent_renders = [
                r for r in self.render_history
                if r.timestamp >= start_time and r.success
            ]
        
        if not recent_renders:
            return {
                'time_window': time_window,
                'total_renders': 0,
                'analysis': '没有足够的数据进行分析'
            }
        
        # 计算统计指标
        render_times = [r.render_time for r in recent_renders]
        memory_usages = [r.memory_usage for r in recent_renders]
        data_points = [r.data_points for r in recent_renders]
        
        analysis = {
            'time_window': time_window,
            'total_renders': len(recent_renders),
            'render_time': {
                'min': min(render_times),
                'max': max(render_times),
                'mean': statistics.mean(render_times),
                'median': statistics.median(render_times),
                'stdev': statistics.stdev(render_times) if len(render_times) > 1 else 0
            },
            'memory_usage': {
                'min': min(memory_usages),
                'max': max(memory_usages),
                'mean': statistics.mean(memory_usages),
                'median': statistics.median(memory_usages),
                'stdev': statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0
            },
            'data_points': {
                'min': min(data_points),
                'max': max(data_points),
                'mean': statistics.mean(data_points),
                'median': statistics.median(data_points)
            }
        }
        
        # 性能趋势分析
        if len(recent_renders) >= 10:
            # 分析渲染时间趋势
            mid_point = len(recent_renders) // 2
            first_half_avg = statistics.mean(render_times[:mid_point])
            second_half_avg = statistics.mean(render_times[mid_point:])
            
            time_trend = 'improving' if second_half_avg < first_half_avg else 'degrading'
            analysis['trends'] = {
                'render_time': time_trend,
                'time_change_percent': ((second_half_avg - first_half_avg) / first_half_avg) * 100
            }
        
        return analysis
    
    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告
        
        Returns:
            Dict[str, Any]: 性能报告
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_stats': self.get_current_stats(),
            'stats_by_type': self.get_stats_by_type(),
            'stats_by_library': self.get_stats_by_library(),
            'recent_analysis': self.analyze_performance(3600),  # 最近1小时
            'system_info': self._get_system_info()
        }
        
        # 添加内存分析（如果启用）
        if self.enable_memory_profiling:
            report['memory_profile'] = self._get_memory_profile()
        
        return report
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息
        
        Returns:
            Dict[str, Any]: 系统信息
        """
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total': memory.total,
                'memory_available': memory.available,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'python_version': f"{psutil.version_info}"
            }
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def _get_memory_profile(self) -> Dict[str, Any]:
        """获取内存分析信息
        
        Returns:
            Dict[str, Any]: 内存分析信息
        """
        try:
            if not tracemalloc.is_tracing():
                return {'error': '内存分析未启用'}
            
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            # 获取前10个内存使用最多的位置
            top_10 = top_stats[:10]
            
            memory_profile = {
                'total_memory': sum(stat.size for stat in top_stats),
                'total_blocks': sum(stat.count for stat in top_stats),
                'top_consumers': []
            }
            
            for stat in top_10:
                memory_profile['top_consumers'].append({
                    'filename': stat.traceback.format()[0] if stat.traceback else 'unknown',
                    'size_mb': stat.size / 1024 / 1024,
                    'blocks': stat.count
                })
            
            return memory_profile
            
        except Exception as e:
            self.logger.error(f"获取内存分析失败: {e}")
            return {'error': str(e)}
    
    def export_report(self, filepath: str, format: str = 'json') -> bool:
        """导出性能报告
        
        Args:
            filepath: 文件路径
            format: 导出格式 ('json' 或 'csv')
        
        Returns:
            bool: 是否成功导出
        """
        try:
            report = self.get_performance_report()
            
            if format.lower() == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            elif format.lower() == 'csv':
                import pandas as pd
                
                # 转换渲染历史为DataFrame
                render_data = [r.to_dict() for r in self.get_recent_renders()]
                if render_data:
                    df = pd.DataFrame(render_data)
                    df.to_csv(filepath, index=False)
                else:
                    # 创建空CSV
                    pd.DataFrame().to_csv(filepath, index=False)
            
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            self.logger.info(f"性能报告已导出到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出性能报告失败: {e}")
            return False
    
    def clear_history(self):
        """清除历史记录"""
        with self._lock:
            self.metrics_history.clear()
            self.render_history.clear()
            self.system_metrics.clear()
            
            # 重置统计
            self.current_stats = {
                'total_renders': 0,
                'successful_renders': 0,
                'failed_renders': 0,
                'total_render_time': 0.0,
                'total_memory_usage': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }
            
            self.stats_by_type.clear()
            self.stats_by_library.clear()
        
        self.logger.info("性能监控历史记录已清除")
    
    def __del__(self):
        """析构函数"""
        self.stop_system_monitoring()
        if self.enable_memory_profiling and tracemalloc.is_tracing():
            tracemalloc.stop()


def performance_timer(monitor: PerformanceMonitor = None):
    """性能计时装饰器
    
    Args:
        monitor: 性能监控器实例
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                success = True
                error_msg = ""
            except Exception as e:
                result = None
                success = False
                error_msg = str(e)
                raise
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                render_time = (end_time - start_time) * 1000  # 转换为毫秒
                memory_usage = end_memory - start_memory
                
                if monitor:
                    # 记录性能指标
                    monitor.record_metric(
                        f"function_{func.__name__}_time",
                        render_time,
                        "ms",
                        {'function': func.__name__}
                    )
                    
                    monitor.record_metric(
                        f"function_{func.__name__}_memory",
                        memory_usage,
                        "bytes",
                        {'function': func.__name__}
                    )
            
            return result
        
        return wrapper
    return decorator


# 全局性能监控器实例
_global_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例
    
    Returns:
        PerformanceMonitor: 性能监控器实例
    """
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor


# 为了兼容性，提供别名
get_global_monitor = get_performance_monitor


def reset_global_monitor():
    """重置全局性能监控器实例"""
    global _global_performance_monitor
    _global_performance_monitor = None


def set_global_monitor(monitor: PerformanceMonitor):
    """设置全局性能监控器实例
    
    Args:
        monitor: 性能监控器实例
    """
    global _global_performance_monitor
    _global_performance_monitor = monitor


def start_monitoring(interval: float = 5.0):
    """启动全局性能监控
    
    Args:
        interval: 监控间隔（秒）
    """
    monitor = get_performance_monitor()
    monitor.start_system_monitoring(interval)


def stop_monitoring():
    """停止全局性能监控"""
    monitor = get_performance_monitor()
    monitor.stop_system_monitoring()


def record_render_performance(chart_type: str, library: str, data_points: int,
                            render_time: float, memory_usage: int, file_size: int,
                            success: bool = True, error_message: str = ""):
    """记录渲染性能（便捷函数）
    
    Args:
        chart_type: 图表类型
        library: 使用的库
        data_points: 数据点数
        render_time: 渲染时间（毫秒）
        memory_usage: 内存使用（字节）
        file_size: 文件大小（字节）
        success: 是否成功
        error_message: 错误信息
    """
    monitor = get_performance_monitor()
    performance_data = RenderPerformance(
        chart_type=chart_type,
        library=library,
        data_points=data_points,
        render_time=render_time,
        memory_usage=memory_usage,
        file_size=file_size,
        timestamp=time.time(),
        success=success,
        error_message=error_message
    )
    monitor.record_render_performance(performance_data)