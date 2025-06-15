#!/usr/bin/env python3
"""
PowerAutomation v0.2 標準化日誌系統
提供統一的日誌格式、分級記錄、集中配置和性能監控
"""

import logging
import logging.handlers
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import traceback

class LogLevel(Enum):
    """日誌級別枚舉"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """日誌分類枚舉"""
    SYSTEM = "system"
    MCP = "mcp"
    MEMORY = "memory"
    BACKUP = "backup"
    TOKEN = "token"
    MONITOR = "monitor"
    GAIA = "gaia"
    CLI = "cli"
    PERFORMANCE = "performance"
    ERROR = "error"

@dataclass
class LogEntry:
    """標準化日誌條目"""
    timestamp: str
    level: str
    category: str
    module: str
    function: str
    message: str
    context: Dict[str, Any]
    performance_metrics: Optional[Dict[str, float]] = None
    error_details: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class PowerAutomationLogger:
    """PowerAutomation標準化日誌器"""
    
    def __init__(self, 
                 log_dir: str = "/home/ubuntu/projects/communitypowerautomation/logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_performance: bool = True):
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_performance = enable_performance
        
        # 創建不同類別的日誌文件
        self.loggers = {}
        self.handlers = {}
        
        # 性能監控
        self.performance_data = {}
        self.session_id = self._generate_session_id()
        
        # 初始化日誌器
        self._setup_loggers()
        
        # 啟動性能監控線程
        if self.enable_performance:
            self._start_performance_monitor()
    
    def _generate_session_id(self) -> str:
        """生成會話ID"""
        return f"session_{int(time.time())}_{os.getpid()}"
    
    def _setup_loggers(self):
        """設置所有類別的日誌器"""
        
        # 主日誌文件 - 所有日誌
        main_log_file = self.log_dir / "powerautomation.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log_file, 
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # 錯誤日誌文件 - 只記錄錯誤
        error_log_file = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # 性能日誌文件
        performance_log_file = self.log_dir / "performance.log"
        performance_handler = logging.handlers.RotatingFileHandler(
            performance_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 設置格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        main_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        performance_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 為每個類別創建日誌器
        for category in LogCategory:
            logger_name = f"powerautomation.{category.value}"
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            
            # 清除現有處理器
            logger.handlers.clear()
            
            # 添加處理器
            logger.addHandler(main_handler)
            logger.addHandler(error_handler)
            logger.addHandler(performance_handler)
            
            if self.enable_console:
                logger.addHandler(console_handler)
            
            # 防止重複日誌
            logger.propagate = False
            
            self.loggers[category.value] = logger
        
        # 存儲處理器引用
        self.handlers = {
            'main': main_handler,
            'error': error_handler,
            'performance': performance_handler,
            'console': console_handler
        }
    
    def _start_performance_monitor(self):
        """啟動性能監控線程"""
        def monitor():
            while True:
                try:
                    # 收集系統性能指標
                    import psutil
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    
                    performance_metrics = {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available_gb': memory.available / (1024**3),
                        'disk_percent': disk.percent,
                        'disk_free_gb': disk.free / (1024**3),
                        'timestamp': time.time()
                    }
                    
                    self.log_performance("system_monitor", performance_metrics)
                    
                    # 每60秒監控一次
                    time.sleep(60)
                    
                except Exception as e:
                    self.log_error("performance_monitor", f"性能監控錯誤: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _create_log_entry(self, 
                         level: str,
                         category: str,
                         message: str,
                         context: Dict[str, Any] = None,
                         performance_metrics: Dict[str, float] = None,
                         error_details: Dict[str, Any] = None) -> LogEntry:
        """創建標準化日誌條目"""
        
        # 獲取調用者信息
        try:
            frame = sys._getframe(3)  # 跳過內部調用層級
            module = frame.f_globals.get('__name__', 'unknown')
            function = frame.f_code.co_name
        except ValueError:
            # 調用棧不夠深時的備用方案
            module = 'unknown'
            function = 'unknown'
        
        return LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            category=category,
            module=module,
            function=function,
            message=message,
            context=context or {},
            performance_metrics=performance_metrics,
            error_details=error_details,
            session_id=self.session_id
        )
    
    def log(self, 
            level: LogLevel,
            category: LogCategory,
            message: str,
            context: Dict[str, Any] = None,
            performance_metrics: Dict[str, float] = None):
        """通用日誌記錄方法"""
        
        try:
            logger = self.loggers.get(category.value)
            if not logger:
                return
            
            log_entry = self._create_log_entry(
                level.value,
                category.value,
                message,
                context,
                performance_metrics
            )
            
            # 記錄到對應級別
            log_level = getattr(logging, level.value)
            logger.log(log_level, self._format_log_message(log_entry))
            
        except Exception as e:
            # 日誌系統本身出錯時的備用處理
            print(f"日誌記錄失敗: {e}")
    
    def _format_log_message(self, log_entry: LogEntry) -> str:
        """格式化日誌消息"""
        base_msg = f"[{log_entry.category}] {log_entry.message}"
        
        if log_entry.context:
            base_msg += f" | Context: {json.dumps(log_entry.context, ensure_ascii=False)}"
        
        if log_entry.performance_metrics:
            base_msg += f" | Performance: {json.dumps(log_entry.performance_metrics)}"
        
        if log_entry.error_details:
            base_msg += f" | Error: {json.dumps(log_entry.error_details, ensure_ascii=False)}"
        
        return base_msg
    
    def log_info(self, category: Union[str, LogCategory], message: str, context: Dict[str, Any] = None):
        """記錄信息日誌"""
        if isinstance(category, str):
            category = LogCategory(category)
        self.log(LogLevel.INFO, category, message, context)
    
    def log_warning(self, category: Union[str, LogCategory], message: str, context: Dict[str, Any] = None):
        """記錄警告日誌"""
        if isinstance(category, str):
            category = LogCategory(category)
        self.log(LogLevel.WARNING, category, message, context)
    
    def log_error(self, category: Union[str, LogCategory], message: str, 
                  context: Dict[str, Any] = None, exception: Exception = None):
        """記錄錯誤日誌"""
        if isinstance(category, str):
            category = LogCategory(category)
        
        error_details = None
        if exception:
            error_details = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        log_entry = self._create_log_entry(
            LogLevel.ERROR.value,
            category.value,
            message,
            context,
            error_details=error_details
        )
        
        logger = self.loggers.get(category.value)
        if logger:
            logger.error(self._format_log_message(log_entry))
    
    def log_performance(self, operation: str, metrics: Dict[str, float], 
                       category: LogCategory = LogCategory.PERFORMANCE):
        """記錄性能指標"""
        message = f"Performance metrics for {operation}"
        self.log(LogLevel.INFO, category, message, performance_metrics=metrics)
    
    def log_critical(self, category: Union[str, LogCategory], message: str, 
                    context: Dict[str, Any] = None, exception: Exception = None):
        """記錄嚴重錯誤日誌"""
        if isinstance(category, str):
            category = LogCategory(category)
        
        error_details = None
        if exception:
            error_details = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        log_entry = self._create_log_entry(
            LogLevel.CRITICAL.value,
            category.value,
            message,
            context,
            error_details=error_details
        )
        
        logger = self.loggers.get(category.value)
        if logger:
            logger.critical(self._format_log_message(log_entry))
    
    def get_log_stats(self) -> Dict[str, Any]:
        """獲取日誌統計信息"""
        stats = {
            'session_id': self.session_id,
            'log_directory': str(self.log_dir),
            'log_files': [],
            'total_size_mb': 0
        }
        
        for log_file in self.log_dir.glob('*.log'):
            file_size = log_file.stat().st_size
            stats['log_files'].append({
                'name': log_file.name,
                'size_mb': file_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            })
            stats['total_size_mb'] += file_size / (1024 * 1024)
        
        return stats

# 全局日誌器實例
_global_logger = None

def get_logger() -> PowerAutomationLogger:
    """獲取全局日誌器實例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = PowerAutomationLogger()
    return _global_logger

