#!/usr/bin/env python3
"""
統一基礎MCP類 - 解決agent適配器載入問題
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseMCP(ABC):
    """MCP適配器基礎類"""
    
    def __init__(self, mcp_id: str, name: str, version: str = "1.0.0"):
        """
        初始化MCP適配器
        
        Args:
            mcp_id: MCP唯一標識符
            name: MCP名稱
            version: 版本號
        """
        self.mcp_id = mcp_id
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"MCP.{self.__class__.__name__}")
        self.logger.info(f"初始化MCP适配器: {self.__class__.__name__}")
        
        # 狀態管理
        self._status = "initialized"
        self._error_message = None
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        獲取適配器能力列表
        
        Returns:
            List[str]: 能力列表
        """
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        處理輸入數據
        
        Args:
            input_data: 輸入數據
            
        Returns:
            Any: 處理結果
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取適配器狀態
        
        Returns:
            Dict[str, Any]: 狀態信息
        """
        return {
            "mcp_id": self.mcp_id,
            "name": self.name,
            "version": self.version,
            "status": self._status,
            "error_message": self._error_message,
            "capabilities": self.get_capabilities()
        }
    
    def set_status(self, status: str, error_message: Optional[str] = None):
        """
        設置適配器狀態
        
        Args:
            status: 狀態
            error_message: 錯誤信息
        """
        self._status = status
        self._error_message = error_message
        
    def get_info(self) -> Dict[str, Any]:
        """
        獲取適配器信息
        
        Returns:
            Dict[str, Any]: 適配器信息
        """
        return {
            "mcp_id": self.mcp_id,
            "name": self.name,
            "version": self.version,
            "class_name": self.__class__.__name__,
            "module": self.__class__.__module__,
            "capabilities": self.get_capabilities(),
            "status": self.get_status()
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """
        驗證輸入數據
        
        Args:
            input_data: 輸入數據
            
        Returns:
            bool: 驗證是否通過
        """
        return input_data is not None
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        處理錯誤
        
        Args:
            error: 異常對象
            
        Returns:
            Dict[str, Any]: 錯誤信息
        """
        error_info = {
            "error": True,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "mcp_id": self.mcp_id
        }
        
        self.logger.error(f"MCP處理錯誤: {error_info}")
        self.set_status("error", str(error))
        
        return error_info

class AgentOptimizationMCP(BaseMCP):
    """智能體優化MCP基礎類"""
    
    def __init__(self, mcp_id: str, name: str, optimization_type: str = "general"):
        super().__init__(mcp_id, name)
        self.optimization_type = optimization_type
        self.metrics = {}
        
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """
        獲取優化指標
        
        Returns:
            Dict[str, Any]: 優化指標
        """
        return self.metrics
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """
        更新優化指標
        
        Args:
            metrics: 新的指標數據
        """
        self.metrics.update(metrics)
        
    def optimize(self, data: Any, target: str = "performance") -> Any:
        """
        執行優化
        
        Args:
            data: 待優化數據
            target: 優化目標
            
        Returns:
            Any: 優化結果
        """
        try:
            result = self.process(data)
            self.set_status("optimized")
            return result
        except Exception as e:
            return self.handle_error(e)

if __name__ == "__main__":
    # 測試基礎類
    class TestMCP(BaseMCP):
        def get_capabilities(self):
            return ["test"]
        
        def process(self, input_data):
            return {"result": "test"}
    
    test_mcp = TestMCP("test", "Test MCP")
    print(f"測試MCP: {test_mcp.get_info()}")

