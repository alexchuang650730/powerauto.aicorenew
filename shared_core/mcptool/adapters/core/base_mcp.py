"""
基础MCP适配器模块

提供MCP适配器的基类实现，符合AI模块标准接口规范
"""

from typing import Dict, Any, List, Optional
import logging
import time
from datetime import datetime

# 导入标准接口
try:
    from .interfaces.ai_module_interface import AIModuleInterface, StandardResponse, ErrorHandler, monitor_performance
except ImportError:
    # 如果导入失败，提供基本的接口定义
    class AIModuleInterface:
        def __init__(self, name: str):
            self.name = name
        
        def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
            pass
        
        def get_capabilities(self) -> List[str]:
            pass
    
    class StandardResponse:
        @staticmethod
        def success(data: Any, message: str = "操作成功", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
            return {
                "status": "success",
                "message": message,
                "data": data,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
        
        @staticmethod
        def error(message: str, error_code: str = "GENERAL_ERROR", details: Dict[str, Any] = None) -> Dict[str, Any]:
            return {
                "status": "error",
                "message": message,
                "error_code": error_code,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            }
    
    class ErrorHandler:
        @staticmethod
        def handle_exception(e: Exception, context: str = "") -> Dict[str, Any]:
            return StandardResponse.error(
                message=f"{context}: {str(e)}" if context else str(e),
                error_code=type(e).__name__
            )
    
    def monitor_performance(operation_name: str = None):
        def decorator(func):
            return func
        return decorator


class BaseMCP(AIModuleInterface):
    """MCP适配器基类，所有MCP适配器都应继承此类，符合AI模块标准接口"""
    
    def __init__(self, name: str = "BaseMCP"):
        """
        初始化基础MCP适配器
        
        Args:
            name: 适配器名称
        """
        super().__init__(name)
        self.logger = logging.getLogger(f"MCP.{name}")
        self.logger.info(f"初始化MCP适配器: {name}")
        
        # 扩展性能指标
        self.performance_metrics.update({
            "last_error": None,
            "uptime_start": datetime.now().isoformat(),
            "module_version": "1.0.0"
        })
    
    @monitor_performance("mcp_process")
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理输入数据 - 标准化实现
        
        Args:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        Returns:
            标准化的处理结果字典
        """
        start_time = time.time()
        
        try:
            # 验证输入数据
            if not self.validate_input(input_data):
                return StandardResponse.error(
                    message="输入数据验证失败",
                    error_code="INVALID_INPUT"
                )
            
            # 调用子类的具体处理逻辑
            result = self._process_implementation(input_data, context)
            
            # 更新性能指标
            response_time = time.time() - start_time
            self.update_metrics(True, response_time)
            
            # 如果结果已经是标准格式，直接返回
            if isinstance(result, dict) and "status" in result:
                return result
            
            # 否则包装为标准成功响应
            return StandardResponse.success(
                data=result,
                message="处理完成",
                metadata={
                    "response_time": response_time,
                    "module_name": self.name
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            self.update_metrics(False, response_time)
            self.performance_metrics["last_error"] = str(e)
            
            self.logger.error(f"处理失败: {e}")
            return ErrorHandler.handle_exception(e, f"{self.name}.process")
    
    def _process_implementation(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        具体的处理实现 - 子类应该覆盖此方法
        
        Args:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        Returns:
            处理结果
        """
        self.logger.warning(f"{self.name}._process_implementation()被调用，这是一个应该被子类覆盖的方法")
        return {
            "message": f"{self.name}基础处理完成",
            "input_received": True,
            "context_available": context is not None
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据是否有效
        
        Args:
            input_data: 输入数据字典
            
        Returns:
            数据是否有效
        """
        self.logger.warning("BaseMCP.validate_input()被调用，这是一个应该被子类覆盖的方法")
        return True
    
    def get_capabilities(self) -> List[str]:
        """
        获取适配器能力列表
        
        Returns:
            能力描述列表
        """
        return ["基础MCP适配功能"]
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取适配器状态信息
        
        Returns:
            状态信息字典
        """
        return {
            "name": self.name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "health": "healthy"
        }

        if not isinstance(input_data, dict):
            self.logger.error("输入数据必须是字典类型")
            return False
        
        return True
    
    def get_capabilities(self) -> List[str]:
        """
        获取适配器能力列表 - 标准化实现
        
        Returns:
            能力描述列表
        """
        return [
            "基础MCP适配功能",
            "数据处理",
            "标准化响应"
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取适配器状态信息 - 扩展实现
        
        Returns:
            详细的状态信息字典
        """
        base_status = super().get_status()
        
        # 添加MCP特定的状态信息
        base_status.update({
            "adapter_type": "MCP",
            "logger_name": self.logger.name,
            "uptime": self._calculate_uptime(),
            "health_status": self._get_health_status()
        })
        
        return base_status
    
    def _calculate_uptime(self) -> str:
        """计算运行时间"""
        try:
            start_time = datetime.fromisoformat(self.performance_metrics["uptime_start"])
            uptime_seconds = (datetime.now() - start_time).total_seconds()
            
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            seconds = int(uptime_seconds % 60)
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "unknown"
    
    def _get_health_status(self) -> str:
        """获取健康状态"""
        total_requests = self.performance_metrics.get("total_requests", 0)
        failed_requests = self.performance_metrics.get("failed_requests", 0)
        
        if total_requests == 0:
            return "ready"
        
        failure_rate = failed_requests / total_requests
        
        if failure_rate < 0.05:  # 失败率小于5%
            return "healthy"
        elif failure_rate < 0.20:  # 失败率小于20%
            return "warning"
        else:
            return "unhealthy"
    
    def reset_metrics(self):
        """重置性能指标"""
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_error": None,
            "uptime_start": datetime.now().isoformat(),
            "module_version": "1.0.0"
        }
        self.logger.info(f"{self.name} 性能指标已重置")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        metrics = self.performance_metrics
        total = metrics.get("total_requests", 0)
        
        return {
            "total_requests": total,
            "success_rate": f"{(metrics.get('successful_requests', 0) / max(total, 1)) * 100:.1f}%",
            "failure_rate": f"{(metrics.get('failed_requests', 0) / max(total, 1)) * 100:.1f}%",
            "average_response_time": f"{metrics.get('average_response_time', 0):.3f}s",
            "uptime": self._calculate_uptime(),
            "health_status": self._get_health_status(),
            "last_error": metrics.get("last_error")
        }

