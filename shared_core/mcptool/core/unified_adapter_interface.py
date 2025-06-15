#!/usr/bin/env python3
"""
PowerAutomation 統一適配器接口 - 兼容性層

解決不同適配器接口不一致的問題
"""

import logging
import inspect
from typing import Any, Dict, Optional, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class UnifiedAdapterInterface(ABC):
    """統一適配器接口"""
    
    @abstractmethod
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """統一的處理接口"""
        pass
    
    @abstractmethod
    def get_adapter_info(self) -> Dict[str, Any]:
        """獲取適配器信息"""
        pass

class AdapterCompatibilityWrapper:
    """適配器兼容性包裝器
    
    將不同類型的適配器包裝成統一接口
    """
    
    def __init__(self, adapter, adapter_name: str = "unknown"):
        self.adapter = adapter
        self.adapter_name = adapter_name
        self.adapter_type = self._detect_adapter_type()
        self.call_method = self._determine_call_method()
        
        logger.info(f"包裝適配器: {adapter_name}, 類型: {self.adapter_type}, 調用方法: {self.call_method}")
    
    def _detect_adapter_type(self) -> str:
        """檢測適配器類型"""
        adapter_class_name = type(self.adapter).__name__.lower()
        
        # 檢查類名模式
        if 'gemini' in adapter_class_name or 'claude' in adapter_class_name:
            return 'ai_model'
        elif 'smart_tool' in adapter_class_name or 'tool_engine' in adapter_class_name:
            return 'tool_engine'
        elif 'memory' in adapter_class_name:
            return 'memory_system'
        elif 'webagent' in adapter_class_name:
            return 'web_agent'
        else:
            return 'general'
    
    def _determine_call_method(self) -> str:
        """確定調用方法"""
        # 按優先級檢查可用方法
        method_priority = [
            'generate',      # AI模型常用
            'process',       # 通用處理方法
            'query',         # 查詢方法
            'execute',       # 執行方法
            'run',          # 運行方法
            '__call__'      # 直接調用
        ]
        
        for method in method_priority:
            if hasattr(self.adapter, method):
                return method
        
        return 'unknown'
    
    def process(self, query: str, **kwargs) -> Dict[str, Any]:
        """統一的處理接口"""
        try:
            # 根據適配器類型和調用方法處理
            if self.call_method == 'unknown':
                return self._handle_unknown_adapter(query, **kwargs)
            
            # 獲取調用方法
            method = getattr(self.adapter, self.call_method)
            
            # 根據適配器類型準備參數
            if self.adapter_type == 'ai_model':
                return self._call_ai_model(method, query, **kwargs)
            elif self.adapter_type == 'tool_engine':
                return self._call_tool_engine(method, query, **kwargs)
            elif self.adapter_type == 'memory_system':
                return self._call_memory_system(method, query, **kwargs)
            elif self.adapter_type == 'web_agent':
                return self._call_web_agent(method, query, **kwargs)
            else:
                return self._call_general_adapter(method, query, **kwargs)
                
        except Exception as e:
            logger.error(f"適配器 {self.adapter_name} 調用失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "adapter_name": self.adapter_name,
                "adapter_type": self.adapter_type,
                "call_method": self.call_method
            }
    
    def _call_ai_model(self, method, query: str, **kwargs) -> Dict[str, Any]:
        """調用AI模型適配器"""
        try:
            # 檢查方法簽名
            sig = inspect.signature(method)
            params = {}
            
            if 'query' in sig.parameters:
                params['query'] = query
            elif 'prompt' in sig.parameters:
                params['prompt'] = query
            elif 'text' in sig.parameters:
                params['text'] = query
            else:
                # 嘗試位置參數
                params = [query]
            
            # 添加其他參數
            for param_name in ['max_tokens', 'temperature', 'model']:
                if param_name in sig.parameters and param_name in kwargs:
                    if isinstance(params, dict):
                        params[param_name] = kwargs[param_name]
            
            # 調用方法
            if isinstance(params, dict):
                result = method(**params)
            else:
                result = method(*params)
            
            # 標準化返回格式
            return self._standardize_ai_response(result)
            
        except Exception as e:
            logger.error(f"AI模型調用失敗: {e}")
            raise
    
    def _call_tool_engine(self, method, query: str, **kwargs) -> Dict[str, Any]:
        """調用工具引擎適配器"""
        try:
            # 工具引擎通常期望字典參數
            if isinstance(query, str):
                params = {"query": query}
            else:
                params = query
            
            # 添加上下文
            if kwargs:
                params.update(kwargs)
            
            result = method(params)
            return self._standardize_tool_response(result)
            
        except Exception as e:
            logger.error(f"工具引擎調用失敗: {e}")
            raise
    
    def _call_memory_system(self, method, query: str, **kwargs) -> Dict[str, Any]:
        """調用記憶系統適配器"""
        try:
            # 記憶系統通常用於查詢
            params = {
                "query": query,
                "operation": kwargs.get("operation", "search")
            }
            
            result = method(params)
            return self._standardize_memory_response(result)
            
        except Exception as e:
            logger.error(f"記憶系統調用失敗: {e}")
            raise
    
    def _call_web_agent(self, method, query: str, **kwargs) -> Dict[str, Any]:
        """調用Web代理適配器"""
        try:
            params = {
                "task": query,
                "action": kwargs.get("action", "search")
            }
            
            result = method(params)
            return self._standardize_web_response(result)
            
        except Exception as e:
            logger.error(f"Web代理調用失敗: {e}")
            raise
    
    def _call_general_adapter(self, method, query: str, **kwargs) -> Dict[str, Any]:
        """調用通用適配器"""
        try:
            # 嘗試多種參數格式
            formats_to_try = [
                lambda: method(query),                    # 直接字符串
                lambda: method({"query": query}),         # 字典格式
                lambda: method(query, **kwargs),          # 字符串+關鍵字參數
                lambda: method({"query": query, **kwargs}) # 完整字典
            ]
            
            last_error = None
            for format_func in formats_to_try:
                try:
                    result = format_func()
                    return self._standardize_general_response(result)
                except Exception as e:
                    last_error = e
                    continue
            
            # 如果所有格式都失敗，拋出最後一個錯誤
            raise last_error
            
        except Exception as e:
            logger.error(f"通用適配器調用失敗: {e}")
            raise
    
    def _handle_unknown_adapter(self, query: str, **kwargs) -> Dict[str, Any]:
        """處理未知類型的適配器"""
        try:
            # 嘗試直接調用
            if callable(self.adapter):
                result = self.adapter(query)
                return self._standardize_general_response(result)
            else:
                raise ValueError(f"適配器 {self.adapter_name} 不可調用")
                
        except Exception as e:
            logger.error(f"未知適配器處理失敗: {e}")
            raise
    
    def _standardize_ai_response(self, result) -> Dict[str, Any]:
        """標準化AI模型響應"""
        if isinstance(result, dict):
            return {
                "success": True,
                "data": result.get("data", result.get("response", result.get("text", str(result)))),
                "confidence": result.get("confidence", 0.8),
                "adapter_type": "ai_model",
                "raw_response": result
            }
        elif isinstance(result, str):
            return {
                "success": True,
                "data": result,
                "confidence": 0.8,
                "adapter_type": "ai_model",
                "raw_response": result
            }
        else:
            return {
                "success": True,
                "data": str(result),
                "confidence": 0.6,
                "adapter_type": "ai_model",
                "raw_response": result
            }
    
    def _standardize_tool_response(self, result) -> Dict[str, Any]:
        """標準化工具引擎響應"""
        if isinstance(result, dict):
            return {
                "success": True,
                "data": result.get("result", result.get("data", str(result))),
                "confidence": 0.7,
                "adapter_type": "tool_engine",
                "raw_response": result
            }
        else:
            return {
                "success": True,
                "data": str(result),
                "confidence": 0.7,
                "adapter_type": "tool_engine",
                "raw_response": result
            }
    
    def _standardize_memory_response(self, result) -> Dict[str, Any]:
        """標準化記憶系統響應"""
        if isinstance(result, dict):
            return {
                "success": True,
                "data": result.get("results", result.get("data", str(result))),
                "confidence": 0.6,
                "adapter_type": "memory_system",
                "raw_response": result
            }
        else:
            return {
                "success": True,
                "data": str(result),
                "confidence": 0.6,
                "adapter_type": "memory_system",
                "raw_response": result
            }
    
    def _standardize_web_response(self, result) -> Dict[str, Any]:
        """標準化Web代理響應"""
        if isinstance(result, dict):
            return {
                "success": True,
                "data": result.get("result", result.get("data", str(result))),
                "confidence": 0.7,
                "adapter_type": "web_agent",
                "raw_response": result
            }
        else:
            return {
                "success": True,
                "data": str(result),
                "confidence": 0.7,
                "adapter_type": "web_agent",
                "raw_response": result
            }
    
    def _standardize_general_response(self, result) -> Dict[str, Any]:
        """標準化通用響應"""
        if isinstance(result, dict):
            return {
                "success": True,
                "data": result.get("data", result.get("result", str(result))),
                "confidence": 0.5,
                "adapter_type": "general",
                "raw_response": result
            }
        else:
            return {
                "success": True,
                "data": str(result),
                "confidence": 0.5,
                "adapter_type": "general",
                "raw_response": result
            }
    
    def get_adapter_info(self) -> Dict[str, Any]:
        """獲取適配器信息"""
        return {
            "adapter_name": self.adapter_name,
            "adapter_type": self.adapter_type,
            "call_method": self.call_method,
            "available_methods": [method for method in dir(self.adapter) if not method.startswith('_')],
            "adapter_class": type(self.adapter).__name__
        }

