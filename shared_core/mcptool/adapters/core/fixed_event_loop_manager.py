#!/usr/bin/env python3
"""
修復的事件循環管理器
解決異步事件循環問題
"""

import asyncio
import logging
import threading
from typing import Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class FixedEventLoopManager:
    """修復的事件循環管理器"""
    
    _instance = None
    _lock = threading.Lock()
    _loop = None
    _thread = None
    _executor = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._executor = ThreadPoolExecutor(max_workers=4)
        logger.info("事件循環管理器初始化完成")
    
    def get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """獲取或創建事件循環"""
        try:
            # 嘗試獲取當前線程的事件循環
            loop = asyncio.get_running_loop()
            return loop
        except RuntimeError:
            # 沒有運行中的事件循環，創建新的
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                return loop
            except RuntimeError:
                # 創建新的事件循環
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop
    
    def run_async_function(self, coro_func: Callable, *args, **kwargs) -> Any:
        """在事件循環中運行異步函數"""
        try:
            loop = self.get_or_create_loop()
            
            # 如果循環正在運行，使用線程池執行
            if loop.is_running():
                future = self._executor.submit(self._run_in_new_loop, coro_func, *args, **kwargs)
                return future.result(timeout=30)
            else:
                # 循環未運行，直接運行
                return loop.run_until_complete(coro_func(*args, **kwargs))
                
        except Exception as e:
            logger.error(f"運行異步函數失敗: {e}")
            return None
    
    def _run_in_new_loop(self, coro_func: Callable, *args, **kwargs) -> Any:
        """在新的事件循環中運行協程"""
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro_func(*args, **kwargs))
        finally:
            new_loop.close()
    
    def close(self):
        """關閉事件循環管理器"""
        if self._executor:
            self._executor.shutdown(wait=True)
        logger.info("事件循環管理器已關閉")

# 全局事件循環管理器
_global_loop_manager = None

def get_loop_manager() -> FixedEventLoopManager:
    """獲取全局事件循環管理器"""
    global _global_loop_manager
    if _global_loop_manager is None:
        _global_loop_manager = FixedEventLoopManager()
    return _global_loop_manager

