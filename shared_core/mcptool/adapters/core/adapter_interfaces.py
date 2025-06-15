"""
接口定义模块

此模块定义了适配器层的标准接口，确保Kilo Code和SRT组件与PowerAutomation系统的无缝集成。
所有适配器必须实现这些接口，以保证系统的一致性和可扩展性。
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

class CodeGenerationInterface(ABC):
    """
    代码生成接口
    
    定义代码生成相关的方法。
    """
    
    @abstractmethod
    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
                     mode: str = "standard") -> str:
        """
        根据提示生成代码
        
        Args:
            prompt: 代码生成提示
            context: 上下文信息
            mode: 生成模式
            
        Returns:
            生成的代码字符串
        """
        pass
    
    @abstractmethod
    def interpret_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        解释代码
        
        Args:
            code: 需要解释的代码
            context: 上下文信息
            
        Returns:
            包含代码解释的字典
        """
        pass

class CodeOptimizationInterface(ABC):
    """
    代码优化接口
    
    定义代码优化相关的方法。
    """
    
    @abstractmethod
    def optimize_code(self, code: str, optimization_level: str = "medium") -> str:
        """
        优化代码
        
        Args:
            code: 需要优化的代码
            optimization_level: 优化级别
            
        Returns:
            优化后的代码
        """
        pass
    
    @abstractmethod
    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """
        分析代码复杂度
        
        Args:
            code: 需要分析的代码
            
        Returns:
            包含复杂度分析的字典
        """
        pass
    
    @abstractmethod
    def suggest_improvements(self, code: str) -> List[Dict[str, Any]]:
        """
        提供代码改进建议
        
        Args:
            code: 需要分析的代码
            
        Returns:
            改进建议列表
        """
        pass

class SelfRewardTrainingInterface(ABC):
    """
    自我奖励训练接口
    
    定义自我奖励训练相关的方法。
    """
    
    @abstractmethod
    def train(self, thought_process: Union[str, Dict[str, Any]], 
             iterations: int = 100) -> Dict[str, Any]:
        """
        使用自我奖励机制训练模型
        
        Args:
            thought_process: 思考过程
            iterations: 训练迭代次数
            
        Returns:
            训练结果信息
        """
        pass
    
    @abstractmethod
    def evaluate(self, thought_process: Union[str, Dict[str, Any]]) -> float:
        """
        评估思考过程的质量
        
        Args:
            thought_process: 需要评估的思考过程
            
        Returns:
            质量评分
        """
        pass
    
    @abstractmethod
    def improve(self, thought_process: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """
        改进思考过程
        
        Args:
            thought_process: 原始思考过程
            
        Returns:
            改进后的思考过程
        """
        pass
