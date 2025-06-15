#!/usr/bin/env python3
"""
PowerAutomation v0.5.3 共享核心組件庫

提供三種架構共享的核心功能和基礎組件
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# 添加共享核心路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入核心組件
try:
    from architecture.unified_architecture import UnifiedArchitectureCoordinator as UnifiedArchitecture
except ImportError:
    UnifiedArchitecture = None

try:
    from architecture.interaction_log_manager import InteractionLogManager
except ImportError:
    InteractionLogManager = None

try:
    from engines.rl_srt_learning_system import RLSRTLearningSystem
except ImportError:
    RLSRTLearningSystem = None

try:
    from utils.standardized_logging_system import StandardizedLogger
except ImportError:
    StandardizedLogger = logging.getLogger

logger = logging.getLogger(__name__)

class ArchitectureType(Enum):
    """架構類型枚舉"""
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    OPENSOURCE = "opensource"

class ComponentStatus(Enum):
    """組件狀態枚舉"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class CoreConfig:
    """核心配置數據結構"""
    architecture_type: ArchitectureType
    debug_mode: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    cache_dir: str = "./cache"
    max_workers: int = 4
    timeout_seconds: int = 30

class BaseComponent(ABC):
    """基礎組件抽象類"""
    
    def __init__(self, name: str, config: CoreConfig):
        self.name = name
        self.config = config
        self.status = ComponentStatus.INITIALIZING
        self.logger = StandardizedLogger(f"Component.{name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化組件"""
        pass
    
    @abstractmethod
    async def start(self) -> bool:
        """啟動組件"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """停止組件"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        pass
    
    def get_status(self) -> ComponentStatus:
        """獲取組件狀態"""
        return self.status

class SharedCoreManager:
    """共享核心管理器"""
    
    def __init__(self, config: CoreConfig):
        self.config = config
        self.components: Dict[str, BaseComponent] = {}
        self.logger = StandardizedLogger("SharedCoreManager")
        
        # 初始化核心組件
        self._initialize_core_components()
    
    def _initialize_core_components(self):
        """初始化核心組件"""
        try:
            # 統一架構組件
            if UnifiedArchitecture:
                self.unified_architecture = UnifiedArchitecture(
                    config={"architecture_type": self.config.architecture_type.value}
                )
            else:
                self.unified_architecture = None
                self.logger.warning("UnifiedArchitecture 不可用")
            
            # 交互日誌管理器
            if InteractionLogManager:
                self.interaction_manager = InteractionLogManager()
            else:
                self.interaction_manager = None
                self.logger.warning("InteractionLogManager 不可用")
            
            # RL-SRT學習系統
            if RLSRTLearningSystem:
                self.learning_system = RLSRTLearningSystem()
            else:
                self.learning_system = None
                self.logger.warning("RLSRTLearningSystem 不可用")
            
            available_components = [
                name for name, obj in [
                    ("unified_architecture", self.unified_architecture),
                    ("interaction_manager", self.interaction_manager),
                    ("learning_system", self.learning_system)
                ] if obj is not None
            ]
            
            self.logger.info("核心組件初始化完成", {
                "architecture_type": self.config.architecture_type.value,
                "available_components": available_components
            })
            
        except Exception as e:
            self.logger.error("核心組件初始化失敗", {"error": str(e)})
            # 不抛出异常，允许部分组件可用
            pass
    
    async def start_all_components(self) -> bool:
        """啟動所有組件"""
        try:
            self.logger.info("開始啟動所有核心組件")
            
            # 啟動統一架構
            if hasattr(self.unified_architecture, 'start'):
                await self.unified_architecture.start()
            
            # 啟動交互管理器
            if hasattr(self.interaction_manager, 'start'):
                await self.interaction_manager.start()
            
            # 啟動學習系統
            if hasattr(self.learning_system, 'start'):
                await self.learning_system.start()
            
            self.logger.info("所有核心組件啟動完成")
            return True
            
        except Exception as e:
            self.logger.error("組件啟動失敗", {"error": str(e)})
            return False
    
    async def stop_all_components(self) -> bool:
        """停止所有組件"""
        try:
            self.logger.info("開始停止所有核心組件")
            
            # 停止學習系統
            if hasattr(self.learning_system, 'stop'):
                await self.learning_system.stop()
            
            # 停止交互管理器
            if hasattr(self.interaction_manager, 'stop'):
                await self.interaction_manager.stop()
            
            # 停止統一架構
            if hasattr(self.unified_architecture, 'stop'):
                await self.unified_architecture.stop()
            
            self.logger.info("所有核心組件停止完成")
            return True
            
        except Exception as e:
            self.logger.error("組件停止失敗", {"error": str(e)})
            return False
    
    async def health_check_all(self) -> Dict[str, Any]:
        """所有組件健康檢查"""
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            # 檢查統一架構
            if hasattr(self.unified_architecture, 'health_check'):
                health_status["components"]["unified_architecture"] = await self.unified_architecture.health_check()
            else:
                health_status["components"]["unified_architecture"] = {"status": "unknown"}
            
            # 檢查交互管理器
            if hasattr(self.interaction_manager, 'health_check'):
                health_status["components"]["interaction_manager"] = await self.interaction_manager.health_check()
            else:
                health_status["components"]["interaction_manager"] = {"status": "unknown"}
            
            # 檢查學習系統
            if hasattr(self.learning_system, 'health_check'):
                health_status["components"]["learning_system"] = await self.learning_system.health_check()
            else:
                health_status["components"]["learning_system"] = {"status": "unknown"}
            
            # 判斷整體狀態
            unhealthy_components = [
                name for name, status in health_status["components"].items()
                if status.get("status") != "healthy"
            ]
            
            if unhealthy_components:
                health_status["overall_status"] = "degraded"
                health_status["unhealthy_components"] = unhealthy_components
            
        except Exception as e:
            health_status["overall_status"] = "error"
            health_status["error"] = str(e)
        
        return health_status
    
    def get_component(self, name: str) -> Optional[Any]:
        """獲取指定組件"""
        component_map = {
            "unified_architecture": self.unified_architecture,
            "interaction_manager": self.interaction_manager,
            "learning_system": self.learning_system
        }
        return component_map.get(name)
    
    def get_config(self) -> CoreConfig:
        """獲取配置"""
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """更新配置"""
        try:
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            self.logger.info("配置更新成功", {"updated_keys": list(new_config.keys())})
            return True
            
        except Exception as e:
            self.logger.error("配置更新失敗", {"error": str(e)})
            return False

class ArchitectureFactory:
    """架構工廠類"""
    
    @staticmethod
    def create_shared_core(architecture_type: str, **kwargs) -> SharedCoreManager:
        """創建共享核心管理器"""
        try:
            # 創建配置
            config = CoreConfig(
                architecture_type=ArchitectureType(architecture_type),
                **kwargs
            )
            
            # 創建共享核心管理器
            core_manager = SharedCoreManager(config)
            
            return core_manager
            
        except Exception as e:
            logger.error(f"創建共享核心失敗: {e}")
            raise
    
    @staticmethod
    def get_architecture_specific_config(architecture_type: str) -> Dict[str, Any]:
        """獲取架構特定配置"""
        configs = {
            "enterprise": {
                "max_workers": 8,
                "timeout_seconds": 60,
                "log_level": "INFO",
                "features": ["auth", "billing", "monitoring", "analytics"]
            },
            "consumer": {
                "max_workers": 4,
                "timeout_seconds": 30,
                "log_level": "WARNING",
                "features": ["sync", "offline", "notifications"]
            },
            "opensource": {
                "max_workers": 2,
                "timeout_seconds": 15,
                "log_level": "ERROR",
                "features": ["basic", "plugins"]
            }
        }
        
        return configs.get(architecture_type, {})

# 全局共享核心實例
_shared_core_instance: Optional[SharedCoreManager] = None

def get_shared_core() -> Optional[SharedCoreManager]:
    """獲取全局共享核心實例"""
    return _shared_core_instance

def initialize_shared_core(architecture_type: str, **kwargs) -> SharedCoreManager:
    """初始化全局共享核心實例"""
    global _shared_core_instance
    
    if _shared_core_instance is None:
        _shared_core_instance = ArchitectureFactory.create_shared_core(
            architecture_type, **kwargs
        )
    
    return _shared_core_instance

async def main():
    """主函數 - 演示共享核心組件庫"""
    print("🚀 PowerAutomation v0.5.3 共享核心組件庫演示")
    
    try:
        # 測試三種架構
        for arch_type in ["enterprise", "consumer", "opensource"]:
            print(f"\n📋 測試 {arch_type} 架構:")
            
            # 創建共享核心
            core_manager = ArchitectureFactory.create_shared_core(arch_type)
            
            # 啟動組件
            success = await core_manager.start_all_components()
            print(f"   啟動狀態: {'✅ 成功' if success else '❌ 失敗'}")
            
            # 健康檢查
            health = await core_manager.health_check_all()
            print(f"   健康狀態: {health['overall_status']}")
            print(f"   組件數量: {len(health['components'])}")
            
            # 停止組件
            success = await core_manager.stop_all_components()
            print(f"   停止狀態: {'✅ 成功' if success else '❌ 失敗'}")
        
        print("\n✅ 共享核心組件庫演示完成")
        
    except Exception as e:
        print(f"❌ 演示失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())

