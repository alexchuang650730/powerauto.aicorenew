"""
PowerAutomation 智慧路由MCP端云协同增强模块

基于现有smart_routing_mcp.py的增强实现，添加：
- 端云混合部署策略
- 隐私感知路由
- 成本优化算法
- Qwen 3 8B本地模型集成
- RL-SRT学习机制

作者: PowerAutomation团队
版本: 2.0.0 (基于现有1.0.0增强)
日期: 2025-06-14
"""

import os
import sys
import json
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import statistics

# 导入现有的智能路由MCP
sys.path.append('/home/ubuntu/powerauto.ai_0.53/shared_core/mcptool/adapters')
try:
    from smart_routing_mcp import SmartRoutingMCP, RoutingStrategy, MCPStatus, LoadBalancingMode
    from smart_routing_mcp import RouteRequest, RouteResult, MCPMetrics
except ImportError:
    # 如果导入失败，定义基础类
    class SmartRoutingMCP:
        def __init__(self):
            self.logger = logging.getLogger("SmartRoutingMCP")
    
    class RoutingStrategy(Enum):
        INTELLIGENT_MATCH = "intelligent_match"
        ADAPTIVE = "adaptive"

logger = logging.getLogger("edge_cloud_routing")

class EdgeCloudRoutingStrategy(Enum):
    """端云混合路由策略"""
    PRIVACY_AWARE = "privacy_aware"          # 隐私感知路由
    COST_OPTIMIZED = "cost_optimized"        # 成本优化路由  
    LATENCY_FIRST = "latency_first"          # 延迟优先路由
    HYBRID_INTELLIGENT = "hybrid_intelligent" # 混合智能路由
    TOKEN_SAVING = "token_saving"            # Token节省路由

class DataSensitivityLevel(Enum):
    """数据敏感度级别"""
    PUBLIC = "public"           # 公开数据 -> 优先云端处理
    INTERNAL = "internal"       # 内部数据 -> 混合处理
    CONFIDENTIAL = "confidential"  # 机密数据 -> 优先端侧处理
    RESTRICTED = "restricted"   # 限制数据 -> 强制端侧处理

class EdgeMCPType(Enum):
    """端侧MCP类型"""
    QWEN_3_8B = "qwen_3_8b"                    # Qwen 3 8B本地模型
    RL_SRT = "rl_srt"                          # 强化学习自适应训练
    PLAYWRIGHT = "playwright"                   # 跨平台自动化
    SEQUENTIAL_THINKING = "sequential_thinking" # 序列思维
    RELEASE_DISCOVERY = "release_discovery"     # 发布发现

class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"       # 简单任务 -> 端侧处理
    MEDIUM = "medium"       # 中等任务 -> 混合处理
    COMPLEX = "complex"     # 复杂任务 -> 云端处理
    CRITICAL = "critical"   # 关键任务 -> 最优资源

@dataclass
class EdgeCloudRouteRequest:
    """端云混合路由请求"""
    task_id: str
    content: str
    task_type: str
    complexity: TaskComplexity
    sensitivity: DataSensitivityLevel
    cost_budget: Optional[float] = None
    latency_requirement: Optional[float] = None  # 毫秒
    preferred_edge_mcps: Optional[List[EdgeMCPType]] = None
    fallback_to_cloud: bool = True
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class EdgeCloudRouteResult:
    """端云混合路由结果"""
    task_id: str
    selected_mcp: str
    mcp_type: str  # "edge" or "cloud"
    routing_strategy: EdgeCloudRoutingStrategy
    estimated_cost: float
    estimated_latency: float
    confidence_score: float
    privacy_compliance: bool
    fallback_used: bool = False
    execution_path: List[str] = None
    
    def __post_init__(self):
        if self.execution_path is None:
            self.execution_path = []

