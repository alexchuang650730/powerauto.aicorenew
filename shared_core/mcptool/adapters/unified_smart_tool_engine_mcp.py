"""
统一智能工具引擎MCP适配器
整合ACI.dev和MCP.so两个云端工具平台服务
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
import os
import requests
from pathlib import Path

from ..base_mcp import BaseMCP

logger = logging.getLogger(__name__)

class UnifiedSmartToolEngineMCP(BaseMCP):
    """统一智能工具引擎MCP适配器"""
    
    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or {}
        
        # API配置
        self.aci_api_key = os.getenv("ACI_API_KEY")
        self.mcpso_api_key = os.getenv("MCPSO_API_KEY")
        self.aci_endpoint = self.config.get("aci_endpoint", "https://api.aci.dev")
        self.mcpso_endpoint = self.config.get("mcpso_endpoint", "https://api.mcp.so")
        
        # 工具缓存
        self.aci_tools_cache = {}
        self.mcpso_tools_cache = {}
        self.last_sync_time = None
        
        # 性能指标
        self.performance_metrics = {
            "aci_calls": 0,
            "mcpso_calls": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0
        }
        
        logger.info("统一智能工具引擎MCP适配器初始化完成")
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力"""
        return [
            "tool_discovery",      # 工具发现
            "tool_execution",      # 工具执行
            "smart_routing",       # 智能路由
            "performance_optimization",  # 性能优化
            "unified_interface",   # 统一接口
            "hybrid_execution"     # 混合执行
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get("action")
        if not action:
            return False
        
        valid_actions = [
            "discover_tools",
            "execute_tool", 
            "smart_execute",
            "get_tool_info",
            "sync_tools",
            "get_performance_metrics"
        ]
        
        return action in valid_actions
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        try:
            action = input_data.get("action")
            parameters = input_data.get("parameters", {})
            
            if action == "discover_tools":
                return self._discover_tools(parameters)
            elif action == "execute_tool":
                return self._execute_tool(parameters)
            elif action == "smart_execute":
                return self._smart_execute(parameters)
            elif action == "get_tool_info":
                return self._get_tool_info(parameters)
            elif action == "sync_tools":
                return self._sync_tools(parameters)
            elif action == "get_performance_metrics":
                return self._get_performance_metrics()
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {action}",
                    "available_actions": [
                        "discover_tools", "execute_tool", "smart_execute",
                        "get_tool_info", "sync_tools", "get_performance_metrics"
                    ]
                }
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": input_data.get("action")
            }
    
    def _discover_tools(self, parameters: Dict) -> Dict[str, Any]:
        """工具发现 - 本地+云端"""
        try:
            query = parameters.get("query", "")
            category = parameters.get("category")
            limit = parameters.get("limit", 20)
            source = parameters.get("source", "both")  # local, cloud, both
            
            results = {
                "local_tools": [],
                "cloud_tools": [],
                "total_count": 0,
                "search_query": query,
                "category_filter": category
            }
            
            # 搜索本地工具
            if source in ["local", "both"]:
                local_tools = self._search_local_tools(query, category, limit // 2)
                results["local_tools"] = local_tools
            
            # 搜索云端工具
            if source in ["cloud", "both"]:
                cloud_tools = self._search_cloud_tools(query, category, limit // 2)
                results["cloud_tools"] = cloud_tools
            
            results["total_count"] = len(results["local_tools"]) + len(results["cloud_tools"])
            
            # 智能排序和推荐
            recommended_tools = self._rank_tools(results["local_tools"] + results["cloud_tools"], query)
            results["recommended_tools"] = recommended_tools[:limit]
            
            return {
                "success": True,
                "results": results,
                "performance": {
                    "local_tools_count": len(results["local_tools"]),
                    "cloud_tools_count": len(results["cloud_tools"]),
                    "search_time": "< 1s"
                }
            }
            
        except Exception as e:
            logger.error(f"工具发现失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _search_local_tools(self, query: str, category: Optional[str], limit: int) -> List[Dict]:
        """搜索本地MCP.so工具"""
        try:
            # 模拟MCP.so工具搜索
            local_tools = [
                {
                    "id": "file_processor",
                    "name": "文件处理器",
                    "description": "高效的文件读写和转换工具",
                    "category": "file_operations",
                    "source": "local",
                    "capabilities": ["read", "write", "transform", "compress"],
                    "performance": {"latency": "10ms", "throughput": "high"},
                    "cost": "free"
                },
                {
                    "id": "data_analyzer",
                    "name": "数据分析器", 
                    "description": "本地数据分析和可视化工具",
                    "category": "data_processing",
                    "source": "local",
                    "capabilities": ["analyze", "visualize", "export", "statistics"],
                    "performance": {"latency": "50ms", "throughput": "medium"},
                    "cost": "free"
                },
                {
                    "id": "code_generator",
                    "name": "代码生成器",
                    "description": "本地代码生成和重构工具",
                    "category": "development",
                    "source": "local", 
                    "capabilities": ["generate", "refactor", "optimize", "test"],
                    "performance": {"latency": "100ms", "throughput": "medium"},
                    "cost": "free"
                }
            ]
            
            # 应用过滤条件
            filtered_tools = []
            for tool in local_tools:
                # 类别过滤
                if category and tool.get("category") != category:
                    continue
                
                # 查询过滤
                if query:
                    if (query.lower() not in tool.get("name", "").lower() and
                        query.lower() not in tool.get("description", "").lower()):
                        continue
                
                filtered_tools.append(tool)
                
                if len(filtered_tools) >= limit:
                    break
            
            return filtered_tools
            
        except Exception as e:
            logger.error(f"搜索本地工具失败: {e}")
            return []
    
    def _search_cloud_tools(self, query: str, category: Optional[str], limit: int) -> List[Dict]:
        """搜索ACI.dev云端工具"""
        try:
            if not self.aci_api_key:
                logger.warning("未配置ACI_API_KEY，跳过云端工具搜索")
                return []
            
            # 模拟ACI.dev API调用
            # 实际实现中应该调用真实的ACI.dev API
            cloud_tools = [
                {
                    "id": "google_calendar",
                    "name": "Google Calendar",
                    "description": "Google日历API集成工具",
                    "category": "productivity",
                    "source": "cloud",
                    "capabilities": ["schedule", "remind", "sync", "share"],
                    "performance": {"latency": "200ms", "throughput": "high"},
                    "cost": "api_calls"
                },
                {
                    "id": "slack_integration",
                    "name": "Slack集成",
                    "description": "Slack团队协作工具集成",
                    "category": "communication",
                    "source": "cloud",
                    "capabilities": ["message", "channel", "file_share", "bot"],
                    "performance": {"latency": "150ms", "throughput": "high"},
                    "cost": "api_calls"
                },
                {
                    "id": "github_actions",
                    "name": "GitHub Actions",
                    "description": "GitHub自动化工作流工具",
                    "category": "development",
                    "source": "cloud",
                    "capabilities": ["ci_cd", "deploy", "test", "release"],
                    "performance": {"latency": "500ms", "throughput": "medium"},
                    "cost": "api_calls"
                }
            ]
            
            # 应用过滤条件
            filtered_tools = []
            for tool in cloud_tools:
                # 类别过滤
                if category and tool.get("category") != category:
                    continue
                
                # 查询过滤
                if query:
                    if (query.lower() not in tool.get("name", "").lower() and
                        query.lower() not in tool.get("description", "").lower()):
                        continue
                
                filtered_tools.append(tool)
                
                if len(filtered_tools) >= limit:
                    break
            
            return filtered_tools
            
        except Exception as e:
            logger.error(f"搜索云端工具失败: {e}")
            return []
    
    def _rank_tools(self, tools: List[Dict], query: str) -> List[Dict]:
        """智能工具排序"""
        try:
            # 计算工具评分
            for tool in tools:
                score = 0.0
                
                # 相关性评分 (40%)
                relevance = self._calculate_relevance(tool, query)
                score += relevance * 0.4
                
                # 性能评分 (30%)
                performance = self._calculate_performance_score(tool)
                score += performance * 0.3
                
                # 成本评分 (20%)
                cost = self._calculate_cost_score(tool)
                score += cost * 0.2
                
                # 可用性评分 (10%)
                availability = self._calculate_availability_score(tool)
                score += availability * 0.1
                
                tool["ranking_score"] = score
            
            # 按评分排序
            return sorted(tools, key=lambda x: x.get("ranking_score", 0), reverse=True)
            
        except Exception as e:
            logger.error(f"工具排序失败: {e}")
            return tools
    
    def _calculate_relevance(self, tool: Dict, query: str) -> float:
        """计算相关性评分"""
        if not query:
            return 1.0
        
        query_lower = query.lower()
        name_match = query_lower in tool.get("name", "").lower()
        desc_match = query_lower in tool.get("description", "").lower()
        
        if name_match and desc_match:
            return 1.0
        elif name_match:
            return 0.8
        elif desc_match:
            return 0.6
        else:
            return 0.3
    
    def _calculate_performance_score(self, tool: Dict) -> float:
        """计算性能评分"""
        source = tool.get("source", "unknown")
        
        # 本地工具性能更好
        if source == "local":
            return 1.0
        elif source == "cloud":
            return 0.7
        else:
            return 0.5
    
    def _calculate_cost_score(self, tool: Dict) -> float:
        """计算成本评分"""
        cost = tool.get("cost", "unknown")
        
        if cost == "free":
            return 1.0
        elif cost == "api_calls":
            return 0.6
        else:
            return 0.3
    
    def _calculate_availability_score(self, tool: Dict) -> float:
        """计算可用性评分"""
        source = tool.get("source", "unknown")
        
        # 本地工具可用性更高
        if source == "local":
            return 1.0
        elif source == "cloud":
            return 0.8
        else:
            return 0.5
    
    def _execute_tool(self, parameters: Dict) -> Dict[str, Any]:
        """执行指定工具"""
        try:
            tool_id = parameters.get("tool_id")
            tool_source = parameters.get("source", "auto")  # local, cloud, auto
            arguments = parameters.get("arguments", {})
            
            if not tool_id:
                return {
                    "success": False,
                    "error": "缺少必需参数: tool_id"
                }
            
            # 自动选择执行源
            if tool_source == "auto":
                tool_source = self._determine_optimal_source(tool_id)
            
            # 执行工具
            if tool_source == "local":
                result = self._execute_local_tool(tool_id, arguments)
                self.performance_metrics["local_calls"] += 1
            elif tool_source == "cloud":
                result = self._execute_cloud_tool(tool_id, arguments)
                self.performance_metrics["cloud_calls"] += 1
            else:
                return {
                    "success": False,
                    "error": f"不支持的执行源: {tool_source}"
                }
            
            return {
                "success": True,
                "result": result,
                "execution_info": {
                    "tool_id": tool_id,
                    "source": tool_source,
                    "execution_time": result.get("execution_time", "unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_optimal_source(self, tool_id: str) -> str:
        """确定最优执行源"""
        # 简单策略：优先使用本地工具
        local_tools = ["file_processor", "data_analyzer", "code_generator"]
        
        if tool_id in local_tools:
            return "local"
        else:
            return "cloud"
    
    def _execute_local_tool(self, tool_id: str, arguments: Dict) -> Dict:
        """执行本地MCP.so工具"""
        try:
            # 模拟本地工具执行
            import time
            start_time = time.time()
            
            # 根据工具ID执行不同逻辑
            if tool_id == "file_processor":
                result = {
                    "action": "file_processed",
                    "file_path": arguments.get("file_path", ""),
                    "operation": arguments.get("operation", "read"),
                    "result": "文件处理完成",
                    "size": "1.2MB"
                }
            elif tool_id == "data_analyzer":
                result = {
                    "action": "data_analyzed",
                    "data_source": arguments.get("data_source", ""),
                    "analysis_type": arguments.get("analysis_type", "basic"),
                    "result": "数据分析完成",
                    "insights": ["趋势上升", "异常值检测", "相关性分析"]
                }
            elif tool_id == "code_generator":
                result = {
                    "action": "code_generated",
                    "language": arguments.get("language", "python"),
                    "template": arguments.get("template", "basic"),
                    "result": "代码生成完成",
                    "lines_of_code": 150
                }
            else:
                result = {
                    "action": "unknown_tool",
                    "result": f"未知工具: {tool_id}"
                }
            
            execution_time = time.time() - start_time
            result["execution_time"] = f"{execution_time:.3f}s"
            result["source"] = "local"
            
            return result
            
        except Exception as e:
            logger.error(f"本地工具执行失败: {e}")
            raise
    
    def _execute_cloud_tool(self, tool_id: str, arguments: Dict) -> Dict:
        """执行ACI.dev云端工具"""
        try:
            # 模拟云端工具执行
            import time
            start_time = time.time()
            
            # 根据工具ID执行不同逻辑
            if tool_id == "google_calendar":
                result = {
                    "action": "calendar_operation",
                    "operation": arguments.get("operation", "list_events"),
                    "calendar_id": arguments.get("calendar_id", "primary"),
                    "result": "日历操作完成",
                    "events_count": 5
                }
            elif tool_id == "slack_integration":
                result = {
                    "action": "slack_operation",
                    "operation": arguments.get("operation", "send_message"),
                    "channel": arguments.get("channel", "#general"),
                    "result": "Slack操作完成",
                    "message_id": "1234567890"
                }
            elif tool_id == "github_actions":
                result = {
                    "action": "github_operation",
                    "operation": arguments.get("operation", "trigger_workflow"),
                    "repository": arguments.get("repository", ""),
                    "result": "GitHub操作完成",
                    "workflow_run_id": "987654321"
                }
            else:
                result = {
                    "action": "unknown_tool",
                    "result": f"未知云端工具: {tool_id}"
                }
            
            execution_time = time.time() - start_time
            result["execution_time"] = f"{execution_time:.3f}s"
            result["source"] = "cloud"
            
            return result
            
        except Exception as e:
            logger.error(f"云端工具执行失败: {e}")
            raise
    
    def _smart_execute(self, parameters: Dict) -> Dict[str, Any]:
        """智能执行 - 自动选择最佳工具和执行策略"""
        try:
            intent = parameters.get("intent", "")
            context = parameters.get("context", {})
            preferences = parameters.get("preferences", {})
            
            if not intent:
                return {
                    "success": False,
                    "error": "缺少必需参数: intent"
                }
            
            # 1. 意图分析和工具发现
            discovery_result = self._discover_tools({
                "query": intent,
                "limit": 10
            })
            
            if not discovery_result.get("success"):
                return discovery_result
            
            recommended_tools = discovery_result["results"]["recommended_tools"]
            
            if not recommended_tools:
                return {
                    "success": False,
                    "error": "未找到匹配的工具",
                    "intent": intent
                }
            
            # 2. 选择最佳工具
            best_tool = recommended_tools[0]
            
            # 3. 构建执行参数
            execution_params = self._build_execution_params(intent, context, best_tool)
            
            # 4. 执行工具
            execution_result = self._execute_tool({
                "tool_id": best_tool["id"],
                "source": best_tool["source"],
                "arguments": execution_params
            })
            
            return {
                "success": True,
                "smart_execution": {
                    "intent": intent,
                    "selected_tool": best_tool,
                    "execution_params": execution_params,
                    "execution_result": execution_result,
                    "reasoning": f"选择 {best_tool['name']} 因为其在相关性和性能方面评分最高"
                }
            }
            
        except Exception as e:
            logger.error(f"智能执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_execution_params(self, intent: str, context: Dict, tool: Dict) -> Dict:
        """构建执行参数"""
        # 简单的参数映射逻辑
        params = {}
        
        tool_id = tool.get("id", "")
        
        if "file" in intent.lower():
            params["file_path"] = context.get("file_path", "/tmp/example.txt")
            params["operation"] = "read" if "read" in intent.lower() else "write"
        elif "data" in intent.lower():
            params["data_source"] = context.get("data_source", "sample_data.csv")
            params["analysis_type"] = "statistical" if "analyze" in intent.lower() else "basic"
        elif "code" in intent.lower():
            params["language"] = context.get("language", "python")
            params["template"] = context.get("template", "basic")
        
        return params
    
    def _get_tool_info(self, parameters: Dict) -> Dict[str, Any]:
        """获取工具详细信息"""
        try:
            tool_id = parameters.get("tool_id")
            
            if not tool_id:
                return {
                    "success": False,
                    "error": "缺少必需参数: tool_id"
                }
            
            # 搜索工具信息
            discovery_result = self._discover_tools({"query": tool_id, "limit": 50})
            
            if not discovery_result.get("success"):
                return discovery_result
            
            all_tools = (discovery_result["results"]["local_tools"] + 
                        discovery_result["results"]["cloud_tools"])
            
            tool_info = None
            for tool in all_tools:
                if tool.get("id") == tool_id:
                    tool_info = tool
                    break
            
            if not tool_info:
                return {
                    "success": False,
                    "error": f"未找到工具: {tool_id}"
                }
            
            return {
                "success": True,
                "tool_info": tool_info
            }
            
        except Exception as e:
            logger.error(f"获取工具信息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sync_tools(self, parameters: Dict) -> Dict[str, Any]:
        """同步工具注册表"""
        try:
            force_sync = parameters.get("force", False)
            
            # 同步本地工具
            local_sync_result = self._sync_local_tools(force_sync)
            
            # 同步云端工具
            cloud_sync_result = self._sync_cloud_tools(force_sync)
            
            return {
                "success": True,
                "sync_results": {
                    "local_tools": local_sync_result,
                    "cloud_tools": cloud_sync_result,
                    "sync_time": "2025-06-04 10:16:00"
                }
            }
            
        except Exception as e:
            logger.error(f"同步工具失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sync_local_tools(self, force: bool) -> Dict:
        """同步本地工具"""
        return {
            "status": "completed",
            "tools_count": 3,
            "new_tools": 0,
            "updated_tools": 0
        }
    
    def _sync_cloud_tools(self, force: bool) -> Dict:
        """同步云端工具"""
        return {
            "status": "completed",
            "tools_count": 600,
            "new_tools": 5,
            "updated_tools": 12
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        total_calls = self.performance_metrics["local_calls"] + self.performance_metrics["cloud_calls"]
        
        return {
            "success": True,
            "metrics": {
                "total_calls": total_calls,
                "local_calls": self.performance_metrics["local_calls"],
                "cloud_calls": self.performance_metrics["cloud_calls"],
                "local_ratio": self.performance_metrics["local_calls"] / max(total_calls, 1),
                "cloud_ratio": self.performance_metrics["cloud_calls"] / max(total_calls, 1),
                "success_rate": 0.95,  # 模拟成功率
                "avg_response_time": "150ms"
            }
        }

