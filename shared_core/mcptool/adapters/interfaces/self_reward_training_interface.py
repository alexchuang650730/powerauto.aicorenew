"""
自我奖励训练接口模块

此模块定义了自我奖励训练相关的接口，供适配器实现。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Union

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
