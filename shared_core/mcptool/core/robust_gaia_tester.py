#!/usr/bin/env python3
"""
PowerAutomation 重新設計的GAIA測試器

使用統一適配器接口和增強錯誤處理的健壯測試器
"""

import sys
import json
import time
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 添加項目路徑
sys.path.append('/home/ubuntu/Powerauto.ai')

from mcptool.core.enhanced_error_handling import enhanced_logger, safe_executor, with_error_handling
from mcptool.core.unified_adapter_interface import UnifiedAdapterRegistry
from mcptool.core.api_configuration_manager import APIConfigurationManager
from mcptool.adapters.core.safe_mcp_registry import CompleteMCPRegistry

class RobustGAIATester:
    """健壯的GAIA測試器"""
    
    def __init__(self):
        self.logger = enhanced_logger
        self.unified_registry = None
        self.api_manager = None
        self.test_results = []
        self.gaia_questions = []
        
        # 初始化組件
        self._initialize_components()
        self._load_gaia_questions()
    
    @with_error_handling(logger=enhanced_logger, context={"component": "initialization"})
    def _initialize_components(self):
        """初始化所有組件"""
        self.logger.info("🚀 初始化PowerAutomation GAIA測試器...")
        
        # 初始化API管理器
        self.api_manager = APIConfigurationManager()
        api_status = self.api_manager.get_api_status()
        self.logger.info(f"API狀態: {api_status['valid_apis']}/{api_status['total_apis']} 可用")
        
        # 初始化統一註冊表
        original_registry = CompleteMCPRegistry()
        self.unified_registry = UnifiedAdapterRegistry(original_registry)
        adapter_count = len(self.unified_registry.list_adapters())
        self.logger.info(f"適配器註冊表: {adapter_count} 個適配器可用")
        
        self.logger.info("✅ 組件初始化完成")
    
    def _load_gaia_questions(self):
        """載入GAIA測試題目"""
        try:
            # 嘗試載入完整的165題數據集
            data_file = "/home/ubuntu/Powerauto.ai/gaia_level1_complete_dataset.json"
            with open(data_file, 'r', encoding='utf-8') as f:
                self.gaia_questions = json.load(f)
            
            self.logger.info(f"✅ 載入了 {len(self.gaia_questions)} 個GAIA Level 1測試題目")
            
        except Exception as e:
            self.logger.warning(f"無法載入完整數據集: {e}")
            # 回退到內置的20題
            self._load_builtin_questions()
    
    def _load_builtin_questions(self):
        """載入內置的測試題目"""
        # 模擬GAIA Level 1題目
        self.gaia_questions = [
            {
                "id": "gaia_001",
                "question": "What is the capital of France?",
                "expected_answer": "Paris",
                "category": "geography",
                "difficulty": "easy"
            },
            {
                "id": "gaia_002", 
                "question": "What is 15 + 27?",
                "expected_answer": "42",
                "category": "math",
                "difficulty": "easy"
            },
            {
                "id": "gaia_003",
                "question": "Who wrote the novel '1984'?",
                "expected_answer": "George Orwell",
                "category": "literature", 
                "difficulty": "easy"
            },
            {
                "id": "gaia_004",
                "question": "What is the chemical symbol for gold?",
                "expected_answer": "Au",
                "category": "science",
                "difficulty": "easy"
            },
            {
                "id": "gaia_005",
                "question": "In which year did World War II end?",
                "expected_answer": "1945",
                "category": "history",
                "difficulty": "easy"
            },
            {
                "id": "gaia_006",
                "question": "What is the largest planet in our solar system?",
                "expected_answer": "Jupiter",
                "category": "science",
                "difficulty": "easy"
            },
            {
                "id": "gaia_007",
                "question": "What is the square root of 144?",
                "expected_answer": "12",
                "category": "math",
                "difficulty": "easy"
            },
            {
                "id": "gaia_008",
                "question": "Which continent is Egypt located in?",
                "expected_answer": "Africa",
                "category": "geography",
                "difficulty": "easy"
            },
            {
                "id": "gaia_009",
                "question": "What does GDP stand for?",
                "expected_answer": "Gross Domestic Product",
                "category": "economics",
                "difficulty": "medium"
            },
            {
                "id": "gaia_010",
                "question": "What is the longest river in the world?",
                "expected_answer": "Nile River",
                "category": "geography",
                "difficulty": "medium"
            },
            {
                "id": "gaia_011",
                "question": "What is the atomic number of carbon?",
                "expected_answer": "6",
                "category": "science",
                "difficulty": "medium"
            },
            {
                "id": "gaia_012",
                "question": "Who painted the Mona Lisa?",
                "expected_answer": "Leonardo da Vinci",
                "category": "art",
                "difficulty": "easy"
            },
            {
                "id": "gaia_013",
                "question": "What is 8 × 7?",
                "expected_answer": "56",
                "category": "math",
                "difficulty": "easy"
            },
            {
                "id": "gaia_014",
                "question": "What gas do plants absorb from the atmosphere during photosynthesis?",
                "expected_answer": "Carbon dioxide",
                "category": "science",
                "difficulty": "medium"
            },
            {
                "id": "gaia_015",
                "question": "Which mountain range contains Mount Everest?",
                "expected_answer": "Himalayas",
                "category": "geography",
                "difficulty": "medium"
            },
            {
                "id": "gaia_016",
                "question": "What does HTTP stand for?",
                "expected_answer": "HyperText Transfer Protocol",
                "category": "technology",
                "difficulty": "medium"
            },
            {
                "id": "gaia_017",
                "question": "What is 100 ÷ 4?",
                "expected_answer": "25",
                "category": "math",
                "difficulty": "easy"
            },
            {
                "id": "gaia_018",
                "question": "What is the smallest unit of matter?",
                "expected_answer": "Atom",
                "category": "science",
                "difficulty": "medium"
            },
            {
                "id": "gaia_019",
                "question": "Which ocean is the largest?",
                "expected_answer": "Pacific Ocean",
                "category": "geography",
                "difficulty": "easy"
            },
            {
                "id": "gaia_020",
                "question": "What is the speed of light in vacuum?",
                "expected_answer": "299,792,458 meters per second",
                "category": "science",
                "difficulty": "hard"
            }
        ]
        
        self.logger.info(f"載入 {len(self.gaia_questions)} 個GAIA測試題目")
    
    def _select_best_adapter(self, question: Dict[str, Any]) -> str:
        """根據問題類型選擇最佳適配器"""
        category = question.get("category", "general")
        difficulty = question.get("difficulty", "medium")
        
        # 適配器選擇策略
        adapter_preferences = {
            "math": ["gemini", "claude", "smart_tool_engine"],
            "science": ["claude", "gemini", "unified_memory"],
            "geography": ["claude", "gemini", "webagent"],
            "history": ["claude", "unified_memory", "gemini"],
            "literature": ["claude", "gemini", "unified_memory"],
            "art": ["claude", "gemini", "unified_memory"],
            "economics": ["claude", "gemini", "smart_tool_engine"],
            "technology": ["gemini", "claude", "smart_tool_engine"],
            "general": ["claude", "gemini", "smart_tool_engine"]
        }
        
        # 獲取首選適配器列表
        preferred_adapters = adapter_preferences.get(category, adapter_preferences["general"])
        available_adapters = self.unified_registry.list_adapters()
        
        # 選擇第一個可用的首選適配器
        for adapter_name in preferred_adapters:
            if adapter_name in available_adapters:
                self.logger.debug(f"為 {category} 類問題選擇適配器: {adapter_name}")
                return adapter_name
        
        # 如果沒有首選適配器可用，隨機選擇一個
        if available_adapters:
            fallback_adapter = random.choice(available_adapters)
            self.logger.warning(f"使用fallback適配器: {fallback_adapter}")
            return fallback_adapter
        
        raise ValueError("沒有可用的適配器")
    
    @with_error_handling(logger=enhanced_logger, context={"operation": "process_question"})
    def _process_single_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """處理單個問題"""
        question_id = question["id"]
        self.logger.info(f"處理問題 {question_id}: {question['question'][:50]}...")
        
        start_time = time.time()
        
        try:
            # 選擇最佳適配器
            adapter_name = self._select_best_adapter(question)
            adapter = self.unified_registry.get_adapter(adapter_name)
            
            if not adapter:
                raise ValueError(f"適配器 {adapter_name} 不可用")
            
            # 使用安全執行器處理問題
            result = safe_executor.safe_call(
                adapter.process,
                question["question"],
                max_retries=2,
                retry_delay=1.0
            )
            
            execution_time = time.time() - start_time
            
            if result["success"]:
                response_data = result["result"]
                
                # 提取答案
                answer = self._extract_answer(response_data)
                
                # 評估答案
                is_correct = self._evaluate_answer(answer, question.get("answer", question.get("expected_answer", "")))
                
                return {
                    "question_id": question_id,
                    "question": question["question"],
                    "expected_answer": question.get("answer", question.get("expected_answer", "")),
                    "actual_answer": answer,
                    "adapter_used": adapter_name,
                    "correct": is_correct,
                    "execution_time": execution_time,
                    "raw_response": response_data,
                    "success": True,
                    "category": question.get("category", "unknown"),
                    "difficulty": question.get("difficulty", "unknown")
                }
            else:
                return {
                    "question_id": question_id,
                    "question": question["question"],
                    "expected_answer": question.get("answer", question.get("expected_answer", "")),
                    "actual_answer": None,
                    "adapter_used": adapter_name,
                    "correct": False,
                    "execution_time": execution_time,
                    "error": result["error"],
                    "success": False,
                    "category": question.get("category", "unknown"),
                    "difficulty": question.get("difficulty", "unknown")
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"處理問題 {question_id} 失敗: {e}")
            
            return {
                "question_id": question_id,
                "question": question["question"],
                "expected_answer": question.get("answer", question.get("expected_answer", "")),
                "actual_answer": None,
                "adapter_used": None,
                "correct": False,
                "execution_time": execution_time,
                "error": str(e),
                "success": False,
                "category": question.get("category", "unknown"),
                "difficulty": question.get("difficulty", "unknown")
            }
    
    def _extract_answer(self, response_data: Dict[str, Any]) -> str:
        """從響應中提取答案"""
        if isinstance(response_data, dict):
            # 嘗試從不同字段提取答案
            answer_fields = ["data", "answer", "result", "response", "text"]
            
            for field in answer_fields:
                if field in response_data:
                    answer = response_data[field]
                    if isinstance(answer, str) and answer.strip():
                        return answer.strip()
            
            # 如果沒有找到，返回整個響應的字符串表示
            return str(response_data)
        
        return str(response_data)
    
    def _evaluate_answer(self, actual_answer: str, expected_answer: str) -> bool:
        """評估答案是否正確"""
        if not actual_answer or not expected_answer:
            return False
        
        # 標準化答案（轉小寫，去除標點符號）
        import re
        
        def normalize(text):
            # 轉小寫
            text = text.lower()
            # 移除標點符號和多餘空格
            text = re.sub(r'[^\w\s]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        
        actual_norm = normalize(actual_answer)
        expected_norm = normalize(expected_answer)
        
        # 精確匹配
        if actual_norm == expected_norm:
            return True
        
        # 包含匹配
        if expected_norm in actual_norm or actual_norm in expected_norm:
            return True
        
        # 數字匹配（提取數字進行比較）
        actual_numbers = re.findall(r'\d+', actual_answer)
        expected_numbers = re.findall(r'\d+', expected_answer)
        
        if actual_numbers and expected_numbers:
            return actual_numbers[0] == expected_numbers[0]
        
        return False
    
    def run_gaia_test(self, question_limit: Optional[int] = None) -> Dict[str, Any]:
        """運行GAIA測試"""
        self.logger.info("🎯 開始GAIA Level 1測試")
        
        # 限制問題數量（用於測試）
        questions_to_test = self.gaia_questions
        if question_limit:
            questions_to_test = self.gaia_questions[:question_limit]
        
        self.logger.info(f"測試 {len(questions_to_test)} 個問題")
        
        results = []
        correct_count = 0
        
        for i, question in enumerate(questions_to_test, 1):
            self.logger.info(f"進度: {i}/{len(questions_to_test)}")
            
            result = self._process_single_question(question)
            results.append(result)
            
            if result["correct"]:
                correct_count += 1
                self.logger.info(f"✅ {question['id']}: 正確")
            else:
                self.logger.warning(f"❌ {question['id']}: 錯誤")
                if result.get("error"):
                    self.logger.warning(f"   錯誤: {result['error']}")
                else:
                    self.logger.warning(f"   期望: {question.get('answer', question.get('expected_answer', ''))}")
                    self.logger.warning(f"   實際: {result.get('actual_answer', 'N/A')}")
        
        # 計算統計信息
        accuracy = correct_count / len(questions_to_test) if questions_to_test else 0
        
        # 按類別統計
        category_stats = {}
        for result in results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {"total": 0, "correct": 0}
            category_stats[category]["total"] += 1
            if result["correct"]:
                category_stats[category]["correct"] += 1
        
        # 計算每個類別的準確率
        for category in category_stats:
            stats = category_stats[category]
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        
        # 適配器使用統計
        adapter_stats = {}
        for result in results:
            adapter = result.get("adapter_used", "unknown")
            if adapter not in adapter_stats:
                adapter_stats[adapter] = {"total": 0, "correct": 0}
            adapter_stats[adapter]["total"] += 1
            if result["correct"]:
                adapter_stats[adapter]["correct"] += 1
        
        # 計算每個適配器的準確率
        for adapter in adapter_stats:
            stats = adapter_stats[adapter]
            stats["accuracy"] = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        
        test_summary = {
            "total_questions": len(questions_to_test),
            "correct_answers": correct_count,
            "accuracy": accuracy,
            "category_stats": category_stats,
            "adapter_stats": adapter_stats,
            "timestamp": datetime.now().isoformat(),
            "test_version": "robust_v1.0"
        }
        
        self.logger.info(f"🎯 GAIA測試完成: {correct_count}/{len(questions_to_test)} 正確 ({accuracy:.1%})")
        
        return {
            "summary": test_summary,
            "detailed_results": results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """保存測試結果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/ubuntu/Powerauto.ai/gaia_test_results_robust_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"測試結果已保存: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"保存測試結果失敗: {e}")
            return None
    
    def print_summary(self, results: Dict[str, Any]):
        """打印測試摘要"""
        summary = results["summary"]
        
        print(f"\\n📊 GAIA Level 1 測試摘要")
        print(f"總問題數: {summary['total_questions']}")
        print(f"正確答案: {summary['correct_answers']}")
        print(f"準確率: {summary['accuracy']:.1%}")
        print(f"測試時間: {summary['timestamp']}")
        
        print(f"\\n📋 按類別統計:")
        for category, stats in summary['category_stats'].items():
            print(f"  {category}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})")
        
        print(f"\\n🤖 按適配器統計:")
        for adapter, stats in summary['adapter_stats'].items():
            print(f"  {adapter}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})")

# 測試腳本
if __name__ == "__main__":
    print("🧪 PowerAutomation 健壯GAIA測試器")
    
    try:
        # 創建測試器
        tester = RobustGAIATester()
        
        # 運行測試（先測試5個問題）
        print("\\n🎯 運行GAIA Level 1測試（前5題）...")
        results = tester.run_gaia_test(question_limit=5)
        
        # 打印摘要
        tester.print_summary(results)
        
        # 保存結果
        result_file = tester.save_results(results)
        if result_file:
            print(f"\\n📄 測試結果: {result_file}")
        
        print("\\n🎯 健壯GAIA測試完成")
        
    except Exception as e:
        print(f"❌ 測試器執行失敗: {e}")
        import traceback
        traceback.print_exc()

