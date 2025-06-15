#!/usr/bin/env python3
"""
PowerAutomation 分布式协调器引擎包
集成智能调度、性能优化和分布式协调功能

作者: PowerAutomation团队
版本: 1.0.0-production
"""

from .smart_scheduler import (
    SmartSchedulingEngine,
    NodePerformanceMetrics,
    TaskCharacteristics,
    NodePerformancePredictor,
    TaskNodeMatcher
)

from .performance_engine import (
    PerformanceOptimizationEngine,
    SmartCache,
    IncrementalTestEngine,
    ParallelExecutionOptimizer,
    PerformanceMetrics
)

from .distributed_coordinator import (
    DistributedTestCoordinator,
    TestNode,
    TestTask,
    TestResult,
    NodeManager,
    TaskScheduler
)

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"

__all__ = [
    # 智能调度
    'SmartSchedulingEngine',
    'NodePerformanceMetrics',
    'TaskCharacteristics',
    'NodePerformancePredictor',
    'TaskNodeMatcher',
    
    # 性能优化
    'PerformanceOptimizationEngine',
    'SmartCache',
    'IncrementalTestEngine',
    'ParallelExecutionOptimizer',
    'PerformanceMetrics',
    
    # 分布式协调
    'DistributedTestCoordinator',
    'TestNode',
    'TestTask',
    'TestResult',
    'NodeManager',
    'TaskScheduler'
]

# 模块信息
DISTRIBUTED_COORDINATOR_INFO = {
    "name": "PowerAutomation 分布式测试协调器",
    "version": __version__,
    "description": "企业级分布式测试执行协调器，支持智能调度、性能优化和AI集成",
    "features": [
        "机器学习驱动的智能调度",
        "多层缓存和性能优化",
        "十层测试架构集成",
        "AI组件深度集成",
        "企业级监控和报告"
    ],
    "compatibility": {
        "powerautomation_version": ">=0.571",
        "python_version": ">=3.11",
        "required_packages": [
            "scikit-learn>=1.7.0",
            "numpy>=1.25.0",
            "pandas>=2.1.0",
            "asyncio",
            "psutil"
        ]
    }
}