class UnifiedAdapterRegistry:
    """統一適配器註冊表
    
    提供統一的適配器訪問接口
    """
    
    def __init__(self, original_registry):
        self.original_registry = original_registry
        self.wrapped_adapters = {}
        self._wrap_all_adapters()
    
    def _wrap_all_adapters(self):
        """包裝所有適配器"""
        try:
            # 獲取所有適配器
            if hasattr(self.original_registry, 'list_adapters'):
                adapter_names = self.original_registry.list_adapters()
            elif hasattr(self.original_registry, 'get_adapter_names'):
                adapter_names = self.original_registry.get_adapter_names()
            else:
                # 嘗試從註冊表中獲取
                adapter_names = getattr(self.original_registry, 'adapters', {}).keys()
            
            logger.info(f"開始包裝 {len(adapter_names)} 個適配器")
            
            for adapter_name in adapter_names:
                try:
                    original_adapter = self.original_registry.get_adapter(adapter_name)
                    if original_adapter:
                        wrapped_adapter = AdapterCompatibilityWrapper(original_adapter, adapter_name)
                        self.wrapped_adapters[adapter_name] = wrapped_adapter
                        logger.info(f"✅ 成功包裝適配器: {adapter_name}")
                    else:
                        logger.warning(f"⚠️ 適配器 {adapter_name} 為空")
                except Exception as e:
                    logger.error(f"❌ 包裝適配器 {adapter_name} 失敗: {e}")
            
            logger.info(f"適配器包裝完成: {len(self.wrapped_adapters)}/{len(adapter_names)}")
            
        except Exception as e:
            logger.error(f"包裝適配器過程失敗: {e}")
    
    def get_adapter(self, adapter_name: str) -> Optional[AdapterCompatibilityWrapper]:
        """獲取包裝後的適配器"""
        return self.wrapped_adapters.get(adapter_name)
    
    def list_adapters(self) -> list:
        """列出所有可用適配器"""
        return list(self.wrapped_adapters.keys())
    
    def get_adapter_info(self, adapter_name: str) -> Optional[Dict[str, Any]]:
        """獲取適配器信息"""
        adapter = self.get_adapter(adapter_name)
        if adapter:
            return adapter.get_adapter_info()
        return None
    
    def test_adapter(self, adapter_name: str, test_query: str = "Hello") -> Dict[str, Any]:
        """測試適配器功能"""
        adapter = self.get_adapter(adapter_name)
        if not adapter:
            return {"success": False, "error": f"適配器 {adapter_name} 不存在"}
        
        try:
            result = adapter.process(test_query)
            return {
                "success": True,
                "adapter_name": adapter_name,
                "test_query": test_query,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "adapter_name": adapter_name,
                "test_query": test_query,
                "error": str(e)
            }

