#!/usr/bin/env python3
"""
PowerAutomation 性能优化引擎
智能缓存、增量测试和并行执行优化

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import asyncio
import hashlib
import json
import logging
import time
import pickle
import zlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
from collections import defaultdict, OrderedDict
import psutil

logger = logging.getLogger("PowerAutomation.PerformanceEngine")

class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    TTL = "ttl"  # 时间过期
    ADAPTIVE = "adaptive"  # 自适应

class OptimizationType(Enum):
    """优化类型枚举"""
    CACHE_HIT = "cache_hit"
    INCREMENTAL_TEST = "incremental_test"
    PARALLEL_EXECUTION = "parallel_execution"
    RESOURCE_OPTIMIZATION = "resource_optimization"

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds
    
    def update_access(self):
        """更新访问信息"""
        self.last_accessed = datetime.now()
        self.access_count += 1

@dataclass
class TestExecutionResult:
    """测试执行结果"""
    test_id: str
    test_hash: str
    result: Dict[str, Any]
    execution_time: float
    resource_usage: Dict[str, float]
    dependencies: List[str]
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    """性能指标"""
    cache_hit_rate: float
    cache_miss_rate: float
    incremental_test_ratio: float
    parallel_efficiency: float
    resource_utilization: float
    total_time_saved: float
    memory_usage_mb: float
    cpu_usage_percent: float

class SmartCache:
    """智能缓存系统"""
    
    def __init__(self, max_size_mb: int = 1024, strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.strategy = strategy
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.current_size_bytes = 0
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()
        
        # 自适应策略参数
        self.access_patterns = defaultdict(list)
        self.strategy_performance = {
            CacheStrategy.LRU: 0.0,
            CacheStrategy.LFU: 0.0,
            CacheStrategy.TTL: 0.0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # 检查是否过期
                if entry.is_expired():
                    self._remove_entry(key)
                    self.miss_count += 1
                    return None
                
                # 更新访问信息
                entry.update_access()
                
                # LRU策略：移动到末尾
                if self.strategy in [CacheStrategy.LRU, CacheStrategy.ADAPTIVE]:
                    self.cache.move_to_end(key)
                
                self.hit_count += 1
                logger.debug(f"缓存命中: {key}")
                return entry.value
            
            self.miss_count += 1
            logger.debug(f"缓存未命中: {key}")
            return None
    
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None, metadata: Dict[str, Any] = None):
        """存储缓存值"""
        with self._lock:
            # 计算值的大小
            serialized_value = pickle.dumps(value)
            compressed_value = zlib.compress(serialized_value)
            size_bytes = len(compressed_value)
            
            # 检查是否超过最大缓存大小
            if size_bytes > self.max_size_bytes:
                logger.warning(f"值太大，无法缓存: {key} ({size_bytes} bytes)")
                return False
            
            # 如果键已存在，先删除
            if key in self.cache:
                self._remove_entry(key)
            
            # 确保有足够空间
            while self.current_size_bytes + size_bytes > self.max_size_bytes:
                if not self._evict_entry():
                    break
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=compressed_value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds,
                metadata=metadata or {}
            )
            
            self.cache[key] = entry
            self.current_size_bytes += size_bytes
            
            logger.debug(f"缓存存储: {key} ({size_bytes} bytes)")
            return True
    
    def _remove_entry(self, key: str):
        """删除缓存条目"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]
    
    def _evict_entry(self) -> bool:
        """驱逐缓存条目"""
        if not self.cache:
            return False
        
        if self.strategy == CacheStrategy.LRU:
            # 删除最近最少使用的
            key = next(iter(self.cache))
        elif self.strategy == CacheStrategy.LFU:
            # 删除使用频率最低的
            key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
        elif self.strategy == CacheStrategy.TTL:
            # 删除最早过期的
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            if expired_keys:
                key = expired_keys[0]
            else:
                key = next(iter(self.cache))
        else:  # ADAPTIVE
            key = self._adaptive_eviction()
        
        self._remove_entry(key)
        logger.debug(f"驱逐缓存条目: {key}")
        return True
    
    def _adaptive_eviction(self) -> str:
        """自适应驱逐策略"""
        # 简化的自适应算法：结合LRU和LFU
        scores = {}
        now = datetime.now()
        
        for key, entry in self.cache.items():
            # 时间因子 (越久未访问分数越低)
            time_factor = 1.0 / max(1, (now - entry.last_accessed).total_seconds() / 3600)
            
            # 频率因子
            freq_factor = entry.access_count / max(1, (now - entry.created_at).total_seconds() / 3600)
            
            # 大小因子 (越大的条目越容易被驱逐)
            size_factor = 1.0 / max(1, entry.size_bytes / 1024)
            
            scores[key] = time_factor * freq_factor * size_factor
        
        return min(scores.keys(), key=lambda k: scores[k])
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / max(1, total_requests)
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "total_entries": len(self.cache),
            "current_size_mb": self.current_size_bytes / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "utilization": self.current_size_bytes / self.max_size_bytes
        }

