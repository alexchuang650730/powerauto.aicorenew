"""
代码优化接口模块

此模块定义了代码优化相关的接口，供适配器实现。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

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
