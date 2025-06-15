"""
MCP规划器模块 - MCPPlanner

负责规划和协调MCP模块的工作，集成mcp.so，调用各种工具。
"""

import os
import sys
import json
import importlib.util
from datetime import datetime
from ..development_tools.thought_action_recorder import ThoughtActionRecorder
from ..development_tools.agent_problem_solver import AgentProblemSolver
from ..development_tools.release_manager import ReleaseManager
from ..development_tools.test_issue_collector import TestAndIssueCollector

class MCPPlanner:
    def __init__(self):
        """初始化MCP规划器"""
        self.recorder = ThoughtActionRecorder()
        self.problem_solver = AgentProblemSolver()
        self.release_manager = ReleaseManager()
        self.test_collector = TestAndIssueCollector()
        
        # 集成mcp.so
        self.mcp_so_loaded = False
        self.mcp_so = None
        self._load_mcp_so()
        
        # 工具注册表
        self.tools_registry = {}
        self._register_default_tools()
        
        # 会话ID
        self.session_id = None
    
    def _load_mcp_so(self):
        """加载mcp.so动态库"""
        try:
            # 尝试加载mcp.so
            mcp_so_path = os.path.join(os.path.dirname(__file__), 'lib', 'mcp.so')
            if os.path.exists(mcp_so_path):
                spec = importlib.util.spec_from_file_location("mcp_so", mcp_so_path)
                self.mcp_so = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.mcp_so)
                self.mcp_so_loaded = True
                print(f"成功加载mcp.so: {mcp_so_path}")
            else:
                print(f"警告: mcp.so文件不存在: {mcp_so_path}")
        except Exception as e:
            print(f"加载mcp.so时出错: {e}")
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 注册开发工具
        self.tools_registry.update({
            "thought_action_recorder": self.recorder,
            "agent_problem_solver": self.problem_solver,
            "release_manager": self.release_manager,
            "test_issue_collector": self.test_collector
        })
        
        # 注册mcp.so提供的工具
        if self.mcp_so_loaded and hasattr(self.mcp_so, 'get_tools'):
            mcp_tools = self.mcp_so.get_tools()
            self.tools_registry.update(mcp_tools)
    
    def register_tool(self, tool_name, tool_instance):
        """注册新工具"""
        self.tools_registry[tool_name] = tool_instance
        return True
    
    def get_tool(self, tool_name):
        """获取工具实例"""
        return self.tools_registry.get(tool_name)
    
    def list_tools(self):
        """列出所有可用工具"""
        return list(self.tools_registry.keys())
    
    def start_session(self, agent_type):
        """启动新的会话"""
        self.session_id = self.recorder.start_session(agent_type)
        return self.session_id
    
    def plan_task(self, task_description, context=None):
        """规划任务执行步骤"""
        if not self.session_id:
            self.start_session("mcp_planner")
        
        self.recorder.record_thought(self.session_id, f"开始规划任务: {task_description}")
        
        # 使用mcp.so进行任务规划（如果可用）
        if self.mcp_so_loaded and hasattr(self.mcp_so, 'plan_task'):
            plan = self.mcp_so.plan_task(task_description, context or {})
            self.recorder.record_action(self.session_id, "mcp_so.plan_task", {
                "task_description": task_description,
                "context": context
            }, plan)
            return plan
        
        # 默认规划逻辑
        steps = [
            {"step": 1, "description": "分析任务需求", "tool": "thought_action_recorder"},
            {"step": 2, "description": "收集必要信息", "tool": None},
            {"step": 3, "description": "执行任务步骤", "tool": None},
            {"step": 4, "description": "验证结果", "tool": "test_issue_collector"}
        ]
        
        plan = {
            "task": task_description,
            "created_at": datetime.now().isoformat(),
            "steps": steps
        }
        
        self.recorder.record_action(self.session_id, "plan_task", {
            "task_description": task_description
        }, plan)
        
        return plan
    
    def execute_step(self, step, parameters=None):
        """执行计划中的步骤"""
        if not self.session_id:
            self.start_session("mcp_planner")
        
        self.recorder.record_thought(self.session_id, f"执行步骤: {step['description']}")
        
        tool_name = step.get('tool')
        if not tool_name:
            self.recorder.record_thought(self.session_id, f"步骤没有指定工具，跳过执行")
            return {"status": "skipped", "reason": "No tool specified"}
        
        tool = self.get_tool(tool_name)
        if not tool:
            self.recorder.record_thought(self.session_id, f"找不到工具: {tool_name}")
            return {"status": "error", "reason": f"Tool not found: {tool_name}"}
        
        try:
            # 确定要调用的方法
            method_name = parameters.pop("method", "execute") if parameters else "execute"
            method = getattr(tool, method_name, None)
            
            if not method or not callable(method):
                self.recorder.record_thought(self.session_id, f"工具 {tool_name} 没有方法 {method_name}")
                return {"status": "error", "reason": f"Method {method_name} not found in tool {tool_name}"}
            
            # 执行方法
            result = method(**(parameters or {}))
            
            self.recorder.record_action(self.session_id, f"{tool_name}.{method_name}", parameters, result)
            return {"status": "success", "result": result}
        
        except Exception as e:
            self.recorder.record_thought(self.session_id, f"执行步骤时出错: {e}")
            return {"status": "error", "reason": str(e)}
    
    def execute_plan(self, plan):
        """执行完整计划"""
        if not self.session_id:
            self.start_session("mcp_planner")
        
        self.recorder.record_thought(self.session_id, f"开始执行计划: {plan['task']}")
        
        results = []
        for step in plan['steps']:
            step_result = self.execute_step(step)
            results.append({
                "step": step['step'],
                "description": step['description'],
                "result": step_result
            })
            
            # 如果步骤执行失败，停止执行计划
            if step_result['status'] == 'error':
                self.recorder.record_thought(self.session_id, f"计划执行失败，停止执行")
                break
        
        return {
            "task": plan['task'],
            "executed_at": datetime.now().isoformat(),
            "results": results,
            "status": "completed" if all(r['result']['status'] == 'success' for r in results) else "failed"
        }
    
    def run_e2e_test(self, test_name, test_parameters=None):
        """运行端到端测试"""
        if not self.session_id:
            self.start_session("mcp_planner")
        
        self.recorder.record_thought(self.session_id, f"开始运行端到端测试: {test_name}")
        
        # 创建测试计划
        test_plan = {
            "task": f"运行端到端测试: {test_name}",
            "created_at": datetime.now().isoformat(),
            "steps": [
                {"step": 1, "description": "准备测试环境", "tool": "test_issue_collector"},
                {"step": 2, "description": "执行测试用例", "tool": "test_issue_collector"},
                {"step": 3, "description": "收集测试结果", "tool": "test_issue_collector"},
                {"step": 4, "description": "分析测试问题", "tool": "agent_problem_solver"}
            ]
        }
        
        # 执行测试计划
        test_result = self.execute_plan(test_plan)
        
        # 记录测试结果
        self.recorder.record_action(self.session_id, "run_e2e_test", {
            "test_name": test_name,
            "test_parameters": test_parameters
        }, test_result)
        
        return test_result
