"""
代码生成接口模块

此模块定义了代码生成相关的接口，供适配器实现。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

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
