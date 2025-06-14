# powerauto.aicorenew/mcp/mcp_coordinator/enhanced_mcp_coordinator.py

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from .shared_core_integration import create_shared_core_integrator, create_enhanced_dialog_processor
from .dialog_classifier import OneStepSuggestionGenerator, DialogType
from .mcp_coordinator import MCPCoordinator

class EnhancedMCPCoordinator(MCPCoordinator):
    """
    增强版MCP协调器
    集成shared_core架构，专门优化智能编辑器和Manus的对话框处理
    """
    
    def __init__(self, architecture_type: str = "consumer"):
        super().__init__()
        
        # Shared Core集成
        self.integrator = create_shared_core_integrator(architecture_type)
        self.enhanced_dialog_processor = create_enhanced_dialog_processor(self.integrator)
        
        # 专用组件
        self.suggestion_generator = OneStepSuggestionGenerator()
        
        # 性能统计
        self.stats = {
            "total_requests": 0,
            "successful_suggestions": 0,
            "average_response_time": 0.0,
            "dialog_type_distribution": {
                "thinking": 0,
                "observing": 0,
                "action": 0
            }
        }

    async def initialize(self) -> bool:
        """初始化增强协调器"""
        # 初始化基础MCP协调器
        base_init = await super().initialize()
        
        # 初始化Shared Core集成
        shared_core_init = await self.integrator.initialize_integration()
        
        self.logger.info("增强MCP协调器初始化完成", {
            "base_coordinator": base_init,
            "shared_core_integration": shared_core_init
        })
        
        return base_init and shared_core_init

    async def process_smart_editor_dialog(self, dialog_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理智能编辑器对话框
        专门优化的智能编辑器介入处理流程
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 提取对话内容和上下文
            dialog_content = dialog_data.get("content", "")
            context = dialog_data.get("context", {})
            context["source"] = "smart_editor"
            
            self.logger.info("处理智能编辑器对话", {
                "content_preview": dialog_content[:50],
                "file_type": context.get("file_type", "unknown"),
                "session_id": context.get("session_id", "unknown")
            })
            
            # 使用增强对话处理器
            suggestion = await self.enhanced_dialog_processor.process_dialog_with_logging(
                dialog_content, context
            )
            
            # 针对智能编辑器的特殊优化
            suggestion = await self._optimize_for_smart_editor(suggestion, context)
            
            # 更新统计
            self._update_stats(suggestion, time.time() - start_time)
            
            self.logger.info("智能编辑器对话处理完成", {
                "dialog_type": suggestion.get("dialog_type"),
                "confidence": suggestion.get("confidence"),
                "response_time": time.time() - start_time
            })
            
            return {
                "status": "success",
                "suggestion": suggestion,
                "response_time": time.time() - start_time,
                "source": "smart_editor"
            }
            
        except Exception as e:
            self.logger.error("智能编辑器对话处理失败", {"error": str(e)})
            return {
                "status": "error",
                "error": str(e),
                "response_time": time.time() - start_time,
                "source": "smart_editor"
            }

    async def process_manus_dialog(self, dialog_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理Manus对话框
        专门优化的Manus介入处理流程
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 提取对话内容和上下文
            dialog_content = dialog_data.get("content", "")
            context = dialog_data.get("context", {})
            context["source"] = "manus"
            
            self.logger.info("处理Manus对话", {
                "content_preview": dialog_content[:50],
                "user_id": context.get("user_id", "unknown"),
                "session_id": context.get("session_id", "unknown")
            })
            
            # 使用增强对话处理器
            suggestion = await self.enhanced_dialog_processor.process_dialog_with_logging(
                dialog_content, context
            )
            
            # 针对Manus的特殊优化
            suggestion = await self._optimize_for_manus(suggestion, context)
            
            # 更新统计
            self._update_stats(suggestion, time.time() - start_time)
            
            self.logger.info("Manus对话处理完成", {
                "dialog_type": suggestion.get("dialog_type"),
                "confidence": suggestion.get("confidence"),
                "response_time": time.time() - start_time
            })
            
            return {
                "status": "success",
                "suggestion": suggestion,
                "response_time": time.time() - start_time,
                "source": "manus"
            }
            
        except Exception as e:
            self.logger.error("Manus对话处理失败", {"error": str(e)})
            return {
                "status": "error",
                "error": str(e),
                "response_time": time.time() - start_time,
                "source": "manus"
            }

    async def _optimize_for_smart_editor(self, suggestion: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """针对智能编辑器的建议优化"""
        dialog_type = suggestion.get("dialog_type")
        
        # 根据文件类型优化建议
        file_type = context.get("file_type", "")
        if file_type:
            suggestion["file_type_specific"] = True
            
            if dialog_type == "action":
                # 为动作类建议添加编辑器特定的执行命令
                if file_type == "python":
                    suggestion["executable_command"]["editor_actions"] = [
                        "format_python_code",
                        "run_python_linter",
                        "auto_import_optimization"
                    ]
                elif file_type == "javascript":
                    suggestion["executable_command"]["editor_actions"] = [
                        "format_js_code", 
                        "run_eslint",
                        "auto_fix_syntax"
                    ]
            
            elif dialog_type == "observing":
                # 为观察类建议添加编辑器特定的查询
                suggestion["executable_command"]["editor_queries"] = [
                    f"check_{file_type}_syntax",
                    f"analyze_{file_type}_complexity",
                    f"get_{file_type}_metrics"
                ]
        
        # 添加编辑器上下文信息
        if context.get("current_line"):
            suggestion["context_aware"] = {
                "current_line": context["current_line"],
                "line_specific_suggestion": True
            }
        
        return suggestion

    async def _optimize_for_manus(self, suggestion: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """针对Manus的建议优化"""
        dialog_type = suggestion.get("dialog_type")
        
        # 根据用户上下文优化建议
        user_id = context.get("user_id")
        if user_id:
            suggestion["user_specific"] = True
            
            # 获取用户历史洞察
            historical_insights = await self.enhanced_dialog_processor.get_historical_insights(
                dialog_type, limit=5
            )
            
            if historical_insights.get("status") == "success":
                suggestion["historical_context"] = historical_insights["insights"]
        
        # 为Manus添加个性化元素
        if dialog_type == "action":
            suggestion["executable_command"]["manus_actions"] = [
                "create_personalized_workflow",
                "update_user_preferences", 
                "trigger_automation_sequence"
            ]
        elif dialog_type == "thinking":
            suggestion["executable_command"]["manus_analysis"] = [
                "analyze_user_behavior_pattern",
                "generate_personalization_insights",
                "recommend_workflow_optimizations"
            ]
        
        # 添加Manus特定的UI适应性
        user_preferences = context.get("user_preferences", {})
        if user_preferences:
            suggestion["ui_adaptation"] = {
                "theme": user_preferences.get("theme", "light"),
                "language": user_preferences.get("language", "en"),
                "layout_preference": user_preferences.get("layout", "default")
            }
        
        return suggestion

    def _update_stats(self, suggestion: Dict[str, Any], response_time: float):
        """更新性能统计"""
        if suggestion.get("confidence", 0) > 0.5:
            self.stats["successful_suggestions"] += 1
        
        # 更新平均响应时间
        total_requests = self.stats["total_requests"]
        current_avg = self.stats["average_response_time"]
        self.stats["average_response_time"] = (current_avg * (total_requests - 1) + response_time) / total_requests
        
        # 更新对话类型分布
        dialog_type = suggestion.get("dialog_type", "unknown")
        if dialog_type in self.stats["dialog_type_distribution"]:
            self.stats["dialog_type_distribution"][dialog_type] += 1

    async def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        success_rate = (self.stats["successful_suggestions"] / self.stats["total_requests"] 
                       if self.stats["total_requests"] > 0 else 0)
        
        return {
            "performance_stats": self.stats,
            "success_rate": success_rate,
            "health_check": await self.integrator.health_check(),
            "timestamp": time.time()
        }

    async def shutdown(self) -> bool:
        """关闭增强协调器"""
        # 关闭Shared Core集成
        shared_core_shutdown = await self.integrator.shutdown()
        
        # 关闭基础协调器
        base_shutdown = await super().shutdown()
        
        self.logger.info("增强MCP协调器关闭完成", {
            "shared_core_shutdown": shared_core_shutdown,
            "base_shutdown": base_shutdown
        })
        
        return shared_core_shutdown and base_shutdown

# CLI接口
async def main():
    """CLI主函数"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="增强MCP协调器")
    parser.add_argument("action", choices=["test_editor", "test_manus", "stats", "health"],
                       help="要执行的操作")
    parser.add_argument("--architecture", choices=["enterprise", "consumer", "opensource"],
                       default="consumer", help="架构类型")
    parser.add_argument("--data", help="输入数据(JSON格式)")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    coordinator = EnhancedMCPCoordinator(args.architecture)
    
    try:
        await coordinator.initialize()
        
        if args.action == "test_editor":
            # 测试智能编辑器对话
            test_data = json.loads(args.data) if args.data else {
                "content": "如何优化这段代码？",
                "context": {
                    "session_id": "test_001",
                    "file_type": "python",
                    "current_line": 42
                }
            }
            result = await coordinator.process_smart_editor_dialog(test_data)
            
        elif args.action == "test_manus":
            # 测试Manus对话
            test_data = json.loads(args.data) if args.data else {
                "content": "分析用户行为模式",
                "context": {
                    "session_id": "test_002",
                    "user_id": "user_123",
                    "current_page": "dashboard"
                }
            }
            result = await coordinator.process_manus_dialog(test_data)
            
        elif args.action == "stats":
            # 获取性能统计
            result = await coordinator.get_performance_stats()
            
        elif args.action == "health":
            # 健康检查
            result = await coordinator.integrator.health_check()
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return result
        
    finally:
        await coordinator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

