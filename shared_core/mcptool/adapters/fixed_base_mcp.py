#!/usr/bin/env python3
"""
修復版的基礎MCP適配器
提供所有MCP適配器的統一基類
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseMCP:
    """MCP適配器基類，所有MCP適配器都應繼承此類"""
    
    def __init__(self, name: str = "BaseMCP"):
        """
        初始化基礎MCP適配器
        
        Args:
            name: 適配器名稱
        """
        self.name = name
        self.logger = logging.getLogger(f"MCP.{name}")
        self.logger.info(f"初始化MCP适配器: {name}")
        
        # 性能指標
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_request_time": None,
            "uptime_start": datetime.now().isoformat(),
            "module_version": "1.0.0"
        }
        
        # 狀態管理
        self.is_available = True
        self.last_error = None
    
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        處理輸入數據 - 標準化實現
        
        Args:
            input_data: 輸入數據字典
            context: 上下文信息字典
            
        Returns:
            標準化的處理結果字典
        """
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1
        self.performance_metrics["last_request_time"] = datetime.now().isoformat()
        
        try:
            # 檢查可用性
            if not self.is_available:
                return self._error_response("適配器當前不可用", "ADAPTER_UNAVAILABLE")
            
            # 驗證輸入數據
            if not self.validate_input(input_data):
                return self._error_response("輸入數據驗證失敗", "INVALID_INPUT")
            
            # 調用子類的具體處理邏輯
            result = self._process_implementation(input_data, context)
            
            # 更新性能指標
            response_time = time.time() - start_time
            self._update_success_metrics(response_time)
            
            # 如果結果已經是標準格式，直接返回
            if isinstance(result, dict) and "status" in result:
                return result
            
            # 否則包裝為標準成功響應
            return self._success_response(
                data=result,
                message="處理完成",
                metadata={
                    "response_time": response_time,
                    "module_name": self.name
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self._update_error_metrics(response_time, str(e))
            
            self.logger.error(f"處理失敗: {e}")
            return self._error_response(f"處理失敗: {str(e)}", "PROCESSING_ERROR")
    
    def _process_implementation(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        """
        具體的處理實現 - 子類應該覆蓋此方法
        
        Args:
            input_data: 輸入數據字典
            context: 上下文信息字典
            
        Returns:
            處理結果
        """
        self.logger.warning(f"{self.name}._process_implementation()被調用，這是一個應該被子類覆蓋的方法")
        return {
            "message": f"{self.name}基礎處理完成",
            "input_received": True,
            "context_available": context is not None
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        驗證輸入數據 - 子類可以覆蓋此方法
        
        Args:
            input_data: 輸入數據字典
            
        Returns:
            驗證是否通過
        """
        if not isinstance(input_data, dict):
            return False
        return True
    
    def get_capabilities(self) -> List[str]:
        """
        獲取適配器能力列表 - 子類應該覆蓋此方法
        
        Returns:
            能力列表
        """
        return ["basic_processing"]
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取適配器狀態信息
        
        Returns:
            狀態信息字典
        """
        return {
            "name": self.name,
            "is_available": self.is_available,
            "capabilities": self.get_capabilities(),
            "performance_metrics": self.performance_metrics.copy(),
            "last_error": self.last_error
        }
    
    def test_connection(self) -> bool:
        """
        測試適配器連接 - 子類可以覆蓋此方法
        
        Returns:
            連接是否正常
        """
        try:
            test_result = self.process({"test": True})
            return test_result.get("status") == "success"
        except:
            return False
    
    def _success_response(self, data: Any, message: str = "操作成功", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成標準成功響應"""
        return {
            "status": "success",
            "message": message,
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    
    def _error_response(self, message: str, error_code: str = "GENERAL_ERROR", details: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成標準錯誤響應"""
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_success_metrics(self, response_time: float):
        """更新成功指標"""
        self.performance_metrics["successful_requests"] += 1
        self._update_average_response_time(response_time)
        self.last_error = None
    
    def _update_error_metrics(self, response_time: float, error_message: str):
        """更新錯誤指標"""
        self.performance_metrics["failed_requests"] += 1
        self._update_average_response_time(response_time)
        self.last_error = error_message
    
    def _update_average_response_time(self, response_time: float):
        """更新平均響應時間"""
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        
        # 計算新的平均響應時間
        new_avg = ((current_avg * (total_requests - 1)) + response_time) / total_requests
        self.performance_metrics["average_response_time"] = new_avg
    
    def set_availability(self, available: bool):
        """設置適配器可用性"""
        self.is_available = available
        self.logger.info(f"{self.name} 可用性設置為: {available}")
    
    def reset_metrics(self):
        """重置性能指標"""
        self.performance_metrics.update({
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_request_time": None
        })
        self.logger.info(f"{self.name} 性能指標已重置")


class AbstractMCP(BaseMCP, ABC):
    """抽象MCP基類，用於需要強制實現特定方法的適配器"""
    
    @abstractmethod
    def _process_implementation(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        """抽象處理方法，子類必須實現"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """抽象能力方法，子類必須實現"""
        pass

