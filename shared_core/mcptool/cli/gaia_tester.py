#!/usr/bin/env python3
"""
GAIA測試器
使用安全的MCP註冊表進行GAIA基準測試
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from datasets import load_dataset

logger = logging.getLogger(__name__)

class GAIATester:
    """GAIA測試器"""
    
    def __init__(self, registry, available_adapters: List[str]):
        self.registry = registry
        self.available_adapters = available_adapters
        self.test_results = []
        self.adapter_usage = {}
        
        # 初始化適配器使用統計
        for adapter_id in available_adapters:
            self.adapter_usage[adapter_id] = 0
    
    def run_test(self, level: int = 1, max_tasks: int = 10) -> Dict[str, Any]:
        """運行GAIA測試"""
        print(f"開始GAIA Level {level} 測試...")
        
        start_time = time.time()
        
        try:
            # 加載GAIA數據集
            dataset = load_dataset("gaia-benchmark/GAIA", "2023_all")
            validation_data = dataset["validation"]
            
            # 過濾指定級別的問題
            level_questions = [
                item for item in validation_data 
                if item["Level"] == str(level)  # Level是字符串類型
            ]
            
            if not level_questions:
                raise ValueError(f"沒有找到Level {level}的問題")
            
            # 限制測試數量
            test_questions = level_questions[:max_tasks]
            
            print(f"找到 {len(level_questions)} 個Level {level}問題，測試前 {len(test_questions)} 個")
            
            # 逐個處理問題
            correct_count = 0
            
            for i, question_data in enumerate(test_questions):
                print(f"\\n處理問題 {i+1}/{len(test_questions)}...")
                
                result = self._process_question(question_data, i+1)
                self.test_results.append(result)
                
                if result["is_correct"]:
                    correct_count += 1
                
                # 顯示進度
                accuracy = (correct_count / (i+1)) * 100
                print(f"當前準確率: {accuracy:.1f}% ({correct_count}/{i+1})")
            
            # 計算最終結果
            total_time = time.time() - start_time
            final_accuracy = correct_count / len(test_questions)
            
            results = {
                "level": level,
                "total_questions": len(test_questions),
                "correct_answers": correct_count,
                "accuracy": final_accuracy,
                "processing_time": total_time,
                "adapter_usage": self.adapter_usage,
                "test_results": self.test_results
            }
            
            # 保存結果
            self._save_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"GAIA測試失敗: {e}")
            raise
    
    def _process_question(self, question_data: Dict[str, Any], question_num: int) -> Dict[str, Any]:
        """處理單個問題"""
        question = question_data["Question"]
        expected_answer = question_data["Final answer"]
        task_id = question_data.get("task_id", f"question_{question_num}")
        
        print(f"問題: {question[:100]}...")
        print(f"期望答案: {expected_answer}")
        
        start_time = time.time()
        
        try:
            # 選擇適配器並處理問題
            ai_answer = self._get_ai_answer(question, question_data)
            
            # 比較答案
            is_correct = self._compare_answers(ai_answer, expected_answer)
            
            processing_time = time.time() - start_time
            
            result = {
                "task_id": task_id,
                "question": question,
                "ai_answer": ai_answer,
                "expected_answer": expected_answer,
                "is_correct": is_correct,
                "processing_time": processing_time,
                "has_file": bool(question_data.get("file_name")),
                "file_name": question_data.get("file_name", "")
            }
            
            print(f"AI答案: {ai_answer}")
            print(f"結果: {'✅ 正確' if is_correct else '❌ 錯誤'}")
            print(f"處理時間: {processing_time:.2f}秒")
            
            return result
            
        except Exception as e:
            logger.error(f"處理問題失敗: {e}")
            return {
                "task_id": task_id,
                "question": question,
                "ai_answer": f"錯誤: {str(e)}",
                "expected_answer": expected_answer,
                "is_correct": False,
                "processing_time": time.time() - start_time,
                "has_file": bool(question_data.get("file_name")),
                "file_name": question_data.get("file_name", ""),
                "error": str(e)
            }
    
    def _get_ai_answer(self, question: str, question_data: Dict[str, Any]) -> str:
        """獲取AI答案"""
        # 選擇最佳適配器
        adapter_id = self._select_adapter(question, question_data)
        
        try:
            # 獲取適配器實例
            adapter = self.registry.get_adapter(adapter_id)
            
            # 更新使用統計
            self.adapter_usage[adapter_id] += 1
            
            # 處理問題
            if hasattr(adapter, 'process'):
                answer = adapter.process(question)
            else:
                # 備用方法
                answer = f"適配器 {adapter_id} 處理: {question[:50]}..."
            
            return str(answer)
            
        except Exception as e:
            logger.error(f"適配器 {adapter_id} 處理失敗: {e}")
            
            # 嘗試備用適配器
            for backup_adapter in self.available_adapters:
                if backup_adapter != adapter_id:
                    try:
                        backup = self.registry.get_adapter(backup_adapter)
                        self.adapter_usage[backup_adapter] += 1
                        
                        if hasattr(backup, 'process'):
                            return str(backup.process(question))
                        
                    except Exception as backup_error:
                        logger.error(f"備用適配器 {backup_adapter} 也失敗: {backup_error}")
                        continue
            
            # 所有適配器都失敗
            raise Exception(f"所有適配器都無法處理問題: {e}")
    
    def _select_adapter(self, question: str, question_data: Dict[str, Any]) -> str:
        """選擇最佳適配器"""
        question_lower = question.lower()
        
        # 獲取可用適配器列表
        available_list = list(self.available_adapters.keys()) if isinstance(self.available_adapters, dict) else self.available_adapters
        
        # 如果有文件附件，優先使用支持多模態的適配器
        if question_data.get("file_name"):
            if "gemini" in available_list:
                return "gemini"
        
        # 需要網頁搜索或信息檢索
        if any(keyword in question_lower for keyword in ["wikipedia", "google", "search", "website", "url", "http"]):
            if "webagent" in available_list:
                return "webagent"
        
        # 需要工具或計算
        if any(keyword in question_lower for keyword in ["計算", "數學", "math", "calculate", "工具", "tool"]):
            if "smart_tool_engine" in available_list:
                return "smart_tool_engine"
        
        # 需要複雜推理
        if any(keyword in question_lower for keyword in ["分析", "推理", "邏輯", "analyze", "reasoning", "logic"]):
            if "sequential_thinking" in available_list:
                return "sequential_thinking"
        
        # 需要動態工具創建（最後防線）
        if any(keyword in question_lower for keyword in ["創建", "生成", "create", "generate", "新工具"]):
            if "kilocode" in available_list:
                return "kilocode"
        
        # 默認選擇：優先使用Claude，然後Gemini
        if "claude" in available_list:
            return "claude"
        elif "gemini" in available_list:
            return "gemini"
        elif available_list:
            return available_list[0]
        else:
            raise Exception("沒有可用的適配器")
    
    def _compare_answers(self, ai_answer: str, expected_answer: str) -> bool:
        """
        if not ai_answer or not expected_answer:
            return False
        
        # 清理答案文本
        ai_clean = str(ai_answer).strip().lower()
        expected_clean = str(expected_answer).strip().lower()
        
        # 精確匹配
        if ai_clean == expected_clean:
            return True
        
        # 包含匹配
        if expected_clean in ai_clean or ai_clean in expected_clean:
            return True
        
        # 數字匹配
        try:
            ai_num = float(ai_clean)
            expected_num = float(expected_clean)
            return abs(ai_num - expected_num) < 0.001
        except:
            pass
        
        return False
    
    def _save_results(self, results: Dict[str, Any]):
        """保存測試結果"""
        timestamp = int(time.time())
        filename = f"gaia_level{results['level']}_safe_test_results_{timestamp}.json"
        filepath = Path("/home/ubuntu/Powerauto.ai") / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\\n結果已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存結果失敗: {e}")

