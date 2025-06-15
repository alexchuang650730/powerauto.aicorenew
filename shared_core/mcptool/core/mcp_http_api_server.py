"""
MCP HTTP API服务器
为MCP服务器提供RESTful API接口包装
"""

import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from mcptool.mcp_tool_engine_server import MCPToolEngineServer
from mcptool.adapters.ai_enhanced_intent_understanding_mcp import AIEnhancedIntentUnderstandingMCP

logger = logging.getLogger(__name__)

# Pydantic模型定义
class ToolDiscoveryRequest(BaseModel):
    """工具发现请求"""
    query: str = Field(..., description="搜索查询")
    filters: Dict[str, Any] = Field(default_factory=dict, description="过滤条件")
    limit: int = Field(default=10, ge=1, le=100, description="返回数量限制")

class ToolExecutionRequest(BaseModel):
    """工具执行请求"""
    tool_name: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="执行参数")
    context: Dict[str, Any] = Field(default_factory=dict, description="执行上下文")

class IntentAnalysisRequest(BaseModel):
    """意图分析请求"""
    user_input: str = Field(..., description="用户输入")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    mode: str = Field(default="comprehensive", description="分析模式")

class WorkflowExecutionRequest(BaseModel):
    """工作流执行请求"""
    workflow_definition: Dict[str, Any] = Field(..., description="工作流定义")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="输入参数")
    execution_mode: str = Field(default="async", description="执行模式")

class GitHubWorkflowRequest(BaseModel):
    """GitHub工作流请求"""
    workflow_id: str = Field(..., description="工作流ID")
    ref: str = Field(default="main", description="分支或标签")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="工作流输入")

class APIResponse(BaseModel):
    """标准API响应"""
    success: bool = Field(..., description="是否成功")
    data: Any = Field(default=None, description="响应数据")
    error: Optional[str] = Field(default=None, description="错误信息")
    timestamp: float = Field(default_factory=time.time, description="时间戳")
    request_id: Optional[str] = Field(default=None, description="请求ID")

