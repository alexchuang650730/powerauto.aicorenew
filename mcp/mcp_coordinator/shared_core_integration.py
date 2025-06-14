# powerauto.aicorenew/mcp/mcp_coordinator/shared_core_integration.py

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 添加shared_core路径以便导入
shared_core_path = "/home/ubuntu/powerauto.ai_0.53/shared_core"
if shared_core_path not in sys.path:
    sys.path.append(shared_core_path)

try:
    from architecture.interaction_log_manager import InteractionLogManager
    from engines.rl_srt_learning_system import RLSRTLearningSystem
    from utils.standardized_logging_system import StandardizedLogger
    SHARED_CORE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Shared core components not available: {e}")
    InteractionLogManager = None
    RLSRTLearningSystem = None
    StandardizedLogger = logging.getLogger
    SHARED_CORE_AVAILABLE = False

class ArchitectureType(Enum):
    """架构类型枚举 - 与shared_core保持一致"""
    ENTERPRISE = "enterprise"
    CONSUMER = "consumer"
    OPENSOURCE = "opensource"

@dataclass
class MCPCoordinatorConfig:
    """MCP协调器配置 - 兼容shared_core的CoreConfig"""
    architecture_type: ArchitectureType = ArchitectureType.CONSUMER
    debug_mode: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    cache_dir: str = "./cache"
    max_workers: int = 4
    timeout_seconds: int = 30
    
    # MCP Coordinator特有配置
    enable_dialog_classification: bool = True
    enable_one_step_suggestion: bool = True
    suggestion_confidence_threshold: float = 0.7
    max_suggestion_steps: int = 5

