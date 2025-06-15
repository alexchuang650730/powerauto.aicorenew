#!/usr/bin/env python3
"""
MCPTool统一CLI测试工具
支持集成测试、端到端测试和性能测试
"""

import argparse
import asyncio
import json
import logging
import time
import sys
from pathlib import Path
from typing import Dict, List, Any

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from adapters.unified_smart_tool_engine_mcp import UnifiedSmartToolEngineMCP
from adapters.infinite_context_adapter_mcp import InfiniteContextAdapterMCP
from adapters.development_tools.agent_problem_solver_mcp import AgentProblemSolverMCP
from adapters.development_tools.thought_action_recorder_mcp import ThoughtActionRecorderMCP
from adapters.development_tools.release_manager_mcp import ReleaseManagerMCP

logger = logging.getLogger(__name__)

class MCPToolCLITester:
    """MCPTool CLI测试器"""
    
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {}
        
        # 初始化适配器
        self.adapters = {
            "unified_tool_engine": UnifiedSmartToolEngineMCP(),
            "infinite_context": InfiniteContextAdapterMCP(),
            "agent_problem_solver": AgentProblemSolverMCP(),
            "thought_action_recorder": ThoughtActionRecorderMCP(),
            "release_manager": ReleaseManagerMCP()
        }
    
    async def run_integration_tests(self, test_type: str = "all") -> Dict[str, Any]:
        """运行集成测试"""
        logger.info(f"开始运行集成测试: {test_type}")
        
        results = {
            "test_type": "integration",
            "test_category": test_type,
            "start_time": time.time(),
            "tests": []
        }
        
        if test_type in ["all", "multi-model-sync"]:
            await self._test_multi_model_sync(results)
        
        if test_type in ["all", "mcp-coordinator"]:
            await self._test_mcp_coordinator(results)
        
        if test_type in ["all", "tool-discovery"]:
            await self._test_tool_discovery(results)
        
        if test_type in ["all", "component"]:
            await self._test_component_functionality(results)
        
        if test_type in ["all", "mcp-compliance"]:
            await self._test_mcp_compliance(results)
        
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        results["total_tests"] = len(results["tests"])
        results["passed_tests"] = len([t for t in results["tests"] if t["status"] == "passed"])
        results["success_rate"] = results["passed_tests"] / max(results["total_tests"], 1)
        
        return results
    
    async def run_e2e_tests(self, test_type: str = "all") -> Dict[str, Any]:
        """运行端到端测试"""
        logger.info(f"开始运行端到端测试: {test_type}")
        
        results = {
            "test_type": "e2e",
            "test_category": test_type,
            "start_time": time.time(),
            "workflows": []
        }
        
        if test_type in ["all", "release-pipeline"]:
            await self._test_release_pipeline(results)
        
        if test_type in ["all", "thought-action-training"]:
            await self._test_thought_action_training(results)
        
        if test_type in ["all", "tool-discovery-deployment"]:
            await self._test_tool_discovery_deployment(results)
        
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        results["total_workflows"] = len(results["workflows"])
        results["passed_workflows"] = len([w for w in results["workflows"] if w["status"] == "passed"])
        results["success_rate"] = results["passed_workflows"] / max(results["total_workflows"], 1)
        
        return results
    
    async def run_performance_tests(self, test_type: str = "all", **kwargs) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info(f"开始运行性能测试: {test_type}")
        
        results = {
            "test_type": "performance",
            "test_category": test_type,
            "start_time": time.time(),
            "metrics": []
        }
        
        if test_type in ["all", "concurrent"]:
            threads = kwargs.get("threads", 5)
            await self._test_concurrent_performance(results, threads)
        
        if test_type in ["all", "response-time"]:
            duration = kwargs.get("duration", 60)
            await self._test_response_time(results, duration)
        
        if test_type in ["all", "resource-usage"]:
            monitor = kwargs.get("monitor", ["cpu", "memory"])
            await self._test_resource_usage(results, monitor)
        
        if test_type in ["all", "stability"]:
            duration = kwargs.get("duration", 300)
            await self._test_stability(results, duration)
        
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        
        return results
    
    # 集成测试方法
    async def _test_multi_model_sync(self, results: Dict):
        """测试多模型协同"""
        test_name = "多模型协同测试"
        logger.info(f"执行: {test_name}")
        
        try:
            start_time = time.time()
            
            # 1. 工具发现
            discovery_result = self.adapters["unified_tool_engine"].process({
                "action": "discover_tools",
                "parameters": {
                    "query": "数据分析",
                    "source": "both",
                    "limit": 10
                }
            })
            
            # 2. 智能执行
            execution_result = self.adapters["unified_tool_engine"].process({
                "action": "smart_execute",
                "parameters": {
                    "intent": "分析销售数据并生成报告",
                    "context": {
                        "data_source": "sales_data.csv",
                        "output_format": "pdf"
                    }
                }
            })
            
            # 3. 上下文增强
            context_result = self.adapters["infinite_context"].process({
                "action": "enhance_context",
                "parameters": {
                    "context": execution_result,
                    "enhancement_type": "memory_integration"
                }
            })
            
            duration = time.time() - start_time
            
            test_result = {
                "name": test_name,
                "status": "passed" if all([
                    discovery_result.get("success"),
                    execution_result.get("success"),
                    context_result.get("success")
                ]) else "failed",
                "duration": duration,
                "details": {
                    "discovery": discovery_result.get("success", False),
                    "execution": execution_result.get("success", False),
                    "context_enhancement": context_result.get("success", False)
                }
            }
            
        except Exception as e:
            test_result = {
                "name": test_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["tests"].append(test_result)
    
    async def _test_mcp_coordinator(self, results: Dict):
        """测试MCP协调器集成"""
        test_name = "MCP协调器集成测试"
        logger.info(f"执行: {test_name}")
        
        try:
            start_time = time.time()
            
            # 1. 问题分析
            problem_result = self.adapters["agent_problem_solver"].process({
                "action": "analyze_problem",
                "parameters": {
                    "problem_description": "系统响应时间过长",
                    "context": {"system": "web_application", "users": 1000}
                }
            })
            
            # 2. 思考记录
            thought_result = self.adapters["thought_action_recorder"].process({
                "action": "record_thought",
                "parameters": {
                    "thought": "需要优化数据库查询和缓存策略",
                    "context": problem_result
                }
            })
            
            # 3. 工具执行
            tool_result = self.adapters["unified_tool_engine"].process({
                "action": "execute_tool",
                "parameters": {
                    "tool_id": "data_analyzer",
                    "arguments": {
                        "data_source": "performance_logs",
                        "analysis_type": "bottleneck_detection"
                    }
                }
            })
            
            duration = time.time() - start_time
            
            test_result = {
                "name": test_name,
                "status": "passed" if all([
                    problem_result.get("success"),
                    thought_result.get("success"),
                    tool_result.get("success")
                ]) else "failed",
                "duration": duration,
                "details": {
                    "problem_analysis": problem_result.get("success", False),
                    "thought_recording": thought_result.get("success", False),
                    "tool_execution": tool_result.get("success", False)
                }
            }
            
        except Exception as e:
            test_result = {
                "name": test_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["tests"].append(test_result)
    
    async def _test_tool_discovery(self, results: Dict):
        """测试工具发现功能"""
        test_name = "工具发现测试"
        logger.info(f"执行: {test_name}")
        
        try:
            start_time = time.time()
            
            # 测试不同的搜索场景
            test_cases = [
                {"query": "文件处理", "expected_min": 1},
                {"query": "数据分析", "expected_min": 1},
                {"query": "代码生成", "expected_min": 1},
                {"category": "development", "expected_min": 1}
            ]
            
            all_passed = True
            case_results = []
            
            for case in test_cases:
                case_result = self.adapters["unified_tool_engine"].process({
                    "action": "discover_tools",
                    "parameters": case
                })
                
                if case_result.get("success"):
                    total_count = case_result["results"]["total_count"]
                    passed = total_count >= case["expected_min"]
                else:
                    passed = False
                
                case_results.append({
                    "case": case,
                    "passed": passed,
                    "result_count": case_result.get("results", {}).get("total_count", 0)
                })
                
                if not passed:
                    all_passed = False
            
            duration = time.time() - start_time
            
            test_result = {
                "name": test_name,
                "status": "passed" if all_passed else "failed",
                "duration": duration,
                "details": {
                    "test_cases": case_results,
                    "total_cases": len(test_cases),
                    "passed_cases": len([c for c in case_results if c["passed"]])
                }
            }
            
        except Exception as e:
            test_result = {
                "name": test_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["tests"].append(test_result)
    
    async def _test_component_functionality(self, results: Dict):
        """测试单个组件功能"""
        test_name = "组件功能测试"
        logger.info(f"执行: {test_name}")
        
        try:
            start_time = time.time()
            
            component_tests = []
            
            # 测试每个适配器的基本功能
            for adapter_name, adapter in self.adapters.items():
                try:
                    # 测试能力获取
                    capabilities = adapter.get_capabilities()
                    
                    # 测试输入验证
                    valid_input = {"action": "test", "parameters": {}}
                    validation_result = adapter.validate_input(valid_input)
                    
                    component_tests.append({
                        "adapter": adapter_name,
                        "capabilities_count": len(capabilities),
                        "validation_passed": validation_result,
                        "status": "passed"
                    })
                    
                except Exception as e:
                    component_tests.append({
                        "adapter": adapter_name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            duration = time.time() - start_time
            passed_components = len([t for t in component_tests if t["status"] == "passed"])
            
            test_result = {
                "name": test_name,
                "status": "passed" if passed_components == len(self.adapters) else "failed",
                "duration": duration,
                "details": {
                    "component_tests": component_tests,
                    "total_components": len(self.adapters),
                    "passed_components": passed_components
                }
            }
            
        except Exception as e:
            test_result = {
                "name": test_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["tests"].append(test_result)
    
    async def _test_mcp_compliance(self, results: Dict):
        """测试MCP协议合规性"""
        test_name = "MCP协议合规性测试"
        logger.info(f"执行: {test_name}")
        
        try:
            start_time = time.time()
            
            compliance_tests = []
            
            for adapter_name, adapter in self.adapters.items():
                compliance_score = 0
                max_score = 5
                
                # 检查必需方法
                if hasattr(adapter, 'process'):
                    compliance_score += 1
                if hasattr(adapter, 'get_capabilities'):
                    compliance_score += 1
                if hasattr(adapter, 'validate_input'):
                    compliance_score += 1
                
                # 检查返回格式
                try:
                    test_result = adapter.process({"action": "test", "parameters": {}})
                    if isinstance(test_result, dict) and "success" in test_result:
                        compliance_score += 1
                except:
                    pass
                
                # 检查错误处理
                try:
                    error_result = adapter.process({"invalid": "input"})
                    if isinstance(error_result, dict) and error_result.get("success") == False:
                        compliance_score += 1
                except:
                    pass
                
                compliance_tests.append({
                    "adapter": adapter_name,
                    "score": compliance_score,
                    "max_score": max_score,
                    "compliance_rate": compliance_score / max_score,
                    "status": "passed" if compliance_score >= 4 else "failed"
                })
            
            duration = time.time() - start_time
            passed_adapters = len([t for t in compliance_tests if t["status"] == "passed"])
            
            test_result = {
                "name": test_name,
                "status": "passed" if passed_adapters == len(self.adapters) else "failed",
                "duration": duration,
                "details": {
                    "compliance_tests": compliance_tests,
                    "total_adapters": len(self.adapters),
                    "compliant_adapters": passed_adapters,
                    "avg_compliance_rate": sum([t["compliance_rate"] for t in compliance_tests]) / len(compliance_tests)
                }
            }
            
        except Exception as e:
            test_result = {
                "name": test_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["tests"].append(test_result)
    
    # 端到端测试方法
    async def _test_release_pipeline(self, results: Dict):
        """测试完整发布流程"""
        workflow_name = "完整发布流程测试"
        logger.info(f"执行工作流: {workflow_name}")
        
        try:
            start_time = time.time()
            
            # 1. 发布准备
            prepare_result = self.adapters["release_manager"].process({
                "action": "prepare_release",
                "parameters": {
                    "version": "2.0.0",
                    "project": "mcptool",
                    "branch": "main"
                }
            })
            
            # 2. 代码检测
            analyze_result = self.adapters["unified_tool_engine"].process({
                "action": "execute_tool",
                "parameters": {
                    "tool_id": "code_generator",
                    "arguments": {
                        "operation": "quality_check",
                        "project_path": "/home/ubuntu/powerautomation"
                    }
                }
            })
            
            # 3. 测试执行
            test_result = self.adapters["unified_tool_engine"].process({
                "action": "smart_execute",
                "parameters": {
                    "intent": "运行所有测试用例",
                    "context": {"test_suite": "full", "coverage": "required"}
                }
            })
            
            # 4. 部署验证
            deploy_result = self.adapters["release_manager"].process({
                "action": "deploy_release",
                "parameters": {
                    "version": "2.0.0",
                    "environment": "staging",
                    "validation": True
                }
            })
            
            duration = time.time() - start_time
            
            workflow_result = {
                "name": workflow_name,
                "status": "passed" if all([
                    prepare_result.get("success"),
                    analyze_result.get("success"),
                    test_result.get("success"),
                    deploy_result.get("success")
                ]) else "failed",
                "duration": duration,
                "stages": {
                    "prepare": prepare_result.get("success", False),
                    "analyze": analyze_result.get("success", False),
                    "test": test_result.get("success", False),
                    "deploy": deploy_result.get("success", False)
                }
            }
            
        except Exception as e:
            workflow_result = {
                "name": workflow_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["workflows"].append(workflow_result)
    
    async def _test_thought_action_training(self, results: Dict):
        """测试思考-行动训练流程"""
        workflow_name = "思考-行动训练流程测试"
        logger.info(f"执行工作流: {workflow_name}")
        
        try:
            start_time = time.time()
            
            # 1. 数据收集
            collect_result = self.adapters["thought_action_recorder"].process({
                "action": "collect_training_data",
                "parameters": {
                    "scenario": "problem_solving",
                    "samples": 100,
                    "quality_threshold": 0.8
                }
            })
            
            # 2. 上下文增强
            enhance_result = self.adapters["infinite_context"].process({
                "action": "enhance_training_data",
                "parameters": {
                    "data": collect_result,
                    "enhancement_type": "context_expansion"
                }
            })
            
            # 3. 训练执行
            train_result = self.adapters["unified_tool_engine"].process({
                "action": "smart_execute",
                "parameters": {
                    "intent": "执行SRT训练",
                    "context": {
                        "training_data": enhance_result,
                        "model_type": "thought_action",
                        "epochs": 10
                    }
                }
            })
            
            # 4. 模型评估
            eval_result = self.adapters["agent_problem_solver"].process({
                "action": "evaluate_model",
                "parameters": {
                    "model": train_result,
                    "test_cases": ["reasoning", "planning", "execution"],
                    "metrics": ["accuracy", "coherence", "efficiency"]
                }
            })
            
            duration = time.time() - start_time
            
            workflow_result = {
                "name": workflow_name,
                "status": "passed" if all([
                    collect_result.get("success"),
                    enhance_result.get("success"),
                    train_result.get("success"),
                    eval_result.get("success")
                ]) else "failed",
                "duration": duration,
                "stages": {
                    "collect": collect_result.get("success", False),
                    "enhance": enhance_result.get("success", False),
                    "train": train_result.get("success", False),
                    "evaluate": eval_result.get("success", False)
                }
            }
            
        except Exception as e:
            workflow_result = {
                "name": workflow_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["workflows"].append(workflow_result)
    
    async def _test_tool_discovery_deployment(self, results: Dict):
        """测试工具发现和部署流程"""
        workflow_name = "工具发现和部署流程测试"
        logger.info(f"执行工作流: {workflow_name}")
        
        try:
            start_time = time.time()
            
            # 1. 工具生成
            generate_result = self.adapters["unified_tool_engine"].process({
                "action": "smart_execute",
                "parameters": {
                    "intent": "创建新的数据可视化工具",
                    "context": {
                        "tool_type": "visualization",
                        "target_platform": "web",
                        "features": ["charts", "dashboards", "export"]
                    }
                }
            })
            
            # 2. 测试验证
            validate_result = self.adapters["unified_tool_engine"].process({
                "action": "execute_tool",
                "parameters": {
                    "tool_id": "code_generator",
                    "arguments": {
                        "operation": "test_generation",
                        "target": generate_result
                    }
                }
            })
            
            # 3. 质量分析
            quality_result = self.adapters["agent_problem_solver"].process({
                "action": "analyze_quality",
                "parameters": {
                    "artifact": validate_result,
                    "criteria": ["functionality", "performance", "security"],
                    "threshold": 0.85
                }
            })
            
            # 4. 自动部署
            deploy_result = self.adapters["release_manager"].process({
                "action": "deploy_tool",
                "parameters": {
                    "tool": quality_result,
                    "environment": "production",
                    "monitoring": True
                }
            })
            
            duration = time.time() - start_time
            
            workflow_result = {
                "name": workflow_name,
                "status": "passed" if all([
                    generate_result.get("success"),
                    validate_result.get("success"),
                    quality_result.get("success"),
                    deploy_result.get("success")
                ]) else "failed",
                "duration": duration,
                "stages": {
                    "generate": generate_result.get("success", False),
                    "validate": validate_result.get("success", False),
                    "quality": quality_result.get("success", False),
                    "deploy": deploy_result.get("success", False)
                }
            }
            
        except Exception as e:
            workflow_result = {
                "name": workflow_name,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["workflows"].append(workflow_result)
    
    # 性能测试方法
    async def _test_concurrent_performance(self, results: Dict, threads: int):
        """测试并发性能"""
        metric_name = f"并发性能测试 ({threads} 线程)"
        logger.info(f"执行: {metric_name}")
        
        try:
            start_time = time.time()
            
            # 创建并发任务
            tasks = []
            for i in range(threads):
                task = self._concurrent_task(i)
                tasks.append(task)
            
            # 并发执行
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计结果
            successful_tasks = len([r for r in task_results if not isinstance(r, Exception)])
            failed_tasks = threads - successful_tasks
            
            duration = time.time() - start_time
            throughput = successful_tasks / duration
            
            metric_result = {
                "name": metric_name,
                "threads": threads,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": successful_tasks / threads,
                "duration": duration,
                "throughput": throughput,
                "avg_task_time": duration / threads
            }
            
        except Exception as e:
            metric_result = {
                "name": metric_name,
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["metrics"].append(metric_result)
    
    async def _concurrent_task(self, task_id: int) -> Dict:
        """并发任务"""
        try:
            result = self.adapters["unified_tool_engine"].process({
                "action": "discover_tools",
                "parameters": {
                    "query": f"task_{task_id}",
                    "limit": 5
                }
            })
            return {"task_id": task_id, "success": result.get("success", False)}
        except Exception as e:
            return {"task_id": task_id, "success": False, "error": str(e)}
    
    async def _test_response_time(self, results: Dict, duration: int):
        """测试响应时间"""
        metric_name = f"响应时间测试 ({duration}秒)"
        logger.info(f"执行: {metric_name}")
        
        try:
            start_time = time.time()
            response_times = []
            
            while time.time() - start_time < duration:
                request_start = time.time()
                
                result = self.adapters["unified_tool_engine"].process({
                    "action": "get_performance_metrics"
                })
                
                request_end = time.time()
                response_time = request_end - request_start
                response_times.append(response_time)
                
                # 短暂休息
                await asyncio.sleep(0.1)
            
            # 计算统计数据
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            metric_result = {
                "name": metric_name,
                "total_requests": len(response_times),
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "duration": duration
            }
            
        except Exception as e:
            metric_result = {
                "name": metric_name,
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["metrics"].append(metric_result)
    
    async def _test_resource_usage(self, results: Dict, monitor: List[str]):
        """测试资源使用率"""
        metric_name = f"资源使用率测试 ({', '.join(monitor)})"
        logger.info(f"执行: {metric_name}")
        
        try:
            import psutil
            
            start_time = time.time()
            
            # 获取初始资源状态
            initial_cpu = psutil.cpu_percent()
            initial_memory = psutil.virtual_memory().percent
            
            # 执行一些操作
            for i in range(10):
                result = self.adapters["unified_tool_engine"].process({
                    "action": "smart_execute",
                    "parameters": {
                        "intent": f"测试资源使用 {i}",
                        "context": {"load_test": True}
                    }
                })
                await asyncio.sleep(0.5)
            
            # 获取最终资源状态
            final_cpu = psutil.cpu_percent()
            final_memory = psutil.virtual_memory().percent
            
            duration = time.time() - start_time
            
            metric_result = {
                "name": metric_name,
                "monitored_resources": monitor,
                "cpu_usage": {
                    "initial": initial_cpu,
                    "final": final_cpu,
                    "delta": final_cpu - initial_cpu
                },
                "memory_usage": {
                    "initial": initial_memory,
                    "final": final_memory,
                    "delta": final_memory - initial_memory
                },
                "duration": duration
            }
            
        except Exception as e:
            metric_result = {
                "name": metric_name,
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["metrics"].append(metric_result)
    
    async def _test_stability(self, results: Dict, duration: int):
        """测试稳定性"""
        metric_name = f"稳定性测试 ({duration}秒)"
        logger.info(f"执行: {metric_name}")
        
        try:
            start_time = time.time()
            error_count = 0
            success_count = 0
            
            while time.time() - start_time < duration:
                try:
                    result = self.adapters["unified_tool_engine"].process({
                        "action": "discover_tools",
                        "parameters": {"query": "stability_test"}
                    })
                    
                    if result.get("success"):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception:
                    error_count += 1
                
                await asyncio.sleep(1)
            
            total_requests = success_count + error_count
            stability_rate = success_count / max(total_requests, 1)
            
            metric_result = {
                "name": metric_name,
                "duration": duration,
                "total_requests": total_requests,
                "successful_requests": success_count,
                "failed_requests": error_count,
                "stability_rate": stability_rate,
                "requests_per_second": total_requests / duration
            }
            
        except Exception as e:
            metric_result = {
                "name": metric_name,
                "error": str(e),
                "duration": time.time() - start_time
            }
        
        results["metrics"].append(metric_result)
    
    def generate_report(self, results: Dict, output_format: str = "json") -> str:
        """生成测试报告"""
        if output_format == "json":
            return json.dumps(results, indent=2, ensure_ascii=False)
        elif output_format == "summary":
            return self._generate_summary_report(results)
        else:
            return str(results)
    
    def _generate_summary_report(self, results: Dict) -> str:
        """生成摘要报告"""
        report_lines = []
        
        report_lines.append(f"=== MCPTool测试报告 ===")
        report_lines.append(f"测试类型: {results.get('test_type', 'unknown')}")
        report_lines.append(f"测试分类: {results.get('test_category', 'unknown')}")
        report_lines.append(f"执行时间: {results.get('duration', 0):.2f}秒")
        
        if results.get("test_type") == "integration":
            report_lines.append(f"总测试数: {results.get('total_tests', 0)}")
            report_lines.append(f"通过测试: {results.get('passed_tests', 0)}")
            report_lines.append(f"成功率: {results.get('success_rate', 0):.2%}")
        
        elif results.get("test_type") == "e2e":
            report_lines.append(f"总工作流: {results.get('total_workflows', 0)}")
            report_lines.append(f"通过工作流: {results.get('passed_workflows', 0)}")
            report_lines.append(f"成功率: {results.get('success_rate', 0):.2%}")
        
        elif results.get("test_type") == "performance":
            report_lines.append(f"性能指标数: {len(results.get('metrics', []))}")
        
        return "\n".join(report_lines)

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MCPTool CLI测试工具")
    
    # 测试类型
    parser.add_argument("test_type", choices=["integration", "e2e", "performance", "all"],
                       help="测试类型")
    
    # 测试子类型
    parser.add_argument("--test", default="all", help="具体测试项目")
    
    # 性能测试参数
    parser.add_argument("--threads", type=int, default=5, help="并发线程数")
    parser.add_argument("--duration", type=int, default=60, help="测试持续时间(秒)")
    parser.add_argument("--monitor", nargs="+", default=["cpu", "memory"], help="监控资源")
    
    # 输出参数
    parser.add_argument("--output", choices=["json", "summary"], default="summary", help="输出格式")
    parser.add_argument("--save", help="保存报告到文件")
    
    # 日志级别
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建测试器
    tester = MCPToolCLITester()
    
    # 执行测试
    if args.test_type == "integration":
        results = await tester.run_integration_tests(args.test)
    elif args.test_type == "e2e":
        results = await tester.run_e2e_tests(args.test)
    elif args.test_type == "performance":
        results = await tester.run_performance_tests(
            args.test, 
            threads=args.threads,
            duration=args.duration,
            monitor=args.monitor
        )
    elif args.test_type == "all":
        # 运行所有测试
        integration_results = await tester.run_integration_tests()
        e2e_results = await tester.run_e2e_tests()
        performance_results = await tester.run_performance_tests()
        
        results = {
            "test_type": "comprehensive",
            "integration": integration_results,
            "e2e": e2e_results,
            "performance": performance_results,
            "summary": {
                "total_duration": (integration_results.get("duration", 0) + 
                                 e2e_results.get("duration", 0) + 
                                 performance_results.get("duration", 0)),
                "overall_success": all([
                    integration_results.get("success_rate", 0) > 0.8,
                    e2e_results.get("success_rate", 0) > 0.8
                ])
            }
        }
    
    # 生成报告
    report = tester.generate_report(results, args.output)
    
    # 输出报告
    print(report)
    
    # 保存报告
    if args.save:
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {args.save}")

if __name__ == "__main__":
    asyncio.run(main())

