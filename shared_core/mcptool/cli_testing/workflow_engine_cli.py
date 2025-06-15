#!/usr/bin/env python3
"""
智能工作流引擎CLI - 統一工具注册表接口

提供對IntelligentWorkflowEngineMCP的完整CLI訪問，包括：
- 統一工具注册表管理
- Claude MCP集成
- 工作流執行和管理
- AI增強功能
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("workflow_engine_cli")

class WorkflowEngineCLI:
    """智能工作流引擎CLI接口"""
    
    def __init__(self):
        """初始化CLI"""
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化工作流引擎"""
        try:
            from mcptool.adapters.intelligent_workflow_engine_mcp import get_instance
            self.engine = get_instance()
            logger.info("智能工作流引擎初始化成功")
        except Exception as e:
            logger.error(f"工作流引擎初始化失敗: {e}")
            self.engine = None
    
    def list_tools(self, category: Optional[str] = None, platform: Optional[str] = None) -> Dict[str, Any]:
        """列出所有可用工具"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            # 獲取統一工具引擎中的工具
            result = self.engine.process({
                "action": "list_unified_tools",
                "parameters": {
                    "category": category,
                    "platform": platform
                }
            })
            
            if result.get("success"):
                tools = result.get("data", {}).get("tools", [])
                return {
                    "success": True,
                    "total_tools": len(tools),
                    "tools": tools,
                    "categories": self._get_tool_categories(tools),
                    "platforms": self._get_tool_platforms(tools)
                }
            else:
                # 如果統一工具引擎不可用，返回基礎工具列表
                return self._get_basic_tools()
                
        except Exception as e:
            logger.error(f"列出工具失敗: {e}")
            return {"error": str(e)}
    
    def _get_basic_tools(self) -> Dict[str, Any]:
        """獲取基礎工具列表"""
        basic_tools = []
        
        # 從IntelligentWorkflowEngineMCP獲取工具
        if self.engine:
            # AgentProblemSolverMCP工具
            if hasattr(self.engine, 'agent_problem_solver') and self.engine.agent_problem_solver:
                problem_solver_tools = [
                    {
                        "name": "analyze_problem",
                        "description": "分析和識別問題的根本原因",
                        "category": "problem_solving",
                        "platform": "agent_problem_solver",
                        "capabilities": ["analyze", "identify", "categorize"],
                        "parameters": {
                            "problem_description": "string",
                            "context": "object"
                        }
                    },
                    {
                        "name": "solve_problem", 
                        "description": "提供問題的自動化解決方案",
                        "category": "problem_solving",
                        "platform": "agent_problem_solver",
                        "capabilities": ["solve", "recommend", "automate"],
                        "parameters": {
                            "problem_id": "integer"
                        }
                    },
                    {
                        "name": "get_problem_history",
                        "description": "獲取問題分析歷史記錄",
                        "category": "data_retrieval",
                        "platform": "agent_problem_solver", 
                        "capabilities": ["retrieve", "filter", "export"],
                        "parameters": {
                            "limit": "integer"
                        }
                    },
                    {
                        "name": "get_solution_history",
                        "description": "獲取解決方案實施歷史",
                        "category": "data_retrieval",
                        "platform": "agent_problem_solver",
                        "capabilities": ["retrieve", "track", "analyze"],
                        "parameters": {
                            "limit": "integer"
                        }
                    }
                ]
                basic_tools.extend(problem_solver_tools)
            
            # ReleaseManagerMCP工具
            if hasattr(self.engine, 'release_manager') and self.engine.release_manager:
                release_manager_tools = [
                    {
                        "name": "create_release",
                        "description": "創建新的軟件發布版本",
                        "category": "release_management",
                        "platform": "release_manager",
                        "capabilities": ["create", "version", "package"],
                        "parameters": {
                            "version": "string",
                            "release_notes": "string"
                        }
                    },
                    {
                        "name": "run_code_detection",
                        "description": "運行代碼質量檢測和分析",
                        "category": "quality_assurance",
                        "platform": "release_manager",
                        "capabilities": ["detect", "analyze", "report"],
                        "parameters": {
                            "release_id": "integer"
                        }
                    },
                    {
                        "name": "run_tests",
                        "description": "執行自動化測試套件",
                        "category": "testing",
                        "platform": "release_manager",
                        "capabilities": ["test", "validate", "report"],
                        "parameters": {
                            "release_id": "integer"
                        }
                    },
                    {
                        "name": "deploy_release",
                        "description": "部署發布到指定環境",
                        "category": "deployment",
                        "platform": "release_manager",
                        "capabilities": ["deploy", "configure", "monitor"],
                        "parameters": {
                            "release_id": "integer",
                            "environment": "string"
                        }
                    },
                    {
                        "name": "verify_deployment",
                        "description": "驗證部署的健康狀態和性能",
                        "category": "verification",
                        "platform": "release_manager",
                        "capabilities": ["verify", "monitor", "validate"],
                        "parameters": {
                            "release_id": "integer"
                        }
                    }
                ]
                basic_tools.extend(release_manager_tools)
        
        # 添加其他基礎工具
        workflow_tools = [
            {
                "name": "workflow_analyzer",
                "description": "分析和執行智能工作流",
                "category": "workflow",
                "platform": "intelligent_workflow_engine",
                "capabilities": ["analyze", "execute", "monitor"],
                "parameters": {
                    "workflow_request": "string",
                    "context": "object"
                }
            },
            {
                "name": "context_manager",
                "description": "無限上下文管理和壓縮",
                "category": "memory",
                "platform": "infinite_context",
                "capabilities": ["store", "retrieve", "compress"],
                "parameters": {
                    "action": "string",
                    "data": "any"
                }
            },
            {
                "name": "claude_mcp",
                "description": "Claude MCP集成和AI生成",
                "category": "ai_generation",
                "platform": "claude",
                "capabilities": ["generate", "analyze", "code"],
                "parameters": {
                    "prompt": "string",
                    "task_type": "string"
                }
            }
        ]
        basic_tools.extend(workflow_tools)
        
        return {
            "success": True,
            "total_tools": len(basic_tools),
            "tools": basic_tools,
            "categories": list(set(tool["category"] for tool in basic_tools)),
            "platforms": list(set(tool["platform"] for tool in basic_tools))
        }
    
    def _get_tool_categories(self, tools: List[Dict]) -> List[str]:
        """獲取工具類別列表"""
        return list(set(tool.get("category", "unknown") for tool in tools))
    
    def _get_tool_platforms(self, tools: List[Dict]) -> List[str]:
        """獲取工具平台列表"""
        return list(set(tool.get("platform", "unknown") for tool in tools))
    
    def search_tools(self, query: str, category: Optional[str] = None, 
                    platform: Optional[str] = None) -> Dict[str, Any]:
        """搜索工具"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            result = self.engine.process({
                "action": "search_tools",
                "parameters": {
                    "query": query,
                    "filters": {
                        "category": category,
                        "platform": platform
                    }
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"搜索工具失敗: {e}")
            return {"error": str(e)}
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行指定工具"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            # 根據工具名稱路由到相應的MCP適配器
            if tool_name in ["analyze_problem", "solve_problem", "get_problem_history", "get_solution_history"]:
                # AgentProblemSolverMCP工具
                if hasattr(self.engine, 'agent_problem_solver') and self.engine.agent_problem_solver:
                    result = self.engine.agent_problem_solver.process({
                        "action": tool_name,
                        "parameters": parameters
                    })
                    return result
                else:
                    return {"error": "AgentProblemSolverMCP不可用"}
            
            elif tool_name in ["create_release", "run_code_detection", "run_tests", "deploy_release", "verify_deployment"]:
                # ReleaseManagerMCP工具
                if hasattr(self.engine, 'release_manager') and self.engine.release_manager:
                    result = self.engine.release_manager.process({
                        "action": tool_name,
                        "parameters": parameters
                    })
                    return result
                else:
                    return {"error": "ReleaseManagerMCP不可用"}
            
            elif tool_name == "workflow_analyzer":
                # 工作流分析器
                result = self.engine.process({
                    "action": "analyze_and_execute",
                    "parameters": parameters
                })
                return result
            
            else:
                # 通用工具執行
                result = self.engine.process({
                    "action": "execute_tool",
                    "parameters": {
                        "tool_name": tool_name,
                        "tool_parameters": parameters
                    }
                })
                return result
            
        except Exception as e:
            logger.error(f"執行工具失敗: {e}")
            return {"error": str(e)}
    
    def create_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """創建工作流"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            result = self.engine.process({
                "action": "create_workflow",
                "parameters": workflow_definition
            })
            
            return result
            
        except Exception as e:
            logger.error(f"創建工作流失敗: {e}")
            return {"error": str(e)}
    
    def execute_workflow(self, workflow_request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """執行工作流"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            result = self.engine.process({
                "action": "analyze_and_execute",
                "parameters": {
                    "request": workflow_request,
                    "context": context or {}
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"執行工作流失敗: {e}")
            return {"error": str(e)}
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """獲取工作流狀態"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            result = self.engine.process({
                "action": "get_workflow_status"
            })
            
            return result
            
        except Exception as e:
            logger.error(f"獲取工作流狀態失敗: {e}")
            return {"error": str(e)}
    
    def register_claude_mcp(self, api_key: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """註冊Claude MCP適配器"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            claude_config = {
                "name": "claude_mcp",
                "type": "ai_generation",
                "api_key": api_key,
                "capabilities": ["text_generation", "code_generation", "analysis", "reasoning"],
                **(config or {})
            }
            
            result = self.engine.process({
                "action": "register_adapter",
                "parameters": {
                    "adapter_type": "claude_mcp",
                    "config": claude_config
                }
            })
            
            return result
            
        except Exception as e:
            logger.error(f"註冊Claude MCP失敗: {e}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        if not self.engine:
            return {"error": "工作流引擎未初始化"}
        
        try:
            # 獲取基本狀態
            workflow_status = self.get_workflow_status()
            tools_info = self.list_tools()
            
            return {
                "success": True,
                "system_info": {
                    "engine_status": "running" if self.engine else "stopped",
                    "timestamp": datetime.now().isoformat()
                },
                "workflow_status": workflow_status,
                "tools_summary": {
                    "total_tools": tools_info.get("total_tools", 0),
                    "categories": len(tools_info.get("categories", [])),
                    "platforms": len(tools_info.get("platforms", []))
                }
            }
            
        except Exception as e:
            logger.error(f"獲取系統狀態失敗: {e}")
            return {"error": str(e)}

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="智能工作流引擎CLI - 統一工具注册表接口")
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出工具命令
    list_parser = subparsers.add_parser('list', help='列出所有可用工具')
    list_parser.add_argument('--category', help='按類別過濾')
    list_parser.add_argument('--platform', help='按平台過濾')
    list_parser.add_argument('--format', choices=['json', 'table'], default='table', help='輸出格式')
    
    # 搜索工具命令
    search_parser = subparsers.add_parser('search', help='搜索工具')
    search_parser.add_argument('query', help='搜索查詢')
    search_parser.add_argument('--category', help='按類別過濾')
    search_parser.add_argument('--platform', help='按平台過濾')
    
    # 執行工具命令
    exec_parser = subparsers.add_parser('exec', help='執行工具')
    exec_parser.add_argument('tool_name', help='工具名稱')
    exec_parser.add_argument('--params', help='工具參數 (JSON格式)')
    
    # 執行工作流命令
    workflow_parser = subparsers.add_parser('workflow', help='執行工作流')
    workflow_parser.add_argument('request', help='工作流請求描述')
    workflow_parser.add_argument('--context', help='上下文信息 (JSON格式)')
    
    # 系統狀態命令
    status_parser = subparsers.add_parser('status', help='獲取系統狀態')
    
    # 註冊Claude MCP命令
    claude_parser = subparsers.add_parser('register-claude', help='註冊Claude MCP適配器')
    claude_parser.add_argument('--api-key', required=True, help='Claude API密鑰')
    claude_parser.add_argument('--config', help='額外配置 (JSON格式)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化CLI
    cli = WorkflowEngineCLI()
    
    try:
        if args.command == 'list':
            result = cli.list_tools(args.category, args.platform)
            if args.format == 'json':
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                _print_tools_table(result)
        
        elif args.command == 'search':
            result = cli.search_tools(args.query, args.category, args.platform)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'exec':
            params = json.loads(args.params) if args.params else {}
            result = cli.execute_tool(args.tool_name, params)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'workflow':
            context = json.loads(args.context) if args.context else None
            result = cli.execute_workflow(args.request, context)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'status':
            result = cli.get_system_status()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'register-claude':
            config = json.loads(args.config) if args.config else None
            result = cli.register_claude_mcp(args.api_key, config)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        sys.exit(1)

def _print_tools_table(result: Dict[str, Any]):
    """以表格形式打印工具列表"""
    if not result.get("success"):
        print(f"❌ 錯誤: {result.get('error', '未知錯誤')}")
        return
    
    tools = result.get("tools", [])
    
    print(f"\n📋 可用工具 (總計: {result.get('total_tools', 0)})")
    print("=" * 80)
    
    for tool in tools:
        print(f"🔧 {tool.get('name', 'Unknown')}")
        print(f"   描述: {tool.get('description', 'No description')}")
        print(f"   類別: {tool.get('category', 'Unknown')}")
        print(f"   平台: {tool.get('platform', 'Unknown')}")
        if tool.get('capabilities'):
            print(f"   能力: {', '.join(tool['capabilities'])}")
        print()
    
    categories = result.get("categories", [])
    platforms = result.get("platforms", [])
    
    print(f"📊 類別: {', '.join(categories)}")
    print(f"🏢 平台: {', '.join(platforms)}")

if __name__ == "__main__":
    main()

