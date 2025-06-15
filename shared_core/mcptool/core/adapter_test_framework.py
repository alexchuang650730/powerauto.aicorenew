#!/usr/bin/env python3
"""
PowerAutomation 適配器測試框架

為每個適配器提供全面的測試功能
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# 添加項目路徑
sys.path.append('/home/ubuntu/Powerauto.ai')

from mcptool.core.enhanced_error_handling import enhanced_logger, safe_executor, debug_helper
from mcptool.core.unified_adapter_interface import UnifiedAdapterRegistry
from mcptool.adapters.core.safe_mcp_registry import CompleteMCPRegistry

class AdapterTestCase:
    """適配器測試用例"""
    
    def __init__(self, name: str, query: str, expected_type: str = None, timeout: float = 30.0):
        self.name = name
        self.query = query
        self.expected_type = expected_type
        self.timeout = timeout

class AdapterTestFramework:
    """適配器測試框架"""
    
    def __init__(self):
        self.logger = enhanced_logger
        self.test_results = {}
        self.unified_registry = None
        self._initialize_registry()
        
        # 定義測試用例
        self.test_cases = self._create_test_cases()
    
    def _initialize_registry(self):
        """初始化統一註冊表"""
        try:
            self.logger.info("初始化適配器註冊表...")
            original_registry = CompleteMCPRegistry()
            self.unified_registry = UnifiedAdapterRegistry(original_registry)
            self.logger.info(f"註冊表初始化完成，可用適配器: {len(self.unified_registry.list_adapters())}")
        except Exception as e:
            self.logger.error(f"註冊表初始化失敗: {e}")
            raise
    
    def _create_test_cases(self) -> List[AdapterTestCase]:
        """創建測試用例"""
        return [
            # 基礎功能測試
            AdapterTestCase("basic_hello", "Hello", "string"),
            AdapterTestCase("basic_math", "What is 2+2?", "string"),
            AdapterTestCase("basic_question", "What is the capital of France?", "string"),
            
            # AI模型特定測試
            AdapterTestCase("ai_reasoning", "Explain why the sky is blue in simple terms", "string"),
            AdapterTestCase("ai_creative", "Write a short poem about technology", "string"),
            
            # 工具引擎測試
            AdapterTestCase("tool_analysis", "Analyze this text: 'Hello World'", "string"),
            AdapterTestCase("tool_processing", "Process data: [1, 2, 3, 4, 5]", "string"),
            
            # 記憶系統測試
            AdapterTestCase("memory_query", "Search for information about Python", "string"),
            AdapterTestCase("memory_store", "Store this information: Test data", "string"),
            
            # Web代理測試
            AdapterTestCase("web_search", "Search for latest news about AI", "string"),
            AdapterTestCase("web_task", "Find information about weather", "string"),
            
            # 錯誤處理測試
            AdapterTestCase("empty_query", "", "string"),
            AdapterTestCase("long_query", "A" * 1000, "string"),
            AdapterTestCase("special_chars", "Test with special chars: @#$%^&*()", "string"),
        ]
    
    def test_single_adapter(self, adapter_name: str) -> Dict[str, Any]:
        """測試單個適配器"""
        self.logger.info(f"開始測試適配器: {adapter_name}")
        
        adapter = self.unified_registry.get_adapter(adapter_name)
        if not adapter:
            return {
                "adapter_name": adapter_name,
                "success": False,
                "error": "適配器不存在",
                "test_results": []
            }
        
        # 獲取適配器信息
        adapter_info = adapter.get_adapter_info()
        self.logger.info(f"適配器信息: {adapter_info['adapter_type']}, 調用方法: {adapter_info['call_method']}")
        
        test_results = []
        successful_tests = 0
        
        for test_case in self.test_cases:
            self.logger.debug(f"執行測試用例: {test_case.name}")
            
            test_result = self._run_test_case(adapter, test_case)
            test_results.append(test_result)
            
            if test_result["success"]:
                successful_tests += 1
                self.logger.debug(f"✅ {test_case.name}: 成功")
            else:
                self.logger.warning(f"❌ {test_case.name}: {test_result['error']}")
        
        success_rate = successful_tests / len(self.test_cases) if self.test_cases else 0
        
        result = {
            "adapter_name": adapter_name,
            "adapter_info": adapter_info,
            "success": success_rate > 0.5,  # 50%以上成功率視為通過
            "success_rate": success_rate,
            "successful_tests": successful_tests,
            "total_tests": len(self.test_cases),
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"適配器 {adapter_name} 測試完成: {successful_tests}/{len(self.test_cases)} 成功 ({success_rate:.1%})")
        
        return result
    
    def _run_test_case(self, adapter, test_case: AdapterTestCase) -> Dict[str, Any]:
        """運行單個測試用例"""
        start_time = time.time()
        
        try:
            # 使用安全執行器運行測試
            result = safe_executor.safe_call(
                adapter.process,
                test_case.query,
                max_retries=1,  # 測試時不重試
                retry_delay=0
            )
            
            execution_time = time.time() - start_time
            
            if result["success"]:
                response_data = result["result"]
                
                # 驗證響應格式
                validation_result = self._validate_response(response_data, test_case)
                
                return {
                    "test_name": test_case.name,
                    "query": test_case.query,
                    "success": validation_result["valid"],
                    "response": response_data,
                    "execution_time": execution_time,
                    "validation": validation_result,
                    "error": None
                }
            else:
                return {
                    "test_name": test_case.name,
                    "query": test_case.query,
                    "success": False,
                    "response": None,
                    "execution_time": execution_time,
                    "error": result["error"]
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "test_name": test_case.name,
                "query": test_case.query,
                "success": False,
                "response": None,
                "execution_time": execution_time,
                "error": str(e)
            }
    
    def _validate_response(self, response: Dict[str, Any], test_case: AdapterTestCase) -> Dict[str, Any]:
        """驗證響應格式"""
        validation = {
            "valid": True,
            "issues": []
        }
        
        # 檢查響應是否為字典
        if not isinstance(response, dict):
            validation["valid"] = False
            validation["issues"].append("響應不是字典格式")
            return validation
        
        # 檢查必需字段
        required_fields = ["success", "data"]
        for field in required_fields:
            if field not in response:
                validation["valid"] = False
                validation["issues"].append(f"缺少必需字段: {field}")
        
        # 檢查success字段
        if "success" in response and not isinstance(response["success"], bool):
            validation["valid"] = False
            validation["issues"].append("success字段應為布爾值")
        
        # 檢查data字段
        if "data" in response:
            data = response["data"]
            if test_case.expected_type == "string" and not isinstance(data, str):
                validation["issues"].append(f"期望字符串類型，實際: {type(data).__name__}")
            
            # 檢查數據是否為空
            if not data or (isinstance(data, str) and not data.strip()):
                validation["issues"].append("響應數據為空")
        
        # 檢查響應時間
        if "execution_time" in response and response.get("execution_time", 0) > 30:
            validation["issues"].append("響應時間過長")
        
        return validation
    
    def test_all_adapters(self) -> Dict[str, Any]:
        """測試所有適配器"""
        self.logger.info("開始測試所有適配器...")
        
        adapter_names = self.unified_registry.list_adapters()
        self.logger.info(f"發現 {len(adapter_names)} 個適配器")
        
        all_results = {}
        successful_adapters = 0
        
        for adapter_name in adapter_names:
            try:
                result = self.test_single_adapter(adapter_name)
                all_results[adapter_name] = result
                
                if result["success"]:
                    successful_adapters += 1
                    
            except Exception as e:
                self.logger.error(f"測試適配器 {adapter_name} 時發生錯誤: {e}")
                all_results[adapter_name] = {
                    "adapter_name": adapter_name,
                    "success": False,
                    "error": str(e),
                    "test_results": []
                }
        
        # 生成總結報告
        summary = {
            "total_adapters": len(adapter_names),
            "successful_adapters": successful_adapters,
            "success_rate": successful_adapters / len(adapter_names) if adapter_names else 0,
            "timestamp": datetime.now().isoformat(),
            "test_framework_version": "1.0.0"
        }
        
        return {
            "summary": summary,
            "detailed_results": all_results
        }
    
    def test_critical_adapters(self) -> Dict[str, Any]:
        """測試關鍵適配器"""
        critical_adapters = [
            "gemini", "claude", "smart_tool_engine", 
            "webagent", "unified_memory", "context_monitor"
        ]
        
        self.logger.info(f"測試關鍵適配器: {critical_adapters}")
        
        results = {}
        for adapter_name in critical_adapters:
            if adapter_name in self.unified_registry.list_adapters():
                results[adapter_name] = self.test_single_adapter(adapter_name)
            else:
                self.logger.warning(f"關鍵適配器 {adapter_name} 不存在")
                results[adapter_name] = {
                    "adapter_name": adapter_name,
                    "success": False,
                    "error": "適配器不存在"
                }
        
        return results
    
    def generate_test_report(self, results: Dict[str, Any], save_path: str = None) -> str:
        """生成測試報告"""
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"/home/ubuntu/Powerauto.ai/adapter_test_report_{timestamp}.json"
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"測試報告已保存: {save_path}")
            return save_path
            
        except Exception as e:
            self.logger.error(f"保存測試報告失敗: {e}")
            return None
    
    def print_summary(self, results: Dict[str, Any]):
        """打印測試摘要"""
        if "summary" in results:
            summary = results["summary"]
            print(f"\\n📊 適配器測試摘要")
            print(f"總適配器數: {summary['total_adapters']}")
            print(f"成功適配器: {summary['successful_adapters']}")
            print(f"成功率: {summary['success_rate']:.1%}")
            print(f"測試時間: {summary['timestamp']}")
        
        if "detailed_results" in results:
            print(f"\\n📋 詳細結果:")
            for adapter_name, result in results["detailed_results"].items():
                if result["success"]:
                    success_rate = result.get("success_rate", 0)
                    print(f"  ✅ {adapter_name}: {success_rate:.1%} ({result.get('successful_tests', 0)}/{result.get('total_tests', 0)})")
                else:
                    error = result.get("error", "未知錯誤")
                    print(f"  ❌ {adapter_name}: {error}")

# 測試腳本
if __name__ == "__main__":
    print("🧪 PowerAutomation 適配器測試框架")
    
    try:
        # 創建測試框架
        test_framework = AdapterTestFramework()
        
        # 選擇測試模式
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == "critical":
            print("\\n🎯 執行關鍵適配器測試...")
            results = test_framework.test_critical_adapters()
        else:
            print("\\n🔍 執行全面適配器測試...")
            results = test_framework.test_all_adapters()
        
        # 打印摘要
        test_framework.print_summary(results)
        
        # 保存報告
        report_path = test_framework.generate_test_report(results)
        if report_path:
            print(f"\\n📄 測試報告: {report_path}")
        
        print("\\n🎯 適配器測試完成")
        
    except Exception as e:
        print(f"❌ 測試框架執行失敗: {e}")
        import traceback
        traceback.print_exc()

