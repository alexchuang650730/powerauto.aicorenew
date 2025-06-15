#!/usr/bin/env python3
"""
開發部署閉環協調器MCP

整合KiloCode代碼生成和Release Manager部署功能，
實現從需求到部署的完整自動化閉環。

作者: PowerAutomation團隊
版本: 1.0.0
日期: 2025-06-08
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 導入基礎MCP
try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")

# 導入現有組件
try:
    from mcptool.adapters.kilocode_adapter.kilocode_mcp import KiloCodeAdapter
    from mcptool.core.development_tools.release_manager import ReleaseManager
    from mcptool.adapters.smart_routing_mcp import SmartRoutingMCP
    from mcptool.adapters.mcp_registry_integration_manager import MCPRegistryIntegrationManager
except ImportError as e:
    logging.warning(f"導入現有組件失敗: {e}")
    # 創建Mock類
    class KiloCodeAdapter:
        def __init__(self):
            pass
        def generate_code(self, *args, **kwargs):
            return {"status": "mock", "code": "# Mock code"}
    
    class ReleaseManager:
        def __init__(self, project_dir):
            self.project_dir = project_dir
        def create_release(self, *args, **kwargs):
            return {"status": "mock", "version": "1.0.0"}
    
    class SmartRoutingMCP:
        def __init__(self):
            pass
    
    class MCPRegistryIntegrationManager:
        def __init__(self):
            pass

# 導入標準化日誌系統
try:
    from standardized_logging_system import log_info, log_error, log_warning, LogCategory, performance_monitor
except ImportError:
    def log_info(category, message, data=None): pass
    def log_error(category, message, data=None): pass
    def log_warning(category, message, data=None): pass
    def performance_monitor(name): 
        def decorator(func): return func
        return decorator
    class LogCategory:
        SYSTEM = "system"
        MEMORY = "memory"
        MCP = "mcp"

logger = logging.getLogger("dev_deploy_loop_coordinator")

class LoopStage(Enum):
    """閉環階段枚舉"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    CODE_GENERATION = "code_generation"
    CODE_OPTIMIZATION = "code_optimization"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    FEEDBACK = "feedback"
    ITERATION = "iteration"

class DeploymentTarget(Enum):
    """部署目標枚舉"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"

class LoopStatus(Enum):
    """閉環狀態枚舉"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class DevelopmentRequest:
    """開發請求信息"""
    request_id: str
    user_requirement: str
    project_name: str
    target_language: str = "python"
    deployment_target: DeploymentTarget = DeploymentTarget.DEVELOPMENT
    priority: str = "medium"
    deadline: str = ""
    context: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class LoopExecution:
    """閉環執行信息"""
    execution_id: str
    request: DevelopmentRequest
    current_stage: LoopStage
    status: LoopStatus
    stages_completed: List[str]
    generated_code: str = ""
    optimized_code: str = ""
    test_results: Dict[str, Any] = None
    deployment_info: Dict[str, Any] = None
    feedback_data: Dict[str, Any] = None
    error_messages: List[str] = None
    start_time: str = ""
    end_time: str = ""
    total_duration: float = 0.0
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = {}
        if self.deployment_info is None:
            self.deployment_info = {}
        if self.feedback_data is None:
            self.feedback_data = {}
        if self.error_messages is None:
            self.error_messages = []
        if not self.start_time:
            self.start_time = datetime.now().isoformat()

