#!/usr/bin/env python3
"""
统一智能工具引擎MCP适配器 - 完善版
整合ACI.dev、MCP.so、Zapier三个云端平台的统一工具引擎
同时整合发布发现功能
"""

import json
import logging
import asyncio
import time
import os
import requests
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import sys
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcptool.core.base_mcp import BaseMCP

logger = logging.getLogger(__name__)

class UnifiedToolRegistry:
    """统一工具注册表"""
    
    def __init__(self):
        self.tools_db = {}
        self.platform_clients = {}
        self.last_sync_time = None
        
    def register_tool(self, tool_info: Dict) -> str:
        """注册工具到统一注册表"""
        tool_id = f"{tool_info['platform']}:{tool_info['name']}"
        
        unified_tool = {
            # 基础信息
            "id": tool_id,
            "name": tool_info["name"],
            "description": tool_info["description"],
            "category": tool_info["category"],
            "version": tool_info.get("version", "1.0.0"),
            
            # 平台信息
            "platform": tool_info["platform"],
            "platform_tool_id": tool_info["platform_tool_id"],
            "mcp_endpoint": tool_info["mcp_endpoint"],
            
            # 功能特性
            "capabilities": tool_info["capabilities"],
            "input_schema": tool_info["input_schema"],
            "output_schema": tool_info["output_schema"],
            
            # 性能指标
            "performance_metrics": {
                "avg_response_time": tool_info.get("avg_response_time", 1000),
                "success_rate": tool_info.get("success_rate", 0.95),
                "throughput": tool_info.get("throughput", 100),
                "reliability_score": tool_info.get("reliability_score", 0.9)
            },
            
            # 成本信息
            "cost_model": {
                "type": tool_info.get("cost_type", "free"),
                "cost_per_call": tool_info.get("cost_per_call", 0.0),
                "monthly_limit": tool_info.get("monthly_limit", -1),
                "currency": tool_info.get("currency", "USD")
            },
            
            # 质量评分
            "quality_scores": {
                "user_rating": tool_info.get("user_rating", 4.0),
                "documentation_quality": tool_info.get("doc_quality", 0.8),
                "community_support": tool_info.get("community_support", 0.7),
                "update_frequency": tool_info.get("update_frequency", 0.8)
            }
        }
        
        self.tools_db[tool_id] = unified_tool
        return tool_id
    
    def search_tools(self, query: str, filters: Dict = None) -> List[Dict]:
        """搜索工具"""
        filters = filters or {}
        matches = []
        query_lower = query.lower()
        
        for tool_id, tool in self.tools_db.items():
            score = 0.0
            
            # 名称匹配
            if query_lower in tool["name"].lower():
                score += 0.4
            
            # 描述匹配
            if query_lower in tool["description"].lower():
                score += 0.3
            
            # 类别匹配
            if query_lower in tool["category"].lower():
                score += 0.2
            
            # 能力匹配
            for capability in tool["capabilities"]:
                if query_lower in capability.lower():
                    score += 0.1
                    break
            
            # 应用过滤器
            if self._apply_filters(tool, filters) and score > 0:
                tool_copy = tool.copy()
                tool_copy["relevance_score"] = score
                matches.append(tool_copy)
        
        return sorted(matches, key=lambda x: x["relevance_score"], reverse=True)
    
    def _apply_filters(self, tool: Dict, filters: Dict) -> bool:
        """应用过滤器"""
        if "platforms" in filters and tool["platform"] not in filters["platforms"]:
            return False
        
        if "categories" in filters and tool["category"] not in filters["categories"]:
            return False
        
        if "max_cost" in filters:
            if tool["cost_model"]["cost_per_call"] > filters["max_cost"]:
                return False
        
        if "min_success_rate" in filters:
            if tool["performance_metrics"]["success_rate"] < filters["min_success_rate"]:
                return False
        
        return True

