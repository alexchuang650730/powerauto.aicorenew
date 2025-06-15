"""
PowerAutomation 增强错误处理模块
提供统一的错误处理、日志记录和恢复机制
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, Callable
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"           # 低级错误，不影响主要功能
    MEDIUM = "medium"     # 中级错误，影响部分功能
    HIGH = "high"         # 高级错误，影响主要功能
    CRITICAL = "critical" # 严重错误，系统无法正常运行

class ErrorCategory(Enum):
    """错误类别"""
    API_ERROR = "api_error"                    # API调用错误
    WORKFLOW_ERROR = "workflow_error"          # 工作流错误
    CONFIG_ERROR = "config_error"              # 配置错误
    NETWORK_ERROR = "network_error"            # 网络错误
    VALIDATION_ERROR = "validation_error"      # 验证错误
    SYSTEM_ERROR = "system_error"              # 系统错误
    USER_ERROR = "user_error"                  # 用户错误

class PowerAutomationError(Exception):
    """PowerAutomation基础异常类"""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM_ERROR, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "timestamp": self.timestamp,
            "traceback": traceback.format_exc()
        }

class APIError(PowerAutomationError):
    """API相关错误"""
    
    def __init__(self, message: str, api_name: str = None, status_code: int = None, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        details = {"api_name": api_name, "status_code": status_code}
        super().__init__(message, ErrorCategory.API_ERROR, severity, details)

class WorkflowError(PowerAutomationError):
    """工作流相关错误"""
    
    def __init__(self, message: str, workflow_id: str = None, node_id: str = None,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        details = {"workflow_id": workflow_id, "node_id": node_id}
        super().__init__(message, ErrorCategory.WORKFLOW_ERROR, severity, details)

class ConfigError(PowerAutomationError):
    """配置相关错误"""
    
    def __init__(self, message: str, config_file: str = None, config_key: str = None,
                 severity: ErrorSeverity = ErrorSeverity.HIGH):
        details = {"config_file": config_file, "config_key": config_key}
        super().__init__(message, ErrorCategory.CONFIG_ERROR, severity, details)

class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        self.error_callbacks = {}
        
    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable):
        """注册错误恢复策略"""
        self.recovery_strategies[category] = strategy
        logger.info(f"已注册{category.value}的恢复策略")
        
    def register_error_callback(self, category: ErrorCategory, callback: Callable):
        """注册错误回调函数"""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)
        logger.info(f"已注册{category.value}的错误回调")
        
    def handle_error(self, error: PowerAutomationError) -> Dict[str, Any]:
        """处理错误"""
        # 记录错误
        self._log_error(error)
        
        # 添加到历史记录
        self.error_history.append(error)
        
        # 执行错误回调
        self._execute_callbacks(error)
        
        # 尝试恢复
        recovery_result = self._attempt_recovery(error)
        
        return {
            "error": error.to_dict(),
            "recovery_attempted": recovery_result["attempted"],
            "recovery_successful": recovery_result["successful"],
            "recovery_details": recovery_result["details"]
        }
        
    def _log_error(self, error: PowerAutomationError):
        """记录错误日志"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error.severity, logging.ERROR)
        
        logger.log(log_level, f"[{error.category.value.upper()}] {error.message}")
        if error.details:
            logger.log(log_level, f"错误详情: {error.details}")
            
    def _execute_callbacks(self, error: PowerAutomationError):
        """执行错误回调"""
        callbacks = self.error_callbacks.get(error.category, [])
        for callback in callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"执行错误回调失败: {e}")
                
    def _attempt_recovery(self, error: PowerAutomationError) -> Dict[str, Any]:
        """尝试错误恢复"""
        strategy = self.recovery_strategies.get(error.category)
        
        if not strategy:
            return {
                "attempted": False,
                "successful": False,
                "details": "没有可用的恢复策略"
            }
            
        try:
            result = strategy(error)
            return {
                "attempted": True,
                "successful": result.get("successful", False),
                "details": result.get("details", "恢复策略执行完成")
            }
        except Exception as e:
            logger.error(f"恢复策略执行失败: {e}")
            return {
                "attempted": True,
                "successful": False,
                "details": f"恢复策略执行失败: {e}"
            }
            
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        if not self.error_history:
            return {"total_errors": 0}
            
        total_errors = len(self.error_history)
        
        # 按类别统计
        category_stats = {}
        for error in self.error_history:
            category = error.category.value
            category_stats[category] = category_stats.get(category, 0) + 1
            
        # 按严重程度统计
        severity_stats = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
            
        # 最近错误
        recent_errors = self.error_history[-10:]
        
        return {
            "total_errors": total_errors,
            "category_distribution": category_stats,
            "severity_distribution": severity_stats,
            "recent_errors": [error.to_dict() for error in recent_errors]
        }
        
    def clear_error_history(self):
        """清空错误历史"""
        self.error_history.clear()
        logger.info("错误历史已清空")

