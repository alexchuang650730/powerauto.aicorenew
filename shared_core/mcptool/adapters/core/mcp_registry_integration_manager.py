#!/usr/bin/env python3
"""
MCP註冊表整合管理器

整合現有的統一適配器註冊表，確保所有新舊MCP都能正確註冊，
並提供高效的意圖匹配和工作流整合功能。

作者: PowerAutomation團隊
版本: 1.0.0
日期: 2025-06-08
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Type, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 導入現有組件
try:
    from mcptool.adapters.core.unified_adapter_registry import UnifiedAdapterRegistry
    from mcptool.adapters.intelligent_intent_processor import IntelligentIntentProcessor
    from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError as e:
    logging.warning(f"導入現有組件失敗: {e}")
    # 創建Mock類
    class UnifiedAdapterRegistry:
        def __init__(self):
            self.registered_adapters = {}
        def list_adapters(self):
            return []
    
    class IntelligentIntentProcessor:
        def __init__(self):
            pass
    
    class IntelligentWorkflowEngineMCP:
        def __init__(self):
            pass
    
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name

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

logger = logging.getLogger("mcp_registry_integration_manager")

class MCPCapability(Enum):
    """MCP能力枚舉"""
    DATA_PROCESSING = "data_processing"
    MEMORY_MANAGEMENT = "memory_management"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    AI_ENHANCEMENT = "ai_enhancement"
    MONITORING = "monitoring"
    BACKUP_RECOVERY = "backup_recovery"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    DEVELOPMENT = "development"

class IntentCategory(Enum):
    """意圖分類枚舉"""
    DATA_OPERATION = "data_operation"
    MEMORY_QUERY = "memory_query"
    WORKFLOW_EXECUTION = "workflow_execution"
    SYSTEM_MONITORING = "system_monitoring"
    BACKUP_RESTORE = "backup_restore"
    OPTIMIZATION_REQUEST = "optimization_request"
    DEVELOPMENT_TASK = "development_task"
    INTEGRATION_SETUP = "integration_setup"

class MCPRegistryIntegrationManager(BaseMCP):
    """MCP註冊表整合管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("MCPRegistryIntegrationManager")
        
        # 配置參數
        self.config = config or {}
        
        # 初始化現有組件
        self.adapter_registry = UnifiedAdapterRegistry()
        self.intent_processor = IntelligentIntentProcessor()
        self.workflow_engine = IntelligentWorkflowEngineMCP()
        
        # MCP能力映射
        self.capability_mapping = {}
        self.intent_mcp_mapping = {}
        
        # 性能統計
        self.performance_stats = {
            "total_registrations": 0,
            "successful_matches": 0,
            "failed_matches": 0,
            "average_match_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # 意圖匹配緩存
        self.intent_cache = {}
        self.capability_cache = {}
        
        # MCP操作映射
        self.operations = {
            "register_mcp": self.register_mcp,
            "match_intent": self.match_intent_to_mcp,
            "get_mcp_capabilities": self.get_mcp_capabilities,
            "list_registered_mcps": self.list_registered_mcps,
            "optimize_matching": self.optimize_matching,
            "get_performance_stats": self.get_performance_stats,
            "refresh_registry": self.refresh_registry,
            "validate_mcps": self.validate_mcps,
            "export_registry": self.export_registry,
            "import_registry": self.import_registry
        }
        
        # 初始化系統
        self._initialize_system()
        
        log_info(LogCategory.MCP, "MCP註冊表整合管理器初始化完成", {
            "registered_mcps": len(self.adapter_registry.registered_adapters),
            "operations": list(self.operations.keys())
        })
    
    def _initialize_system(self):
        """初始化系統"""
        try:
            # 註冊新創建的MCP組件
            self._register_new_mcps()
            
            # 構建能力映射
            self._build_capability_mapping()
            
            # 構建意圖映射
            self._build_intent_mapping()
            
            log_info(LogCategory.MCP, "MCP註冊表系統初始化完成", {
                "total_mcps": len(self.adapter_registry.registered_adapters),
                "capability_mappings": len(self.capability_mapping),
                "intent_mappings": len(self.intent_mcp_mapping)
            })
            
        except Exception as e:
            log_error(LogCategory.MCP, "MCP註冊表系統初始化失敗", {"error": str(e)})
    
    def _register_new_mcps(self):
        """註冊新創建的MCP組件"""
        new_mcps = [
            {
                "name": "CloudEdgeDataMCP",
                "file_path": "mcptool/adapters/cloud_edge_data_mcp.py",
                "capabilities": [MCPCapability.DATA_PROCESSING, MCPCapability.INTEGRATION],
                "description": "端雲協同數據管理",
                "intents": ["data_collection", "data_processing", "cloud_sync"]
            },
            {
                "name": "RLSRTDataFlowMCP",
                "file_path": "mcptool/adapters/rl_srt_dataflow_mcp.py",
                "capabilities": [MCPCapability.AI_ENHANCEMENT, MCPCapability.DATA_PROCESSING],
                "description": "RL-SRT數據流處理",
                "intents": ["model_training", "data_flow", "ai_optimization"]
            },
            {
                "name": "UnifiedMemoryMCP",
                "file_path": "mcptool/adapters/unified_memory_mcp.py",
                "capabilities": [MCPCapability.MEMORY_MANAGEMENT, MCPCapability.DATA_PROCESSING],
                "description": "統一記憶系統管理",
                "intents": ["memory_query", "memory_management", "data_retrieval"]
            },
            {
                "name": "ContextMonitorMCP",
                "file_path": "mcptool/adapters/context_monitor_mcp.py",
                "capabilities": [MCPCapability.MONITORING, MCPCapability.OPTIMIZATION],
                "description": "上下文監控和優化",
                "intents": ["context_monitoring", "performance_optimization", "alert_management"]
            }
        ]
        
        for mcp_info in new_mcps:
            self._register_mcp_info(mcp_info)
            self.performance_stats["total_registrations"] += 1
    
    def _register_mcp_info(self, mcp_info: Dict[str, Any]):
        """註冊MCP信息"""
        try:
            mcp_id = mcp_info["name"].lower()
            
            # 檢查是否已註冊
            if mcp_id in self.adapter_registry.registered_adapters:
                log_info(LogCategory.MCP, f"MCP已存在，更新信息: {mcp_id}", mcp_info)
            
            # 註冊到統一適配器註冊表
            self.adapter_registry.registered_adapters[mcp_id] = {
                "name": mcp_info["name"],
                "file_path": mcp_info["file_path"],
                "capabilities": [cap.value for cap in mcp_info["capabilities"]],
                "description": mcp_info["description"],
                "intents": mcp_info["intents"],
                "registered_at": datetime.now().isoformat(),
                "status": "active",
                "version": "1.0.0"
            }
            
            # 更新能力映射
            for capability in mcp_info["capabilities"]:
                if capability not in self.capability_mapping:
                    self.capability_mapping[capability] = []
                self.capability_mapping[capability].append(mcp_id)
            
            # 更新意圖映射
            for intent in mcp_info["intents"]:
                if intent not in self.intent_mcp_mapping:
                    self.intent_mcp_mapping[intent] = []
                self.intent_mcp_mapping[intent].append(mcp_id)
            
            log_info(LogCategory.MCP, f"MCP註冊成功: {mcp_id}", {
                "capabilities": len(mcp_info["capabilities"]),
                "intents": len(mcp_info["intents"])
            })
            
        except Exception as e:
            log_error(LogCategory.MCP, f"MCP註冊失敗: {mcp_info.get('name', 'unknown')}", {"error": str(e)})
    
    def _build_capability_mapping(self):
        """構建能力映射"""
        try:
            # 清空現有映射
            self.capability_mapping.clear()
            
            # 遍歷所有註冊的MCP
            for mcp_id, mcp_info in self.adapter_registry.registered_adapters.items():
                capabilities = mcp_info.get("capabilities", [])
                
                for capability in capabilities:
                    if capability not in self.capability_mapping:
                        self.capability_mapping[capability] = []
                    self.capability_mapping[capability].append(mcp_id)
            
            log_info(LogCategory.MCP, "能力映射構建完成", {
                "total_capabilities": len(self.capability_mapping),
                "mappings": {cap: len(mcps) for cap, mcps in self.capability_mapping.items()}
            })
            
        except Exception as e:
            log_error(LogCategory.MCP, "能力映射構建失敗", {"error": str(e)})
    
    def _build_intent_mapping(self):
        """構建意圖映射"""
        try:
            # 清空現有映射
            self.intent_mcp_mapping.clear()
            
            # 遍歷所有註冊的MCP
            for mcp_id, mcp_info in self.adapter_registry.registered_adapters.items():
                intents = mcp_info.get("intents", [])
                
                for intent in intents:
                    if intent not in self.intent_mcp_mapping:
                        self.intent_mcp_mapping[intent] = []
                    self.intent_mcp_mapping[intent].append(mcp_id)
            
            log_info(LogCategory.MCP, "意圖映射構建完成", {
                "total_intents": len(self.intent_mcp_mapping),
                "mappings": {intent: len(mcps) for intent, mcps in self.intent_mcp_mapping.items()}
            })
            
        except Exception as e:
            log_error(LogCategory.MCP, "意圖映射構建失敗", {"error": str(e)})
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP標準處理接口"""
        try:
            operation = input_data.get("operation", "list_registered_mcps")
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
            
            log_info(LogCategory.MCP, f"MCP註冊表管理器操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "MCP註冊表管理器處理失敗", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"處理失敗: {str(e)}"
            }
    
    @performance_monitor("register_mcp")
    async def register_mcp(self, mcp_info: Dict[str, Any]) -> Dict[str, Any]:
        """註冊MCP"""
        try:
            # 驗證MCP信息
            validation_result = self._validate_mcp_info(mcp_info)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": f"MCP信息驗證失敗: {validation_result['errors']}"
                }
            
            # 註冊MCP
            self._register_mcp_info(mcp_info)
            
            # 重新構建映射
            self._build_capability_mapping()
            self._build_intent_mapping()
            
            # 清空緩存
            self.intent_cache.clear()
            self.capability_cache.clear()
            
            self.performance_stats["total_registrations"] += 1
            
            return {
                "status": "success",
                "message": f"MCP註冊成功: {mcp_info['name']}",
                "mcp_id": mcp_info["name"].lower()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"MCP註冊失敗: {str(e)}"
            }
    
    def _validate_mcp_info(self, mcp_info: Dict[str, Any]) -> Dict[str, Any]:
        """驗證MCP信息"""
        errors = []
        
        # 檢查必需字段
        required_fields = ["name", "file_path", "capabilities", "description"]
        for field in required_fields:
            if field not in mcp_info:
                errors.append(f"缺少必需字段: {field}")
        
        # 檢查能力是否有效
        if "capabilities" in mcp_info:
            for cap in mcp_info["capabilities"]:
                if isinstance(cap, str):
                    try:
                        MCPCapability(cap)
                    except ValueError:
                        errors.append(f"無效的能力: {cap}")
                elif not isinstance(cap, MCPCapability):
                    errors.append(f"能力類型錯誤: {cap}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @performance_monitor("match_intent")
    async def match_intent_to_mcp(self, user_intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """匹配用戶意圖到MCP"""
        try:
            start_time = datetime.now()
            
            # 檢查緩存
            cache_key = f"{user_intent}_{hash(str(context))}"
            if cache_key in self.intent_cache:
                self.performance_stats["cache_hits"] += 1
                return self.intent_cache[cache_key]
            
            self.performance_stats["cache_misses"] += 1
            
            # 分析用戶意圖
            intent_analysis = await self._analyze_user_intent(user_intent, context)
            
            # 匹配MCP
            matched_mcps = await self._match_mcps_by_intent(intent_analysis)
            
            # 排序和優化
            optimized_mcps = await self._optimize_mcp_selection(matched_mcps, intent_analysis)
            
            # 計算匹配時間
            match_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(match_time, len(optimized_mcps) > 0)
            
            result = {
                "status": "success",
                "user_intent": user_intent,
                "intent_analysis": intent_analysis,
                "matched_mcps": optimized_mcps,
                "match_time": match_time,
                "total_candidates": len(matched_mcps)
            }
            
            # 緩存結果
            self.intent_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.performance_stats["failed_matches"] += 1
            return {
                "status": "error",
                "message": f"意圖匹配失敗: {str(e)}"
            }
    
    async def _analyze_user_intent(self, user_intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """分析用戶意圖"""
        try:
            # 關鍵詞提取
            keywords = self._extract_keywords(user_intent)
            
            # 意圖分類
            intent_category = self._classify_intent(user_intent, keywords)
            
            # 所需能力推斷
            required_capabilities = self._infer_capabilities(user_intent, keywords, intent_category)
            
            # 優先級評估
            priority = self._assess_priority(user_intent, context)
            
            return {
                "original_intent": user_intent,
                "keywords": keywords,
                "intent_category": intent_category.value if intent_category else "unknown",
                "required_capabilities": [cap.value for cap in required_capabilities],
                "priority": priority,
                "context": context or {}
            }
            
        except Exception as e:
            log_error(LogCategory.MCP, "用戶意圖分析失敗", {"intent": user_intent, "error": str(e)})
            return {
                "original_intent": user_intent,
                "keywords": [],
                "intent_category": "unknown",
                "required_capabilities": [],
                "priority": "medium",
                "context": context or {}
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        import re
        
        # 簡單的關鍵詞提取
        keywords = []
        
        # 數據相關關鍵詞
        data_keywords = ["數據", "data", "處理", "process", "存儲", "storage", "同步", "sync"]
        memory_keywords = ["記憶", "memory", "查詢", "query", "檢索", "search", "存取", "access"]
        monitor_keywords = ["監控", "monitor", "警告", "alert", "性能", "performance", "狀態", "status"]
        backup_keywords = ["備份", "backup", "恢復", "restore", "歸檔", "archive"]
        
        text_lower = text.lower()
        
        for keyword in data_keywords + memory_keywords + monitor_keywords + backup_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return list(set(keywords))
    
    def _classify_intent(self, user_intent: str, keywords: List[str]) -> Optional[IntentCategory]:
        """分類用戶意圖"""
        text_lower = user_intent.lower()
        
        # 基於關鍵詞的簡單分類
        if any(kw in text_lower for kw in ["數據", "data", "處理", "process"]):
            return IntentCategory.DATA_OPERATION
        elif any(kw in text_lower for kw in ["記憶", "memory", "查詢", "query"]):
            return IntentCategory.MEMORY_QUERY
        elif any(kw in text_lower for kw in ["工作流", "workflow", "執行", "execute"]):
            return IntentCategory.WORKFLOW_EXECUTION
        elif any(kw in text_lower for kw in ["監控", "monitor", "狀態", "status"]):
            return IntentCategory.SYSTEM_MONITORING
        elif any(kw in text_lower for kw in ["備份", "backup", "恢復", "restore"]):
            return IntentCategory.BACKUP_RESTORE
        elif any(kw in text_lower for kw in ["優化", "optimize", "性能", "performance"]):
            return IntentCategory.OPTIMIZATION_REQUEST
        elif any(kw in text_lower for kw in ["開發", "develop", "創建", "create"]):
            return IntentCategory.DEVELOPMENT_TASK
        elif any(kw in text_lower for kw in ["整合", "integrate", "連接", "connect"]):
            return IntentCategory.INTEGRATION_SETUP
        
        return None
    
    def _infer_capabilities(self, user_intent: str, keywords: List[str], intent_category: Optional[IntentCategory]) -> List[MCPCapability]:
        """推斷所需能力"""
        capabilities = []
        
        # 基於意圖分類推斷能力
        if intent_category:
            category_capability_map = {
                IntentCategory.DATA_OPERATION: [MCPCapability.DATA_PROCESSING],
                IntentCategory.MEMORY_QUERY: [MCPCapability.MEMORY_MANAGEMENT],
                IntentCategory.WORKFLOW_EXECUTION: [MCPCapability.WORKFLOW_ORCHESTRATION],
                IntentCategory.SYSTEM_MONITORING: [MCPCapability.MONITORING],
                IntentCategory.BACKUP_RESTORE: [MCPCapability.BACKUP_RECOVERY],
                IntentCategory.OPTIMIZATION_REQUEST: [MCPCapability.OPTIMIZATION],
                IntentCategory.DEVELOPMENT_TASK: [MCPCapability.DEVELOPMENT],
                IntentCategory.INTEGRATION_SETUP: [MCPCapability.INTEGRATION]
            }
            
            capabilities.extend(category_capability_map.get(intent_category, []))
        
        # 基於關鍵詞推斷額外能力
        text_lower = user_intent.lower()
        if any(kw in text_lower for kw in ["ai", "智能", "學習", "training"]):
            capabilities.append(MCPCapability.AI_ENHANCEMENT)
        if any(kw in text_lower for kw in ["安全", "security", "權限", "permission"]):
            capabilities.append(MCPCapability.SECURITY)
        
        return list(set(capabilities))
    
    def _assess_priority(self, user_intent: str, context: Dict[str, Any] = None) -> str:
        """評估優先級"""
        text_lower = user_intent.lower()
        
        # 高優先級關鍵詞
        if any(kw in text_lower for kw in ["緊急", "urgent", "立即", "immediately", "critical"]):
            return "high"
        
        # 低優先級關鍵詞
        if any(kw in text_lower for kw in ["稍後", "later", "可選", "optional", "建議", "suggest"]):
            return "low"
        
        return "medium"
    
    async def _match_mcps_by_intent(self, intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根據意圖匹配MCP"""
        matched_mcps = []
        
        try:
            required_capabilities = intent_analysis["required_capabilities"]
            keywords = intent_analysis["keywords"]
            
            # 遍歷所有註冊的MCP
            for mcp_id, mcp_info in self.adapter_registry.registered_adapters.items():
                match_score = self._calculate_match_score(mcp_info, intent_analysis)
                
                if match_score > 0:
                    matched_mcps.append({
                        "mcp_id": mcp_id,
                        "mcp_info": mcp_info,
                        "match_score": match_score,
                        "match_reasons": self._get_match_reasons(mcp_info, intent_analysis)
                    })
            
            # 按匹配分數排序
            matched_mcps.sort(key=lambda x: x["match_score"], reverse=True)
            
            return matched_mcps
            
        except Exception as e:
            log_error(LogCategory.MCP, "MCP匹配失敗", {"error": str(e)})
            return []
    
    def _calculate_match_score(self, mcp_info: Dict[str, Any], intent_analysis: Dict[str, Any]) -> float:
        """計算匹配分數"""
        score = 0.0
        
        # 能力匹配分數 (權重: 0.5)
        mcp_capabilities = set(mcp_info.get("capabilities", []))
        required_capabilities = set(intent_analysis["required_capabilities"])
        
        if required_capabilities:
            capability_match = len(mcp_capabilities & required_capabilities) / len(required_capabilities)
            score += capability_match * 0.5
        
        # 意圖匹配分數 (權重: 0.3)
        mcp_intents = set(mcp_info.get("intents", []))
        keywords = set(intent_analysis["keywords"])
        
        intent_match = 0.0
        for intent in mcp_intents:
            if any(keyword in intent.lower() for keyword in keywords):
                intent_match += 1
        
        if mcp_intents:
            intent_match = intent_match / len(mcp_intents)
            score += intent_match * 0.3
        
        # 狀態分數 (權重: 0.2)
        if mcp_info.get("status") == "active":
            score += 0.2
        
        return score
    
    def _get_match_reasons(self, mcp_info: Dict[str, Any], intent_analysis: Dict[str, Any]) -> List[str]:
        """獲取匹配原因"""
        reasons = []
        
        # 能力匹配原因
        mcp_capabilities = set(mcp_info.get("capabilities", []))
        required_capabilities = set(intent_analysis["required_capabilities"])
        matched_capabilities = mcp_capabilities & required_capabilities
        
        if matched_capabilities:
            reasons.append(f"能力匹配: {', '.join(matched_capabilities)}")
        
        # 意圖匹配原因
        mcp_intents = mcp_info.get("intents", [])
        keywords = intent_analysis["keywords"]
        
        for intent in mcp_intents:
            for keyword in keywords:
                if keyword in intent.lower():
                    reasons.append(f"意圖匹配: {intent} (關鍵詞: {keyword})")
        
        return reasons
    
    async def _optimize_mcp_selection(self, matched_mcps: List[Dict[str, Any]], intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """優化MCP選擇"""
        try:
            # 取前5個最佳匹配
            top_mcps = matched_mcps[:5]
            
            # 添加執行建議
            for mcp in top_mcps:
                mcp["execution_suggestion"] = self._generate_execution_suggestion(mcp, intent_analysis)
            
            return top_mcps
            
        except Exception as e:
            log_error(LogCategory.MCP, "MCP選擇優化失敗", {"error": str(e)})
            return matched_mcps[:3]  # 返回前3個作為備用
    
    def _generate_execution_suggestion(self, mcp: Dict[str, Any], intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成執行建議"""
        return {
            "recommended_operation": self._suggest_operation(mcp["mcp_info"], intent_analysis),
            "estimated_time": self._estimate_execution_time(mcp["mcp_info"], intent_analysis),
            "prerequisites": self._check_prerequisites(mcp["mcp_info"], intent_analysis),
            "confidence": mcp["match_score"]
        }
    
    def _suggest_operation(self, mcp_info: Dict[str, Any], intent_analysis: Dict[str, Any]) -> str:
        """建議操作"""
        # 基於MCP類型和意圖分析建議操作
        mcp_name = mcp_info.get("name", "").lower()
        intent_category = intent_analysis.get("intent_category", "")
        
        if "memory" in mcp_name and "query" in intent_category:
            return "query_memory"
        elif "data" in mcp_name and "data_operation" in intent_category:
            return "process_data"
        elif "monitor" in mcp_name:
            return "start_monitoring"
        elif "workflow" in mcp_name:
            return "execute_workflow"
        
        return "process"  # 默認操作
    
    def _estimate_execution_time(self, mcp_info: Dict[str, Any], intent_analysis: Dict[str, Any]) -> str:
        """估算執行時間"""
        # 簡單的時間估算邏輯
        priority = intent_analysis.get("priority", "medium")
        
        if priority == "high":
            return "< 1 minute"
        elif priority == "low":
            return "5-10 minutes"
        else:
            return "1-5 minutes"
    
    def _check_prerequisites(self, mcp_info: Dict[str, Any], intent_analysis: Dict[str, Any]) -> List[str]:
        """檢查前置條件"""
        prerequisites = []
        
        # 基於MCP類型檢查前置條件
        capabilities = mcp_info.get("capabilities", [])
        
        if "data_processing" in capabilities:
            prerequisites.append("確保數據源可訪問")
        if "memory_management" in capabilities:
            prerequisites.append("檢查記憶系統狀態")
        if "monitoring" in capabilities:
            prerequisites.append("確認監控權限")
        
        return prerequisites
    
    def _update_performance_stats(self, match_time: float, success: bool):
        """更新性能統計"""
        if success:
            self.performance_stats["successful_matches"] += 1
        else:
            self.performance_stats["failed_matches"] += 1
        
        # 更新平均匹配時間
        total_matches = self.performance_stats["successful_matches"] + self.performance_stats["failed_matches"]
        current_avg = self.performance_stats["average_match_time"]
        self.performance_stats["average_match_time"] = (current_avg * (total_matches - 1) + match_time) / total_matches
    
    def get_mcp_capabilities(self, mcp_id: str = None) -> Dict[str, Any]:
        """獲取MCP能力"""
        try:
            if mcp_id:
                # 獲取特定MCP的能力
                if mcp_id in self.adapter_registry.registered_adapters:
                    mcp_info = self.adapter_registry.registered_adapters[mcp_id]
                    return {
                        "status": "success",
                        "mcp_id": mcp_id,
                        "capabilities": mcp_info.get("capabilities", []),
                        "intents": mcp_info.get("intents", []),
                        "description": mcp_info.get("description", "")
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"MCP不存在: {mcp_id}"
                    }
            else:
                # 獲取所有MCP的能力概覽
                capabilities_overview = {}
                for mcp_id, mcp_info in self.adapter_registry.registered_adapters.items():
                    capabilities_overview[mcp_id] = {
                        "capabilities": mcp_info.get("capabilities", []),
                        "intents": mcp_info.get("intents", [])
                    }
                
                return {
                    "status": "success",
                    "capabilities_overview": capabilities_overview,
                    "total_mcps": len(capabilities_overview)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取MCP能力失敗: {str(e)}"
            }
    
    def list_registered_mcps(self, category: str = None, status: str = None) -> Dict[str, Any]:
        """列出註冊的MCP"""
        try:
            mcps = []
            
            for mcp_id, mcp_info in self.adapter_registry.registered_adapters.items():
                # 過濾條件
                if category and mcp_info.get("category") != category:
                    continue
                if status and mcp_info.get("status") != status:
                    continue
                
                mcps.append({
                    "mcp_id": mcp_id,
                    "name": mcp_info.get("name", mcp_id),
                    "description": mcp_info.get("description", ""),
                    "capabilities": mcp_info.get("capabilities", []),
                    "intents": mcp_info.get("intents", []),
                    "status": mcp_info.get("status", "unknown"),
                    "registered_at": mcp_info.get("registered_at", "")
                })
            
            return {
                "status": "success",
                "mcps": mcps,
                "total_count": len(mcps),
                "filter_applied": {
                    "category": category,
                    "status": status
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"列出MCP失敗: {str(e)}"
            }
    
    async def optimize_matching(self, optimization_type: str = "cache") -> Dict[str, Any]:
        """優化匹配性能"""
        try:
            optimization_results = []
            
            if optimization_type in ["cache", "all"]:
                # 清理過期緩存
                cache_cleaned = self._clean_expired_cache()
                optimization_results.append({
                    "type": "cache_cleanup",
                    "cleaned_entries": cache_cleaned
                })
            
            if optimization_type in ["mapping", "all"]:
                # 重建映射
                self._build_capability_mapping()
                self._build_intent_mapping()
                optimization_results.append({
                    "type": "mapping_rebuild",
                    "capability_mappings": len(self.capability_mapping),
                    "intent_mappings": len(self.intent_mcp_mapping)
                })
            
            if optimization_type in ["stats", "all"]:
                # 重置性能統計
                old_stats = self.performance_stats.copy()
                self._reset_performance_stats()
                optimization_results.append({
                    "type": "stats_reset",
                    "old_stats": old_stats
                })
            
            return {
                "status": "success",
                "optimization_type": optimization_type,
                "optimization_results": optimization_results,
                "optimization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"匹配優化失敗: {str(e)}"
            }
    
    def _clean_expired_cache(self) -> int:
        """清理過期緩存"""
        # 簡單實現：清空所有緩存
        cache_size = len(self.intent_cache) + len(self.capability_cache)
        self.intent_cache.clear()
        self.capability_cache.clear()
        return cache_size
    
    def _reset_performance_stats(self):
        """重置性能統計"""
        self.performance_stats = {
            "total_registrations": self.performance_stats["total_registrations"],  # 保留註冊數
            "successful_matches": 0,
            "failed_matches": 0,
            "average_match_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """獲取性能統計"""
        return {
            "status": "success",
            "performance_stats": self.performance_stats.copy(),
            "cache_stats": {
                "intent_cache_size": len(self.intent_cache),
                "capability_cache_size": len(self.capability_cache)
            },
            "registry_stats": {
                "total_mcps": len(self.adapter_registry.registered_adapters),
                "capability_mappings": len(self.capability_mapping),
                "intent_mappings": len(self.intent_mcp_mapping)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def refresh_registry(self) -> Dict[str, Any]:
        """刷新註冊表"""
        try:
            # 重新發現適配器
            old_count = len(self.adapter_registry.registered_adapters)
            self.adapter_registry._discover_adapters()
            new_count = len(self.adapter_registry.registered_adapters)
            
            # 重新註冊新MCP
            self._register_new_mcps()
            
            # 重建映射
            self._build_capability_mapping()
            self._build_intent_mapping()
            
            # 清空緩存
            self.intent_cache.clear()
            self.capability_cache.clear()
            
            return {
                "status": "success",
                "message": "註冊表刷新完成",
                "old_mcp_count": old_count,
                "new_mcp_count": new_count,
                "refresh_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"註冊表刷新失敗: {str(e)}"
            }
    
    async def validate_mcps(self) -> Dict[str, Any]:
        """驗證MCP"""
        try:
            validation_results = []
            
            for mcp_id, mcp_info in self.adapter_registry.registered_adapters.items():
                validation_result = await self._validate_single_mcp(mcp_id, mcp_info)
                validation_results.append(validation_result)
            
            # 統計驗證結果
            valid_count = sum(1 for result in validation_results if result["valid"])
            invalid_count = len(validation_results) - valid_count
            
            return {
                "status": "success",
                "validation_results": validation_results,
                "summary": {
                    "total_mcps": len(validation_results),
                    "valid_mcps": valid_count,
                    "invalid_mcps": invalid_count
                },
                "validation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"MCP驗證失敗: {str(e)}"
            }
    
    async def _validate_single_mcp(self, mcp_id: str, mcp_info: Dict[str, Any]) -> Dict[str, Any]:
        """驗證單個MCP"""
        validation_issues = []
        
        # 檢查文件是否存在
        file_path = mcp_info.get("file_path", "")
        if file_path and not Path(file_path).exists():
            validation_issues.append(f"文件不存在: {file_path}")
        
        # 檢查必需字段
        required_fields = ["name", "capabilities", "description"]
        for field in required_fields:
            if not mcp_info.get(field):
                validation_issues.append(f"缺少字段: {field}")
        
        # 檢查狀態
        status = mcp_info.get("status", "unknown")
        if status not in ["active", "inactive", "error", "file_only"]:
            validation_issues.append(f"無效狀態: {status}")
        
        return {
            "mcp_id": mcp_id,
            "valid": len(validation_issues) == 0,
            "issues": validation_issues
        }
    
    async def export_registry(self, export_path: str = None) -> Dict[str, Any]:
        """導出註冊表"""
        try:
            if export_path is None:
                export_path = f"mcp_registry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "registry_version": "1.0.0",
                "registered_adapters": self.adapter_registry.registered_adapters,
                "capability_mapping": {k: v for k, v in self.capability_mapping.items()},
                "intent_mcp_mapping": self.intent_mcp_mapping,
                "performance_stats": self.performance_stats
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "export_path": export_path,
                "exported_mcps": len(self.adapter_registry.registered_adapters),
                "export_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"導出註冊表失敗: {str(e)}"
            }
    
    async def import_registry(self, import_path: str) -> Dict[str, Any]:
        """導入註冊表"""
        try:
            if not Path(import_path).exists():
                return {
                    "status": "error",
                    "message": f"導入文件不存在: {import_path}"
                }
            
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 備份當前註冊表
            backup_data = {
                "registered_adapters": self.adapter_registry.registered_adapters.copy(),
                "capability_mapping": self.capability_mapping.copy(),
                "intent_mcp_mapping": self.intent_mcp_mapping.copy()
            }
            
            # 導入數據
            imported_adapters = import_data.get("registered_adapters", {})
            self.adapter_registry.registered_adapters.update(imported_adapters)
            
            # 重建映射
            self._build_capability_mapping()
            self._build_intent_mapping()
            
            # 清空緩存
            self.intent_cache.clear()
            self.capability_cache.clear()
            
            return {
                "status": "success",
                "imported_mcps": len(imported_adapters),
                "total_mcps": len(self.adapter_registry.registered_adapters),
                "import_time": datetime.now().isoformat(),
                "backup_data": backup_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"導入註冊表失敗: {str(e)}"
            }

# 創建全局實例
mcp_registry_integration_manager = MCPRegistryIntegrationManager()

# 導出主要接口
__all__ = [
    'MCPRegistryIntegrationManager',
    'MCPCapability',
    'IntentCategory',
    'mcp_registry_integration_manager'
]

if __name__ == "__main__":
    # 測試MCP功能
    test_data = {
        "operation": "list_registered_mcps",
        "params": {}
    }
    
    result = mcp_registry_integration_manager.process(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

