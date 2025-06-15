#!/usr/bin/env python3
"""
錯誤檢測和分析系統
用於分析GAIA測試中的partial和failed結果，並提供詳細的錯誤分類和修復建議
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import os
import sys
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """錯誤類型枚舉"""
    API_FAILURE = "api_failure"
    ANSWER_FORMAT = "answer_format"
    KNOWLEDGE_GAP = "knowledge_gap"
    REASONING_ERROR = "reasoning_error"
    FILE_PROCESSING = "file_processing"
    SEARCH_FAILURE = "search_failure"
    CALCULATION_ERROR = "calculation_error"
    CONTEXT_MISSING = "context_missing"
    TOOL_LIMITATION = "tool_limitation"
    UNKNOWN = "unknown"

class ErrorSeverity(Enum):
    """錯誤嚴重程度"""
    CRITICAL = "critical"  # 完全失敗
    HIGH = "high"         # 部分正確但有重大問題
    MEDIUM = "medium"     # 部分正確，需要改進
    LOW = "low"          # 基本正確，小問題

@dataclass
class ErrorAnalysisResult:
    """錯誤分析結果"""
    error_type: ErrorType
    severity: ErrorSeverity
    confidence: float
    description: str
    root_cause: str
    suggested_tools: List[str]
    repair_strategy: str
    estimated_fix_time: int  # 預估修復時間（分鐘）

class GAIAErrorDetectionAnalyzer:
    """GAIA錯誤檢測和分析器"""
    
    def __init__(self):
        """初始化錯誤檢測分析器"""
        self.error_patterns = self._initialize_error_patterns()
        self.tool_recommendations = self._initialize_tool_recommendations()
        self.analysis_history = []
        
        logger.info("GAIA錯誤檢測分析器初始化完成")
    
    def _initialize_error_patterns(self) -> Dict[ErrorType, List[str]]:
        """初始化錯誤模式"""
        return {
            ErrorType.API_FAILURE: [
                "api.*error", "rate.*limit", "timeout", "connection.*error",
                "authentication.*failed", "quota.*exceeded", "service.*unavailable",
                "錯誤", "失敗", "超時", "連接失敗"
            ],
            ErrorType.ANSWER_FORMAT: [
                "format.*incorrect", "invalid.*format", "unexpected.*format",
                "格式錯誤", "格式不正確", "答案格式", "輸出格式"
            ],
            ErrorType.KNOWLEDGE_GAP: [
                "don't.*know", "cannot.*find", "no.*information", "insufficient.*data",
                "不知道", "找不到", "沒有信息", "信息不足", "無法確定"
            ],
            ErrorType.REASONING_ERROR: [
                "logical.*error", "reasoning.*failed", "incorrect.*logic",
                "推理錯誤", "邏輯錯誤", "推論失敗", "分析錯誤"
            ],
            ErrorType.FILE_PROCESSING: [
                "file.*error", "cannot.*read", "parsing.*failed", "attachment.*error",
                "文件錯誤", "無法讀取", "解析失敗", "附件錯誤"
            ],
            ErrorType.SEARCH_FAILURE: [
                "search.*failed", "no.*results", "query.*error", "web.*search.*error",
                "搜索失敗", "沒有結果", "查詢錯誤", "網絡搜索錯誤"
            ],
            ErrorType.CALCULATION_ERROR: [
                "math.*error", "calculation.*wrong", "arithmetic.*error", "compute.*failed",
                "計算錯誤", "數學錯誤", "運算失敗", "計算失敗"
            ],
            ErrorType.CONTEXT_MISSING: [
                "context.*missing", "insufficient.*context", "need.*more.*information",
                "上下文缺失", "上下文不足", "需要更多信息", "背景信息不足"
            ],
            ErrorType.TOOL_LIMITATION: [
                "tool.*limitation", "capability.*exceeded", "not.*supported",
                "工具限制", "能力超出", "不支持", "功能限制"
            ]
        }
    
    def _initialize_tool_recommendations(self) -> Dict[ErrorType, List[str]]:
        """初始化工具推薦"""
        return {
            ErrorType.API_FAILURE: [
                "api_retry_tool", "fallback_api_tool", "rate_limit_handler"
            ],
            ErrorType.ANSWER_FORMAT: [
                "answer_formatter_tool", "output_parser_tool", "format_validator_tool"
            ],
            ErrorType.KNOWLEDGE_GAP: [
                "knowledge_search_tool", "web_scraper_tool", "database_query_tool"
            ],
            ErrorType.REASONING_ERROR: [
                "logic_checker_tool", "reasoning_validator_tool", "step_by_step_analyzer"
            ],
            ErrorType.FILE_PROCESSING: [
                "file_parser_tool", "document_analyzer_tool", "attachment_processor_tool"
            ],
            ErrorType.SEARCH_FAILURE: [
                "enhanced_search_tool", "multi_source_search_tool", "search_optimizer_tool"
            ],
            ErrorType.CALCULATION_ERROR: [
                "math_solver_tool", "calculation_validator_tool", "numerical_analyzer_tool"
            ],
            ErrorType.CONTEXT_MISSING: [
                "context_enricher_tool", "background_researcher_tool", "information_gatherer_tool"
            ],
            ErrorType.TOOL_LIMITATION: [
                "capability_extender_tool", "alternative_tool_finder", "hybrid_approach_tool"
            ]
        }
    
    def analyze_gaia_test_result(self, test_result: Dict[str, Any]) -> ErrorAnalysisResult:
        """分析GAIA測試結果"""
        try:
            # 提取關鍵信息
            status = test_result.get('status', 'unknown')
            confidence = test_result.get('confidence', 0.0)
            actual_answer = test_result.get('actual_answer', '')
            expected_answer = test_result.get('expected_answer', '')
            question = test_result.get('question', '')
            reason = test_result.get('reason', '')
            
            # 如果是成功狀態，不需要分析
            if status == 'passed' or status == 'success':
                return ErrorAnalysisResult(
                    error_type=ErrorType.UNKNOWN,
                    severity=ErrorSeverity.LOW,
                    confidence=1.0,
                    description="測試通過，無需修復",
                    root_cause="無錯誤",
                    suggested_tools=[],
                    repair_strategy="無需修復",
                    estimated_fix_time=0
                )
            
            # 分析錯誤類型
            error_type = self._classify_error_type(actual_answer, reason, question)
            
            # 確定嚴重程度
            severity = self._determine_severity(status, confidence, error_type)
            
            # 分析根本原因
            root_cause = self._analyze_root_cause(error_type, actual_answer, expected_answer, question)
            
            # 生成修復策略
            repair_strategy = self._generate_repair_strategy(error_type, severity, root_cause)
            
            # 推薦工具
            suggested_tools = self.tool_recommendations.get(error_type, [])
            
            # 預估修復時間
            estimated_fix_time = self._estimate_fix_time(error_type, severity)
            
            # 計算分析置信度
            analysis_confidence = self._calculate_analysis_confidence(error_type, actual_answer, reason)
            
            result = ErrorAnalysisResult(
                error_type=error_type,
                severity=severity,
                confidence=analysis_confidence,
                description=f"{error_type.value}錯誤：{reason}",
                root_cause=root_cause,
                suggested_tools=suggested_tools,
                repair_strategy=repair_strategy,
                estimated_fix_time=estimated_fix_time
            )
            
            # 記錄分析歷史
            self.analysis_history.append({
                'timestamp': time.time(),
                'test_id': test_result.get('test_id', 'unknown'),
                'analysis_result': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"錯誤分析失敗: {e}")
            return ErrorAnalysisResult(
                error_type=ErrorType.UNKNOWN,
                severity=ErrorSeverity.CRITICAL,
                confidence=0.0,
                description=f"分析失敗: {str(e)}",
                root_cause="分析器錯誤",
                suggested_tools=["error_analyzer_tool"],
                repair_strategy="重新分析",
                estimated_fix_time=5
            )
    
    def _classify_error_type(self, actual_answer: str, reason: str, question: str) -> ErrorType:
        """分類錯誤類型"""
        text_to_analyze = f"{actual_answer} {reason} {question}".lower()
        
        # 計算每種錯誤類型的匹配分數
        type_scores = {}
        for error_type, patterns in self.error_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_to_analyze):
                    score += 1
            type_scores[error_type] = score
        
        # 返回得分最高的錯誤類型
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        return ErrorType.UNKNOWN
    
    def _determine_severity(self, status: str, confidence: float, error_type: ErrorType) -> ErrorSeverity:
        """確定錯誤嚴重程度"""
        if status == 'failed' or confidence == 0.0:
            return ErrorSeverity.CRITICAL
        elif status == 'partial' and confidence < 0.3:
            return ErrorSeverity.HIGH
        elif status == 'partial' and confidence < 0.6:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _analyze_root_cause(self, error_type: ErrorType, actual: str, expected: str, question: str) -> str:
        """分析根本原因"""
        root_causes = {
            ErrorType.API_FAILURE: "API服務不穩定或配置錯誤",
            ErrorType.ANSWER_FORMAT: "答案格式不符合預期要求",
            ErrorType.KNOWLEDGE_GAP: "缺少必要的知識或信息源",
            ErrorType.REASONING_ERROR: "推理邏輯存在缺陷",
            ErrorType.FILE_PROCESSING: "文件處理能力不足",
            ErrorType.SEARCH_FAILURE: "搜索策略或工具不當",
            ErrorType.CALCULATION_ERROR: "數學計算邏輯錯誤",
            ErrorType.CONTEXT_MISSING: "上下文信息不完整",
            ErrorType.TOOL_LIMITATION: "現有工具能力不足",
            ErrorType.UNKNOWN: "需要進一步分析確定原因"
        }
        
        base_cause = root_causes.get(error_type, "未知原因")
        
        # 添加具體分析
        if len(actual) < 10:
            base_cause += "，回答過於簡短"
        elif "無法" in actual or "不能" in actual:
            base_cause += "，系統能力限制"
        elif len(question) > 500:
            base_cause += "，問題複雜度過高"
        
        return base_cause
    
    def _generate_repair_strategy(self, error_type: ErrorType, severity: ErrorSeverity, root_cause: str) -> str:
        """生成修復策略"""
        strategies = {
            ErrorType.API_FAILURE: "實施API重試機制和備用API切換",
            ErrorType.ANSWER_FORMAT: "創建答案格式化和驗證工具",
            ErrorType.KNOWLEDGE_GAP: "擴展知識源和搜索能力",
            ErrorType.REASONING_ERROR: "改進推理邏輯和驗證機制",
            ErrorType.FILE_PROCESSING: "增強文件解析和處理能力",
            ErrorType.SEARCH_FAILURE: "優化搜索策略和多源整合",
            ErrorType.CALCULATION_ERROR: "加強數學計算和驗證功能",
            ErrorType.CONTEXT_MISSING: "建立上下文收集和整合機制",
            ErrorType.TOOL_LIMITATION: "開發專用工具或混合解決方案",
            ErrorType.UNKNOWN: "進行深度分析並創建針對性工具"
        }
        
        base_strategy = strategies.get(error_type, "創建通用修復工具")
        
        # 根據嚴重程度調整策略
        if severity == ErrorSeverity.CRITICAL:
            base_strategy = f"緊急{base_strategy}，並實施兜底機制"
        elif severity == ErrorSeverity.HIGH:
            base_strategy = f"優先{base_strategy}，加強測試驗證"
        
        return base_strategy
    
    def _estimate_fix_time(self, error_type: ErrorType, severity: ErrorSeverity) -> int:
        """預估修復時間（分鐘）"""
        base_times = {
            ErrorType.API_FAILURE: 15,
            ErrorType.ANSWER_FORMAT: 10,
            ErrorType.KNOWLEDGE_GAP: 30,
            ErrorType.REASONING_ERROR: 25,
            ErrorType.FILE_PROCESSING: 20,
            ErrorType.SEARCH_FAILURE: 20,
            ErrorType.CALCULATION_ERROR: 15,
            ErrorType.CONTEXT_MISSING: 25,
            ErrorType.TOOL_LIMITATION: 45,
            ErrorType.UNKNOWN: 30
        }
        
        base_time = base_times.get(error_type, 30)
        
        # 根據嚴重程度調整時間
        severity_multipliers = {
            ErrorSeverity.CRITICAL: 2.0,
            ErrorSeverity.HIGH: 1.5,
            ErrorSeverity.MEDIUM: 1.2,
            ErrorSeverity.LOW: 1.0
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        return int(base_time * multiplier)
    
    def _calculate_analysis_confidence(self, error_type: ErrorType, actual_answer: str, reason: str) -> float:
        """計算分析置信度"""
        confidence = 0.5  # 基礎置信度
        
        # 如果錯誤類型不是UNKNOWN，增加置信度
        if error_type != ErrorType.UNKNOWN:
            confidence += 0.3
        
        # 如果有明確的錯誤信息，增加置信度
        if reason and len(reason) > 10:
            confidence += 0.1
        
        # 如果有具體的錯誤模式匹配，增加置信度
        patterns = self.error_patterns.get(error_type, [])
        text_to_check = f"{actual_answer} {reason}".lower()
        matches = sum(1 for pattern in patterns if re.search(pattern, text_to_check))
        if matches > 0:
            confidence += min(0.1 * matches, 0.2)
        
        return min(confidence, 1.0)
    
    def batch_analyze_results(self, test_results: List[Dict[str, Any]]) -> List[ErrorAnalysisResult]:
        """批量分析測試結果"""
        analyses = []
        for result in test_results:
            analysis = self.analyze_gaia_test_result(result)
            analyses.append(analysis)
        
        return analyses
    
    def generate_analysis_report(self, analyses: List[ErrorAnalysisResult]) -> Dict[str, Any]:
        """生成分析報告"""
        if not analyses:
            return {"error": "沒有分析結果"}
        
        # 統計錯誤類型分布
        error_type_counts = {}
        severity_counts = {}
        total_fix_time = 0
        
        for analysis in analyses:
            error_type = analysis.error_type.value
            severity = analysis.severity.value
            
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            total_fix_time += analysis.estimated_fix_time
        
        # 找出最常見的錯誤類型
        most_common_error = max(error_type_counts, key=error_type_counts.get) if error_type_counts else "unknown"
        
        # 計算平均置信度
        avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
        
        return {
            "total_errors": len(analyses),
            "error_type_distribution": error_type_counts,
            "severity_distribution": severity_counts,
            "most_common_error": most_common_error,
            "average_confidence": avg_confidence,
            "total_estimated_fix_time": total_fix_time,
            "average_fix_time": total_fix_time / len(analyses),
            "critical_errors": sum(1 for a in analyses if a.severity == ErrorSeverity.CRITICAL),
            "high_priority_errors": sum(1 for a in analyses if a.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]),
            "timestamp": time.time()
        }
    
    def get_prioritized_repair_list(self, analyses: List[ErrorAnalysisResult]) -> List[Dict[str, Any]]:
        """獲取優先修復列表"""
        # 按嚴重程度和置信度排序
        def priority_score(analysis):
            severity_weights = {
                ErrorSeverity.CRITICAL: 4,
                ErrorSeverity.HIGH: 3,
                ErrorSeverity.MEDIUM: 2,
                ErrorSeverity.LOW: 1
            }
            return severity_weights.get(analysis.severity, 0) * analysis.confidence
        
        sorted_analyses = sorted(analyses, key=priority_score, reverse=True)
        
        repair_list = []
        for i, analysis in enumerate(sorted_analyses):
            repair_list.append({
                "priority": i + 1,
                "error_type": analysis.error_type.value,
                "severity": analysis.severity.value,
                "confidence": analysis.confidence,
                "description": analysis.description,
                "root_cause": analysis.root_cause,
                "repair_strategy": analysis.repair_strategy,
                "suggested_tools": analysis.suggested_tools,
                "estimated_fix_time": analysis.estimated_fix_time
            })
        
        return repair_list

def main():
    """測試函數"""
    analyzer = GAIAErrorDetectionAnalyzer()
    
    # 測試用例
    test_result = {
        "test_id": "test_001",
        "status": "partial",
        "confidence": 0.3,
        "actual_answer": "無法確定具體答案",
        "expected_answer": "42",
        "question": "計算複雜數學問題的結果",
        "reason": "需要人工評估"
    }
    
    analysis = analyzer.analyze_gaia_test_result(test_result)
    print(f"錯誤類型: {analysis.error_type.value}")
    print(f"嚴重程度: {analysis.severity.value}")
    print(f"修復策略: {analysis.repair_strategy}")
    print(f"建議工具: {analysis.suggested_tools}")

if __name__ == "__main__":
    main()