class IncrementalTestEngine:
    """增量测试引擎"""
    
    def __init__(self, cache: SmartCache):
        self.cache = cache
        self.test_dependencies: Dict[str, Set[str]] = {}
        self.file_hashes: Dict[str, str] = {}
        self.test_results: Dict[str, TestExecutionResult] = {}
        self._lock = threading.RLock()
    
    def analyze_dependencies(self, test_files: List[str], source_files: List[str]) -> Dict[str, Set[str]]:
        """分析测试依赖关系"""
        dependencies = {}
        
        for test_file in test_files:
            deps = set()
            
            # 简化的依赖分析：基于import语句
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 查找import语句
                import re
                imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
                
                for imp in imports:
                    module = imp[0] or imp[1]
                    if module:
                        # 查找对应的源文件
                        for source_file in source_files:
                            if module.replace('.', '/') in source_file:
                                deps.add(source_file)
                
                dependencies[test_file] = deps
                
            except Exception as e:
                logger.warning(f"分析依赖失败: {test_file} - {e}")
                dependencies[test_file] = set()
        
        self.test_dependencies.update(dependencies)
        return dependencies
    
    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.warning(f"计算文件哈希失败: {file_path} - {e}")
            return ""
    
    def detect_changes(self, files: List[str]) -> Tuple[Set[str], Set[str]]:
        """检测文件变更"""
        changed_files = set()
        unchanged_files = set()
        
        for file_path in files:
            current_hash = self.calculate_file_hash(file_path)
            previous_hash = self.file_hashes.get(file_path)
            
            if previous_hash != current_hash:
                changed_files.add(file_path)
                self.file_hashes[file_path] = current_hash
            else:
                unchanged_files.add(file_path)
        
        return changed_files, unchanged_files
    
    def get_affected_tests(self, changed_files: Set[str]) -> Set[str]:
        """获取受影响的测试"""
        affected_tests = set()
        
        for test_file, dependencies in self.test_dependencies.items():
            if any(changed_file in dependencies for changed_file in changed_files):
                affected_tests.add(test_file)
            elif test_file in changed_files:
                affected_tests.add(test_file)
        
        return affected_tests
    
    def should_run_test(self, test_file: str, force_run: bool = False) -> bool:
        """判断是否需要运行测试"""
        if force_run:
            return True
        
        # 检查测试文件是否有缓存结果
        test_hash = self.calculate_file_hash(test_file)
        cache_key = f"test_result_{test_hash}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"跳过测试 (缓存命中): {test_file}")
            return False
        
        return True
    
    def cache_test_result(self, test_file: str, result: Dict[str, Any], execution_time: float):
        """缓存测试结果"""
        test_hash = self.calculate_file_hash(test_file)
        cache_key = f"test_result_{test_hash}"
        
        test_result = TestExecutionResult(
            test_id=test_file,
            test_hash=test_hash,
            result=result,
            execution_time=execution_time,
            resource_usage=self._get_current_resource_usage(),
            dependencies=list(self.test_dependencies.get(test_file, set())),
            timestamp=datetime.now()
        )
        
        # 缓存24小时
        self.cache.put(cache_key, test_result, ttl_seconds=24*3600)
        self.test_results[test_file] = test_result
    
    def _get_current_resource_usage(self) -> Dict[str, float]:
        """获取当前资源使用情况"""
        try:
            process = psutil.Process()
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / (1024 * 1024),
                "disk_io_read": process.io_counters().read_bytes if hasattr(process, 'io_counters') else 0,
                "disk_io_write": process.io_counters().write_bytes if hasattr(process, 'io_counters') else 0
            }
        except Exception:
            return {"cpu_percent": 0, "memory_mb": 0, "disk_io_read": 0, "disk_io_write": 0}

