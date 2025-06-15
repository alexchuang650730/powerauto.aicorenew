#!/usr/bin/env python3
"""
PowerAutomation 統一配置管理

提供三種架構的統一配置管理功能
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class ArchitectureType(Enum):
    """架構類型"""
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    OPENSOURCE = "opensource"

class DeploymentMode(Enum):
    """部署模式"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class BaseConfig:
    """基礎配置"""
    architecture_type: str
    deployment_mode: str
    debug_mode: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    cache_dir: str = "./cache"
    temp_dir: str = "./temp"
    max_workers: int = 4
    timeout_seconds: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ServerConfig:
    """服務器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    ssl_enabled: bool = False
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    cors_enabled: bool = True
    cors_origins: List[str] = None
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class DatabaseConfig:
    """數據庫配置"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "powerautomation"
    username: str = ""
    password: str = ""
    connection_pool_size: int = 10
    connection_timeout: int = 30

@dataclass
class SecurityConfig:
    """安全配置"""
    jwt_secret_key: str = ""
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    max_login_attempts: int = 5
    session_timeout_minutes: int = 60
    encryption_key: str = ""

@dataclass
class FeatureConfig:
    """功能配置"""
    auth_enabled: bool = True
    billing_enabled: bool = False
    monitoring_enabled: bool = True
    analytics_enabled: bool = False
    sync_enabled: bool = True
    offline_enabled: bool = False
    plugins_enabled: bool = True

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self._configs: Dict[str, Any] = {}
        self._load_default_configs()
    
    def _load_default_configs(self):
        """加載默認配置"""
        # 企業級配置
        self._configs["enterprise"] = {
            "base": BaseConfig(
                architecture_type="enterprise",
                deployment_mode="production",
                max_workers=8,
                timeout_seconds=60,
                log_level="INFO"
            ),
            "server": ServerConfig(
                port=8000,
                ssl_enabled=True,
                cors_origins=["https://app.powerautomation.com"]
            ),
            "database": DatabaseConfig(
                type="postgresql",
                connection_pool_size=20
            ),
            "security": SecurityConfig(
                jwt_expiration_hours=8,
                password_min_length=12,
                max_login_attempts=3
            ),
            "features": FeatureConfig(
                auth_enabled=True,
                billing_enabled=True,
                monitoring_enabled=True,
                analytics_enabled=True
            )
        }
        
        # 消費級配置
        self._configs["consumer"] = {
            "base": BaseConfig(
                architecture_type="consumer",
                deployment_mode="production",
                max_workers=4,
                timeout_seconds=30,
                log_level="WARNING"
            ),
            "server": ServerConfig(
                port=8001,
                ssl_enabled=False,
                cors_origins=["http://localhost:3000"]
            ),
            "database": DatabaseConfig(
                type="sqlite",
                database="consumer.db"
            ),
            "security": SecurityConfig(
                jwt_expiration_hours=24,
                password_min_length=8,
                max_login_attempts=5
            ),
            "features": FeatureConfig(
                auth_enabled=True,
                billing_enabled=False,
                monitoring_enabled=False,
                analytics_enabled=False,
                sync_enabled=True,
                offline_enabled=True
            )
        }
        
        # 開源配置
        self._configs["opensource"] = {
            "base": BaseConfig(
                architecture_type="opensource",
                deployment_mode="development",
                max_workers=2,
                timeout_seconds=15,
                log_level="ERROR"
            ),
            "server": ServerConfig(
                port=8002,
                ssl_enabled=False,
                cors_origins=["*"]
            ),
            "database": DatabaseConfig(
                type="sqlite",
                database="opensource.db"
            ),
            "security": SecurityConfig(
                jwt_expiration_hours=168,  # 7 days
                password_min_length=6,
                max_login_attempts=10
            ),
            "features": FeatureConfig(
                auth_enabled=False,
                billing_enabled=False,
                monitoring_enabled=False,
                analytics_enabled=False,
                plugins_enabled=True
            )
        }
    
    def get_config(self, architecture_type: str, config_type: str = "base") -> Any:
        """獲取配置"""
        if architecture_type not in self._configs:
            raise ValueError(f"不支持的架構類型: {architecture_type}")
        
        arch_config = self._configs[architecture_type]
        if config_type not in arch_config:
            raise ValueError(f"不支持的配置類型: {config_type}")
        
        return arch_config[config_type]
    
    def get_all_config(self, architecture_type: str) -> Dict[str, Any]:
        """獲取所有配置"""
        if architecture_type not in self._configs:
            raise ValueError(f"不支持的架構類型: {architecture_type}")
        
        return self._configs[architecture_type]
    
    def update_config(self, architecture_type: str, config_type: str, updates: Dict[str, Any]):
        """更新配置"""
        config = self.get_config(architecture_type, config_type)
        
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    def save_config_to_file(self, architecture_type: str, file_format: str = "yaml"):
        """保存配置到文件"""
        config = self.get_all_config(architecture_type)
        
        # 轉換為可序列化的字典
        serializable_config = {}
        for config_type, config_obj in config.items():
            if hasattr(config_obj, 'to_dict'):
                serializable_config[config_type] = config_obj.to_dict()
            else:
                serializable_config[config_type] = asdict(config_obj)
        
        # 保存文件
        if file_format == "yaml":
            file_path = self.config_dir / f"{architecture_type}_config.yaml"
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(serializable_config, f, default_flow_style=False, allow_unicode=True)
        elif file_format == "json":
            file_path = self.config_dir / f"{architecture_type}_config.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")
        
        return str(file_path)
    
    def load_config_from_file(self, file_path: str) -> Dict[str, Any]:
        """從文件加載配置"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        if file_path.suffix == ".yaml" or file_path.suffix == ".yml":
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        elif file_path.suffix == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
    
    def create_environment_config(self, architecture_type: str, deployment_mode: str) -> Dict[str, str]:
        """創建環境變量配置"""
        config = self.get_all_config(architecture_type)
        
        env_vars = {}
        
        # 基礎配置
        base_config = config["base"]
        env_vars.update({
            "POWERAUTO_ARCHITECTURE_TYPE": base_config.architecture_type,
            "POWERAUTO_DEPLOYMENT_MODE": deployment_mode,
            "POWERAUTO_DEBUG_MODE": str(base_config.debug_mode),
            "POWERAUTO_LOG_LEVEL": base_config.log_level,
            "POWERAUTO_DATA_DIR": base_config.data_dir,
            "POWERAUTO_MAX_WORKERS": str(base_config.max_workers)
        })
        
        # 服務器配置
        server_config = config["server"]
        env_vars.update({
            "POWERAUTO_SERVER_HOST": server_config.host,
            "POWERAUTO_SERVER_PORT": str(server_config.port),
            "POWERAUTO_SSL_ENABLED": str(server_config.ssl_enabled)
        })
        
        # 數據庫配置
        db_config = config["database"]
        env_vars.update({
            "POWERAUTO_DB_TYPE": db_config.type,
            "POWERAUTO_DB_HOST": db_config.host,
            "POWERAUTO_DB_PORT": str(db_config.port),
            "POWERAUTO_DB_NAME": db_config.database
        })
        
        return env_vars
    
    def get_supported_architectures(self) -> List[str]:
        """獲取支持的架構類型"""
        return list(self._configs.keys())
    
    def validate_config(self, architecture_type: str) -> Dict[str, Any]:
        """驗證配置"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            config = self.get_all_config(architecture_type)
            
            # 驗證基礎配置
            base_config = config["base"]
            if base_config.max_workers <= 0:
                validation_result["errors"].append("max_workers 必須大於 0")
            
            if base_config.timeout_seconds <= 0:
                validation_result["errors"].append("timeout_seconds 必須大於 0")
            
            # 驗證服務器配置
            server_config = config["server"]
            if not (1 <= server_config.port <= 65535):
                validation_result["errors"].append("端口號必須在 1-65535 範圍內")
            
            if server_config.ssl_enabled and not server_config.ssl_cert_path:
                validation_result["errors"].append("啟用 SSL 時必須提供證書路徑")
            
            # 驗證安全配置
            security_config = config["security"]
            if security_config.password_min_length < 6:
                validation_result["warnings"].append("密碼最小長度建議至少 6 位")
            
            if validation_result["errors"]:
                validation_result["valid"] = False
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"配置驗證異常: {str(e)}")
        
        return validation_result

