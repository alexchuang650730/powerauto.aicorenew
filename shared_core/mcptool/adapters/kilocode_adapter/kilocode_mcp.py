"""
Kilo Code适配器实现

此模块实现了Kilo Code适配器，用于将Kilo Code的功能集成到PowerAutomation系统中。
适配器遵循接口标准，确保与系统的无缝集成，同时最小化对原有代码的修改。
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
import requests

# 导入接口定义
from ..interfaces.code_generation_interface import CodeGenerationInterface
from ..interfaces.code_optimization_interface import CodeOptimizationInterface
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日志
logging.basicConfig(
    level=os.environ.get("KILO_CODE_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("KILO_CODE_LOG_FILE", None)
)
logger = logging.getLogger("kilo_code_adapter")

class KiloCodeAdapter(CodeGenerationInterface, CodeOptimizationInterface, KiloCodeAdapterInterface):
    """
    Kilo Code适配器实现，提供代码生成、解释、优化等功能。
    
    此适配器通过API调用Kilo Code服务，将其功能集成到PowerAutomation系统中。
    所有方法都严格遵循接口标准，确保与系统的兼容性。
    """
    
    def __init__(self, api_key: Optional[str] = None, server_url: Optional[str] = None):
        """
        初始化Kilo Code适配器
        
        Args:
            api_key: Kilo Code API密钥，如果为None则从环境变量获取
            server_url: Kilo Code服务器URL，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.environ.get("KILO_CODE_API_KEY")
        self.server_url = server_url or os.environ.get("KILO_CODE_SERVER_URL", "https://api.kilocode.ai/v1")
        self.timeout = int(os.environ.get("KILO_CODE_TIMEOUT", "30"))
        
        if not self.api_key:
            logger.warning("No API key provided for Kilo Code adapter")
        
        logger.info(f"Initialized Kilo Code adapter with server URL: {self.server_url}")
        
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
        try:
            response = self._call_api("generate", {
                "prompt": prompt,
                "language": language,
                "options": kwargs
            })
            
            if "error" in response:
                return {
                    "status": "error",
                    "message": response["error"],
                    "code": None
                }
                
            return {
                "status": "success",
                "code": response.get("code", ""),
                "language": language,
                "metadata": response.get("metadata", {})
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
        try:
            response = self._call_api("optimize", {
                "code": code,
                "language": language,
                "optimization_type": optimization_type,
                "options": kwargs
            })
            
            if "error" in response:
                return {
                    "status": "error",
                    "message": response["error"],
                    "optimized_code": None
                }
                
            return {
                "status": "success",
                "optimized_code": response.get("optimized_code", ""),
                "language": language,
                "improvements": response.get("improvements", []),
                "metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error optimizing code: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "optimized_code": None
            }
    
    def _call_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用Kilo Code API
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应
        """
        if not self.api_key:
            return {"error": "No API key available"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.server_url}/{endpoint}",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {"error": f"API returned status code {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            return {"error": str(e)}


class KiloCodeMCP:
    """
    Kilo Code MCP适配器，将Kilo Code的代码生成和优化能力集成到MCP系统中。
    
    此适配器实现了MCP协议，提供代码生成、优化等功能，并支持与其他MCP适配器协同工作。
    """
    
    def __init__(self):
        """初始化Kilo Code MCP适配器"""
        self.name = "KiloCodeMCP"
        self.version = "1.0.0"
        self.description = "Kilo Code MCP适配器，提供AI代码生成和优化功能"
        
        # 尝试使用Claude API密钥作为备用
        api_key = os.environ.get("KILO_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        self.adapter = KiloCodeAdapter(api_key=api_key)
        
        self.capabilities = ["code_generation", "code_optimization", "code_explanation"]
        
        # 初始化日志
        self.logger = logging.getLogger("MCP.KiloCodeMCP")
        self.logger.info("初始化MCP适配器: KiloCodeMCP")
        
        # 检查API密钥
        if not self.adapter.api_key:
            self.logger.warning("未提供Kilo Code API密钥，部分功能可能不可用")
            self.available = False
        else:
            self.available = True
            
        self.logger.info(f"Kilo Code MCP适配器初始化完成，可用性: {self.available}")
    
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
            
        if data["action"] not in ["generate_code", "optimize_code", "explain_code"]:
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
                "message": "Kilo Code适配器不可用，请检查API密钥",
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
            elif action == "explain_code":
                return self._handle_explain_code(data)
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
    
    def _handle_explain_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理代码解释请求"""
        code = data.get("code", "")
        language = data.get("language", "python")
        
        if not code:
            return {
                "status": "error",
                "message": "缺少必要参数: code",
                "error_code": "MISSING_PARAMETER"
            }
            
        # 使用Claude API作为备用
        try:
            from ..claude_adapter.claude_mcp import ClaudeAdapter
            claude = ClaudeAdapter()
            
            system_prompt = f"You are an expert {language} programmer. Explain the following code clearly and concisely."
            user_prompt = f"Explain this {language} code:\n\n```{language}\n{code}\n```"
            
            explanation = claude._call_claude_api(system_prompt, user_prompt)
            
            return {
                "status": "success",
                "result": {
                    "explanation": explanation,
                    "language": language
                }
            }
        except Exception as e:
            self.logger.error(f"代码解释失败: {str(e)}")
            return {
                "status": "error",
                "message": f"代码解释失败: {str(e)}",
                "error_code": "EXPLANATION_FAILED"
            }

