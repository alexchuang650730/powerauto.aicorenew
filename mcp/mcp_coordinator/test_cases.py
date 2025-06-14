# powerauto.aicorenew/mcp/mcp_coordinator/test_cases.py

import asyncio
import json
import time
from typing import Dict, Any
from .shared_core_integration import create_shared_core_integrator, create_enhanced_dialog_processor
from .dialog_classifier import OneStepSuggestionGenerator

class TestCaseRunner:
    """
    测试用例运行器
    专门用于运行智能编辑器和Manus的两条测试用例
    """
    
    def __init__(self, architecture_type: str = "consumer"):
        self.integrator = create_shared_core_integrator(architecture_type)
        self.dialog_processor = create_enhanced_dialog_processor(self.integrator)
        self.suggestion_generator = OneStepSuggestionGenerator()

    async def initialize(self):
        """初始化测试环境"""
        await self.integrator.initialize_integration()

    async def run_smart_editor_test(self) -> Dict[str, Any]:
        """
        测试用例1: 智能编辑器介入操作对话框提供智能一步直达建议
        """
        print("🧠 开始测试：智能编辑器介入操作对话框")
        
        # 模拟智能编辑器对话框数据
        test_scenarios = [
            {
                "dialog_content": "如何优化这段Python代码的性能？",
                "context": {
                    "source": "smart_editor",
                    "session_id": "editor_test_001",
                    "file_type": "python",
                    "code_snippet": "for i in range(1000000): result.append(i**2)",
                    "current_line": 42
                },
                "expected_type": "thinking"
            },
            {
                "dialog_content": "检查当前文件的语法错误",
                "context": {
                    "source": "smart_editor", 
                    "session_id": "editor_test_002",
                    "file_type": "javascript",
                    "file_path": "/src/main.js"
                },
                "expected_type": "observing"
            },
            {
                "dialog_content": "自动格式化当前代码",
                "context": {
                    "source": "smart_editor",
                    "session_id": "editor_test_003", 
                    "file_type": "python",
                    "selection": "lines 10-50"
                },
                "expected_type": "action"
            }
        ]
        
        results = []
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📝 子测试 {i}: {scenario['dialog_content']}")
            
            # 生成建议
            suggestion = await self.dialog_processor.process_dialog_with_logging(
                scenario["dialog_content"],
                scenario["context"]
            )
            
            # 验证结果
            is_correct_type = suggestion.get("dialog_type") == scenario["expected_type"]
            confidence = suggestion.get("confidence", 0.0)
            
            result = {
                "test_id": f"smart_editor_{i}",
                "dialog_content": scenario["dialog_content"],
                "expected_type": scenario["expected_type"],
                "actual_type": suggestion.get("dialog_type"),
                "confidence": confidence,
                "suggestion": suggestion,
                "type_match": is_correct_type,
                "high_confidence": confidence > 0.7,
                "success": is_correct_type and confidence > 0.5
            }
            
            results.append(result)
            
            print(f"   ✅ 类型: {suggestion.get('dialog_type')} (期望: {scenario['expected_type']})")
            print(f"   📊 置信度: {confidence:.2f}")
            print(f"   💡 建议: {suggestion.get('title', 'N/A')}")
            print(f"   🎯 成功: {'是' if result['success'] else '否'}")
        
        # 统计结果
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        summary = {
            "test_name": "智能编辑器介入操作对话框",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "results": results,
            "overall_success": success_rate >= 0.8
        }
        
        print(f"\n📊 智能编辑器测试总结:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功数: {successful_tests}")
        print(f"   成功率: {success_rate:.1%}")
        print(f"   整体评价: {'✅ 通过' if summary['overall_success'] else '❌ 需要改进'}")
        
        return summary

    async def run_manus_test(self) -> Dict[str, Any]:
        """
        测试用例2: Manus介入操作对话框提供智能一步直达建议
        """
        print("\n🌐 开始测试：Manus介入操作对话框")
        
        # 模拟Manus对话框数据
        test_scenarios = [
            {
                "dialog_content": "分析这个用户的行为模式并提供个性化建议",
                "context": {
                    "source": "manus",
                    "session_id": "manus_test_001",
                    "user_id": "user_12345",
                    "interaction_history": ["search", "click", "scroll"],
                    "current_page": "dashboard"
                },
                "expected_type": "thinking"
            },
            {
                "dialog_content": "查看当前用户的活跃状态",
                "context": {
                    "source": "manus",
                    "session_id": "manus_test_002",
                    "user_id": "user_67890",
                    "timestamp": time.time()
                },
                "expected_type": "observing"
            },
            {
                "dialog_content": "为用户创建个性化工作流",
                "context": {
                    "source": "manus",
                    "session_id": "manus_test_003",
                    "user_preferences": {"theme": "dark", "language": "zh-CN"},
                    "workflow_type": "automation"
                },
                "expected_type": "action"
            }
        ]
        
        results = []
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🎯 子测试 {i}: {scenario['dialog_content']}")
            
            # 生成建议
            suggestion = await self.dialog_processor.process_dialog_with_logging(
                scenario["dialog_content"],
                scenario["context"]
            )
            
            # 验证结果
            is_correct_type = suggestion.get("dialog_type") == scenario["expected_type"]
            confidence = suggestion.get("confidence", 0.0)
            
            result = {
                "test_id": f"manus_{i}",
                "dialog_content": scenario["dialog_content"],
                "expected_type": scenario["expected_type"],
                "actual_type": suggestion.get("dialog_type"),
                "confidence": confidence,
                "suggestion": suggestion,
                "type_match": is_correct_type,
                "high_confidence": confidence > 0.7,
                "success": is_correct_type and confidence > 0.5
            }
            
            results.append(result)
            
            print(f"   ✅ 类型: {suggestion.get('dialog_type')} (期望: {scenario['expected_type']})")
            print(f"   📊 置信度: {confidence:.2f}")
            print(f"   💡 建议: {suggestion.get('title', 'N/A')}")
            print(f"   🎯 成功: {'是' if result['success'] else '否'}")
        
        # 统计结果
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        summary = {
            "test_name": "Manus介入操作对话框",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "results": results,
            "overall_success": success_rate >= 0.8
        }
        
        print(f"\n📊 Manus测试总结:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功数: {successful_tests}")
        print(f"   成功率: {success_rate:.1%}")
        print(f"   整体评价: {'✅ 通过' if summary['overall_success'] else '❌ 需要改进'}")
        
        return summary

    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试用例"""
        print("🚀 开始运行PowerAutomation智能介入测试套件")
        print("=" * 60)
        
        await self.initialize()
        
        # 运行两条主要测试
        smart_editor_result = await self.run_smart_editor_test()
        manus_result = await self.run_manus_test()
        
        # 综合评估
        total_tests = smart_editor_result["total_tests"] + manus_result["total_tests"]
        total_successful = smart_editor_result["successful_tests"] + manus_result["successful_tests"]
        overall_success_rate = total_successful / total_tests if total_tests > 0 else 0
        
        final_result = {
            "test_suite": "PowerAutomation智能介入测试",
            "timestamp": time.time(),
            "smart_editor_test": smart_editor_result,
            "manus_test": manus_result,
            "overall_stats": {
                "total_tests": total_tests,
                "successful_tests": total_successful,
                "success_rate": overall_success_rate,
                "overall_pass": overall_success_rate >= 0.8
            }
        }
        
        print("\n" + "=" * 60)
        print("🏆 最终测试结果:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功数: {total_successful}")
        print(f"   整体成功率: {overall_success_rate:.1%}")
        print(f"   最终评价: {'🎉 测试通过！' if final_result['overall_stats']['overall_pass'] else '⚠️  需要优化'}")
        
        # 健康检查
        health_status = await self.integrator.health_check()
        final_result["health_check"] = health_status
        
        return final_result

    async def cleanup(self):
        """清理测试环境"""
        await self.integrator.shutdown()

# CLI接口
async def main():
    """主函数 - CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PowerAutomation智能介入测试套件")
    parser.add_argument("--test", choices=["all", "editor", "manus"], default="all",
                       help="选择要运行的测试")
    parser.add_argument("--architecture", choices=["enterprise", "consumer", "opensource"], 
                       default="consumer", help="架构类型")
    parser.add_argument("--output", help="输出结果到JSON文件")
    
    args = parser.parse_args()
    
    runner = TestCaseRunner(args.architecture)
    
    try:
        if args.test == "all":
            result = await runner.run_all_tests()
        elif args.test == "editor":
            await runner.initialize()
            result = await runner.run_smart_editor_test()
        elif args.test == "manus":
            await runner.initialize()
            result = await runner.run_manus_test()
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n📄 结果已保存到: {args.output}")
        
        return result
        
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

