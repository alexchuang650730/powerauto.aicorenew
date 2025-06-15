#!/usr/bin/env python3
"""
PowerAutomation 統一意圖處理引擎 - 個人專業版

實現正確的分層架構：
1. 意圖識別 → 識別三大工作流意圖
2. 工作流路由 → 路由到對應的專業工作流引擎
3. 工具調用 → 工作流中需要工具時驅動MCP
4. 智慧路由 → MCP層面進行端雲選擇
5. 工作流兜底 → Kilo Code引擎（工作流內兜底）
6. 全局兜底 → 搜索引擎（所有工作流外的兜底）
"""

import os
import re
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowIntention(Enum):
    """個人專業版工作流意圖枚舉"""
    CODING_IMPLEMENTATION = "coding_implementation"
    TESTING_VERIFICATION = "testing_verification"
    DEPLOYMENT_RELEASE = "deployment_release"
    UNKNOWN = "unknown"

class ProcessingResult(Enum):
    """處理結果狀態"""
    SUCCESS = "success"
    FALLBACK_TO_KILO = "fallback_to_kilo"
    FALLBACK_TO_SEARCH = "fallback_to_search"
    FAILED = "failed"

@dataclass
class IntentionAnalysisResult:
    """意圖分析結果"""
    intention: WorkflowIntention
    confidence: float
    keywords_matched: List[str]
    patterns_matched: List[str]
    reasoning: str

@dataclass
class WorkflowExecutionResult:
    """工作流執行結果"""
    intention: WorkflowIntention
    engine_used: str
    result_status: ProcessingResult
    output: Any
    execution_time: float
    tokens_used: int
    cost_saved: float
    reasoning: str

class IntentionClassifier:
    """意圖分類器"""
    
    def __init__(self):
        # 個人專業版三大工作流意圖配置
        self.workflow_intentions = {
            WorkflowIntention.CODING_IMPLEMENTATION: {
                "keywords": ["編碼", "實現", "開發", "代碼", "編程", "寫代碼", "程式", "function", "class", "method", "api"],
                "patterns": [
                    r"code.*",
                    r"implement.*",
                    r"develop.*",
                    r"寫.*代碼",
                    r"實現.*功能",
                    r"開發.*",
                    r"編程.*",
                    r"創建.*函數",
                    r"建立.*類別"
                ],
                "target_engine": "kilo_code_engine",
                "description": "AI編程助手，代碼自動生成，智能代碼補全和模板生成"
            },
            WorkflowIntention.TESTING_VERIFICATION: {
                "keywords": ["測試", "驗證", "檢測", "質量", "斷言", "test", "verify", "validate", "check", "assert"],
                "patterns": [
                    r"test.*",
                    r"verify.*",
                    r"validate.*",
                    r"測試.*",
                    r"驗證.*",
                    r"檢查.*",
                    r"質量.*",
                    r"單元測試",
                    r"集成測試"
                ],
                "target_engine": "template_test_generator",
                "description": "自動化測試，質量保障，智能介入協調和質量門檻檢查"
            },
            WorkflowIntention.DEPLOYMENT_RELEASE: {
                "keywords": ["部署", "發布", "上線", "環境", "配置", "deploy", "release", "publish", "launch", "build"],
                "patterns": [
                    r"deploy.*",
                    r"release.*",
                    r"publish.*",
                    r"部署.*",
                    r"發布.*",
                    r"上線.*",
                    r"打包.*",
                    r"構建.*",
                    r"環境.*配置"
                ],
                "target_engine": "release_manager",
                "description": "一鍵部署，環境管理，版本控制和發布流程自動化"
            }
        }
    
    def analyze_intention(self, user_input: str) -> IntentionAnalysisResult:
        """分析用戶輸入的意圖"""
        user_input_lower = user_input.lower()
        
        best_match = None
        best_score = 0.0
        best_keywords = []
        best_patterns = []
        
        for intention, config in self.workflow_intentions.items():
            score = 0.0
            matched_keywords = []
            matched_patterns = []
            
            # 關鍵詞匹配
            for keyword in config["keywords"]:
                if keyword.lower() in user_input_lower:
                    score += 1.0
                    matched_keywords.append(keyword)
            
            # 模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, user_input, re.IGNORECASE):
                    score += 1.5  # 模式匹配權重更高
                    matched_patterns.append(pattern)
            
            # 計算信心度
            total_possible = len(config["keywords"]) + len(config["patterns"]) * 1.5
            confidence = score / total_possible if total_possible > 0 else 0.0
            
            if confidence > best_score:
                best_score = confidence
                best_match = intention
                best_keywords = matched_keywords
                best_patterns = matched_patterns
        
        # 如果信心度太低，標記為未知
        if best_score < 0.1:
            best_match = WorkflowIntention.UNKNOWN
        
        reasoning = f"匹配到 {len(best_keywords)} 個關鍵詞和 {len(best_patterns)} 個模式"
        
        return IntentionAnalysisResult(
            intention=best_match,
            confidence=best_score,
            keywords_matched=best_keywords,
            patterns_matched=best_patterns,
            reasoning=reasoning
        )

