#!/usr/bin/env python3
"""
統一MCP管理器
整合核心載入器和適配器註冊表，提供統一的MCP管理接口
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from mcptool.core.mcp_core_loader import MCPCoreLoader, MCPInfo, MCPStatus
from mcptool.adapters.core.unified_adapter_registry import get_global_registry

logger = logging.getLogger(__name__)

class UnifiedMCPManager:
    """統一MCP管理器"""
    
    def __init__(self):
        """初始化統一MCP管理器"""
        self.core_loader = MCPCoreLoader()
        self.adapter_registry = get_global_registry()
        self.initialized = False
        
        logger.info("統一MCP管理器初始化")
    
    def initialize(self) -> bool:
        """初始化MCP系統"""
        try:
            # 使用核心載入器發現MCP
            mcps = self.core_loader.discover_mcps()
            logger.info(f"發現 {len(mcps)} 個MCP適配器")
            
            # 載入所有MCP
            load_results = self.core_loader.load_all_mcps()
            
            # 同步到適配器註冊表
            self._sync_to_registry()
            
            self.initialized = True
            success_count = sum(load_results.values())
            total_count = len(load_results)
            
            logger.info(f"MCP系統初始化完成: {success_count}/{total_count}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"MCP系統初始化失敗: {e}")
            return False
    
    def _sync_to_registry(self):
        """同步載入的MCP到適配器註冊表"""
        loaded_mcps = self.core_loader.get_loaded_mcps()
        
        for name, mcp_info in loaded_mcps.items():
            if mcp_info.instance:
                # 註冊到適配器註冊表
                self.adapter_registry.register_adapter(
                    adapter_id=name,
                    adapter_instance=mcp_info.instance,
                    category="mcp_loaded",
                    description=mcp_info.description
                )
    
    def get_mcp_instance(self, mcp_name: str) -> Optional[Any]:
        """獲取MCP實例"""
        return self.core_loader.get_mcp_instance(mcp_name)
    
    def list_mcps(self) -> Dict[str, Dict[str, Any]]:
        """列出所有MCP"""
        return self.core_loader.get_mcp_status()
    
    def reload_mcp(self, mcp_name: str) -> bool:
        """重新載入MCP"""
        success = self.core_loader.reload_mcp(mcp_name)
        if success:
            self._sync_to_registry()
        return success
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        mcp_status = self.core_loader.get_mcp_status()
        registry_status = self.adapter_registry.get_registry_info()
        
        loaded_count = sum(1 for info in mcp_status.values() 
                          if info["status"] == "loaded")
        error_count = sum(1 for info in mcp_status.values() 
                         if info["status"] == "error")
        
        return {
            "initialized": self.initialized,
            "total_mcps": len(mcp_status),
            "loaded_mcps": loaded_count,
            "error_mcps": error_count,
            "registry_adapters": registry_status["total_adapters"],
            "registry_categories": len(registry_status["categories"]),
            "mcp_details": mcp_status,
            "registry_details": registry_status
        }
    
    def execute_mcp(self, mcp_name: str, method: str, *args, **kwargs) -> Any:
        """執行MCP方法"""
        instance = self.get_mcp_instance(mcp_name)
        if not instance:
            raise ValueError(f"MCP未載入: {mcp_name}")
        
        if not hasattr(instance, method):
            raise ValueError(f"MCP {mcp_name} 沒有方法: {method}")
        
        return getattr(instance, method)(*args, **kwargs)
    
    def get_mcp_capabilities(self, mcp_name: str) -> List[str]:
        """獲取MCP能力列表"""
        instance = self.get_mcp_instance(mcp_name)
        if not instance:
            return []
        
        # 獲取所有公共方法
        capabilities = []
        for attr_name in dir(instance):
            if not attr_name.startswith('_'):
                attr = getattr(instance, attr_name)
                if callable(attr):
                    capabilities.append(attr_name)
        
        return capabilities

# 全局管理器實例
_global_manager = None

def get_global_manager() -> UnifiedMCPManager:
    """獲取全局MCP管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = UnifiedMCPManager()
    return _global_manager

def initialize_unified_mcp_system() -> bool:
    """初始化統一MCP系統"""
    manager = get_global_manager()
    return manager.initialize()

if __name__ == "__main__":
    # 測試統一管理器
    manager = UnifiedMCPManager()
    
    print("🔄 初始化MCP系統...")
    success = manager.initialize()
    
    if success:
        print("✅ MCP系統初始化成功")
        
        # 顯示系統狀態
        status = manager.get_system_status()
        print(f"\n📊 系統狀態:")
        print(f"  總MCP數: {status['total_mcps']}")
        print(f"  已載入: {status['loaded_mcps']}")
        print(f"  錯誤: {status['error_mcps']}")
        print(f"  註冊表適配器: {status['registry_adapters']}")
        
        # 列出所有MCP
        mcps = manager.list_mcps()
        print(f"\n📋 MCP列表:")
        for name, info in mcps.items():
            status_icon = "✅" if info["status"] == "loaded" else "❌"
            print(f"  {status_icon} {name}: {info['description']}")
    else:
        print("❌ MCP系統初始化失敗")

