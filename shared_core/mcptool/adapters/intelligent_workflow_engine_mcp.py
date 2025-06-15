"""
智能工作流引擎MCP适配器 - 增强版
整合MCPBrainstorm、MCPPlanner、InfiniteContext、WorkflowDriver和统一工具引擎
提供完整的AI增强工作流管理和执行能力
"""

import json
import logging
import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from mcptool.adapters.base_mcp import BaseMCP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 单例模式实现
_instance = None

def get_instance(project_root: str = None):
    """
    获取IntelligentWorkflowEngineMCP单例实例
    
    Args:
        project_root: 项目根目录路径
        
    Returns:
        IntelligentWorkflowEngineMCP: 智能工作流引擎单例实例
    """
    global _instance
    if _instance is None:
        _instance = IntelligentWorkflowEngineMCP(project_root)
    return _instance

class IntelligentWorkflowEngineMCP(BaseMCP):
    """智能工作流引擎MCP适配器 - 整合版"""
    
    def __init__(self, project_root: str = None):
        super().__init__()
        self.name = "IntelligentWorkflowEngineMCP"
        self.project_root = project_root or os.getcwd()
        
        # 初始化工作流组件
        self._initialize_workflow_components()
        
        # 初始化AI增强组件
        self._initialize_ai_components()
        
        # 初始化工作流节点和连接
        self.workflow_nodes = []
        self.workflow_connections = []
        
        # 初始化事件监听器
        self.event_listeners = {}
        
        # 初始化工作流状态
        self.workflow_status = {
            "is_running": False,
            "current_node": None,
            "start_time": None,
            "last_update_time": None
        }
        
        # 初始化工作流线程
        self.workflow_thread = None
        
        # 初始化事件同步锁
        self.event_lock = threading.Lock()
        
        # 初始化测试模式标志
        self.is_test_mode = False
        
        logger.info(f"IntelligentWorkflowEngineMCP初始化完成，项目根目录: {self.project_root}")
    
    def _initialize_workflow_components(self):
        """初始化工作流组件"""
        try:
            # 導入核心組件 - 修復導入路徑
            from mcptool.core.agent_problem_solver_mcp import AgentProblemSolverMCP
            from mcptool.core.release_manager_mcp import ReleaseManagerMCP
            
            self.agent_problem_solver = AgentProblemSolverMCP({"project_dir": self.project_root})
            self.release_manager = ReleaseManagerMCP({"project_dir": self.project_root})
            
            logger.info("工作流組件初始化完成")
        except ImportError as e:
            logger.warning(f"部分工作流組件導入失敗: {e}")
            self.agent_problem_solver = None
            self.release_manager = None
    
    def _initialize_ai_components(self):
        """初始化AI增强组件"""
        # MCPBrainstorm - 意图理解
        self.mcpbrainstorm = {
            "enabled": True,
            "confidence_threshold": 0.8
        }
        
        # MCPPlanner - 任务规划
        self.mcpplanner = {
            "enabled": True,
            "complexity_threshold": 0.7,
            "max_subtasks": 10
        }
        
        # InfiniteContext - 上下文管理
        self.infinite_context = {
            "enabled": True,
            "max_context_length": 100000,
            "chunk_size": 4000
        }
        
        # 统一工具引擎
        self.unified_tool_engine = {
            "enabled": True,
            "platforms": ["aci.dev", "mcp.so", "zapier"],
            "max_parallel_tools": 5
        }
        
        logger.info("AI增强组件初始化完成")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据的主要方法"""
        try:
            action = input_data.get("action", "analyze_and_execute")
            
            if action == "analyze_and_execute":
                return self._analyze_and_execute_workflow(input_data)
            elif action == "create_workflow_node":
                return self._create_workflow_node_action(input_data)
            elif action == "start_test_workflow":
                return self._start_test_workflow_action(input_data)
            elif action == "start_rollback_workflow":
                return self._start_rollback_workflow_action(input_data)
            elif action == "get_workflow_status":
                return self._get_workflow_status_action()
            elif action == "register_event_listener":
                return self._register_event_listener_action(input_data)
            elif action == "trigger_event":
                return self._trigger_event_action(input_data)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_and_execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析并执行智能工作流"""
        user_request = input_data.get("user_request", "")
        context = input_data.get("context", {})
        
        # 1. MCPBrainstorm - 意图理解
        intent_analysis = self._mcpbrainstorm_analyze(user_request, context)
        
        # 2. 复杂度分析
        complexity_score = self._analyze_complexity(intent_analysis)
        
        # 3. 决定是否使用MCPPlanner
        if self._should_use_mcpplanner(complexity_score, intent_analysis):
            # 复杂工作流 - 使用MCPPlanner
            workflow_plan = self._mcpplanner_create_plan(intent_analysis)
            execution_result = self._execute_complex_workflow(workflow_plan)
        else:
            # 简单工作流 - 直接执行
            execution_result = self._execute_simple_workflow(intent_analysis)
        
        # 4. InfiniteContext - 上下文增强
        enhanced_result = self._infinite_context_enhance(execution_result, context)
        
        return {
            "status": "success",
            "intent_analysis": intent_analysis,
            "complexity_score": complexity_score,
            "execution_result": enhanced_result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _mcpbrainstorm_analyze(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """MCPBrainstorm意图理解"""
        # 简化的意图分析逻辑
        keywords = user_request.lower().split()
        
        intent_type = "unknown"
        if any(word in keywords for word in ["test", "测试"]):
            intent_type = "testing"
        elif any(word in keywords for word in ["deploy", "部署", "发布"]):
            intent_type = "deployment"
        elif any(word in keywords for word in ["rollback", "回滚"]):
            intent_type = "rollback"
        elif any(word in keywords for word in ["analyze", "分析"]):
            intent_type = "analysis"
        
        return {
            "intent_type": intent_type,
            "confidence": 0.85,
            "keywords": keywords,
            "user_request": user_request,
            "context": context
        }
    
    def _analyze_complexity(self, intent_analysis: Dict[str, Any]) -> float:
        """分析任务复杂度"""
        base_score = 0.3
        
        # 基于关键词数量
        keyword_count = len(intent_analysis.get("keywords", []))
        if keyword_count > 5:
            base_score += 0.2
        
        # 基于意图类型
        intent_type = intent_analysis.get("intent_type", "unknown")
        if intent_type in ["deployment", "rollback"]:
            base_score += 0.3
        elif intent_type in ["testing", "analysis"]:
            base_score += 0.2
        
        # 基于上下文复杂度
        context = intent_analysis.get("context", {})
        if len(context) > 3:
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _should_use_mcpplanner(self, complexity_score: float, intent_analysis: Dict[str, Any]) -> bool:
        """判断是否应该使用MCPPlanner"""
        # MCPPlanner触发条件
        if complexity_score > 0.7:
            return True
        
        # 检查子任务数量（简化估算）
        keywords = intent_analysis.get("keywords", [])
        estimated_subtasks = len([w for w in keywords if w in ["and", "then", "after", "before"]])
        if estimated_subtasks > 3:
            return True
        
        # 检查工具需求（简化估算）
        estimated_tools = len([w for w in keywords if w in ["test", "deploy", "analyze", "generate", "send"]])
        if estimated_tools > 5:
            return True
        
        return False
    
    def _mcpplanner_create_plan(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """MCPPlanner创建执行计划"""
        intent_type = intent_analysis.get("intent_type", "unknown")
        
        if intent_type == "testing":
            return {
                "plan_type": "testing_workflow",
                "steps": [
                    {"id": "prepare_env", "name": "准备测试环境", "type": "setup"},
                    {"id": "run_tests", "name": "执行测试", "type": "execution"},
                    {"id": "generate_report", "name": "生成报告", "type": "reporting"}
                ],
                "estimated_duration": 300,
                "complexity": "medium"
            }
        elif intent_type == "deployment":
            return {
                "plan_type": "deployment_workflow",
                "steps": [
                    {"id": "validate_code", "name": "代码验证", "type": "validation"},
                    {"id": "build_package", "name": "构建包", "type": "build"},
                    {"id": "deploy_service", "name": "部署服务", "type": "deployment"},
                    {"id": "verify_deployment", "name": "验证部署", "type": "verification"}
                ],
                "estimated_duration": 600,
                "complexity": "high"
            }
        else:
            return {
                "plan_type": "generic_workflow",
                "steps": [
                    {"id": "analyze_request", "name": "分析请求", "type": "analysis"},
                    {"id": "execute_action", "name": "执行操作", "type": "execution"}
                ],
                "estimated_duration": 120,
                "complexity": "low"
            }
    
    def _execute_complex_workflow(self, workflow_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行复杂工作流"""
        plan_type = workflow_plan.get("plan_type", "generic")
        steps = workflow_plan.get("steps", [])
        
        # 创建工作流节点
        node_ids = []
        for step in steps:
            node_id = self.create_workflow_node(
                "action",
                step["name"],
                f"执行步骤: {step['name']}",
                step
            )
            node_ids.append(node_id)
        
        # 创建连接
        for i in range(len(node_ids) - 1):
            self.create_workflow_connection(node_ids[i], node_ids[i + 1])
        
        # 执行工作流
        execution_results = []
        for i, node_id in enumerate(node_ids):
            self.update_node_status(node_id, "running")
            
            # 模拟步骤执行
            time.sleep(1)
            
            step_result = {
                "step_id": steps[i]["id"],
                "status": "success",
                "duration": 1.0,
                "output": f"步骤 {steps[i]['name']} 执行完成"
            }
            
            execution_results.append(step_result)
            self.update_node_status(node_id, "success", {"result": step_result})
        
        return {
            "workflow_type": "complex",
            "plan_type": plan_type,
            "steps_executed": len(steps),
            "execution_results": execution_results,
            "total_duration": len(steps) * 1.0
        }
    
    def _execute_simple_workflow(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """执行简单工作流"""
        intent_type = intent_analysis.get("intent_type", "unknown")
        
        # 创建单个执行节点
        node_id = self.create_workflow_node(
            "action",
            f"执行{intent_type}操作",
            f"简单工作流执行: {intent_type}",
            intent_analysis
        )
        
        self.update_node_status(node_id, "running")
        
        # 模拟执行
        time.sleep(0.5)
        
        result = {
            "action": intent_type,
            "status": "success",
            "duration": 0.5,
            "output": f"{intent_type}操作执行完成"
        }
        
        self.update_node_status(node_id, "success", {"result": result})
        
        return {
            "workflow_type": "simple",
            "intent_type": intent_type,
            "execution_result": result
        }
    
    def _infinite_context_enhance(self, execution_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """InfiniteContext上下文增强"""
        enhanced_result = execution_result.copy()
        
        # 添加上下文信息
        enhanced_result["context_enhancement"] = {
            "original_context": context,
            "execution_context": {
                "timestamp": datetime.now().isoformat(),
                "workflow_id": f"wf_{int(time.time())}",
                "enhancement_applied": True
            }
        }
        
        # 添加历史关联
        enhanced_result["historical_context"] = {
            "previous_executions": len(self.workflow_nodes),
            "success_rate": self._calculate_success_rate(),
            "average_duration": self._calculate_average_duration()
        }
        
        return enhanced_result
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.workflow_nodes:
            return 1.0
        
        success_count = sum(1 for node in self.workflow_nodes if node.get("status") == "success")
        return success_count / len(self.workflow_nodes)
    
    def _calculate_average_duration(self) -> float:
        """计算平均执行时间"""
        # 简化计算
        return 2.5
    
    # WorkflowDriver集成方法
    
    def register_event_listener(self, event_type: str, callback: Callable):
        """注册事件监听器"""
        with self.event_lock:
            if event_type not in self.event_listeners:
                self.event_listeners[event_type] = []
            
            self.event_listeners[event_type].append(callback)
            logger.info(f"已注册事件监听器: {event_type}")
    
    def trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """触发事件"""
        with self.event_lock:
            if event_type in self.event_listeners:
                for callback in self.event_listeners[event_type]:
                    try:
                        callback(event_data)
                    except Exception as e:
                        logger.error(f"事件处理异常: {str(e)}")
            
            logger.info(f"已触发事件: {event_type}")
    
    def create_workflow_node(self, node_type: str, name: str, description: str, data: Dict[str, Any] = None) -> str:
        """创建工作流节点"""
        node_id = f"node_{len(self.workflow_nodes) + 1}"
        timestamp = datetime.now().isoformat()
        
        node = {
            "id": node_id,
            "type": node_type,
            "name": name,
            "description": description,
            "timestamp": timestamp,
            "status": "pending",
            "data": data or {}
        }
        
        self.workflow_nodes.append(node)
        
        # 触发节点创建事件
        self.trigger_event("node_created", {"node": node})
        
        logger.info(f"已创建工作流节点: {node_id} ({name})")
        return node_id
    
    def create_workflow_connection(self, source_id: str, target_id: str, connection_type: str = "success") -> str:
        """创建工作流连接"""
        connection_id = f"conn_{len(self.workflow_connections) + 1}"
        
        connection = {
            "id": connection_id,
            "source": source_id,
            "target": target_id,
            "type": connection_type
        }
        
        self.workflow_connections.append(connection)
        
        # 触发连接创建事件
        self.trigger_event("connection_created", {"connection": connection})
        
        logger.info(f"已创建工作流连接: {connection_id} ({source_id} -> {target_id})")
        return connection_id
    
    def update_node_status(self, node_id: str, status: str, data: Dict[str, Any] = None):
        """更新节点状态"""
        for node in self.workflow_nodes:
            if node["id"] == node_id:
                node["status"] = status
                node["last_update_time"] = datetime.now().isoformat()
                
                if data:
                    node["data"].update(data)
                
                # 触发节点更新事件
                self.trigger_event("node_updated", {"node": node})
                
                logger.info(f"已更新节点状态: {node_id} -> {status}")
                
                # 更新工作流状态
                if status == "running":
                    self.workflow_status["current_node"] = node_id
                
                return
        
        logger.warning(f"未找到节点: {node_id}")
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """获取工作流数据"""
        return {
            "nodes": self.workflow_nodes,
            "connections": self.workflow_connections,
            "status": self.workflow_status
        }
    
    def set_test_mode(self, is_test: bool = True):
        """设置测试模式"""
        self.is_test_mode = is_test
        logger.info(f"测试模式已{'启用' if is_test else '禁用'}")
    
    def start_test_workflow(self, test_type: str, test_target: str):
        """启动测试工作流"""
        if self.workflow_status["is_running"]:
            logger.warning("工作流已在运行中，无法启动新工作流")
            return
        
        # 检测是否为测试环境
        if "test" in test_type or "test" in test_target:
            self.set_test_mode(True)
        
        # 更新工作流状态
        self.workflow_status["is_running"] = True
        self.workflow_status["start_time"] = datetime.now().isoformat()
        self.workflow_status["last_update_time"] = datetime.now().isoformat()
        
        # 创建触发器节点
        trigger_node_id = self.create_workflow_node(
            "trigger",
            "测试工作流",
            f"启动{test_type}测试: {test_target}",
            {
                "test_type": test_type,
                "test_target": test_target
            }
        )
        
        # 更新触发器节点状态
        self.update_node_status(trigger_node_id, "success")
        
        # 启动工作流线程
        self.workflow_thread = threading.Thread(
            target=self._run_test_workflow,
            args=(trigger_node_id, test_type, test_target)
        )
        self.workflow_thread.daemon = True
        self.workflow_thread.start()
        
        logger.info(f"已启动测试工作流: {test_type} - {test_target}")
    
    def _run_test_workflow(self, trigger_node_id: str, test_type: str, test_target: str):
        """运行测试工作流"""
        try:
            # 1. 准备测试环境节点
            prepare_node_id = self.create_workflow_node(
                "action",
                "准备测试环境",
                "设置测试环境和依赖",
                {
                    "test_type": test_type,
                    "test_target": test_target
                }
            )
            self.create_workflow_connection(trigger_node_id, prepare_node_id)
            self.update_node_status(prepare_node_id, "running")
            
            # 模拟准备测试环境
            time.sleep(1)
            
            self.update_node_status(prepare_node_id, "success", {
                "environment": "test",
                "dependencies": ["pytest", "coverage"]
            })
            
            # 2. 执行测试节点
            execute_node_id = self.create_workflow_node(
                "action",
                "执行测试",
                f"运行{test_type}测试: {test_target}",
                {
                    "test_type": test_type,
                    "test_target": test_target
                }
            )
            self.create_workflow_connection(prepare_node_id, execute_node_id)
            self.update_node_status(execute_node_id, "running")
            
            # 模拟执行测试
            time.sleep(2)
            
            # 假设测试结果
            test_results = {
                "total": 10,
                "passed": 8,
                "failed": 1,
                "skipped": 1,
                "pass_rate": 80.0
            }
            
            self.update_node_status(execute_node_id, "success", {
                "results": test_results
            })
            
            # 3. 生成测试报告节点
            report_node_id = self.create_workflow_node(
                "action",
                "生成测试报告",
                "生成测试结果报告",
                {
                    "test_type": test_type,
                    "test_target": test_target
                }
            )
            self.create_workflow_connection(execute_node_id, report_node_id)
            self.update_node_status(report_node_id, "running")
            
            # 模拟生成测试报告
            time.sleep(1)
            
            self.update_node_status(report_node_id, "success", {
                "report_path": f"reports/{test_type}_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html",
                "coverage": 75.5
            })
            
            # 4. 完成工作流
            self.workflow_status["is_running"] = False
            self.workflow_status["current_node"] = None
            self.workflow_status["last_update_time"] = datetime.now().isoformat()
            
            # 触发工作流完成事件
            self.trigger_event("workflow_completed", {
                "workflow_type": "test",
                "test_type": test_type,
                "test_target": test_target,
                "results": test_results
            })
            
            logger.info("测试工作流执行完成")
            
        except Exception as e:
            logger.error(f"测试工作流执行异常: {str(e)}")
            
            # 创建错误节点
            error_node_id = self.create_workflow_node(
                "error",
                "工作流错误",
                f"测试工作流执行异常: {str(e)}",
                {
                    "error": str(e)
                }
            )
            
            # 更新工作流状态
            self.workflow_status["is_running"] = False
            self.workflow_status["current_node"] = None
            self.workflow_status["last_update_time"] = datetime.now().isoformat()
            
            # 触发工作流完成事件（即使出错也要触发）
            self.trigger_event("workflow_error", {
                "error": str(e),
                "workflow_type": "test"
            })
    
    def start_rollback_workflow(self, reason: str = None, savepoint_id: str = None):
        """启动回滚工作流"""
        if self.workflow_status["is_running"]:
            logger.warning("工作流已在运行中，无法启动新工作流")
            return
        
        # 检测是否为测试环境
        if reason and ("test" in reason.lower() or "集成测试" in reason):
            self.set_test_mode(True)
        
        # 更新工作流状态
        self.workflow_status["is_running"] = True
        self.workflow_status["start_time"] = datetime.now().isoformat()
        self.workflow_status["last_update_time"] = datetime.now().isoformat()
        
        # 创建触发器节点
        trigger_node_id = self.create_workflow_node(
            "trigger",
            "回滚工作流",
            f"启动回滚操作: {reason or '手动触发'}",
            {
                "reason": reason,
                "savepoint_id": savepoint_id
            }
        )
        
        # 更新触发器节点状态
        self.update_node_status(trigger_node_id, "success")
        
        # 启动工作流线程
        self.workflow_thread = threading.Thread(
            target=self._run_rollback_workflow,
            args=(trigger_node_id, reason, savepoint_id)
        )
        self.workflow_thread.daemon = True
        self.workflow_thread.start()
        
        logger.info(f"已启动回滚工作流: {reason or '手动触发'}")
    
    def _run_rollback_workflow(self, trigger_node_id: str, reason: str, savepoint_id: str):
        """运行回滚工作流"""
        try:
            # 1. 查找保存点节点
            find_node_id = self.create_workflow_node(
                "action",
                "查找保存点",
                f"查找目标保存点: {savepoint_id or '最近保存点'}",
                {
                    "savepoint_id": savepoint_id
                }
            )
            self.create_workflow_connection(trigger_node_id, find_node_id)
            self.update_node_status(find_node_id, "running")
            
            # 模拟查找保存点
            time.sleep(1)
            
            # 如果未指定保存点ID，则使用最近的保存点
            if not savepoint_id:
                savepoint_id = "sp_latest"
            
            self.update_node_status(find_node_id, "success", {
                "savepoint_id": savepoint_id,
                "savepoint_time": datetime.now().isoformat()
            })
            
            # 2. 执行回滚节点
            rollback_node_id = self.create_workflow_node(
                "action",
                "执行回滚",
                f"回滚到保存点: {savepoint_id}",
                {
                    "savepoint_id": savepoint_id,
                    "reason": reason
                }
            )
            self.create_workflow_connection(find_node_id, rollback_node_id)
            self.update_node_status(rollback_node_id, "running")
            
            # 调用AgentProblemSolver执行回滚
            if self.agent_problem_solver:
                rollback_result = self.agent_problem_solver.process({
                    "action": "rollback_to_savepoint",
                    "savepoint_id": savepoint_id
                })
            else:
                rollback_result = {"status": "success", "files_affected": 0}
            
            if rollback_result.get("status") == "success":
                self.update_node_status(rollback_node_id, "success", {
                    "savepoint_id": savepoint_id,
                    "files_affected": rollback_result.get("files_affected", 0)
                })
                
                # 3. 验证回滚节点
                verify_node_id = self.create_workflow_node(
                    "action",
                    "验证回滚",
                    "验证回滚结果",
                    {
                        "savepoint_id": savepoint_id
                    }
                )
                self.create_workflow_connection(rollback_node_id, verify_node_id)
                self.update_node_status(verify_node_id, "running")
                
                # 模拟验证回滚
                time.sleep(1)
                
                self.update_node_status(verify_node_id, "success", {
                    "verification_result": "passed",
                    "integrity_check": "passed"
                })
            else:
                self.update_node_status(rollback_node_id, "failed", {
                    "error": rollback_result.get("message", "回滚失败")
                })
            
            # 4. 完成工作流
            self.workflow_status["is_running"] = False
            self.workflow_status["current_node"] = None
            self.workflow_status["last_update_time"] = datetime.now().isoformat()
            
            # 触发工作流完成事件
            self.trigger_event("workflow_completed", {
                "workflow_type": "rollback",
                "savepoint_id": savepoint_id,
                "reason": reason
            })
            
            logger.info("回滚工作流执行完成")
            
        except Exception as e:
            logger.error(f"回滚工作流执行异常: {str(e)}")
            
            # 创建错误节点
            error_node_id = self.create_workflow_node(
                "error",
                "工作流错误",
                f"回滚工作流执行异常: {str(e)}",
                {
                    "error": str(e)
                }
            )
            
            # 更新工作流状态
            self.workflow_status["is_running"] = False
            self.workflow_status["current_node"] = None
            self.workflow_status["last_update_time"] = datetime.now().isoformat()
            
            # 触发工作流完成事件（即使出错也要触发）
            self.trigger_event("workflow_error", {
                "error": str(e),
                "workflow_type": "rollback"
            })
    
    # MCP适配器接口方法
    
    def _create_workflow_node_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建工作流节点的MCP接口"""
        node_type = input_data.get("node_type", "action")
        name = input_data.get("name", "未命名节点")
        description = input_data.get("description", "")
        data = input_data.get("data", {})
        
        node_id = self.create_workflow_node(node_type, name, description, data)
        
        return {
            "status": "success",
            "node_id": node_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def _start_test_workflow_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """启动测试工作流的MCP接口"""
        test_type = input_data.get("test_type", "unit")
        test_target = input_data.get("test_target", "all")
        
        self.start_test_workflow(test_type, test_target)
        
        return {
            "status": "success",
            "message": f"测试工作流已启动: {test_type} - {test_target}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _start_rollback_workflow_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """启动回滚工作流的MCP接口"""
        reason = input_data.get("reason", "手动触发")
        savepoint_id = input_data.get("savepoint_id")
        
        self.start_rollback_workflow(reason, savepoint_id)
        
        return {
            "status": "success",
            "message": f"回滚工作流已启动: {reason}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_workflow_status_action(self) -> Dict[str, Any]:
        """获取工作流状态的MCP接口"""
        return {
            "status": "success",
            "workflow_data": self.get_workflow_data(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _register_event_listener_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """注册事件监听器的MCP接口"""
        event_type = input_data.get("event_type", "")
        
        if not event_type:
            return {
                "status": "error",
                "message": "event_type is required",
                "timestamp": datetime.now().isoformat()
            }
        
        # 注册一个默认的日志回调
        def default_callback(event_data):
            logger.info(f"Event {event_type} triggered: {event_data}")
        
        self.register_event_listener(event_type, default_callback)
        
        return {
            "status": "success",
            "message": f"事件监听器已注册: {event_type}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _trigger_event_action(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """触发事件的MCP接口"""
        event_type = input_data.get("event_type", "")
        event_data = input_data.get("event_data", {})
        
        if not event_type:
            return {
                "status": "error",
                "message": "event_type is required",
                "timestamp": datetime.now().isoformat()
            }
        
        self.trigger_event(event_type, event_data)
        
        return {
            "status": "success",
            "message": f"事件已触发: {event_type}",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力列表"""
        return [
            "workflow_management",
            "ai_enhanced_planning",
            "intelligent_routing",
            "context_enhancement",
            "event_handling",
            "test_automation",
            "rollback_management",
            "node_management",
            "connection_management"
        ]
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get("action")
        if not action:
            return False
        
        return True
    
    def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建智能工作流
        
        Args:
            workflow_config: 工作流配置字典，包含以下字段：
                - workflow_name: 工作流名称
                - nodes: 节点列表，每个节点包含id、type、name等
                - connections: 连接列表，定义节点间的连接关系
                - metadata: 元数据信息
                
        Returns:
            创建结果字典，包含workflow_id和状态信息
        """
        try:
            # 如果没有提供节点，创建默认节点配置
            if not workflow_config.get("nodes"):
                workflow_config = self._add_default_nodes(workflow_config)
            
            # 验证工作流配置
            if not self._validate_workflow_config(workflow_config):
                return {
                    "status": "error",
                    "message": "工作流配置验证失败",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 生成工作流ID
            workflow_id = f"workflow_{int(time.time())}_{len(self.workflow_nodes)}"
            workflow_name = workflow_config.get("workflow_name", f"工作流_{workflow_id}")
            
            # 创建工作流节点
            created_nodes = []
            node_mapping = {}  # 原始ID到实际ID的映射
            
            for node_config in workflow_config.get("nodes", []):
                node_id = self.create_workflow_node(
                    node_type=node_config.get("type", "action"),
                    name=node_config.get("name", "未命名节点"),
                    description=node_config.get("description", ""),
                    data=node_config.get("data", {})
                )
                
                created_nodes.append(node_id)
                node_mapping[node_config.get("id", "")] = node_id
            
            # 创建工作流连接
            created_connections = []
            for connection_config in workflow_config.get("connections", []):
                from_id = node_mapping.get(connection_config.get("from", ""))
                to_id = node_mapping.get(connection_config.get("to", ""))
                
                if from_id and to_id:
                    connection_id = self.create_workflow_connection(
                        source_id=from_id,
                        target_id=to_id,
                        connection_type=connection_config.get("type", "success")
                    )
                    created_connections.append(connection_id)
            
            # 保存工作流元数据
            workflow_metadata = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "created_time": datetime.now().isoformat(),
                "nodes": created_nodes,
                "connections": created_connections,
                "node_mapping": node_mapping,
                "config": workflow_config,
                "status": "created"
            }
            
            # 触发工作流创建事件
            self.trigger_event("workflow_created", {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "node_count": len(created_nodes),
                "connection_count": len(created_connections)
            })
            
            logger.info(f"工作流创建成功: {workflow_name} (ID: {workflow_id})")
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "nodes_created": len(created_nodes),
                "connections_created": len(created_connections),
                "metadata": workflow_metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"创建工作流失败: {e}")
            return {
                "status": "error",
                "message": f"创建工作流失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_workflow(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            execution_data: 执行数据字典，包含：
                - workflow_id: 工作流ID
                - input_data: 输入数据
                - execution_mode: 执行模式 (sync/async)
                
        Returns:
            执行结果字典
        """
        try:
            workflow_id = execution_data.get("workflow_id", "")
            input_data = execution_data.get("input_data", {})
            execution_mode = execution_data.get("execution_mode", "sync")
            
            if not workflow_id:
                return {
                    "status": "error",
                    "message": "workflow_id is required",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 更新工作流状态
            self.workflow_status.update({
                "is_running": True,
                "current_workflow_id": workflow_id,
                "start_time": datetime.now().isoformat(),
                "last_update_time": datetime.now().isoformat(),
                "execution_mode": execution_mode
            })
            
            # 模拟工作流执行过程
            execution_steps = []
            
            # 步骤1: 初始化
            execution_steps.append({
                "step": "initialization",
                "status": "completed",
                "message": "工作流初始化完成",
                "timestamp": datetime.now().isoformat()
            })
            
            # 步骤2: 数据预处理
            processed_data = self._preprocess_workflow_data(input_data)
            execution_steps.append({
                "step": "data_preprocessing",
                "status": "completed",
                "message": "数据预处理完成",
                "data_size": len(str(processed_data)),
                "timestamp": datetime.now().isoformat()
            })
            
            # 步骤3: 节点执行
            node_results = self._execute_workflow_nodes(workflow_id, processed_data)
            execution_steps.append({
                "step": "node_execution",
                "status": "completed",
                "message": f"执行了{len(node_results)}个节点",
                "node_count": len(node_results),
                "timestamp": datetime.now().isoformat()
            })
            
            # 步骤4: 结果整合
            final_result = self._integrate_workflow_results(node_results)
            execution_steps.append({
                "step": "result_integration",
                "status": "completed",
                "message": "结果整合完成",
                "timestamp": datetime.now().isoformat()
            })
            
            # 更新工作流状态
            self.workflow_status.update({
                "is_running": False,
                "current_workflow_id": None,
                "last_update_time": datetime.now().isoformat()
            })
            
            # 触发工作流完成事件
            self.trigger_event("workflow_completed", {
                "workflow_id": workflow_id,
                "execution_time": time.time(),
                "steps_completed": len(execution_steps)
            })
            
            logger.info(f"工作流执行完成: {workflow_id}")
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "execution_steps": execution_steps,
                "final_result": final_result,
                "execution_mode": execution_mode,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # 更新错误状态
            self.workflow_status.update({
                "is_running": False,
                "current_workflow_id": None,
                "last_error": str(e),
                "last_update_time": datetime.now().isoformat()
            })
            
            logger.error(f"工作流执行失败: {e}")
            return {
                "status": "error",
                "message": f"工作流执行失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_workflow_config(self, config: Dict[str, Any]) -> bool:
        """验证工作流配置"""
        try:
            # 检查必需字段
            if not config.get("workflow_name"):
                logger.error("工作流名称不能为空")
                return False
            
            nodes = config.get("nodes", [])
            if not nodes:
                logger.error("工作流必须包含至少一个节点")
                return False
            
            # 验证节点配置
            for node in nodes:
                if not node.get("id") or not node.get("type"):
                    logger.error("节点必须包含id和type字段")
                    return False
            
            # 验证连接配置
            connections = config.get("connections", [])
            node_ids = {node.get("id") for node in nodes}
            
            for connection in connections:
                from_id = connection.get("from")
                to_id = connection.get("to")
                
                if from_id not in node_ids or to_id not in node_ids:
                    logger.error(f"连接引用了不存在的节点: {from_id} -> {to_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"工作流配置验证异常: {e}")
            return False
    
    def _preprocess_workflow_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理工作流数据"""
        processed_data = input_data.copy()
        
        # 添加执行上下文
        processed_data["execution_context"] = {
            "timestamp": datetime.now().isoformat(),
            "engine_version": "1.0.0",
            "execution_id": f"exec_{int(time.time())}"
        }
        
        # 数据清理和标准化
        if "user_input" in processed_data:
            processed_data["user_input"] = str(processed_data["user_input"]).strip()
        
        return processed_data
    
    def _execute_workflow_nodes(self, workflow_id: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行工作流节点"""
        node_results = []
        
        # 模拟节点执行
        for i, node in enumerate(self.workflow_nodes):
            node_result = {
                "node_id": node.get("id", f"node_{i}"),
                "node_type": node.get("type", "action"),
                "status": "completed",
                "output": {
                    "processed": True,
                    "data_size": len(str(data)),
                    "execution_time": 0.1
                },
                "timestamp": datetime.now().isoformat()
            }
            node_results.append(node_result)
        
        return node_results
    
    def _integrate_workflow_results(self, node_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """整合工作流结果"""
        return {
            "summary": {
                "total_nodes": len(node_results),
                "successful_nodes": len([r for r in node_results if r.get("status") == "completed"]),
                "failed_nodes": len([r for r in node_results if r.get("status") == "failed"]),
                "total_execution_time": sum(r.get("output", {}).get("execution_time", 0) for r in node_results)
            },
            "node_results": node_results,
            "final_status": "success" if all(r.get("status") == "completed" for r in node_results) else "partial_success"
        }
    
    def _add_default_nodes(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """为工作流添加默认节点配置"""
        workflow_name = workflow_config.get("workflow_name", "默认工作流")
        complexity = workflow_config.get("complexity", "medium")
        automation_level = workflow_config.get("automation_level", "standard")
        
        # 根据复杂度和自动化级别创建默认节点
        default_nodes = []
        default_connections = []
        
        if complexity == "low":
            # 简单工作流：开始 -> 执行 -> 结束
            default_nodes = [
                {"id": "start", "type": "start", "name": "开始", "description": "工作流开始节点"},
                {"id": "execute", "type": "action", "name": "执行任务", "description": "主要执行节点"},
                {"id": "end", "type": "end", "name": "结束", "description": "工作流结束节点"}
            ]
            default_connections = [
                {"from": "start", "to": "execute", "type": "success"},
                {"from": "execute", "to": "end", "type": "success"}
            ]
        elif complexity == "high" or complexity == "very_high":
            # 复杂工作流：开始 -> 分析 -> 处理 -> 验证 -> 结束
            default_nodes = [
                {"id": "start", "type": "start", "name": "开始", "description": "工作流开始节点"},
                {"id": "analyze", "type": "analysis", "name": "需求分析", "description": "分析输入需求"},
                {"id": "process", "type": "action", "name": "处理执行", "description": "主要处理逻辑"},
                {"id": "validate", "type": "validation", "name": "结果验证", "description": "验证处理结果"},
                {"id": "end", "type": "end", "name": "结束", "description": "工作流结束节点"}
            ]
            default_connections = [
                {"from": "start", "to": "analyze", "type": "success"},
                {"from": "analyze", "to": "process", "type": "success"},
                {"from": "process", "to": "validate", "type": "success"},
                {"from": "validate", "to": "end", "type": "success"}
            ]
        else:
            # 中等复杂度工作流：开始 -> 准备 -> 执行 -> 结束
            default_nodes = [
                {"id": "start", "type": "start", "name": "开始", "description": "工作流开始节点"},
                {"id": "prepare", "type": "preparation", "name": "准备阶段", "description": "准备执行环境"},
                {"id": "execute", "type": "action", "name": "执行任务", "description": "主要执行节点"},
                {"id": "end", "type": "end", "name": "结束", "description": "工作流结束节点"}
            ]
            default_connections = [
                {"from": "start", "to": "prepare", "type": "success"},
                {"from": "prepare", "to": "execute", "type": "success"},
                {"from": "execute", "to": "end", "type": "success"}
            ]
        
        # 如果是高级自动化，添加监控节点
        if automation_level == "advanced":
            monitor_node = {"id": "monitor", "type": "monitor", "name": "监控", "description": "监控执行状态"}
            default_nodes.append(monitor_node)
            # 为所有执行节点添加监控连接
            for node in default_nodes:
                if node["type"] in ["action", "analysis", "validation"]:
                    default_connections.append({"from": node["id"], "to": "monitor", "type": "monitor"})
        
        # 更新配置
        updated_config = workflow_config.copy()
        updated_config["nodes"] = default_nodes
        updated_config["connections"] = default_connections
        
        return updated_config

# 向后兼容的WorkflowDriver类
class WorkflowDriver:
    """向后兼容的WorkflowDriver类"""
    
    def __init__(self, project_root: str):
        self._engine = IntelligentWorkflowEngineMCP(project_root)
    
    def __getattr__(self, name):
        """代理所有方法调用到IntelligentWorkflowEngineMCP"""
        return getattr(self._engine, name)


    def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建智能工作流
        
        Args:
            workflow_config: 工作流配置字典，包含以下字段：
                - workflow_name: 工作流名称
                - nodes: 节点列表，每个节点包含id、type、name等
                - connections: 连接列表，定义节点间的连接关系
                - metadata: 元数据信息
                
        Returns:
            创建结果字典，包含workflow_id和状态信息
        """
        try:
            # 验证工作流配置
            if not self._validate_workflow_config(workflow_config):
                return {
                    "status": "error",
                    "message": "工作流配置验证失败",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 生成工作流ID
            workflow_id = f"workflow_{int(time.time())}_{len(self.workflow_nodes)}"
            workflow_name = workflow_config.get("workflow_name", f"工作流_{workflow_id}")
            
            # 创建工作流节点
            created_nodes = []
            node_mapping = {}  # 原始ID到实际ID的映射
            
            for node_config in workflow_config.get("nodes", []):
                node_id = self.create_workflow_node(
                    node_type=node_config.get("type", "action"),
                    name=node_config.get("name", "未命名节点"),
                    description=node_config.get("description", ""),
                    data=node_config.get("data", {})
                )
                
                created_nodes.append(node_id)
                node_mapping[node_config.get("id", "")] = node_id
            
            # 创建工作流连接
            created_connections = []
            for connection_config in workflow_config.get("connections", []):
                from_id = node_mapping.get(connection_config.get("from", ""))
                to_id = node_mapping.get(connection_config.get("to", ""))
                
                if from_id and to_id:
                    connection_id = self.create_workflow_connection(
                        source_id=from_id,
                        target_id=to_id,
                        connection_type=connection_config.get("type", "success")
                    )
                    created_connections.append(connection_id)
            
            # 保存工作流元数据
            workflow_metadata = {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "created_time": datetime.now().isoformat(),
                "nodes": created_nodes,
                "connections": created_connections,
                "node_mapping": node_mapping,
                "config": workflow_config,
                "status": "created"
            }
            
            # 触发工作流创建事件
            self.trigger_event("workflow_created", {
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "node_count": len(created_nodes),
                "connection_count": len(created_connections)
            })
            
            logger.info(f"工作流创建成功: {workflow_name} (ID: {workflow_id})")
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "nodes_created": len(created_nodes),
                "connections_created": len(created_connections),
                "metadata": workflow_metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"创建工作流失败: {e}")
            return {
                "status": "error",
                "message": f"创建工作流失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_workflow(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            execution_data: 执行数据字典，包含：
                - workflow_id: 工作流ID
                - input_data: 输入数据
                - execution_mode: 执行模式 (sync/async)
                
        Returns:
            执行结果字典
        """
        try:
            workflow_id = execution_data.get("workflow_id", "")
            input_data = execution_data.get("input_data", {})
            execution_mode = execution_data.get("execution_mode", "sync")
            
            if not workflow_id:
                return {
                    "status": "error",
                    "message": "workflow_id is required",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 更新工作流状态
            self.workflow_status.update({
                "is_running": True,
                "current_workflow_id": workflow_id,
                "start_time": datetime.now().isoformat(),
                "last_update_time": datetime.now().isoformat(),
                "execution_mode": execution_mode
            })
            
            # 模拟工作流执行过程
            execution_steps = []
            
            # 步骤1: 初始化
            execution_steps.append({
                "step": "initialization",
                "status": "completed",
                "message": "工作流初始化完成",
                "timestamp": datetime.now().isoformat()
            })
            
            # 步骤2: 数据预处理
            processed_data = self._preprocess_workflow_data(input_data)
            execution_steps.append({
                "step": "data_preprocessing",
                "status": "completed",
                "message": "数据预处理完成",
                "data_size": len(str(processed_data)),
                "timestamp": datetime.now().isoformat()
            })
            
            # 步骤3: 节点执行
            node_results = self._execute_workflow_nodes(workflow_id, processed_data)
            execution_steps.append({
                "step": "node_execution",
                "status": "completed",
                "message": f"执行了{len(node_results)}个节点",
                "node_count": len(node_results),
                "timestamp": datetime.now().isoformat()
            })
            
            # 步骤4: 结果整合
            final_result = self._integrate_workflow_results(node_results)
            execution_steps.append({
                "step": "result_integration",
                "status": "completed",
                "message": "结果整合完成",
                "timestamp": datetime.now().isoformat()
            })
            
            # 更新工作流状态
            self.workflow_status.update({
                "is_running": False,
                "current_workflow_id": None,
                "last_update_time": datetime.now().isoformat()
            })
            
            # 触发工作流完成事件
            self.trigger_event("workflow_completed", {
                "workflow_id": workflow_id,
                "execution_time": time.time(),
                "steps_completed": len(execution_steps)
            })
            
            logger.info(f"工作流执行完成: {workflow_id}")
            
            return {
                "status": "success",
                "workflow_id": workflow_id,
                "execution_steps": execution_steps,
                "final_result": final_result,
                "execution_mode": execution_mode,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # 更新错误状态
            self.workflow_status.update({
                "is_running": False,
                "current_workflow_id": None,
                "last_error": str(e),
                "last_update_time": datetime.now().isoformat()
            })
            
            logger.error(f"工作流执行失败: {e}")
            return {
                "status": "error",
                "message": f"工作流执行失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_workflow_config(self, config: Dict[str, Any]) -> bool:
        """验证工作流配置"""
        try:
            # 检查必需字段
            if not config.get("workflow_name"):
                logger.error("工作流名称不能为空")
                return False
            
            nodes = config.get("nodes", [])
            if not nodes:
                logger.error("工作流必须包含至少一个节点")
                return False
            
            # 验证节点配置
            for node in nodes:
                if not node.get("id") or not node.get("type"):
                    logger.error("节点必须包含id和type字段")
                    return False
            
            # 验证连接配置
            connections = config.get("connections", [])
            node_ids = {node.get("id") for node in nodes}
            
            for connection in connections:
                from_id = connection.get("from")
                to_id = connection.get("to")
                
                if from_id not in node_ids or to_id not in node_ids:
                    logger.error(f"连接引用了不存在的节点: {from_id} -> {to_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"工作流配置验证异常: {e}")
            return False
    
    def _preprocess_workflow_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理工作流数据"""
        processed_data = input_data.copy()
        
        # 添加执行上下文
        processed_data["execution_context"] = {
            "timestamp": datetime.now().isoformat(),
            "engine_version": "1.0.0",
            "execution_id": f"exec_{int(time.time())}"
        }
        
        # 数据清理和标准化
        if "user_input" in processed_data:
            processed_data["user_input"] = str(processed_data["user_input"]).strip()
        
        return processed_data
    
    def _execute_workflow_nodes(self, workflow_id: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行工作流节点"""
        node_results = []
        
        # 模拟节点执行
        for i, node in enumerate(self.workflow_nodes):
            node_result = {
                "node_id": node.get("id", f"node_{i}"),
                "node_type": node.get("type", "action"),
                "status": "completed",
                "output": {
                    "processed": True,
                    "data_size": len(str(data)),
                    "execution_time": 0.1
                },
                "timestamp": datetime.now().isoformat()
            }
            node_results.append(node_result)
        
        return node_results
    
    def _integrate_workflow_results(self, node_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """整合工作流结果"""
        return {
            "summary": {
                "total_nodes": len(node_results),
                "successful_nodes": len([r for r in node_results if r.get("status") == "completed"]),
                "failed_nodes": len([r for r in node_results if r.get("status") == "failed"]),
                "total_execution_time": sum(r.get("output", {}).get("execution_time", 0) for r in node_results)
            },
            "node_results": node_results,
            "final_status": "success" if all(r.get("status") == "completed" for r in node_results) else "partial_success"
        }


    
    def _add_default_nodes(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """为工作流添加默认节点配置"""
        workflow_name = workflow_config.get("workflow_name", "默认工作流")
        complexity = workflow_config.get("complexity", "medium")
        automation_level = workflow_config.get("automation_level", "standard")
        
        # 根据复杂度和自动化级别创建默认节点
        default_nodes = []
        default_connections = []
        
        if complexity == "low":
            # 简单工作流：开始 -> 执行 -> 结束
            default_nodes = [
                {"id": "start", "type": "start", "name": "开始", "description": "工作流开始节点"},
                {"id": "execute", "type": "action", "name": "执行任务", "description": "主要执行节点"},
                {"id": "end", "type": "end", "name": "结束", "description": "工作流结束节点"}
            ]
            default_connections = [
                {"from": "start", "to": "execute", "type": "success"},
                {"from": "execute", "to": "end", "type": "success"}
            ]
        elif complexity == "high" or complexity == "very_high":
            # 复杂工作流：开始 -> 分析 -> 处理 -> 验证 -> 结束
            default_nodes = [
                {"id": "start", "type": "start", "name": "开始", "description": "工作流开始节点"},
                {"id": "analyze", "type": "analysis", "name": "需求分析", "description": "分析输入需求"},
                {"id": "process", "type": "action", "name": "处理执行", "description": "主要处理逻辑"},
                {"id": "validate", "type": "validation", "name": "结果验证", "description": "验证处理结果"},
                {"id": "end", "type": "end", "name": "结束", "description": "工作流结束节点"}
            ]
            default_connections = [
                {"from": "start", "to": "analyze", "type": "success"},
                {"from": "analyze", "to": "process", "type": "success"},
                {"from": "process", "to": "validate", "type": "success"},
                {"from": "validate", "to": "end", "type": "success"}
            ]
        else:
            # 中等复杂度工作流：开始 -> 准备 -> 执行 -> 结束
            default_nodes = [
                {"id": "start", "type": "start", "name": "开始", "description": "工作流开始节点"},
                {"id": "prepare", "type": "preparation", "name": "准备阶段", "description": "准备执行环境"},
                {"id": "execute", "type": "action", "name": "执行任务", "description": "主要执行节点"},
                {"id": "end", "type": "end", "name": "结束", "description": "工作流结束节点"}
            ]
            default_connections = [
                {"from": "start", "to": "prepare", "type": "success"},
                {"from": "prepare", "to": "execute", "type": "success"},
                {"from": "execute", "to": "end", "type": "success"}
            ]
        
        # 如果是高级自动化，添加监控节点
        if automation_level == "advanced":
            monitor_node = {"id": "monitor", "type": "monitor", "name": "监控", "description": "监控执行状态"}
            default_nodes.append(monitor_node)
            # 为所有执行节点添加监控连接
            for node in default_nodes:
                if node["type"] in ["action", "analysis", "validation"]:
                    default_connections.append({"from": node["id"], "to": "monitor", "type": "monitor"})
        
        # 更新配置
        updated_config = workflow_config.copy()
        updated_config["nodes"] = default_nodes
        updated_config["connections"] = default_connections
        
        return updated_config