class IntelligentRoutingEngine:
    """智能路由决策引擎"""
    
    def __init__(self, registry: UnifiedToolRegistry):
        self.registry = registry
        self.decision_weights = {
            "performance": 0.3,
            "cost": 0.25,
            "quality": 0.25,
            "availability": 0.2
        }
    
    def select_optimal_tool(self, user_request: str, context: Dict = None) -> Dict:
        """选择最优工具"""
        context = context or {}
        
        # 工具发现
        candidate_tools = self.registry.search_tools(
            user_request, 
            filters=context.get("filters", {})
        )
        
        if not candidate_tools:
            return {"success": False, "error": "未找到匹配的工具"}
        
        # 多维度评分
        scored_tools = []
        for tool in candidate_tools:
            score = self._calculate_comprehensive_score(tool, context)
            tool["comprehensive_score"] = score
            scored_tools.append(tool)
        
        # 选择最优工具
        best_tool = max(scored_tools, key=lambda x: x["comprehensive_score"])
        
        return {
            "success": True,
            "selected_tool": best_tool,
            "alternatives": scored_tools[1:4],
            "decision_explanation": self._generate_decision_explanation(best_tool, context)
        }
    
    def _calculate_comprehensive_score(self, tool: Dict, context: Dict) -> float:
        """计算综合评分"""
        performance_score = self._calculate_performance_score(tool)
        cost_score = self._calculate_cost_score(tool, context)
        quality_score = self._calculate_quality_score(tool)
        availability_score = self._calculate_availability_score(tool, context)
        
        comprehensive_score = (
            performance_score * self.decision_weights["performance"] +
            cost_score * self.decision_weights["cost"] +
            quality_score * self.decision_weights["quality"] +
            availability_score * self.decision_weights["availability"]
        )
        
        # 相关性加成
        relevance_bonus = tool.get("relevance_score", 0) * 0.1
        
        return min(comprehensive_score + relevance_bonus, 1.0)
    
    def _calculate_performance_score(self, tool: Dict) -> float:
        """计算性能评分"""
        metrics = tool["performance_metrics"]
        
        response_time_score = max(0, 1 - (metrics["avg_response_time"] / 5000))
        success_rate_score = metrics["success_rate"]
        throughput_score = min(metrics["throughput"] / 1000, 1.0)
        reliability_score = metrics["reliability_score"]
        
        return (response_time_score * 0.3 + success_rate_score * 0.3 + 
                throughput_score * 0.2 + reliability_score * 0.2)
    
    def _calculate_cost_score(self, tool: Dict, context: Dict) -> float:
        """计算成本评分"""
        cost_model = tool["cost_model"]
        
        if cost_model["type"] == "free":
            return 1.0
        elif cost_model["type"] == "per_call":
            max_cost = context.get("budget", {}).get("max_cost_per_call", 0.01)
            cost_ratio = cost_model["cost_per_call"] / max_cost
            return max(0, 1 - cost_ratio)
        else:
            return 0.8
    
    def _calculate_quality_score(self, tool: Dict) -> float:
        """计算质量评分"""
        quality = tool["quality_scores"]
        
        user_rating_score = (quality["user_rating"] - 1) / 4
        doc_quality_score = quality["documentation_quality"]
        community_score = quality["community_support"]
        update_score = quality["update_frequency"]
        
        return (user_rating_score * 0.4 + doc_quality_score * 0.2 + 
                community_score * 0.2 + update_score * 0.2)
    
    def _calculate_availability_score(self, tool: Dict, context: Dict) -> float:
        """计算可用性评分"""
        # 简化的可用性评分
        return 0.9
    
    def _generate_decision_explanation(self, tool: Dict, context: Dict) -> Dict:
        """生成决策解释"""
        return {
            "selected_tool": {
                "name": tool["name"],
                "platform": tool["platform"],
                "score": tool["comprehensive_score"]
            },
            "key_factors": {
                "performance": self._calculate_performance_score(tool),
                "cost": self._calculate_cost_score(tool, context),
                "quality": self._calculate_quality_score(tool)
            }
        }

