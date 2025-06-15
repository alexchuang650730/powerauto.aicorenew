"""
統一配置管理器MCP適配器

此模塊實現了統一配置管理器MCP適配器，用於管理PowerAutomation系統的所有配置。
適配器提供了配置的讀取、寫入、驗證等功能，並支持多種配置類型。
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pathlib import Path

# 配置日誌
logging.basicConfig(
    level=os.environ.get("CONFIG_MANAGER_LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get("CONFIG_MANAGER_LOG_FILE", None)
)
logger = logging.getLogger("config_manager_mcp")

class ConfigType(Enum):
    """配置類型枚舉"""
    SYSTEM_CONFIG = "system"
    API_CONFIG = "api"
    API_KEYS = "api_keys"
    TOOL_CONFIG = "tools"
    USER_CONFIG = "user"
    TEST_CONFIG = "test"
    SECURITY_CONFIG = "security"

class UnifiedConfigManagerMCP:
    """
    統一配置管理器MCP適配器
    
    此適配器提供了統一的配置管理功能，包括：
    - 配置的讀取和寫入
    - 配置的驗證和更新
    - API密鑰的管理
    - 工具配置的管理
    """
    
    def __init__(self):
        """初始化統一配置管理器MCP適配器"""
        self.name = "UnifiedConfigManagerMCP"
        self.version = "1.0.0"
        self.description = "統一配置管理器MCP適配器，提供配置管理功能"
        
        # 初始化配置
        self.configs = {}
        for config_type in ConfigType:
            self.configs[config_type] = {}
        
        # 初始化工具列表
        self.tools = [
            {
                "id": "config_get",
                "name": "獲取配置",
                "description": "獲取指定配置項的值",
                "parameters": ["config_type", "key"]
            },
            {
                "id": "config_set",
                "name": "設置配置",
                "description": "設置指定配置項的值",
                "parameters": ["config_type", "key", "value"]
            },
            {
                "id": "config_list",
                "name": "列出配置",
                "description": "列出指定類型的所有配置項",
                "parameters": ["config_type"]
            },
            {
                "id": "api_key_check",
                "name": "檢查API密鑰",
                "description": "檢查指定API的密鑰是否有效",
                "parameters": ["api_name"]
            },
            {
                "id": "api_key_set",
                "name": "設置API密鑰",
                "description": "設置指定API的密鑰",
                "parameters": ["api_name", "api_key"]
            },
            {
                "id": "load_env",
                "name": "加載環境變量",
                "description": "從.env文件加載環境變量",
                "parameters": ["env_file"]
            },
            {
                "id": "save_env",
                "name": "保存環境變量",
                "description": "將環境變量保存到.env文件",
                "parameters": ["env_file"]
            }
        ]
        
        # 初始化API客戶端
        self.api_clients = {}
        
        # 初始化配置
        self._initialize_configs()
        
        logger.info(f"統一配置器管理器初始化完成，支持 {len(self.tools)} 個工具")
    
    def _initialize_configs(self):
        """初始化所有配置"""
        # API配置
        self.configs[ConfigType.API_CONFIG] = {
            "mode": "mock",
            "providers": {
                "claude": {
                    "enabled": True,
                    "mode": "mock",
                    "endpoint": "https://api.anthropic.com/v1/messages",
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,
                    "temperature": 0.7
                },
                "gemini": {
                    "enabled": True,
                    "mode": "mock",
                    "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
                    "model": "gemini-1.5-flash",
                    "max_tokens": 2048,
                    "temperature": 0.7
                },
                "openai": {
                    "enabled": False,
                    "mode": "mock",
                    "endpoint": "https://api.openai.com/v1/chat/completions",
                    "model": "gpt-4",
                    "max_tokens": 4096,
                    "temperature": 0.7
                },
                "manus": {
                    "enabled": True,
                    "mode": "real",
                    "endpoint": "internal",
                    "model": "unified_ai",
                    "max_tokens": 8192,
                    "temperature": 0.7
                }
            }
        }
        
        # API密鑰配置
        self.configs[ConfigType.API_KEYS] = {
            "claude": {
                "api_key": os.getenv("CLAUDE_API_KEY", ""),
                "status": "configured" if os.getenv("CLAUDE_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "gemini": {
                "api_key": os.getenv("GEMINI_API_KEY", ""),
                "status": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "status": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "supermemory": {
                "api_key": os.getenv("SUPERMEMORY_API_KEY", ""),
                "status": "configured" if os.getenv("SUPERMEMORY_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "kilocode": {
                "api_key": os.getenv("KILO_API_KEY", ""),
                "status": "configured" if os.getenv("KILO_API_KEY") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            },
            "github": {
                "api_key": os.getenv("GITHUB_TOKEN", ""),
                "status": "configured" if os.getenv("GITHUB_TOKEN") else "not_configured",
                "last_verified": None,
                "usage_count": 0
            }
        }
        
        # 系統配置
        self.configs[ConfigType.SYSTEM_CONFIG] = {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "log_file": os.getenv("LOG_FILE", ""),
            "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
            "max_retries": int(os.getenv("MAX_RETRIES", "3")),
            "timeout": int(os.getenv("TIMEOUT", "30")),
            "cache_dir": os.getenv("CACHE_DIR", "/tmp/powerautomation_cache"),
            "temp_dir": os.getenv("TEMP_DIR", "/tmp/powerautomation_temp")
        }
        
        # 工具配置
        self.configs[ConfigType.TOOL_CONFIG] = {
            "enabled_tools": ["config_get", "config_set", "config_list", "api_key_check", "api_key_set", "load_env", "save_env"],
            "default_tool": "config_get",
            "tool_timeout": int(os.getenv("TOOL_TIMEOUT", "10"))
        }
        
        # 測試配置
        self.configs[ConfigType.TEST_CONFIG] = {
            "test_mode": os.getenv("TEST_MODE", "mock"),
            "gaia_test_level": int(os.getenv("GAIA_TEST_LEVEL", "1")),
            "max_test_tasks": int(os.getenv("MAX_TEST_TASKS", "10")),
            "test_output_dir": os.getenv("TEST_OUTPUT_DIR", "test/results")
        }
        
        # 安全配置
        self.configs[ConfigType.SECURITY_CONFIG] = {
            "enable_api_key_rotation": os.getenv("ENABLE_API_KEY_ROTATION", "false").lower() == "true",
            "api_key_rotation_interval": int(os.getenv("API_KEY_ROTATION_INTERVAL", "30")),
            "enable_request_logging": os.getenv("ENABLE_REQUEST_LOGGING", "false").lower() == "true",
            "enable_response_logging": os.getenv("ENABLE_RESPONSE_LOGGING", "false").lower() == "true"
        }
        
        # 用戶配置
        self.configs[ConfigType.USER_CONFIG] = {
            "username": os.getenv("USERNAME", ""),
            "email": os.getenv("EMAIL", ""),
            "organization": os.getenv("ORGANIZATION", ""),
            "preferences": {
                "theme": os.getenv("THEME", "light"),
                "language": os.getenv("LANGUAGE", "zh-TW"),
                "timezone": os.getenv("TIMEZONE", "Asia/Taipei")
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """
        獲取適配器能力列表
        
        Returns:
            能力列表
        """
        return ["config_management", "api_key_management", "env_management"]
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        驗證輸入數據
        
        Args:
            data: 輸入數據
            
        Returns:
            數據是否有效
        """
        if not isinstance(data, dict):
            return False
            
        if "action" not in data:
            return False
            
        if data["action"] not in ["config_get", "config_set", "config_list", "api_key_check", "api_key_set", "load_env", "save_env"]:
            return False
            
        return True
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理請求
        
        Args:
            data: 請求數據
            
        Returns:
            處理結果
        """
        if not self.validate_input(data):
            return {
                "status": "error",
                "message": "無效的輸入數據",
                "error_code": "INVALID_INPUT"
            }
            
        try:
            action = data["action"]
            
            if action == "config_get":
                return self._handle_config_get(data)
            elif action == "config_set":
                return self._handle_config_set(data)
            elif action == "config_list":
                return self._handle_config_list(data)
            elif action == "api_key_check":
                return self._handle_api_key_check(data)
            elif action == "api_key_set":
                return self._handle_api_key_set(data)
            elif action == "load_env":
                return self._handle_load_env(data)
            elif action == "save_env":
                return self._handle_save_env(data)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {action}",
                    "error_code": "UNSUPPORTED_ACTION"
                }
                
        except Exception as e:
            logger.error(f"處理請求時出錯: {str(e)}")
            return {
                "status": "error",
                "message": f"處理請求時出錯: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
    
    def _handle_config_get(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理獲取配置請求"""
        config_type_str = data.get("config_type", "")
        key = data.get("key", "")
        
        if not config_type_str:
            return {
                "status": "error",
                "message": "缺少必要參數: config_type",
                "error_code": "MISSING_PARAMETER"
            }
            
        try:
            config_type = ConfigType(config_type_str)
        except ValueError:
            return {
                "status": "error",
                "message": f"無效的配置類型: {config_type_str}",
                "error_code": "INVALID_CONFIG_TYPE"
            }
            
        if not key:
            return {
                "status": "error",
                "message": "缺少必要參數: key",
                "error_code": "MISSING_PARAMETER"
            }
            
        # 獲取配置
        config = self.configs.get(config_type, {})
        
        # 處理嵌套鍵
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return {
                    "status": "error",
                    "message": f"配置項不存在: {key}",
                    "error_code": "CONFIG_NOT_FOUND"
                }
                
        # 如果是API密鑰，不返回實際值
        if config_type == ConfigType.API_KEYS and keys[-1] == "api_key":
            if value:
                value = "********"
            
        return {
            "status": "success",
            "config_type": config_type_str,
            "key": key,
            "value": value
        }
    
    def _handle_config_set(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理設置配置請求"""
        config_type_str = data.get("config_type", "")
        key = data.get("key", "")
        value = data.get("value", None)
        
        if not config_type_str:
            return {
                "status": "error",
                "message": "缺少必要參數: config_type",
                "error_code": "MISSING_PARAMETER"
            }
            
        try:
            config_type = ConfigType(config_type_str)
        except ValueError:
            return {
                "status": "error",
                "message": f"無效的配置類型: {config_type_str}",
                "error_code": "INVALID_CONFIG_TYPE"
            }
            
        if not key:
            return {
                "status": "error",
                "message": "缺少必要參數: key",
                "error_code": "MISSING_PARAMETER"
            }
            
        if value is None:
            return {
                "status": "error",
                "message": "缺少必要參數: value",
                "error_code": "MISSING_PARAMETER"
            }
            
        # 獲取配置
        config = self.configs.get(config_type, {})
        
        # 處理嵌套鍵
        keys = key.split(".")
        parent = config
        for i, k in enumerate(keys[:-1]):
            if k not in parent:
                parent[k] = {}
            parent = parent[k]
            
        # 設置值
        parent[keys[-1]] = value
        
        # 如果是API密鑰，同時設置環境變量和狀態
        if config_type == ConfigType.API_KEYS and keys[-1] == "api_key":
            api_name = keys[0]
            os.environ[f"{api_name.upper()}_API_KEY"] = value
            if api_name in self.configs[ConfigType.API_KEYS]:
                self.configs[ConfigType.API_KEYS][api_name]["status"] = "configured" if value else "not_configured"
                self.configs[ConfigType.API_KEYS][api_name]["last_verified"] = time.time() if value else None
            
        return {
            "status": "success",
            "config_type": config_type_str,
            "key": key,
            "value": "********" if config_type == ConfigType.API_KEYS and keys[-1] == "api_key" else value
        }
    
    def _handle_config_list(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理列出配置請求"""
        config_type_str = data.get("config_type", "")
        
        if not config_type_str:
            # 列出所有配置類型
            return {
                "status": "success",
                "config_types": [ct.value for ct in ConfigType]
            }
            
        try:
            config_type = ConfigType(config_type_str)
        except ValueError:
            return {
                "status": "error",
                "message": f"無效的配置類型: {config_type_str}",
                "error_code": "INVALID_CONFIG_TYPE"
            }
            
        # 獲取配置
        config = self.configs.get(config_type, {})
        
        # 如果是API密鑰，不返回實際值
        if config_type == ConfigType.API_KEYS:
            masked_config = {}
            for api_name, api_config in config.items():
                masked_config[api_name] = api_config.copy()
                if "api_key" in masked_config[api_name] and masked_config[api_name]["api_key"]:
                    masked_config[api_name]["api_key"] = "********"
            config = masked_config
            
        return {
            "status": "success",
            "config_type": config_type_str,
            "config": config
        }
    
    def _handle_api_key_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理檢查API密鑰請求"""
        api_name = data.get("api_name", "")
        
        if not api_name:
            return {
                "status": "error",
                "message": "缺少必要參數: api_name",
                "error_code": "MISSING_PARAMETER"
            }
            
        # 檢查API是否存在
        if api_name not in self.configs[ConfigType.API_KEYS]:
            return {
                "status": "error",
                "message": f"無效的API名稱: {api_name}",
                "error_code": "INVALID_API_NAME"
            }
            
        # 獲取API配置
        api_config = self.configs[ConfigType.API_KEYS][api_name]
        
        # 檢查API密鑰是否配置
        if not api_config.get("api_key"):
            return {
                "status": "success",
                "api_name": api_name,
                "configured": False,
                "status": "not_configured"
            }
            
        # 模擬API密鑰驗證
        # 在實際應用中，應該調用API進行驗證
        is_valid = True
        
        # 更新API配置
        api_config["status"] = "valid" if is_valid else "invalid"
        api_config["last_verified"] = time.time()
        
        return {
            "status": "success",
            "api_name": api_name,
            "configured": True,
            "valid": is_valid,
            "status": api_config["status"],
            "last_verified": api_config["last_verified"]
        }
    
    def _handle_api_key_set(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理設置API密鑰請求"""
        api_name = data.get("api_name", "")
        api_key = data.get("api_key", "")
        
        if not api_name:
            return {
                "status": "error",
                "message": "缺少必要參數: api_name",
                "error_code": "MISSING_PARAMETER"
            }
            
        if not api_key:
            return {
                "status": "error",
                "message": "缺少必要參數: api_key",
                "error_code": "MISSING_PARAMETER"
            }
            
        # 檢查API是否存在
        if api_name not in self.configs[ConfigType.API_KEYS]:
            # 創建新的API配置
            self.configs[ConfigType.API_KEYS][api_name] = {
                "api_key": "",
                "status": "not_configured",
                "last_verified": None,
                "usage_count": 0
            }
            
        # 設置API密鑰
        self.configs[ConfigType.API_KEYS][api_name]["api_key"] = api_key
        self.configs[ConfigType.API_KEYS][api_name]["status"] = "configured"
        
        # 設置環境變量
        os.environ[f"{api_name.upper()}_API_KEY"] = api_key
        
        return {
            "status": "success",
            "api_name": api_name,
            "configured": True
        }
    
    def _handle_load_env(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理加載環境變量請求"""
        env_file = data.get("env_file", ".env")
        
        if not env_file:
            env_file = ".env"
            
        # 檢查文件是否存在
        if not os.path.exists(env_file):
            return {
                "status": "error",
                "message": f"環境變量文件不存在: {env_file}",
                "error_code": "FILE_NOT_FOUND"
            }
            
        # 加載環境變量
        loaded_vars = {}
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 去除引號
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                        
                    os.environ[key] = value
                    loaded_vars[key] = value
                    
            # 重新初始化配置
            self._initialize_configs()
            
            return {
                "status": "success",
                "env_file": env_file,
                "loaded_vars": len(loaded_vars),
                "vars": list(loaded_vars.keys())
            }
            
        except Exception as e:
            logger.error(f"加載環境變量失敗: {str(e)}")
            return {
                "status": "error",
                "message": f"加載環境變量失敗: {str(e)}",
                "error_code": "ENV_LOAD_FAILED"
            }
    
    def _handle_save_env(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """處理保存環境變量請求"""
        env_file = data.get("env_file", ".env")
        
        if not env_file:
            env_file = ".env"
            
        # 保存環境變量
        try:
            # 獲取所有API密鑰
            api_keys = {}
            for api_name, api_config in self.configs[ConfigType.API_KEYS].items():
                if api_config.get("api_key"):
                    api_keys[f"{api_name.upper()}_API_KEY"] = api_config["api_key"]
            
            # 獲取系統配置
            system_config = {}
            for key, value in self.configs[ConfigType.SYSTEM_CONFIG].items():
                system_config[key.upper()] = value
            
            # 獲取測試配置
            test_config = {}
            for key, value in self.configs[ConfigType.TEST_CONFIG].items():
                test_config[key.upper()] = value
            
            # 合併所有配置
            env_vars = {**api_keys, **system_config, **test_config}
            
            # 寫入文件
            with open(env_file, "w") as f:
                f.write("# PowerAutomation API密鑰配置文件\n")
                f.write("# 用於Real API測試\n\n")
                
                # API密鑰
                f.write("# Claude API配置\n")
                f.write(f"CLAUDE_API_KEY={api_keys.get('CLAUDE_API_KEY', '')}\n")
                f.write(f"CLAUDE_MODEL={self.configs[ConfigType.API_CONFIG]['providers']['claude']['model']}\n\n")
                
                f.write("# Gemini API配置\n")
                f.write(f"GEMINI_API_KEY={api_keys.get('GEMINI_API_KEY', '')}\n")
                f.write(f"GEMINI_MODEL={self.configs[ConfigType.API_CONFIG]['providers']['gemini']['model']}\n\n")
                
                f.write("# KiloCode API配置\n")
                f.write(f"KILO_API_KEY={api_keys.get('KILO_API_KEY', '')}\n")
                f.write(f"KILO_CODE_SERVER_URL=https://api.kilocode.ai/v1\n\n")
                
                f.write("# SuperMemory API配置\n")
                f.write(f"SUPERMEMORY_API_KEY={api_keys.get('SUPERMEMORY_API_KEY', '')}\n\n")
                
                f.write("# GitHub配置\n")
                f.write(f"GITHUB_TOKEN={api_keys.get('GITHUB_TOKEN', '')}\n\n")
                
                # 系統配置
                f.write("# 日誌配置\n")
                f.write(f"LOG_LEVEL={system_config.get('LOG_LEVEL', 'INFO')}\n")
                f.write(f"LOG_FILE={system_config.get('LOG_FILE', '')}\n\n")
                
                # 測試配置
                f.write("# 測試配置\n")
                f.write(f"TEST_MODE={test_config.get('TEST_MODE', 'mock')}  # mock或real\n")
                f.write(f"GAIA_TEST_LEVEL={test_config.get('GAIA_TEST_LEVEL', 1)}  # 1, 2, 或3\n")
            
            return {
                "status": "success",
                "env_file": env_file,
                "saved_vars": len(env_vars)
            }
            
        except Exception as e:
            logger.error(f"保存環境變量失敗: {str(e)}")
            return {
                "status": "error",
                "message": f"保存環境變量失敗: {str(e)}",
                "error_code": "ENV_SAVE_FAILED"
            }