# 測試代碼
if __name__ == "__main__":
    import sys
    sys.path.append('/home/ubuntu/Powerauto.ai')
    
    print("🔧 測試統一適配器接口")
    
    try:
        # 導入原始註冊表
        from mcptool.adapters.core.safe_mcp_registry import CompleteMCPRegistry
        original_registry = CompleteMCPRegistry()
        
        # 創建統一註冊表
        unified_registry = UnifiedAdapterRegistry(original_registry)
        
        # 測試幾個關鍵適配器
        test_adapters = ['gemini', 'claude', 'smart_tool_engine', 'webagent']
        
        for adapter_name in test_adapters:
            print(f"\\n測試適配器: {adapter_name}")
            
            # 獲取適配器信息
            info = unified_registry.get_adapter_info(adapter_name)
            if info:
                print(f"  類型: {info['adapter_type']}")
                print(f"  調用方法: {info['call_method']}")
            
            # 測試適配器
            test_result = unified_registry.test_adapter(adapter_name, "What is 2+2?")
            if test_result['success']:
                print(f"  ✅ 測試成功")
                print(f"  響應: {test_result['result'].get('data', 'N/A')}")
            else:
                print(f"  ❌ 測試失敗: {test_result['error']}")
        
        print(f"\\n🎯 統一適配器接口測試完成")
        print(f"可用適配器: {len(unified_registry.list_adapters())}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