class ParallelExecutionOptimizer:
    """并行执行优化器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (psutil.cpu_count() or 1) + 4)
        self.execution_history: Dict[str, List[float]] = defaultdict(list)
        self.resource_profiles: Dict[str, Dict[str, float]] = {}
        self._lock = threading.RLock()
    
    def optimize_task_groups(self, tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """优化任务分组"""
        # 按资源需求和执行时间分组
        groups = []
        current_group = []
        current_group_resources = {"cpu": 0, "memory": 0, "io": 0}
        
        # 按预估执行时间排序（长任务优先）
        sorted_tasks = sorted(tasks, key=lambda t: self._estimate_execution_time(t), reverse=True)
        
        for task in sorted_tasks:
            task_resources = self._estimate_resource_usage(task)
            
            # 检查是否可以加入当前组
            if self._can_add_to_group(current_group_resources, task_resources):
                current_group.append(task)
                for resource, usage in task_resources.items():
                    current_group_resources[resource] += usage
            else:
                # 开始新组
                if current_group:
                    groups.append(current_group)
                current_group = [task]
                current_group_resources = task_resources.copy()
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _estimate_execution_time(self, task: Dict[str, Any]) -> float:
        """估算执行时间"""
        task_id = task.get("task_id", "unknown")
        
        # 使用历史数据
        if task_id in self.execution_history:
            history = self.execution_history[task_id]
            return sum(history) / len(history)
        
        # 基于任务类型的默认估算
        task_type = task.get("test_type", "unknown")
        default_times = {
            "unit_test": 30,
            "integration_test": 120,
            "ui_test": 300,
            "performance_test": 600,
            "e2e_test": 900
        }
        
        return default_times.get(task_type, 180)
    
    def _estimate_resource_usage(self, task: Dict[str, Any]) -> Dict[str, float]:
        """估算资源使用"""
        task_type = task.get("test_type", "unknown")
        
        # 基于任务类型的资源估算
        resource_profiles = {
            "unit_test": {"cpu": 0.5, "memory": 0.2, "io": 0.1},
            "integration_test": {"cpu": 1.0, "memory": 0.5, "io": 0.3},
            "ui_test": {"cpu": 2.0, "memory": 1.0, "io": 0.2},
            "performance_test": {"cpu": 4.0, "memory": 2.0, "io": 1.0},
            "e2e_test": {"cpu": 2.0, "memory": 1.5, "io": 0.5}
        }
        
        return resource_profiles.get(task_type, {"cpu": 1.0, "memory": 0.5, "io": 0.3})
    
    def _can_add_to_group(self, current_resources: Dict[str, float], task_resources: Dict[str, float]) -> bool:
        """检查是否可以添加到当前组"""
        # 资源限制
        limits = {"cpu": self.max_workers, "memory": 8.0, "io": 4.0}
        
        for resource, usage in task_resources.items():
            if current_resources.get(resource, 0) + usage > limits.get(resource, float('inf')):
                return False
        
        return True
    
    def record_execution(self, task_id: str, execution_time: float, resource_usage: Dict[str, float]):
        """记录执行结果"""
        with self._lock:
            self.execution_history[task_id].append(execution_time)
            
            # 保持最近20次记录
            if len(self.execution_history[task_id]) > 20:
                self.execution_history[task_id] = self.execution_history[task_id][-20:]
            
            self.resource_profiles[task_id] = resource_usage

class PerformanceOptimizationEngine:
    """性能优化引擎"""
    
    def __init__(self, cache_size_mb: int = 1024):
        self.cache = SmartCache(cache_size_mb)
        self.incremental_engine = IncrementalTestEngine(self.cache)
        self.parallel_optimizer = ParallelExecutionOptimizer()
        
        # 性能指标
        self.metrics = PerformanceMetrics(
            cache_hit_rate=0.0,
            cache_miss_rate=0.0,
            incremental_test_ratio=0.0,
            parallel_efficiency=0.0,
            resource_utilization=0.0,
            total_time_saved=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0
        )
        
        self.optimization_history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
    
    async def initialize(self):
        """初始化性能优化引擎"""
        logger.info("⚡ 初始化性能优化引擎...")
        
        # 启动性能监控
        asyncio.create_task(self._performance_monitoring_loop())
        
        logger.info("✅ 性能优化引擎初始化完成")
    
    async def optimize_test_execution(
        self, 
        test_tasks: List[Dict[str, Any]], 
        source_files: List[str] = None
    ) -> Tuple[List[List[Dict[str, Any]]], Dict[str, Any]]:
        """优化测试执行"""
        start_time = time.time()
        optimization_report = {
            "total_tasks": len(test_tasks),
            "optimizations_applied": [],
            "time_saved_seconds": 0.0,
            "cache_hits": 0,
            "incremental_skips": 0
        }
        
        # 1. 增量测试优化
        if source_files:
            changed_files, _ = self.incremental_engine.detect_changes(source_files)
            if changed_files:
                affected_tests = self.incremental_engine.get_affected_tests(changed_files)
                
                # 过滤出需要运行的测试
                filtered_tasks = []
                for task in test_tasks:
                    test_file = task.get("test_file", "")
                    if test_file in affected_tests or self.incremental_engine.should_run_test(test_file):
                        filtered_tasks.append(task)
                    else:
                        optimization_report["incremental_skips"] += 1
                
                test_tasks = filtered_tasks
                optimization_report["optimizations_applied"].append("incremental_testing")
        
        # 2. 缓存优化
        cached_tasks = []
        remaining_tasks = []
        
        for task in test_tasks:
            cache_key = self._generate_task_cache_key(task)
            cached_result = self.cache.get(cache_key)
            
            if cached_result:
                cached_tasks.append((task, cached_result))
                optimization_report["cache_hits"] += 1
            else:
                remaining_tasks.append(task)
        
        if cached_tasks:
            optimization_report["optimizations_applied"].append("result_caching")
        
        # 3. 并行执行优化
        optimized_groups = self.parallel_optimizer.optimize_task_groups(remaining_tasks)
        
        if len(optimized_groups) > 1:
            optimization_report["optimizations_applied"].append("parallel_optimization")
        
        # 计算时间节省
        original_time = sum(self.parallel_optimizer._estimate_execution_time(task) for task in test_tasks)
        optimized_time = sum(
            max(self.parallel_optimizer._estimate_execution_time(task) for task in group) 
            for group in optimized_groups
        )
        optimization_report["time_saved_seconds"] = max(0, original_time - optimized_time)
        
        # 更新指标
        await self._update_metrics(optimization_report)
        
        execution_time = time.time() - start_time
        logger.info(f"⚡ 测试执行优化完成 ({execution_time:.2f}s): {optimization_report}")
        
        return optimized_groups, optimization_report
    
    def _generate_task_cache_key(self, task: Dict[str, Any]) -> str:
        """生成任务缓存键"""
        # 基于任务内容生成哈希
        task_str = json.dumps(task, sort_keys=True)
        return f"task_{hashlib.md5(task_str.encode()).hexdigest()}"
    
    async def cache_task_result(self, task: Dict[str, Any], result: Dict[str, Any], execution_time: float):
        """缓存任务结果"""
        cache_key = self._generate_task_cache_key(task)
        
        cache_data = {
            "result": result,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
            "task_metadata": {
                "test_type": task.get("test_type"),
                "test_level": task.get("test_level")
            }
        }
        
        # 缓存12小时
        self.cache.put(cache_key, cache_data, ttl_seconds=12*3600)
        
        # 记录到并行优化器
        task_id = task.get("task_id", cache_key)
        resource_usage = task.get("resource_usage", {})
        self.parallel_optimizer.record_execution(task_id, execution_time, resource_usage)
    
    async def _update_metrics(self, optimization_report: Dict[str, Any]):
        """更新性能指标"""
        with self._lock:
            cache_stats = self.cache.get_stats()
            
            self.metrics.cache_hit_rate = cache_stats["hit_rate"]
            self.metrics.cache_miss_rate = 1.0 - cache_stats["hit_rate"]
            self.metrics.total_time_saved += optimization_report["time_saved_seconds"]
            
            # 计算增量测试比例
            total_tasks = optimization_report["total_tasks"]
            if total_tasks > 0:
                self.metrics.incremental_test_ratio = optimization_report["incremental_skips"] / total_tasks
            
            # 系统资源使用
            try:
                self.metrics.memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
                self.metrics.cpu_usage_percent = psutil.cpu_percent()
            except Exception:
                pass
    
    async def _performance_monitoring_loop(self):
        """性能监控循环"""
        while True:
            try:
                # 收集性能数据
                cache_stats = self.cache.get_stats()
                system_stats = {
                    "memory_usage_mb": psutil.virtual_memory().used / (1024 * 1024),
                    "cpu_usage_percent": psutil.cpu_percent(),
                    "disk_usage_percent": psutil.disk_usage('/').percent
                }
                
                # 记录历史数据
                self.optimization_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "cache_stats": cache_stats,
                    "system_stats": system_stats,
                    "metrics": {
                        "cache_hit_rate": self.metrics.cache_hit_rate,
                        "total_time_saved": self.metrics.total_time_saved,
                        "incremental_test_ratio": self.metrics.incremental_test_ratio
                    }
                })
                
                # 保持最近100条记录
                if len(self.optimization_history) > 100:
                    self.optimization_history = self.optimization_history[-100:]
                
                await asyncio.sleep(60)  # 每分钟收集一次
                
            except Exception as e:
                logger.error(f"❌ 性能监控错误: {e}")
                await asyncio.sleep(300)  # 出错时等待5分钟
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        cache_stats = self.cache.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cache_performance": cache_stats,
            "optimization_metrics": {
                "cache_hit_rate": self.metrics.cache_hit_rate,
                "cache_miss_rate": self.metrics.cache_miss_rate,
                "incremental_test_ratio": self.metrics.incremental_test_ratio,
                "parallel_efficiency": self.metrics.parallel_efficiency,
                "total_time_saved_hours": self.metrics.total_time_saved / 3600
            },
            "system_resources": {
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "cpu_usage_percent": self.metrics.cpu_usage_percent,
                "cache_memory_mb": cache_stats["current_size_mb"]
            },
            "optimization_history_count": len(self.optimization_history),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 缓存命中率建议
        if self.metrics.cache_hit_rate < 0.5:
            recommendations.append("考虑增加缓存大小或调整缓存策略以提高命中率")
        
        # 增量测试建议
        if self.metrics.incremental_test_ratio < 0.3:
            recommendations.append("优化依赖分析以提高增量测试效率")
        
        # 资源使用建议
        if self.metrics.memory_usage_mb > 8192:  # 8GB
            recommendations.append("内存使用较高，考虑优化内存管理")
        
        if self.metrics.cpu_usage_percent > 80:
            recommendations.append("CPU使用率较高，考虑调整并行度")
        
        return recommendations

# 导出主要类
__all__ = [
    'PerformanceOptimizationEngine',
    'SmartCache',
    'IncrementalTestEngine', 
    'ParallelExecutionOptimizer',
    'PerformanceMetrics'
]

