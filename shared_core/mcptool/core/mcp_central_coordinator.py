"""
MCP中央协调器模块 - MCPCentralCoordinator

负责协调MCPPlanner和MCPBrainstorm，确保所有工具通过统一接口调用。
"""

import os
import sys
import json
from datetime import datetime
from .mcp_planner import MCPPlanner
from .mcp_brainstorm import MCPBrainstorm
from ..development_tools.thought_action_recorder import ThoughtActionRecorder

class MCPCentralCoordinator:
    def __init__(self):
        """初始化MCP中央协调器"""
        self.planner = MCPPlanner()
        self.brainstorm = MCPBrainstorm()
        self.recorder = ThoughtActionRecorder()
        
        # 会话ID
        self.session_id = None
    
    def start_session(self, agent_type):
        """启动新的会话"""
        self.session_id = self.recorder.start_session(agent_type)
        self.planner.session_id = self.session_id
        self.brainstorm.session_id = self.session_id
        return self.session_id
    
    def get_tool(self, tool_name):
        """获取工具实例，优先从MCPPlanner获取，如果不存在则从MCPBrainstorm获取"""
        tool = self.planner.get_tool(tool_name)
        if not tool:
            tool = self.brainstorm.get_tool(tool_name)
        return tool
    
    def list_tools(self):
        """列出所有可用工具"""
        planner_tools = self.planner.list_tools()
        brainstorm_tools = self.brainstorm.list_tools()
        return list(set(planner_tools + brainstorm_tools))
    
    def execute_tool(self, tool_name, method_name="execute", **parameters):
        """执行工具方法"""
        if not self.session_id:
            self.start_session("mcp_central_coordinator")
        
        self.recorder.record_thought(self.session_id, f"开始执行工具: {tool_name}.{method_name}")
        
        tool = self.get_tool(tool_name)
        if not tool:
            # 如果工具不存在，尝试通过MCPBrainstorm创建
            self.recorder.record_thought(self.session_id, f"工具 {tool_name} 不存在，尝试创建")
            
            tool_info = self.brainstorm.brainstorm_tool(f"创建一个名为 {tool_name} 的工具")
            tool = self.brainstorm.get_tool(tool_info["tool_name"])
            
            if not tool:
                self.recorder.record_thought(self.session_id, f"无法创建工具 {tool_name}")
                return {"status": "error", "reason": f"Tool not found and cannot be created: {tool_name}"}
        
        try:
            # 获取方法
            method = getattr(tool, method_name, None)
            if not method or not callable(method):
                self.recorder.record_thought(self.session_id, f"工具 {tool_name} 没有方法 {method_name}")
                return {"status": "error", "reason": f"Method {method_name} not found in tool {tool_name}"}
            
            # 执行方法
            result = method(**parameters)
            
            self.recorder.record_action(self.session_id, f"{tool_name}.{method_name}", parameters, result)
            return {"status": "success", "result": result}
        
        except Exception as e:
            self.recorder.record_thought(self.session_id, f"执行工具时出错: {e}")
            return {"status": "error", "reason": str(e)}
    
    def plan_and_execute(self, task_description, context=None):
        """规划并执行任务"""
        if not self.session_id:
            self.start_session("mcp_central_coordinator")
        
        self.recorder.record_thought(self.session_id, f"开始规划并执行任务: {task_description}")
        
        # 使用MCPPlanner规划任务
        plan = self.planner.plan_task(task_description, context)
        
        # 执行计划
        execution_result = self.planner.execute_plan(plan)
        
        return {
            "task": task_description,
            "plan": plan,
            "execution_result": execution_result
        }
    
    def run_e2e_test(self, component_name, test_parameters=None):
        """运行端到端测试"""
        if not self.session_id:
            self.start_session("mcp_central_coordinator")
        
        self.recorder.record_thought(self.session_id, f"开始运行端到端测试: {component_name}")
        
        # 确定测试类型
        if component_name.startswith("tool:"):
            # 工具测试
            tool_name = component_name[5:]
            tool = self.get_tool(tool_name)
            
            if tool:
                # 使用MCPPlanner或MCPBrainstorm运行测试
                if tool_name in self.planner.list_tools():
                    test_result = self.planner.run_e2e_test(tool_name, test_parameters)
                else:
                    test_result = self.brainstorm.run_e2e_test(tool_name, test_parameters)
            else:
                test_result = {"status": "error", "reason": f"Tool not found: {tool_name}"}
        
        elif component_name.startswith("agent:"):
            # 智能体测试
            agent_name = component_name[6:]
            
            # 创建智能体测试计划
            test_plan = {
                "task": f"运行智能体端到端测试: {agent_name}",
                "created_at": datetime.now().isoformat(),
                "steps": [
                    {"step": 1, "description": "准备测试环境", "tool": "test_issue_collector"},
                    {"step": 2, "description": "执行测试用例", "tool": "test_issue_collector"},
                    {"step": 3, "description": "收集测试结果", "tool": "test_issue_collector"},
                    {"step": 4, "description": "分析测试问题", "tool": "agent_problem_solver"}
                ]
            }
            
            # 执行测试计划
            test_result = self.planner.execute_plan(test_plan)
        
        else:
            # 默认为组件测试
            test_result = self.planner.run_e2e_test(component_name, test_parameters)
        
        self.recorder.record_action(self.session_id, "run_e2e_test", {
            "component_name": component_name,
            "test_parameters": test_parameters
        }, test_result)
        
        return test_result
    
    def sync_with_github(self, operation, parameters=None):
        """与GitHub同步"""
        if not self.session_id:
            self.start_session("mcp_central_coordinator")
        
        self.recorder.record_thought(self.session_id, f"开始与GitHub同步: {operation}")
        
        # 使用ReleaseManager工具
        release_manager = self.planner.get_tool("release_manager")
        if not release_manager:
            self.recorder.record_thought(self.session_id, "找不到ReleaseManager工具")
            return {"status": "error", "reason": "ReleaseManager tool not found"}
        
        try:
            # 执行同步操作
            if operation == "download":
                result = release_manager.download_release(parameters.get("repo_url"), parameters.get("local_path"))
            elif operation == "upload":
                result = release_manager.upload_code(parameters.get("local_path"), parameters.get("repo_url"), parameters.get("commit_message"))
            else:
                result = {"status": "error", "reason": f"Unknown operation: {operation}"}
            
            self.recorder.record_action(self.session_id, f"sync_with_github.{operation}", parameters, result)
            return {"status": "success", "result": result}
        
        except Exception as e:
            self.recorder.record_thought(self.session_id, f"与GitHub同步时出错: {e}")
            return {"status": "error", "reason": str(e)}
