#!/usr/bin/env python3
"""
統一適配器註冊表 - 標準化格式和接口
提供統一的適配器發現、註冊和管理機制

主要功能：
- 統一的適配器註冊格式
- 標準化的適配器接口
- 自動適配器發現
- 類型安全的適配器管理
"""

import logging
import sys
import os
from typing import Dict, Any, Optional, List, Tuple, Union, Protocol
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
import importlib
import inspect

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class AdapterInfo:
    """標準化適配器信息"""
    name: str
    instance: Any
    adapter_type: str
    version: str
    description: str
    capabilities: List[str]
    status: str
    metadata: Dict[str, Any]

class AdapterProtocol(Protocol):
    """適配器協議定義"""
    
    def get_name(self) -> str:
        """獲取適配器名稱"""
        ...
    
    def get_capabilities(self) -> List[str]:
        """獲取適配器能力"""
        ...
    
    def process(self, data: Any) -> Any:
        """處理數據"""
        ...

class BaseAdapter(ABC):
    """基礎適配器抽象類"""
    
    @abstractmethod
    def get_name(self) -> str:
        """獲取適配器名稱"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """獲取適配器能力"""
        pass
    
    def get_version(self) -> str:
        """獲取適配器版本"""
        return "1.0.0"
    
    def get_description(self) -> str:
        """獲取適配器描述"""
        return f"MCP適配器: {self.get_name()}"
    
    def get_metadata(self) -> Dict[str, Any]:
        """獲取適配器元數據"""
        return {}
    
    def process(self, data: Any) -> Any:
        """處理數據 - 默認實現"""
        return {"status": "processed", "data": data}

class UnifiedMCPRegistry:
    """統一MCP註冊表"""
    
    def __init__(self):
        self._adapters: Dict[str, AdapterInfo] = {}
        self._adapter_instances: Dict[str, Any] = {}
        self._initialization_errors: Dict[str, str] = {}
        
        # 自動初始化
        self._auto_discover_adapters()
    
    def _auto_discover_adapters(self):
        """自動發現和註冊適配器"""
        logger.info("開始自動發現適配器...")
        
        # 基礎適配器
        self._register_basic_adapters()
        
        # 從現有註冊表導入
        self._import_from_existing_registry()
        
        # 掃描適配器目錄
        self._scan_adapter_directories()
        
        logger.info(f"適配器發現完成，註冊了 {len(self._adapters)} 個適配器")
    
    def _register_basic_adapters(self):
        """註冊基礎適配器"""
        basic_adapters = [
            ("simple_gemini", "mcptool.adapters.simple_gemini_adapter", "SimpleGeminiAdapter"),
            ("simple_claude", "mcptool.adapters.simple_claude_adapter", "SimpleClaudeAdapter"),
            ("simple_smart_tool", "mcptool.adapters.simple_smart_tool_engine", "SimpleSmartToolEngine"),
            ("simple_webagent", "mcptool.adapters.simple_webagent", "SimpleWebAgent"),
            ("simple_sequential_thinking", "mcptool.adapters.simple_sequential_thinking", "SimpleSequentialThinking"),
            ("simple_kilocode", "mcptool.adapters.simple_kilocode_adapter", "SimpleKiloCodeAdapter"),
        ]
        
        for name, module_path, class_name in basic_adapters:
            self._safe_import_adapter(name, module_path, class_name)
    
    def _import_from_existing_registry(self):
        """從現有註冊表導入適配器"""
        try:
            from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
            existing_registry = SafeMCPRegistry()
            
            # 獲取現有適配器
            existing_adapters = existing_registry.list_adapters()
            
            if isinstance(existing_adapters, list):
                for item in existing_adapters:
                    if isinstance(item, tuple) and len(item) >= 2:
                        name, instance = item[0], item[1]
                        self._register_adapter_instance(name, instance)
                    elif hasattr(item, 'name'):
                        self._register_adapter_instance(item.name, item)
            elif isinstance(existing_adapters, dict):
                for name, adapter_data in existing_adapters.items():
                    if isinstance(adapter_data, dict) and 'instance' in adapter_data:
                        self._register_adapter_instance(name, adapter_data['instance'])
                    else:
                        self._register_adapter_instance(name, adapter_data)
                        
        except Exception as e:
            logger.warning(f"無法從現有註冊表導入適配器: {e}")
    
    def _scan_adapter_directories(self):
        """掃描適配器目錄"""
        adapter_dirs = [
            "mcptool/adapters",
            "mcptool/adapters/core",
            "mcptool/adapters/unified_smart_tool_engine",
            "mcptool/adapters/infinite_context_adapter"
        ]
        
        for adapter_dir in adapter_dirs:
            self._scan_directory(adapter_dir)
    
    def _scan_directory(self, directory: str):
        """掃描指定目錄中的適配器"""
        try:
            dir_path = project_root / directory
            if not dir_path.exists():
                return
            
            for file_path in dir_path.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                
                module_name = file_path.stem
                module_path = f"{directory.replace('/', '.')}.{module_name}"
                
                self._try_import_module(module_name, module_path)
                
        except Exception as e:
            logger.warning(f"掃描目錄 {directory} 時出錯: {e}")
    
    def _try_import_module(self, name: str, module_path: str):
        """嘗試導入模組並發現適配器"""
        try:
            module = importlib.import_module(module_path)
            
            # 查找適配器類
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (inspect.isclass(attr) and 
                    attr_name not in ['BaseAdapter', 'ABC', 'Protocol'] and
                    (hasattr(attr, 'get_name') or hasattr(attr, 'process'))):
                    
                    try:
                        instance = attr()
                        adapter_name = f"{name}_{attr_name.lower()}"
                        self._register_adapter_instance(adapter_name, instance)
                    except Exception as e:
                        logger.warning(f"無法實例化 {attr_name}: {e}")
                        
        except Exception as e:
            logger.debug(f"無法導入模組 {module_path}: {e}")
    
    def _safe_import_adapter(self, name: str, module_path: str, class_name: str):
        """安全導入適配器"""
        try:
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)
            instance = adapter_class()
            self._register_adapter_instance(name, instance)
            
        except Exception as e:
            self._initialization_errors[name] = str(e)
            logger.warning(f"無法導入適配器 {name}: {e}")
    
    def _register_adapter_instance(self, name: str, instance: Any):
        """註冊適配器實例"""
        try:
            # 標準化適配器信息
            adapter_info = self._create_adapter_info(name, instance)
            
            # 註冊到字典
            self._adapters[name] = adapter_info
            self._adapter_instances[name] = instance
            
            logger.debug(f"成功註冊適配器: {name}")
            
        except Exception as e:
            self._initialization_errors[name] = str(e)
            logger.warning(f"註冊適配器 {name} 時出錯: {e}")
    
    def _create_adapter_info(self, name: str, instance: Any) -> AdapterInfo:
        """創建標準化適配器信息"""
        # 獲取適配器名稱
        adapter_name = name
        if hasattr(instance, 'get_name'):
            try:
                adapter_name = instance.get_name()
            except:
                pass
        elif hasattr(instance, 'name'):
            adapter_name = instance.name
        
        # 獲取適配器能力
        capabilities = []
        if hasattr(instance, 'get_capabilities'):
            try:
                caps = instance.get_capabilities()
                if isinstance(caps, list):
                    capabilities = caps
                elif isinstance(caps, dict):
                    capabilities = list(caps.keys())
            except:
                pass
        
        # 獲取適配器類型
        adapter_type = "unknown"
        if hasattr(instance, '__class__'):
            adapter_type = instance.__class__.__name__
        
        # 獲取版本
        version = "1.0.0"
        if hasattr(instance, 'get_version'):
            try:
                version = instance.get_version()
            except:
                pass
        
        # 獲取描述
        description = f"MCP適配器: {adapter_name}"
        if hasattr(instance, 'get_description'):
            try:
                description = instance.get_description()
            except:
                pass
        elif hasattr(instance, '__doc__') and instance.__doc__:
            description = instance.__doc__.strip()
        
        # 獲取元數據
        metadata = {}
        if hasattr(instance, 'get_metadata'):
            try:
                metadata = instance.get_metadata()
            except:
                pass
        
        # 確定狀態
        status = "active"
        if name in self._initialization_errors:
            status = "error"
        
        return AdapterInfo(
            name=adapter_name,
            instance=instance,
            adapter_type=adapter_type,
            version=version,
            description=description,
            capabilities=capabilities,
            status=status,
            metadata=metadata
        )
    
    def register_adapter(self, name: str, instance: Any) -> bool:
        """手動註冊適配器"""
        try:
            self._register_adapter_instance(name, instance)
            return True
        except Exception as e:
            logger.error(f"註冊適配器 {name} 失敗: {e}")
            return False
    
    def get_adapter(self, name: str) -> Optional[Any]:
        """獲取適配器實例"""
        return self._adapter_instances.get(name)
    
    def get_adapter_info(self, name: str) -> Optional[AdapterInfo]:
        """獲取適配器信息"""
        return self._adapters.get(name)
    
    def list_adapters(self) -> List[Tuple[str, Any]]:
        """列出所有適配器 - 統一格式"""
        return [(info.name, info.instance) for info in self._adapters.values()]
    
    def list_adapter_infos(self) -> List[AdapterInfo]:
        """列出所有適配器信息"""
        return list(self._adapters.values())
    
    def get_adapters_dict(self) -> Dict[str, AdapterInfo]:
        """獲取適配器字典"""
        return self._adapters.copy()
    
    def get_adapter_names(self) -> List[str]:
        """獲取所有適配器名稱"""
        return list(self._adapters.keys())
    
    def get_adapters_by_type(self, adapter_type: str) -> List[AdapterInfo]:
        """按類型獲取適配器"""
        return [info for info in self._adapters.values() if info.adapter_type == adapter_type]
    
    def get_adapters_by_capability(self, capability: str) -> List[AdapterInfo]:
        """按能力獲取適配器"""
        return [info for info in self._adapters.values() if capability in info.capabilities]
    
    def get_active_adapters(self) -> List[AdapterInfo]:
        """獲取活躍的適配器"""
        return [info for info in self._adapters.values() if info.status == "active"]
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """獲取註冊表統計信息"""
        total_adapters = len(self._adapters)
        active_adapters = len(self.get_active_adapters())
        error_adapters = len([info for info in self._adapters.values() if info.status == "error"])
        
        adapter_types = {}
        for info in self._adapters.values():
            adapter_types[info.adapter_type] = adapter_types.get(info.adapter_type, 0) + 1
        
        return {
            "total_adapters": total_adapters,
            "active_adapters": active_adapters,
            "error_adapters": error_adapters,
            "adapter_types": adapter_types,
            "initialization_errors": self._initialization_errors.copy()
        }
    
    def validate_adapter(self, name: str) -> Dict[str, Any]:
        """驗證適配器"""
        adapter_info = self.get_adapter_info(name)
        if not adapter_info:
            return {"valid": False, "error": "適配器不存在"}
        
        instance = adapter_info.instance
        validation_result = {
            "valid": True,
            "name": adapter_info.name,
            "type": adapter_info.adapter_type,
            "capabilities": adapter_info.capabilities,
            "checks": {}
        }
        
        # 檢查基本方法
        required_methods = ["get_name", "get_capabilities"]
        for method in required_methods:
            validation_result["checks"][method] = hasattr(instance, method)
        
        # 檢查處理方法
        validation_result["checks"]["process"] = hasattr(instance, "process")
        
        # 檢查是否有錯誤
        if name in self._initialization_errors:
            validation_result["valid"] = False
            validation_result["error"] = self._initialization_errors[name]
        
        return validation_result
    
    def test_adapter(self, name: str, test_data: Any = None) -> Dict[str, Any]:
        """測試適配器"""
        adapter_info = self.get_adapter_info(name)
        if not adapter_info:
            return {"success": False, "error": "適配器不存在"}
        
        instance = adapter_info.instance
        
        try:
            # 測試基本方法
            test_result = {
                "success": True,
                "name": adapter_info.name,
                "tests": {}
            }
            
            # 測試get_name
            if hasattr(instance, "get_name"):
                try:
                    name_result = instance.get_name()
                    test_result["tests"]["get_name"] = {"success": True, "result": name_result}
                except Exception as e:
                    test_result["tests"]["get_name"] = {"success": False, "error": str(e)}
            
            # 測試get_capabilities
            if hasattr(instance, "get_capabilities"):
                try:
                    caps_result = instance.get_capabilities()
                    test_result["tests"]["get_capabilities"] = {"success": True, "result": caps_result}
                except Exception as e:
                    test_result["tests"]["get_capabilities"] = {"success": False, "error": str(e)}
            
            # 測試process方法
            if hasattr(instance, "process"):
                try:
                    if test_data is None:
                        test_data = {"test": "data"}
                    process_result = instance.process(test_data)
                    test_result["tests"]["process"] = {"success": True, "result": process_result}
                except Exception as e:
                    test_result["tests"]["process"] = {"success": False, "error": str(e)}
            
            return test_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# 全局註冊表實例
_global_registry = None

def get_unified_registry() -> UnifiedMCPRegistry:
    """獲取全局統一註冊表"""
    global _global_registry
    if _global_registry is None:
        _global_registry = UnifiedMCPRegistry()
    return _global_registry

# 向後兼容的別名
SafeMCPRegistry = UnifiedMCPRegistry

if __name__ == "__main__":
    # 測試註冊表
    registry = UnifiedMCPRegistry()
    
    print(f"註冊表統計: {registry.get_registry_stats()}")
    print(f"適配器列表: {[info.name for info in registry.list_adapter_infos()]}")
    
    # 測試第一個適配器
    adapters = registry.list_adapter_infos()
    if adapters:
        first_adapter = adapters[0]
        print(f"測試適配器: {first_adapter.name}")
        test_result = registry.test_adapter(first_adapter.name)
        print(f"測試結果: {test_result}")