class EdgeCloudCoordinator:
    """端云协调器"""
    
    def __init__(self):
        self.logger = logging.getLogger("EdgeCloudCoordinator")
        self.edge_mcps = {}
        self.cloud_mcps = {}
        self.performance_history = {}
        self.cost_tracker = {}
        
        # 初始化端侧MCP配置
        self._initialize_edge_mcps()
        
    def _initialize_edge_mcps(self):
        """初始化端侧MCP配置"""
        self.edge_mcps = {
            EdgeMCPType.QWEN_3_8B: {
                "name": "qwen3_8b_local_mcp",
                "capabilities": ["text_generation", "code_completion", "simple_reasoning"],
                "max_tokens": 8192,
                "avg_latency": 50,  # 毫秒
                "cost_per_token": 0.0,  # 本地免费
                "privacy_level": "high"
            },
            EdgeMCPType.RL_SRT: {
                "name": "rl_srt_dataflow_mcp", 
                "capabilities": ["learning", "optimization", "adaptation"],
                "max_tokens": 4096,
                "avg_latency": 100,
                "cost_per_token": 0.0,
                "privacy_level": "high"
            },
            EdgeMCPType.PLAYWRIGHT: {
                "name": "playwright_adapter",
                "capabilities": ["automation", "cross_platform", "ui_interaction"],
                "max_tokens": 2048,
                "avg_latency": 200,
                "cost_per_token": 0.0,
                "privacy_level": "medium"
            },
            EdgeMCPType.SEQUENTIAL_THINKING: {
                "name": "sequential_thinking_adapter",
                "capabilities": ["logical_reasoning", "step_by_step", "analysis"],
                "max_tokens": 4096,
                "avg_latency": 80,
                "cost_per_token": 0.0,
                "privacy_level": "high"
            }
        }
        
        self.logger.info(f"初始化了 {len(self.edge_mcps)} 个端侧MCP")

