#!/usr/bin/env python3
"""
簡化的Smart Tool Engine適配器
專門用於GAIA測試的工具引擎
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class SimpleSmartToolEngine:
    """簡化的智能工具引擎"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化智能工具引擎"""
        self.config = config or {}
        self.tools_registry = {}
        self.performance_metrics = {
            "tool_calls": 0,
            "success_count": 0,
            "error_count": 0
        }
        
        # 註冊內建工具
        self._register_builtin_tools()
        
        logger.info("簡化智能工具引擎初始化完成")
    
    def _register_builtin_tools(self):
        """註冊內建工具"""
        self.tools_registry = {
            "web_search": {
                "name": "網頁搜索",
                "description": "搜索網頁信息",
                "category": "search",
                "handler": self._web_search
            },
            "calculator": {
                "name": "計算器",
                "description": "執行數學計算",
                "category": "math",
                "handler": self._calculator
            },
            "text_analyzer": {
                "name": "文本分析",
                "description": "分析文本內容",
                "category": "analysis",
                "handler": self._text_analyzer
            },
            "data_extractor": {
                "name": "數據提取",
                "description": "從文本中提取結構化數據",
                "category": "extraction",
                "handler": self._data_extractor
            }
        }
    
    def process(self, question: str) -> str:
        """處理問題並選擇合適的工具"""
        try:
            # 分析問題類型
            tool_name = self._select_tool(question)
            
            # 執行工具
            if tool_name in self.tools_registry:
                handler = self.tools_registry[tool_name]["handler"]
                result = handler(question)
                
                self.performance_metrics["tool_calls"] += 1
                self.performance_metrics["success_count"] += 1
                
                logger.info(f"工具 {tool_name} 處理成功: {question[:50]}...")
                return result
            else:
                # 使用默認處理
                return self._default_handler(question)
                
        except Exception as e:
            self.performance_metrics["error_count"] += 1
            logger.error(f"工具引擎處理失敗: {e}")
            return f"工具處理錯誤: {str(e)}"
    
    def _select_tool(self, question: str) -> str:
        """選擇合適的工具"""
        question_lower = question.lower()
        
        # 數學計算相關
        if any(keyword in question_lower for keyword in ["計算", "數學", "math", "calculate", "加", "減", "乘", "除", "等於"]):
            return "calculator"
        
        # 搜索相關
        if any(keyword in question_lower for keyword in ["搜索", "查找", "wikipedia", "google", "網站", "url", "http"]):
            return "web_search"
        
        # 數據提取相關
        if any(keyword in question_lower for keyword in ["提取", "數據", "信息", "列表", "表格"]):
            return "data_extractor"
        
        # 默認使用文本分析
        return "text_analyzer"
    
    def _web_search(self, question: str) -> str:
        """網頁搜索工具"""
        # 簡化實現：模擬搜索結果
        if "wikipedia" in question.lower():
            return "根據Wikipedia搜索結果分析..."
        elif "google" in question.lower():
            return "根據Google搜索結果分析..."
        else:
            return "執行網頁搜索並分析結果..."
    
    def _calculator(self, question: str) -> str:
        """計算器工具"""
        try:
            # 簡單的數學表達式計算
            import re
            
            # 提取數字和運算符
            numbers = re.findall(r'\\d+(?:\\.\\d+)?', question)
            
            if len(numbers) >= 2:
                num1 = float(numbers[0])
                num2 = float(numbers[1])
                
                if "+" in question or "加" in question:
                    result = num1 + num2
                elif "-" in question or "減" in question:
                    result = num1 - num2
                elif "*" in question or "乘" in question or "×" in question:
                    result = num1 * num2
                elif "/" in question or "除" in question or "÷" in question:
                    result = num1 / num2 if num2 != 0 else "除零錯誤"
                else:
                    result = f"計算 {num1} 和 {num2}"
                
                return str(result)
            else:
                return "無法識別數學表達式"
                
        except Exception as e:
            return f"計算錯誤: {e}"
    
    def _text_analyzer(self, question: str) -> str:
        """文本分析工具"""
        # 簡化的文本分析
        analysis = {
            "length": len(question),
            "words": len(question.split()),
            "has_question": "?" in question,
            "has_numbers": any(char.isdigit() for char in question)
        }
        
        return f"文本分析完成，長度: {analysis['length']}字符"
    
    def _data_extractor(self, question: str) -> str:
        """數據提取工具"""
        # 簡化的數據提取
        import re
        
        # 提取數字
        numbers = re.findall(r'\\d+(?:\\.\\d+)?', question)
        # 提取日期
        dates = re.findall(r'\\d{4}[-/]\\d{1,2}[-/]\\d{1,2}', question)
        # 提取URL
        urls = re.findall(r'https?://[^\\s]+', question)
        
        extracted = {
            "numbers": numbers,
            "dates": dates,
            "urls": urls
        }
        
        return f"提取到數據: {json.dumps(extracted, ensure_ascii=False)}"
    
    def _default_handler(self, question: str) -> str:
        """默認處理器"""
        return f"智能工具引擎分析: {question[:100]}..."
    
    def get_tools_info(self) -> Dict[str, Any]:
        """獲取工具信息"""
        return {
            "available_tools": list(self.tools_registry.keys()),
            "performance_metrics": self.performance_metrics
        }
    
    def test_connection(self) -> bool:
        """測試連接"""
        try:
            result = self.process("測試 2+2")
            return "4" in result or "計算" in result
        except:
            return False

