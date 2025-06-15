"""
适配器接口模块

此模块定义了适配器的基础接口，包括KiloCodeAdapterInterface和SRTAdapterInterface。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

class AdapterInterface(ABC):
    """
    适配器基础接口
    
    所有适配器必须实现的基础接口，提供初始化、健康检查、能力查询等基本功能。
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        使用配置信息初始化适配器
        
        Args:
            config: 配置信息字典
            
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """
        获取适配器支持的能力
        
        Returns:
            支持的能力字典，键为能力名称，值为是否支持
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        检查适配器健康状态
        
        Returns:
            健康状态信息字典
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        关闭适配器，释放资源
        
        Returns:
            关闭是否成功
        """
        pass

class KiloCodeAdapterInterface(AdapterInterface):
    """
    Kilo Code适配器接口
    
    扩展基础适配器接口，添加Kilo Code特有的方法。
    """
    
    @abstractmethod
    def decompose_task(self, task_description: str) -> List[Dict[str, Any]]:
        """
        分解任务
        
        Args:
            task_description: 任务描述
            
        Returns:
            分解后的子任务列表
        """
        pass
    
    @abstractmethod
    def batch_generate(self, prompts: List[str], context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        批量生成代码
        
        Args:
            prompts: 代码生成提示列表
            context: 共享上下文信息
            
        Returns:
            生成的代码字符串列表
        """
        pass

class SRTAdapterInterface(AdapterInterface):
    """
    SRT适配器接口
    
    扩展基础适配器接口，添加SRT特有的方法。
    """
    
    @abstractmethod
    def batch_train(self, thought_processes: List[Union[str, Dict[str, Any]]], 
                  batch_size: int = 32) -> Dict[str, Any]:
        """
        批量训练模型
        
        Args:
            thought_processes: 思考过程列表
            batch_size: 批处理大小
            
        Returns:
            训练结果信息
        """
        pass
    
    @abstractmethod
    def save_model(self, path: str) -> bool:
        """
        保存模型
        
        Args:
            path: 模型保存路径
            
        Returns:
            保存是否成功
        """
        pass
    
    @abstractmethod
    def load_model(self, path: str) -> bool:
        """
        加载模型
        
        Args:
            path: 模型加载路径
            
        Returns:
            加载是否成功
        """
        pass
