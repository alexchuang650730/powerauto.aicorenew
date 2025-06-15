"""
Qwen3 8B 本地模型 MCP 適配器
支持跨平台部署 (Windows WSL, macOS, Linux)
"""

import os
import sys
import json
import asyncio
import logging
import platform
import subprocess
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import requests
import time

logger = logging.getLogger(__name__)

class Qwen3LocalModelMCP:
    """Qwen3 8B 本地模型 MCP 適配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_name = "qwen2.5:8b"  # Ollama模型名稱
        self.base_url = self.config.get('base_url', 'http://localhost:11434')
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        
        # 平台檢測
        self.platform = platform.system().lower()
        self.is_wsl = self._detect_wsl()
        
        # 模型狀態
        self.model_loaded = False
        self.ollama_running = False
        
        logger.info(f"Qwen3 8B MCP適配器初始化 - 平台: {self.platform}, WSL: {self.is_wsl}")
    
    def _detect_wsl(self) -> bool:
        """檢測是否在WSL環境中運行"""
        try:
            if self.platform == "linux":
                with open('/proc/version', 'r') as f:
                    return 'microsoft' in f.read().lower()
        except:
            pass
        return False
    
    async def initialize(self) -> bool:
        """初始化本地模型環境"""
        try:
            # 1. 檢查Ollama是否安裝
            if not await self._check_ollama_installed():
                logger.info("Ollama未安裝，開始安裝...")
                if not await self._install_ollama():
                    return False
            
            # 2. 啟動Ollama服務
            if not await self._start_ollama_service():
                return False
            
            # 3. 下載並加載Qwen3模型
            if not await self._ensure_model_available():
                return False
            
            self.model_loaded = True
            logger.info("Qwen3 8B模型初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"Qwen3模型初始化失敗: {e}")
            return False
    
    async def _check_ollama_installed(self) -> bool:
        """檢查Ollama是否已安裝"""
        try:
            result = subprocess.run(['ollama', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    async def _install_ollama(self) -> bool:
        """跨平台安裝Ollama"""
        try:
            if self.platform == "darwin":  # macOS
                logger.info("在macOS上安裝Ollama...")
                result = subprocess.run([
                    'curl', '-fsSL', 'https://ollama.ai/install.sh'
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.run(['sh'], input=result.stdout, text=True)
                    
            elif self.platform == "linux" or self.is_wsl:  # Linux/WSL
                logger.info("在Linux/WSL上安裝Ollama...")
                result = subprocess.run([
                    'curl', '-fsSL', 'https://ollama.ai/install.sh'
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.run(['sh'], input=result.stdout, text=True)
                    
            elif self.platform == "windows":  # Windows
                logger.info("請手動從 https://ollama.ai 下載Windows版本")
                return False
            
            # 驗證安裝
            await asyncio.sleep(5)  # 等待安裝完成
            return await self._check_ollama_installed()
            
        except Exception as e:
            logger.error(f"Ollama安裝失敗: {e}")
            return False
    
    async def _start_ollama_service(self) -> bool:
        """啟動Ollama服務"""
        try:
            # 檢查服務是否已運行
            if await self._check_ollama_running():
                self.ollama_running = True
                return True
            
            # 啟動服務
            logger.info("啟動Ollama服務...")
            if self.platform == "windows":
                subprocess.Popen(['ollama', 'serve'], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(['ollama', 'serve'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # 等待服務啟動
            for _ in range(30):  # 最多等待30秒
                await asyncio.sleep(1)
                if await self._check_ollama_running():
                    self.ollama_running = True
                    logger.info("Ollama服務啟動成功")
                    return True
            
            logger.error("Ollama服務啟動超時")
            return False
            
        except Exception as e:
            logger.error(f"Ollama服務啟動失敗: {e}")
            return False
    
    async def _check_ollama_running(self) -> bool:
        """檢查Ollama服務是否運行"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def _ensure_model_available(self) -> bool:
        """確保Qwen3模型可用"""
        try:
            # 檢查模型是否已下載
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if self.model_name in model.get('name', ''):
                        logger.info(f"模型 {self.model_name} 已存在")
                        return True
            
            # 下載模型
            logger.info(f"下載模型 {self.model_name}...")
            result = subprocess.run([
                'ollama', 'pull', self.model_name
            ], capture_output=True, text=True, timeout=600)  # 10分鐘超時
            
            if result.returncode == 0:
                logger.info(f"模型 {self.model_name} 下載成功")
                return True
            else:
                logger.error(f"模型下載失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"模型準備失敗: {e}")
            return False
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成回應"""
        try:
            if not self.model_loaded:
                await self.initialize()
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get('response', ''),
                    "model": self.model_name,
                    "done": result.get('done', True),
                    "context": result.get('context', [])
                }
            else:
                return {
                    "success": False,
                    "error": f"API請求失敗: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"生成回應失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        try:
            if not self.model_loaded:
                await self.initialize()
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                **kwargs
            }
            
            response = requests.post(
                self.chat_endpoint,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message": result.get('message', {}),
                    "model": self.model_name,
                    "done": result.get('done', True)
                }
            else:
                return {
                    "success": False,
                    "error": f"聊天API請求失敗: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"聊天完成失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """獲取模型信息"""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": self.model_name},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "model_info": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"獲取模型信息失敗: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 檢查Ollama服務
            ollama_status = await self._check_ollama_running()
            
            # 檢查模型狀態
            model_info = await self.get_model_info()
            
            return {
                "success": True,
                "status": {
                    "ollama_running": ollama_status,
                    "model_loaded": self.model_loaded,
                    "model_available": model_info.get("success", False),
                    "platform": self.platform,
                    "is_wsl": self.is_wsl,
                    "base_url": self.base_url,
                    "model_name": self.model_name
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """獲取適配器信息"""
        return {
            "name": "Qwen3 8B Local Model MCP",
            "version": "1.0.0",
            "description": "Qwen3 8B本地模型適配器，支持跨平台部署",
            "supported_platforms": ["Windows WSL", "macOS", "Linux"],
            "model": self.model_name,
            "inference_engine": "Ollama",
            "capabilities": [
                "text_generation",
                "chat_completion", 
                "cross_platform_deployment",
                "local_inference"
            ]
        }

# MCP適配器註冊
def create_adapter(config: Dict[str, Any] = None) -> Qwen3LocalModelMCP:
    """創建Qwen3 8B適配器實例"""
    return Qwen3LocalModelMCP(config)

# 適配器元數據
ADAPTER_METADATA = {
    "name": "qwen3_8b_local_mcp",
    "display_name": "Qwen3 8B Local Model",
    "category": "ai_model",
    "version": "1.0.0",
    "description": "Qwen3 8B本地模型適配器，支持Windows WSL、macOS和Linux",
    "author": "PowerAutomation Team",
    "supported_platforms": ["windows_wsl", "macos", "linux"],
    "dependencies": ["ollama", "requests"],
    "config_schema": {
        "base_url": {
            "type": "string",
            "default": "http://localhost:11434",
            "description": "Ollama服務地址"
        },
        "model_name": {
            "type": "string", 
            "default": "qwen2.5:8b",
            "description": "模型名稱"
        }
    }
}

if __name__ == "__main__":
    # 測試適配器
    async def test_adapter():
        adapter = Qwen3LocalModelMCP()
        
        print("🧪 測試Qwen3 8B適配器...")
        
        # 健康檢查
        health = await adapter.health_check()
        print(f"健康檢查: {health}")
        
        # 初始化
        if await adapter.initialize():
            print("✅ 初始化成功")
            
            # 測試生成
            result = await adapter.generate_response("你好，請介紹一下你自己。")
            print(f"生成測試: {result}")
            
            # 測試聊天
            messages = [{"role": "user", "content": "什麼是人工智能？"}]
            chat_result = await adapter.chat_completion(messages)
            print(f"聊天測試: {chat_result}")
        else:
            print("❌ 初始化失敗")
    
    asyncio.run(test_adapter())

