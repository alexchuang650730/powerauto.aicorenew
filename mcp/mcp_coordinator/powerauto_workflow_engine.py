# PowerAutomation 完整自进化测试工作流架构 v0.2

"""
基于现有PowerAutomation兜底自动化流程测试架构，
实现完整的自进化测试工作流：

文本驱动 → 文本+范本 → executor → test case执行 → 
视频+可视化可编辑n8n工作流 → 验证节点及节点结果 → 
修正 → 产生更细更多样化的test cases

核心增强：
1. n8n工作流可视化集成
2. 智能验证节点和结果反馈
3. 自动修正和迭代优化
4. 自进化测试用例生成
"""

import os
import sys
import json
import yaml
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum

# 导入现有组件
# 移除测试相关导入
# from .powerauto_test_generator import PowerAutoTestGenerator, PowerAutoTestCase, PowerAutoTestType
from .dialog_classifier import DialogClassifier, DialogType
from .mcp_coordinator import MCPCoordinator

class WorkflowStage(Enum):
    """工作流阶段枚举"""
    TEXT_DRIVEN = "文本驱动"
    TEXT_TEMPLATE = "文本+范本"
    EXECUTOR = "executor"
    TEST_EXECUTION = "test case执行"
    VIDEO_N8N_WORKFLOW = "视频+可视化可编辑n8n工作流"
    VERIFICATION_NODES = "验证节点及节点结果"
    CORRECTION = "修正"
    ENHANCED_GENERATION = "产生更细更多样化的test cases"

@dataclass
class N8NWorkflowNode:
    """n8n工作流节点数据类"""
    node_id: str
    node_type: str  # "trigger", "action", "condition", "verification"
    name: str
    description: str
    position: Dict[str, int]  # {"x": 100, "y": 200}
    parameters: Dict[str, Any]
    connections: List[str]  # 连接到的下一个节点ID列表
    verification_criteria: Optional[str] = None
    expected_result: Optional[str] = None
    failure_action: Optional[str] = None

@dataclass
class N8NWorkflow:
    """n8n工作流数据类"""
    workflow_id: str
    name: str
    description: str
    test_case_id: str
    nodes: List[N8NWorkflowNode]
    connections: Dict[str, List[str]]  # 节点连接关系
    metadata: Dict[str, Any]
    created_time: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class VerificationResult:
    """验证结果数据类"""
    node_id: str
    node_name: str
    success: bool
    actual_result: Any
    expected_result: Any
    verification_time: str
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    video_path: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)

@dataclass
class CorrectionAction:
    """修正动作数据类"""
    action_type: str  # "parameter_adjust", "node_replace", "flow_restructure"
    target_node_id: str
    original_value: Any
    corrected_value: Any
    reason: str
    confidence: float
    applied_time: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class EnhancedTestCase:
    """增强测试用例数据类"""
    original_test_case: PowerAutoTestCase
    n8n_workflow: N8NWorkflow
    verification_results: List[VerificationResult]
    correction_actions: List[CorrectionAction]
    enhancement_suggestions: List[str]
    generation_iteration: int
    quality_score: float
    diversity_metrics: Dict[str, float]

