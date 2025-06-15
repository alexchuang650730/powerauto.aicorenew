"""
PowerAuto AI Core 配置文件
"""

import os
from typing import Dict, Any

class Config:
    """配置类"""
    
    # 基础配置
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # 搜索引擎配置
    SEARCH_ENGINE = {
        "max_results": 10,
        "timeout": 5.0,
        "cache_ttl": 300  # 5分钟缓存
    }
    
    # MCP配置
    MCP_CONFIG = {
        "timeout": 30.0,
        "max_retries": 3,
        "retry_delay": 1.0
    }
    
    # Kilo Code配置
    KILOCODE_CONFIG = {
        "timeout": 60.0,
        "max_strategies": 5
    }
    
    # 智能介入配置
    INTERVENTION_CONFIG = {
        "monitor_interval": 1.0,  # 监听间隔（秒）
        "input_threshold": 10,    # 最小输入长度
        "browser_headless": False,  # 浏览器是否无头模式
        "targets": {
            "vscode": {
                "enabled": True,
                "url_patterns": ["vscode://", "localhost:3000"],
                "selectors": {
                    "input": "textarea, input[type='text']",
                    "file_input": "input[type='file']"
                }
            },
            "manus": {
                "enabled": True,
                "url_patterns": ["manus.im", "localhost:8080"],
                "selectors": {
                    "input": "[placeholder*='发送消息'], textarea",
                    "file_input": "input[type='file']"
                }
            }
        }
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取完整配置"""
        return {
            "debug": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "search_engine": cls.SEARCH_ENGINE,
            "mcp": cls.MCP_CONFIG,
            "kilocode": cls.KILOCODE_CONFIG,
            "intervention": cls.INTERVENTION_CONFIG
        }

