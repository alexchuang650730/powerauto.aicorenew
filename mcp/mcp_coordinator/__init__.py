"""
PowerAutomation MCP协调器包

提供智能MCP协调、对话分类、工作流引擎等核心功能。
"""

from .mcp_coordinator import MCPCoordinator
from .dialog_classifier import DialogClassifier, DialogType, OneStepSuggestionGenerator
# 移除测试相关导入
# from .powerauto_test_generator import PowerAutoTestGenerator, PowerAutoTestCase, PowerAutoTestType
from .powerauto_workflow_engine import PowerAutoWorkflowEngine, EnhancedTestCase, WorkflowStage
from .shared_core_integration import SharedCoreIntegration
# 移除测试相关导入
# from .test_cases import TestCaseRunner

__version__ = "0.2.0"
__author__ = "PowerAutomation AI"
__description__ = "PowerAutomation智能介入和自进化测试系统"

__all__ = [
    "MCPCoordinator",
    "DialogClassifier", 
    "DialogType",
    "OneStepSuggestionGenerator",
    "PowerAutoWorkflowEngine",
    "EnhancedTestCase",
    "WorkflowStage",
    "SharedCoreIntegration"
]

