#!/usr/bin/env python3
"""
PowerAutomation 分布式测试协调器 MCP 适配器
将分布式协调器功能暴露为MCP服务

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

# 导入现有MCP基础设施
try:
    from mcptool.base_mcp import BaseMCP
    from mcptool.mcp_types import MCPRequest, MCPResponse, MCPError
except ImportError:
    # 如果MCP基础设施不可用，创建基础类
    class BaseMCP:
        def __init__(self, name: str):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
    
    @dataclass
    class MCPRequest:
        method: str
        params: Dict[str, Any]
        id: Optional[str] = None
    
    @dataclass
    class MCPResponse:
        result: Any
        id: Optional[str] = None
        error: Optional[str] = None

# 导入分布式协调器组件
try:
    from shared_core.engines.distributed_coordinator import (
        DistributedTestCoordinator,
        SmartSchedulingEngine,
        PerformanceOptimizationEngine
    )
    from tests.automated_testing_framework.integrations.test_architecture_integrator import (
        TestArchitectureIntegrator
    )
    from tests.automated_testing_framework.integrations.ai_integrator import (
        PowerAutoAIIntegrator
    )
except ImportError as e:
    logging.warning(f"导入分布式协调器组件失败: {e}")
    # 创建模拟类以保证MCP适配器可以运行
    class DistributedTestCoordinator:
        async def initialize(self): pass
        async def get_status(self): return {"status": "mock"}
    
    class SmartSchedulingEngine:
        async def initialize(self): pass
        async def get_scheduling_insights(self): return {"insights": "mock"}
    
    class PerformanceOptimizationEngine:
        async def initialize(self): pass
        def get_performance_report(self): return {"performance": "mock"}
    
    class TestArchitectureIntegrator:
        def __init__(self, path): pass
        async def initialize(self): pass
        async def get_integration_report(self): return {"integration": "mock"}
    
    class PowerAutoAIIntegrator:
        def __init__(self, path): pass
        async def initialize(self): pass
        def get_integration_status(self): return {"ai_status": "mock"}

logger = logging.getLogger("MCP.DistributedTestCoordinatorMCP")

class DistributedTestCoordinatorMCP(BaseMCP):
    """分布式测试协调器MCP适配器"""
    
    def __init__(self):
        super().__init__("DistributedTestCoordinatorMCP")
        
        # 核心组件
        self.coordinator = None
        self.smart_scheduler = None
        self.performance_engine = None
        self.test_integrator = None
        self.ai_integrator = None
        
        # 状态管理
        self.is_initialized = False
        self.initialization_time = None
        self.last_health_check = None
        
        # 性能指标
        self.request_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        
        # MCP方法注册
        self.methods = {
            # 核心协调器方法
            "coordinator.initialize": self.initialize_coordinator,
            "coordinator.get_status": self.get_coordinator_status,
            "coordinator.submit_task": self.submit_test_task,
            "coordinator.get_results": self.get_test_results,
            
            # 智能调度方法
            "scheduler.get_insights": self.get_scheduling_insights,
            "scheduler.select_node": self.select_optimal_node,
            "scheduler.get_node_status": self.get_node_status,
            
            # 性能优化方法
            "performance.get_report": self.get_performance_report,
            "performance.optimize_execution": self.optimize_test_execution,
            "performance.get_cache_stats": self.get_cache_statistics,
            
            # 测试架构集成方法
            "architecture.get_capabilities": self.get_test_capabilities,
            "architecture.get_dependencies": self.get_level_dependencies,
            "architecture.validate_architecture": self.validate_test_architecture,
            
            # AI集成方法
            "ai.coordinate_task": self.coordinate_ai_task,
            "ai.get_integration_status": self.get_ai_integration_status,
            
            # 系统管理方法
            "system.health_check": self.health_check,
            "system.get_metrics": self.get_system_metrics,
            "system.restart_components": self.restart_components
        }
        
        logger.info("初始化MCP适配器: DistributedTestCoordinatorMCP")
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """处理MCP请求"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            method = request.method
            params = request.params or {}
            
            if method not in self.methods:
                raise ValueError(f"未知的MCP方法: {method}")
            
            # 执行方法
            result = await self.methods[method](**params)
            
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            logger.info(f"MCP请求成功: {method} ({execution_time:.3f}s)")
            
            return MCPResponse(
                result=result,
                id=request.id
            )
            
        except Exception as e:
            self.error_count += 1
            execution_time = time.time() - start_time
            
            logger.error(f"MCP请求失败: {request.method} - {e}")
            
            return MCPResponse(
                result=None,
                id=request.id,
                error=str(e)
            )
    
    # 核心协调器方法
    
    async def initialize_coordinator(self, powerauto_repo_path: str = "/home/ubuntu/powerauto.ai_0.53") -> Dict[str, Any]:
        """初始化分布式协调器"""
        try:
            logger.info("🚀 初始化分布式测试协调器...")
            
            # 初始化核心组件
            self.coordinator = DistributedTestCoordinator()
            await self.coordinator.initialize()
            
            # 初始化智能调度器
            self.smart_scheduler = SmartSchedulingEngine()
            await self.smart_scheduler.initialize()
            
            # 初始化性能优化引擎
            self.performance_engine = PerformanceOptimizationEngine()
            await self.performance_engine.initialize()
            
            # 初始化测试架构集成器
            self.test_integrator = TestArchitectureIntegrator(powerauto_repo_path)
            await self.test_integrator.initialize()
            
            # 初始化AI集成器
            self.ai_integrator = PowerAutoAIIntegrator(powerauto_repo_path)
            await self.ai_integrator.initialize()
            
            self.is_initialized = True
            self.initialization_time = datetime.now()
            
            logger.info("✅ 分布式测试协调器初始化完成")
            
            return {
                "status": "success",
                "message": "分布式测试协调器初始化完成",
                "initialization_time": self.initialization_time.isoformat(),
                "components": {
                    "coordinator": True,
                    "smart_scheduler": True,
                    "performance_engine": True,
                    "test_integrator": True,
                    "ai_integrator": True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 分布式协调器初始化失败: {e}")
            return {
                "status": "error",
                "message": f"初始化失败: {e}",
                "components": {
                    "coordinator": self.coordinator is not None,
                    "smart_scheduler": self.smart_scheduler is not None,
                    "performance_engine": self.performance_engine is not None,
                    "test_integrator": self.test_integrator is not None,
                    "ai_integrator": self.ai_integrator is not None
                }
            }
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        if not self.is_initialized:
            return {"status": "not_initialized", "message": "协调器未初始化"}
        
        try:
            coordinator_status = await self.coordinator.get_status()
            
            return {
                "status": "active",
                "initialization_time": self.initialization_time.isoformat() if self.initialization_time else None,
                "uptime_seconds": (datetime.now() - self.initialization_time).total_seconds() if self.initialization_time else 0,
                "coordinator_details": coordinator_status,
                "mcp_metrics": {
                    "request_count": self.request_count,
                    "error_count": self.error_count,
                    "error_rate": self.error_count / max(1, self.request_count),
                    "average_response_time": self.total_execution_time / max(1, self.request_count)
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def submit_test_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """提交测试任务"""
        if not self.is_initialized:
            raise ValueError("协调器未初始化")
        
        try:
            # 通过协调器提交任务
            result = await self.coordinator.submit_task(task_data)
            
            return {
                "status": "success",
                "task_id": result.get("task_id"),
                "message": "任务提交成功",
                "estimated_completion": result.get("estimated_completion"),
                "assigned_node": result.get("assigned_node")
            }
            
        except Exception as e:
            logger.error(f"任务提交失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_test_results(self, task_id: str) -> Dict[str, Any]:
        """获取测试结果"""
        if not self.is_initialized:
            raise ValueError("协调器未初始化")
        
        try:
            results = await self.coordinator.get_task_results(task_id)
            return {"status": "success", "results": results}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # 智能调度方法
    
    async def get_scheduling_insights(self) -> Dict[str, Any]:
        """获取调度洞察"""
        if not self.smart_scheduler:
            raise ValueError("智能调度器未初始化")
        
        try:
            insights = await self.smart_scheduler.get_scheduling_insights()
            return {"status": "success", "insights": insights}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def select_optimal_node(self, task_characteristics: Dict[str, Any], available_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """选择最优节点"""
        if not self.smart_scheduler:
            raise ValueError("智能调度器未初始化")
        
        try:
            # 转换数据格式并调用调度器
            from shared_core.engines.distributed_coordinator.smart_scheduler import TaskCharacteristics, NodePerformanceMetrics
            
            task = TaskCharacteristics(**task_characteristics)
            nodes = [NodePerformanceMetrics(**node) for node in available_nodes]
            
            selected_node = await self.smart_scheduler.select_optimal_node(task, nodes)
            
            return {
                "status": "success",
                "selected_node": selected_node,
                "selection_reason": "AI智能调度选择"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_node_status(self) -> Dict[str, Any]:
        """获取节点状态"""
        if not self.coordinator:
            raise ValueError("协调器未初始化")
        
        try:
            node_status = await self.coordinator.get_all_nodes_status()
            return {"status": "success", "nodes": node_status}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # 性能优化方法
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if not self.performance_engine:
            raise ValueError("性能优化引擎未初始化")
        
        try:
            report = self.performance_engine.get_performance_report()
            return {"status": "success", "report": report}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def optimize_test_execution(self, test_tasks: List[Dict[str, Any]], source_files: List[str] = None) -> Dict[str, Any]:
        """优化测试执行"""
        if not self.performance_engine:
            raise ValueError("性能优化引擎未初始化")
        
        try:
            optimized_groups, optimization_report = await self.performance_engine.optimize_test_execution(
                test_tasks, source_files
            )
            
            return {
                "status": "success",
                "optimized_groups": len(optimized_groups),
                "optimization_report": optimization_report
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """获取缓存统计"""
        if not self.performance_engine:
            raise ValueError("性能优化引擎未初始化")
        
        try:
            cache_stats = self.performance_engine.cache.get_stats()
            return {"status": "success", "cache_stats": cache_stats}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # 测试架构集成方法
    
    async def get_test_capabilities(self, test_level: str) -> Dict[str, Any]:
        """获取测试能力"""
        if not self.test_integrator:
            raise ValueError("测试架构集成器未初始化")
        
        try:
            from tests.automated_testing_framework.integrations.test_architecture_integrator import TestLevel
            
            level = TestLevel(test_level)
            capability = self.test_integrator.get_test_capability(level)
            
            if capability:
                return {
                    "status": "success",
                    "capability": {
                        "test_types": list(capability.test_types),
                        "parallel_support": capability.parallel_support,
                        "resource_requirements": capability.required_resources,
                        "execution_patterns": capability.execution_patterns
                    }
                }
            else:
                return {"status": "error", "message": f"未找到测试级别 {test_level} 的能力定义"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_level_dependencies(self, test_level: str) -> Dict[str, Any]:
        """获取级别依赖"""
        if not self.test_integrator:
            raise ValueError("测试架构集成器未初始化")
        
        try:
            from tests.automated_testing_framework.integrations.test_architecture_integrator import TestLevel
            
            level = TestLevel(test_level)
            dependencies = self.test_integrator.get_level_dependencies(level)
            
            return {
                "status": "success",
                "dependencies": [dep.value for dep in dependencies]
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def validate_test_architecture(self) -> Dict[str, Any]:
        """验证测试架构"""
        if not self.test_integrator:
            raise ValueError("测试架构集成器未初始化")
        
        try:
            report = await self.test_integrator.get_integration_report()
            return {"status": "success", "validation_report": report}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # AI集成方法
    
    async def coordinate_ai_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """协调AI任务"""
        if not self.ai_integrator:
            raise ValueError("AI集成器未初始化")
        
        try:
            result = await self.ai_integrator.coordinate_intelligent_task(task_data)
            return {"status": "success", "coordination_result": result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_ai_integration_status(self) -> Dict[str, Any]:
        """获取AI集成状态"""
        if not self.ai_integrator:
            raise ValueError("AI集成器未初始化")
        
        try:
            status = self.ai_integrator.get_integration_status()
            return {"status": "success", "ai_integration": status}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # 系统管理方法
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        self.last_health_check = datetime.now()
        
        health_status = {
            "overall_status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": self.last_health_check.isoformat(),
            "components": {
                "coordinator": self.coordinator is not None,
                "smart_scheduler": self.smart_scheduler is not None,
                "performance_engine": self.performance_engine is not None,
                "test_integrator": self.test_integrator is not None,
                "ai_integrator": self.ai_integrator is not None
            },
            "metrics": {
                "uptime_seconds": (self.last_health_check - self.initialization_time).total_seconds() if self.initialization_time else 0,
                "request_count": self.request_count,
                "error_rate": self.error_count / max(1, self.request_count),
                "average_response_time": self.total_execution_time / max(1, self.request_count)
            }
        }
        
        return health_status
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            import psutil
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent
                },
                "mcp_adapter": {
                    "request_count": self.request_count,
                    "error_count": self.error_count,
                    "error_rate": self.error_count / max(1, self.request_count),
                    "total_execution_time": self.total_execution_time,
                    "average_response_time": self.total_execution_time / max(1, self.request_count)
                }
            }
            
            # 添加组件特定指标
            if self.performance_engine:
                performance_report = self.performance_engine.get_performance_report()
                metrics["performance_engine"] = performance_report.get("optimization_metrics", {})
            
            if self.smart_scheduler:
                scheduling_insights = await self.smart_scheduler.get_scheduling_insights()
                metrics["smart_scheduler"] = {
                    "training_samples": scheduling_insights.get("total_training_samples", 0),
                    "models_trained": scheduling_insights.get("models_trained", {})
                }
            
            return {"status": "success", "metrics": metrics}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def restart_components(self, components: List[str] = None) -> Dict[str, Any]:
        """重启组件"""
        if components is None:
            components = ["all"]
        
        restart_results = {}
        
        try:
            if "all" in components or "coordinator" in components:
                if self.coordinator:
                    await self.coordinator.initialize()
                    restart_results["coordinator"] = "success"
            
            if "all" in components or "smart_scheduler" in components:
                if self.smart_scheduler:
                    await self.smart_scheduler.initialize()
                    restart_results["smart_scheduler"] = "success"
            
            if "all" in components or "performance_engine" in components:
                if self.performance_engine:
                    await self.performance_engine.initialize()
                    restart_results["performance_engine"] = "success"
            
            return {
                "status": "success",
                "message": "组件重启完成",
                "restart_results": restart_results
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

# MCP适配器实例
distributed_coordinator_mcp = DistributedTestCoordinatorMCP()

# 导出
__all__ = ['DistributedTestCoordinatorMCP', 'distributed_coordinator_mcp']

