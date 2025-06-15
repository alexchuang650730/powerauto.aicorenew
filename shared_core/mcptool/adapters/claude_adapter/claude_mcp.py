"""
Claude适配器实现

此模块实现了基于Anthropic Claude API的适配器，用于将Claude的大模型能力集成到PowerAutomation系统中。
适配器遵循接口标准，确保与系统的无缝集成，同时支持与Gemini和Kilo Code适配器的协同工作。
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
import requests

# 导入接口定义
from ..interfaces.code_generation_interface import CodeGenerationInterface
from ..interfaces.code_optimization_interface import CodeOptimizationInterface
from ..interfaces.adapter_interface import KiloCodeAdapterInterface

# 配置日志
logging.basicConfig(
    level=os.environ.get("CLAUDE_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("CLAUDE_LOG_FILE", None)
)
logger = logging.getLogger("claude_adapter")

class ClaudeAdapter(CodeGenerationInterface, CodeOptimizationInterface, KiloCodeAdapterInterface):
    """
    Claude适配器实现，提供代码生成、解释、优化等功能。
    
    此适配器通过API调用Anthropic Claude服务，将其功能集成到PowerAutomation系统中。
    所有方法都严格遵循接口标准，确保与系统的兼容性和与其他适配器的协同工作。
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化Claude适配器
        
        Args:
            api_key: Claude API密钥，如果为None则从环境变量获取
            base_url: Claude API基础URL，如果为None则使用默认值
        """
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        self.base_url = base_url or os.environ.get("CLAUDE_BASE_URL", "https://api.anthropic.com")
        self.model = os.environ.get("CLAUDE_MODEL", "claude-3-opus-20240229")
        self.timeout = int(os.environ.get("CLAUDE_TIMEOUT", "60"))
        
        if not self.api_key:
            logger.warning("No API key provided for Claude adapter")
            
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
        system_prompt = f"You are an expert {language} programmer. Generate clean, efficient, and well-documented code."
        user_prompt = f"Generate {language} code for: {prompt}"
        
        response = self._call_claude_api(system_prompt, user_prompt)
        
        return {
            "code": self._extract_code(response, language),
            "language": language,
            "model": self.model,
            "status": "success"
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
        system_prompt = f"You are an expert {language} programmer specializing in code optimization."
        user_prompt = f"Optimize this {language} code for {optimization_type}:\n\n```{language}\n{code}\n```"
        
        response = self._call_claude_api(system_prompt, user_prompt)
        
        return {
            "optimized_code": self._extract_code(response, language),
            "language": language,
            "optimization_type": optimization_type,
            "model": self.model,
            "status": "success"
        }
    
    def _call_claude_api(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用Claude API
        
        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            
        Returns:
            API响应文本
        """
        if not self.api_key:
            logger.error("Cannot call Claude API: No API key available")
            return "ERROR: No API key available"
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 4000
            }
            
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return f"ERROR: API returned status code {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return f"ERROR: {str(e)}"
    
    def _extract_code(self, response: str, language: str) -> str:
        """
        从响应中提取代码
        
        Args:
            response: API响应文本
            language: 编程语言
            
        Returns:
            提取的代码
        """
        # 尝试提取代码块
        import re
        pattern = f"```(?:{language})?\\n(.*?)\\n```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        else:
            # 如果没有代码块，返回整个响应
            return response.strip()


class ClaudeMCP:
    """
    Claude MCP适配器，将Claude的能力集成到MCP系统中。
    
    此适配器实现了MCP协议，提供代码生成、优化等功能，并支持与其他MCP适配器协同工作。
    """
    
    def __init__(self):
        """初始化Claude MCP适配器"""
        self.name = "ClaudeMCP"
        self.version = "1.0.0"
        self.description = "Claude MCP适配器，提供AI代码生成和优化功能"
        self.adapter = ClaudeAdapter()
        self.capabilities = ["code_generation", "code_optimization", "text_completion"]
        
        # 初始化日志
        self.logger = logging.getLogger("MCP.ClaudeMCP")
        self.logger.info("初始化MCP适配器: ClaudeMCP")
        
        # 检查API密钥
        if not self.adapter.api_key:
            self.logger.warning("未提供Claude API密钥，部分功能可能不可用")
            self.available = False
        else:
            self.available = True
            
        self.logger.info(f"Claude MCP适配器初始化完成，可用性: {self.available}")
    
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
                "message": "Claude适配器不可用，请检查API密钥",
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
            
        system_prompt = "You are a helpful AI assistant."
        response = self.adapter._call_claude_api(system_prompt, prompt)
        
        return {
            "status": "success",
            "result": {
                "completion": response,
                "model": self.adapter.model
            }
        }