class MCPHTTPAPIServer:
    """MCP HTTP API服务器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # 初始化FastAPI应用
        self.app = FastAPI(
            title="MCP Tool Engine HTTP API",
            description="为MCP工具引擎提供RESTful API接口",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 配置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 初始化MCP服务器
        self.mcp_server = MCPToolEngineServer()
        
        # 初始化AI增强组件
        self.ai_enhanced = AIEnhancedIntentUnderstandingMCP(
            config=self.config.get("ai_config", {})
        )
        
        # API统计
        self.api_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "endpoints_usage": {}
        }
        
        # 注册路由
        self._register_routes()
        
        logger.info("MCP HTTP API服务器初始化完成")
    
    def _register_routes(self):
        """注册API路由"""
        
        # 健康检查
        @self.app.get("/health", response_model=APIResponse)
        async def health_check():
            """健康检查接口"""
            return APIResponse(
                success=True,
                data={"status": "healthy", "version": "1.0.0"}
            )
        
        # 工具发现
        @self.app.post("/api/v1/tools/discover", response_model=APIResponse)
        async def discover_tools(request: ToolDiscoveryRequest):
            """发现工具接口"""
            try:
                start_time = time.time()
                
                # 转换为MCP请求
                mcp_request = {
                    "method": "intelligent_tool_discovery",
                    "params": {
                        "query": request.query,
                        "filters": request.filters,
                        "limit": request.limit
                    }
                }
                
                # 调用MCP服务器
                result = await self._call_mcp_server(mcp_request)
                
                # 更新统计
                self._update_stats("discover_tools", True, time.time() - start_time)
                
                return APIResponse(
                    success=True,
                    data=result
                )
                
            except Exception as e:
                self._update_stats("discover_tools", False, time.time() - start_time)
                logger.error(f"工具发现失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 工具执行
        @self.app.post("/api/v1/tools/execute", response_model=APIResponse)
        async def execute_tool(request: ToolExecutionRequest):
            """执行工具接口"""
            try:
                start_time = time.time()
                
                # 转换为MCP请求
                mcp_request = {
                    "method": "smart_tool_execution",
                    "params": {
                        "tool_name": request.tool_name,
                        "parameters": request.parameters,
                        "context": request.context
                    }
                }
                
                # 调用MCP服务器
                result = await self._call_mcp_server(mcp_request)
                
                self._update_stats("execute_tool", True, time.time() - start_time)
                
                return APIResponse(
                    success=True,
                    data=result
                )
                
            except Exception as e:
                self._update_stats("execute_tool", False, time.time() - start_time)
                logger.error(f"工具执行失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 意图分析
        @self.app.post("/api/v1/ai/analyze-intent", response_model=APIResponse)
        async def analyze_intent(request: IntentAnalysisRequest):
            """AI意图分析接口"""
            try:
                start_time = time.time()
                
                # 调用AI增强组件
                result = self.ai_enhanced.process({
                    "action": "analyze_intent",
                    "parameters": {
                        "user_input": request.user_input,
                        "context": request.context,
                        "mode": request.mode
                    }
                })
                
                self._update_stats("analyze_intent", result.get("success", False), time.time() - start_time)
                
                return APIResponse(
                    success=result.get("success", False),
                    data=result.get("enhanced_intent") if result.get("success") else None,
                    error=result.get("error") if not result.get("success") else None
                )
                
            except Exception as e:
                self._update_stats("analyze_intent", False, time.time() - start_time)
                logger.error(f"意图分析失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 任务分解
        @self.app.post("/api/v1/ai/decompose-task", response_model=APIResponse)
        async def decompose_task(request: Dict[str, Any]):
            """AI任务分解接口"""
            try:
                start_time = time.time()
                
                result = self.ai_enhanced.process({
                    "action": "decompose_task",
                    "parameters": request
                })
                
                self._update_stats("decompose_task", result.get("success", False), time.time() - start_time)
                
                return APIResponse(
                    success=result.get("success", False),
                    data=result.get("enhanced_decomposition") if result.get("success") else None,
                    error=result.get("error") if not result.get("success") else None
                )
                
            except Exception as e:
                self._update_stats("decompose_task", False, time.time() - start_time)
                logger.error(f"任务分解失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 增强理解
        @self.app.post("/api/v1/ai/enhance-understanding", response_model=APIResponse)
        async def enhance_understanding(request: IntentAnalysisRequest):
            """AI增强理解接口"""
            try:
                start_time = time.time()
                
                result = self.ai_enhanced.process({
                    "action": "enhance_understanding",
                    "parameters": {
                        "user_input": request.user_input,
                        "context": request.context
                    }
                })
                
                self._update_stats("enhance_understanding", result.get("success", False), time.time() - start_time)
                
                return APIResponse(
                    success=result.get("success", False),
                    data=result.get("enhanced_understanding") if result.get("success") else None,
                    error=result.get("error") if not result.get("success") else None
                )
                
            except Exception as e:
                self._update_stats("enhance_understanding", False, time.time() - start_time)
                logger.error(f"增强理解失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # GitHub工作流触发
        @self.app.post("/api/v1/github/trigger-workflow", response_model=APIResponse)
        async def trigger_github_workflow(request: GitHubWorkflowRequest):
            """触发GitHub工作流接口"""
            try:
                start_time = time.time()
                
                result = self.ai_enhanced.process({
                    "action": "trigger_github_workflow",
                    "parameters": {
                        "workflow_id": request.workflow_id,
                        "ref": request.ref,
                        "inputs": request.inputs
                    }
                })
                
                self._update_stats("trigger_github_workflow", result.get("success", False), time.time() - start_time)
                
                return APIResponse(
                    success=result.get("success", False),
                    data=result.get("trigger_result") if result.get("success") else None,
                    error=result.get("error") if not result.get("success") else None
                )
                
            except Exception as e:
                self._update_stats("trigger_github_workflow", False, time.time() - start_time)
                logger.error(f"触发GitHub工作流失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 工作流监控
        @self.app.get("/api/v1/github/workflow/{run_id}", response_model=APIResponse)
        async def monitor_workflow(run_id: int):
            """监控GitHub工作流接口"""
            try:
                start_time = time.time()
                
                result = self.ai_enhanced.process({
                    "action": "monitor_workflow",
                    "parameters": {"run_id": run_id}
                })
                
                self._update_stats("monitor_workflow", result.get("success", False), time.time() - start_time)
                
                return APIResponse(
                    success=result.get("success", False),
                    data=result.get("run_info") if result.get("success") else None,
                    error=result.get("error") if not result.get("success") else None
                )
                
            except Exception as e:
                self._update_stats("monitor_workflow", False, time.time() - start_time)
                logger.error(f"监控工作流失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 工作流编排
        @self.app.post("/api/v1/workflow/orchestrate", response_model=APIResponse)
        async def orchestrate_workflow(request: WorkflowExecutionRequest):
            """工作流编排接口"""
            try:
                start_time = time.time()
                
                mcp_request = {
                    "method": "workflow_orchestration",
                    "params": {
                        "workflow_definition": request.workflow_definition,
                        "inputs": request.inputs,
                        "execution_mode": request.execution_mode
                    }
                }
                
                result = await self._call_mcp_server(mcp_request)
                
                self._update_stats("orchestrate_workflow", True, time.time() - start_time)
                
                return APIResponse(
                    success=True,
                    data=result
                )
                
            except Exception as e:
                self._update_stats("orchestrate_workflow", False, time.time() - start_time)
                logger.error(f"工作流编排失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 统计信息
        @self.app.get("/api/v1/stats", response_model=APIResponse)
        async def get_statistics():
            """获取统计信息接口"""
            try:
                # 获取MCP服务器统计
                mcp_stats = await self._call_mcp_server({
                    "method": "server_statistics",
                    "params": {}
                })
                
                # 获取AI组件统计
                ai_stats = self.ai_enhanced.process({
                    "action": "get_statistics"
                })
                
                combined_stats = {
                    "api_stats": self.api_stats,
                    "mcp_stats": mcp_stats,
                    "ai_stats": ai_stats.get("statistics", {})
                }
                
                return APIResponse(
                    success=True,
                    data=combined_stats
                )
                
            except Exception as e:
                logger.error(f"获取统计信息失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # 流式响应示例
        @self.app.post("/api/v1/stream/execute")
        async def stream_execute(request: ToolExecutionRequest):
            """流式执行接口"""
            async def generate_stream():
                try:
                    # 模拟流式响应
                    yield f"data: {json.dumps({'status': 'started', 'tool': request.tool_name})}\n\n"
                    
                    # 执行工具
                    mcp_request = {
                        "method": "smart_tool_execution",
                        "params": {
                            "tool_name": request.tool_name,
                            "parameters": request.parameters,
                            "context": request.context
                        }
                    }
                    
                    result = await self._call_mcp_server(mcp_request)
                    
                    yield f"data: {json.dumps({'status': 'completed', 'result': result})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"Cache-Control": "no-cache"}
            )
    
    async def _call_mcp_server(self, request: Dict) -> Any:
        """调用MCP服务器"""
        try:
            # 这里需要实现实际的MCP服务器调用
            # 目前使用模拟响应
            method = request.get("method", "")
            params = request.get("params", {})
            
            if method == "intelligent_tool_discovery":
                return {
                    "tools": [
                        {
                            "name": "calendar_create",
                            "description": "创建日历事件",
                            "platform": "aci.dev"
                        },
                        {
                            "name": "data_analyzer",
                            "description": "数据分析工具",
                            "platform": "mcp.so"
                        }
                    ],
                    "total": 2,
                    "query": params.get("query", "")
                }
            elif method == "smart_tool_execution":
                return {
                    "execution_id": f"exec_{int(time.time())}",
                    "tool_name": params.get("tool_name"),
                    "status": "completed",
                    "result": {"message": "执行成功"},
                    "execution_time": 1.5
                }
            elif method == "workflow_orchestration":
                return {
                    "workflow_id": f"wf_{int(time.time())}",
                    "status": "running",
                    "steps": len(params.get("workflow_definition", {}).get("steps", [])),
                    "estimated_completion": time.time() + 300
                }
            elif method == "server_statistics":
                return {
                    "total_tools": 150,
                    "total_executions": 1250,
                    "success_rate": 0.94,
                    "avg_response_time": 1.2
                }
            else:
                return {"message": f"模拟响应: {method}"}
                
        except Exception as e:
            logger.error(f"MCP服务器调用失败: {e}")
            raise
    
    def _update_stats(self, endpoint: str, success: bool, response_time: float):
        """更新API统计"""
        self.api_stats["total_requests"] += 1
        
        if success:
            self.api_stats["successful_requests"] += 1
        else:
            self.api_stats["failed_requests"] += 1
        
        # 更新平均响应时间
        total = self.api_stats["total_requests"]
        current_avg = self.api_stats["avg_response_time"]
        self.api_stats["avg_response_time"] = ((current_avg * (total - 1)) + response_time) / total
        
        # 更新端点使用统计
        if endpoint not in self.api_stats["endpoints_usage"]:
            self.api_stats["endpoints_usage"][endpoint] = {"count": 0, "success": 0, "avg_time": 0.0}
        
        endpoint_stats = self.api_stats["endpoints_usage"][endpoint]
        endpoint_stats["count"] += 1
        if success:
            endpoint_stats["success"] += 1
        
        # 更新端点平均时间
        count = endpoint_stats["count"]
        current_avg = endpoint_stats["avg_time"]
        endpoint_stats["avg_time"] = ((current_avg * (count - 1)) + response_time) / count
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """启动HTTP API服务器"""
        logger.info(f"启动MCP HTTP API服务器: http://{host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()

# 启动脚本
async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP HTTP API服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机")
    parser.add_argument("--port", type=int, default=8080, help="服务器端口")
    parser.add_argument("--config", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # 创建并启动服务器
    server = MCPHTTPAPIServer(config)
    await server.start_server(args.host, args.port)

if __name__ == "__main__":
    asyncio.run(main())

