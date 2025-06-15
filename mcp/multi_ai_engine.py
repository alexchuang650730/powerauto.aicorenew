"""
多AI引擎管理器
集成Gemini、Claude、SuperMemory等AI引擎
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
import aiohttp
import json

class MultiAIEngine:
    """多AI引擎管理器"""
    
    def __init__(self):
        """初始化多AI引擎"""
        self.logger = logging.getLogger("MultiAIEngine")
        
        # API配置
        self.api_configs = {
            "gemini": {
                "api_key": "AIzaSyBjQOKRMz0uTGnvDe9CDE5BmAwlY0_rCMw",
                "model": "gemini-2.0-flash",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            },
            "claude": {
                "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
                "model": "claude-3-sonnet-20240229",
                "endpoint": "https://api.anthropic.com/v1/messages"
            },
            "supermemory": {
                "api_key": "sm_ohYKVYxdyurx5qGri5VqCi_iIsxIrnpbPeXAivFKEgGIpqonwNUiHIaqTjKmxZFEzekkmXbkuGZNVykhgqCxogP",
                "endpoint": "https://api.supermemory.ai/v1/chat"
            }
        }
        
        self.session = None
        self.logger.info("多AI引擎管理器初始化完成")
    
    async def start(self):
        """启动AI引擎"""
        self.session = aiohttp.ClientSession()
        self.logger.info("多AI引擎已启动")
    
    async def stop(self):
        """停止AI引擎"""
        if self.session:
            await self.session.close()
        self.logger.info("多AI引擎已停止")
    
    async def analyze_content(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        多AI引擎并行分析内容
        
        Args:
            content: 要分析的内容
            context: 上下文信息
            
        Returns:
            所有AI引擎的分析结果
        """
        self.logger.info(f"开始多AI分析: {content[:50]}...")
        
        # 并行调用所有AI引擎
        tasks = []
        
        # Gemini分析
        tasks.append(self._call_gemini(content, context))
        
        # Claude分析
        tasks.append(self._call_claude(content, context))
        
        # SuperMemory分析
        tasks.append(self._call_supermemory(content, context))
        
        # 等待所有结果
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理结果
        analysis_results = {
            "gemini": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "claude": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "supermemory": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "timestamp": asyncio.get_event_loop().time(),
            "content": content[:100] + "..." if len(content) > 100 else content
        }
        
        self.logger.info("多AI分析完成")
        return analysis_results
    
    async def _call_gemini(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用Gemini API"""
        try:
            config = self.api_configs["gemini"]
            
            # 构建请求
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"请分析以下内容并提供智能建议：\n\n{content}"
                    }]
                }]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            url = f"{config['endpoint']}?key={config['api_key']}"
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 提取文本内容
                    text = ""
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            text = candidate["content"]["parts"][0].get("text", "")
                    
                    return {
                        "success": True,
                        "result": text,
                        "engine": "gemini",
                        "model": config["model"]
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Gemini API错误: {response.status} - {error_text}",
                        "engine": "gemini"
                    }
                    
        except Exception as e:
            self.logger.error(f"Gemini调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "gemini"
            }
    
    async def _call_claude(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用Claude API"""
        try:
            config = self.api_configs["claude"]
            
            # 构建请求
            payload = {
                "model": config["model"],
                "max_tokens": 1000,
                "messages": [{
                    "role": "user",
                    "content": f"请分析以下内容并提供智能建议：\n\n{content}"
                }]
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": config["api_key"],
                "anthropic-version": "2023-06-01"
            }
            
            async with self.session.post(config["endpoint"], json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 提取文本内容
                    text = ""
                    if "content" in result and len(result["content"]) > 0:
                        text = result["content"][0].get("text", "")
                    
                    return {
                        "success": True,
                        "result": text,
                        "engine": "claude",
                        "model": config["model"]
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Claude API错误: {response.status} - {error_text}",
                        "engine": "claude"
                    }
                    
        except Exception as e:
            self.logger.error(f"Claude调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "claude"
            }
    
    async def _call_supermemory(self, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用SuperMemory API"""
        try:
            config = self.api_configs["supermemory"]
            
            # 构建请求
            payload = {
                "message": f"请基于记忆和上下文分析以下内容：\n\n{content}",
                "context": context or {}
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['api_key']}"
            }
            
            async with self.session.post(config["endpoint"], json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    return {
                        "success": True,
                        "result": result.get("response", ""),
                        "engine": "supermemory",
                        "memory_context": result.get("memory_context", {})
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"SuperMemory API错误: {response.status} - {error_text}",
                        "engine": "supermemory"
                    }
                    
        except Exception as e:
            self.logger.error(f"SuperMemory调用失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "supermemory"
            }
    
    async def compare_results(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        对比分析所有AI引擎的结果
        这里可以集成用户的智能引擎进行对比
        """
        self.logger.info("开始对比分析AI结果")
        
        # 提取成功的结果
        successful_results = {}
        for engine, result in analysis_results.items():
            if isinstance(result, dict) and result.get("success"):
                successful_results[engine] = result
        
        if not successful_results:
            return {
                "best_result": None,
                "comparison": "所有AI引擎都失败了",
                "confidence": 0.0
            }
        
        # 简单的对比逻辑（这里可以集成用户的智能引擎）
        best_engine = None
        best_score = 0
        comparison_details = {}
        
        for engine, result in successful_results.items():
            # 简单评分逻辑
            score = 0
            text = result.get("result", "")
            
            # 长度评分
            if 50 <= len(text) <= 500:
                score += 30
            
            # 内容质量评分（简单关键词检测）
            quality_keywords = ["建议", "分析", "优化", "改进", "解决", "方案"]
            score += sum(10 for keyword in quality_keywords if keyword in text)
            
            # 特殊引擎加分
            if engine == "supermemory":
                score += 20  # SuperMemory有记忆优势
            elif engine == "claude":
                score += 15  # Claude分析能力强
            elif engine == "gemini":
                score += 10  # Gemini速度快
            
            comparison_details[engine] = {
                "score": score,
                "length": len(text),
                "quality": "高" if score > 60 else "中" if score > 30 else "低"
            }
            
            if score > best_score:
                best_score = score
                best_engine = engine
        
        return {
            "best_result": successful_results.get(best_engine),
            "best_engine": best_engine,
            "comparison": comparison_details,
            "confidence": min(best_score / 100.0, 1.0),
            "all_results": successful_results
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "engines": list(self.api_configs.keys()),
            "session_active": self.session is not None,
            "available": True
        }

