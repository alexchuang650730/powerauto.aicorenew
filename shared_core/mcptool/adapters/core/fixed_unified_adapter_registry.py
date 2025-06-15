#!/usr/bin/env python3
"""
修復的MCP適配器註冊表
解決循環依賴和重複初始化問題
"""

import os
import sys
import json
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class FixedUnifiedAdapterRegistry:
    """修復的統一適配器註冊表"""
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        """單例模式，防止重複初始化"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            logger.info("初始化修復的統一適配器註冊表")
            
            # 適配器根目錄
            self.adapters_root = str(Path(__file__).parent.parent)
            self.registered_adapters = {}
            self.adapter_instances = {}
            self.adapter_metadata = {}
            self.initialization_stack = set()  # 防止循環初始化
            
            # 適配器分類
            self.adapter_categories = {
                "core": "核心組件",
                "ai_enhanced": "AI增強功能", 
                "unified_config_manager": "統一配置管理",
                "optimization": "優化相關",
                "workflow": "工作流引擎",
                "development_tools": "開發工具",
                "integration": "多適配器整合",
                "claude_adapter": "Claude適配器",
                "gemini_adapter": "Gemini適配器"
            }
            
            self._initialized = True
            logger.info("修復的統一適配器註冊表初始化完成")
    
    def register_adapter(self, adapter_id: str, adapter_class: Type, category: str = "core", 
                        metadata: Dict[str, Any] = None) -> bool:
        """註冊適配器，防止重複註冊"""
        try:
            # 檢查是否已註冊
            if adapter_id in self.registered_adapters:
                logger.warning(f"適配器 {adapter_id} 已註冊，跳過重複註冊")
                return True
            
            # 檢查是否在初始化堆棧中（防止循環依賴）
            if adapter_id in self.initialization_stack:
                logger.error(f"檢測到循環依賴: {adapter_id}")
                return False
            
            self.initialization_stack.add(adapter_id)
            
            # 註冊適配器
            self.registered_adapters[adapter_id] = {
                "class": adapter_class,
                "category": category,
                "metadata": metadata or {},
                "registered_at": datetime.now().isoformat()
            }
            
            logger.info(f"成功註冊適配器: {adapter_id} (分類: {category})")
            
            # 從初始化堆棧中移除
            self.initialization_stack.discard(adapter_id)
            
            return True
            
        except Exception as e:
            logger.error(f"註冊適配器 {adapter_id} 失敗: {e}")
            self.initialization_stack.discard(adapter_id)
            return False
    
    def get_adapter_instance(self, adapter_id: str, **kwargs) -> Optional[Any]:
        """獲取適配器實例，防止重複實例化"""
        try:
            # 檢查是否已有實例
            if adapter_id in self.adapter_instances:
                return self.adapter_instances[adapter_id]
            
            # 檢查是否已註冊
            if adapter_id not in self.registered_adapters:
                logger.error(f"適配器 {adapter_id} 未註冊")
                return None
            
            # 檢查循環依賴
            if adapter_id in self.initialization_stack:
                logger.error(f"檢測到實例化循環依賴: {adapter_id}")
                return None
            
            self.initialization_stack.add(adapter_id)
            
            # 創建實例
            adapter_class = self.registered_adapters[adapter_id]["class"]
            instance = adapter_class(**kwargs)
            
            # 緩存實例
            self.adapter_instances[adapter_id] = instance
            
            logger.info(f"成功創建適配器實例: {adapter_id}")
            
            # 從初始化堆棧中移除
            self.initialization_stack.discard(adapter_id)
            
            return instance
            
        except Exception as e:
            logger.error(f"創建適配器實例 {adapter_id} 失敗: {e}")
            self.initialization_stack.discard(adapter_id)
            return None
    
    def list_adapters(self, category: str = None) -> List[Dict[str, Any]]:
        """列出適配器"""
        try:
            adapters = []
            
            for adapter_id, adapter_info in self.registered_adapters.items():
                if category and adapter_info["category"] != category:
                    continue
                
                adapters.append({
                    "id": adapter_id,
                    "category": adapter_info["category"],
                    "category_name": self.adapter_categories.get(adapter_info["category"], "未知分類"),
                    "metadata": adapter_info["metadata"],
                    "registered_at": adapter_info["registered_at"],
                    "has_instance": adapter_id in self.adapter_instances
                })
            
            return adapters
            
        except Exception as e:
            logger.error(f"列出適配器失敗: {e}")
            return []
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """獲取分類統計"""
        try:
            categories = {}
            
            for category_id, category_name in self.adapter_categories.items():
                count = sum(1 for info in self.registered_adapters.values() 
                           if info["category"] == category_id)
                
                categories[category_id] = {
                    "name": category_name,
                    "count": count
                }
            
            return categories
            
        except Exception as e:
            logger.error(f"獲取分類統計失敗: {e}")
            return {}
    
    def clear_initialization_stack(self):
        """清理初始化堆棧（用於錯誤恢復）"""
        self.initialization_stack.clear()
        logger.info("已清理初始化堆棧")

# 全局註冊表實例
_global_registry = None

def get_global_registry() -> FixedUnifiedAdapterRegistry:
    """獲取全局註冊表實例"""
    global _global_registry
    if _global_registry is None:
        _global_registry = FixedUnifiedAdapterRegistry()
    return _global_registry

