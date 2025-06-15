#!/usr/bin/env python3
"""
CLI驅動修復系統
整合workflow_engine_cli，實現自動化修復工具的CLI驅動執行
"""

import json
import logging
import time
import subprocess
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import uuid

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

from mcptool.core.error_detection_analyzer import ErrorAnalysisResult, ErrorType, ErrorSeverity
from mcptool.core.automatic_tool_creation_engine import CreatedTool, AutomaticToolCreationEngine

logger = logging.getLogger(__name__)

@dataclass
class CLIRepairRequest:
    """CLI修復請求"""
    request_id: str
    error_analysis: ErrorAnalysisResult
    created_tool: CreatedTool
    input_data: Dict[str, Any]
    repair_options: Dict[str, Any]
    priority: int
    timeout: int

@dataclass
class CLIRepairResult:
    """CLI修復結果"""
    request_id: str
    success: bool
    repaired_data: Any
    confidence: float
    execution_time: float
    tool_used: str
    cli_command: str
    output_log: str
    error_log: str
    repair_report: Dict[str, Any]

class CLIDrivenRepairSystem:
    """CLI驅動修復系統"""
    
    def __init__(self):
        """初始化CLI驅動修復系統"""
        self.workflow_cli_path = "/home/ubuntu/projects/communitypowerautomation/mcptool/cli_testing/workflow_engine_cli.py"
        self.repair_history = []
        self.active_repairs = {}
        
        # CLI命令模板
        self.cli_templates = self._initialize_cli_templates()
        
        # 修復策略配置
        self.repair_strategies = self._initialize_repair_strategies()
        
        logger.info("CLI驅動修復系統初始化完成")
    
    def _initialize_cli_templates(self) -> Dict[ErrorType, str]:
        """初始化CLI命令模板"""
        return {
            ErrorType.API_FAILURE: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'api_retry'",
            ErrorType.ANSWER_FORMAT: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'format_repair'",
            ErrorType.KNOWLEDGE_GAP: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'knowledge_search'",
            ErrorType.REASONING_ERROR: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'logic_validation'",
            ErrorType.FILE_PROCESSING: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'file_repair'",
            ErrorType.SEARCH_FAILURE: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'enhanced_search'",
            ErrorType.CALCULATION_ERROR: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'math_validation'",
            ErrorType.CONTEXT_MISSING: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'context_enrichment'",
            ErrorType.TOOL_LIMITATION: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'capability_extension'",
            ErrorType.UNKNOWN: "python3 {cli_path} solve '{problem_description}' --context '{context}' --strategy 'general_repair'"
        }
    
    def _initialize_repair_strategies(self) -> Dict[str, Dict[str, Any]]:
        """初始化修復策略"""
        return {
            "api_retry": {
                "max_retries": 3,
                "backoff_factor": 2,
                "timeout": 30,
                "fallback_apis": ["backup_api_1", "backup_api_2"]
            },
            "format_repair": {
                "validation_rules": ["json_format", "text_cleanup", "encoding_fix"],
                "output_formats": ["json", "text", "xml"],
                "cleanup_patterns": ["remove_extra_spaces", "fix_encoding", "normalize_quotes"]
            },
            "knowledge_search": {
                "search_engines": ["google", "bing", "duckduckgo"],
                "knowledge_bases": ["wikipedia", "wikidata", "dbpedia"],
                "fact_checkers": ["snopes", "factcheck", "politifact"]
            },
            "logic_validation": {
                "reasoning_engines": ["symbolic_logic", "natural_logic", "probabilistic_reasoning"],
                "validation_methods": ["consistency_check", "contradiction_detection", "inference_validation"]
            },
            "file_repair": {
                "supported_formats": ["pdf", "docx", "xlsx", "csv", "json", "xml"],
                "repair_methods": ["encoding_fix", "structure_repair", "content_extraction"]
            },
            "enhanced_search": {
                "search_strategies": ["multi_query", "semantic_search", "contextual_search"],
                "result_aggregation": ["relevance_ranking", "duplicate_removal", "source_validation"]
            },
            "math_validation": {
                "calculation_engines": ["sympy", "wolfram", "mathematical_solver"],
                "validation_methods": ["step_verification", "result_checking", "alternative_calculation"]
            },
            "context_enrichment": {
                "context_sources": ["background_knowledge", "related_information", "domain_expertise"],
                "enrichment_methods": ["semantic_expansion", "knowledge_graph", "expert_systems"]
            },
            "capability_extension": {
                "extension_methods": ["tool_combination", "api_integration", "service_orchestration"],
                "fallback_capabilities": ["manual_processing", "human_intervention", "alternative_approaches"]
            },
            "general_repair": {
                "repair_approaches": ["heuristic_repair", "pattern_matching", "machine_learning"],
                "fallback_methods": ["rule_based", "statistical", "hybrid_approach"]
            }
        }
    
    def execute_cli_repair(self, repair_request: CLIRepairRequest) -> CLIRepairResult:
        """執行CLI驅動修復"""
        start_time = time.time()
        request_id = repair_request.request_id
        
        try:
            logger.info(f"開始CLI修復: {request_id}")
            
            # 準備CLI命令
            cli_command = self._prepare_cli_command(repair_request)
            
            # 執行CLI命令
            execution_result = self._execute_cli_command(cli_command, repair_request.timeout)
            
            # 解析執行結果
            repair_result = self._parse_cli_result(execution_result, repair_request)
            
            # 驗證修復結果
            validation_result = self._validate_repair_result(repair_result, repair_request)
            
            # 更新修復結果
            repair_result.confidence = validation_result["confidence"]
            repair_result.success = validation_result["success"]
            
            # 記錄修復歷史
            self._record_repair_history(repair_request, repair_result)
            
            execution_time = time.time() - start_time
            repair_result.execution_time = execution_time
            
            logger.info(f"CLI修復完成: {request_id}, 成功: {repair_result.success}, 置信度: {repair_result.confidence}")
            
            return repair_result
            
        except Exception as e:
            logger.error(f"CLI修復失敗: {request_id}, 錯誤: {e}")
            return self._create_error_result(repair_request, str(e), time.time() - start_time)
    
    def _prepare_cli_command(self, repair_request: CLIRepairRequest) -> str:
        """準備CLI命令"""
        error_type = repair_request.error_analysis.error_type
        template = self.cli_templates.get(error_type, self.cli_templates[ErrorType.UNKNOWN])
        
        # 準備問題描述
        problem_description = self._generate_problem_description(repair_request)
        
        # 準備上下文信息
        context = self._generate_context_info(repair_request)
        
        # 格式化CLI命令
        cli_command = template.format(
            cli_path=self.workflow_cli_path,
            problem_description=problem_description.replace("'", "\\'"),
            context=json.dumps(context).replace("'", "\\'")
        )
        
        return cli_command
    
    def _generate_problem_description(self, repair_request: CLIRepairRequest) -> str:
        """生成問題描述"""
        error_analysis = repair_request.error_analysis
        input_data = repair_request.input_data
        
        description = f"""
錯誤類型: {error_analysis.error_type.value}
嚴重程度: {error_analysis.severity.value}
錯誤描述: {error_analysis.description}
根本原因: {error_analysis.root_cause}
修復策略: {error_analysis.repair_strategy}
輸入數據: {json.dumps(input_data, ensure_ascii=False)}
預期修復: {error_analysis.suggested_tools}
"""
        return description.strip()
    
    def _generate_context_info(self, repair_request: CLIRepairRequest) -> Dict[str, Any]:
        """生成上下文信息"""
        return {
            "request_id": repair_request.request_id,
            "error_type": repair_request.error_analysis.error_type.value,
            "severity": repair_request.error_analysis.severity.value,
            "confidence": repair_request.error_analysis.confidence,
            "tool_path": repair_request.created_tool.file_path,
            "tool_id": repair_request.created_tool.tool_id,
            "repair_options": repair_request.repair_options,
            "priority": repair_request.priority,
            "estimated_fix_time": repair_request.error_analysis.estimated_fix_time
        }
    
    def _execute_cli_command(self, cli_command: str, timeout: int) -> Dict[str, Any]:
        """執行CLI命令"""
        try:
            logger.info(f"執行CLI命令: {cli_command}")
            
            # 執行命令
            result = subprocess.run(
                cli_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="/home/ubuntu/projects/communitypowerautomation"
            )
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": cli_command
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"CLI命令超時: {cli_command}")
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"命令執行超時 ({timeout}秒)",
                "command": cli_command
            }
        except Exception as e:
            logger.error(f"CLI命令執行失敗: {e}")
            return {
                "returncode": -2,
                "stdout": "",
                "stderr": str(e),
                "command": cli_command
            }
    
    def _parse_cli_result(self, execution_result: Dict[str, Any], repair_request: CLIRepairRequest) -> CLIRepairResult:
        """解析CLI執行結果"""
        stdout = execution_result.get("stdout", "")
        stderr = execution_result.get("stderr", "")
        returncode = execution_result.get("returncode", -1)
        
        # 嘗試解析JSON輸出
        repaired_data = ""
        success = False
        confidence = 0.0
        
        if returncode == 0 and stdout:
            try:
                # 嘗試解析JSON格式的輸出
                if stdout.strip().startswith("{"):
                    result_json = json.loads(stdout.strip())
                    repaired_data = result_json.get("repaired_data", stdout)
                    success = result_json.get("success", True)
                    confidence = result_json.get("confidence", 0.8)
                else:
                    # 純文本輸出
                    repaired_data = stdout.strip()
                    success = True
                    confidence = 0.7
            except json.JSONDecodeError:
                # JSON解析失敗，使用原始輸出
                repaired_data = stdout.strip()
                success = True if returncode == 0 else False
                confidence = 0.6 if success else 0.0
        else:
            success = False
            confidence = 0.0
            repaired_data = ""
        
        # 生成修復報告
        repair_report = {
            "cli_execution": {
                "command": execution_result.get("command", ""),
                "returncode": returncode,
                "success": returncode == 0
            },
            "output_analysis": {
                "stdout_length": len(stdout),
                "stderr_length": len(stderr),
                "has_json_output": stdout.strip().startswith("{"),
                "has_error_output": len(stderr) > 0
            },
            "repair_assessment": {
                "data_extracted": len(str(repaired_data)) > 0,
                "success_indicated": success,
                "confidence_level": confidence
            }
        }
        
        return CLIRepairResult(
            request_id=repair_request.request_id,
            success=success,
            repaired_data=repaired_data,
            confidence=confidence,
            execution_time=0.0,  # 將在外部設置
            tool_used=repair_request.created_tool.tool_name,
            cli_command=execution_result.get("command", ""),
            output_log=stdout,
            error_log=stderr,
            repair_report=repair_report
        )
    
    def _validate_repair_result(self, repair_result: CLIRepairResult, repair_request: CLIRepairRequest) -> Dict[str, Any]:
        """驗證修復結果"""
        validation_score = 0.0
        validation_details = {}
        
        # 基本成功檢查
        if repair_result.success:
            validation_score += 0.4
            validation_details["basic_success"] = True
        
        # 數據質量檢查
        if repair_result.repaired_data and len(str(repair_result.repaired_data).strip()) > 0:
            validation_score += 0.3
            validation_details["data_quality"] = True
        
        # 錯誤日誌檢查
        if not repair_result.error_log or len(repair_result.error_log.strip()) == 0:
            validation_score += 0.2
            validation_details["no_errors"] = True
        
        # 置信度檢查
        if repair_result.confidence > 0.5:
            validation_score += 0.1
            validation_details["confidence_acceptable"] = True
        
        # 根據錯誤類型進行特定驗證
        error_type = repair_request.error_analysis.error_type
        type_validation = self._validate_by_error_type(repair_result, error_type)
        validation_score += type_validation["score"]
        validation_details.update(type_validation["details"])
        
        # 最終驗證結果
        final_success = validation_score >= 0.7
        final_confidence = min(validation_score, 1.0)
        
        return {
            "success": final_success,
            "confidence": final_confidence,
            "validation_score": validation_score,
            "validation_details": validation_details
        }
    
    def _validate_by_error_type(self, repair_result: CLIRepairResult, error_type: ErrorType) -> Dict[str, Any]:
        """根據錯誤類型進行特定驗證"""
        validation_methods = {
            ErrorType.API_FAILURE: self._validate_api_repair,
            ErrorType.ANSWER_FORMAT: self._validate_format_repair,
            ErrorType.KNOWLEDGE_GAP: self._validate_knowledge_repair,
            ErrorType.REASONING_ERROR: self._validate_reasoning_repair,
            ErrorType.FILE_PROCESSING: self._validate_file_repair,
            ErrorType.SEARCH_FAILURE: self._validate_search_repair,
            ErrorType.CALCULATION_ERROR: self._validate_calculation_repair,
            ErrorType.CONTEXT_MISSING: self._validate_context_repair,
            ErrorType.TOOL_LIMITATION: self._validate_capability_repair,
            ErrorType.UNKNOWN: self._validate_general_repair
        }
        
        validator = validation_methods.get(error_type, self._validate_general_repair)
        return validator(repair_result)
    
    def _validate_api_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證API修復結果"""
        score = 0.0
        details = {}
        
        # 檢查是否包含API響應
        if "api" in str(repair_result.repaired_data).lower():
            score += 0.1
            details["contains_api_response"] = True
        
        # 檢查是否有重試信息
        if "retry" in repair_result.output_log.lower():
            score += 0.05
            details["retry_attempted"] = True
        
        return {"score": score, "details": details}
    
    def _validate_format_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證格式修復結果"""
        score = 0.0
        details = {}
        
        # 檢查JSON格式
        try:
            json.loads(str(repair_result.repaired_data))
            score += 0.1
            details["valid_json"] = True
        except:
            pass
        
        # 檢查格式清理
        if len(str(repair_result.repaired_data).strip()) > 0:
            score += 0.05
            details["format_cleaned"] = True
        
        return {"score": score, "details": details}
    
    def _validate_knowledge_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證知識修復結果"""
        score = 0.0
        details = {}
        
        # 檢查是否包含知識信息
        if len(str(repair_result.repaired_data)) > 50:
            score += 0.1
            details["substantial_content"] = True
        
        return {"score": score, "details": details}
    
    def _validate_reasoning_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證推理修復結果"""
        score = 0.0
        details = {}
        
        # 檢查邏輯結構
        if "because" in str(repair_result.repaired_data).lower() or "therefore" in str(repair_result.repaired_data).lower():
            score += 0.1
            details["logical_structure"] = True
        
        return {"score": score, "details": details}
    
    def _validate_file_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證文件修復結果"""
        score = 0.0
        details = {}
        
        # 檢查文件處理信息
        if "file" in repair_result.output_log.lower():
            score += 0.1
            details["file_processed"] = True
        
        return {"score": score, "details": details}
    
    def _validate_search_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證搜索修復結果"""
        score = 0.0
        details = {}
        
        # 檢查搜索結果
        if "search" in repair_result.output_log.lower() or "found" in repair_result.output_log.lower():
            score += 0.1
            details["search_performed"] = True
        
        return {"score": score, "details": details}
    
    def _validate_calculation_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證計算修復結果"""
        score = 0.0
        details = {}
        
        # 檢查數值結果
        try:
            float(str(repair_result.repaired_data).strip())
            score += 0.1
            details["numeric_result"] = True
        except:
            pass
        
        return {"score": score, "details": details}
    
    def _validate_context_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證上下文修復結果"""
        score = 0.0
        details = {}
        
        # 檢查上下文豐富度
        if len(str(repair_result.repaired_data)) > 100:
            score += 0.1
            details["context_enriched"] = True
        
        return {"score": score, "details": details}
    
    def _validate_capability_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證能力修復結果"""
        score = 0.0
        details = {}
        
        # 檢查能力擴展
        if "capability" in repair_result.output_log.lower() or "extended" in repair_result.output_log.lower():
            score += 0.1
            details["capability_extended"] = True
        
        return {"score": score, "details": details}
    
    def _validate_general_repair(self, repair_result: CLIRepairResult) -> Dict[str, Any]:
        """驗證通用修復結果"""
        score = 0.0
        details = {}
        
        # 基本驗證
        if repair_result.repaired_data:
            score += 0.05
            details["general_repair_attempted"] = True
        
        return {"score": score, "details": details}
    
    def _record_repair_history(self, repair_request: CLIRepairRequest, repair_result: CLIRepairResult):
        """記錄修復歷史"""
        history_entry = {
            "timestamp": time.time(),
            "request_id": repair_request.request_id,
            "error_type": repair_request.error_analysis.error_type.value,
            "severity": repair_request.error_analysis.severity.value,
            "tool_used": repair_request.created_tool.tool_name,
            "success": repair_result.success,
            "confidence": repair_result.confidence,
            "execution_time": repair_result.execution_time,
            "cli_command": repair_result.cli_command
        }
        
        self.repair_history.append(history_entry)
        
        # 保持歷史記錄在合理範圍內
        if len(self.repair_history) > 1000:
            self.repair_history = self.repair_history[-500:]
    
    def _create_error_result(self, repair_request: CLIRepairRequest, error_message: str, execution_time: float) -> CLIRepairResult:
        """創建錯誤結果"""
        return CLIRepairResult(
            request_id=repair_request.request_id,
            success=False,
            repaired_data="",
            confidence=0.0,
            execution_time=execution_time,
            tool_used=repair_request.created_tool.tool_name,
            cli_command="",
            output_log="",
            error_log=error_message,
            repair_report={
                "error": error_message,
                "cli_execution": {"success": False},
                "output_analysis": {"has_error": True},
                "repair_assessment": {"failed": True}
            }
        )
    
    def batch_repair(self, repair_requests: List[CLIRepairRequest]) -> List[CLIRepairResult]:
        """批量修復"""
        results = []
        
        for request in repair_requests:
            result = self.execute_cli_repair(request)
            results.append(result)
        
        return results
    
    def get_repair_statistics(self) -> Dict[str, Any]:
        """獲取修復統計信息"""
        if not self.repair_history:
            return {"total_repairs": 0}
        
        total_repairs = len(self.repair_history)
        successful_repairs = sum(1 for entry in self.repair_history if entry["success"])
        
        # 按錯誤類型統計
        error_type_stats = {}
        for entry in self.repair_history:
            error_type = entry["error_type"]
            if error_type not in error_type_stats:
                error_type_stats[error_type] = {"total": 0, "success": 0}
            error_type_stats[error_type]["total"] += 1
            if entry["success"]:
                error_type_stats[error_type]["success"] += 1
        
        # 計算平均置信度和執行時間
        avg_confidence = sum(entry["confidence"] for entry in self.repair_history) / total_repairs
        avg_execution_time = sum(entry["execution_time"] for entry in self.repair_history) / total_repairs
        
        return {
            "total_repairs": total_repairs,
            "successful_repairs": successful_repairs,
            "success_rate": successful_repairs / total_repairs,
            "average_confidence": avg_confidence,
            "average_execution_time": avg_execution_time,
            "error_type_statistics": error_type_stats
        }

def main():
    """測試函數"""
    from mcptool.core.error_detection_analyzer import GAIAErrorDetectionAnalyzer
    from mcptool.core.automatic_tool_creation_engine import AutomaticToolCreationEngine
    
    # 創建測試數據
    analyzer = GAIAErrorDetectionAnalyzer()
    tool_engine = AutomaticToolCreationEngine()
    cli_system = CLIDrivenRepairSystem()
    
    # 模擬錯誤分析結果
    test_result = {
        "test_id": "test_001",
        "status": "partial",
        "confidence": 0.3,
        "actual_answer": "格式錯誤的答案",
        "expected_answer": "正確答案",
        "question": "測試問題",
        "reason": "答案格式不正確"
    }
    
    # 分析錯誤
    error_analysis = analyzer.analyze_gaia_test_result(test_result)
    
    # 創建修復工具
    created_tool = tool_engine.analyze_and_create_tool(error_analysis)
    
    # 創建CLI修復請求
    repair_request = CLIRepairRequest(
        request_id=str(uuid.uuid4()),
        error_analysis=error_analysis,
        created_tool=created_tool,
        input_data={"input_data": "格式錯誤的答案"},
        repair_options={},
        priority=1,
        timeout=60
    )
    
    # 執行CLI修復
    repair_result = cli_system.execute_cli_repair(repair_request)
    
    print(f"修復結果: {repair_result.success}")
    print(f"置信度: {repair_result.confidence}")
    print(f"修復數據: {repair_result.repaired_data}")

if __name__ == "__main__":
    main()