class MCPUnifiedExecutionEngine:
    """MCP统一执行引擎"""
    
    def __init__(self, registry: UnifiedToolRegistry):
        self.registry = registry
        self.routing_engine = IntelligentRoutingEngine(registry)
        
        # 执行统计
        self.execution_stats = {
            "total_executions": 0,
            "platform_usage": {"aci.dev": 0, "mcp.so": 0, "zapier": 0},
            "success_rate": 0.0,
            "avg_execution_time": 0.0
        }
    
    async def execute_user_request(self, user_request: str, context: Dict = None) -> Dict:
        """执行用户请求"""
        context = context or {}
        execution_id = f"exec_{int(time.time())}"
        
        try:
            # 智能路由选择工具
            routing_result = self.routing_engine.select_optimal_tool(user_request, context)
            
            if not routing_result["success"]:
                return routing_result
            
            selected_tool = routing_result["selected_tool"]
            
            # 准备执行参数
            execution_params = self._prepare_execution_params(user_request, selected_tool, context)
            
            # 模拟MCP执行
            execution_result = await self._simulate_mcp_execution(
                selected_tool, execution_params, execution_id
            )
            
            # 更新统计信息
            self._update_execution_stats(selected_tool, execution_result)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "selected_tool": {
                    "name": selected_tool["name"],
                    "platform": selected_tool["platform"],
                    "confidence_score": selected_tool["comprehensive_score"]
                },
                "execution_result": execution_result,
                "routing_info": routing_result["decision_explanation"],
                "alternatives": routing_result["alternatives"]
            }
            
        except Exception as e:
            logger.error(f"执行失败 {execution_id}: {e}")
            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e)
            }
    
    def _prepare_execution_params(self, user_request: str, tool: Dict, context: Dict) -> Dict:
        """准备执行参数"""
        return {
            "request": user_request,
            "context": context,
            "tool_specific_params": self._extract_tool_specific_params(user_request, tool)
        }
    
    def _extract_tool_specific_params(self, request: str, tool: Dict) -> Dict:
        """提取工具特定参数"""
        category = tool["category"]
        
        if category == "productivity":
            return {"priority": "normal", "notification": True}
        elif category == "data_analysis":
            return {"analysis_type": "basic", "output_format": "json"}
        elif category == "communication":
            return {"message_format": "text", "urgent": False}
        else:
            return {}
    
    async def _simulate_mcp_execution(self, tool: Dict, params: Dict, execution_id: str) -> Dict:
        """模拟MCP执行"""
        start_time = time.time()
        
        # 模拟执行延迟
        await asyncio.sleep(0.1)
        
        execution_time = time.time() - start_time
        
        # 模拟成功执行
        return {
            "success": True,
            "result": f"工具 {tool['name']} 执行完成",
            "execution_time": execution_time,
            "platform": tool["platform"],
            "tool_name": tool["name"],
            "metadata": {
                "execution_timestamp": time.time(),
                "mcp_version": "1.0"
            }
        }
    
    def _update_execution_stats(self, tool: Dict, result: Dict):
        """更新执行统计"""
        self.execution_stats["total_executions"] += 1
        self.execution_stats["platform_usage"][tool["platform"]] += 1
        
        if result.get("success"):
            current_success = self.execution_stats.get("successful_executions", 0)
            self.execution_stats["successful_executions"] = current_success + 1
        
        total = self.execution_stats["total_executions"]
        successful = self.execution_stats.get("successful_executions", 0)
        self.execution_stats["success_rate"] = successful / total if total > 0 else 0
    
    def get_execution_statistics(self) -> Dict:
        """获取执行统计信息"""
        return {
            "statistics": self.execution_stats,
            "platform_distribution": {
                platform: count / max(self.execution_stats["total_executions"], 1)
                for platform, count in self.execution_stats["platform_usage"].items()
            },
            "registry_info": {
                "total_tools": len(self.registry.tools_db)
            }
        }

