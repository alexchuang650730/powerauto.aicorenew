"""
智能MCP工具引擎服务器
基于MCP协议的统一工具发现和执行服务器
参考ACI.dev的MCP实现设计
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from adapters.unified_smart_tool_engine_mcp_v2 import UnifiedSmartToolEngineMCP
from adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP

logger = logging.getLogger(__name__)

class MCPToolEngineServer:
    """智能MCP工具引擎服务器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # 初始化核心适配器
        self.tool_engine = UnifiedSmartToolEngineMCP(config)
        self.workflow_engine = IntelligentWorkflowEngineMCP(config)
        
        # 服务器状态
        self.server_info = {
            "name": "Intelligent MCP Tool Engine Server",
            "version": "1.0.0",
            "description": "统一的智能MCP工具发现和执行服务器",
            "capabilities": [
                "tool_discovery",
                "intelligent_routing", 
                "multi_platform_execution",
                "workflow_orchestration",
                "performance_optimization"
            ]
        }
        
        # 工具注册表
        self.available_tools = {
            "INTELLIGENT_TOOL_DISCOVERY": {
                "name": "intelligent_tool_discovery",
                "description": "智能工具发现和推荐",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索查询"},
                        "filters": {"type": "object", "description": "过滤条件"},
                        "limit": {"type": "integer", "description": "结果数量限制"}
                    },
                    "required": ["query"]
                }
            },
            "SMART_TOOL_EXECUTION": {
                "name": "smart_tool_execution", 
                "description": "智能工具执行",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "request": {"type": "string", "description": "用户请求"},
                        "context": {"type": "object", "description": "执行上下文"}
                    },
                    "required": ["request"]
                }
            },
            "WORKFLOW_ORCHESTRATION": {
                "name": "workflow_orchestration",
                "description": "智能工作流编排",
                "input_schema": {
                    "type": "object", 
                    "properties": {
                        "request": {"type": "string", "description": "工作流请求"},
                        "context": {"type": "object", "description": "工作流上下文"}
                    },
                    "required": ["request"]
                }
            },
            "TOOL_REGISTRATION": {
                "name": "tool_registration",
                "description": "工具注册",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tool_info": {"type": "object", "description": "工具信息"}
                    },
                    "required": ["tool_info"]
                }
            },
            "SERVER_STATISTICS": {
                "name": "server_statistics",
                "description": "服务器统计信息",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
        logger.info("智能MCP工具引擎服务器初始化完成")
    
    async def handle_initialize(self, params: Dict) -> Dict:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            },
            "serverInfo": self.server_info
        }
    
    async def handle_list_tools(self, params: Dict) -> Dict:
        """处理工具列表请求"""
        tools = []
        
        for tool_id, tool_info in self.available_tools.items():
            tools.append({
                "name": tool_info["name"],
                "description": tool_info["description"],
                "inputSchema": tool_info["input_schema"]
            })
        
        return {"tools": tools}
    
    async def handle_call_tool(self, params: Dict) -> Dict:
        """处理工具调用请求"""
        try:
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
            
            if tool_name == "intelligent_tool_discovery":
                result = await self._handle_tool_discovery(arguments)
            elif tool_name == "smart_tool_execution":
                result = await self._handle_tool_execution(arguments)
            elif tool_name == "workflow_orchestration":
                result = await self._handle_workflow_orchestration(arguments)
            elif tool_name == "tool_registration":
                result = await self._handle_tool_registration(arguments)
            elif tool_name == "server_statistics":
                result = await self._handle_server_statistics(arguments)
            else:
                result = {
                    "success": False,
                    "error": f"未知工具: {tool_name}",
                    "available_tools": list(self.available_tools.keys())
                }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, ensure_ascii=False)
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"工具调用失败: {e}")
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": json.dumps({
                            "success": False,
                            "error": str(e),
                            "tool_name": params.get("name")
                        }, indent=2, ensure_ascii=False)
                    }
                ],
                "isError": True
            }
    
    async def _handle_tool_discovery(self, arguments: Dict) -> Dict:
        """处理工具发现请求"""
        query = arguments.get("query", "")
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 10)
        
        result = self.tool_engine.process({
            "action": "discover_tools",
            "parameters": {
                "query": query,
                "filters": filters,
                "limit": limit
            }
        })
        
        return result
    
    async def _handle_tool_execution(self, arguments: Dict) -> Dict:
        """处理工具执行请求"""
        request = arguments.get("request", "")
        context = arguments.get("context", {})
        
        result = self.tool_engine.process({
            "action": "execute_request",
            "parameters": {
                "request": request,
                "context": context
            }
        })
        
        return result
    
    async def _handle_workflow_orchestration(self, arguments: Dict) -> Dict:
        """处理工作流编排请求"""
        request = arguments.get("request", "")
        context = arguments.get("context", {})
        
        result = self.workflow_engine.process({
            "action": "process_user_request",
            "parameters": {
                "request": request,
                "context": context
            }
        })
        
        return result
    
    async def _handle_tool_registration(self, arguments: Dict) -> Dict:
        """处理工具注册请求"""
        tool_info = arguments.get("tool_info", {})
        
        result = self.tool_engine.process({
            "action": "register_tool",
            "parameters": {
                "tool_info": tool_info
            }
        })
        
        return result
    
    async def _handle_server_statistics(self, arguments: Dict) -> Dict:
        """处理服务器统计请求"""
        tool_stats = self.tool_engine.process({
            "action": "get_statistics"
        })
        
        workflow_stats = self.workflow_engine.process({
            "action": "get_workflow_stats"
        })
        
        return {
            "success": True,
            "server_info": self.server_info,
            "tool_engine_stats": tool_stats,
            "workflow_engine_stats": workflow_stats,
            "timestamp": time.time()
        }
    
    async def handle_list_resources(self, params: Dict) -> Dict:
        """处理资源列表请求"""
        return {
            "resources": [
                {
                    "uri": "tool://registry",
                    "name": "工具注册表",
                    "description": "统一工具注册表资源",
                    "mimeType": "application/json"
                },
                {
                    "uri": "stats://execution",
                    "name": "执行统计",
                    "description": "工具执行统计信息",
                    "mimeType": "application/json"
                }
            ]
        }
    
    async def handle_read_resource(self, params: Dict) -> Dict:
        """处理资源读取请求"""
        uri = params.get("uri", "")
        
        if uri == "tool://registry":
            registry_data = {
                "total_tools": len(self.tool_engine.registry.tools_db),
                "tools": list(self.tool_engine.registry.tools_db.keys()),
                "platforms": ["aci.dev", "mcp.so", "zapier"]
            }
            
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(registry_data, indent=2, ensure_ascii=False)
                    }
                ]
            }
        
        elif uri == "stats://execution":
            stats = self.tool_engine.execution_engine.get_execution_statistics()
            
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json", 
                        "text": json.dumps(stats, indent=2, ensure_ascii=False)
                    }
                ]
            }
        
        else:
            return {
                "contents": [],
                "error": f"未知资源: {uri}"
            }

