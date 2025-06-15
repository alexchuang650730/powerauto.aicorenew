"""
Gemini API适配器实现

此模块实现了基于Google Gemini API的Kilo Code适配器，用于将Gemini的大模型能力集成到PowerAutomation系统中。
适配器遵循接口标准，确保与系统的无缝集成，同时最小化对原有代码的修改。
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
import google.generativeai as genai

# 导入接口定义
from ..interfaces.code_generation_interface import CodeGenerationInterface
from ..interfaces.code_optimization_interface import CodeOptimizationInterface
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日志
logging.basicConfig(
    level=os.environ.get("GEMINI_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("GEMINI_LOG_FILE", None)
)
logger = logging.getLogger("gemini_adapter")

class GeminiAdapter(CodeGenerationInterface, CodeOptimizationInterface, KiloCodeAdapterInterface):
    """
    Gemini适配器实现，提供代码生成、解释、优化等功能。
    
    此适配器通过API调用Google Gemini服务，将其功能集成到PowerAutomation系统中。
    所有方法都严格遵循接口标准，确保与系统的兼容性。
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化Gemini适配器
        
        Args:
            api_key: Gemini API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("No API key provided for Gemini adapter")
        
        # 初始化Gemini模型
        self.model = None
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        
        # 如果有API密钥，初始化模型
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"Initialized Gemini model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
                self.model = None
    
    def generate_code(self, prompt: str, language: str, **kwargs) -> Dict[str, Any]:
        """
        生成代码
        
        Args:
            prompt: 代码生成提示
            language: 目标编程语言
            **kwargs: 其他参数
            
        Returns:
            包含生成代码的字典
        """
        if not self.model:
            return {
                "status": "error",
                "message": "Gemini model not initialized",
                "code": None
            }
            
        try:
            # 构建提示
            full_prompt = f"Generate {language} code for the following task. Only return the code without explanations:\n\n{prompt}"
            
            # 调用Gemini API
            response = self.model.generate_content(full_prompt)
            
            # 提取代码
            code = self._extract_code(response.text, language)
            
            return {
                "status": "success",
                "code": code,
                "language": language,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "code": None
            }
    
    def optimize_code(self, code: str, language: str, optimization_type: str = "performance", **kwargs) -> Dict[str, Any]:
        """
        优化代码
        
        Args:
            code: 要优化的代码
            language: 编程语言
            optimization_type: 优化类型，如"performance"、"readability"等
            **kwargs: 其他参数
            
        Returns:
            包含优化后代码的字典
        """
        if not self.model:
            return {
                "status": "error",
                "message": "Gemini model not initialized",
                "optimized_code": None
            }
            
        try:
            # 构建提示
            full_prompt = f"Optimize the following {language} code for {optimization_type}. Only return the optimized code without explanations:\n\n```{language}\n{code}\n```"
            
            # 调用Gemini API
            response = self.model.generate_content(full_prompt)
            
            # 提取代码
            optimized_code = self._extract_code(response.text, language)
            
            return {
                "status": "success",
                "optimized_code": optimized_code,
                "language": language,
                "optimization_type": optimization_type,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error optimizing code: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "optimized_code": None
            }
    
    def _extract_code(self, text: str, language: str) -> str:
        """
        从响应中提取代码
        
        Args:
            text: 响应文本
            language: 编程语言
            
        Returns:
            提取的代码
        """
        # 尝试提取代码块
        import re
        pattern = f"```(?:{language})?\\n(.*?)\\n```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        else:
            # 如果没有代码块，返回整个响应
            return text.strip()


class GeminiMCP:
    """
    Gemini MCP适配器，将Google Gemini的能力集成到MCP系统中。
    
    此适配器实现了MCP协议，提供代码生成、优化等功能，并支持与其他MCP适配器协同工作。
    """
    
    def __init__(self):
        """初始化Gemini MCP适配器"""
        self.name = "GeminiMCP"
        self.version = "1.0.0"
        self.description = "Gemini MCP适配器，提供AI代码生成和优化功能"
        self.adapter = GeminiAdapter()
        self.capabilities = ["code_generation", "code_optimization", "text_completion"]
        
        # 初始化日志
        self.logger = logging.getLogger("MCP.GeminiMCP")
        self.logger.info("初始化MCP适配器: GeminiMCP")
        
        # 检查API密钥
        if not self.adapter.api_key:
            self.logger.warning("未提供Gemini API密钥，部分功能可能不可用")
            self.available = False
        else:
            self.available = True
            
        self.logger.info(f"Gemini MCP适配器初始化完成，可用性: {self.available}")
    
    def get_capabilities(self) -> List[str]:
        """
        获取适配器能力列表
        
        Returns:
            能力列表
        """
        return self.capabilities
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        验证输入数据
        
        Args:
            data: 输入数据
            
        Returns:
            数据是否有效
        """
        if not isinstance(data, dict):
            return False
            
        if "action" not in data:
            return False
            
        if data["action"] not in ["generate_code", "optimize_code", "complete_text"]:
            return False
            
        return True
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理请求
        
        Args:
            data: 请求数据
            
        Returns:
            处理结果
        """
        if not self.available:
            return {
                "status": "error",
                "message": "Gemini适配器不可用，请检查API密钥",
                "error_code": "ADAPTER_UNAVAILABLE"
            }
            
        if not self.validate_input(data):
            return {
                "status": "error",
                "message": "无效的输入数据",
                "error_code": "INVALID_INPUT"
            }
            
        try:
            action = data["action"]
            
            if action == "generate_code":
                return self._handle_generate_code(data)
            elif action == "optimize_code":
                return self._handle_optimize_code(data)
            elif action == "complete_text":
                return self._handle_complete_text(data)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {action}",
                    "error_code": "UNSUPPORTED_ACTION"
                }
                
        except Exception as e:
            self.logger.error(f"处理请求时出错: {str(e)}")
            return {
                "status": "error",
                "message": f"处理请求时出错: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
    
    def _handle_generate_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理代码生成请求"""
        prompt = data.get("prompt", "")
        language = data.get("language", "python")
        
        if not prompt:
            return {
                "status": "error",
                "message": "缺少必要参数: prompt",
                "error_code": "MISSING_PARAMETER"
            }
            
        result = self.adapter.generate_code(prompt, language)
        return {
            "status": "success",
            "result": result
        }
    
    def _handle_optimize_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理代码优化请求"""
        code = data.get("code", "")
        language = data.get("language", "python")
        optimization_type = data.get("optimization_type", "performance")
        
        if not code:
            return {
                "status": "error",
                "message": "缺少必要参数: code",
                "error_code": "MISSING_PARAMETER"
            }
            
        result = self.adapter.optimize_code(code, language, optimization_type)
        return {
            "status": "success",
            "result": result
        }
    
    def _handle_complete_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理文本补全请求"""
        prompt = data.get("prompt", "")
        
        if not prompt:
            return {
                "status": "error",
                "message": "缺少必要参数: prompt",
                "error_code": "MISSING_PARAMETER"
            }
            
        if not self.adapter.model:
            return {
                "status": "error",
                "message": "Gemini模型未初始化",
                "error_code": "MODEL_UNAVAILABLE"
            }
            
        try:
            response = self.adapter.model.generate_content(prompt)
            
            return {
                "status": "success",
                "result": {
                    "completion": response.text,
                    "model": self.adapter.model_name
                }
            }
        except Exception as e:
            self.logger.error(f"文本补全失败: {str(e)}")
            return {
                "status": "error",
                "message": f"文本补全失败: {str(e)}",
                "error_code": "COMPLETION_FAILED"
            }

