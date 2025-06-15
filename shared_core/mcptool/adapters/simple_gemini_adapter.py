#!/usr/bin/env python3
"""
簡化的Gemini適配器
專門用於GAIA測試，避免抽象方法問題
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class SimpleGeminiAdapter:
    """簡化的Gemini適配器，專門用於GAIA測試"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化Gemini適配器"""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = None
        self.model_name = "gemini-2.0-flash-exp"
        
        if not self.api_key:
            logger.warning("No API key provided for Gemini adapter")
            return
        
        try:
            if genai:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info("Gemini適配器初始化成功")
            else:
                logger.error("google-generativeai 模塊未安裝")
        except Exception as e:
            logger.error(f"Gemini適配器初始化失敗: {e}")
    
    def process(self, question: str) -> str:
        """處理問題並返回答案"""
        if not self.model:
            return "Gemini適配器未正確初始化"
        
        try:
            # 構建提示
            prompt = f"""請回答以下問題，要求：
1. 直接回答問題，不要添加額外解釋
2. 如果是數字答案，只返回數字
3. 如果是文字答案，保持簡潔

問題: {question}

答案:"""
            
            # 調用Gemini API
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                answer = response.text.strip()
                logger.info(f"Gemini處理成功: {question[:50]}... -> {answer[:50]}...")
                return answer
            else:
                return "Gemini未返回有效回應"
                
        except Exception as e:
            logger.error(f"Gemini處理失敗: {e}")
            return f"處理錯誤: {str(e)}"
    
    def test_connection(self) -> bool:
        """測試連接"""
        try:
            result = self.process("2+2=?")
            return "4" in result
        except:
            return False