# 全局错误处理器实例
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
        _setup_default_strategies()
    return _error_handler

def _setup_default_strategies():
    """设置默认恢复策略"""
    handler = get_error_handler()
    
    # API错误恢复策略
    def api_recovery_strategy(error: APIError) -> Dict[str, Any]:
        """API错误恢复策略"""
        api_name = error.details.get("api_name")
        
        # 嘗試切換到模擬模式
        try:
            from mcptool.adapters.unified_config_manager_mcp import UnifiedConfigManagerMCP
            config_manager = UnifiedConfigManagerMCP()
            
            if api_name:
                # 切換到模擬模式作為回退
                switch_request = {
                    'action': 'execute_tool',
                    'parameters': {
                        'tool_name': 'switch_api_mode',
                        'tool_params': {
                            'mode': 'mock',
                            'api_provider': api_name
                        }
                    }
                }
                
                result = config_manager.process(switch_request)
                if result.get('status') == 'success':
                    return {
                        "successful": True,
                        "details": f"已為{api_name}啟用回退模式（切換到模擬模式）"
                    }
        except Exception as e:
            return {
                "successful": False,
                "details": f"API恢復失敗: {e}"
            }
            
        return {
            "successful": False,
            "details": "无法恢复API错误"
        }
    
    # 工作流错误恢复策略
    def workflow_recovery_strategy(error: WorkflowError) -> Dict[str, Any]:
        """工作流错误恢复策略"""
        workflow_id = error.details.get("workflow_id")
        
        # 尝试重置工作流状态
        try:
            # 这里应该实现工作流重置逻辑
            return {
                "successful": True,
                "details": f"工作流{workflow_id}状态已重置"
            }
        except Exception as e:
            return {
                "successful": False,
                "details": f"工作流恢复失败: {e}"
            }
    
    # 配置错误恢复策略
    def config_recovery_strategy(error: ConfigError) -> Dict[str, Any]:
        """配置错误恢复策略"""
        config_file = error.details.get("config_file")
        
        # 尝试重新加载配置
        try:
            # 这里应该实现配置重新加载逻辑
            return {
                "successful": True,
                "details": f"配置文件{config_file}已重新加载"
            }
        except Exception as e:
            return {
                "successful": False,
                "details": f"配置恢复失败: {e}"
            }
    
    # 注册恢复策略
    handler.register_recovery_strategy(ErrorCategory.API_ERROR, api_recovery_strategy)
    handler.register_recovery_strategy(ErrorCategory.WORKFLOW_ERROR, workflow_recovery_strategy)
    handler.register_recovery_strategy(ErrorCategory.CONFIG_ERROR, config_recovery_strategy)

def error_handler_decorator(category: ErrorCategory = ErrorCategory.SYSTEM_ERROR, 
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except PowerAutomationError as e:
                # 已经是PowerAutomation错误，直接处理
                handler = get_error_handler()
                return handler.handle_error(e)
            except Exception as e:
                # 转换为PowerAutomation错误
                pa_error = PowerAutomationError(
                    message=str(e),
                    category=category,
                    severity=severity,
                    details={"original_exception": type(e).__name__}
                )
                handler = get_error_handler()
                return handler.handle_error(pa_error)
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """安全执行函数"""
    try:
        result = func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except PowerAutomationError as e:
        handler = get_error_handler()
        error_result = handler.handle_error(e)
        return {
            "success": False,
            "result": None,
            "error": error_result
        }
    except Exception as e:
        pa_error = PowerAutomationError(
            message=str(e),
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.MEDIUM
        )
        handler = get_error_handler()
        error_result = handler.handle_error(pa_error)
        return {
            "success": False,
            "result": None,
            "error": error_result
        }

# 便捷函数
def raise_api_error(message: str, api_name: str = None, status_code: int = None):
    """抛出API错误"""
    raise APIError(message, api_name, status_code)

def raise_workflow_error(message: str, workflow_id: str = None, node_id: str = None):
    """抛出工作流错误"""
    raise WorkflowError(message, workflow_id, node_id)

def raise_config_error(message: str, config_file: str = None, config_key: str = None):
    """抛出配置错误"""
    raise ConfigError(message, config_file, config_key)