class DevDeployLoopCoordinatorMCP(BaseMCP):
    """開發部署閉環協調器MCP"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("DevDeployLoopCoordinatorMCP")
        
        # 配置參數
        self.config = config or {}
        self.project_root = self.config.get("project_root", "/home/ubuntu/projects/communitypowerautomation")
        self.auto_deploy = self.config.get("auto_deploy", False)
        self.max_iterations = self.config.get("max_iterations", 3)
        self.timeout_minutes = self.config.get("timeout_minutes", 30)
        
        # 初始化組件
        self.kilocode_adapter = KiloCodeAdapter()
        self.release_manager = ReleaseManager(self.project_root)
        self.smart_routing = SmartRoutingMCP()
        self.registry_manager = MCPRegistryIntegrationManager()
        
        # 閉環管理
        self.active_loops = {}
        self.loop_history = []
        self.max_history_size = self.config.get("max_history_size", 100)
        
        # 統計信息
        self.loop_stats = {
            "total_loops": 0,
            "successful_loops": 0,
            "failed_loops": 0,
            "average_duration": 0.0,
            "stage_success_rates": {stage.value: 0.0 for stage in LoopStage},
            "deployment_targets": {target.value: 0 for target in DeploymentTarget}
        }
        
        # 閉環階段處理器
        self.stage_processors = {
            LoopStage.REQUIREMENT_ANALYSIS: self._process_requirement_analysis,
            LoopStage.CODE_GENERATION: self._process_code_generation,
            LoopStage.CODE_OPTIMIZATION: self._process_code_optimization,
            LoopStage.TESTING: self._process_testing,
            LoopStage.DEPLOYMENT: self._process_deployment,
            LoopStage.MONITORING: self._process_monitoring,
            LoopStage.FEEDBACK: self._process_feedback,
            LoopStage.ITERATION: self._process_iteration
        }
        
        # MCP操作映射
        self.operations = {
            "start_dev_loop": self.start_development_loop,
            "get_loop_status": self.get_loop_status,
            "pause_loop": self.pause_loop,
            "resume_loop": self.resume_loop,
            "cancel_loop": self.cancel_loop,
            "get_loop_history": self.get_loop_history,
            "get_loop_stats": self.get_loop_stats,
            "optimize_loop": self.optimize_loop,
            "export_loop_data": self.export_loop_data,
            "reset_stats": self.reset_loop_stats,
            "get_active_loops": self.get_active_loops
        }
        
        log_info(LogCategory.MCP, "開發部署閉環協調器初始化完成", {
            "project_root": self.project_root,
            "auto_deploy": self.auto_deploy,
            "max_iterations": self.max_iterations,
            "operations": list(self.operations.keys())
        })
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP標準處理接口"""
        try:
            operation = input_data.get("operation", "get_loop_stats")
            params = input_data.get("params", {})
            
            if operation not in self.operations:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {operation}",
                    "available_operations": list(self.operations.keys())
                }
            
            # 執行對應操作
            if asyncio.iscoroutinefunction(self.operations[operation]):
                # 異步操作
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.operations[operation](**params))
            else:
                # 同步操作
                result = self.operations[operation](**params)
            
            log_info(LogCategory.MCP, f"開發部署閉環協調器操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "開發部署閉環協調器處理失敗", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"處理失敗: {str(e)}"
            }
    
    @performance_monitor("start_development_loop")
    async def start_development_loop(self, user_requirement: str, project_name: str, 
                                   target_language: str = "python", 
                                   deployment_target: str = "development",
                                   priority: str = "medium") -> Dict[str, Any]:
        """啟動開發部署閉環"""
        try:
            # 創建開發請求
            request = DevelopmentRequest(
                request_id=self._generate_request_id(),
                user_requirement=user_requirement,
                project_name=project_name,
                target_language=target_language,
                deployment_target=DeploymentTarget(deployment_target),
                priority=priority
            )
            
            # 創建閉環執行
            execution = LoopExecution(
                execution_id=self._generate_execution_id(),
                request=request,
                current_stage=LoopStage.REQUIREMENT_ANALYSIS,
                status=LoopStatus.RUNNING,
                stages_completed=[]
            )
            
            # 註冊活動閉環
            self.active_loops[execution.execution_id] = execution
            
            # 啟動閉環執行
            asyncio.create_task(self._execute_loop(execution))
            
            self.loop_stats["total_loops"] += 1
            
            log_info(LogCategory.MCP, f"開發部署閉環已啟動: {execution.execution_id}", {
                "project_name": project_name,
                "target_language": target_language,
                "deployment_target": deployment_target
            })
            
            return {
                "status": "success",
                "execution_id": execution.execution_id,
                "request_id": request.request_id,
                "message": "開發部署閉環已啟動",
                "current_stage": execution.current_stage.value
            }
            
        except Exception as e:
            self.loop_stats["failed_loops"] += 1
            return {
                "status": "error",
                "message": f"啟動開發部署閉環失敗: {str(e)}"
            }
    
    def _generate_request_id(self) -> str:
        """生成請求ID"""
        import uuid
        return f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    def _generate_execution_id(self) -> str:
        """生成執行ID"""
        import uuid
        return f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    async def _execute_loop(self, execution: LoopExecution):
        """執行閉環流程"""
        try:
            log_info(LogCategory.MCP, f"開始執行閉環: {execution.execution_id}", {})
            
            # 定義閉環階段順序
            stages = [
                LoopStage.REQUIREMENT_ANALYSIS,
                LoopStage.CODE_GENERATION,
                LoopStage.CODE_OPTIMIZATION,
                LoopStage.TESTING,
                LoopStage.DEPLOYMENT,
                LoopStage.MONITORING,
                LoopStage.FEEDBACK
            ]
            
            # 執行各個階段
            for stage in stages:
                if execution.status != LoopStatus.RUNNING:
                    break
                
                execution.current_stage = stage
                
                try:
                    # 執行階段處理器
                    stage_result = await self.stage_processors[stage](execution)
                    
                    if stage_result.get("status") == "success":
                        execution.stages_completed.append(stage.value)
                        log_info(LogCategory.MCP, f"閉環階段完成: {stage.value}", {
                            "execution_id": execution.execution_id
                        })
                    else:
                        # 階段失敗
                        error_msg = stage_result.get("message", f"階段 {stage.value} 執行失敗")
                        execution.error_messages.append(error_msg)
                        
                        # 決定是否繼續或重試
                        if await self._should_retry_stage(execution, stage):
                            log_warning(LogCategory.MCP, f"重試閉環階段: {stage.value}", {})
                            continue
                        else:
                            execution.status = LoopStatus.FAILED
                            break
                
                except Exception as e:
                    error_msg = f"階段 {stage.value} 執行異常: {str(e)}"
                    execution.error_messages.append(error_msg)
                    log_error(LogCategory.MCP, error_msg, {})
                    
                    if not await self._should_retry_stage(execution, stage):
                        execution.status = LoopStatus.FAILED
                        break
            
            # 檢查是否需要迭代
            if execution.status == LoopStatus.RUNNING:
                iteration_result = await self._process_iteration(execution)
                if iteration_result.get("iterate", False):
                    # 開始新的迭代
                    await self._execute_loop(execution)
                else:
                    # 閉環完成
                    execution.status = LoopStatus.COMPLETED
                    execution.end_time = datetime.now().isoformat()
                    execution.total_duration = self._calculate_duration(execution)
                    
                    self.loop_stats["successful_loops"] += 1
            
            # 更新統計信息
            self._update_loop_stats(execution)
            
            # 記錄閉環歷史
            self._record_loop_history(execution)
            
            # 從活動閉環中移除
            if execution.execution_id in self.active_loops:
                del self.active_loops[execution.execution_id]
            
            log_info(LogCategory.MCP, f"閉環執行完成: {execution.execution_id}", {
                "status": execution.status.value,
                "stages_completed": len(execution.stages_completed),
                "duration": execution.total_duration
            })
            
        except Exception as e:
            execution.status = LoopStatus.FAILED
            execution.error_messages.append(f"閉環執行異常: {str(e)}")
            log_error(LogCategory.MCP, f"閉環執行失敗: {execution.execution_id}", {"error": str(e)})
            
            self.loop_stats["failed_loops"] += 1
            self._update_loop_stats(execution)
            self._record_loop_history(execution)
            
            if execution.execution_id in self.active_loops:
                del self.active_loops[execution.execution_id]
    
    async def _process_requirement_analysis(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理需求分析階段"""
        try:
            log_info(LogCategory.MCP, "開始需求分析", {"execution_id": execution.execution_id})
            
            # 使用智慧路由分析需求
            analysis_result = await self.smart_routing.route_request(
                user_intent=execution.request.user_requirement,
                operation="analyze_requirement",
                params={
                    "project_name": execution.request.project_name,
                    "target_language": execution.request.target_language
                }
            )
            
            if analysis_result.get("status") == "success":
                # 更新執行上下文
                execution.request.context.update({
                    "requirement_analysis": analysis_result.get("response", {}),
                    "analyzed_at": datetime.now().isoformat()
                })
                
                return {
                    "status": "success",
                    "message": "需求分析完成",
                    "analysis_result": analysis_result
                }
            else:
                return {
                    "status": "error",
                    "message": f"需求分析失敗: {analysis_result.get('message', '未知錯誤')}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"需求分析階段異常: {str(e)}"
            }
    
    async def _process_code_generation(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理代碼生成階段"""
        try:
            log_info(LogCategory.MCP, "開始代碼生成", {"execution_id": execution.execution_id})
            
            # 使用KiloCode生成代碼
            generation_params = {
                "requirement": execution.request.user_requirement,
                "language": execution.request.target_language,
                "project_name": execution.request.project_name,
                "context": execution.request.context
            }
            
            # 模擬KiloCode代碼生成（實際實現中需要調用真實的KiloCode API）
            code_result = await self._simulate_code_generation(generation_params)
            
            if code_result.get("status") == "success":
                execution.generated_code = code_result.get("code", "")
                
                # 保存生成的代碼
                await self._save_generated_code(execution)
                
                return {
                    "status": "success",
                    "message": "代碼生成完成",
                    "code_length": len(execution.generated_code),
                    "code_result": code_result
                }
            else:
                return {
                    "status": "error",
                    "message": f"代碼生成失敗: {code_result.get('message', '未知錯誤')}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"代碼生成階段異常: {str(e)}"
            }
    
    async def _simulate_code_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """模擬代碼生成（實際實現中需要調用KiloCode API）"""
        try:
            # 模擬代碼生成過程
            await asyncio.sleep(2)  # 模擬生成時間
            
            # 生成示例代碼
            project_name = params.get("project_name", "example_project")
            language = params.get("language", "python")
            requirement = params.get("requirement", "")
            
            if language.lower() == "python":
                generated_code = f'''#!/usr/bin/env python3
"""
{project_name}

自動生成的代碼，基於需求: {requirement}
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class {project_name.replace("_", "").title()}:
    """主要功能類"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        logger.info(f"{project_name} 初始化完成")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理輸入數據"""
        try:
            # 實現主要邏輯
            result = {{
                "status": "success",
                "message": "處理完成",
                "data": input_data
            }}
            
            return result
            
        except Exception as e:
            logger.error(f"處理失敗: {{str(e)}}")
            return {{
                "status": "error",
                "message": f"處理失敗: {{str(e)}}"
            }}

if __name__ == "__main__":
    # 測試代碼
    app = {project_name.replace("_", "").title()}()
    test_data = {{"test": "data"}}
    result = app.process(test_data)
    print(json.dumps(result, indent=2))
'''
            else:
                generated_code = f"// {project_name} - Generated code for {requirement}"
            
            return {
                "status": "success",
                "code": generated_code,
                "language": language,
                "project_name": project_name,
                "generation_time": 2.0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"代碼生成模擬失敗: {str(e)}"
            }
    
    async def _save_generated_code(self, execution: LoopExecution):
        """保存生成的代碼"""
        try:
            project_dir = Path(self.project_root) / "generated_projects" / execution.request.project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 確定文件擴展名
            language = execution.request.target_language.lower()
            extensions = {
                "python": ".py",
                "javascript": ".js",
                "typescript": ".ts",
                "java": ".java",
                "cpp": ".cpp",
                "c": ".c"
            }
            
            extension = extensions.get(language, ".txt")
            code_file = project_dir / f"main{extension}"
            
            # 保存代碼
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(execution.generated_code)
            
            # 更新執行信息
            execution.request.metadata["code_file_path"] = str(code_file)
            execution.request.metadata["project_dir"] = str(project_dir)
            
            log_info(LogCategory.MCP, f"代碼已保存: {code_file}", {})
            
        except Exception as e:
            log_error(LogCategory.MCP, f"保存代碼失敗: {str(e)}", {})
    
    async def _process_code_optimization(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理代碼優化階段"""
        try:
            log_info(LogCategory.MCP, "開始代碼優化", {"execution_id": execution.execution_id})
            
            if not execution.generated_code:
                return {
                    "status": "error",
                    "message": "沒有可優化的代碼"
                }
            
            # 模擬代碼優化
            optimization_result = await self._simulate_code_optimization(execution.generated_code)
            
            if optimization_result.get("status") == "success":
                execution.optimized_code = optimization_result.get("optimized_code", execution.generated_code)
                
                # 保存優化後的代碼
                await self._save_optimized_code(execution)
                
                return {
                    "status": "success",
                    "message": "代碼優化完成",
                    "optimization_result": optimization_result
                }
            else:
                # 優化失敗，使用原始代碼
                execution.optimized_code = execution.generated_code
                return {
                    "status": "success",
                    "message": "代碼優化跳過，使用原始代碼",
                    "warning": optimization_result.get("message", "優化失敗")
                }
                
        except Exception as e:
            execution.optimized_code = execution.generated_code
            return {
                "status": "success",
                "message": "代碼優化異常，使用原始代碼",
                "error": str(e)
            }
    
    async def _simulate_code_optimization(self, code: str) -> Dict[str, Any]:
        """模擬代碼優化"""
        try:
            await asyncio.sleep(1)  # 模擬優化時間
            
            # 簡單的代碼優化（添加註釋和格式化）
            optimized_code = code.replace("# 實現主要邏輯", """# 實現主要邏輯
            # 優化: 添加輸入驗證
            if not isinstance(input_data, dict):
                raise ValueError("輸入數據必須是字典類型")
            
            # 優化: 添加日誌記錄
            logger.info(f"開始處理數據: {len(input_data)} 個字段")""")
            
            return {
                "status": "success",
                "optimized_code": optimized_code,
                "optimizations_applied": [
                    "添加輸入驗證",
                    "增強日誌記錄",
                    "改進錯誤處理"
                ],
                "optimization_time": 1.0
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"代碼優化失敗: {str(e)}"
            }
    
    async def _save_optimized_code(self, execution: LoopExecution):
        """保存優化後的代碼"""
        try:
            project_dir = Path(execution.request.metadata.get("project_dir", ""))
            if not project_dir.exists():
                return
            
            # 確定文件擴展名
            language = execution.request.target_language.lower()
            extensions = {
                "python": ".py",
                "javascript": ".js",
                "typescript": ".ts",
                "java": ".java",
                "cpp": ".cpp",
                "c": ".c"
            }
            
            extension = extensions.get(language, ".txt")
            optimized_file = project_dir / f"main_optimized{extension}"
            
            # 保存優化後的代碼
            with open(optimized_file, 'w', encoding='utf-8') as f:
                f.write(execution.optimized_code)
            
            execution.request.metadata["optimized_code_file_path"] = str(optimized_file)
            
            log_info(LogCategory.MCP, f"優化代碼已保存: {optimized_file}", {})
            
        except Exception as e:
            log_error(LogCategory.MCP, f"保存優化代碼失敗: {str(e)}", {})
    
    async def _process_testing(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理測試階段"""
        try:
            log_info(LogCategory.MCP, "開始代碼測試", {"execution_id": execution.execution_id})
            
            # 模擬代碼測試
            test_result = await self._simulate_code_testing(execution)
            
            execution.test_results = test_result
            
            if test_result.get("status") == "success":
                return {
                    "status": "success",
                    "message": "代碼測試完成",
                    "test_result": test_result
                }
            else:
                return {
                    "status": "error",
                    "message": f"代碼測試失敗: {test_result.get('message', '未知錯誤')}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"測試階段異常: {str(e)}"
            }
    
    async def _simulate_code_testing(self, execution: LoopExecution) -> Dict[str, Any]:
        """模擬代碼測試"""
        try:
            await asyncio.sleep(1.5)  # 模擬測試時間
            
            # 模擬測試結果
            import random
            
            test_cases = [
                {"name": "基本功能測試", "status": "passed"},
                {"name": "輸入驗證測試", "status": "passed"},
                {"name": "錯誤處理測試", "status": "passed"},
                {"name": "性能測試", "status": "passed" if random.random() > 0.2 else "failed"},
                {"name": "邊界條件測試", "status": "passed" if random.random() > 0.1 else "failed"}
            ]
            
            passed_tests = [test for test in test_cases if test["status"] == "passed"]
            failed_tests = [test for test in test_cases if test["status"] == "failed"]
            
            success_rate = len(passed_tests) / len(test_cases)
            
            return {
                "status": "success" if success_rate >= 0.8 else "error",
                "test_cases": test_cases,
                "passed_tests": len(passed_tests),
                "failed_tests": len(failed_tests),
                "success_rate": success_rate,
                "test_duration": 1.5,
                "message": f"測試完成，成功率: {success_rate:.1%}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"代碼測試失敗: {str(e)}"
            }
    
    async def _process_deployment(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理部署階段"""
        try:
            log_info(LogCategory.MCP, "開始代碼部署", {"execution_id": execution.execution_id})
            
            # 使用Release Manager進行部署
            deployment_result = await self._deploy_with_release_manager(execution)
            
            execution.deployment_info = deployment_result
            
            if deployment_result.get("status") == "success":
                return {
                    "status": "success",
                    "message": "代碼部署完成",
                    "deployment_result": deployment_result
                }
            else:
                return {
                    "status": "error",
                    "message": f"代碼部署失敗: {deployment_result.get('message', '未知錯誤')}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"部署階段異常: {str(e)}"
            }
    
    async def _deploy_with_release_manager(self, execution: LoopExecution) -> Dict[str, Any]:
        """使用Release Manager進行部署"""
        try:
            # 創建發布版本
            version = f"1.0.{len(self.loop_history)}"
            release_notes = f"自動生成的發布版本，基於需求: {execution.request.user_requirement}"
            
            # 模擬Release Manager部署
            release_result = self.release_manager.create_release(
                version=version,
                release_notes=release_notes,
                release_type="minor"
            )
            
            if release_result.get("status") == "success":
                # 模擬部署過程
                await asyncio.sleep(2)  # 模擬部署時間
                
                deployment_target = execution.request.deployment_target.value
                
                return {
                    "status": "success",
                    "version": version,
                    "deployment_target": deployment_target,
                    "deployment_url": f"http://localhost:8080/{execution.request.project_name}",
                    "deployment_time": datetime.now().isoformat(),
                    "release_info": release_result
                }
            else:
                return {
                    "status": "error",
                    "message": f"創建發布版本失敗: {release_result.get('message', '未知錯誤')}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Release Manager部署失敗: {str(e)}"
            }
    
    async def _process_monitoring(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理監控階段"""
        try:
            log_info(LogCategory.MCP, "開始部署監控", {"execution_id": execution.execution_id})
            
            # 模擬監控設置
            monitoring_result = await self._setup_monitoring(execution)
            
            return {
                "status": "success",
                "message": "監控設置完成",
                "monitoring_result": monitoring_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"監控階段異常: {str(e)}"
            }
    
    async def _setup_monitoring(self, execution: LoopExecution) -> Dict[str, Any]:
        """設置監控"""
        try:
            await asyncio.sleep(0.5)  # 模擬設置時間
            
            return {
                "status": "success",
                "monitoring_endpoints": [
                    f"/health/{execution.request.project_name}",
                    f"/metrics/{execution.request.project_name}",
                    f"/logs/{execution.request.project_name}"
                ],
                "alert_rules": [
                    "響應時間 > 5秒",
                    "錯誤率 > 5%",
                    "CPU使用率 > 80%"
                ],
                "setup_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"監控設置失敗: {str(e)}"
            }
    
    async def _process_feedback(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理反饋階段"""
        try:
            log_info(LogCategory.MCP, "收集反饋信息", {"execution_id": execution.execution_id})
            
            # 收集反饋數據
            feedback_data = await self._collect_feedback(execution)
            
            execution.feedback_data = feedback_data
            
            return {
                "status": "success",
                "message": "反饋收集完成",
                "feedback_data": feedback_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"反饋階段異常: {str(e)}"
            }
    
    async def _collect_feedback(self, execution: LoopExecution) -> Dict[str, Any]:
        """收集反饋數據"""
        try:
            await asyncio.sleep(0.3)  # 模擬收集時間
            
            # 模擬反饋數據
            import random
            
            return {
                "user_satisfaction": random.uniform(0.7, 1.0),
                "performance_score": random.uniform(0.8, 1.0),
                "code_quality_score": random.uniform(0.75, 0.95),
                "deployment_success": execution.deployment_info.get("status") == "success",
                "test_success_rate": execution.test_results.get("success_rate", 0.0),
                "feedback_time": datetime.now().isoformat(),
                "suggestions": [
                    "代碼註釋可以更詳細",
                    "可以添加更多測試用例",
                    "性能優化空間較大"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"反饋收集失敗: {str(e)}"
            }
    
    async def _process_iteration(self, execution: LoopExecution) -> Dict[str, Any]:
        """處理迭代階段"""
        try:
            log_info(LogCategory.MCP, "評估迭代需求", {"execution_id": execution.execution_id})
            
            # 評估是否需要迭代
            iteration_decision = await self._evaluate_iteration_need(execution)
            
            return iteration_decision
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"迭代階段異常: {str(e)}",
                "iterate": False
            }
    
    async def _evaluate_iteration_need(self, execution: LoopExecution) -> Dict[str, Any]:
        """評估迭代需求"""
        try:
            # 基於反饋數據決定是否迭代
            feedback = execution.feedback_data
            
            if not feedback:
                return {"iterate": False, "reason": "沒有反饋數據"}
            
            # 迭代條件
            user_satisfaction = feedback.get("user_satisfaction", 1.0)
            performance_score = feedback.get("performance_score", 1.0)
            code_quality_score = feedback.get("code_quality_score", 1.0)
            test_success_rate = feedback.get("test_success_rate", 1.0)
            
            # 計算總體分數
            overall_score = (user_satisfaction + performance_score + code_quality_score + test_success_rate) / 4
            
            # 迭代決策
            should_iterate = (
                overall_score < 0.8 or  # 總體分數低
                test_success_rate < 0.9 or  # 測試成功率低
                not feedback.get("deployment_success", True)  # 部署失敗
            )
            
            # 檢查迭代次數限制
            iteration_count = execution.request.metadata.get("iteration_count", 0)
            if iteration_count >= self.max_iterations:
                should_iterate = False
                reason = f"已達到最大迭代次數: {self.max_iterations}"
            else:
                reason = f"總體分數: {overall_score:.2f}, 測試成功率: {test_success_rate:.2f}"
            
            if should_iterate:
                # 更新迭代計數
                execution.request.metadata["iteration_count"] = iteration_count + 1
                
                # 重置階段狀態
                execution.stages_completed = []
                execution.current_stage = LoopStage.REQUIREMENT_ANALYSIS
            
            return {
                "iterate": should_iterate,
                "reason": reason,
                "overall_score": overall_score,
                "iteration_count": iteration_count + (1 if should_iterate else 0)
            }
            
        except Exception as e:
            return {
                "iterate": False,
                "reason": f"迭代評估失敗: {str(e)}"
            }
    
    async def _should_retry_stage(self, execution: LoopExecution, stage: LoopStage) -> bool:
        """判斷是否應該重試階段"""
        # 簡單的重試邏輯
        retry_count = execution.request.metadata.get(f"{stage.value}_retry_count", 0)
        max_retries = 2
        
        if retry_count < max_retries:
            execution.request.metadata[f"{stage.value}_retry_count"] = retry_count + 1
            return True
        
        return False
    
    def _calculate_duration(self, execution: LoopExecution) -> float:
        """計算執行時長"""
        try:
            start_time = datetime.fromisoformat(execution.start_time)
            end_time = datetime.fromisoformat(execution.end_time)
            return (end_time - start_time).total_seconds()
        except:
            return 0.0
    
    def _update_loop_stats(self, execution: LoopExecution):
        """更新閉環統計"""
        try:
            # 更新平均時長
            total_loops = self.loop_stats["total_loops"]
            if total_loops > 0:
                current_avg = self.loop_stats["average_duration"]
                new_duration = execution.total_duration
                self.loop_stats["average_duration"] = (current_avg * (total_loops - 1) + new_duration) / total_loops
            
            # 更新階段成功率
            for stage in execution.stages_completed:
                if stage in self.loop_stats["stage_success_rates"]:
                    current_rate = self.loop_stats["stage_success_rates"][stage]
                    self.loop_stats["stage_success_rates"][stage] = (current_rate + 1.0) / 2.0
            
            # 更新部署目標統計
            target = execution.request.deployment_target.value
            self.loop_stats["deployment_targets"][target] += 1
            
        except Exception as e:
            log_error(LogCategory.MCP, f"更新閉環統計失敗: {str(e)}", {})
    
    def _record_loop_history(self, execution: LoopExecution):
        """記錄閉環歷史"""
        try:
            history_entry = {
                "execution_id": execution.execution_id,
                "request_id": execution.request.request_id,
                "project_name": execution.request.project_name,
                "status": execution.status.value,
                "stages_completed": execution.stages_completed,
                "total_duration": execution.total_duration,
                "start_time": execution.start_time,
                "end_time": execution.end_time,
                "error_count": len(execution.error_messages),
                "deployment_target": execution.request.deployment_target.value
            }
            
            self.loop_history.append(history_entry)
            
            # 保持歷史記錄在合理範圍內
            if len(self.loop_history) > self.max_history_size:
                self.loop_history = self.loop_history[-self.max_history_size:]
                
        except Exception as e:
            log_error(LogCategory.MCP, f"記錄閉環歷史失敗: {str(e)}", {})
    
    def get_loop_status(self, execution_id: str) -> Dict[str, Any]:
        """獲取閉環狀態"""
        try:
            if execution_id in self.active_loops:
                execution = self.active_loops[execution_id]
                return {
                    "status": "success",
                    "execution_id": execution_id,
                    "loop_status": execution.status.value,
                    "current_stage": execution.current_stage.value,
                    "stages_completed": execution.stages_completed,
                    "progress": len(execution.stages_completed) / len(LoopStage) * 100,
                    "start_time": execution.start_time,
                    "error_count": len(execution.error_messages)
                }
            else:
                # 檢查歷史記錄
                for entry in self.loop_history:
                    if entry["execution_id"] == execution_id:
                        return {
                            "status": "success",
                            "execution_id": execution_id,
                            "loop_status": entry["status"],
                            "stages_completed": entry["stages_completed"],
                            "total_duration": entry["total_duration"],
                            "start_time": entry["start_time"],
                            "end_time": entry["end_time"],
                            "in_history": True
                        }
                
                return {
                    "status": "error",
                    "message": f"閉環執行不存在: {execution_id}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取閉環狀態失敗: {str(e)}"
            }
    
    async def pause_loop(self, execution_id: str) -> Dict[str, Any]:
        """暫停閉環"""
        try:
            if execution_id not in self.active_loops:
                return {
                    "status": "error",
                    "message": f"閉環執行不存在: {execution_id}"
                }
            
            execution = self.active_loops[execution_id]
            if execution.status == LoopStatus.RUNNING:
                execution.status = LoopStatus.PAUSED
                
                log_info(LogCategory.MCP, f"閉環已暫停: {execution_id}", {})
                
                return {
                    "status": "success",
                    "message": f"閉環已暫停: {execution_id}",
                    "current_stage": execution.current_stage.value
                }
            else:
                return {
                    "status": "error",
                    "message": f"閉環狀態不允許暫停: {execution.status.value}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"暫停閉環失敗: {str(e)}"
            }
    
    async def resume_loop(self, execution_id: str) -> Dict[str, Any]:
        """恢復閉環"""
        try:
            if execution_id not in self.active_loops:
                return {
                    "status": "error",
                    "message": f"閉環執行不存在: {execution_id}"
                }
            
            execution = self.active_loops[execution_id]
            if execution.status == LoopStatus.PAUSED:
                execution.status = LoopStatus.RUNNING
                
                # 重新啟動執行
                asyncio.create_task(self._execute_loop(execution))
                
                log_info(LogCategory.MCP, f"閉環已恢復: {execution_id}", {})
                
                return {
                    "status": "success",
                    "message": f"閉環已恢復: {execution_id}",
                    "current_stage": execution.current_stage.value
                }
            else:
                return {
                    "status": "error",
                    "message": f"閉環狀態不允許恢復: {execution.status.value}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"恢復閉環失敗: {str(e)}"
            }
    
    async def cancel_loop(self, execution_id: str) -> Dict[str, Any]:
        """取消閉環"""
        try:
            if execution_id not in self.active_loops:
                return {
                    "status": "error",
                    "message": f"閉環執行不存在: {execution_id}"
                }
            
            execution = self.active_loops[execution_id]
            execution.status = LoopStatus.CANCELLED
            execution.end_time = datetime.now().isoformat()
            execution.total_duration = self._calculate_duration(execution)
            
            # 記錄歷史
            self._record_loop_history(execution)
            
            # 從活動閉環中移除
            del self.active_loops[execution_id]
            
            log_info(LogCategory.MCP, f"閉環已取消: {execution_id}", {})
            
            return {
                "status": "success",
                "message": f"閉環已取消: {execution_id}",
                "stages_completed": execution.stages_completed
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"取消閉環失敗: {str(e)}"
            }
    
    def get_loop_history(self, limit: int = 20) -> Dict[str, Any]:
        """獲取閉環歷史"""
        try:
            history = self.loop_history[-limit:] if limit > 0 else self.loop_history
            
            return {
                "status": "success",
                "loop_history": history,
                "total_history": len(self.loop_history),
                "returned_count": len(history)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取閉環歷史失敗: {str(e)}"
            }
    
    def get_loop_stats(self) -> Dict[str, Any]:
        """獲取閉環統計"""
        return {
            "status": "success",
            "loop_stats": self.loop_stats.copy(),
            "active_loops_count": len(self.active_loops),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_active_loops(self) -> Dict[str, Any]:
        """獲取活動閉環"""
        try:
            active_loops = []
            
            for execution_id, execution in self.active_loops.items():
                active_loops.append({
                    "execution_id": execution_id,
                    "project_name": execution.request.project_name,
                    "status": execution.status.value,
                    "current_stage": execution.current_stage.value,
                    "progress": len(execution.stages_completed) / len(LoopStage) * 100,
                    "start_time": execution.start_time
                })
            
            return {
                "status": "success",
                "active_loops": active_loops,
                "total_active": len(active_loops)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取活動閉環失敗: {str(e)}"
            }
    
    async def optimize_loop(self, optimization_type: str = "auto") -> Dict[str, Any]:
        """優化閉環"""
        try:
            optimization_results = []
            
            if optimization_type in ["auto", "performance"]:
                # 性能優化
                perf_result = await self._optimize_performance()
                optimization_results.append({"type": "performance", "result": perf_result})
            
            if optimization_type in ["auto", "stages"]:
                # 階段優化
                stage_result = await self._optimize_stages()
                optimization_results.append({"type": "stages", "result": stage_result})
            
            return {
                "status": "success",
                "optimization_type": optimization_type,
                "optimization_results": optimization_results,
                "optimization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"閉環優化失敗: {str(e)}"
            }
    
    async def _optimize_performance(self) -> Dict[str, Any]:
        """優化性能"""
        try:
            # 分析歷史數據，優化超時設置
            if self.loop_history:
                durations = [entry["total_duration"] for entry in self.loop_history if entry["total_duration"] > 0]
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    new_timeout = max(avg_duration * 1.5, self.timeout_minutes * 60)
                    
                    if new_timeout != self.timeout_minutes * 60:
                        old_timeout = self.timeout_minutes
                        self.timeout_minutes = new_timeout / 60
                        
                        return {
                            "status": "success",
                            "old_timeout": old_timeout,
                            "new_timeout": self.timeout_minutes,
                            "message": "超時設置已優化"
                        }
            
            return {
                "status": "success",
                "message": "性能設置已是最優"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"性能優化失敗: {str(e)}"
            }
    
    async def _optimize_stages(self) -> Dict[str, Any]:
        """優化階段"""
        try:
            # 分析階段成功率，調整策略
            stage_rates = self.loop_stats["stage_success_rates"]
            
            problematic_stages = [
                stage for stage, rate in stage_rates.items() 
                if rate < 0.8 and rate > 0
            ]
            
            if problematic_stages:
                return {
                    "status": "success",
                    "problematic_stages": problematic_stages,
                    "suggestions": [
                        f"階段 {stage} 成功率較低，建議增加重試次數" 
                        for stage in problematic_stages
                    ],
                    "message": f"發現 {len(problematic_stages)} 個需要優化的階段"
                }
            else:
                return {
                    "status": "success",
                    "message": "所有階段運行良好"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"階段優化失敗: {str(e)}"
            }
    
    async def export_loop_data(self, export_path: str = None) -> Dict[str, Any]:
        """導出閉環數據"""
        try:
            if export_path is None:
                export_path = f"dev_loop_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "export_time": datetime.now().isoformat(),
                "loop_config": {
                    "project_root": self.project_root,
                    "auto_deploy": self.auto_deploy,
                    "max_iterations": self.max_iterations,
                    "timeout_minutes": self.timeout_minutes
                },
                "loop_stats": self.loop_stats,
                "loop_history": self.loop_history,
                "active_loops": {
                    execution_id: {
                        "request": asdict(execution.request),
                        "status": execution.status.value,
                        "current_stage": execution.current_stage.value,
                        "stages_completed": execution.stages_completed
                    }
                    for execution_id, execution in self.active_loops.items()
                }
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "export_path": export_path,
                "exported_loops": len(self.loop_history),
                "active_loops": len(self.active_loops),
                "export_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"導出閉環數據失敗: {str(e)}"
            }
    
    def reset_loop_stats(self) -> Dict[str, Any]:
        """重置閉環統計"""
        try:
            old_stats = self.loop_stats.copy()
            
            self.loop_stats = {
                "total_loops": 0,
                "successful_loops": 0,
                "failed_loops": 0,
                "average_duration": 0.0,
                "stage_success_rates": {stage.value: 0.0 for stage in LoopStage},
                "deployment_targets": {target.value: 0 for target in DeploymentTarget}
            }
            
            # 清空歷史記錄
            self.loop_history.clear()
            
            return {
                "status": "success",
                "message": "閉環統計已重置",
                "old_stats": old_stats,
                "reset_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"重置閉環統計失敗: {str(e)}"
            }

# 創建全局實例
dev_deploy_loop_coordinator = DevDeployLoopCoordinatorMCP()

# 導出主要接口
__all__ = [
    'DevDeployLoopCoordinatorMCP',
    'LoopStage',
    'DeploymentTarget',
    'LoopStatus',
    'DevelopmentRequest',
    'LoopExecution',
    'dev_deploy_loop_coordinator'
]

if __name__ == "__main__":
    # 測試MCP功能
    test_data = {
        "operation": "get_loop_stats",
        "params": {}
    }
    
    result = dev_deploy_loop_coordinator.process(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

