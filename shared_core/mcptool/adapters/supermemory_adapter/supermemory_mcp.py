"""
SuperMemory API適配器實現

此模塊實現了基於SuperMemory API的適配器，用於將SuperMemory的記憶管理能力集成到PowerAutomation系統中。
適配器遵循接口標準，確保與系統的無縫集成，同時最小化對原有代碼的修改。
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
import requests

# 導入接口定義
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日誌
logging.basicConfig(
    level=os.environ.get("SUPERMEMORY_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("SUPERMEMORY_LOG_FILE", None)
)
logger = logging.getLogger("supermemory_adapter")

class SuperMemoryAdapter(KiloCodeAdapterInterface):
    """
    SuperMemory適配器實現，提供記憶存儲、檢索、搜索等功能。
    
    此適配器通過API調用SuperMemory服務，將其功能集成到PowerAutomation系統中。
    所有方法都嚴格遵循接口標準，確保與系統的兼容性。
    """
    
    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        """
        初始化SuperMemory適配器
        
        Args:
            api_key: SuperMemory API密鑰，如果為None則從環境變量獲取
            server_url: SuperMemory服務器URL，如果為None則從環境變量獲取
        """
        self.api_key = api_key or os.environ.get("SUPERMEMORY_API_KEY")
        self.server_url = server_url or os.environ.get("SUPERMEMORY_SERVER_URL", "https://api.supermemory.ai/v1")
        self.timeout = int(os.environ.get("SUPERMEMORY_TIMEOUT", "30"))
        
        if not self.api_key:
            logger.warning("No API key provided for SuperMemory adapter")
        
        logger.info(f"Initialized SuperMemory adapter with server URL: {self.server_url}")
    
    # 實現KiloCodeAdapterInterface的抽象方法
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化適配器"""
        try:
            if config.get("api_key"):
                self.api_key = config["api_key"]
            if config.get("server_url"):
                self.server_url = config["server_url"]
            if config.get("timeout"):
                self.timeout = int(config["timeout"])
            
            logger.info("SuperMemory適配器初始化成功")
            return True
        except Exception as e:
            logger.error(f"SuperMemory適配器初始化失敗: {e}")
            return False
    
    def get_capabilities(self) -> Dict[str, bool]:
        """獲取適配器支持的能力"""
        return {
            "memory_storage": True,
            "memory_retrieval": True,
            "memory_search": True,
            "memory_management": True,
            "batch_processing": False,
            "task_decomposition": False
        }
    
    def health_check(self) -> Dict[str, Any]:
        """檢查適配器健康狀態"""
        try:
            # 嘗試調用API檢查連接
            response = requests.get(
                f"{self.server_url}/health",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "api_accessible": response.status_code in [200, 401, 403],
                "server_url": self.server_url,
                "has_api_key": bool(self.api_key),
                "response_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "server_url": self.server_url,
                "has_api_key": bool(self.api_key),
                "error": str(e)
            }
    
    def shutdown(self) -> bool:
        """關閉適配器，釋放資源"""
        try:
            logger.info("SuperMemory適配器正在關閉")
            # 清理資源
            self.api_key = None
            return True
        except Exception as e:
            logger.error(f"SuperMemory適配器關閉失敗: {e}")
            return False
    
    def decompose_task(self, task_description: str) -> List[Dict[str, Any]]:
        """分解任務 - SuperMemory不支持任務分解，返回原任務"""
        return [{
            "id": "memory_task",
            "description": task_description,
            "type": "memory_operation",
            "supported": False,
            "reason": "SuperMemory專注於記憶管理，不支持任務分解"
        }]
    
    def batch_generate(self, prompts: List[str], context: Optional[Dict[str, Any]] = None) -> List[str]:
        """批量生成 - SuperMemory不支持代碼生成，返回記憶檢索結果"""
        results = []
        for prompt in prompts:
            try:
                # 將prompt作為搜索查詢
                search_result = self.search_memories(prompt, limit=1)
                if search_result.get("success") and search_result.get("memories"):
                    results.append(search_result["memories"][0].get("content", ""))
                else:
                    results.append(f"未找到與'{prompt}'相關的記憶")
            except Exception as e:
                results.append(f"搜索記憶時出錯: {e}")
        
        return results
        
    def store_memory(self, key: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        存儲記憶
        
        Args:
            key: 記憶鍵
            value: 記憶內容
            metadata: 元數據
            
        Returns:
            包含存儲結果的字典
        """
        try:
            response = self._call_api("store", {
                "key": key,
                "value": value,
                "metadata": metadata or {}
            })
            
            if "error" in response:
                return {
                    "status": "error",
                    "message": response["error"],
                    "stored": False
                }
                
            return {
                "status": "success",
                "stored": True,
                "key": key,
                "timestamp": response.get("timestamp"),
                "id": response.get("id")
            }
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "stored": False
            }
    
    def retrieve_memory(self, key: str) -> Dict[str, Any]:
        """
        檢索記憶
        
        Args:
            key: 記憶鍵
            
        Returns:
            包含檢索結果的字典
        """
        try:
            response = self._call_api("retrieve", {
                "key": key
            })
            
            if "error" in response:
                return {
                    "status": "error",
                    "message": response["error"],
                    "found": False,
                    "value": None
                }
                
            return {
                "status": "success",
                "found": True,
                "key": key,
                "value": response.get("value"),
                "metadata": response.get("metadata", {}),
                "timestamp": response.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "found": False,
                "value": None
            }
    
    def search_memories(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        搜索記憶
        
        Args:
            query: 搜索查詢
            limit: 結果限制
            
        Returns:
            包含搜索結果的字典
        """
        try:
            response = self._call_api("search", {
                "query": query,
                "limit": limit
            })
            
            if "error" in response:
                return {
                    "status": "error",
                    "message": response["error"],
                    "results": []
                }
                
            return {
                "status": "success",
                "query": query,
                "results": response.get("results", []),
                "total": response.get("total", 0)
            }
            
        except Exception as e:
            logger.error(f"Error searching memories: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "results": []
            }
    
    def delete_memory(self, key: str) -> Dict[str, Any]:
        """
        刪除記憶
        
        Args:
            key: 記憶鍵
            
        Returns:
            包含刪除結果的字典
        """
        try:
            response = self._call_api("delete", {
                "key": key
            })
            
            if "error" in response:
                return {
                    "status": "error",
                    "message": response["error"],
                    "deleted": False
                }
                
            return {
                "status": "success",
                "deleted": True,
                "key": key
            }
            
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "deleted": False
            }
    
    def _call_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        調用SuperMemory API
        
        Args:
            endpoint: API端點
            data: 請求數據
            
        Returns:
            API響應
        """
        if not self.api_key:
            return {"error": "No API key available"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.server_url}/{endpoint}",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {"error": f"API returned status code {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            return {"error": str(e)}


class SuperMemoryMCP:
    """
    SuperMemory MCP適配器，將SuperMemory的記憶管理能力集成到MCP系統中。
    
    此適配器實現了MCP協議，提供記憶存儲、檢索、搜索等功能，並支持與其他MCP適配器協同工作。
    """
    
    def __init__(self):
        """初始化SuperMemory MCP適配器"""
        self.name = "SuperMemoryMCP"
        self.version = "1.0.0"
        self.description = "SuperMemory MCP適配器，提供AI記憶管理功能"
        
        # 嘗試使用Claude API密鑰作為備用
        api_key = os.environ.get("SUPERMEMORY_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        self.adapter = SuperMemoryAdapter(api_key=api_key)
        
        self.capabilities = ["memory_storage", "memory_retrieval", "memory_search", "memory_management"]
        
        # 初始化日誌
        self.logger = logging.getLogger("MCP.SuperMemoryMCP")
        self.logger.info("初始化MCP適配器: SuperMemoryMCP")
        
        # 檢查API密鑰
        if not self.adapter.api_key:
            self.logger.warning("未提供SuperMemory API密鑰，部分功能可能不可用")
            self.available = False
        else:
            self.available = True
            
        self.logger.info(f"SuperMemory MCP適配器初始化完成，可用性: {self.available}")
    
    def get_capabilities(self) -> List[str]:
        """
        獲取適配器能力列表
        
        Returns:
            能力列表
        """
        return self.capabilities
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        驗證輸入數據
        
        Args:
            data: 輸入數據
            
        Returns:
            數據是否有效
        """
        if not isinstance(data, dict):
            return False
            
        if "action" not in data:
            return False
            
        if data["action"] not in ["store", "retrieve", "search", "delete"]:
            return False
            
        return True
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理請求
        
        Args:
            data: 請求數據
            
        Returns:
            處理結果
        """
        if not self.available:
            return {
                "status": "error",
                "message": "SuperMemory適配器不可用，請檢查API密鑰",
                "error_code": "ADAPTER_UNAVAILABLE"
            }
            
        if not self.validate_input(data):
            return {
                "status": "error",
                "message": "無效的輸入數據",
                "error_code": "INVALID_INPUT"
            }
            
        try:
            action = data["action"]
            
            if action == "store":
                return self._handle_store(data)
            elif action == "retrieve":
                return self._handle_retrieve(data)
            elif action == "search":
                return self._handle_search(data)
            elif action == "delete":
                return self._handle_delete(data)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {action}",
                    "error_code": "UNSUPPORTED_ACTION"
                }
                
        except Exception as e:
            self.logger.error(f"處理請求時出錯: {str(e)}")
            return {
                "status": "error",
                "message": f"處理請求時出錯: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
    
    def _handle_store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理存儲請求"""
        key = data.get("key", "")
        value = data.get("value", "")
        metadata = data.get("metadata", {})
        
        if not key or not value:
            return {
                "status": "error",
                "message": "缺少必要參數: key 和 value",
                "error_code": "MISSING_PARAMETER"
            }
            
        result = self.adapter.store_memory(key, value, metadata)
        return {
            "status": "success",
            "result": result
        }
    
    def _handle_retrieve(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理檢索請求"""
        key = data.get("key", "")
        
        if not key:
            return {
                "status": "error",
                "message": "缺少必要參數: key",
                "error_code": "MISSING_PARAMETER"
            }
            
        result = self.adapter.retrieve_memory(key)
        return {
            "status": "success",
            "result": result
        }
    
    def _handle_search(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理搜索請求"""
        query = data.get("query", "")
        limit = data.get("limit", 10)
        
        if not query:
            return {
                "status": "error",
                "message": "缺少必要參數: query",
                "error_code": "MISSING_PARAMETER"
            }
            
        result = self.adapter.search_memories(query, limit)
        return {
            "status": "success",
            "result": result
        }
    
    def _handle_delete(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理刪除請求"""
        key = data.get("key", "")
        
        if not key:
            return {
                "status": "error",
                "message": "缺少必要參數: key",
                "error_code": "MISSING_PARAMETER"
            }
            
        result = self.adapter.delete_memory(key)
        return {
            "status": "success",
            "result": result
        }