class SharedCoreIntegrator:
    """
    Shared Core集成器
    负责将mcp_coordinator与shared_core架构无缝集成
    """
    
    def __init__(self, config: MCPCoordinatorConfig):
        self.config = config
        self.logger = StandardizedLogger("SharedCoreIntegrator")
        
        # Shared Core组件
        self.interaction_manager: Optional[InteractionLogManager] = None
        self.learning_system: Optional[RLSRTLearningSystem] = None
        
        # 集成状态
        self.is_integrated = False
        self.available_components = []

    async def initialize_integration(self) -> bool:
        """初始化与shared_core的集成"""
        try:
            self.logger.info("开始初始化Shared Core集成")
            
            if not SHARED_CORE_AVAILABLE:
                self.logger.warning("Shared Core组件不可用，使用独立模式")
                return True
            
            # 初始化InteractionLogManager
            if InteractionLogManager:
                self.interaction_manager = InteractionLogManager()
                if hasattr(self.interaction_manager, 'start'):
                    await self.interaction_manager.start()
                self.available_components.append("interaction_manager")
                self.logger.info("InteractionLogManager集成成功")
            
            # 初始化RLSRTLearningSystem
            if RLSRTLearningSystem:
                self.learning_system = RLSRTLearningSystem()
                if hasattr(self.learning_system, 'start'):
                    await self.learning_system.start()
                self.available_components.append("learning_system")
                self.logger.info("RLSRTLearningSystem集成成功")
            
            self.is_integrated = True
            self.logger.info("Shared Core集成完成", {
                "architecture_type": self.config.architecture_type.value,
                "available_components": self.available_components
            })
            return True
            
        except Exception as e:
            self.logger.error("Shared Core集成失败", {"error": str(e)})
            return False

    async def log_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """记录交互日志到InteractionLogManager"""
        if not self.interaction_manager:
            self.logger.debug("InteractionLogManager不可用，跳过日志记录")
            return False
        
        try:
            # 转换为InteractionLogManager期望的格式
            log_entry = {
                "session_id": interaction_data.get("session_id", "unknown"),
                "timestamp": interaction_data.get("timestamp", ""),
                "interaction_type": interaction_data.get("dialog_type", "unknown"),
                "user_input": interaction_data.get("content", ""),
                "ai_response": interaction_data.get("suggestion", {}),
                "context": interaction_data.get("context", {}),
                "metadata": {
                    "confidence": interaction_data.get("confidence", 0.0),
                    "source": interaction_data.get("source", "mcp_coordinator"),
                    "architecture_type": self.config.architecture_type.value
                }
            }
            
            # 调用InteractionLogManager的记录方法
            if hasattr(self.interaction_manager, 'log_interaction'):
                await self.interaction_manager.log_interaction(log_entry)
            elif hasattr(self.interaction_manager, 'record_interaction'):
                await self.interaction_manager.record_interaction(log_entry)
            else:
                self.logger.warning("InteractionLogManager没有找到记录方法")
                return False
            
            self.logger.debug("交互日志记录成功", {"session_id": log_entry["session_id"]})
            return True
            
        except Exception as e:
            self.logger.error("交互日志记录失败", {"error": str(e)})
            return False

    async def feedback_to_learning_system(self, feedback_data: Dict[str, Any]) -> bool:
        """向RL/SRT学习系统提供反馈"""
        if not self.learning_system:
            self.logger.debug("RLSRTLearningSystem不可用，跳过学习反馈")
            return False
        
        try:
            # 转换为学习系统期望的格式
            learning_data = {
                "experience_type": "dialog_suggestion",
                "state": {
                    "dialog_content": feedback_data.get("dialog_content", ""),
                    "dialog_type": feedback_data.get("dialog_type", ""),
                    "context": feedback_data.get("context", {})
                },
                "action": {
                    "suggestion_type": feedback_data.get("suggestion_type", ""),
                    "primary_action": feedback_data.get("primary_action", ""),
                    "executable_command": feedback_data.get("executable_command", {})
                },
                "reward": feedback_data.get("user_satisfaction", 0.5),  # 默认中性反馈
                "next_state": feedback_data.get("execution_result", {}),
                "metadata": {
                    "confidence": feedback_data.get("confidence", 0.0),
                    "timestamp": feedback_data.get("timestamp", ""),
                    "architecture_type": self.config.architecture_type.value
                }
            }
            
            # 调用学习系统的反馈方法
            if hasattr(self.learning_system, 'add_experience'):
                await self.learning_system.add_experience(learning_data)
            elif hasattr(self.learning_system, 'feedback'):
                await self.learning_system.feedback(learning_data)
            else:
                self.logger.warning("RLSRTLearningSystem没有找到反馈方法")
                return False
            
            self.logger.debug("学习系统反馈成功")
            return True
            
        except Exception as e:
            self.logger.error("学习系统反馈失败", {"error": str(e)})
            return False

    async def get_learning_insights(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """从学习系统获取洞察"""
        if not self.learning_system:
            return {"status": "unavailable", "message": "Learning system not available"}
        
        try:
            # 查询学习系统的洞察
            if hasattr(self.learning_system, 'get_insights'):
                insights = await self.learning_system.get_insights(query_data)
            elif hasattr(self.learning_system, 'query'):
                insights = await self.learning_system.query(query_data)
            else:
                return {"status": "unsupported", "message": "Learning system query not supported"}
            
            return {"status": "success", "insights": insights}
            
        except Exception as e:
            self.logger.error("获取学习洞察失败", {"error": str(e)})
            return {"status": "error", "message": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "shared_core_integration": {
                "status": "healthy" if self.is_integrated else "degraded",
                "available_components": self.available_components,
                "architecture_type": self.config.architecture_type.value
            },
            "components": {}
        }
        
        # 检查InteractionLogManager
        if self.interaction_manager:
            try:
                if hasattr(self.interaction_manager, 'health_check'):
                    health_status["components"]["interaction_manager"] = await self.interaction_manager.health_check()
                else:
                    health_status["components"]["interaction_manager"] = {"status": "unknown"}
            except Exception as e:
                health_status["components"]["interaction_manager"] = {"status": "error", "error": str(e)}
        
        # 检查RLSRTLearningSystem
        if self.learning_system:
            try:
                if hasattr(self.learning_system, 'health_check'):
                    health_status["components"]["learning_system"] = await self.learning_system.health_check()
                else:
                    health_status["components"]["learning_system"] = {"status": "unknown"}
            except Exception as e:
                health_status["components"]["learning_system"] = {"status": "error", "error": str(e)}
        
        return health_status

    async def shutdown(self) -> bool:
        """关闭集成"""
        try:
            self.logger.info("开始关闭Shared Core集成")
            
            # 关闭学习系统
            if self.learning_system and hasattr(self.learning_system, 'stop'):
                await self.learning_system.stop()
            
            # 关闭交互管理器
            if self.interaction_manager and hasattr(self.interaction_manager, 'stop'):
                await self.interaction_manager.stop()
            
            self.is_integrated = False
            self.logger.info("Shared Core集成关闭完成")
            return True
            
        except Exception as e:
            self.logger.error("Shared Core集成关闭失败", {"error": str(e)})
            return False

class EnhancedDialogProcessor:
    """
    增强的对话处理器
    集成shared_core的InteractionLogManager和学习系统
    """
    
    def __init__(self, integrator: SharedCoreIntegrator):
        self.integrator = integrator
        self.logger = StandardizedLogger("EnhancedDialogProcessor")

    async def process_dialog_with_logging(self, dialog_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理对话并记录到shared_core"""
        from .dialog_classifier import OneStepSuggestionGenerator
        
        # 生成建议
        suggestion_generator = OneStepSuggestionGenerator()
        suggestion = suggestion_generator.generate_suggestion(dialog_content, context)
        
        # 准备交互数据
        interaction_data = {
            "session_id": context.get("session_id", "unknown"),
            "timestamp": suggestion.get("timestamp", ""),
            "dialog_type": suggestion.get("dialog_type", ""),
            "content": dialog_content,
            "suggestion": suggestion,
            "context": context,
            "confidence": suggestion.get("confidence", 0.0),
            "source": context.get("source", "unknown")
        }
        
        # 记录到InteractionLogManager
        await self.integrator.log_interaction(interaction_data)
        
        # 如果有执行结果，反馈给学习系统
        if context.get("execution_result"):
            feedback_data = {
                "dialog_content": dialog_content,
                "dialog_type": suggestion.get("dialog_type", ""),
                "context": context,
                "suggestion_type": suggestion.get("suggestion_type", ""),
                "primary_action": suggestion.get("primary_action", ""),
                "executable_command": suggestion.get("executable_command", {}),
                "confidence": suggestion.get("confidence", 0.0),
                "timestamp": suggestion.get("timestamp", ""),
                "execution_result": context.get("execution_result", {}),
                "user_satisfaction": context.get("user_satisfaction", 0.5)
            }
            await self.integrator.feedback_to_learning_system(feedback_data)
        
        return suggestion

    async def get_historical_insights(self, dialog_type: str, limit: int = 10) -> Dict[str, Any]:
        """获取历史对话的洞察"""
        query_data = {
            "query_type": "dialog_insights",
            "dialog_type": dialog_type,
            "limit": limit
        }
        return await self.integrator.get_learning_insights(query_data)

# 工厂函数
def create_shared_core_integrator(architecture_type: str = "consumer", **kwargs) -> SharedCoreIntegrator:
    """创建Shared Core集成器"""
    config = MCPCoordinatorConfig(
        architecture_type=ArchitectureType(architecture_type),
        **kwargs
    )
    return SharedCoreIntegrator(config)

def create_enhanced_dialog_processor(integrator: SharedCoreIntegrator) -> EnhancedDialogProcessor:
    """创建增强对话处理器"""
    return EnhancedDialogProcessor(integrator)

