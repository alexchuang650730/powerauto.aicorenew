# powerauto.aicorenew/mcp/mcp_coordinator/__init__.py

"""
PowerAutomation MCP Coordinator 模块

集成了完整的智能介入和自进化测试工作流系统：
- MCP协调器核心
- 对话分类和智能建议
- PowerAuto测试生成器
- 完整自进化工作流引擎
- Shared Core架构集成
"""

from .mcp_coordinator import MCPCoordinator
from .dialog_classifier import DialogClassifier, DialogType, OneStepSuggestionGenerator
from .powerauto_test_generator import PowerAutoTestGenerator, PowerAutoTestCase, PowerAutoTestType
from .powerauto_workflow_engine import PowerAutoWorkflowEngine, EnhancedTestCase, WorkflowStage
from .shared_core_integration import SharedCoreIntegration
from .test_cases import TestCaseRunner

__version__ = "0.2.0"
__author__ = "PowerAutomation AI"
__description__ = "PowerAutomation智能介入和自进化测试系统"

# 导出主要类
__all__ = [
    # 核心协调器
    "MCPCoordinator",
    
    # 对话分类和建议
    "DialogClassifier", 
    "DialogType", 
    "OneStepSuggestionGenerator",
    
    # 测试生成器
    "PowerAutoTestGenerator", 
    "PowerAutoTestCase", 
    "PowerAutoTestType",
    
    # 完整工作流引擎
    "PowerAutoWorkflowEngine", 
    "EnhancedTestCase", 
    "WorkflowStage",
    
    # 集成组件
    "SharedCoreIntegration",
    "TestCaseRunner",
    
    # 版本信息
    "__version__",
    "__author__", 
    "__description__"
]

# 模块级别的便捷函数
async def create_mcp_coordinator(config: dict = None) -> MCPCoordinator:
    """创建MCP协调器实例"""
    coordinator = MCPCoordinator()
    if config:
        await coordinator.configure(config)
    return coordinator

async def create_workflow_engine(output_dir: str = "powerauto_workflows", 
                               mcp_coordinator: MCPCoordinator = None) -> PowerAutoWorkflowEngine:
    """创建完整工作流引擎实例"""
    if mcp_coordinator is None:
        mcp_coordinator = await create_mcp_coordinator()
    
    return PowerAutoWorkflowEngine(output_dir, mcp_coordinator)

async def execute_smart_intervention(description: str, 
                                   context: dict = None,
                                   output_dir: str = "powerauto_workflows") -> EnhancedTestCase:
    """
    执行智能介入的完整工作流
    
    这是模块的主要入口点，实现：
    文本驱动 → 文本+范本 → executor → test case执行 → 
    视频+可视化可编辑n8n工作流 → 验证节点及节点结果 → 
    修正 → 产生更细更多样化的test cases
    """
    # 创建工作流引擎
    engine = await create_workflow_engine(output_dir)
    
    # 执行完整工作流
    return await engine.execute_complete_workflow(description, context or {})

# 模块初始化日志
import logging
logger = logging.getLogger(__name__)
logger.info(f"PowerAutomation MCP Coordinator v{__version__} 模块已加载")
logger.info("支持功能: 智能介入、自进化测试、n8n工作流、视频集成")