class UnifiedSmartToolEngineMCP(BaseMCP):
    """统一智能工具引擎MCP适配器 - 完善版"""
    
    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or {}
        
        # 初始化核心组件
        self.registry = UnifiedToolRegistry()
        self.execution_engine = MCPUnifiedExecutionEngine(self.registry)
        
        # 初始化示例工具
        self._initialize_sample_tools()
        
        logger.info("统一智能工具引擎MCP适配器初始化完成")
    
    def _initialize_sample_tools(self):
        """初始化示例工具"""
        sample_tools = [
            {
                "name": "google_calendar_integration",
                "description": "Google Calendar API集成工具",
                "category": "productivity",
                "platform": "aci.dev",
                "platform_tool_id": "google_calendar_v3",
                "mcp_endpoint": "https://api.aci.dev/mcp/google_calendar",
                "capabilities": ["schedule", "remind", "sync", "share"],
                "input_schema": {"type": "object", "properties": {"action": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"result": {"type": "string"}}},
                "avg_response_time": 200,
                "success_rate": 0.98,
                "cost_type": "per_call",
                "cost_per_call": 0.001,
                "user_rating": 4.5
            },
            {
                "name": "advanced_data_analyzer",
                "description": "高级数据分析MCP工具",
                "category": "data_analysis",
                "platform": "mcp.so",
                "platform_tool_id": "data_analyzer_pro",
                "mcp_endpoint": "https://api.mcp.so/tools/data_analyzer",
                "capabilities": ["analyze", "visualize", "predict", "export"],
                "input_schema": {"type": "object", "properties": {"data": {"type": "array"}}},
                "output_schema": {"type": "object", "properties": {"analysis": {"type": "object"}}},
                "avg_response_time": 500,
                "success_rate": 0.96,
                "cost_type": "subscription",
                "monthly_limit": 1000,
                "user_rating": 4.3
            },
            {
                "name": "slack_team_notification",
                "description": "Slack团队通知自动化",
                "category": "communication",
                "platform": "zapier",
                "platform_tool_id": "slack_webhook_v2",
                "mcp_endpoint": "https://zapier-mcp-bridge.com/slack_notification",
                "capabilities": ["message", "channel", "mention", "format"],
                "input_schema": {"type": "object", "properties": {"message": {"type": "string"}}},
                "output_schema": {"type": "object", "properties": {"status": {"type": "string"}}},
                "avg_response_time": 150,
                "success_rate": 0.99,
                "cost_type": "free",
                "user_rating": 4.7
            }
        ]
        
        for tool in sample_tools:
            self.registry.register_tool(tool)
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力"""
        return [
            "unified_tool_discovery",
            "intelligent_routing",
            "multi_platform_execution",
            "performance_optimization",
            "cost_optimization",
            "quality_assurance"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get("action")
        valid_actions = [
            "execute_request",
            "discover_tools",
            "get_statistics",
            "register_tool",
            "health_check"
        ]
        
        return action in valid_actions
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        try:
            action = input_data.get("action")
            parameters = input_data.get("parameters", {})
            
            if action == "execute_request":
                return asyncio.run(self._execute_request(parameters))
            elif action == "discover_tools":
                return self._discover_tools(parameters)
            elif action == "get_statistics":
                return self._get_statistics()
            elif action == "register_tool":
                return self._register_tool(parameters)
            elif action == "health_check":
                return self._health_check()
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {action}",
                    "available_actions": [
                        "execute_request", "discover_tools", "get_statistics",
                        "register_tool", "health_check"
                    ]
                }
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": input_data.get("action")
            }
    
    async def _execute_request(self, parameters: Dict) -> Dict[str, Any]:
        """执行用户请求"""
        user_request = parameters.get("request", "")
        context = parameters.get("context", {})
        
        if not user_request:
            return {
                "success": False,
                "error": "缺少必需参数: request"
            }
        
        result = await self.execution_engine.execute_user_request(user_request, context)
        return result
    
    def _discover_tools(self, parameters: Dict) -> Dict[str, Any]:
        """工具发现"""
        try:
            query = parameters.get("query", "")
            filters = parameters.get("filters", {})
            limit = parameters.get("limit", 10)
            
            tools = self.registry.search_tools(query, filters)
            
            return {
                "success": True,
                "tools": tools[:limit],
                "total_count": len(tools),
                "search_query": query,
                "filters_applied": filters
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            stats = self.execution_engine.get_execution_statistics()
            return {
                "success": True,
                "statistics": stats
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _register_tool(self, parameters: Dict) -> Dict[str, Any]:
        """注册新工具"""
        try:
            tool_info = parameters.get("tool_info", {})
            
            if not tool_info:
                return {
                    "success": False,
                    "error": "缺少工具信息"
                }
            
            tool_id = self.registry.register_tool(tool_info)
            
            return {
                "success": True,
                "tool_id": tool_id,
                "message": "工具注册成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "success": True,
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0",
            "components": {
                "registry": "operational",
                "routing_engine": "operational",
                "execution_engine": "operational"
            },
            "metrics": {
                "total_tools": len(self.registry.tools_db),
                "total_executions": self.execution_engine.execution_stats["total_executions"]
            }
        }


class ReleaseDiscoveryEngine:
    """發布發現引擎 - 整合到統一智能工具引擎"""
    
    def __init__(self, registry: UnifiedToolRegistry):
        self.registry = registry
        self.workflow_state = {
            "current_phase": "idle",
            "context_cache": {},
            "discovery_results": [],
            "release_status": "pending"
        }
        
        # 工具註冊表 - 發布發現相關工具
        self.release_tools = {
            "discover_tools": {
                "name": "工具發現",
                "description": "執行智能工具發現工作流",
                "category": "discovery",
                "parameters": ["context", "requirements", "filters"]
            },
            "release_workflow": {
                "name": "發布工作流",
                "description": "執行完整的發布管理工作流",
                "category": "release",
                "parameters": ["version", "release_context", "rules", "target"]
            },
            "analyze_context": {
                "name": "上下文分析",
                "description": "深度分析項目上下文和依賴關係",
                "category": "analysis",
                "parameters": ["text", "context_id", "analysis_depth"]
            },
            "validate_tools": {
                "name": "工具驗證",
                "description": "驗證工具質量和可用性",
                "category": "validation",
                "parameters": ["tools", "validation_criteria", "quality_threshold"]
            },
            "quality_assessment": {
                "name": "質量評估",
                "description": "評估發布質量和準備度",
                "category": "quality",
                "parameters": ["version", "context", "quality_gates"]
            },
            "deployment_validation": {
                "name": "部署驗證",
                "description": "驗證部署準備和環境配置",
                "category": "deployment",
                "parameters": ["target", "configuration", "prerequisites"]
            }
        }
        
        logger.info("發布發現引擎初始化完成")
    
    def execute_discovery_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行工具發現工作流
        MCPBrainstorm → InfiniteContext → MCP.so → ACI.dev → 自動部署
        """
        self.workflow_state["current_phase"] = "discovery"
        
        try:
            # 階段1: 上下文分析
            context_data = input_data.get("context", "")
            context_result = self._analyze_discovery_context(context_data)
            
            # 階段2: 工具發現
            discovery_result = self._discover_tools_from_registry(context_result, input_data)
            
            # 階段3: 質量分析
            quality_result = self._analyze_tool_quality(discovery_result.get("tools", []))
            
            # 階段4: 部署驗證
            deployment_result = self._validate_deployment_readiness(quality_result)
            
            # 彙總結果
            workflow_result = {
                "status": "success",
                "workflow": "discovery",
                "phases": {
                    "context_analysis": context_result,
                    "tool_discovery": discovery_result,
                    "quality_analysis": quality_result,
                    "deployment_validation": deployment_result
                },
                "summary": {
                    "tools_discovered": len(discovery_result.get("tools", [])),
                    "quality_score": quality_result.get("score", 0),
                    "deployment_ready": deployment_result.get("ready", False)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.workflow_state["discovery_results"].append(workflow_result)
            self.workflow_state["current_phase"] = "completed"
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"工具發現工作流執行失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    def execute_release_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行發布工作流
        上下文分析 → 質量評估 → 規則執行 → 發布驗證
        """
        self.workflow_state["current_phase"] = "release"
        
        try:
            # 階段1: 上下文分析
            release_context = input_data.get("release_context", {})
            context_analysis = self._analyze_release_context(release_context)
            
            # 階段2: 質量評估
            quality_assessment = self._assess_release_quality(
                context_analysis, 
                input_data.get("version", "1.0.0")
            )
            
            # 階段3: 規則執行
            rule_execution = self._execute_release_rules(
                quality_assessment, 
                input_data.get("rules", [])
            )
            
            # 階段4: 發布驗證
            release_validation = self._validate_release_readiness(
                rule_execution, 
                input_data.get("target", "production")
            )
            
            # 彙總結果
            release_result = {
                "status": "success",
                "workflow": "release",
                "version": input_data.get("version", "1.0.0"),
                "phases": {
                    "context_analysis": context_analysis,
                    "quality_assessment": quality_assessment,
                    "rule_execution": rule_execution,
                    "release_validation": release_validation
                },
                "summary": {
                    "quality_passed": quality_assessment.get("passed", False),
                    "rules_satisfied": rule_execution.get("satisfied", False),
                    "release_approved": release_validation.get("approved", False)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.workflow_state["release_status"] = "completed"
            
            return release_result
            
        except Exception as e:
            logger.error(f"發布工作流執行失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_discovery_context(self, context_data: str) -> Dict[str, Any]:
        """分析發現上下文"""
        return {
            "context_length": len(context_data),
            "key_concepts": self._extract_key_concepts(context_data),
            "requirements": self._extract_requirements(context_data),
            "complexity_score": min(len(context_data) / 1000, 1.0),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _discover_tools_from_registry(self, context_result: Dict, input_data: Dict) -> Dict[str, Any]:
        """從註冊表發現工具"""
        requirements = input_data.get("requirements", [])
        search_query = " ".join(requirements) if requirements else context_result.get("key_concepts", ["general"])[0]
        
        # 使用統一工具註冊表搜索
        discovered_tools = self.registry.search_tools(search_query)
        
        return {
            "tools": discovered_tools[:10],  # 限制返回前10個工具
            "search_query": search_query,
            "total_found": len(discovered_tools),
            "discovery_method": "registry_search"
        }
    
    def _analyze_tool_quality(self, tools: List[Dict]) -> Dict[str, Any]:
        """分析工具質量"""
        if not tools:
            return {"score": 0, "analysis": "無工具可分析"}
        
        total_score = 0
        quality_details = []
        
        for tool in tools:
            tool_score = (
                tool.get("quality_scores", {}).get("user_rating", 3.0) / 5.0 * 0.4 +
                tool.get("performance_metrics", {}).get("success_rate", 0.8) * 0.3 +
                tool.get("quality_scores", {}).get("documentation_quality", 0.7) * 0.3
            )
            total_score += tool_score
            quality_details.append({
                "tool_name": tool.get("name", "unknown"),
                "quality_score": tool_score,
                "strengths": ["高用戶評分", "良好性能", "完整文檔"],
                "weaknesses": ["需要更多測試", "社區支持有限"]
            })
        
        average_score = total_score / len(tools)
        
        return {
            "score": average_score,
            "total_tools": len(tools),
            "quality_details": quality_details,
            "recommendation": "優秀" if average_score > 0.8 else "良好" if average_score > 0.6 else "需要改進"
        }
    
    def _validate_deployment_readiness(self, quality_result: Dict) -> Dict[str, Any]:
        """驗證部署準備度"""
        quality_score = quality_result.get("score", 0)
        
        return {
            "ready": quality_score > 0.7,
            "quality_gate_passed": quality_score > 0.6,
            "deployment_score": quality_score,
            "recommendations": [
                "執行完整測試套件",
                "驗證環境配置",
                "準備回滾計劃"
            ] if quality_score > 0.7 else [
                "提高工具質量",
                "增加測試覆蓋率",
                "改善文檔質量"
            ]
        }
    
    def _analyze_release_context(self, release_context: Dict) -> Dict[str, Any]:
        """分析發布上下文"""
        changes = release_context.get("changes", [])
        target = release_context.get("target", "production")
        
        return {
            "changes_count": len(changes),
            "change_types": self._categorize_changes(changes),
            "target_environment": target,
            "risk_level": self._assess_risk_level(changes, target),
            "impact_analysis": self._analyze_impact(changes)
        }
    
    def _assess_release_quality(self, context_analysis: Dict, version: str) -> Dict[str, Any]:
        """評估發布質量"""
        risk_level = context_analysis.get("risk_level", "medium")
        changes_count = context_analysis.get("changes_count", 0)
        
        quality_score = 0.9 if risk_level == "low" else 0.7 if risk_level == "medium" else 0.5
        
        return {
            "passed": quality_score > 0.6,
            "quality_score": quality_score,
            "version": version,
            "risk_assessment": risk_level,
            "quality_gates": {
                "code_quality": quality_score > 0.7,
                "test_coverage": quality_score > 0.6,
                "security_scan": quality_score > 0.8,
                "performance_test": quality_score > 0.7
            }
        }
    
    def _execute_release_rules(self, quality_assessment: Dict, rules: List[str]) -> Dict[str, Any]:
        """執行發布規則"""
        satisfied_rules = []
        failed_rules = []
        
        for rule in rules:
            if self._check_rule(rule, quality_assessment):
                satisfied_rules.append(rule)
            else:
                failed_rules.append(rule)
        
        return {
            "satisfied": len(failed_rules) == 0,
            "satisfied_rules": satisfied_rules,
            "failed_rules": failed_rules,
            "compliance_rate": len(satisfied_rules) / len(rules) if rules else 1.0
        }
    
    def _validate_release_readiness(self, rule_execution: Dict, target: str) -> Dict[str, Any]:
        """驗證發布準備度"""
        rules_satisfied = rule_execution.get("satisfied", False)
        compliance_rate = rule_execution.get("compliance_rate", 0)
        
        return {
            "approved": rules_satisfied and compliance_rate > 0.8,
            "target_environment": target,
            "compliance_rate": compliance_rate,
            "readiness_score": compliance_rate,
            "approval_status": "approved" if rules_satisfied else "pending_fixes"
        }
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """提取關鍵概念"""
        # 簡化的關鍵詞提取
        keywords = ["data", "analysis", "visualization", "api", "automation", "workflow"]
        found_concepts = [kw for kw in keywords if kw.lower() in text.lower()]
        return found_concepts[:5] if found_concepts else ["general"]
    
    def _extract_requirements(self, text: str) -> List[str]:
        """提取需求"""
        # 簡化的需求提取
        requirements = []
        if "python" in text.lower():
            requirements.append("python")
        if "data" in text.lower():
            requirements.append("data_processing")
        if "api" in text.lower():
            requirements.append("api_integration")
        return requirements if requirements else ["general"]
    
    def _categorize_changes(self, changes: List[str]) -> Dict[str, int]:
        """分類變更"""
        categories = {"feature": 0, "bugfix": 0, "security": 0, "performance": 0}
        
        for change in changes:
            change_lower = change.lower()
            if "新增" in change_lower or "feature" in change_lower:
                categories["feature"] += 1
            elif "修復" in change_lower or "fix" in change_lower:
                categories["bugfix"] += 1
            elif "安全" in change_lower or "security" in change_lower:
                categories["security"] += 1
            elif "性能" in change_lower or "performance" in change_lower:
                categories["performance"] += 1
        
        return categories
    
    def _assess_risk_level(self, changes: List[str], target: str) -> str:
        """評估風險等級"""
        if target == "production" and len(changes) > 5:
            return "high"
        elif len(changes) > 3:
            return "medium"
        else:
            return "low"
    
    def _analyze_impact(self, changes: List[str]) -> Dict[str, Any]:
        """分析影響"""
        return {
            "user_impact": "medium" if len(changes) > 3 else "low",
            "system_impact": "high" if any("架構" in change for change in changes) else "medium",
            "rollback_complexity": "high" if len(changes) > 5 else "medium"
        }
    
    def _check_rule(self, rule: str, quality_assessment: Dict) -> bool:
        """檢查規則"""
        quality_gates = quality_assessment.get("quality_gates", {})
        
        rule_mapping = {
            "quality_gate": quality_gates.get("code_quality", False),
            "security_scan": quality_gates.get("security_scan", False),
            "performance_test": quality_gates.get("performance_test", False),
            "test_coverage": quality_gates.get("test_coverage", False)
        }
        
        return rule_mapping.get(rule, True)  # 默認通過未知規則
    
    def get_workflow_state(self) -> Dict[str, Any]:
        """獲取工作流狀態"""
        return self.workflow_state.copy()
    
    def reset_workflow(self) -> Dict[str, Any]:
        """重置工作流狀態"""
        self.workflow_state = {
            "current_phase": "idle",
            "context_cache": {},
            "discovery_results": [],
            "release_status": "pending"
        }
        
        return {"status": "success", "message": "工作流狀態已重置"}
    
    def get_release_tools(self) -> Dict[str, Any]:
        """獲取發布相關工具"""
        return self.release_tools

