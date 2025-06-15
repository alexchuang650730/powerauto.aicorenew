#!/usr/bin/env python3
"""
智慧路由MCP適配器

實現智能請求路由和負載均衡功能，包括：
- 多策略智能路由引擎
- 動態負載均衡
- 故障檢測和自動恢復
- 性能監控和優化
- 路由策略管理

作者: PowerAutomation團隊
版本: 1.0.0
日期: 2025-06-08
"""

import os
import sys
import json
import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import statistics

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 導入基礎MCP
try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子類必須實現此方法")

# 導入MCP註冊表管理器
try:
    from mcptool.adapters.mcp_registry_integration_manager import MCPRegistryIntegrationManager
except ImportError:
    class MCPRegistryIntegrationManager:
        def __init__(self):
            self.adapter_registry = type('obj', (object,), {'registered_adapters': {}})()
        
        async def match_intent_to_mcp(self, *args, **kwargs):
            return {"status": "mock", "matched_mcps": []}

# 導入標準化日誌系統
try:
    from standardized_logging_system import log_info, log_error, log_warning, LogCategory, performance_monitor
except ImportError:
    def log_info(category, message, data=None): pass
    def log_error(category, message, data=None): pass
    def log_warning(category, message, data=None): pass
    def performance_monitor(name): 
        def decorator(func): return func
        return decorator
    class LogCategory:
        SYSTEM = "system"
        MEMORY = "memory"
        MCP = "mcp"

logger = logging.getLogger("smart_routing_mcp")

class RoutingStrategy(Enum):
    """路由策略枚舉"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    FASTEST_RESPONSE = "fastest_response"
    INTELLIGENT_MATCH = "intelligent_match"
    RANDOM = "random"
    HASH_BASED = "hash_based"
    ADAPTIVE = "adaptive"

class MCPStatus(Enum):
    """MCP狀態枚舉"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class LoadBalancingMode(Enum):
    """負載均衡模式枚舉"""
    ACTIVE_ACTIVE = "active_active"
    ACTIVE_PASSIVE = "active_passive"
    WEIGHTED_ACTIVE = "weighted_active"
    CIRCUIT_BREAKER = "circuit_breaker"

@dataclass
class MCPNode:
    """MCP節點信息"""
    mcp_id: str
    name: str
    endpoint: str
    status: MCPStatus
    weight: float = 1.0
    current_connections: int = 0
    max_connections: int = 100
    response_time_avg: float = 0.0
    success_rate: float = 1.0
    last_health_check: str = ""
    capabilities: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}
        if not self.last_health_check:
            self.last_health_check = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPNode':
        """從字典創建實例"""
        data['status'] = MCPStatus(data['status'])
        return cls(**data)