class KiloCodeEngine:
    """Kilo Code智能引擎 - 工作流內兜底"""
    
    def __init__(self):
        self.name = "Kilo Code Engine"
        self.capabilities = ["code_generation", "code_completion", "template_generation"]
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理編碼實現請求"""
        logger.info(f"🤖 Kilo Code引擎處理: {user_input[:50]}...")
        
        # 模擬智能代碼生成
        await asyncio.sleep(0.5)  # 模擬處理時間
        
        result = {
            "engine": self.name,
            "output": f"# 智能生成的代碼\ndef generated_function():\n    # 基於需求: {user_input}\n    pass",
            "confidence": 0.85,
            "tokens_used": 150,
            "processing_time": 0.5
        }
        
        return result

class TemplateTestGenerator:
    """模板測試生成引擎"""
    
    def __init__(self):
        self.name = "Template Test Generator"
        self.capabilities = ["test_generation", "quality_assurance", "test_automation"]
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理測試驗證請求"""
        logger.info(f"🧪 模板測試生成引擎處理: {user_input[:50]}...")
        
        # 模擬測試生成
        await asyncio.sleep(0.3)
        
        result = {
            "engine": self.name,
            "output": f"# 自動生成的測試用例\ndef test_{user_input.replace(' ', '_').lower()}():\n    # 測試: {user_input}\n    assert True",
            "confidence": 0.90,
            "tokens_used": 120,
            "processing_time": 0.3
        }
        
        return result

class ReleaseManager:
    """發布管理器"""
    
    def __init__(self):
        self.name = "Release Manager"
        self.capabilities = ["deployment", "release_automation", "environment_management"]
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理部署發布請求"""
        logger.info(f"🚀 發布管理器處理: {user_input[:50]}...")
        
        # 模擬部署處理
        await asyncio.sleep(0.4)
        
        result = {
            "engine": self.name,
            "output": f"# 部署配置\ndeployment:\n  target: {user_input}\n  status: ready\n  environment: production",
            "confidence": 0.88,
            "tokens_used": 100,
            "processing_time": 0.4
        }
        
        return result

class SearchEngine:
    """搜索引擎 - 全局兜底"""
    
    def __init__(self):
        self.name = "Search Engine"
        self.capabilities = ["web_search", "information_retrieval"]
    
    async def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理搜索請求"""
        logger.info(f"🔍 搜索引擎兜底處理: {user_input[:50]}...")
        
        # 模擬搜索
        await asyncio.sleep(0.2)
        
        result = {
            "engine": self.name,
            "output": f"搜索結果: 找到關於 '{user_input}' 的相關信息...",
            "confidence": 0.70,
            "tokens_used": 80,
            "processing_time": 0.2
        }
        
        return result