def log_info(category: Union[str, LogCategory], message: str, context: Dict[str, Any] = None):
    """全局信息日誌函數"""
    get_logger().log_info(category, message, context)

def log_warning(category: Union[str, LogCategory], message: str, context: Dict[str, Any] = None):
    """全局警告日誌函數"""
    get_logger().log_warning(category, message, context)

def log_error(category: Union[str, LogCategory], message: str, 
              context: Dict[str, Any] = None, exception: Exception = None):
    """全局錯誤日誌函數"""
    get_logger().log_error(category, message, context, exception)

def log_performance(operation: str, metrics: Dict[str, float]):
    """全局性能日誌函數"""
    get_logger().log_performance(operation, metrics)

def log_critical(category: Union[str, LogCategory], message: str, 
                context: Dict[str, Any] = None, exception: Exception = None):
    """全局嚴重錯誤日誌函數"""
    get_logger().log_critical(category, message, context, exception)

# 性能監控裝飾器
def performance_monitor(operation_name: str = None):
    """性能監控裝飾器 - 支持異步函數"""
    def decorator(func):
        import asyncio
        import functools
        
        if asyncio.iscoroutinefunction(func):
            # 異步函數處理
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    log_performance(op_name, {
                        'execution_time_seconds': execution_time,
                        'success': True
                    })
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    log_performance(op_name, {
                        'execution_time_seconds': execution_time,
                        'success': False
                    })
                    
                    log_error(LogCategory.ERROR, f"函數執行失敗: {op_name}", 
                             {'function': func.__name__}, e)
                    raise
            
            return async_wrapper
        else:
            # 同步函數處理
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    log_performance(op_name, {
                        'execution_time_seconds': execution_time,
                        'success': True
                    })
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    log_performance(op_name, {
                        'execution_time_seconds': execution_time,
                        'success': False
                    })
                    
                    log_error(LogCategory.ERROR, f"函數執行失敗: {op_name}", 
                             {'function': func.__name__}, e)
                    raise
            
            return sync_wrapper
        
        return wrapper
    return decorator

if __name__ == "__main__":
    # 測試標準化日誌系統
    logger = PowerAutomationLogger()
    
    # 測試不同類型的日誌
    logger.log_info(LogCategory.SYSTEM, "系統啟動", {'version': 'v0.2'})
    logger.log_warning(LogCategory.MCP, "MCP適配器連接緩慢", {'adapter': 'kilocode'})
    logger.log_error(LogCategory.BACKUP, "備份失敗", {'reason': '網絡錯誤'})
    
    # 測試性能監控
    logger.log_performance("test_operation", {
        'execution_time': 1.5,
        'memory_usage': 256.7,
        'cpu_usage': 45.2
    })
    
    # 測試裝飾器
    @performance_monitor("test_function")
    def test_function():
        time.sleep(0.1)
        return "測試完成"
    
    result = test_function()
    print(f"測試結果: {result}")
    
    # 顯示日誌統計
    stats = logger.get_log_stats()
    print(f"日誌統計: {json.dumps(stats, indent=2, ensure_ascii=False)}")

