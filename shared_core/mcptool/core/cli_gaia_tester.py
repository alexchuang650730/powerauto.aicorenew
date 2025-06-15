#!/usr/bin/env python3
"""
PowerAutomation CLI接口GAIA測試器

使用CLI接口進行端到端測試
"""

import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class CLIGAIATester:
    """使用CLI接口的GAIA測試器"""
    
    def __init__(self):
        self.project_root = Path("/home/ubuntu/Powerauto.ai")
        self.cli_script = self.project_root / "mcptool/cli/safe_unified_mcp_cli.py"
        self.test_results = []
        
        # 檢查CLI腳本是否存在
        if not self.cli_script.exists():
            raise FileNotFoundError(f"CLI腳本不存在: {self.cli_script}")
        
        print(f"✅ CLI腳本路徑: {self.cli_script}")
        
        # 載入GAIA測試題目
        self._load_gaia_questions()
    
    def _load_gaia_questions(self):
        """載入GAIA測試題目"""
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
            }
        ]
        
        print(f"✅ 載入 {len(self.gaia_questions)} 個GAIA測試題目")
    
    def _get_available_adapters(self) -> List[str]:
        """獲取可用適配器列表"""
        try:
            cmd = [
                "python3", str(self.cli_script),
                "list"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析輸出獲取適配器列表
                output_lines = result.stdout.strip().split('\\n')
                adapters = []
                
                for line in output_lines:
                    if line.strip() and not line.startswith('INFO') and not line.startswith('WARNING'):
                        # 假設適配器名稱在每行中
                        if ':' in line:
                            adapter_name = line.split(':')[0].strip()
                            adapters.append(adapter_name)
                
                return adapters
            else:
                print(f"❌ 獲取適配器列表失敗: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ 獲取適配器列表異常: {e}")
            return []
    
    def _select_adapter_for_question(self, question: Dict[str, Any], available_adapters: List[str]) -> str:
        """為問題選擇適配器"""
        category = question.get("category", "general")
        
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
        
        # 選擇第一個可用的首選適配器
        for adapter_name in preferred_adapters:
            if adapter_name in available_adapters:
                return adapter_name
        
        # 如果沒有首選適配器可用，選擇第一個可用的
        if available_adapters:
            return available_adapters[0]
        
        return "claude"  # 默認適配器
    
    def _call_cli(self, adapter_name: str, question: str, timeout: int = 60) -> Dict[str, Any]:
        """調用CLI接口"""
        try:
            # 修正CLI調用格式
            cmd = [
                "python3", str(self.cli_script),
                "test", adapter_name,
                "--query", question,
                "--format", "json"
            ]
            
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # 嘗試解析JSON輸出
                try:
                    output_data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "data": output_data,
                        "execution_time": execution_time,
                        "raw_stdout": result.stdout,
                        "raw_stderr": result.stderr
                    }
                except json.JSONDecodeError:
                    # 如果不是JSON格式，返回原始文本
                    return {
                        "success": True,
                        "data": {"response": result.stdout.strip()},
                        "execution_time": execution_time,
                        "raw_stdout": result.stdout,
                        "raw_stderr": result.stderr
                    }
            else:
                return {
                    "success": False,
                    "error": result.stderr or "CLI調用失敗",
                    "execution_time": execution_time,
                    "return_code": result.returncode,
                    "raw_stdout": result.stdout,
                    "raw_stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"CLI調用超時 ({timeout}s)",
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"CLI調用異常: {e}",
                "execution_time": 0
            }
    
    def _extract_answer(self, cli_response: Dict[str, Any]) -> str:
        """從CLI響應中提取答案"""
        if not cli_response.get("success"):
            return ""
        
        data = cli_response.get("data", {})
        
        # 嘗試從不同字段提取答案
        answer_fields = ["response", "answer", "result", "data", "text"]
        
        for field in answer_fields:
            if field in data:
                answer = data[field]
                if isinstance(answer, str) and answer.strip():
                    return answer.strip()
        
        # 如果沒有找到，嘗試從原始輸出提取
        raw_stdout = cli_response.get("raw_stdout", "")
        if raw_stdout:
            # 移除日誌信息，只保留實際響應
            lines = raw_stdout.split('\\n')
            for line in lines:
                if line.strip() and not line.startswith('INFO') and not line.startswith('WARNING') and not line.startswith('ERROR'):
                    return line.strip()
        
        return str(data) if data else ""
    
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
            text = re.sub(r'[^\\w\\s]', '', text)
            text = re.sub(r'\\s+', ' ', text).strip()
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
        actual_numbers = re.findall(r'\\d+', actual_answer)
        expected_numbers = re.findall(r'\\d+', expected_answer)
        
        if actual_numbers and expected_numbers:
            return actual_numbers[0] == expected_numbers[0]
        
        return False
    
    def _process_single_question(self, question: Dict[str, Any], available_adapters: List[str]) -> Dict[str, Any]:
        """處理單個問題"""
        question_id = question["id"]
        print(f"🔍 處理問題 {question_id}: {question['question'][:50]}...")
        
        # 選擇適配器
        adapter_name = self._select_adapter_for_question(question, available_adapters)
        print(f"   使用適配器: {adapter_name}")
        
        # 調用CLI
        cli_response = self._call_cli(adapter_name, question["question"])
        
        if cli_response["success"]:
            # 提取答案
            actual_answer = self._extract_answer(cli_response)
            
            # 評估答案
            is_correct = self._evaluate_answer(actual_answer, question["expected_answer"])
            
            result = {
                "question_id": question_id,
                "question": question["question"],
                "expected_answer": question["expected_answer"],
                "actual_answer": actual_answer,
                "adapter_used": adapter_name,
                "correct": is_correct,
                "execution_time": cli_response["execution_time"],
                "success": True,
                "category": question.get("category", "unknown"),
                "difficulty": question.get("difficulty", "unknown"),
                "cli_response": cli_response
            }
            
            if is_correct:
                print(f"   ✅ 正確: {actual_answer}")
            else:
                print(f"   ❌ 錯誤: 期望 '{question['expected_answer']}', 實際 '{actual_answer}'")
            
            return result
        else:
            print(f"   ❌ CLI調用失敗: {cli_response['error']}")
            
            return {
                "question_id": question_id,
                "question": question["question"],
                "expected_answer": question["expected_answer"],
                "actual_answer": None,
                "adapter_used": adapter_name,
                "correct": False,
                "execution_time": cli_response["execution_time"],
                "success": False,
                "error": cli_response["error"],
                "category": question.get("category", "unknown"),
                "difficulty": question.get("difficulty", "unknown"),
                "cli_response": cli_response
            }
    
    def run_gaia_test(self, question_limit: Optional[int] = None) -> Dict[str, Any]:
        """運行GAIA測試"""
        print("🎯 開始CLI接口GAIA Level 1測試")
        
        # 獲取可用適配器
        print("📋 獲取可用適配器...")
        available_adapters = self._get_available_adapters()
        
        if not available_adapters:
            # 如果無法獲取適配器列表，使用默認列表
            available_adapters = ["claude", "gemini", "smart_tool_engine", "webagent", "unified_memory"]
            print(f"⚠️  使用默認適配器列表: {available_adapters}")
        else:
            print(f"✅ 發現 {len(available_adapters)} 個可用適配器: {available_adapters}")
        
        # 限制問題數量（用於測試）
        questions_to_test = self.gaia_questions
        if question_limit:
            questions_to_test = self.gaia_questions[:question_limit]
        
        print(f"📝 測試 {len(questions_to_test)} 個問題")
        
        results = []
        correct_count = 0
        
        for i, question in enumerate(questions_to_test, 1):
            print(f"\\n進度: {i}/{len(questions_to_test)}")
            
            result = self._process_single_question(question, available_adapters)
            results.append(result)
            
            if result["correct"]:
                correct_count += 1
        
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
            "available_adapters": available_adapters,
            "timestamp": datetime.now().isoformat(),
            "test_version": "cli_v1.0"
        }
        
        print(f"\\n🎯 CLI GAIA測試完成: {correct_count}/{len(questions_to_test)} 正確 ({accuracy:.1%})")
        
        return {
            "summary": test_summary,
            "detailed_results": results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """保存測試結果"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/ubuntu/Powerauto.ai/gaia_cli_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 測試結果已保存: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存測試結果失敗: {e}")
            return None
    
    def print_summary(self, results: Dict[str, Any]):
        """打印測試摘要"""
        summary = results["summary"]
        
        print(f"\\n📊 CLI GAIA Level 1 測試摘要")
        print(f"總問題數: {summary['total_questions']}")
        print(f"正確答案: {summary['correct_answers']}")
        print(f"準確率: {summary['accuracy']:.1%}")
        print(f"測試時間: {summary['timestamp']}")
        print(f"可用適配器: {len(summary['available_adapters'])}")
        
        print(f"\\n📋 按類別統計:")
        for category, stats in summary['category_stats'].items():
            print(f"  {category}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})")
        
        print(f"\\n🤖 按適配器統計:")
        for adapter, stats in summary['adapter_stats'].items():
            print(f"  {adapter}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.1%})")

# 測試腳本
if __name__ == "__main__":
    print("🧪 PowerAutomation CLI接口GAIA測試器")
    
    try:
        # 創建測試器
        tester = CLIGAIATester()
        
        # 運行測試（先測試5個問題）
        print("\\n🎯 運行CLI GAIA Level 1測試（前5題）...")
        results = tester.run_gaia_test(question_limit=5)
        
        # 打印摘要
        tester.print_summary(results)
        
        # 保存結果
        result_file = tester.save_results(results)
        if result_file:
            print(f"\\n📄 測試結果: {result_file}")
        
        print("\\n🎯 CLI GAIA測試完成")
        
    except Exception as e:
        print(f"❌ 測試器執行失敗: {e}")
        import traceback
        traceback.print_exc()