class UnifiedIntentionEngine:
    """統一意圖處理引擎"""
    
    def __init__(self):
        self.intention_classifier = IntentionClassifier()
        
        # 初始化工作流引擎
        self.engines = {
            "kilo_code_engine": KiloCodeEngine(),
            "template_test_generator": TemplateTestGenerator(),
            "release_manager": ReleaseManager(),
            "search_engine": SearchEngine()  # 全局兜底
        }
        
        # 工作流路由配置
        self.workflow_routing = {
            WorkflowIntention.CODING_IMPLEMENTATION: "kilo_code_engine",
            WorkflowIntention.TESTING_VERIFICATION: "template_test_generator",
            WorkflowIntention.DEPLOYMENT_RELEASE: "release_manager"
        }
        
        # 統計數據
        self.stats = {
            "total_requests": 0,
            "workflow_hits": 0,
            "kilo_fallbacks": 0,
            "search_fallbacks": 0,
            "total_tokens_saved": 0,
            "total_cost_saved": 0.0
        }
    
    async def process_request(self, user_input: str, context: Dict[str, Any] = None) -> WorkflowExecutionResult:
        """處理用戶請求的主入口"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        logger.info(f"📥 收到請求: {user_input}")
        
        # 1. 意圖識別
        intention_result = self.intention_classifier.analyze_intention(user_input)
        logger.info(f"🎯 意圖識別: {intention_result.intention.value} (信心度: {intention_result.confidence:.2f})")
        
        # 2. 工作流路由
        if intention_result.intention in self.workflow_routing:
            # 路由到對應的工作流引擎
            target_engine_name = self.workflow_routing[intention_result.intention]
            target_engine = self.engines[target_engine_name]
            
            try:
                # 3. 執行工作流
                engine_result = await target_engine.process(user_input, context)
                self.stats["workflow_hits"] += 1
                
                execution_time = time.time() - start_time
                
                # 計算Token節省（假設雲端處理會用更多Token）
                tokens_saved = engine_result["tokens_used"] * 0.3  # 本地處理節省30%
                cost_saved = tokens_saved * 0.00002  # 假設每token $0.00002
                
                self.stats["total_tokens_saved"] += tokens_saved
                self.stats["total_cost_saved"] += cost_saved
                
                return WorkflowExecutionResult(
                    intention=intention_result.intention,
                    engine_used=target_engine.name,
                    result_status=ProcessingResult.SUCCESS,
                    output=engine_result["output"],
                    execution_time=execution_time,
                    tokens_used=engine_result["tokens_used"],
                    cost_saved=cost_saved,
                    reasoning=f"成功路由到{target_engine.name}處理"
                )
                
            except Exception as e:
                logger.warning(f"⚠️ 工作流引擎失敗，回退到Kilo Code: {e}")
                # 4. 工作流內兜底 - Kilo Code
                return await self._fallback_to_kilo(user_input, start_time)
        
        else:
            # 5. 全局兜底 - 搜索引擎
            logger.info("🔍 未識別工作流意圖，使用搜索引擎兜底")
            return await self._fallback_to_search(user_input, start_time)
    
    async def _fallback_to_kilo(self, user_input: str, start_time: float) -> WorkflowExecutionResult:
        """回退到Kilo Code引擎"""
        self.stats["kilo_fallbacks"] += 1
        
        kilo_engine = self.engines["kilo_code_engine"]
        engine_result = await kilo_engine.process(user_input)
        
        execution_time = time.time() - start_time
        
        return WorkflowExecutionResult(
            intention=WorkflowIntention.UNKNOWN,
            engine_used=kilo_engine.name,
            result_status=ProcessingResult.FALLBACK_TO_KILO,
            output=engine_result["output"],
            execution_time=execution_time,
            tokens_used=engine_result["tokens_used"],
            cost_saved=0.0,
            reasoning="工作流引擎失敗，Kilo Code兜底處理"
        )
    
    async def _fallback_to_search(self, user_input: str, start_time: float) -> WorkflowExecutionResult:
        """回退到搜索引擎"""
        self.stats["search_fallbacks"] += 1
        
        search_engine = self.engines["search_engine"]
        engine_result = await search_engine.process(user_input)
        
        execution_time = time.time() - start_time
        
        return WorkflowExecutionResult(
            intention=WorkflowIntention.UNKNOWN,
            engine_used=search_engine.name,
            result_status=ProcessingResult.FALLBACK_TO_SEARCH,
            output=engine_result["output"],
            execution_time=execution_time,
            tokens_used=engine_result["tokens_used"],
            cost_saved=0.0,
            reasoning="未識別工作流意圖，搜索引擎兜底處理"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計數據"""
        return {
            **self.stats,
            "workflow_hit_rate": self.stats["workflow_hits"] / max(self.stats["total_requests"], 1) * 100,
            "kilo_fallback_rate": self.stats["kilo_fallbacks"] / max(self.stats["total_requests"], 1) * 100,
            "search_fallback_rate": self.stats["search_fallbacks"] / max(self.stats["total_requests"], 1) * 100
        }

# 測試函數
async def test_unified_intention_engine():
    """測試統一意圖處理引擎"""
    print("🧪 測試PowerAutomation統一意圖處理引擎")
    print("=" * 60)
    
    engine = UnifiedIntentionEngine()
    
    # 測試用例
    test_cases = [
        "幫我寫一個Python函數來計算斐波那契數列",  # 編碼實現
        "為這個函數生成單元測試用例",  # 測試驗證
        "部署這個應用到生產環境",  # 部署發布
        "今天天氣如何？",  # 未知意圖，應該搜索兜底
        "實現一個REST API接口",  # 編碼實現
        "驗證API的響應格式是否正確",  # 測試驗證
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 測試 {i}: {test_input}")
        print("-" * 40)
        
        result = await engine.process_request(test_input)
        
        print(f"🎯 意圖: {result.intention.value}")
        print(f"🤖 引擎: {result.engine_used}")
        print(f"📊 狀態: {result.result_status.value}")
        print(f"⏱️ 執行時間: {result.execution_time:.3f}s")
        print(f"🎫 Token使用: {result.tokens_used}")
        print(f"💰 成本節省: ${result.cost_saved:.4f}")
        print(f"💭 推理: {result.reasoning}")
        print(f"📤 輸出: {result.output[:100]}...")
    
    # 顯示統計數據
    print("\n📊 統計數據")
    print("=" * 60)
    stats = engine.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_unified_intention_engine())