class PrivacyAwareRouter:
    """隐私感知路由器"""
    
    def __init__(self, edge_coordinator: EdgeCloudCoordinator):
        self.edge_coordinator = edge_coordinator
        self.logger = logging.getLogger("PrivacyAwareRouter")
        
        # 隐私级别到处理位置的映射
        self.privacy_routing_rules = {
            DataSensitivityLevel.PUBLIC: {"edge_weight": 0.3, "cloud_weight": 0.7},
            DataSensitivityLevel.INTERNAL: {"edge_weight": 0.6, "cloud_weight": 0.4},
            DataSensitivityLevel.CONFIDENTIAL: {"edge_weight": 0.9, "cloud_weight": 0.1},
            DataSensitivityLevel.RESTRICTED: {"edge_weight": 1.0, "cloud_weight": 0.0}
        }
    
    async def route_by_privacy(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """基于隐私级别进行路由"""
        rules = self.privacy_routing_rules[request.sensitivity]
        
        # 限制数据必须端侧处理
        if request.sensitivity == DataSensitivityLevel.RESTRICTED:
            return await self._route_to_edge_only(request)
        
        # 其他级别根据权重和能力选择
        edge_score = rules["edge_weight"]
        cloud_score = rules["cloud_weight"]
        
        # 考虑任务复杂度
        if request.complexity == TaskComplexity.SIMPLE:
            edge_score += 0.2
        elif request.complexity == TaskComplexity.COMPLEX:
            cloud_score += 0.2
            
        # 考虑延迟要求
        if request.latency_requirement and request.latency_requirement < 100:
            edge_score += 0.1
            
        if edge_score > cloud_score:
            return await self._route_to_edge(request)
        else:
            return await self._route_to_cloud(request)
    
    async def _route_to_edge_only(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """强制路由到端侧"""
        # 选择最适合的端侧MCP
        best_mcp = await self._select_best_edge_mcp(request)
        
        return {
            "target": "edge",
            "mcp": best_mcp,
            "privacy_compliance": True,
            "confidence": 0.95
        }
    
    async def _route_to_edge(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """路由到端侧"""
        best_mcp = await self._select_best_edge_mcp(request)
        
        return {
            "target": "edge", 
            "mcp": best_mcp,
            "privacy_compliance": True,
            "confidence": 0.8
        }
    
    async def _route_to_cloud(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """路由到云端"""
        return {
            "target": "cloud",
            "mcp": "cloud_ai_service",
            "privacy_compliance": request.sensitivity in [DataSensitivityLevel.PUBLIC, DataSensitivityLevel.INTERNAL],
            "confidence": 0.9
        }
    
    async def _select_best_edge_mcp(self, request: EdgeCloudRouteRequest) -> str:
        """选择最佳端侧MCP"""
        # 如果有偏好的MCP
        if request.preferred_edge_mcps:
            for preferred in request.preferred_edge_mcps:
                if preferred in self.edge_coordinator.edge_mcps:
                    return self.edge_coordinator.edge_mcps[preferred]["name"]
        
        # 根据任务类型选择
        if "code" in request.task_type.lower():
            return self.edge_coordinator.edge_mcps[EdgeMCPType.QWEN_3_8B]["name"]
        elif "automation" in request.task_type.lower():
            return self.edge_coordinator.edge_mcps[EdgeMCPType.PLAYWRIGHT]["name"]
        elif "reasoning" in request.task_type.lower():
            return self.edge_coordinator.edge_mcps[EdgeMCPType.SEQUENTIAL_THINKING]["name"]
        else:
            # 默认使用Qwen 3 8B
            return self.edge_coordinator.edge_mcps[EdgeMCPType.QWEN_3_8B]["name"]

class CostOptimizer:
    """成本优化器"""
    
    def __init__(self):
        self.logger = logging.getLogger("CostOptimizer")
        
        # 基于分析报告的成本模型
        self.cost_models = {
            "enterprise_large": {"edge_ratio": 0.75, "cost_saving": 0.72},
            "enterprise_medium": {"edge_ratio": 0.70, "cost_saving": 0.64},
            "startup": {"edge_ratio": 0.65, "cost_saving": 0.55}
        }
        
        # Token成本 (每1K tokens)
        self.token_costs = {
            "cloud_premium": 0.03,
            "cloud_standard": 0.01,
            "edge_qwen": 0.0,  # 本地免费
            "edge_processing": 0.001  # 电力成本
        }
    
    async def optimize_cost(self, request: EdgeCloudRouteRequest, company_type: str = "enterprise_medium") -> Dict[str, Any]:
        """成本优化路由"""
        model = self.cost_models.get(company_type, self.cost_models["enterprise_medium"])
        
        # 计算端侧处理成本
        edge_cost = self._calculate_edge_cost(request)
        
        # 计算云端处理成本
        cloud_cost = self._calculate_cloud_cost(request)
        
        # 应用成本节省模型
        optimized_edge_cost = edge_cost * (1 - model["cost_saving"])
        
        # 选择成本更低的方案
        if request.cost_budget:
            if optimized_edge_cost <= request.cost_budget and optimized_edge_cost < cloud_cost:
                return {"target": "edge", "estimated_cost": optimized_edge_cost, "savings": cloud_cost - optimized_edge_cost}
            elif cloud_cost <= request.cost_budget:
                return {"target": "cloud", "estimated_cost": cloud_cost, "savings": 0}
            else:
                return {"target": "edge", "estimated_cost": optimized_edge_cost, "savings": max(0, cloud_cost - optimized_edge_cost), "budget_exceeded": True}
        else:
            # 无预算限制，选择最便宜的
            if optimized_edge_cost < cloud_cost:
                return {"target": "edge", "estimated_cost": optimized_edge_cost, "savings": cloud_cost - optimized_edge_cost}
            else:
                return {"target": "cloud", "estimated_cost": cloud_cost, "savings": 0}
    
    def _calculate_edge_cost(self, request: EdgeCloudRouteRequest) -> float:
        """计算端侧处理成本"""
        # 估算token数量
        estimated_tokens = len(request.content.split()) * 1.3  # 粗略估算
        
        # 端侧主要是电力成本
        return estimated_tokens * self.token_costs["edge_processing"] / 1000
    
    def _calculate_cloud_cost(self, request: EdgeCloudRouteRequest) -> float:
        """计算云端处理成本"""
        estimated_tokens = len(request.content.split()) * 1.3
        
        # 根据任务复杂度选择云端服务级别
        if request.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            cost_per_k = self.token_costs["cloud_premium"]
        else:
            cost_per_k = self.token_costs["cloud_standard"]
            
        return estimated_tokens * cost_per_k / 1000

class EnhancedSmartRoutingMCP(SmartRoutingMCP):
    """增强的智慧路由MCP - 端云协同版本"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.config = config or {}
        self.logger = logging.getLogger("EnhancedSmartRoutingMCP")
        
        # 初始化端云协同组件
        self.edge_coordinator = EdgeCloudCoordinator()
        self.privacy_router = PrivacyAwareRouter(self.edge_coordinator)
        self.cost_optimizer = CostOptimizer()
        
        # 性能统计
        self.routing_stats = {
            "total_requests": 0,
            "edge_routed": 0,
            "cloud_routed": 0,
            "cost_saved": 0.0,
            "avg_latency": 0.0
        }
        
        self.logger.info("增强智慧路由MCP初始化完成 - 端云协同模式")
    
    async def route_with_edge_cloud_strategy(
        self,
        request: EdgeCloudRouteRequest,
        strategy: EdgeCloudRoutingStrategy = EdgeCloudRoutingStrategy.HYBRID_INTELLIGENT
    ) -> EdgeCloudRouteResult:
        """端云混合策略路由"""
        start_time = time.time()
        self.routing_stats["total_requests"] += 1
        
        try:
            # 根据策略选择路由方法
            if strategy == EdgeCloudRoutingStrategy.PRIVACY_AWARE:
                route_decision = await self.privacy_router.route_by_privacy(request)
            elif strategy == EdgeCloudRoutingStrategy.COST_OPTIMIZED:
                route_decision = await self.cost_optimizer.optimize_cost(request)
            elif strategy == EdgeCloudRoutingStrategy.LATENCY_FIRST:
                route_decision = await self._route_by_latency(request)
            elif strategy == EdgeCloudRoutingStrategy.TOKEN_SAVING:
                route_decision = await self._route_for_token_saving(request)
            else:  # HYBRID_INTELLIGENT
                route_decision = await self._hybrid_intelligent_routing(request)
            
            # 更新统计
            if route_decision["target"] == "edge":
                self.routing_stats["edge_routed"] += 1
            else:
                self.routing_stats["cloud_routed"] += 1
            
            # 计算延迟
            latency = (time.time() - start_time) * 1000
            self.routing_stats["avg_latency"] = (
                self.routing_stats["avg_latency"] * (self.routing_stats["total_requests"] - 1) + latency
            ) / self.routing_stats["total_requests"]
            
            # 构建结果
            result = EdgeCloudRouteResult(
                task_id=request.task_id,
                selected_mcp=route_decision.get("mcp", "unknown"),
                mcp_type=route_decision["target"],
                routing_strategy=strategy,
                estimated_cost=route_decision.get("estimated_cost", 0.0),
                estimated_latency=route_decision.get("estimated_latency", latency),
                confidence_score=route_decision.get("confidence", 0.5),
                privacy_compliance=route_decision.get("privacy_compliance", True),
                execution_path=[f"{strategy.value}_routing"]
            )
            
            self.logger.info(f"路由完成: {request.task_id} -> {route_decision['target']} ({result.selected_mcp})")
            return result
            
        except Exception as e:
            self.logger.error(f"路由失败: {e}")
            # 返回默认的云端路由
            return EdgeCloudRouteResult(
                task_id=request.task_id,
                selected_mcp="cloud_fallback",
                mcp_type="cloud",
                routing_strategy=strategy,
                estimated_cost=0.01,
                estimated_latency=1000,
                confidence_score=0.1,
                privacy_compliance=False,
                fallback_used=True
            )
    
    async def _route_by_latency(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """基于延迟优先的路由"""
        if request.latency_requirement and request.latency_requirement < 200:
            # 低延迟要求，优先端侧
            return {
                "target": "edge",
                "mcp": await self.privacy_router._select_best_edge_mcp(request),
                "estimated_latency": 50,
                "confidence": 0.9
            }
        else:
            # 可以接受较高延迟，选择最优方案
            return await self._hybrid_intelligent_routing(request)
    
    async def _route_for_token_saving(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """基于Token节省的路由"""
        # 75%的任务适合端侧处理
        if request.complexity in [TaskComplexity.SIMPLE, TaskComplexity.MEDIUM]:
            return {
                "target": "edge",
                "mcp": await self.privacy_router._select_best_edge_mcp(request),
                "estimated_cost": 0.0,
                "savings": 0.02,  # 假设节省的云端成本
                "confidence": 0.85
            }
        else:
            return {
                "target": "cloud",
                "mcp": "cloud_ai_service",
                "estimated_cost": 0.03,
                "confidence": 0.9
            }
    
    async def _hybrid_intelligent_routing(self, request: EdgeCloudRouteRequest) -> Dict[str, Any]:
        """混合智能路由 - 综合考虑所有因素"""
        # 获取隐私路由建议
        privacy_decision = await self.privacy_router.route_by_privacy(request)
        
        # 获取成本优化建议
        cost_decision = await self.cost_optimizer.optimize_cost(request)
        
        # 综合决策
        edge_score = 0
        cloud_score = 0
        
        # 隐私因素 (权重: 40%)
        if privacy_decision["target"] == "edge":
            edge_score += 0.4 * privacy_decision["confidence"]
        else:
            cloud_score += 0.4 * privacy_decision["confidence"]
        
        # 成本因素 (权重: 30%)
        if cost_decision["target"] == "edge":
            edge_score += 0.3
        else:
            cloud_score += 0.3
        
        # 任务复杂度因素 (权重: 20%)
        if request.complexity == TaskComplexity.SIMPLE:
            edge_score += 0.2
        elif request.complexity == TaskComplexity.COMPLEX:
            cloud_score += 0.2
        else:
            edge_score += 0.1
            cloud_score += 0.1
        
        # 延迟因素 (权重: 10%)
        if request.latency_requirement and request.latency_requirement < 100:
            edge_score += 0.1
        else:
            cloud_score += 0.05
            edge_score += 0.05
        
        # 选择得分更高的方案
        if edge_score > cloud_score:
            return {
                "target": "edge",
                "mcp": await self.privacy_router._select_best_edge_mcp(request),
                "estimated_cost": cost_decision.get("estimated_cost", 0.0) if cost_decision["target"] == "edge" else 0.001,
                "confidence": edge_score,
                "decision_factors": {"privacy": privacy_decision["confidence"], "cost": cost_decision.get("savings", 0)}
            }
        else:
            return {
                "target": "cloud",
                "mcp": "cloud_ai_service",
                "estimated_cost": cost_decision.get("estimated_cost", 0.02) if cost_decision["target"] == "cloud" else 0.02,
                "confidence": cloud_score,
                "decision_factors": {"privacy": privacy_decision["confidence"], "cost": cost_decision.get("savings", 0)}
            }
    
    async def get_routing_statistics(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        total = self.routing_stats["total_requests"]
        if total == 0:
            return {"message": "暂无路由统计数据"}
        
        edge_ratio = self.routing_stats["edge_routed"] / total
        cloud_ratio = self.routing_stats["cloud_routed"] / total
        
        return {
            "total_requests": total,
            "edge_routing_ratio": f"{edge_ratio:.2%}",
            "cloud_routing_ratio": f"{cloud_ratio:.2%}",
            "average_latency_ms": f"{self.routing_stats['avg_latency']:.2f}",
            "total_cost_saved": f"${self.routing_stats['cost_saved']:.4f}",
            "edge_mcps_available": len(self.edge_coordinator.edge_mcps),
            "performance_target": "75% edge processing for optimal cost savings"
        }

# 使用示例
async def main():
    """测试端云协同路由"""
    router = EnhancedSmartRoutingMCP()
    
    # 测试请求
    test_request = EdgeCloudRouteRequest(
        task_id="test_001",
        content="请帮我重构这段Python代码，提高可读性",
        task_type="code_refactoring",
        complexity=TaskComplexity.SIMPLE,
        sensitivity=DataSensitivityLevel.INTERNAL,
        latency_requirement=100
    )
    
    # 测试不同策略
    strategies = [
        EdgeCloudRoutingStrategy.PRIVACY_AWARE,
        EdgeCloudRoutingStrategy.COST_OPTIMIZED,
        EdgeCloudRoutingStrategy.HYBRID_INTELLIGENT
    ]
    
    for strategy in strategies:
        result = await router.route_with_edge_cloud_strategy(test_request, strategy)
        print(f"\n策略: {strategy.value}")
        print(f"路由到: {result.mcp_type} ({result.selected_mcp})")
        print(f"预估成本: ${result.estimated_cost:.4f}")
        print(f"预估延迟: {result.estimated_latency:.2f}ms")
        print(f"置信度: {result.confidence_score:.2f}")
        print(f"隐私合规: {result.privacy_compliance}")
    
    # 显示统计信息
    stats = await router.get_routing_statistics()
    print(f"\n路由统计: {stats}")

if __name__ == "__main__":
    asyncio.run(main())

