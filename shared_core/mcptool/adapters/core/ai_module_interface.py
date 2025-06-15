"""
PowerAutomation AI增强功能标准接口规范
定义所有AI模块的统一接口和通信协议
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import time
from datetime import datetime

class AIModuleInterface(ABC):
    """AI模块标准接口"""
    
    def __init__(self, name: str):
        self.name = name
        self.created_time = datetime.now().isoformat()
        self.last_activity_time = datetime.now().isoformat()
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理输入数据的主要方法
        
        Args:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        Returns:
            标准化的处理结果字典
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        获取模块能力列表
        
        Returns:
            能力描述列表
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取模块状态信息
        
        Returns:
            标准化的状态信息字典
        """
        return {
            "module_name": self.name,
            "status": "active",
            "created_time": self.created_time,
            "last_activity_time": self.last_activity_time,
            "capabilities": self.get_capabilities(),
            "performance_metrics": self.performance_metrics
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据格式
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            验证结果
        """
        if not isinstance(input_data, dict):
            return False
        return True
    
    def update_metrics(self, success: bool, response_time: float):
        """
        更新性能指标
        
        Args:
            success: 是否成功
            response_time: 响应时间
        """
        self.performance_metrics["total_requests"] += 1
        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["failed_requests"] += 1
        
        # 更新平均响应时间
        total = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            (current_avg * (total - 1) + response_time) / total
        )
        
        self.last_activity_time = datetime.now().isoformat()

class StandardResponse:
    """标准响应格式"""
    
    @staticmethod
    def success(data: Any, message: str = "操作成功", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            metadata: 元数据
            
        Returns:
            标准化成功响应
        """
        return {
            "status": "success",
            "message": message,
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, error_code: str = "GENERAL_ERROR", details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建错误响应
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
            
        Returns:
            标准化错误响应
        """
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def partial_success(data: Any, message: str = "部分成功", warnings: List[str] = None) -> Dict[str, Any]:
        """
        创建部分成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            warnings: 警告信息列表
            
        Returns:
            标准化部分成功响应
        """
        return {
            "status": "partial_success",
            "message": message,
            "data": data,
            "warnings": warnings or [],
            "timestamp": datetime.now().isoformat()
        }

class AIModuleRegistry:
    """AI模块注册表"""
    
    def __init__(self):
        self.modules = {}
        self.module_dependencies = {}
    
    def register_module(self, module_id: str, module: AIModuleInterface, dependencies: List[str] = None):
        """
        注册AI模块
        
        Args:
            module_id: 模块ID
            module: 模块实例
            dependencies: 依赖的模块ID列表
        """
        if not isinstance(module, AIModuleInterface):
            raise ValueError("模块必须实现AIModuleInterface接口")
        
        self.modules[module_id] = module
        self.module_dependencies[module_id] = dependencies or []
    
    def get_module(self, module_id: str) -> Optional[AIModuleInterface]:
        """
        获取AI模块
        
        Args:
            module_id: 模块ID
            
        Returns:
            模块实例或None
        """
        return self.modules.get(module_id)
    
    def list_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有注册的模块
        
        Returns:
            模块信息字典
        """
        module_info = {}
        for module_id, module in self.modules.items():
            module_info[module_id] = {
                "name": module.name,
                "capabilities": module.get_capabilities(),
                "status": module.get_status(),
                "dependencies": self.module_dependencies.get(module_id, [])
            }
        return module_info
    
    def check_dependencies(self, module_id: str) -> bool:
        """
        检查模块依赖是否满足
        
        Args:
            module_id: 模块ID
            
        Returns:
            依赖是否满足
        """
        dependencies = self.module_dependencies.get(module_id, [])
        for dep_id in dependencies:
            if dep_id not in self.modules:
                return False
        return True

class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_exception(e: Exception, context: str = "") -> Dict[str, Any]:
        """
        处理异常并返回标准错误响应
        
        Args:
            e: 异常对象
            context: 上下文信息
            
        Returns:
            标准化错误响应
        """
        error_type = type(e).__name__
        error_message = str(e)
        
        return StandardResponse.error(
            message=f"{context}: {error_message}" if context else error_message,
            error_code=error_type,
            details={
                "exception_type": error_type,
                "context": context,
                "traceback": str(e)
            }
        )
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Optional[Dict[str, Any]]:
        """
        验证必需字段
        
        Args:
            data: 数据字典
            required_fields: 必需字段列表
            
        Returns:
            如果验证失败返回错误响应，否则返回None
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return StandardResponse.error(
                message=f"缺少必需字段: {', '.join(missing_fields)}",
                error_code="MISSING_REQUIRED_FIELDS",
                details={"missing_fields": missing_fields}
            )
        
        return None

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timing(self, operation_id: str):
        """开始计时"""
        self.metrics[operation_id] = {
            "start_time": time.time(),
            "end_time": None,
            "duration": None
        }
    
    def end_timing(self, operation_id: str):
        """结束计时"""
        if operation_id in self.metrics:
            self.metrics[operation_id]["end_time"] = time.time()
            self.metrics[operation_id]["duration"] = (
                self.metrics[operation_id]["end_time"] - 
                self.metrics[operation_id]["start_time"]
            )
    
    def get_metrics(self, operation_id: str = None) -> Dict[str, Any]:
        """获取性能指标"""
        if operation_id:
            return self.metrics.get(operation_id, {})
        return self.metrics
    
    def clear_metrics(self):
        """清除性能指标"""
        self.metrics.clear()

# 全局实例
ai_module_registry = AIModuleRegistry()
performance_monitor = PerformanceMonitor()

# 标准化装饰器
def standardize_response(func):
    """标准化响应装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # 如果结果已经是标准格式，直接返回
            if isinstance(result, dict) and "status" in result:
                return result
            
            # 否则包装为标准成功响应
            return StandardResponse.success(
                data=result,
                metadata={"response_time": response_time}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ErrorHandler.handle_exception(e, func.__name__)
    
    return wrapper

def validate_input_data(required_fields: List[str]):
    """输入数据验证装饰器"""
    def decorator(func):
        def wrapper(self, input_data: Dict[str, Any], *args, **kwargs):
            # 验证必需字段
            validation_error = ErrorHandler.validate_required_fields(input_data, required_fields)
            if validation_error:
                return validation_error
            
            # 调用原函数
            return func(self, input_data, *args, **kwargs)
        
        return wrapper
    return decorator

def monitor_performance(operation_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            performance_monitor.start_timing(op_name)
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                performance_monitor.end_timing(op_name)
        
        return wrapper
    return decorator

