# powerauto.aicorenew/mcp/mcp_coordinator/__init__.py

"""
PowerAutomation MCP Coordinator
智能介入系统的核心协调器模块

提供智能编辑器和Manus的一步直达建议功能
集成shared_core架构，实现"思考-观察确认-动作"三分类对话处理
"""

from .mcp_coordinator import MCPCoordinator
from .enhanced_mcp_coordinator import EnhancedMCPCoordinator
from .dialog_classifier import DialogClassifier, OneStepSuggestionGenerator, DialogType
from .shared_core_integration import (
    SharedCoreIntegrator, 
    EnhancedDialogProcessor,
    create_shared_core_integrator,
    create_enhanced_dialog_processor
)
from .test_cases import TestCaseRunner

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"

# 主要导出类
__all__ = [
    # 核心协调器
    "MCPCoordinator",
    "EnhancedMCPCoordinator",
    
    # 对话处理
    "DialogClassifier", 
    "OneStepSuggestionGenerator",
    "DialogType",
    
    # Shared Core集成
    "SharedCoreIntegrator",
    "EnhancedDialogProcessor",
    "create_shared_core_integrator",
    "create_enhanced_dialog_processor",
    
    # 测试工具
    "TestCaseRunner"
]

# 便捷工厂函数
def create_coordinator(architecture_type: str = "consumer", enhanced: bool = True):
    """
    创建MCP协调器实例
    
    Args:
        architecture_type: 架构类型 ("enterprise", "consumer", "opensource")
        enhanced: 是否使用增强版本(集成shared_core)
        
    Returns:
        MCPCoordinator或EnhancedMCPCoordinator实例
    """
    if enhanced:
        return EnhancedMCPCoordinator(architecture_type)
    else:
        return MCPCoordinator()

def create_test_runner(architecture_type: str = "consumer"):
    """
    创建测试运行器实例
    
    Args:
        architecture_type: 架构类型
        
    Returns:
        TestCaseRunner实例
    """
    return TestCaseRunner(architecture_type)

# 模块信息
MODULE_INFO = {
    "name": "mcp_coordinator",
    "version": __version__,
    "description": "PowerAutomation智能介入系统核心协调器",
    "features": [
        "智能对话分类(思考-观察确认-动作)",
        "一步直达建议生成",
        "智能编辑器集成",
        "Manus平台集成", 
        "Shared Core架构集成",
        "性能统计和健康检查",
        "自动化测试套件"
    ],
    "supported_architectures": ["enterprise", "consumer", "opensource"],
    "dependencies": {
        "required": ["asyncio", "logging", "typing"],
        "optional": ["shared_core", "interaction_log_manager", "rl_srt_learning_system"]
    }
}

