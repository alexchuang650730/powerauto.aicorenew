"""
Sequential Thinking适配器 - 提供任务拆解和反思能力
该模块封装了Sequential Thinking MCP的功能，提供标准化接口。
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

class SequentialThinkingAdapter:
    """Sequential Thinking适配器，提供任务拆解和反思能力"""
    
    def __init__(self):
        """初始化Sequential Thinking适配器"""
        self.logger = logging.getLogger("SequentialThinkingAdapter")
    
    def decompose_task(self, task_description: str, context: Optional[Dict] = None) -> Dict:
        """
        将任务分解为子任务
        
        Args:
            task_description: 任务描述
            context: 上下文信息
            
        Returns:
            Dict: 分解后的任务结构
        """
        self.logger.info(f"分解任务: {task_description}")
        
        # 实现Sequential Thinking的任务分解逻辑
        # 这里是简化实现，实际应用中需要更复杂的处理
        
        subtasks = []
        
        # 分析阶段
        subtasks.append({
            "id": "analyze",
            "description": f"分析{task_description}的需求和上下文",
            "estimated_time": "10分钟"
        })
        
        # 设计阶段
        subtasks.append({
            "id": "design",
            "description": f"设计{task_description}的解决方案",
            "estimated_time": "15分钟",
            "depends_on": ["analyze"]
        })
        
        # 实现阶段
        subtasks.append({
            "id": "implement",
            "description": f"实现{task_description}的解决方案",
            "estimated_time": "30分钟",
            "depends_on": ["design"]
        })
        
        # 测试阶段
        subtasks.append({
            "id": "test",
            "description": f"测试{task_description}的解决方案",
            "estimated_time": "15分钟",
            "depends_on": ["implement"]
        })
        
        # 部署阶段
        subtasks.append({
            "id": "deploy",
            "description": f"部署{task_description}的解决方案",
            "estimated_time": "10分钟",
            "depends_on": ["test"]
        })
        
        return {
            "task": task_description,
            "subtasks": subtasks,
            "context": context or {}
        }
    
    def create_todo_md(self, decomposed_task: Dict) -> str:
        """
        创建todo.md格式的任务清单
        
        Args:
            decomposed_task: 分解后的任务
            
        Returns:
            str: todo.md格式的任务清单
        """
        self.logger.info("创建todo.md任务清单")
        
        todo_lines = ["# 任务清单\n\n"]
        
        for subtask in decomposed_task["subtasks"]:
            status = "[ ]"  # 未完成状态
            todo_lines.append(f"{status} {subtask['description']} (id:{subtask['id']})\n")
        
        return "".join(todo_lines)
    
    def reflect_and_refine(self, plan: Dict) -> Dict:
        """
        反思和优化计划
        
        Args:
            plan: 执行计划
            
        Returns:
            Dict: 优化后的计划
        """
        self.logger.info("反思和优化计划")
        
        # 实现Sequential Thinking的反思和优化逻辑
        # 这里是简化实现，实际应用中需要更复杂的处理
        
        reflections = []
        optimizations = []
        
        # 检查计划的完整性
        if "task_structure" in plan and "execution_plans" in plan:
            reflections.append("计划结构完整，包含任务结构和执行计划")
        else:
            reflections.append("计划结构不完整，缺少任务结构或执行计划")
            optimizations.append("补充完整的任务结构和执行计划")
        
        # 检查任务依赖关系
        if "dependencies" in plan:
            reflections.append("计划包含任务依赖关系")
            
            # 检查是否有循环依赖
            dependencies = plan.get("dependencies", {})
            if self._has_circular_dependency(dependencies):
                reflections.append("发现循环依赖关系，可能导致执行阻塞")
                optimizations.append("解决循环依赖关系")
        else:
            reflections.append("计划缺少任务依赖关系")
            optimizations.append("添加任务依赖关系")
        
        # 检查执行顺序
        if "execution_order" in plan:
            reflections.append("计划包含执行顺序")
        else:
            reflections.append("计划缺少执行顺序")
            optimizations.append("添加明确的执行顺序")
        
        # 创建优化后的计划
        refined_plan = plan.copy()
        refined_plan["reflections"] = reflections
        refined_plan["optimizations"] = optimizations
        
        return refined_plan
    
    def _has_circular_dependency(self, dependencies: Dict) -> bool:
        """检查是否有循环依赖"""
        # 简化实现，实际应用中需要更复杂的检测算法
        for task_id, depends_on in dependencies.items():
            for dep_id in depends_on:
                if dep_id in dependencies and task_id in dependencies[dep_id]:
                    return True
        return False
    
    def update_todo_status(self, todo_md: str, task_id: str, completed: bool) -> str:
        """
        更新todo.md中任务的完成状态
        
        Args:
            todo_md: todo.md内容
            task_id: 任务ID
            completed: 是否完成
            
        Returns:
            str: 更新后的todo.md内容
        """
        self.logger.info(f"更新任务状态: {task_id}, 完成: {completed}")
        
        lines = todo_md.split("\n")
        for i, line in enumerate(lines):
            if f"(id:{task_id})" in line:
                if completed and "[ ]" in line:
                    lines[i] = line.replace("[ ]", "[x]")
                elif not completed and "[x]" in line:
                    lines[i] = line.replace("[x]", "[ ]")
        
        return "\n".join(lines)
