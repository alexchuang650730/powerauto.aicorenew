#!/usr/bin/env python3
"""
PowerAutomation 增強錯誤處理系統

提供詳細的調試信息和錯誤恢復機制
"""

import logging
import traceback
import sys
import time
import json
from datetime import datetime
from typing import Any, Dict, Optional, List, Callable
from functools import wraps
from pathlib import Path

class EnhancedLogger:
    """增強日誌記錄器"""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 清除現有處理器
        self.logger.handlers.clear()
        
        # 創建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件處理器
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """調試信息"""
        self._log_with_context(self.logger.debug, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息"""
        self._log_with_context(self.logger.info, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告"""
        self._log_with_context(self.logger.warning, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """錯誤"""
        self._log_with_context(self.logger.error, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """嚴重錯誤"""
        self._log_with_context(self.logger.critical, message, **kwargs)
    
    def _log_with_context(self, log_func: Callable, message: str, **kwargs):
        """帶上下文的日誌記錄"""
        if kwargs:
            context_str = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            message = f"{message} | Context: {context_str}"
        log_func(message)

class ErrorContext:
    """錯誤上下文管理器"""
    
    def __init__(self):
        self.context_stack = []
        self.error_history = []
    
    def push_context(self, context: Dict[str, Any]):
        """推入上下文"""
        self.context_stack.append({
            'timestamp': datetime.now().isoformat(),
            'context': context
        })
    
    def pop_context(self):
        """彈出上下文"""
        if self.context_stack:
            return self.context_stack.pop()
        return None
    
    def get_current_context(self) -> Dict[str, Any]:
        """獲取當前上下文"""
        if self.context_stack:
            return self.context_stack[-1]['context']
        return {}
    
    def record_error(self, error: Exception, additional_info: Dict[str, Any] = None):
        """記錄錯誤"""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context_stack': self.context_stack.copy(),
            'additional_info': additional_info or {}
        }
        self.error_history.append(error_record)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """獲取錯誤摘要"""
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": []}
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": self.error_history[-5:],  # 最近5個錯誤
            "error_types": list(set(e['error_type'] for e in self.error_history)),
            "first_error": self.error_history[0]['timestamp'],
            "last_error": self.error_history[-1]['timestamp']
        }

# 全局錯誤上下文
global_error_context = ErrorContext()

def with_error_handling(
    logger: Optional[EnhancedLogger] = None,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = True,
    default_return: Any = None
):
    """錯誤處理裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 推入上下文
            if context:
                global_error_context.push_context(context)
            
            # 添加函數信息到上下文
            func_context = {
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
            global_error_context.push_context(func_context)
            
            try:
                if logger:
                    logger.debug(f"開始執行函數: {func.__name__}", **func_context)
                
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if logger:
                    logger.debug(f"函數執行成功: {func.__name__}", 
                               execution_time=f"{execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time if 'start_time' in locals() else 0
                
                # 記錄錯誤
                additional_info = {
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'args_types': [type(arg).__name__ for arg in args],
                    'kwargs': {k: type(v).__name__ for k, v in kwargs.items()}
                }
                global_error_context.record_error(e, additional_info)
                
                if logger:
                    logger.error(f"函數執行失敗: {func.__name__}", 
                               error=str(e), 
                               error_type=type(e).__name__,
                               execution_time=f"{execution_time:.3f}s")
                
                if reraise:
                    raise
                else:
                    return default_return
                    
            finally:
                # 彈出上下文
                global_error_context.pop_context()
                if context:
                    global_error_context.pop_context()
        
        return wrapper
    return decorator

class SafeExecutor:
    """安全執行器"""
    
    def __init__(self, logger: Optional[EnhancedLogger] = None):
        self.logger = logger or EnhancedLogger("SafeExecutor")
    
    def safe_call(self, 
                  func: Callable, 
                  *args, 
                  max_retries: int = 3,
                  retry_delay: float = 1.0,
                  fallback_func: Optional[Callable] = None,
                  **kwargs) -> Dict[str, Any]:
        """安全調用函數"""
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.debug(f"嘗試調用函數: {func.__name__}", 
                                attempt=attempt + 1, 
                                max_retries=max_retries + 1)
                
                result = func(*args, **kwargs)
                
                self.logger.info(f"函數調用成功: {func.__name__}", 
                               attempt=attempt + 1)
                
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt + 1,
                    "function": func.__name__
                }
                
            except Exception as e:
                self.logger.warning(f"函數調用失敗: {func.__name__}", 
                                  attempt=attempt + 1,
                                  error=str(e),
                                  error_type=type(e).__name__)
                
                # 記錄錯誤
                global_error_context.record_error(e, {
                    "function": func.__name__,
                    "attempt": attempt + 1,
                    "max_retries": max_retries
                })
                
                # 如果不是最後一次嘗試，等待後重試
                if attempt < max_retries:
                    self.logger.info(f"等待 {retry_delay}s 後重試...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # 指數退避
                else:
                    # 最後一次嘗試失敗，嘗試fallback
                    if fallback_func:
                        try:
                            self.logger.info(f"嘗試fallback函數: {fallback_func.__name__}")
                            fallback_result = fallback_func(*args, **kwargs)
                            
                            return {
                                "success": True,
                                "result": fallback_result,
                                "attempts": attempt + 1,
                                "function": func.__name__,
                                "used_fallback": True,
                                "fallback_function": fallback_func.__name__
                            }
                            
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback函數也失敗: {fallback_func.__name__}",
                                            error=str(fallback_error))
                    
                    # 所有嘗試都失敗
                    return {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "attempts": attempt + 1,
                        "function": func.__name__,
                        "traceback": traceback.format_exc()
                    }
    
    def safe_import(self, module_name: str, fallback_value: Any = None) -> Any:
        """安全導入模塊"""
        try:
            module = __import__(module_name)
            self.logger.debug(f"成功導入模塊: {module_name}")
            return module
        except ImportError as e:
            self.logger.warning(f"導入模塊失敗: {module_name}", error=str(e))
            return fallback_value
    
    def safe_getattr(self, obj: Any, attr_name: str, default_value: Any = None) -> Any:
        """安全獲取屬性"""
        try:
            value = getattr(obj, attr_name)
            self.logger.debug(f"成功獲取屬性: {attr_name}")
            return value
        except AttributeError as e:
            self.logger.warning(f"獲取屬性失敗: {attr_name}", error=str(e))
            return default_value

class DebugHelper:
    """調試助手"""
    
    def __init__(self, logger: Optional[EnhancedLogger] = None):
        self.logger = logger or EnhancedLogger("DebugHelper")
    
    def inspect_object(self, obj: Any, name: str = "object") -> Dict[str, Any]:
        """檢查對象"""
        try:
            inspection = {
                "name": name,
                "type": type(obj).__name__,
                "module": getattr(type(obj), '__module__', 'unknown'),
                "str_representation": str(obj)[:200],  # 限制長度
                "attributes": [],
                "methods": [],
                "callable": callable(obj),
                "has_dict": hasattr(obj, '__dict__'),
                "dict_keys": list(obj.__dict__.keys()) if hasattr(obj, '__dict__') else []
            }
            
            # 獲取屬性和方法
            for attr_name in dir(obj):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(obj, attr_name)
                        if callable(attr_value):
                            inspection["methods"].append(attr_name)
                        else:
                            inspection["attributes"].append(attr_name)
                    except Exception:
                        pass  # 忽略無法訪問的屬性
            
            self.logger.debug(f"對象檢查完成: {name}", 
                            type=inspection["type"],
                            attributes_count=len(inspection["attributes"]),
                            methods_count=len(inspection["methods"]))
            
            return inspection
            
        except Exception as e:
            self.logger.error(f"對象檢查失敗: {name}", error=str(e))
            return {"name": name, "error": str(e)}
    
    def trace_execution(self, func: Callable):
        """執行追蹤裝飾器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.debug(f"=== 開始追蹤: {func.__name__} ===")
            
            # 記錄參數
            self.logger.debug(f"參數: args={len(args)}, kwargs={list(kwargs.keys())}")
            
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"返回值類型: {type(result).__name__}")
                self.logger.debug(f"=== 追蹤結束: {func.__name__} (成功) ===")
                return result
            except Exception as e:
                self.logger.error(f"執行異常: {e}")
                self.logger.debug(f"=== 追蹤結束: {func.__name__} (失敗) ===")
                raise
        
        return wrapper
    
    def create_error_report(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """創建錯誤報告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "error_summary": global_error_context.get_error_summary(),
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "current_working_directory": str(Path.cwd())
            },
            "context_stack": global_error_context.context_stack.copy()
        }
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                self.logger.info(f"錯誤報告已保存: {save_path}")
            except Exception as e:
                self.logger.error(f"保存錯誤報告失敗: {e}")
        
        return report

# 全局實例
enhanced_logger = EnhancedLogger("PowerAutomation", "/home/ubuntu/Powerauto.ai/debug.log")
safe_executor = SafeExecutor(enhanced_logger)
debug_helper = DebugHelper(enhanced_logger)

# 測試代碼
if __name__ == "__main__":
    print("🔧 測試增強錯誤處理系統")
    
    # 測試錯誤處理裝飾器
    @with_error_handling(logger=enhanced_logger, context={"test": "decorator"})
    def test_function(should_fail: bool = False):
        if should_fail:
            raise ValueError("測試錯誤")
        return "成功"
    
    # 測試成功情況
    print("\\n測試成功情況:")
    result = test_function(False)
    print(f"結果: {result}")
    
    # 測試失敗情況
    print("\\n測試失敗情況:")
    try:
        test_function(True)
    except ValueError as e:
        print(f"捕獲錯誤: {e}")
    
    # 測試安全執行器
    print("\\n測試安全執行器:")
    def unreliable_function(attempt_count=[0]):
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError(f"嘗試 {attempt_count[0]} 失敗")
        return f"第 {attempt_count[0]} 次嘗試成功"
    
    result = safe_executor.safe_call(unreliable_function, max_retries=3)
    print(f"安全調用結果: {result}")
    
    # 測試對象檢查
    print("\\n測試對象檢查:")
    inspection = debug_helper.inspect_object(enhanced_logger, "enhanced_logger")
    print(f"對象類型: {inspection['type']}")
    print(f"方法數量: {len(inspection['methods'])}")
    
    # 創建錯誤報告
    print("\\n創建錯誤報告:")
    report = debug_helper.create_error_report("/home/ubuntu/Powerauto.ai/error_report.json")
    print(f"錯誤總數: {report['error_summary']['total_errors']}")
    
    print("\\n🎯 增強錯誤處理系統測試完成")