# 全局配置管理器實例
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """獲取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config(architecture_type: str, config_type: str = "base") -> Any:
    """快捷獲取配置"""
    return get_config_manager().get_config(architecture_type, config_type)

def main():
    """主函數 - 演示配置管理"""
    print("🚀 PowerAutomation 統一配置管理演示")
    
    config_manager = ConfigManager()
    
    # 測試三種架構配置
    for arch_type in ["enterprise", "consumer", "opensource"]:
        print(f"\n📋 {arch_type} 架構配置:")
        
        # 獲取基礎配置
        base_config = config_manager.get_config(arch_type, "base")
        print(f"   最大工作線程: {base_config.max_workers}")
        print(f"   超時時間: {base_config.timeout_seconds}s")
        print(f"   日誌級別: {base_config.log_level}")
        
        # 獲取功能配置
        feature_config = config_manager.get_config(arch_type, "features")
        enabled_features = [
            feature for feature, enabled in asdict(feature_config).items()
            if enabled
        ]
        print(f"   啟用功能: {', '.join(enabled_features)}")
        
        # 驗證配置
        validation = config_manager.validate_config(arch_type)
        print(f"   配置驗證: {'✅ 通過' if validation['valid'] else '❌ 失敗'}")
        
        # 保存配置文件
        config_file = config_manager.save_config_to_file(arch_type, "yaml")
        print(f"   配置文件: {config_file}")
    
    print("\n✅ 配置管理演示完成")

if __name__ == "__main__":
    main()

