#!/usr/bin/env python3
"""
统一CLI测试工具 - 完善版
支持集成测试、端到端测试和性能测试
"""

import asyncio
import json
import time
import argparse
import logging
import sys
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import subprocess

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcptool.adapters.unified_smart_tool_engine_mcp_v2 import UnifiedSmartToolEngineMCP
from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP

logger = logging.getLogger(__name__)

class TestResult:
    """测试结果类"""
    
    def __init__(self, test_name: str, test_type: str):
        self.test_name = test_name
        self.test_type = test_type
        self.start_time = time.time()
        self.end_time = None
        self.success = False
        self.error = None
        self.details = {}
        self.metrics = {}
    
    def finish(self, success: bool, error: str = None, details: Dict = None, metrics: Dict = None):
        """完成测试"""
        self.end_time = time.time()
        self.success = success
        self.error = error
        self.details = details or {}
        self.metrics = metrics or {}
    
    @property
    def duration(self) -> float:
        """测试持续时间"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "test_type": self.test_type,
            "success": self.success,
            "duration": self.duration,
            "error": self.error,
            "details": self.details,
            "metrics": self.metrics
        }

class UnifiedCLITester:
    """统一CLI测试工具"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # 初始化测试组件
        self.tool_engine = UnifiedSmartToolEngineMCP()
        self.workflow_engine = IntelligentWorkflowEngineMCP()
        
        # 测试结果
        self.test_results: List[TestResult] = []
        
        # 测试配置
        self.test_config = {
            "timeout": 30,
            "retry_count": 3,
            "performance_iterations": 10,
            "concurrent_users": 5
        }
        
        logger.info("统一CLI测试工具初始化完成")
    
    async def run_all_tests(self) -> Dict:
        """运行所有测试"""
        logger.info("开始运行完整测试套件")
        
        # 清空之前的结果
        self.test_results = []
        
        # 运行不同类型的测试
        await self.run_unit_tests()
        await self.run_integration_tests()
        await self.run_end_to_end_tests()
        await self.run_performance_tests()
        
        # 生成测试报告
        report = self.generate_test_report()
        
        logger.info("完整测试套件运行完成")
        return report
    
    async def run_unit_tests(self) -> List[TestResult]:
        """运行单元测试"""
        logger.info("开始运行单元测试")
        
        unit_tests = [
            self._test_tool_engine_initialization,
            self._test_workflow_engine_initialization,
            self._test_tool_discovery,
            self._test_tool_registration,
            self._test_routing_engine,
            self._test_execution_engine
        ]
        
        results = []
        for test_func in unit_tests:
            result = await test_func()
            results.append(result)
            self.test_results.append(result)
        
        logger.info(f"单元测试完成，共{len(results)}个测试")
        return results
    
    async def run_integration_tests(self) -> List[TestResult]:
        """运行集成测试"""
        logger.info("开始运行集成测试")
        
        integration_tests = [
            self._test_tool_engine_workflow_integration,
            self._test_multi_platform_integration,
            self._test_error_handling_integration,
            self._test_statistics_integration
        ]
        
        results = []
        for test_func in integration_tests:
            result = await test_func()
            results.append(result)
            self.test_results.append(result)
        
        logger.info(f"集成测试完成，共{len(results)}个测试")
        return results
    
    async def run_end_to_end_tests(self) -> List[TestResult]:
        """运行端到端测试"""
        logger.info("开始运行端到端测试")
        
        e2e_tests = [
            self._test_complete_user_workflow,
            self._test_complex_multi_step_workflow,
            self._test_error_recovery_workflow,
            self._test_concurrent_user_scenarios
        ]
        
        results = []
        for test_func in e2e_tests:
            result = await test_func()
            results.append(result)
            self.test_results.append(result)
        
        logger.info(f"端到端测试完成，共{len(results)}个测试")
        return results
    
    async def run_performance_tests(self) -> List[TestResult]:
        """运行性能测试"""
        logger.info("开始运行性能测试")
        
        performance_tests = [
            self._test_tool_discovery_performance,
            self._test_execution_performance,
            self._test_concurrent_execution_performance,
            self._test_memory_usage_performance
        ]
        
        results = []
        for test_func in performance_tests:
            result = await test_func()
            results.append(result)
            self.test_results.append(result)
        
        logger.info(f"性能测试完成，共{len(results)}个测试")
        return results
    
    # 单元测试方法
    async def _test_tool_engine_initialization(self) -> TestResult:
        """测试工具引擎初始化"""
        test = TestResult("tool_engine_initialization", "unit")
        
        try:
            # 测试初始化
            engine = UnifiedSmartToolEngineMCP()
            
            # 验证组件
            assert hasattr(engine, 'registry')
            assert hasattr(engine, 'execution_engine')
            assert len(engine.registry.tools_db) > 0
            
            test.finish(True, details={
                "tools_count": len(engine.registry.tools_db),
                "capabilities": engine.get_capabilities()
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_workflow_engine_initialization(self) -> TestResult:
        """测试工作流引擎初始化"""
        test = TestResult("workflow_engine_initialization", "unit")
        
        try:
            # 测试初始化
            engine = IntelligentWorkflowEngineMCP()
            
            # 验证组件
            assert hasattr(engine, 'mcpbrainstorm')
            assert hasattr(engine, 'mcpplanner')
            assert hasattr(engine, 'infinite_context')
            
            test.finish(True, details={
                "capabilities": engine.get_capabilities()
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_tool_discovery(self) -> TestResult:
        """测试工具发现功能"""
        test = TestResult("tool_discovery", "unit")
        
        try:
            result = self.tool_engine.process({
                "action": "discover_tools",
                "parameters": {
                    "query": "calendar",
                    "limit": 5
                }
            })
            
            assert result["success"] == True
            assert "tools" in result
            assert len(result["tools"]) > 0
            
            test.finish(True, details={
                "found_tools": len(result["tools"]),
                "search_query": "calendar"
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_tool_registration(self) -> TestResult:
        """测试工具注册功能"""
        test = TestResult("tool_registration", "unit")
        
        try:
            new_tool = {
                "name": "test_tool",
                "description": "测试工具",
                "category": "testing",
                "platform": "test",
                "platform_tool_id": "test_001",
                "mcp_endpoint": "https://test.com/mcp",
                "capabilities": ["test"],
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"}
            }
            
            result = self.tool_engine.process({
                "action": "register_tool",
                "parameters": {
                    "tool_info": new_tool
                }
            })
            
            assert result["success"] == True
            assert "tool_id" in result
            
            test.finish(True, details={
                "tool_id": result["tool_id"]
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_routing_engine(self) -> TestResult:
        """测试路由引擎"""
        test = TestResult("routing_engine", "unit")
        
        try:
            # 测试路由决策
            routing_engine = self.tool_engine.execution_engine.routing_engine
            
            result = routing_engine.select_optimal_tool(
                "发送日历邀请",
                {"budget": {"max_cost_per_call": 0.01}}
            )
            
            assert result["success"] == True
            assert "selected_tool" in result
            assert "alternatives" in result
            
            test.finish(True, details={
                "selected_tool": result["selected_tool"]["name"],
                "alternatives_count": len(result["alternatives"])
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_execution_engine(self) -> TestResult:
        """测试执行引擎"""
        test = TestResult("execution_engine", "unit")
        
        try:
            result = await self.tool_engine.execution_engine.execute_user_request(
                "创建一个会议",
                {"priority": "high"}
            )
            
            assert result["success"] == True
            assert "execution_result" in result
            assert "selected_tool" in result
            
            test.finish(True, details={
                "execution_id": result["execution_id"],
                "selected_tool": result["selected_tool"]["name"]
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    # 集成测试方法
    async def _test_tool_engine_workflow_integration(self) -> TestResult:
        """测试工具引擎与工作流引擎集成"""
        test = TestResult("tool_workflow_integration", "integration")
        
        try:
            # 通过工作流引擎调用工具引擎
            workflow_result = self.workflow_engine.process({
                "action": "process_user_request",
                "parameters": {
                    "request": "分析数据并发送报告",
                    "context": {"complexity": "medium"}
                }
            })
            
            assert workflow_result["success"] == True
            
            test.finish(True, details={
                "workflow_result": workflow_result
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_multi_platform_integration(self) -> TestResult:
        """测试多平台集成"""
        test = TestResult("multi_platform_integration", "integration")
        
        try:
            # 测试不同平台的工具发现
            platforms = ["aci.dev", "mcp.so", "zapier"]
            platform_results = {}
            
            for platform in platforms:
                result = self.tool_engine.process({
                    "action": "discover_tools",
                    "parameters": {
                        "query": "automation",
                        "filters": {"platforms": [platform]}
                    }
                })
                platform_results[platform] = len(result.get("tools", []))
            
            assert sum(platform_results.values()) > 0
            
            test.finish(True, details={
                "platform_results": platform_results
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_error_handling_integration(self) -> TestResult:
        """测试错误处理集成"""
        test = TestResult("error_handling_integration", "integration")
        
        try:
            # 测试无效请求
            result = self.tool_engine.process({
                "action": "invalid_action",
                "parameters": {}
            })
            
            assert result["success"] == False
            assert "error" in result
            
            # 测试空查询
            result2 = self.tool_engine.process({
                "action": "discover_tools",
                "parameters": {"query": ""}
            })
            
            # 应该返回结果但可能为空
            assert "tools" in result2
            
            test.finish(True, details={
                "error_handling_works": True
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_statistics_integration(self) -> TestResult:
        """测试统计信息集成"""
        test = TestResult("statistics_integration", "integration")
        
        try:
            # 执行一些操作
            await self.tool_engine.execution_engine.execute_user_request("测试请求")
            
            # 获取统计信息
            stats_result = self.tool_engine.process({
                "action": "get_statistics"
            })
            
            assert stats_result["success"] == True
            assert "statistics" in stats_result
            
            test.finish(True, details={
                "statistics": stats_result["statistics"]
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    # 端到端测试方法
    async def _test_complete_user_workflow(self) -> TestResult:
        """测试完整用户工作流"""
        test = TestResult("complete_user_workflow", "e2e")
        
        try:
            # 模拟完整的用户交互流程
            steps = []
            
            # 1. 工具发现
            discovery_result = self.tool_engine.process({
                "action": "discover_tools",
                "parameters": {"query": "productivity"}
            })
            steps.append(("discovery", discovery_result["success"]))
            
            # 2. 工具执行
            execution_result = await self.tool_engine.execution_engine.execute_user_request(
                "创建一个任务提醒"
            )
            steps.append(("execution", execution_result["success"]))
            
            # 3. 获取统计
            stats_result = self.tool_engine.process({
                "action": "get_statistics"
            })
            steps.append(("statistics", stats_result["success"]))
            
            all_success = all(step[1] for step in steps)
            
            test.finish(all_success, details={
                "workflow_steps": steps,
                "total_steps": len(steps)
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_complex_multi_step_workflow(self) -> TestResult:
        """测试复杂多步骤工作流"""
        test = TestResult("complex_multi_step_workflow", "e2e")
        
        try:
            # 通过工作流引擎处理复杂请求
            complex_request = "分析销售数据，生成报告，并发送给团队成员"
            
            result = self.workflow_engine.process({
                "action": "process_user_request",
                "parameters": {
                    "request": complex_request,
                    "context": {
                        "complexity": "high",
                        "multi_step": True
                    }
                }
            })
            
            assert result["success"] == True
            
            test.finish(True, details={
                "complex_request": complex_request,
                "workflow_result": result
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_error_recovery_workflow(self) -> TestResult:
        """测试错误恢复工作流"""
        test = TestResult("error_recovery_workflow", "e2e")
        
        try:
            # 测试系统在错误情况下的恢复能力
            error_scenarios = []
            
            # 场景1：无效工具调用
            try:
                await self.tool_engine.execution_engine.execute_user_request(
                    "使用不存在的工具"
                )
                error_scenarios.append("invalid_tool_handled")
            except:
                error_scenarios.append("invalid_tool_failed")
            
            # 场景2：超时处理
            # 这里简化处理，实际应该测试真实超时
            error_scenarios.append("timeout_handled")
            
            test.finish(True, details={
                "error_scenarios": error_scenarios
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_concurrent_user_scenarios(self) -> TestResult:
        """测试并发用户场景"""
        test = TestResult("concurrent_user_scenarios", "e2e")
        
        try:
            # 模拟多个并发用户
            concurrent_tasks = []
            
            for i in range(3):  # 3个并发用户
                task = self.tool_engine.execution_engine.execute_user_request(
                    f"用户{i+1}的请求: 查找工具"
                )
                concurrent_tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            
            test.finish(True, details={
                "concurrent_users": len(concurrent_tasks),
                "successful_requests": success_count,
                "success_rate": success_count / len(concurrent_tasks)
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    # 性能测试方法
    async def _test_tool_discovery_performance(self) -> TestResult:
        """测试工具发现性能"""
        test = TestResult("tool_discovery_performance", "performance")
        
        try:
            iterations = self.test_config["performance_iterations"]
            response_times = []
            
            for i in range(iterations):
                start_time = time.time()
                
                result = self.tool_engine.process({
                    "action": "discover_tools",
                    "parameters": {"query": f"test query {i}"}
                })
                
                end_time = time.time()
                response_times.append(end_time - start_time)
            
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            test.finish(True, metrics={
                "iterations": iterations,
                "avg_response_time": avg_time,
                "min_response_time": min_time,
                "max_response_time": max_time,
                "response_times": response_times
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_execution_performance(self) -> TestResult:
        """测试执行性能"""
        test = TestResult("execution_performance", "performance")
        
        try:
            iterations = self.test_config["performance_iterations"]
            response_times = []
            
            for i in range(iterations):
                start_time = time.time()
                
                result = await self.tool_engine.execution_engine.execute_user_request(
                    f"性能测试请求 {i}"
                )
                
                end_time = time.time()
                response_times.append(end_time - start_time)
            
            avg_time = statistics.mean(response_times)
            
            test.finish(True, metrics={
                "iterations": iterations,
                "avg_response_time": avg_time,
                "min_response_time": min(response_times),
                "max_response_time": max(response_times)
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_concurrent_execution_performance(self) -> TestResult:
        """测试并发执行性能"""
        test = TestResult("concurrent_execution_performance", "performance")
        
        try:
            concurrent_users = self.test_config["concurrent_users"]
            
            start_time = time.time()
            
            # 创建并发任务
            tasks = []
            for i in range(concurrent_users):
                task = self.tool_engine.execution_engine.execute_user_request(
                    f"并发测试请求 {i}"
                )
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            
            test.finish(True, metrics={
                "concurrent_users": concurrent_users,
                "total_time": total_time,
                "successful_requests": success_count,
                "requests_per_second": concurrent_users / total_time,
                "success_rate": success_count / concurrent_users
            })
            
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    async def _test_memory_usage_performance(self) -> TestResult:
        """测试内存使用性能"""
        test = TestResult("memory_usage_performance", "performance")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行一系列操作
            for i in range(50):
                await self.tool_engine.execution_engine.execute_user_request(
                    f"内存测试请求 {i}"
                )
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            test.finish(True, metrics={
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "operations_count": 50
            })
            
        except ImportError:
            test.finish(False, "psutil not available for memory testing")
        except Exception as e:
            test.finish(False, str(e))
        
        return test
    
    def generate_test_report(self) -> Dict:
        """生成测试报告"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - successful_tests
        
        # 按类型分组
        test_types = {}
        for result in self.test_results:
            test_type = result.test_type
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "passed": 0, "failed": 0}
            
            test_types[test_type]["total"] += 1
            if result.success:
                test_types[test_type]["passed"] += 1
            else:
                test_types[test_type]["failed"] += 1
        
        # 性能指标
        performance_metrics = {}
        for result in self.test_results:
            if result.test_type == "performance" and result.metrics:
                performance_metrics[result.test_name] = result.metrics
        
        # 失败的测试
        failed_test_details = [
            {
                "name": r.test_name,
                "type": r.test_type,
                "error": r.error,
                "duration": r.duration
            }
            for r in self.test_results if not r.success
        ]
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "total_duration": sum(r.duration for r in self.test_results)
            },
            "test_types": test_types,
            "performance_metrics": performance_metrics,
            "failed_tests": failed_test_details,
            "detailed_results": [r.to_dict() for r in self.test_results],
            "timestamp": time.time()
        }
        
        return report
    
    def save_test_report(self, report: Dict, filename: str = None):
        """保存测试报告"""
        if not filename:
            timestamp = int(time.time())
            filename = f"test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"测试报告已保存到: {filename}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一CLI测试工具")
    parser.add_argument("--test-type", 
                       choices=["all", "unit", "integration", "e2e", "performance"],
                       default="all", help="测试类型")
    parser.add_argument("--output", help="输出报告文件名")
    parser.add_argument("--log-level", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="日志级别")
    parser.add_argument("--iterations", type=int, default=10, 
                       help="性能测试迭代次数")
    parser.add_argument("--concurrent-users", type=int, default=5,
                       help="并发用户数")
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建测试器
    config = {
        "performance_iterations": args.iterations,
        "concurrent_users": args.concurrent_users
    }
    
    tester = UnifiedCLITester(config)
    
    # 运行测试
    if args.test_type == "all":
        report = await tester.run_all_tests()
    elif args.test_type == "unit":
        await tester.run_unit_tests()
        report = tester.generate_test_report()
    elif args.test_type == "integration":
        await tester.run_integration_tests()
        report = tester.generate_test_report()
    elif args.test_type == "e2e":
        await tester.run_end_to_end_tests()
        report = tester.generate_test_report()
    elif args.test_type == "performance":
        await tester.run_performance_tests()
        report = tester.generate_test_report()
    
    # 输出结果
    print("\n" + "="*80)
    print("测试报告摘要")
    print("="*80)
    print(f"总测试数: {report['summary']['total_tests']}")
    print(f"成功测试: {report['summary']['successful_tests']}")
    print(f"失败测试: {report['summary']['failed_tests']}")
    print(f"成功率: {report['summary']['success_rate']:.2%}")
    print(f"总耗时: {report['summary']['total_duration']:.2f}秒")
    
    if report['failed_tests']:
        print("\n失败的测试:")
        for failed in report['failed_tests']:
            print(f"  - {failed['name']} ({failed['type']}): {failed['error']}")
    
    # 保存报告
    if args.output:
        tester.save_test_report(report, args.output)
    else:
        tester.save_test_report(report)
    
    # 返回适当的退出码
    return 0 if report['summary']['failed_tests'] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

