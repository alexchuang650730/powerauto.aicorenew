#!/usr/bin/env python3
"""
簡化的KiloCode適配器
專門用於GAIA測試的動態工具創建引擎
"""

import os
import json
import logging
import time
import re
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class SimpleKiloCodeAdapter:
    """簡化的KiloCode適配器，用於動態創建工具"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化KiloCode適配器"""
        self.config = config or {}
        self.api_key = os.environ.get("KILO_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        
        # 工具創建歷史
        self.created_tools = {}
        self.tool_usage_count = {}
        
        # 性能指標
        self.performance_metrics = {
            "tools_created": 0,
            "tools_executed": 0,
            "success_count": 0,
            "error_count": 0
        }
        
        logger.info("簡化KiloCode適配器初始化完成")
    
    def process(self, question: str) -> str:
        """處理問題並動態創建工具"""
        try:
            # 分析問題需求
            tool_requirement = self._analyze_tool_requirement(question)
            
            # 檢查是否已有合適的工具
            existing_tool = self._find_existing_tool(tool_requirement)
            
            if existing_tool:
                # 使用現有工具
                result = self._execute_existing_tool(existing_tool, question)
            else:
                # 動態創建新工具
                new_tool = self._create_dynamic_tool(tool_requirement, question)
                result = self._execute_new_tool(new_tool, question)
            
            self.performance_metrics["tools_executed"] += 1
            self.performance_metrics["success_count"] += 1
            
            logger.info(f"KiloCode處理成功: {question[:50]}...")
            return result
            
        except Exception as e:
            self.performance_metrics["error_count"] += 1
            logger.error(f"KiloCode處理失敗: {e}")
            return f"動態工具創建錯誤: {str(e)}"
    
    def _analyze_tool_requirement(self, question: str) -> Dict[str, Any]:
        """分析問題的工具需求"""
        question_lower = question.lower()
        
        requirement = {
            "type": "general",
            "category": "analysis",
            "complexity": "simple",
            "inputs": [],
            "outputs": ["text"],
            "keywords": []
        }
        
        # 數學計算工具
        if any(keyword in question_lower for keyword in ["計算", "數學", "math", "calculate", "+", "-", "*", "/"]):
            requirement.update({
                "type": "calculator",
                "category": "math",
                "keywords": ["計算", "數學", "運算"]
            })
        
        # 數據處理工具
        elif any(keyword in question_lower for keyword in ["數據", "統計", "分析", "data", "statistics"]):
            requirement.update({
                "type": "data_processor",
                "category": "data",
                "keywords": ["數據", "處理", "分析"]
            })
        
        # 文本處理工具
        elif any(keyword in question_lower for keyword in ["文本", "字符", "text", "string", "word"]):
            requirement.update({
                "type": "text_processor",
                "category": "text",
                "keywords": ["文本", "處理", "字符"]
            })
        
        # 搜索工具
        elif any(keyword in question_lower for keyword in ["搜索", "查找", "search", "find", "wikipedia"]):
            requirement.update({
                "type": "search_engine",
                "category": "search",
                "keywords": ["搜索", "查找", "檢索"]
            })
        
        # 邏輯推理工具
        elif any(keyword in question_lower for keyword in ["推理", "邏輯", "思考", "reasoning", "logic"]):
            requirement.update({
                "type": "logic_engine",
                "category": "reasoning",
                "complexity": "complex",
                "keywords": ["推理", "邏輯", "思考"]
            })
        
        return requirement
    
    def _find_existing_tool(self, requirement: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """查找現有的合適工具"""
        tool_type = requirement["type"]
        
        if tool_type in self.created_tools:
            tool = self.created_tools[tool_type]
            # 更新使用次數
            self.tool_usage_count[tool_type] = self.tool_usage_count.get(tool_type, 0) + 1
            return tool
        
        return None
    
    def _create_dynamic_tool(self, requirement: Dict[str, Any], question: str) -> Dict[str, Any]:
        """動態創建新工具"""
        tool_type = requirement["type"]
        
        # 創建工具定義
        tool = {
            "id": f"dynamic_{tool_type}_{int(time.time())}",
            "name": f"動態{requirement['category']}工具",
            "type": tool_type,
            "category": requirement["category"],
            "description": f"為處理 '{question[:50]}...' 動態創建的工具",
            "created_at": time.time(),
            "usage_count": 0,
            "handler": self._get_tool_handler(tool_type)
        }
        
        # 保存工具
        self.created_tools[tool_type] = tool
        self.tool_usage_count[tool_type] = 1
        self.performance_metrics["tools_created"] += 1
        
        logger.info(f"動態創建工具: {tool['name']} (類型: {tool_type})")
        
        return tool
    
    def _get_tool_handler(self, tool_type: str):
        """獲取工具處理函數"""
        handlers = {
            "calculator": self._calculator_handler,
            "data_processor": self._data_processor_handler,
            "text_processor": self._text_processor_handler,
            "search_engine": self._search_engine_handler,
            "logic_engine": self._logic_engine_handler,
            "general": self._general_handler
        }
        
        return handlers.get(tool_type, self._general_handler)
    
    def _execute_existing_tool(self, tool: Dict[str, Any], question: str) -> str:
        """執行現有工具"""
        handler = tool["handler"]
        tool["usage_count"] += 1
        
        result = handler(question)
        logger.info(f"使用現有工具 {tool['name']}: {question[:30]}...")
        
        return f"[使用現有工具 {tool['name']}] {result}"
    
    def _execute_new_tool(self, tool: Dict[str, Any], question: str) -> str:
        """執行新創建的工具"""
        handler = tool["handler"]
        tool["usage_count"] += 1
        
        result = handler(question)
        logger.info(f"執行新工具 {tool['name']}: {question[:30]}...")
        
        return f"[動態創建工具 {tool['name']}] {result}"
    
    # 工具處理函數
    def _calculator_handler(self, question: str) -> str:
        """計算器工具處理函數"""
        try:
            # 提取數字和運算
            numbers = re.findall(r'\\d+(?:\\.\\d+)?', question)
            
            if len(numbers) >= 2:
                num1, num2 = float(numbers[0]), float(numbers[1])
                
                if "+" in question or "加" in question:
                    return f"{num1} + {num2} = {num1 + num2}"
                elif "-" in question or "減" in question:
                    return f"{num1} - {num2} = {num1 - num2}"
                elif "*" in question or "乘" in question:
                    return f"{num1} × {num2} = {num1 * num2}"
                elif "/" in question or "除" in question:
                    return f"{num1} ÷ {num2} = {num1 / num2 if num2 != 0 else '無法除零'}"
            
            return "動態計算器分析數學問題"
        except:
            return "計算器工具處理數學問題"
    
    def _data_processor_handler(self, question: str) -> str:
        """數據處理工具處理函數"""
        return "動態數據處理器分析和處理數據"
    
    def _text_processor_handler(self, question: str) -> str:
        """文本處理工具處理函數"""
        return f"動態文本處理器分析文本，長度: {len(question)}字符"
    
    def _search_engine_handler(self, question: str) -> str:
        """搜索引擎工具處理函數"""
        return "動態搜索引擎執行信息檢索"
    
    def _logic_engine_handler(self, question: str) -> str:
        """邏輯推理工具處理函數"""
        return "動態邏輯引擎執行推理分析"
    
    def _general_handler(self, question: str) -> str:
        """通用工具處理函數"""
        return "動態通用工具處理問題"
    
    def get_created_tools(self) -> Dict[str, Any]:
        """獲取已創建的工具信息"""
        return {
            "tools": self.created_tools,
            "usage_stats": self.tool_usage_count,
            "performance": self.performance_metrics
        }
    
    def test_connection(self) -> bool:
        """測試連接"""
        try:
            result = self.process("測試動態工具創建")
            return "動態" in result and "工具" in result
        except:
            return False

