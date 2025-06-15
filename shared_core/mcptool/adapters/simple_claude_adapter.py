#!/usr/bin/env python3
"""
簡化的Claude適配器
專門用於GAIA測試，避免抽象方法問題
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union

try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

class SimpleClaudeAdapter:
    """簡化的Claude適配器，專門用於GAIA測試"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化Claude適配器"""
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        self.client = None
        self.model_name = "claude-3-5-sonnet-20241022"
        
        if not self.api_key:
            logger.warning("No API key provided for Claude adapter")
            return
        
        try:
            if anthropic:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Claude適配器初始化成功")
            else:
                logger.error("anthropic 模塊未安裝")
        except Exception as e:
            logger.error(f"Claude適配器初始化失敗: {e}")
    
    def process(self, question: str) -> str:
        """處理問題並返回答案"""
        if not self.client:
            return "Claude適配器未正確初始化"
        
        try:
            # 構建提示
            prompt = f"""請回答以下問題，要求：
1. 直接回答問題，不要添加額外解釋
2. 如果是數字答案，只返回數字
3. 如果是文字答案，保持簡潔

問題: {question}"""
            
            # 調用Claude API
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            if response and response.content:
                answer = response.content[0].text.strip()
                logger.info(f"Claude處理成功: {question[:50]}... -> {answer[:50]}...")
                return answer
            else:
                return "Claude未返回有效回應"
                
        except Exception as e:
            logger.error(f"Claude處理失敗: {e}")
            return f"處理錯誤: {str(e)}"
    
    def test_connection(self) -> bool:
        """測試連接"""
        try:
            result = self.process("3+3=?")
            return "6" in result
        except:
            return False

