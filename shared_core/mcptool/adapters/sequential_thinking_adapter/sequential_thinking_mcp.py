#!/usr/bin/env python3
"""
順序思考適配器MCP版本
提供任務拆解、反思和優化能力的MCP適配器
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent.parent))

from adapters.base_mcp import BaseMCP

logger = logging.getLogger(__name__)

class SequentialThinkingMCP(BaseMCP):
    """順序思考MCP適配器，提供任務拆解和反思能力"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="SequentialThinkingMCP")
        self.config = config or {}
        
        # 初始化指標
        self.metrics = {
            'task_decompositions': 0,
            'reflections_performed': 0,
            'todo_updates': 0,
            'success_count': 0,
            'error_count': 0,
            'total_execution_time': 0,
            'avg_response_time': 0
        }
        
        # 順序思考工具註冊表
        self.thinking_tools = {
            "task_decomposer": {
                "name": "任務分解器",
                "description": "將複雜任務分解為可執行的子任務",
                "category": "task_planning",
                "parameters": ["task_description", "context", "complexity_level"]
            },
            "reflection_engine": {
                "name": "反思引擎",
                "description": "分析和優化執行計劃",
                "category": "plan_optimization",
                "parameters": ["plan", "execution_history", "optimization_goals"]
            },
            "todo_manager": {
                "name": "待辦事項管理器",
                "description": "創建和管理todo.md格式的任務清單",
                "category": "task_management",
                "parameters": ["tasks", "format_type", "priority_level"]
            },
            "dependency_analyzer": {
                "name": "依賴關係分析器",
                "description": "分析任務間的依賴關係和執行順序",
                "category": "dependency_analysis",
                "parameters": ["tasks", "constraints", "optimization_criteria"]
            },
            "progress_tracker": {
                "name": "進度追蹤器",
                "description": "追蹤任務執行進度和狀態更新",
                "category": "progress_monitoring",
                "parameters": ["task_list", "completion_status", "time_tracking"]
            },
            "strategy_optimizer": {
                "name": "策略優化器",
                "description": "基於歷史數據優化執行策略",
                "category": "strategy_optimization",
                "parameters": ["historical_data", "performance_metrics", "optimization_targets"]
            }
        }
        
        logger.info("順序思考MCP適配器初始化完成")
    
    def decompose_task(self, task_description: str, context: Optional[Dict] = None, complexity_level: str = "medium") -> Dict[str, Any]:
        """
        將任務分解為子任務
        
        Args:
            task_description: 任務描述
            context: 上下文信息
            complexity_level: 複雜度級別 (simple, medium, complex)
            
        Returns:
            分解後的任務結構
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"分解任務: {task_description} (複雜度: {complexity_level})")
            
            # 根據複雜度確定分解策略
            if complexity_level == "simple":
                subtasks = self._create_simple_subtasks(task_description)
            elif complexity_level == "complex":
                subtasks = self._create_complex_subtasks(task_description)
            else:
                subtasks = self._create_medium_subtasks(task_description)
            
            # 添加依賴關係分析
            dependencies = self._analyze_dependencies(subtasks)
            
            # 估算時間和資源
            time_estimates = self._estimate_time_and_resources(subtasks)
            
            result = {
                "task_id": f"task_{int(time.time())}",
                "original_task": task_description,
                "complexity_level": complexity_level,
                "subtasks": subtasks,
                "dependencies": dependencies,
                "time_estimates": time_estimates,
                "context": context or {},
                "created_at": datetime.now().isoformat(),
                "total_estimated_time": sum(est.get("duration_minutes", 0) for est in time_estimates.values()),
                "critical_path": self._calculate_critical_path(subtasks, dependencies)
            }
            
            self.metrics['task_decompositions'] += 1
            self.metrics['success_count'] += 1
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"任務分解失敗: {e}")
            self.metrics['error_count'] += 1
            return {
                "status": "error",
                "task": task_description,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_simple_subtasks(self, task_description: str) -> List[Dict[str, Any]]:
        """創建簡單任務的子任務"""
        return [
            {
                "id": "analyze",
                "title": "需求分析",
                "description": f"分析{task_description}的具體需求",
                "priority": "high",
                "estimated_duration": 15
            },
            {
                "id": "execute",
                "title": "執行任務",
                "description": f"執行{task_description}的主要工作",
                "priority": "high",
                "estimated_duration": 30
            },
            {
                "id": "verify",
                "title": "驗證結果",
                "description": f"驗證{task_description}的執行結果",
                "priority": "medium",
                "estimated_duration": 10
            }
        ]
    
    def _create_medium_subtasks(self, task_description: str) -> List[Dict[str, Any]]:
        """創建中等複雜度任務的子任務"""
        return [
            {
                "id": "research",
                "title": "研究調研",
                "description": f"研究{task_description}的相關技術和方法",
                "priority": "high",
                "estimated_duration": 20
            },
            {
                "id": "design",
                "title": "方案設計",
                "description": f"設計{task_description}的解決方案",
                "priority": "high",
                "estimated_duration": 30
            },
            {
                "id": "implement",
                "title": "實施執行",
                "description": f"實施{task_description}的解決方案",
                "priority": "high",
                "estimated_duration": 45
            },
            {
                "id": "test",
                "title": "測試驗證",
                "description": f"測試{task_description}的實施結果",
                "priority": "medium",
                "estimated_duration": 20
            },
            {
                "id": "optimize",
                "title": "優化改進",
                "description": f"優化{task_description}的執行效果",
                "priority": "low",
                "estimated_duration": 15
            }
        ]
    
    def _create_complex_subtasks(self, task_description: str) -> List[Dict[str, Any]]:
        """創建複雜任務的子任務"""
        return [
            {
                "id": "requirement_analysis",
                "title": "需求分析",
                "description": f"深入分析{task_description}的需求和約束",
                "priority": "critical",
                "estimated_duration": 30
            },
            {
                "id": "feasibility_study",
                "title": "可行性研究",
                "description": f"評估{task_description}的技術和經濟可行性",
                "priority": "high",
                "estimated_duration": 25
            },
            {
                "id": "architecture_design",
                "title": "架構設計",
                "description": f"設計{task_description}的整體架構",
                "priority": "high",
                "estimated_duration": 40
            },
            {
                "id": "detailed_design",
                "title": "詳細設計",
                "description": f"完成{task_description}的詳細設計",
                "priority": "high",
                "estimated_duration": 35
            },
            {
                "id": "implementation",
                "title": "分階段實施",
                "description": f"分階段實施{task_description}",
                "priority": "high",
                "estimated_duration": 60
            },
            {
                "id": "integration_test",
                "title": "集成測試",
                "description": f"進行{task_description}的集成測試",
                "priority": "medium",
                "estimated_duration": 30
            },
            {
                "id": "performance_optimization",
                "title": "性能優化",
                "description": f"優化{task_description}的性能",
                "priority": "medium",
                "estimated_duration": 25
            },
            {
                "id": "deployment",
                "title": "部署上線",
                "description": f"部署{task_description}到生產環境",
                "priority": "high",
                "estimated_duration": 20
            }
        ]
    
    def _analyze_dependencies(self, subtasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """分析任務依賴關係"""
        dependencies = {}
        
        for i, task in enumerate(subtasks):
            task_id = task["id"]
            depends_on = []
            
            # 基於任務順序建立基本依賴關係
            if i > 0:
                depends_on.append(subtasks[i-1]["id"])
            
            # 基於任務類型建立特殊依賴關係
            if task_id == "test" or task_id == "integration_test":
                # 測試任務依賴於實施任務
                impl_tasks = [t["id"] for t in subtasks if "implement" in t["id"] or "execution" in t["id"]]
                depends_on.extend(impl_tasks)
            
            elif task_id == "deployment":
                # 部署任務依賴於測試任務
                test_tasks = [t["id"] for t in subtasks if "test" in t["id"]]
                depends_on.extend(test_tasks)
            
            elif task_id == "optimize" or task_id == "performance_optimization":
                # 優化任務依賴於基本實施
                impl_tasks = [t["id"] for t in subtasks if "implement" in t["id"] or "execute" in t["id"]]
                depends_on.extend(impl_tasks)
            
            # 去重
            dependencies[task_id] = list(set(depends_on))
        
        return dependencies
    
    def _estimate_time_and_resources(self, subtasks: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """估算時間和資源需求"""
        estimates = {}
        
        for task in subtasks:
            task_id = task["id"]
            base_duration = task.get("estimated_duration", 30)
            
            # 根據優先級調整時間估算
            priority_multiplier = {
                "critical": 1.2,
                "high": 1.0,
                "medium": 0.8,
                "low": 0.6
            }
            
            priority = task.get("priority", "medium")
            adjusted_duration = base_duration * priority_multiplier.get(priority, 1.0)
            
            estimates[task_id] = {
                "duration_minutes": int(adjusted_duration),
                "priority": priority,
                "resource_requirements": self._estimate_resources(task),
                "risk_level": self._assess_risk_level(task),
                "buffer_time": int(adjusted_duration * 0.2)  # 20% 緩衝時間
            }
        
        return estimates
    
    def _estimate_resources(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """估算資源需求"""
        task_type = task["id"]
        
        if "research" in task_type or "analysis" in task_type:
            return {"cpu": "low", "memory": "medium", "network": "high", "storage": "low"}
        elif "design" in task_type:
            return {"cpu": "medium", "memory": "high", "network": "low", "storage": "medium"}
        elif "implement" in task_type or "execute" in task_type:
            return {"cpu": "high", "memory": "high", "network": "medium", "storage": "high"}
        elif "test" in task_type:
            return {"cpu": "high", "memory": "medium", "network": "medium", "storage": "medium"}
        else:
            return {"cpu": "medium", "memory": "medium", "network": "medium", "storage": "medium"}
    
    def _assess_risk_level(self, task: Dict[str, Any]) -> str:
        """評估風險級別"""
        task_type = task["id"]
        priority = task.get("priority", "medium")
        
        if priority == "critical":
            return "high"
        elif "implement" in task_type or "deploy" in task_type:
            return "medium"
        elif "test" in task_type or "verify" in task_type:
            return "low"
        else:
            return "medium"
    
    def _calculate_critical_path(self, subtasks: List[Dict[str, Any]], dependencies: Dict[str, List[str]]) -> List[str]:
        """計算關鍵路徑"""
        # 簡化的關鍵路徑計算
        critical_path = []
        
        # 找到沒有依賴的起始任務
        start_tasks = [task["id"] for task in subtasks if not dependencies.get(task["id"], [])]
        
        if start_tasks:
            current_task = start_tasks[0]
            critical_path.append(current_task)
            
            # 沿著依賴鏈找到最長路徑
            while True:
                next_tasks = [task_id for task_id, deps in dependencies.items() if current_task in deps]
                if not next_tasks:
                    break
                
                # 選擇估算時間最長的下一個任務
                next_task = max(next_tasks, key=lambda t: next(
                    (task.get("estimated_duration", 0) for task in subtasks if task["id"] == t), 0
                ))
                critical_path.append(next_task)
                current_task = next_task
        
        return critical_path
    
    def create_todo_md(self, decomposed_task: Dict[str, Any], format_type: str = "standard") -> str:
        """
        創建todo.md格式的任務清單
        
        Args:
            decomposed_task: 分解後的任務
            format_type: 格式類型 (standard, detailed, minimal)
            
        Returns:
            todo.md格式的任務清單
        """
        try:
            self.logger.info("創建todo.md任務清單")
            
            lines = []
            
            # 標題
            lines.append(f"# {decomposed_task.get('original_task', '任務')} 執行清單\n\n")
            
            # 任務概要
            if format_type == "detailed":
                lines.append("## 📋 任務概要\n")
                lines.append(f"- **任務ID**: {decomposed_task.get('task_id', 'N/A')}\n")
                lines.append(f"- **複雜度**: {decomposed_task.get('complexity_level', 'medium')}\n")
                lines.append(f"- **預估總時間**: {decomposed_task.get('total_estimated_time', 0)} 分鐘\n")
                lines.append(f"- **創建時間**: {decomposed_task.get('created_at', 'N/A')}\n\n")
            
            # 子任務列表
            lines.append("## ✅ 任務清單\n\n")
            
            subtasks = decomposed_task.get("subtasks", [])
            time_estimates = decomposed_task.get("time_estimates", {})
            dependencies = decomposed_task.get("dependencies", {})
            
            for i, subtask in enumerate(subtasks, 1):
                task_id = subtask["id"]
                title = subtask.get("title", subtask.get("description", "未命名任務"))
                priority = subtask.get("priority", "medium")
                
                # 基本任務項
                status = "[ ]"  # 未完成狀態
                priority_icon = {"critical": "🔴", "high": "🟡", "medium": "🔵", "low": "⚪"}.get(priority, "🔵")
                
                if format_type == "minimal":
                    lines.append(f"{status} {title} (id:{task_id})\n")
                else:
                    lines.append(f"{status} {priority_icon} **{title}** (id:{task_id})\n")
                    
                    if format_type == "detailed":
                        # 詳細信息
                        lines.append(f"   - 描述: {subtask.get('description', '無描述')}\n")
                        lines.append(f"   - 優先級: {priority}\n")
                        
                        if task_id in time_estimates:
                            estimate = time_estimates[task_id]
                            lines.append(f"   - 預估時間: {estimate.get('duration_minutes', 0)} 分鐘\n")
                            lines.append(f"   - 風險級別: {estimate.get('risk_level', 'medium')}\n")
                        
                        if task_id in dependencies and dependencies[task_id]:
                            deps = ", ".join(dependencies[task_id])
                            lines.append(f"   - 依賴任務: {deps}\n")
                        
                        lines.append("\n")
            
            # 關鍵路徑
            if format_type == "detailed" and "critical_path" in decomposed_task:
                lines.append("## 🎯 關鍵路徑\n\n")
                critical_path = decomposed_task["critical_path"]
                for i, task_id in enumerate(critical_path):
                    task_title = next((t.get("title", t["id"]) for t in subtasks if t["id"] == task_id), task_id)
                    arrow = " → " if i < len(critical_path) - 1 else ""
                    lines.append(f"{task_title}{arrow}")
                lines.append("\n\n")
            
            # 進度統計
            if format_type != "minimal":
                lines.append("## 📊 進度統計\n\n")
                lines.append(f"- 總任務數: {len(subtasks)}\n")
                lines.append(f"- 已完成: 0\n")
                lines.append(f"- 進行中: 0\n")
                lines.append(f"- 待開始: {len(subtasks)}\n")
                lines.append(f"- 完成率: 0%\n\n")
            
            self.metrics['todo_updates'] += 1
            
            return "".join(lines)
            
        except Exception as e:
            self.logger.error(f"創建todo.md失敗: {e}")
            return f"# 任務清單創建失敗\n\n錯誤: {str(e)}\n"
    
    def reflect_and_optimize(self, plan: Dict[str, Any], execution_history: List[Dict] = None, optimization_goals: List[str] = None) -> Dict[str, Any]:
        """
        反思和優化計劃
        
        Args:
            plan: 執行計劃
            execution_history: 執行歷史
            optimization_goals: 優化目標
            
        Returns:
            優化後的計劃
        """
        start_time = time.time()
        
        try:
            self.logger.info("反思和優化計劃")
            
            execution_history = execution_history or []
            optimization_goals = optimization_goals or ["efficiency", "quality", "risk_reduction"]
            
            reflections = []
            optimizations = []
            recommendations = []
            
            # 結構完整性檢查
            structure_analysis = self._analyze_plan_structure(plan)
            reflections.extend(structure_analysis["reflections"])
            optimizations.extend(structure_analysis["optimizations"])
            
            # 依賴關係分析
            dependency_analysis = self._analyze_dependencies_quality(plan)
            reflections.extend(dependency_analysis["reflections"])
            optimizations.extend(dependency_analysis["optimizations"])
            
            # 時間估算分析
            time_analysis = self._analyze_time_estimates(plan)
            reflections.extend(time_analysis["reflections"])
            optimizations.extend(time_analysis["optimizations"])
            
            # 風險評估
            risk_analysis = self._analyze_risks(plan)
            reflections.extend(risk_analysis["reflections"])
            optimizations.extend(risk_analysis["optimizations"])
            
            # 基於執行歷史的優化
            if execution_history:
                history_analysis = self._analyze_execution_history(execution_history)
                reflections.extend(history_analysis["reflections"])
                optimizations.extend(history_analysis["optimizations"])
            
            # 生成改進建議
            recommendations = self._generate_recommendations(plan, optimization_goals)
            
            # 創建優化後的計劃
            optimized_plan = self._apply_optimizations(plan, optimizations)
            
            result = {
                "original_plan": plan,
                "optimized_plan": optimized_plan,
                "reflection_analysis": {
                    "reflections": reflections,
                    "optimizations": optimizations,
                    "recommendations": recommendations,
                    "optimization_goals": optimization_goals,
                    "analysis_timestamp": datetime.now().isoformat()
                },
                "improvement_metrics": self._calculate_improvement_metrics(plan, optimized_plan)
            }
            
            self.metrics['reflections_performed'] += 1
            self.metrics['success_count'] += 1
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"反思和優化失敗: {e}")
            self.metrics['error_count'] += 1
            return {
                "status": "error",
                "plan": plan,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_plan_structure(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """分析計劃結構"""
        reflections = []
        optimizations = []
        
        required_fields = ["subtasks", "dependencies", "time_estimates"]
        missing_fields = [field for field in required_fields if field not in plan]
        
        if missing_fields:
            reflections.append(f"計劃缺少必要字段: {', '.join(missing_fields)}")
            optimizations.append(f"添加缺少的字段: {', '.join(missing_fields)}")
        else:
            reflections.append("計劃結構完整，包含所有必要字段")
        
        # 檢查子任務數量
        subtasks = plan.get("subtasks", [])
        if len(subtasks) < 2:
            reflections.append("子任務數量過少，可能需要更詳細的分解")
            optimizations.append("增加更詳細的子任務分解")
        elif len(subtasks) > 10:
            reflections.append("子任務數量較多，可能需要分組管理")
            optimizations.append("將子任務分組或合併相似任務")
        else:
            reflections.append(f"子任務數量適中 ({len(subtasks)} 個)")
        
        return {"reflections": reflections, "optimizations": optimizations}
    
    def _analyze_dependencies_quality(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """分析依賴關係質量"""
        reflections = []
        optimizations = []
        
        dependencies = plan.get("dependencies", {})
        
        if not dependencies:
            reflections.append("計劃缺少任務依賴關係")
            optimizations.append("添加任務間的依賴關係")
            return {"reflections": reflections, "optimizations": optimizations}
        
        # 檢查循環依賴
        if self._has_circular_dependency(dependencies):
            reflections.append("發現循環依賴關係，可能導致執行阻塞")
            optimizations.append("解決循環依賴關係")
        else:
            reflections.append("依賴關係無循環，結構良好")
        
        # 檢查孤立任務
        all_tasks = set(plan.get("subtasks", [{}])[0].keys() if plan.get("subtasks") else [])
        dependent_tasks = set(dependencies.keys()) | set().union(*dependencies.values())
        isolated_tasks = all_tasks - dependent_tasks
        
        if isolated_tasks:
            reflections.append(f"發現孤立任務: {', '.join(isolated_tasks)}")
            optimizations.append("為孤立任務建立適當的依賴關係")
        
        return {"reflections": reflections, "optimizations": optimizations}
    
    def _analyze_time_estimates(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """分析時間估算"""
        reflections = []
        optimizations = []
        
        time_estimates = plan.get("time_estimates", {})
        
        if not time_estimates:
            reflections.append("計劃缺少時間估算")
            optimizations.append("為所有任務添加時間估算")
            return {"reflections": reflections, "optimizations": optimizations}
        
        # 檢查時間估算的合理性
        durations = [est.get("duration_minutes", 0) for est in time_estimates.values()]
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            total_duration = sum(durations)
            
            reflections.append(f"平均任務時間: {avg_duration:.1f} 分鐘")
            reflections.append(f"總預估時間: {total_duration} 分鐘")
            
            # 檢查是否有異常長的任務
            long_tasks = [task_id for task_id, est in time_estimates.items() 
                         if est.get("duration_minutes", 0) > avg_duration * 2]
            
            if long_tasks:
                reflections.append(f"發現異常長的任務: {', '.join(long_tasks)}")
                optimizations.append("考慮將長任務進一步分解")
        
        return {"reflections": reflections, "optimizations": optimizations}
    
    def _analyze_risks(self, plan: Dict[str, Any]) -> Dict[str, List[str]]:
        """分析風險"""
        reflections = []
        optimizations = []
        
        time_estimates = plan.get("time_estimates", {})
        
        # 統計風險級別
        risk_levels = {}
        for est in time_estimates.values():
            risk = est.get("risk_level", "medium")
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        if risk_levels:
            reflections.append(f"風險分布: {risk_levels}")
            
            high_risk_count = risk_levels.get("high", 0)
            if high_risk_count > len(time_estimates) * 0.3:
                reflections.append("高風險任務比例較高")
                optimizations.append("為高風險任務制定風險緩解措施")
        
        return {"reflections": reflections, "optimizations": optimizations}
    
    def _analyze_execution_history(self, execution_history: List[Dict]) -> Dict[str, List[str]]:
        """分析執行歷史"""
        reflections = []
        optimizations = []
        
        if not execution_history:
            return {"reflections": reflections, "optimizations": optimizations}
        
        # 分析完成率
        completed_tasks = [h for h in execution_history if h.get("status") == "completed"]
        completion_rate = len(completed_tasks) / len(execution_history) * 100
        
        reflections.append(f"歷史完成率: {completion_rate:.1f}%")
        
        if completion_rate < 80:
            optimizations.append("提高任務完成率，分析失敗原因")
        
        # 分析時間偏差
        time_deviations = []
        for history in execution_history:
            estimated = history.get("estimated_time", 0)
            actual = history.get("actual_time", 0)
            if estimated > 0:
                deviation = (actual - estimated) / estimated * 100
                time_deviations.append(deviation)
        
        if time_deviations:
            avg_deviation = sum(time_deviations) / len(time_deviations)
            reflections.append(f"平均時間偏差: {avg_deviation:.1f}%")
            
            if abs(avg_deviation) > 20:
                optimizations.append("調整時間估算方法，提高準確性")
        
        return {"reflections": reflections, "optimizations": optimizations}
    
    def _generate_recommendations(self, plan: Dict[str, Any], optimization_goals: List[str]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        for goal in optimization_goals:
            if goal == "efficiency":
                recommendations.append("並行執行無依賴關係的任務")
                recommendations.append("優化關鍵路徑上的任務")
            elif goal == "quality":
                recommendations.append("增加質量檢查點")
                recommendations.append("為關鍵任務添加審核步驟")
            elif goal == "risk_reduction":
                recommendations.append("為高風險任務準備備選方案")
                recommendations.append("增加緩衝時間")
        
        return recommendations
    
    def _apply_optimizations(self, plan: Dict[str, Any], optimizations: List[str]) -> Dict[str, Any]:
        """應用優化建議"""
        optimized_plan = plan.copy()
        
        # 這裡可以實現具體的優化邏輯
        # 目前返回原計劃加上優化標記
        optimized_plan["applied_optimizations"] = optimizations
        optimized_plan["optimization_timestamp"] = datetime.now().isoformat()
        
        return optimized_plan
    
    def _calculate_improvement_metrics(self, original_plan: Dict[str, Any], optimized_plan: Dict[str, Any]) -> Dict[str, Any]:
        """計算改進指標"""
        return {
            "optimization_count": len(optimized_plan.get("applied_optimizations", [])),
            "structure_completeness": self._calculate_completeness_score(optimized_plan),
            "estimated_efficiency_gain": "10-15%",  # 簡化計算
            "risk_reduction": "medium"
        }
    
    def _calculate_completeness_score(self, plan: Dict[str, Any]) -> float:
        """計算完整性評分"""
        required_fields = ["subtasks", "dependencies", "time_estimates"]
        present_fields = sum(1 for field in required_fields if field in plan and plan[field])
        return present_fields / len(required_fields)
    
    def _has_circular_dependency(self, dependencies: Dict[str, List[str]]) -> bool:
        """檢查是否有循環依賴"""
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in dependencies:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return True
        return False
    
    def update_todo_status(self, todo_md: str, task_id: str, completed: bool) -> str:
        """
        更新todo.md中任務的完成狀態
        
        Args:
            todo_md: todo.md內容
            task_id: 任務ID
            completed: 是否完成
            
        Returns:
            更新後的todo.md內容
        """
        try:
            self.logger.info(f"更新任務狀態: {task_id}, 完成: {completed}")
            
            lines = todo_md.split("\n")
            updated = False
            
            for i, line in enumerate(lines):
                if f"(id:{task_id})" in line:
                    if completed and "[ ]" in line:
                        lines[i] = line.replace("[ ]", "[x]")
                        updated = True
                    elif not completed and "[x]" in line:
                        lines[i] = line.replace("[x]", "[ ]")
                        updated = True
            
            if updated:
                self.metrics['todo_updates'] += 1
                
                # 更新進度統計
                lines = self._update_progress_statistics(lines)
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"更新todo狀態失敗: {e}")
            return todo_md
    
    def _update_progress_statistics(self, lines: List[str]) -> List[str]:
        """更新進度統計"""
        try:
            # 計算完成狀態
            total_tasks = 0
            completed_tasks = 0
            
            for line in lines:
                if "[ ]" in line and "(id:" in line:
                    total_tasks += 1
                elif "[x]" in line and "(id:" in line:
                    total_tasks += 1
                    completed_tasks += 1
            
            if total_tasks > 0:
                completion_rate = (completed_tasks / total_tasks) * 100
                in_progress = 0  # 簡化處理
                pending = total_tasks - completed_tasks
                
                # 更新統計部分
                for i, line in enumerate(lines):
                    if "- 總任務數:" in line:
                        lines[i] = f"- 總任務數: {total_tasks}\n"
                    elif "- 已完成:" in line:
                        lines[i] = f"- 已完成: {completed_tasks}\n"
                    elif "- 進行中:" in line:
                        lines[i] = f"- 進行中: {in_progress}\n"
                    elif "- 待開始:" in line:
                        lines[i] = f"- 待開始: {pending}\n"
                    elif "- 完成率:" in line:
                        lines[i] = f"- 完成率: {completion_rate:.1f}%\n"
            
            return lines
            
        except Exception as e:
            self.logger.error(f"更新進度統計失敗: {e}")
            return lines
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理輸入數據
        
        Args:
            input_data: 輸入數據字典
            
        Returns:
            處理結果字典
        """
        start_time = time.time()
        
        try:
            if not self.validate_input(input_data):
                return {
                    "status": "error",
                    "message": "輸入數據無效",
                    "timestamp": datetime.now().isoformat()
                }
            
            action = input_data.get("action", "")
            parameters = input_data.get("parameters", {})
            
            if action == "decompose_task":
                task_description = parameters.get("task_description", "")
                context = parameters.get("context", {})
                complexity_level = parameters.get("complexity_level", "medium")
                result = self.decompose_task(task_description, context, complexity_level)
                
            elif action == "create_todo_md":
                decomposed_task = parameters.get("decomposed_task", {})
                format_type = parameters.get("format_type", "standard")
                result = {"todo_md": self.create_todo_md(decomposed_task, format_type)}
                
            elif action == "reflect_and_optimize":
                plan = parameters.get("plan", {})
                execution_history = parameters.get("execution_history", [])
                optimization_goals = parameters.get("optimization_goals", [])
                result = self.reflect_and_optimize(plan, execution_history, optimization_goals)
                
            elif action == "update_todo_status":
                todo_md = parameters.get("todo_md", "")
                task_id = parameters.get("task_id", "")
                completed = parameters.get("completed", False)
                result = {"updated_todo_md": self.update_todo_status(todo_md, task_id, completed)}
                
            elif action == "get_capabilities":
                result = {"capabilities": self.get_capabilities()}
                
            elif action == "get_tools":
                result = {"tools": self.get_thinking_tools()}
                
            elif action == "get_status":
                result = self.get_thinking_status()
                
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {action}",
                    "timestamp": datetime.now().isoformat()
                }
            
            execution_time = time.time() - start_time
            self._update_metrics(execution_time)
            
            return {
                "status": "success",
                "action": action,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['error_count'] += 1
            self.logger.error(f"順序思考處理失敗: {e}")
            
            return {
                "status": "error",
                "message": str(e),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get("action", "")
        parameters = input_data.get("parameters", {})
        
        if action == "decompose_task":
            return "task_description" in parameters
        elif action == "create_todo_md":
            return "decomposed_task" in parameters
        elif action == "reflect_and_optimize":
            return "plan" in parameters
        elif action == "update_todo_status":
            return all(key in parameters for key in ["todo_md", "task_id", "completed"])
        elif action in ["get_capabilities", "get_tools", "get_status"]:
            return True
        
        return False
    
    def get_capabilities(self) -> List[str]:
        """獲取適配器能力列表"""
        return [
            "task_decomposition",
            "sequential_planning",
            "dependency_analysis",
            "time_estimation",
            "risk_assessment",
            "todo_management",
            "progress_tracking",
            "reflection_optimization",
            "critical_path_analysis",
            "strategy_optimization"
        ]
    
    def get_thinking_tools(self) -> Dict[str, Any]:
        """獲取順序思考工具列表"""
        return self.thinking_tools
    
    def get_thinking_status(self) -> Dict[str, Any]:
        """獲取順序思考狀態"""
        return {
            "is_available": True,
            "tools_available": len(self.thinking_tools),
            "metrics": self.metrics,
            "capabilities": self.get_capabilities(),
            "last_activity": datetime.now().isoformat()
        }
    
    def _update_metrics(self, execution_time: float):
        """更新執行指標"""
        self.metrics['total_execution_time'] += execution_time
        total_operations = (self.metrics['task_decompositions'] + 
                          self.metrics['reflections_performed'] + 
                          self.metrics['todo_updates'])
        if total_operations > 0:
            self.metrics['avg_response_time'] = self.metrics['total_execution_time'] / total_operations

# 測試代碼
if __name__ == "__main__":
    # 創建順序思考適配器
    thinking_adapter = SequentialThinkingMCP()
    
    # 測試任務分解
    print("=== 測試任務分解 ===")
    decompose_input = {
        "action": "decompose_task",
        "parameters": {
            "task_description": "開發一個Web應用程序",
            "context": {"technology": "Python Flask", "deadline": "2週"},
            "complexity_level": "complex"
        }
    }
    
    result = thinking_adapter.process(decompose_input)
    print(f"任務分解結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 測試創建todo.md
    if result['status'] == 'success':
        print("\n=== 測試創建todo.md ===")
        todo_input = {
            "action": "create_todo_md",
            "parameters": {
                "decomposed_task": result['result'],
                "format_type": "detailed"
            }
        }
        
        todo_result = thinking_adapter.process(todo_input)
        print(f"Todo.md內容:\n{todo_result['result']['todo_md']}")
        
        # 測試反思和優化
        print("\n=== 測試反思和優化 ===")
        reflect_input = {
            "action": "reflect_and_optimize",
            "parameters": {
                "plan": result['result'],
                "optimization_goals": ["efficiency", "quality"]
            }
        }
        
        reflect_result = thinking_adapter.process(reflect_input)
        print(f"反思優化結果: {json.dumps(reflect_result['result']['reflection_analysis'], indent=2, ensure_ascii=False)}")

