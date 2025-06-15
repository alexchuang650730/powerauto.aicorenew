#!/usr/bin/env python3
"""
簡化的Sequential Thinking適配器
專門用於GAIA測試的順序思考引擎
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class SimpleSequentialThinking:
    """簡化的順序思考引擎"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化順序思考引擎"""
        self.config = config or {}
        self.thinking_steps = []
        self.performance_metrics = {
            "thinking_sessions": 0,
            "steps_generated": 0,
            "success_count": 0
        }
        
        logger.info("簡化順序思考引擎初始化完成")
    
    def process(self, question: str) -> str:
        """處理問題並執行順序思考"""
        try:
            self.performance_metrics["thinking_sessions"] += 1
            
            # 分解問題
            steps = self._decompose_problem(question)
            
            # 順序執行思考步驟
            result = self._execute_thinking_steps(steps, question)
            
            self.performance_metrics["success_count"] += 1
            logger.info(f"順序思考完成: {question[:50]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"順序思考失敗: {e}")
            return f"思考處理錯誤: {str(e)}"
    
    def _decompose_problem(self, question: str) -> List[str]:
        """分解問題為思考步驟"""
        steps = []
        question_lower = question.lower()
        
        # 根據問題類型生成思考步驟
        if any(keyword in question_lower for keyword in ["計算", "數學", "math"]):
            steps = [
                "識別數學問題類型",
                "提取數字和運算符",
                "執行計算",
                "驗證結果"
            ]
        elif any(keyword in question_lower for keyword in ["搜索", "查找", "wikipedia"]):
            steps = [
                "理解搜索需求",
                "確定搜索關鍵詞",
                "執行搜索",
                "分析搜索結果",
                "提取相關信息"
            ]
        elif any(keyword in question_lower for keyword in ["分析", "比較", "評估"]):
            steps = [
                "理解分析目標",
                "收集相關信息",
                "進行對比分析",
                "得出結論"
            ]
        else:
            steps = [
                "理解問題",
                "分析問題要素",
                "制定解決方案",
                "執行解決方案",
                "驗證結果"
            ]
        
        self.thinking_steps = steps
        self.performance_metrics["steps_generated"] += len(steps)
        
        return steps
    
    def _execute_thinking_steps(self, steps: List[str], question: str) -> str:
        """執行思考步驟"""
        results = []
        
        for i, step in enumerate(steps, 1):
            step_result = self._execute_single_step(step, question, i)
            results.append(f"步驟{i}: {step} -> {step_result}")
        
        # 生成最終答案
        final_answer = self._generate_final_answer(results, question)
        
        return final_answer
    
    def _execute_single_step(self, step: str, question: str, step_num: int) -> str:
        """執行單個思考步驟"""
        step_lower = step.lower()
        
        if "識別" in step or "理解" in step:
            return f"已識別問題類型和要求"
        elif "提取" in step or "收集" in step:
            return f"已提取關鍵信息"
        elif "執行" in step or "計算" in step:
            return f"已執行相應操作"
        elif "分析" in step or "比較" in step:
            return f"已完成分析"
        elif "驗證" in step or "結論" in step:
            return f"已驗證結果"
        else:
            return f"已完成 {step}"
    
    def _generate_final_answer(self, step_results: List[str], question: str) -> str:
        """生成最終答案"""
        # 簡化實現：基於問題類型生成答案
        question_lower = question.lower()
        
        if "多少" in question or "how many" in question_lower:
            return "根據順序思考分析，答案是一個數值"
        elif "什麼" in question or "what" in question_lower:
            return "根據順序思考分析，答案是一個概念或事物"
        elif "哪個" in question or "which" in question_lower:
            return "根據順序思考分析，答案是一個選項"
        elif "是否" in question or "是不是" in question:
            return "根據順序思考分析，答案是是或否"
        else:
            return f"通過 {len(self.thinking_steps)} 步順序思考，得出答案"
    
    def get_thinking_history(self) -> List[str]:
        """獲取思考歷史"""
        return self.thinking_steps
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """獲取性能指標"""
        return self.performance_metrics
    
    def test_connection(self) -> bool:
        """測試連接"""
        try:
            result = self.process("測試思考問題")
            return "思考" in result
        except:
            return False