class MCPServerRunner:
    """MCP服务器运行器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.server = MCPToolEngineServer(config)
        
    async def run_stdio_server(self):
        """运行标准输入输出服务器"""
        logger.info("启动MCP工具引擎服务器 (stdio模式)")
        
        while True:
            try:
                # 读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                # 解析JSON-RPC请求
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {e}")
                    continue
                
                # 处理请求
                response = await self._handle_request(request)
                
                # 发送响应
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f"服务器错误: {e}")
                break
    
    async def _handle_request(self, request: Dict) -> Dict:
        """处理MCP请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                result = await self.server.handle_initialize(params)
            elif method == "tools/list":
                result = await self.server.handle_list_tools(params)
            elif method == "tools/call":
                result = await self.server.handle_call_tool(params)
            elif method == "resources/list":
                result = await self.server.handle_list_resources(params)
            elif method == "resources/read":
                result = await self.server.handle_read_resource(params)
            else:
                result = {
                    "error": {
                        "code": -32601,
                        "message": f"未知方法: {method}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"请求处理失败: {e}")
            return {
                "jsonrpc": "2.0", 
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能MCP工具引擎服务器")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio", 
                       help="服务器模式")
    parser.add_argument("--port", type=int, default=8000, help="HTTP端口")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建服务器配置
    config = {
        "mode": args.mode,
        "port": args.port
    }
    
    # 启动服务器
    runner = MCPServerRunner(config)
    
    if args.mode == "stdio":
        await runner.run_stdio_server()
    else:
        logger.info(f"HTTP模式暂未实现，使用stdio模式")
        await runner.run_stdio_server()

if __name__ == "__main__":
    asyncio.run(main())