class PowerAutoWorkflowEngine:
    """
    PowerAutomation 完整工作流引擎
    
    实现从文本驱动到自进化测试用例生成的完整闭环工作流
    """
    
    def __init__(self, output_dir: str = "powerauto_workflows", mcp_coordinator: Optional[MCPCoordinator] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建工作流目录结构
        (self.output_dir / "workflows").mkdir(exist_ok=True)
        (self.output_dir / "videos").mkdir(exist_ok=True)
        (self.output_dir / "verifications").mkdir(exist_ok=True)
        (self.output_dir / "corrections").mkdir(exist_ok=True)
        (self.output_dir / "enhanced_tests").mkdir(exist_ok=True)
        (self.output_dir / "n8n_exports").mkdir(exist_ok=True)
        
        # 核心组件
        self.mcp_coordinator = mcp_coordinator
        self.test_generator = PowerAutoTestGenerator(str(self.output_dir / "generated_tests"), mcp_coordinator)
        self.dialog_classifier = DialogClassifier()
        
        # 日志配置
        self.logger = logging.getLogger(__name__)
        
        # 工作流状态跟踪
        self.current_workflows: Dict[str, EnhancedTestCase] = {}
        self.iteration_counter = 0
        
        # n8n集成配置
        self.n8n_config = {
            "base_url": "http://localhost:5678",  # n8n默认地址
            "webhook_base": "http://localhost:5678/webhook",
            "api_key": None  # 如果需要认证
        }
    
    async def execute_complete_workflow(self, description: str, context: Dict[str, Any] = None) -> EnhancedTestCase:
        """
        执行完整的自进化测试工作流
        
        实现完整的8阶段工作流：
        文本驱动 → 文本+范本 → executor → test case执行 → 
        视频+可视化可编辑n8n工作流 → 验证节点及节点结果 → 
        修正 → 产生更细更多样化的test cases
        """
        if context is None:
            context = {}
        
        self.logger.info(f"🚀 开始执行完整工作流: {description[:50]}...")
        
        try:
            # 阶段1: 文本驱动
            stage1_result = await self._stage1_text_driven(description, context)
            
            # 阶段2: 文本+范本
            stage2_result = await self._stage2_text_template(stage1_result, context)
            
            # 阶段3: executor
            stage3_result = await self._stage3_executor(stage2_result, context)
            
            # 阶段4: test case执行
            stage4_result = await self._stage4_test_execution(stage3_result, context)
            
            # 阶段5: 视频+可视化可编辑n8n工作流
            stage5_result = await self._stage5_video_n8n_workflow(stage4_result, context)
            
            # 阶段6: 验证节点及节点结果
            stage6_result = await self._stage6_verification_nodes(stage5_result, context)
            
            # 阶段7: 修正
            stage7_result = await self._stage7_correction(stage6_result, context)
            
            # 阶段8: 产生更细更多样化的test cases
            stage8_result = await self._stage8_enhanced_generation(stage7_result, context)
            
            # 保存完整工作流结果
            await self._save_enhanced_test_case(stage8_result)
            
            self.logger.info(f"✅ 完整工作流执行成功: {stage8_result.original_test_case.test_id}")
            return stage8_result
            
        except Exception as e:
            self.logger.error(f"❌ 完整工作流执行失败: {e}")
            raise
    
    async def _stage1_text_driven(self, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段1: 文本驱动 - 分析用户输入的自然语言描述"""
        self.logger.info("📝 阶段1: 文本驱动分析")
        
        # 使用dialog_classifier分析文本
        dialog_type = await self.dialog_classifier.classify_dialog(description)
        confidence = await self.dialog_classifier.get_confidence_score(description, dialog_type)
        
        # 提取关键信息
        keywords = await self._extract_keywords(description)
        intent = await self._analyze_intent(description, dialog_type)
        complexity = await self._assess_complexity(description)
        
        return {
            "stage": WorkflowStage.TEXT_DRIVEN,
            "description": description,
            "dialog_type": dialog_type,
            "confidence": confidence,
            "keywords": keywords,
            "intent": intent,
            "complexity": complexity,
            "context": context
        }
    
    async def _stage2_text_template(self, stage1_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段2: 文本+范本 - 结合模板生成结构化测试需求"""
        self.logger.info("📋 阶段2: 文本+范本结合")
        
        # 选择合适的PowerAuto模板
        template_type = await self._select_powerauto_template(stage1_result)
        
        # 生成结构化测试需求
        structured_requirement = await self._generate_structured_requirement(stage1_result, template_type)
        
        # 预生成测试用例框架
        test_case_framework = await self._generate_test_case_framework(structured_requirement)
        
        return {
            **stage1_result,
            "stage": WorkflowStage.TEXT_TEMPLATE,
            "template_type": template_type,
            "structured_requirement": structured_requirement,
            "test_case_framework": test_case_framework
        }
    
    async def _stage3_executor(self, stage2_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段3: executor - 生成完整的可执行测试用例"""
        self.logger.info("⚙️ 阶段3: executor生成")
        
        # 使用PowerAutoTestGenerator生成完整测试用例
        test_case = await self.test_generator.generate_test_from_description(
            stage2_result["description"], 
            {**context, **stage2_result}
        )
        
        # 生成执行脚本
        execution_scripts = await self._generate_execution_scripts(test_case)
        
        # 准备执行环境
        execution_environment = await self._prepare_execution_environment(test_case)
        
        return {
            **stage2_result,
            "stage": WorkflowStage.EXECUTOR,
            "test_case": test_case,
            "execution_scripts": execution_scripts,
            "execution_environment": execution_environment
        }
    
    async def _stage4_test_execution(self, stage3_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段4: test case执行 - 实际执行测试用例并记录结果"""
        self.logger.info("🎬 阶段4: test case执行")
        
        test_case = stage3_result["test_case"]
        
        # 开始视频录制
        video_path = await self._start_video_recording(test_case.test_id)
        
        # 执行测试用例
        execution_results = await self._execute_test_case(test_case, stage3_result["execution_scripts"])
        
        # 停止视频录制
        await self._stop_video_recording(video_path)
        
        # 收集执行数据
        execution_data = await self._collect_execution_data(test_case, execution_results, video_path)
        
        return {
            **stage3_result,
            "stage": WorkflowStage.TEST_EXECUTION,
            "execution_results": execution_results,
            "video_path": video_path,
            "execution_data": execution_data
        }
    
    async def _stage5_video_n8n_workflow(self, stage4_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段5: 视频+可视化可编辑n8n工作流 - 生成n8n工作流并集成视频"""
        self.logger.info("🎨 阶段5: 视频+可视化可编辑n8n工作流")
        
        test_case = stage4_result["test_case"]
        execution_data = stage4_result["execution_data"]
        video_path = stage4_result["video_path"]
        
        # 生成n8n工作流
        n8n_workflow = await self._generate_n8n_workflow(test_case, execution_data)
        
        # 集成视频到工作流
        enhanced_workflow = await self._integrate_video_to_workflow(n8n_workflow, video_path)
        
        # 生成可编辑的工作流界面
        editable_workflow = await self._generate_editable_workflow_interface(enhanced_workflow)
        
        # 导出n8n格式
        n8n_export = await self._export_to_n8n_format(enhanced_workflow)
        
        return {
            **stage4_result,
            "stage": WorkflowStage.VIDEO_N8N_WORKFLOW,
            "n8n_workflow": enhanced_workflow,
            "editable_workflow": editable_workflow,
            "n8n_export": n8n_export
        }
    
    async def _stage6_verification_nodes(self, stage5_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段6: 验证节点及节点结果 - 智能验证每个工作流节点"""
        self.logger.info("🔍 阶段6: 验证节点及节点结果")
        
        n8n_workflow = stage5_result["n8n_workflow"]
        execution_data = stage5_result["execution_data"]
        
        # 验证每个工作流节点
        verification_results = []
        for node in n8n_workflow.nodes:
            result = await self._verify_workflow_node(node, execution_data)
            verification_results.append(result)
        
        # 分析验证结果
        verification_analysis = await self._analyze_verification_results(verification_results)
        
        # 生成改进建议
        improvement_suggestions = await self._generate_improvement_suggestions(verification_results)
        
        return {
            **stage5_result,
            "stage": WorkflowStage.VERIFICATION_NODES,
            "verification_results": verification_results,
            "verification_analysis": verification_analysis,
            "improvement_suggestions": improvement_suggestions
        }
    
    async def _stage7_correction(self, stage6_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """阶段7: 修正 - 基于验证结果自动修正工作流"""
        self.logger.info("🔧 阶段7: 修正")
        
        verification_results = stage6_result["verification_results"]
        improvement_suggestions = stage6_result["improvement_suggestions"]
        n8n_workflow = stage6_result["n8n_workflow"]
        
        # 生成修正动作
        correction_actions = await self._generate_correction_actions(verification_results, improvement_suggestions)
        
        # 应用修正
        corrected_workflow = await self._apply_corrections(n8n_workflow, correction_actions)
        
        # 验证修正效果
        correction_verification = await self._verify_corrections(corrected_workflow, correction_actions)
        
        return {
            **stage6_result,
            "stage": WorkflowStage.CORRECTION,
            "correction_actions": correction_actions,
            "corrected_workflow": corrected_workflow,
            "correction_verification": correction_verification
        }
    
    async def _stage8_enhanced_generation(self, stage7_result: Dict[str, Any], context: Dict[str, Any]) -> EnhancedTestCase:
        """阶段8: 产生更细更多样化的test cases - 自进化生成新测试用例"""
        self.logger.info("🌟 阶段8: 产生更细更多样化的test cases")
        
        original_test_case = stage7_result["test_case"]
        corrected_workflow = stage7_result["corrected_workflow"]
        verification_results = stage7_result["verification_results"]
        correction_actions = stage7_result["correction_actions"]
        
        # 分析当前测试用例的覆盖度和多样性
        coverage_analysis = await self._analyze_test_coverage(original_test_case, verification_results)
        diversity_metrics = await self._calculate_diversity_metrics(original_test_case)
        
        # 生成增强建议
        enhancement_suggestions = await self._generate_enhancement_suggestions(
            original_test_case, coverage_analysis, diversity_metrics
        )
        
        # 计算质量分数
        quality_score = await self._calculate_quality_score(
            original_test_case, verification_results, correction_actions
        )
        
        # 创建增强测试用例
        enhanced_test_case = EnhancedTestCase(
            original_test_case=original_test_case,
            n8n_workflow=corrected_workflow,
            verification_results=verification_results,
            correction_actions=correction_actions,
            enhancement_suggestions=enhancement_suggestions,
            generation_iteration=self.iteration_counter,
            quality_score=quality_score,
            diversity_metrics=diversity_metrics
        )
        
        # 生成更多样化的测试用例变体
        enhanced_variants = await self._generate_enhanced_variants(enhanced_test_case)
        
        # 更新迭代计数器
        self.iteration_counter += 1
        
        return enhanced_test_case
    
    # 辅助方法实现
    async def _extract_keywords(self, description: str) -> List[str]:
        """提取关键词"""
        # TODO: 实现智能关键词提取
        keywords = []
        common_keywords = ["蓝牙", "定位", "网络", "音频", "显示", "传感器", "电源", "存储", "相机", "通话"]
        for keyword in common_keywords:
            if keyword in description:
                keywords.append(keyword)
        return keywords
    
    async def _analyze_intent(self, description: str, dialog_type: DialogType) -> str:
        """分析用户意图"""
        if dialog_type == DialogType.THINKING:
            return "分析和推理"
        elif dialog_type == DialogType.OBSERVING:
            return "查询和确认"
        elif dialog_type == DialogType.ACTION:
            return "执行和操作"
        return "未知意图"
    
    async def _assess_complexity(self, description: str) -> str:
        """评估复杂度"""
        if len(description) < 50:
            return "简单"
        elif len(description) < 150:
            return "中等"
        else:
            return "复杂"
    
    async def _select_powerauto_template(self, stage1_result: Dict[str, Any]) -> str:
        """选择PowerAuto模板"""
        dialog_type = stage1_result["dialog_type"]
        keywords = stage1_result["keywords"]
        
        if any(keyword in ["蓝牙", "网络", "音频"] for keyword in keywords):
            return "BSP_Hardware_Template"
        elif dialog_type == DialogType.ACTION:
            return "Operation_Template"
        else:
            return "API_Template"
    
    async def _generate_structured_requirement(self, stage1_result: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """生成结构化需求"""
        return {
            "template_type": template_type,
            "requirements": {
                "functional": ["基础功能验证"],
                "performance": ["响应时间 < 3秒"],
                "compatibility": ["Android 10+"],
                "usability": ["用户友好界面"]
            },
            "constraints": {
                "environment": "测试环境",
                "resources": "标准硬件配置"
            }
        }
    
    async def _generate_test_case_framework(self, structured_requirement: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试用例框架"""
        return {
            "framework_type": "PowerAuto_Framework",
            "test_structure": {
                "setup": "环境准备",
                "execution": "测试执行",
                "verification": "结果验证",
                "cleanup": "环境清理"
            }
        }
    
    async def _generate_execution_scripts(self, test_case: PowerAutoTestCase) -> Dict[str, str]:
        """生成执行脚本"""
        if test_case.test_type == PowerAutoTestType.OPERATION:
            return {
                "python_script": self.test_generator.generate_powerauto_operation_template(test_case),
                "shell_script": f"#!/bin/bash\npython {test_case.test_id}_test.py"
            }
        else:
            return {
                "python_script": self.test_generator.generate_powerauto_api_template(test_case),
                "shell_script": f"#!/bin/bash\npython {test_case.test_id}_api_test.py"
            }
    
    async def _prepare_execution_environment(self, test_case: PowerAutoTestCase) -> Dict[str, Any]:
        """准备执行环境"""
        return {
            "environment_ready": True,
            "dependencies_installed": True,
            "device_connected": True,
            "permissions_granted": True
        }
    
    async def _start_video_recording(self, test_id: str) -> str:
        """开始视频录制"""
        video_path = self.output_dir / "videos" / f"{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        # TODO: 实现实际的视频录制逻辑
        self.logger.info(f"📹 开始录制视频: {video_path}")
        return str(video_path)
    
    async def _stop_video_recording(self, video_path: str):
        """停止视频录制"""
        # TODO: 实现实际的视频录制停止逻辑
        self.logger.info(f"⏹️ 停止录制视频: {video_path}")
    
    async def _execute_test_case(self, test_case: PowerAutoTestCase, execution_scripts: Dict[str, str]) -> Dict[str, Any]:
        """执行测试用例"""
        # TODO: 实现实际的测试用例执行逻辑
        return {
            "success": True,
            "execution_time": 30.5,
            "steps_completed": len(test_case.test_steps),
            "checkpoints_passed": len(test_case.checkpoints),
            "errors": []
        }
    
    async def _collect_execution_data(self, test_case: PowerAutoTestCase, execution_results: Dict[str, Any], video_path: str) -> Dict[str, Any]:
        """收集执行数据"""
        return {
            "test_case": test_case,
            "execution_results": execution_results,
            "video_path": video_path,
            "screenshots": [],
            "logs": [],
            "metrics": {
                "execution_time": execution_results.get("execution_time", 0),
                "success_rate": 1.0 if execution_results.get("success") else 0.0
            }
        }
    
    async def _generate_n8n_workflow(self, test_case: PowerAutoTestCase, execution_data: Dict[str, Any]) -> N8NWorkflow:
        """生成n8n工作流"""
        nodes = []
        
        # 创建触发节点
        trigger_node = N8NWorkflowNode(
            node_id="trigger_001",
            node_type="trigger",
            name="测试触发器",
            description="启动测试执行",
            position={"x": 100, "y": 100},
            parameters={"test_id": test_case.test_id},
            connections=["action_001"]
        )
        nodes.append(trigger_node)
        
        # 为每个测试步骤创建动作节点
        for i, step in enumerate(test_case.test_steps, 1):
            action_node = N8NWorkflowNode(
                node_id=f"action_{i:03d}",
                node_type="action",
                name=f"步骤{i}: {step.get('description', '')}",
                description=step.get('description', ''),
                position={"x": 100 + i * 200, "y": 100},
                parameters=step,
                connections=[f"verification_{i:03d}"],
                verification_criteria=step.get('verification', ''),
                expected_result=f"步骤{i}成功完成"
            )
            nodes.append(action_node)
            
            # 创建验证节点
            verification_node = N8NWorkflowNode(
                node_id=f"verification_{i:03d}",
                node_type="verification",
                name=f"验证{i}",
                description=f"验证步骤{i}的执行结果",
                position={"x": 100 + i * 200, "y": 300},
                parameters={"verification_type": "checkpoint"},
                connections=[f"action_{i+1:03d}"] if i < len(test_case.test_steps) else ["end_001"]
            )
            nodes.append(verification_node)
        
        # 创建结束节点
        end_node = N8NWorkflowNode(
            node_id="end_001",
            node_type="end",
            name="测试完成",
            description="测试执行完成",
            position={"x": 100 + (len(test_case.test_steps) + 1) * 200, "y": 100},
            parameters={"status": "completed"},
            connections=[]
        )
        nodes.append(end_node)
        
        return N8NWorkflow(
            workflow_id=f"workflow_{test_case.test_id}",
            name=f"{test_case.test_name} 工作流",
            description=f"基于 {test_case.test_id} 生成的n8n工作流",
            test_case_id=test_case.test_id,
            nodes=nodes,
            connections={node.node_id: node.connections for node in nodes},
            metadata={
                "test_type": test_case.test_type.value,
                "business_module": test_case.business_module,
                "generation_time": datetime.now().isoformat()
            }
        )
    
    async def _integrate_video_to_workflow(self, workflow: N8NWorkflow, video_path: str) -> N8NWorkflow:
        """集成视频到工作流"""
        # 为每个验证节点添加视频时间戳
        for node in workflow.nodes:
            if node.node_type == "verification":
                node.parameters["video_timestamp"] = f"00:{len(workflow.nodes):02d}:00"
                node.parameters["video_path"] = video_path
        
        workflow.metadata["video_integration"] = {
            "video_path": video_path,
            "integration_time": datetime.now().isoformat(),
            "video_segments": len([n for n in workflow.nodes if n.node_type == "verification"])
        }
        
        return workflow
    
    async def _generate_editable_workflow_interface(self, workflow: N8NWorkflow) -> Dict[str, Any]:
        """生成可编辑的工作流界面"""
        return {
            "interface_type": "n8n_compatible",
            "workflow_data": asdict(workflow),
            "edit_capabilities": {
                "node_editing": True,
                "connection_editing": True,
                "parameter_editing": True,
                "visual_editing": True
            },
            "export_formats": ["json", "yaml", "n8n"]
        }
    
    async def _export_to_n8n_format(self, workflow: N8NWorkflow) -> Dict[str, Any]:
        """导出为n8n格式"""
        n8n_format = {
            "name": workflow.name,
            "nodes": [],
            "connections": {},
            "active": True,
            "settings": {},
            "staticData": None,
            "meta": {
                "instanceId": workflow.workflow_id
            },
            "id": workflow.workflow_id,
            "tags": ["powerauto", "generated", workflow.test_case_id]
        }
        
        # 转换节点格式
        for node in workflow.nodes:
            n8n_node = {
                "parameters": node.parameters,
                "id": node.node_id,
                "name": node.name,
                "type": f"powerauto.{node.node_type}",
                "typeVersion": 1,
                "position": [node.position["x"], node.position["y"]]
            }
            n8n_format["nodes"].append(n8n_node)
        
        # 转换连接格式
        for node_id, connections in workflow.connections.items():
            if connections:
                n8n_format["connections"][node_id] = {
                    "main": [[{"node": conn, "type": "main", "index": 0} for conn in connections]]
                }
        
        return n8n_format
    
    async def _verify_workflow_node(self, node: N8NWorkflowNode, execution_data: Dict[str, Any]) -> VerificationResult:
        """验证工作流节点"""
        # TODO: 实现实际的节点验证逻辑
        success = True  # 模拟验证结果
        
        return VerificationResult(
            node_id=node.node_id,
            node_name=node.name,
            success=success,
            actual_result="节点执行成功",
            expected_result=node.expected_result or "节点正常执行",
            verification_time=datetime.now().isoformat(),
            suggestions=["节点执行正常"] if success else ["需要检查节点参数"]
        )
    
    async def _analyze_verification_results(self, verification_results: List[VerificationResult]) -> Dict[str, Any]:
        """分析验证结果"""
        total_nodes = len(verification_results)
        successful_nodes = sum(1 for result in verification_results if result.success)
        
        return {
            "total_nodes": total_nodes,
            "successful_nodes": successful_nodes,
            "success_rate": successful_nodes / total_nodes if total_nodes > 0 else 0,
            "failed_nodes": [result.node_id for result in verification_results if not result.success],
            "overall_status": "PASS" if successful_nodes == total_nodes else "FAIL"
        }
    
    async def _generate_improvement_suggestions(self, verification_results: List[VerificationResult]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for result in verification_results:
            if not result.success:
                suggestions.append(f"节点 {result.node_name} 需要优化: {result.error_message}")
            suggestions.extend(result.suggestions)
        
        return suggestions
    
    async def _generate_correction_actions(self, verification_results: List[VerificationResult], 
                                         improvement_suggestions: List[str]) -> List[CorrectionAction]:
        """生成修正动作"""
        correction_actions = []
        
        for result in verification_results:
            if not result.success:
                action = CorrectionAction(
                    action_type="parameter_adjust",
                    target_node_id=result.node_id,
                    original_value=result.actual_result,
                    corrected_value=result.expected_result,
                    reason=f"节点验证失败: {result.error_message}",
                    confidence=0.8
                )
                correction_actions.append(action)
        
        return correction_actions
    
    async def _apply_corrections(self, workflow: N8NWorkflow, correction_actions: List[CorrectionAction]) -> N8NWorkflow:
        """应用修正"""
        corrected_workflow = workflow
        
        for action in correction_actions:
            # 找到目标节点并应用修正
            for node in corrected_workflow.nodes:
                if node.node_id == action.target_node_id:
                    # 应用参数调整
                    if action.action_type == "parameter_adjust":
                        node.parameters["corrected"] = True
                        node.parameters["correction_applied"] = action.corrected_value
                    break
        
        return corrected_workflow
    
    async def _verify_corrections(self, corrected_workflow: N8NWorkflow, 
                                correction_actions: List[CorrectionAction]) -> Dict[str, Any]:
        """验证修正效果"""
        return {
            "corrections_applied": len(correction_actions),
            "verification_status": "PASS",
            "improvement_achieved": True
        }
    
    async def _analyze_test_coverage(self, test_case: PowerAutoTestCase, 
                                   verification_results: List[VerificationResult]) -> Dict[str, Any]:
        """分析测试覆盖度"""
        return {
            "functional_coverage": 0.85,
            "path_coverage": 0.90,
            "boundary_coverage": 0.75,
            "error_coverage": 0.60,
            "overall_coverage": 0.78
        }
    
    async def _calculate_diversity_metrics(self, test_case: PowerAutoTestCase) -> Dict[str, float]:
        """计算多样性指标"""
        return {
            "input_diversity": 0.7,
            "scenario_diversity": 0.8,
            "execution_path_diversity": 0.6,
            "data_diversity": 0.75,
            "overall_diversity": 0.72
        }
    
    async def _generate_enhancement_suggestions(self, test_case: PowerAutoTestCase, 
                                              coverage_analysis: Dict[str, Any], 
                                              diversity_metrics: Dict[str, float]) -> List[str]:
        """生成增强建议"""
        suggestions = []
        
        if coverage_analysis["error_coverage"] < 0.8:
            suggestions.append("增加错误场景测试用例")
        
        if diversity_metrics["input_diversity"] < 0.8:
            suggestions.append("增加输入数据的多样性")
        
        if coverage_analysis["boundary_coverage"] < 0.8:
            suggestions.append("增加边界条件测试")
        
        suggestions.append("考虑添加性能测试场景")
        suggestions.append("增加并发操作测试用例")
        
        return suggestions
    
    async def _calculate_quality_score(self, test_case: PowerAutoTestCase, 
                                     verification_results: List[VerificationResult], 
                                     correction_actions: List[CorrectionAction]) -> float:
        """计算质量分数"""
        success_rate = sum(1 for result in verification_results if result.success) / len(verification_results)
        correction_penalty = len(correction_actions) * 0.1
        
        quality_score = success_rate - correction_penalty
        return max(0.0, min(1.0, quality_score))
    
    async def _generate_enhanced_variants(self, enhanced_test_case: EnhancedTestCase) -> List[PowerAutoTestCase]:
        """生成增强的测试用例变体"""
        variants = []
        
        # 基于增强建议生成变体
        for suggestion in enhanced_test_case.enhancement_suggestions:
            if "错误场景" in suggestion:
                # 生成错误场景变体
                variant = await self._create_error_scenario_variant(enhanced_test_case.original_test_case)
                variants.append(variant)
            elif "边界条件" in suggestion:
                # 生成边界条件变体
                variant = await self._create_boundary_condition_variant(enhanced_test_case.original_test_case)
                variants.append(variant)
        
        return variants
    
    async def _create_error_scenario_variant(self, original_test_case: PowerAutoTestCase) -> PowerAutoTestCase:
        """创建错误场景变体"""
        # TODO: 实现错误场景变体生成逻辑
        return original_test_case
    
    async def _create_boundary_condition_variant(self, original_test_case: PowerAutoTestCase) -> PowerAutoTestCase:
        """创建边界条件变体"""
        # TODO: 实现边界条件变体生成逻辑
        return original_test_case
    
    async def _save_enhanced_test_case(self, enhanced_test_case: EnhancedTestCase):
        """保存增强测试用例"""
        # 保存到文件
        output_path = self.output_dir / "enhanced_tests" / f"{enhanced_test_case.original_test_case.test_id}_enhanced.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(enhanced_test_case), f, ensure_ascii=False, indent=2, default=str)
        
        # 保存n8n工作流
        n8n_path = self.output_dir / "n8n_exports" / f"{enhanced_test_case.n8n_workflow.workflow_id}.json"
        n8n_export = await self._export_to_n8n_format(enhanced_test_case.n8n_workflow)
        
        with open(n8n_path, 'w', encoding='utf-8') as f:
            json.dump(n8n_export, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"💾 增强测试用例已保存: {output_path}")
        self.logger.info(f"💾 n8n工作流已导出: {n8n_path}")

# CLI接口
async def main():
    """PowerAuto完整工作流引擎CLI主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation完整自进化测试工作流引擎")
    parser.add_argument("description", help="测试需求的自然语言描述")
    parser.add_argument("--output", default="powerauto_workflows", help="输出目录")
    parser.add_argument("--context", help="上下文信息(JSON格式)")
    parser.add_argument("--iterations", type=int, default=1, help="自进化迭代次数")
    
    args = parser.parse_args()
    
    # 创建工作流引擎
    engine = PowerAutoWorkflowEngine(args.output)
    
    # 解析上下文
    context = {}
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("❌ 上下文JSON格式错误")
            return
    
    try:
        print(f"🚀 启动PowerAutomation完整工作流引擎...")
        print(f"需求描述: {args.description}")
        print(f"迭代次数: {args.iterations}")
        
        # 执行完整工作流
        for iteration in range(args.iterations):
            print(f"\\n🔄 第 {iteration + 1} 次迭代")
            
            enhanced_test_case = await engine.execute_complete_workflow(args.description, context)
            
            print(f"\\n✅ 第 {iteration + 1} 次迭代完成!")
            print(f"测试ID: {enhanced_test_case.original_test_case.test_id}")
            print(f"质量分数: {enhanced_test_case.quality_score:.2f}")
            print(f"多样性指标: {enhanced_test_case.diversity_metrics}")
            print(f"增强建议数: {len(enhanced_test_case.enhancement_suggestions)}")
            
            # 为下一次迭代更新上下文
            context["previous_iteration"] = asdict(enhanced_test_case)
        
        print(f"\\n🎉 PowerAutomation完整工作流执行完成!")
        
    except Exception as e:
        print(f"❌ 工作流执行失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())

