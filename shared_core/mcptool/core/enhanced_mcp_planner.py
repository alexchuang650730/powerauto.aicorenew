"""
增强版MCP规划器 - 集成Sequential Thinking能力
该模块扩展了原有的MCP规划器，添加了任务拆解、阶段性反思和结构化输出能力。
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

# 导入原有MCP规划器 - 调整导入路径以适应主仓库结构
from agents.ppt_agent.core.mcp.mcp_planner import PlannerMCPCentralCoordinator
# 导入Sequential Thinking适配器 - 调整导入路径以适应主仓库结构
from agents.ppt_agent.core.mcp.sequential_thinking_adapter import SequentialThinkingAdapter

class EnhancedMCPPlanner:
    """增强版MCP规划器，集成Sequential Thinking能力"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化增强版MCP规划器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 初始化原有规划器
        self.original_planner = PlannerMCPCentralCoordinator(config_path)
        # 初始化Sequential Thinking适配器
        self.sequential_thinking = SequentialThinkingAdapter()
        # 初始化日志
        self.logger = logging.getLogger("EnhancedMCPPlanner")
        
        self.logger.info("增强版MCP规划器初始化完成")
    
    def plan(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """
        规划任务执行计划
        
        Args:
            task_description: 任务描述
            context: 上下文信息
            
        Returns:
            Dict: 任务执行计划
        """
        self.logger.info(f"开始规划任务: {task_description}")
        
        # 使用Sequential Thinking进行任务拆解
        decomposed_task = self.sequential_thinking.decompose_task(
            task_description, context
        )
        
        # 创建todo.md格式的任务清单
        todo_md = self.sequential_thinking.create_todo_md(decomposed_task)
        
        # 对每个子任务使用原始规划器生成详细计划
        detailed_plans = {}
        for subtask in decomposed_task["subtasks"]:
            subtask_plan = self.original_planner.execute_task(subtask["description"])
            detailed_plans[subtask["id"]] = subtask_plan
        
        # 整合所有计划
        integrated_plan = self._integrate_plans(decomposed_task, detailed_plans)
        
        # 进行阶段性反思和优化
        refined_plan = self.sequential_thinking.reflect_and_refine(integrated_plan)
        
        return {
            "original_task": task_description,
            "decomposed_task": decomposed_task,
            "todo_md": todo_md,
            "detailed_plans": detailed_plans,
            "integrated_plan": integrated_plan,
            "refined_plan": refined_plan
        }
    
    def _integrate_plans(self, decomposed_task: Dict, detailed_plans: Dict) -> Dict:
        """整合所有子任务计划"""
        return {
            "task_structure": decomposed_task,
            "execution_plans": detailed_plans,
            "execution_order": [subtask["id"] for subtask in decomposed_task["subtasks"]],
            "dependencies": self._extract_dependencies(decomposed_task)
        }
    
    def _extract_dependencies(self, decomposed_task: Dict) -> Dict:
        """提取任务依赖关系"""
        dependencies = {}
        for subtask in decomposed_task["subtasks"]:
            if "depends_on" in subtask:
                dependencies[subtask["id"]] = subtask["depends_on"]
        return dependencies
    
    def update_todo_status(self, todo_md: str, task_id: str, completed: bool) -> str:
        """更新todo.md中任务的完成状态"""
        return self.sequential_thinking.update_todo_status(todo_md, task_id, completed)
    
    def execute_plan(self, plan: Dict) -> Dict:
        """
        执行规划好的任务
        
        Args:
            plan: 任务执行计划
            
        Returns:
            Dict: 执行结果
        """
        self.logger.info("开始执行任务计划")
        
        results = {}
        execution_order = plan["integrated_plan"]["execution_order"]
        
        for task_id in execution_order:
            self.logger.info(f"执行任务: {task_id}")
            
            # 获取任务详情
            task_details = None
            for subtask in plan["decomposed_task"]["subtasks"]:
                if subtask["id"] == task_id:
                    task_details = subtask
                    break
            
            if not task_details:
                self.logger.warning(f"未找到任务详情: {task_id}")
                results[task_id] = {
                    "status": "failed",
                    "error": "未找到任务详情"
                }
                continue
            
            # 获取任务计划
            task_plan = plan["detailed_plans"].get(task_id)
            if not task_plan:
                self.logger.warning(f"未找到任务计划: {task_id}")
                results[task_id] = {
                    "status": "failed",
                    "error": "未找到任务计划"
                }
                continue
            
            # 执行任务
            try:
                # 这里应该实际执行任务
                # 为了演示，我们假设任务执行成功
                results[task_id] = {
                    "status": "success",
                    "task_details": task_details,
                    "task_plan": task_plan
                }
                
                # 更新todo.md
                plan["todo_md"] = self.update_todo_status(plan["todo_md"], task_id, True)
            except Exception as e:
                self.logger.error(f"执行任务失败: {task_id}, 错误: {e}")
                results[task_id] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return {
            "plan": plan,
            "results": results,
            "todo_md": plan["todo_md"]
        }