@dataclass
class RoutingRequest:
    """路由請求信息"""
    request_id: str
    user_intent: str
    operation: str
    params: Dict[str, Any]
    priority: str = "medium"
    timeout: float = 30.0
    retry_count: int = 3
    context: Dict[str, Any] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class RoutingResult:
    """路由結果信息"""
    request_id: str
    selected_mcp: str
    routing_strategy: str
    execution_time: float
    success: bool
    response: Dict[str, Any]
    error_message: str = ""
    retry_attempts: int = 0
    fallback_used: bool = False
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class SmartRoutingMCP(BaseMCP):
    """智慧路由MCP適配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("SmartRoutingMCP")
        
        # 配置參數
        self.config = config or {}
        self.default_strategy = RoutingStrategy(self.config.get("default_strategy", "intelligent_match"))
        self.load_balancing_mode = LoadBalancingMode(self.config.get("load_balancing_mode", "active_active"))
        self.health_check_interval = self.config.get("health_check_interval", 30)  # 秒
        self.circuit_breaker_threshold = self.config.get("circuit_breaker_threshold", 0.5)
        self.max_retry_attempts = self.config.get("max_retry_attempts", 3)
        
        # 初始化組件
        self.registry_manager = MCPRegistryIntegrationManager()
        
        # MCP節點管理
        self.mcp_nodes = {}
        self.routing_table = {}
        
        # 路由統計
        self.routing_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "average_response_time": 0.0,
            "strategy_usage": {strategy.value: 0 for strategy in RoutingStrategy},
            "mcp_usage": {},
            "error_counts": {}
        }
        
        # 性能監控
        self.performance_metrics = {}
        self.health_check_results = {}
        
        # 路由歷史
        self.routing_history = []
        self.max_history_size = self.config.get("max_history_size", 1000)
        
        # 異步任務
        self.health_check_task = None
        self.monitoring_active = False
        
        # 路由策略映射
        self.routing_strategies = {
            RoutingStrategy.ROUND_ROBIN: self._round_robin_routing,
            RoutingStrategy.WEIGHTED: self._weighted_routing,
            RoutingStrategy.LEAST_CONNECTIONS: self._least_connections_routing,
            RoutingStrategy.FASTEST_RESPONSE: self._fastest_response_routing,
            RoutingStrategy.INTELLIGENT_MATCH: self._intelligent_match_routing,
            RoutingStrategy.RANDOM: self._random_routing,
            RoutingStrategy.HASH_BASED: self._hash_based_routing,
            RoutingStrategy.ADAPTIVE: self._adaptive_routing
        }
        
        # MCP操作映射
        self.operations = {
            "route_request": self.route_request,
            "add_mcp_node": self.add_mcp_node,
            "remove_mcp_node": self.remove_mcp_node,
            "update_mcp_status": self.update_mcp_status,
            "get_routing_stats": self.get_routing_stats,
            "get_mcp_nodes": self.get_mcp_nodes,
            "set_routing_strategy": self.set_routing_strategy,
            "start_health_monitoring": self.start_health_monitoring,
            "stop_health_monitoring": self.stop_health_monitoring,
            "get_performance_metrics": self.get_performance_metrics,
            "optimize_routing": self.optimize_routing,
            "export_routing_data": self.export_routing_data,
            "reset_stats": self.reset_routing_stats
        }
        
        # 初始化系統
        self._initialize_routing_system()
        
        log_info(LogCategory.MCP, "智慧路由MCP初始化完成", {
            "default_strategy": self.default_strategy.value,
            "load_balancing_mode": self.load_balancing_mode.value,
            "operations": list(self.operations.keys())
        })
    
    def _initialize_routing_system(self):
        """初始化路由系統"""
        try:
            # 從註冊表加載MCP節點
            self._load_mcp_nodes_from_registry()
            
            # 初始化路由表
            self._build_routing_table()
            
            # 啟動健康檢查
            asyncio.create_task(self._start_background_tasks())
            
            log_info(LogCategory.MCP, "路由系統初始化完成", {
                "mcp_nodes": len(self.mcp_nodes),
                "routing_entries": len(self.routing_table)
            })
            
        except Exception as e:
            log_error(LogCategory.MCP, "路由系統初始化失敗", {"error": str(e)})
    
    def _load_mcp_nodes_from_registry(self):
        """從註冊表加載MCP節點"""
        try:
            registered_mcps = self.registry_manager.adapter_registry.registered_adapters
            
            for mcp_id, mcp_info in registered_mcps.items():
                node = MCPNode(
                    mcp_id=mcp_id,
                    name=mcp_info.get("name", mcp_id),
                    endpoint=f"mcp://{mcp_id}",
                    status=MCPStatus.HEALTHY if mcp_info.get("status") == "active" else MCPStatus.OFFLINE,
                    capabilities=mcp_info.get("capabilities", []),
                    metadata=mcp_info
                )
                
                self.mcp_nodes[mcp_id] = node
                self.routing_stats["mcp_usage"][mcp_id] = 0
            
            log_info(LogCategory.MCP, f"從註冊表加載了 {len(self.mcp_nodes)} 個MCP節點", {})
            
        except Exception as e:
            log_error(LogCategory.MCP, "從註冊表加載MCP節點失敗", {"error": str(e)})
    
    def _build_routing_table(self):
        """構建路由表"""
        try:
            self.routing_table.clear()
            
            # 基於能力構建路由表
            for mcp_id, node in self.mcp_nodes.items():
                for capability in node.capabilities:
                    if capability not in self.routing_table:
                        self.routing_table[capability] = []
                    self.routing_table[capability].append(mcp_id)
            
            log_info(LogCategory.MCP, "路由表構建完成", {
                "capabilities": len(self.routing_table),
                "total_routes": sum(len(mcps) for mcps in self.routing_table.values())
            })
            
        except Exception as e:
            log_error(LogCategory.MCP, "路由表構建失敗", {"error": str(e)})
    
    async def _start_background_tasks(self):
        """啟動後台任務"""
        try:
            # 啟動健康檢查
            await self.start_health_monitoring()
            
        except Exception as e:
            log_error(LogCategory.MCP, "後台任務啟動失敗", {"error": str(e)})
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP標準處理接口"""
        try:
            operation = input_data.get("operation", "route_request")
            params = input_data.get("params", {})
            
            if operation not in self.operations:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {operation}",
                    "available_operations": list(self.operations.keys())
                }
            
            # 執行對應操作
            if asyncio.iscoroutinefunction(self.operations[operation]):
                # 異步操作
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.operations[operation](**params))
            else:
                # 同步操作
                result = self.operations[operation](**params)
            
            log_info(LogCategory.MCP, f"智慧路由MCP操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "智慧路由MCP處理失敗", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"處理失敗: {str(e)}"
            }
    
    @performance_monitor("route_request")
    async def route_request(self, user_intent: str, operation: str, params: Dict[str, Any] = None, 
                           strategy: str = None, priority: str = "medium") -> Dict[str, Any]:
        """路由請求到最適合的MCP"""
        try:
            start_time = time.time()
            
            # 創建路由請求
            request = RoutingRequest(
                request_id=self._generate_request_id(),
                user_intent=user_intent,
                operation=operation,
                params=params or {},
                priority=priority
            )
            
            # 確定路由策略
            routing_strategy = RoutingStrategy(strategy) if strategy else self.default_strategy
            
            # 執行路由選擇
            selected_mcp = await self._select_mcp(request, routing_strategy)
            
            if not selected_mcp:
                return {
                    "status": "error",
                    "message": "沒有可用的MCP節點",
                    "request_id": request.request_id
                }
            
            # 執行請求
            execution_result = await self._execute_request(selected_mcp, request)
            
            # 計算執行時間
            execution_time = time.time() - start_time
            
            # 創建路由結果
            result = RoutingResult(
                request_id=request.request_id,
                selected_mcp=selected_mcp,
                routing_strategy=routing_strategy.value,
                execution_time=execution_time,
                success=execution_result.get("status") == "success",
                response=execution_result
            )
            
            # 更新統計和性能指標
            self._update_routing_stats(result)
            self._update_performance_metrics(selected_mcp, execution_time, result.success)
            
            # 記錄路由歷史
            self._record_routing_history(result)
            
            return {
                "status": "success",
                "request_id": request.request_id,
                "selected_mcp": selected_mcp,
                "routing_strategy": routing_strategy.value,
                "execution_time": execution_time,
                "response": execution_result
            }
            
        except Exception as e:
            self.routing_stats["failed_routes"] += 1
            return {
                "status": "error",
                "message": f"路由請求失敗: {str(e)}",
                "request_id": getattr(request, 'request_id', 'unknown')
            }
    
    def _generate_request_id(self) -> str:
        """生成請求ID"""
        import uuid
        return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    async def _select_mcp(self, request: RoutingRequest, strategy: RoutingStrategy) -> Optional[str]:
        """選擇MCP節點"""
        try:
            # 獲取候選MCP列表
            candidates = await self._get_candidate_mcps(request)
            
            if not candidates:
                return None
            
            # 過濾健康的MCP
            healthy_candidates = [mcp_id for mcp_id in candidates 
                                if self.mcp_nodes[mcp_id].status in [MCPStatus.HEALTHY, MCPStatus.DEGRADED]]
            
            if not healthy_candidates:
                log_warning(LogCategory.MCP, "沒有健康的候選MCP", {
                    "total_candidates": len(candidates),
                    "request_id": request.request_id
                })
                return None
            
            # 應用路由策略
            selected_mcp = await self.routing_strategies[strategy](healthy_candidates, request)
            
            # 更新策略使用統計
            self.routing_stats["strategy_usage"][strategy.value] += 1
            
            return selected_mcp
            
        except Exception as e:
            log_error(LogCategory.MCP, "MCP選擇失敗", {
                "strategy": strategy.value,
                "error": str(e)
            })
            return None
    
    async def _get_candidate_mcps(self, request: RoutingRequest) -> List[str]:
        """獲取候選MCP列表"""
        try:
            # 使用意圖匹配獲取候選MCP
            match_result = await self.registry_manager.match_intent_to_mcp(
                user_intent=request.user_intent,
                context=request.context
            )
            
            if match_result.get("status") == "success":
                matched_mcps = match_result.get("matched_mcps", [])
                return [mcp["mcp_id"] for mcp in matched_mcps]
            else:
                # 備用方案：返回所有可用的MCP
                return list(self.mcp_nodes.keys())
                
        except Exception as e:
            log_error(LogCategory.MCP, "獲取候選MCP失敗", {"error": str(e)})
            return list(self.mcp_nodes.keys())
    
    async def _round_robin_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """輪詢路由策略"""
        if not hasattr(self, '_round_robin_index'):
            self._round_robin_index = 0
        
        selected = candidates[self._round_robin_index % len(candidates)]
        self._round_robin_index += 1
        
        return selected
    
    async def _weighted_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """加權路由策略"""
        weights = []
        for mcp_id in candidates:
            node = self.mcp_nodes[mcp_id]
            # 基於權重和成功率計算總權重
            total_weight = node.weight * node.success_rate
            weights.append(total_weight)
        
        # 加權隨機選擇
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(candidates)
        
        random_value = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return candidates[i]
        
        return candidates[-1]
    
    async def _least_connections_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """最少連接路由策略"""
        min_connections = float('inf')
        selected_mcp = candidates[0]
        
        for mcp_id in candidates:
            node = self.mcp_nodes[mcp_id]
            if node.current_connections < min_connections:
                min_connections = node.current_connections
                selected_mcp = mcp_id
        
        return selected_mcp
    
    async def _fastest_response_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """最快響應路由策略"""
        fastest_time = float('inf')
        selected_mcp = candidates[0]
        
        for mcp_id in candidates:
            node = self.mcp_nodes[mcp_id]
            if node.response_time_avg < fastest_time:
                fastest_time = node.response_time_avg
                selected_mcp = mcp_id
        
        return selected_mcp
    
    async def _intelligent_match_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """智能匹配路由策略"""
        try:
            # 使用註冊表管理器的意圖匹配
            match_result = await self.registry_manager.match_intent_to_mcp(
                user_intent=request.user_intent,
                context=request.context
            )
            
            if match_result.get("status") == "success":
                matched_mcps = match_result.get("matched_mcps", [])
                if matched_mcps:
                    # 選擇匹配分數最高的MCP
                    best_match = matched_mcps[0]
                    return best_match["mcp_id"]
            
            # 備用方案：使用加權路由
            return await self._weighted_routing(candidates, request)
            
        except Exception as e:
            log_error(LogCategory.MCP, "智能匹配路由失敗", {"error": str(e)})
            return await self._weighted_routing(candidates, request)
    
    async def _random_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """隨機路由策略"""
        return random.choice(candidates)
    
    async def _hash_based_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """基於哈希的路由策略"""
        # 基於請求ID的哈希值選擇MCP
        hash_value = hash(request.request_id) % len(candidates)
        return candidates[hash_value]
    
    async def _adaptive_routing(self, candidates: List[str], request: RoutingRequest) -> str:
        """自適應路由策略"""
        # 根據當前系統狀態選擇最佳策略
        
        # 計算系統負載
        total_connections = sum(node.current_connections for node in self.mcp_nodes.values())
        avg_response_time = statistics.mean([node.response_time_avg for node in self.mcp_nodes.values() if node.response_time_avg > 0]) or 0
        
        # 根據系統狀態選擇策略
        if total_connections > len(self.mcp_nodes) * 50:  # 高負載
            return await self._least_connections_routing(candidates, request)
        elif avg_response_time > 5.0:  # 響應時間較慢
            return await self._fastest_response_routing(candidates, request)
        else:  # 正常情況
            return await self._intelligent_match_routing(candidates, request)
    
    async def _execute_request(self, mcp_id: str, request: RoutingRequest) -> Dict[str, Any]:
        """執行請求"""
        try:
            # 更新連接計數
            self.mcp_nodes[mcp_id].current_connections += 1
            
            # 模擬MCP執行（實際實現中需要調用真實的MCP）
            execution_result = await self._simulate_mcp_execution(mcp_id, request)
            
            return execution_result
            
        except Exception as e:
            log_error(LogCategory.MCP, f"執行請求失敗: {mcp_id}", {
                "request_id": request.request_id,
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"執行失敗: {str(e)}"
            }
        finally:
            # 減少連接計數
            if mcp_id in self.mcp_nodes:
                self.mcp_nodes[mcp_id].current_connections = max(0, self.mcp_nodes[mcp_id].current_connections - 1)
    
    async def _simulate_mcp_execution(self, mcp_id: str, request: RoutingRequest) -> Dict[str, Any]:
        """模擬MCP執行（實際實現中需要替換為真實的MCP調用）"""
        # 模擬執行時間
        execution_time = random.uniform(0.1, 2.0)
        await asyncio.sleep(execution_time)
        
        # 模擬成功率
        node = self.mcp_nodes[mcp_id]
        success_probability = node.success_rate
        
        if random.random() < success_probability:
            return {
                "status": "success",
                "result": f"MCP {mcp_id} 執行成功",
                "execution_time": execution_time,
                "mcp_id": mcp_id
            }
        else:
            return {
                "status": "error",
                "message": f"MCP {mcp_id} 執行失敗",
                "execution_time": execution_time,
                "mcp_id": mcp_id
            }
    
    def _update_routing_stats(self, result: RoutingResult):
        """更新路由統計"""
        self.routing_stats["total_requests"] += 1
        
        if result.success:
            self.routing_stats["successful_routes"] += 1
        else:
            self.routing_stats["failed_routes"] += 1
        
        # 更新平均響應時間
        total_requests = self.routing_stats["total_requests"]
        current_avg = self.routing_stats["average_response_time"]
        self.routing_stats["average_response_time"] = (
            (current_avg * (total_requests - 1) + result.execution_time) / total_requests
        )
        
        # 更新MCP使用統計
        self.routing_stats["mcp_usage"][result.selected_mcp] += 1
    
    def _update_performance_metrics(self, mcp_id: str, execution_time: float, success: bool):
        """更新性能指標"""
        node = self.mcp_nodes[mcp_id]
        
        # 更新響應時間
        if node.response_time_avg == 0:
            node.response_time_avg = execution_time
        else:
            # 使用指數移動平均
            alpha = 0.1
            node.response_time_avg = alpha * execution_time + (1 - alpha) * node.response_time_avg
        
        # 更新成功率
        if mcp_id not in self.performance_metrics:
            self.performance_metrics[mcp_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "response_times": []
            }
        
        metrics = self.performance_metrics[mcp_id]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
        
        metrics["response_times"].append(execution_time)
        
        # 保持響應時間歷史在合理範圍內
        if len(metrics["response_times"]) > 100:
            metrics["response_times"] = metrics["response_times"][-100:]
        
        # 更新成功率
        node.success_rate = metrics["successful_requests"] / metrics["total_requests"]
    
    def _record_routing_history(self, result: RoutingResult):
        """記錄路由歷史"""
        self.routing_history.append(result.to_dict() if hasattr(result, 'to_dict') else asdict(result))
        
        # 保持歷史記錄在合理範圍內
        if len(self.routing_history) > self.max_history_size:
            self.routing_history = self.routing_history[-self.max_history_size:]
    
    async def add_mcp_node(self, mcp_info: Dict[str, Any]) -> Dict[str, Any]:
        """添加MCP節點"""
        try:
            node = MCPNode.from_dict(mcp_info)
            self.mcp_nodes[node.mcp_id] = node
            self.routing_stats["mcp_usage"][node.mcp_id] = 0
            
            # 重建路由表
            self._build_routing_table()
            
            log_info(LogCategory.MCP, f"添加MCP節點: {node.mcp_id}", {
                "name": node.name,
                "capabilities": len(node.capabilities)
            })
            
            return {
                "status": "success",
                "message": f"MCP節點添加成功: {node.mcp_id}",
                "node_info": node.to_dict()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"添加MCP節點失敗: {str(e)}"
            }
    
    async def remove_mcp_node(self, mcp_id: str) -> Dict[str, Any]:
        """移除MCP節點"""
        try:
            if mcp_id not in self.mcp_nodes:
                return {
                    "status": "error",
                    "message": f"MCP節點不存在: {mcp_id}"
                }
            
            # 移除節點
            removed_node = self.mcp_nodes.pop(mcp_id)
            
            # 清理統計數據
            if mcp_id in self.routing_stats["mcp_usage"]:
                del self.routing_stats["mcp_usage"][mcp_id]
            if mcp_id in self.performance_metrics:
                del self.performance_metrics[mcp_id]
            
            # 重建路由表
            self._build_routing_table()
            
            log_info(LogCategory.MCP, f"移除MCP節點: {mcp_id}", {})
            
            return {
                "status": "success",
                "message": f"MCP節點移除成功: {mcp_id}",
                "removed_node": removed_node.to_dict()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"移除MCP節點失敗: {str(e)}"
            }
    
    async def update_mcp_status(self, mcp_id: str, status: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """更新MCP狀態"""
        try:
            if mcp_id not in self.mcp_nodes:
                return {
                    "status": "error",
                    "message": f"MCP節點不存在: {mcp_id}"
                }
            
            node = self.mcp_nodes[mcp_id]
            old_status = node.status
            node.status = MCPStatus(status)
            node.last_health_check = datetime.now().isoformat()
            
            if metadata:
                node.metadata.update(metadata)
            
            log_info(LogCategory.MCP, f"更新MCP狀態: {mcp_id}", {
                "old_status": old_status.value,
                "new_status": status
            })
            
            return {
                "status": "success",
                "message": f"MCP狀態更新成功: {mcp_id}",
                "old_status": old_status.value,
                "new_status": status
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"更新MCP狀態失敗: {str(e)}"
            }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """獲取路由統計"""
        return {
            "status": "success",
            "routing_stats": self.routing_stats.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_mcp_nodes(self, status_filter: str = None) -> Dict[str, Any]:
        """獲取MCP節點信息"""
        try:
            nodes = []
            
            for mcp_id, node in self.mcp_nodes.items():
                if status_filter and node.status.value != status_filter:
                    continue
                
                nodes.append(node.to_dict())
            
            return {
                "status": "success",
                "mcp_nodes": nodes,
                "total_nodes": len(nodes),
                "filter_applied": status_filter
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取MCP節點失敗: {str(e)}"
            }
    
    def set_routing_strategy(self, strategy: str) -> Dict[str, Any]:
        """設置路由策略"""
        try:
            old_strategy = self.default_strategy
            self.default_strategy = RoutingStrategy(strategy)
            
            log_info(LogCategory.MCP, "路由策略已更新", {
                "old_strategy": old_strategy.value,
                "new_strategy": strategy
            })
            
            return {
                "status": "success",
                "message": "路由策略更新成功",
                "old_strategy": old_strategy.value,
                "new_strategy": strategy
            }
            
        except ValueError:
            return {
                "status": "error",
                "message": f"無效的路由策略: {strategy}",
                "available_strategies": [s.value for s in RoutingStrategy]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"設置路由策略失敗: {str(e)}"
            }
    
    async def start_health_monitoring(self) -> Dict[str, Any]:
        """開始健康監控"""
        try:
            if self.monitoring_active:
                return {
                    "status": "warning",
                    "message": "健康監控已在運行中"
                }
            
            self.monitoring_active = True
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            log_info(LogCategory.MCP, "健康監控已啟動", {
                "check_interval": self.health_check_interval
            })
            
            return {
                "status": "success",
                "message": "健康監控已啟動",
                "check_interval": self.health_check_interval
            }
            
        except Exception as e:
            self.monitoring_active = False
            return {
                "status": "error",
                "message": f"啟動健康監控失敗: {str(e)}"
            }
    
    async def stop_health_monitoring(self) -> Dict[str, Any]:
        """停止健康監控"""
        try:
            if not self.monitoring_active:
                return {
                    "status": "warning",
                    "message": "健康監控未在運行"
                }
            
            self.monitoring_active = False
            
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
                self.health_check_task = None
            
            log_info(LogCategory.MCP, "健康監控已停止", {})
            
            return {
                "status": "success",
                "message": "健康監控已停止"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"停止健康監控失敗: {str(e)}"
            }
    
    async def _health_check_loop(self):
        """健康檢查循環"""
        try:
            log_info(LogCategory.MCP, "健康檢查循環開始", {})
            
            while self.monitoring_active:
                # 執行健康檢查
                await self._perform_health_checks()
                
                # 等待下次檢查
                await asyncio.sleep(self.health_check_interval)
                
        except Exception as e:
            log_error(LogCategory.MCP, "健康檢查循環異常", {"error": str(e)})
        finally:
            self.monitoring_active = False
            log_info(LogCategory.MCP, "健康檢查循環結束", {})
    
    async def _perform_health_checks(self):
        """執行健康檢查"""
        try:
            for mcp_id, node in self.mcp_nodes.items():
                health_result = await self._check_mcp_health(mcp_id, node)
                self.health_check_results[mcp_id] = health_result
                
                # 根據健康檢查結果更新狀態
                if health_result["healthy"]:
                    if node.status == MCPStatus.UNHEALTHY:
                        node.status = MCPStatus.HEALTHY
                        log_info(LogCategory.MCP, f"MCP恢復健康: {mcp_id}", {})
                else:
                    if node.status == MCPStatus.HEALTHY:
                        node.status = MCPStatus.UNHEALTHY
                        log_warning(LogCategory.MCP, f"MCP變為不健康: {mcp_id}", {
                            "reason": health_result.get("reason", "未知")
                        })
                
                node.last_health_check = datetime.now().isoformat()
            
        except Exception as e:
            log_error(LogCategory.MCP, "執行健康檢查失敗", {"error": str(e)})
    
    async def _check_mcp_health(self, mcp_id: str, node: MCPNode) -> Dict[str, Any]:
        """檢查MCP健康狀態"""
        try:
            # 模擬健康檢查（實際實現中需要調用真實的健康檢查接口）
            health_check_time = random.uniform(0.1, 0.5)
            await asyncio.sleep(health_check_time)
            
            # 模擬健康狀態（基於成功率）
            is_healthy = random.random() < node.success_rate
            
            return {
                "healthy": is_healthy,
                "response_time": health_check_time,
                "timestamp": datetime.now().isoformat(),
                "reason": "健康檢查通過" if is_healthy else "響應異常"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "response_time": 0,
                "timestamp": datetime.now().isoformat(),
                "reason": f"健康檢查失敗: {str(e)}"
            }
    
    def get_performance_metrics(self, mcp_id: str = None) -> Dict[str, Any]:
        """獲取性能指標"""
        try:
            if mcp_id:
                # 獲取特定MCP的性能指標
                if mcp_id not in self.performance_metrics:
                    return {
                        "status": "error",
                        "message": f"MCP性能指標不存在: {mcp_id}"
                    }
                
                metrics = self.performance_metrics[mcp_id].copy()
                node = self.mcp_nodes[mcp_id]
                
                # 計算統計信息
                if metrics["response_times"]:
                    metrics["avg_response_time"] = statistics.mean(metrics["response_times"])
                    metrics["min_response_time"] = min(metrics["response_times"])
                    metrics["max_response_time"] = max(metrics["response_times"])
                    metrics["median_response_time"] = statistics.median(metrics["response_times"])
                
                metrics["success_rate"] = node.success_rate
                metrics["current_connections"] = node.current_connections
                
                return {
                    "status": "success",
                    "mcp_id": mcp_id,
                    "metrics": metrics
                }
            else:
                # 獲取所有MCP的性能概覽
                overview = {}
                for mcp_id, metrics in self.performance_metrics.items():
                    node = self.mcp_nodes[mcp_id]
                    overview[mcp_id] = {
                        "total_requests": metrics["total_requests"],
                        "success_rate": node.success_rate,
                        "avg_response_time": node.response_time_avg,
                        "current_connections": node.current_connections,
                        "status": node.status.value
                    }
                
                return {
                    "status": "success",
                    "performance_overview": overview,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取性能指標失敗: {str(e)}"
            }
    
    async def optimize_routing(self, optimization_type: str = "auto") -> Dict[str, Any]:
        """優化路由"""
        try:
            optimization_results = []
            
            if optimization_type in ["auto", "weights"]:
                # 優化權重
                weight_result = await self._optimize_weights()
                optimization_results.append({"type": "weights", "result": weight_result})
            
            if optimization_type in ["auto", "strategy"]:
                # 優化策略
                strategy_result = await self._optimize_strategy()
                optimization_results.append({"type": "strategy", "result": strategy_result})
            
            if optimization_type in ["auto", "cleanup"]:
                # 清理無效節點
                cleanup_result = await self._cleanup_unhealthy_nodes()
                optimization_results.append({"type": "cleanup", "result": cleanup_result})
            
            return {
                "status": "success",
                "optimization_type": optimization_type,
                "optimization_results": optimization_results,
                "optimization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"路由優化失敗: {str(e)}"
            }
    
    async def _optimize_weights(self) -> Dict[str, Any]:
        """優化權重"""
        try:
            optimized_count = 0
            
            for mcp_id, node in self.mcp_nodes.items():
                # 基於性能指標調整權重
                old_weight = node.weight
                
                # 新權重 = 基礎權重 * 成功率 * (1 / 響應時間因子)
                response_factor = 1.0 / (1.0 + node.response_time_avg)
                new_weight = 1.0 * node.success_rate * response_factor
                
                if abs(new_weight - old_weight) > 0.1:
                    node.weight = new_weight
                    optimized_count += 1
            
            return {
                "status": "success",
                "optimized_nodes": optimized_count,
                "message": f"優化了 {optimized_count} 個節點的權重"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"權重優化失敗: {str(e)}"
            }
    
    async def _optimize_strategy(self) -> Dict[str, Any]:
        """優化策略"""
        try:
            # 分析當前策略的性能
            strategy_performance = {}
            
            for entry in self.routing_history[-100:]:  # 分析最近100次路由
                strategy = entry.get("routing_strategy", "unknown")
                if strategy not in strategy_performance:
                    strategy_performance[strategy] = {"total": 0, "successful": 0}
                
                strategy_performance[strategy]["total"] += 1
                if entry.get("success", False):
                    strategy_performance[strategy]["successful"] += 1
            
            # 找到最佳策略
            best_strategy = None
            best_success_rate = 0
            
            for strategy, perf in strategy_performance.items():
                if perf["total"] > 0:
                    success_rate = perf["successful"] / perf["total"]
                    if success_rate > best_success_rate:
                        best_success_rate = success_rate
                        best_strategy = strategy
            
            # 如果找到更好的策略，則切換
            if best_strategy and best_strategy != self.default_strategy.value:
                old_strategy = self.default_strategy.value
                self.default_strategy = RoutingStrategy(best_strategy)
                
                return {
                    "status": "success",
                    "old_strategy": old_strategy,
                    "new_strategy": best_strategy,
                    "success_rate": best_success_rate,
                    "message": f"策略已優化為: {best_strategy}"
                }
            else:
                return {
                    "status": "success",
                    "message": "當前策略已是最優",
                    "current_strategy": self.default_strategy.value
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"策略優化失敗: {str(e)}"
            }
    
    async def _cleanup_unhealthy_nodes(self) -> Dict[str, Any]:
        """清理不健康的節點"""
        try:
            unhealthy_nodes = []
            
            for mcp_id, node in list(self.mcp_nodes.items()):
                if node.status == MCPStatus.OFFLINE:
                    # 檢查是否長時間離線
                    last_check = datetime.fromisoformat(node.last_health_check)
                    if datetime.now() - last_check > timedelta(hours=1):
                        unhealthy_nodes.append(mcp_id)
            
            # 移除長時間離線的節點（但不刪除，只是標記）
            for mcp_id in unhealthy_nodes:
                self.mcp_nodes[mcp_id].status = MCPStatus.MAINTENANCE
            
            return {
                "status": "success",
                "cleaned_nodes": len(unhealthy_nodes),
                "message": f"清理了 {len(unhealthy_nodes)} 個不健康節點"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"節點清理失敗: {str(e)}"
            }
    
    async def export_routing_data(self, export_path: str = None) -> Dict[str, Any]:
        """導出路由數據"""
        try:
            if export_path is None:
                export_path = f"routing_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "routing_config": {
                    "default_strategy": self.default_strategy.value,
                    "load_balancing_mode": self.load_balancing_mode.value,
                    "health_check_interval": self.health_check_interval
                },
                "mcp_nodes": {mcp_id: node.to_dict() for mcp_id, node in self.mcp_nodes.items()},
                "routing_table": self.routing_table,
                "routing_stats": self.routing_stats,
                "performance_metrics": self.performance_metrics,
                "routing_history": self.routing_history[-100:],  # 最近100條記錄
                "health_check_results": self.health_check_results
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "export_path": export_path,
                "exported_nodes": len(self.mcp_nodes),
                "exported_history": len(self.routing_history[-100:]),
                "export_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"導出路由數據失敗: {str(e)}"
            }
    
    def reset_routing_stats(self) -> Dict[str, Any]:
        """重置路由統計"""
        try:
            old_stats = self.routing_stats.copy()
            
            self.routing_stats = {
                "total_requests": 0,
                "successful_routes": 0,
                "failed_routes": 0,
                "average_response_time": 0.0,
                "strategy_usage": {strategy.value: 0 for strategy in RoutingStrategy},
                "mcp_usage": {mcp_id: 0 for mcp_id in self.mcp_nodes.keys()},
                "error_counts": {}
            }
            
            # 清空歷史記錄
            self.routing_history.clear()
            
            # 重置性能指標
            for mcp_id in self.performance_metrics:
                self.performance_metrics[mcp_id] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "response_times": []
                }
            
            return {
                "status": "success",
                "message": "路由統計已重置",
                "old_stats": old_stats,
                "reset_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"重置路由統計失敗: {str(e)}"
            }

# 創建全局實例
smart_routing_mcp = SmartRoutingMCP()

# 導出主要接口
__all__ = [
    'SmartRoutingMCP',
    'RoutingStrategy',
    'MCPStatus',
    'LoadBalancingMode',
    'MCPNode',
    'RoutingRequest',
    'RoutingResult',
    'smart_routing_mcp'
]

if __name__ == "__main__":
    # 測試MCP功能
    test_data = {
        "operation": "get_routing_stats",
        "params": {}
    }
    
    result = smart_routing_mcp.process(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

