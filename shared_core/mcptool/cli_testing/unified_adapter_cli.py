#!/usr/bin/env python3
"""
PowerAutomation增強適配器統一CLI接口

提供所有增強適配器的統一命令行接口
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified_cli")

class UnifiedAdapterCLI:
    """統一適配器CLI"""
    
    def __init__(self):
        """初始化CLI"""
        self.adapters = {}
        self._load_adapters()
    
    def _load_adapters(self):
        """加載所有適配器"""
        try:
            # 增強ACI.dev適配器
            sys.path.append('/home/ubuntu/projects/communitypowerautomation')
            from mcptool.adapters.enhanced_aci_dev_adapter_mcp import EnhancedACIDevAdapterMCP
            self.adapters['aci_dev'] = EnhancedACIDevAdapterMCP()
            logger.info("增強ACI.dev適配器加載成功")
        except Exception as e:
            logger.warning(f"增強ACI.dev適配器加載失敗: {e}")
        
        try:
            # 統一智能工具引擎 (包含MCP.so功能)
            from mcptool.adapters.unified_smart_tool_engine.smart_tool_engine_mcp import SmartToolEngineMCP
            self.adapters['smart_tool_engine'] = SmartToolEngineMCP()
            logger.info("統一智能工具引擎加載成功")
        except Exception as e:
            logger.warning(f"統一智能工具引擎加載失敗: {e}")
        
        try:
            # 無限上下文適配器
            from mcptool.adapters.infinite_context_adapter_mcp_v2 import InfiniteContextAdapterMCP
            self.adapters['infinite_context'] = InfiniteContextAdapterMCP()
            logger.info("無限上下文適配器加載成功")
        except Exception as e:
            logger.warning(f"無限上下文適配器加載失敗: {e}")
        
        try:
            # 真實AI API適配器
            from mcptool.adapters.real_ai_api_adapter_mcp import RealAIAPIAdapterMCP
            self.adapters['real_ai_api'] = RealAIAPIAdapterMCP()
            logger.info("真實AI API適配器加載成功")
        except Exception as e:
            logger.warning(f"真實AI API適配器加載失敗: {e}")
        
        try:
            # Zapier適配器
            from mcptool.adapters.zapier_adapter_mcp import ZapierAdapterMCP
            self.adapters['zapier'] = ZapierAdapterMCP()
            logger.info("Zapier適配器加載成功")
        except Exception as e:
            logger.warning(f"Zapier適配器加載失敗: {e}")
    
    def list_adapters(self) -> Dict[str, Any]:
        """列出所有適配器"""
        adapter_info = {}
        
        for name, adapter in self.adapters.items():
            try:
                # 獲取適配器基本信息
                info_request = {'action': 'list_tools'}
                response = adapter.process(info_request)
                
                if response.get('status') == 'success':
                    data = response.get('data', {})
                    adapter_info[name] = {
                        'name': name,
                        'status': 'available',
                        'tools_count': data.get('total_count', 0),
                        'adapter_info': data.get('adapter_info', {}),
                        'tools': data.get('tools', [])
                    }
                else:
                    adapter_info[name] = {
                        'name': name,
                        'status': 'error',
                        'error': response.get('message', 'Unknown error')
                    }
            
            except Exception as e:
                adapter_info[name] = {
                    'name': name,
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'status': 'success',
            'message': f'找到 {len(self.adapters)} 個適配器',
            'data': {
                'adapters': adapter_info,
                'total_adapters': len(self.adapters),
                'available_adapters': len([a for a in adapter_info.values() if a['status'] == 'available'])
            }
        }
    
    def execute_adapter_action(self, adapter_name: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行適配器操作"""
        if adapter_name not in self.adapters:
            return {
                'status': 'error',
                'message': f'適配器不存在: {adapter_name}',
                'data': None
            }
        
        try:
            adapter = self.adapters[adapter_name]
            request = {
                'action': action,
                'parameters': parameters or {}
            }
            
            response = adapter.process(request)
            
            # 添加適配器信息
            if isinstance(response, dict):
                response['adapter_name'] = adapter_name
                response['action_executed'] = action
            
            return response
        
        except Exception as e:
            logger.error(f"執行適配器 {adapter_name} 操作 {action} 時出錯: {e}")
            return {
                'status': 'error',
                'message': f'適配器操作失敗: {str(e)}',
                'data': {
                    'adapter_name': adapter_name,
                    'action': action,
                    'error': str(e)
                }
            }
    
    def search_tools_across_adapters(self, query: str) -> Dict[str, Any]:
        """跨適配器搜索工具"""
        all_results = {}
        total_found = 0
        
        for adapter_name, adapter in self.adapters.items():
            try:
                request = {
                    'action': 'search_tools',
                    'parameters': {'query': query}
                }
                
                response = adapter.process(request)
                
                if response.get('status') == 'success':
                    data = response.get('data', {})
                    found_count = data.get('total_found', 0)
                    
                    if found_count > 0:
                        all_results[adapter_name] = {
                            'adapter_name': adapter_name,
                            'found_count': found_count,
                            'tools': data.get('relevant_tools', [])
                        }
                        total_found += found_count
            
            except Exception as e:
                logger.warning(f"在適配器 {adapter_name} 中搜索失敗: {e}")
        
        return {
            'status': 'success',
            'message': f'跨 {len(all_results)} 個適配器找到 {total_found} 個相關工具',
            'data': {
                'query': query,
                'results_by_adapter': all_results,
                'total_found': total_found,
                'adapters_searched': len(self.adapters),
                'adapters_with_results': len(all_results)
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        status_info = {}
        total_tools = 0
        
        for adapter_name, adapter in self.adapters.items():
            try:
                # 嘗試獲取適配器狀態
                if hasattr(adapter, 'process'):
                    request = {'action': 'list_tools'}
                    response = adapter.process(request)
                    
                    if response.get('status') == 'success':
                        data = response.get('data', {})
                        tools_count = data.get('total_count', 0)
                        total_tools += tools_count
                        
                        status_info[adapter_name] = {
                            'status': 'healthy',
                            'tools_count': tools_count,
                            'adapter_info': data.get('adapter_info', {})
                        }
                    else:
                        status_info[adapter_name] = {
                            'status': 'error',
                            'error': response.get('message', 'Unknown error')
                        }
                else:
                    status_info[adapter_name] = {
                        'status': 'invalid',
                        'error': 'Adapter does not support process method'
                    }
            
            except Exception as e:
                status_info[adapter_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        healthy_adapters = len([s for s in status_info.values() if s['status'] == 'healthy'])
        
        return {
            'status': 'success',
            'message': f'系統狀態檢查完成，{healthy_adapters}/{len(self.adapters)} 個適配器正常',
            'data': {
                'adapters_status': status_info,
                'total_adapters': len(self.adapters),
                'healthy_adapters': healthy_adapters,
                'total_tools': total_tools,
                'system_health': 'good' if healthy_adapters >= len(self.adapters) * 0.8 else 'degraded'
            }
        }
    
    def process_query(self, query: str, adapter_name: str = None) -> Dict[str, Any]:
        """處理查詢請求 - 為GAIA測試提供的統一接口"""
        try:
            # 如果沒有指定適配器，自動選擇最佳適配器
            if not adapter_name:
                adapter_name = self._select_best_adapter_for_query(query)
            
            # 檢查適配器是否存在
            if adapter_name not in self.adapters:
                return {
                    'result': f'適配器不存在: {adapter_name}',
                    'confidence': 0.0,
                    'api_calls': 0,
                    'adapter_used': adapter_name,
                    'status': 'error'
                }
            
            # 根據適配器類型選擇合適的工具和參數
            tool_request = self._prepare_tool_request(query, adapter_name)
            
            # 執行適配器操作
            adapter = self.adapters[adapter_name]
            response = adapter.process(tool_request)
            
            # 處理響應
            if response.get('status') == 'success':
                data = response.get('data', {})
                result = data.get('result', str(data))
                
                return {
                    'result': result,
                    'confidence': data.get('confidence', 0.8),
                    'api_calls': data.get('api_calls', 1),
                    'adapter_used': adapter_name,
                    'status': 'success'
                }
            else:
                return {
                    'result': response.get('message', 'Unknown error'),
                    'confidence': 0.0,
                    'api_calls': 0,
                    'adapter_used': adapter_name,
                    'status': 'error'
                }
        
        except Exception as e:
            logger.error(f"處理查詢時出錯: {e}")
            return {
                'result': f'處理查詢時出錯: {str(e)}',
                'confidence': 0.0,
                'api_calls': 0,
                'adapter_used': adapter_name or 'unknown',
                'status': 'error'
            }
    
    def _select_best_adapter_for_query(self, query: str) -> str:
        """為查詢選擇最佳適配器"""
        query_lower = query.lower()
        
        # 數學計算問題
        if any(word in query_lower for word in ['calculate', 'compute', 'math', '計算', '數學', 'distance', 'speed', 'time']):
            return 'aci_dev'
        
        # 需要搜索的問題
        elif any(word in query_lower for word in ['who', 'what', 'when', 'where', 'search', '誰', '什麼', '何時', '哪裡', 'find', 'album', 'song']):
            return 'real_ai_api'
        
        # 自動化工作流問題
        elif any(word in query_lower for word in ['workflow', 'automation', 'process', '工作流', '自動化', 'zapier']):
            return 'zapier'
        
        # 複雜推理問題
        elif any(word in query_lower for word in ['analyze', 'reasoning', 'logic', '分析', '推理', '邏輯', 'game', 'strategy', 'rule']):
            return 'infinite_context'
        
        # 專業工具問題
        elif any(word in query_lower for word in ['data', 'file', 'document', '數據', '文件', '文檔']):
            return 'mcp_so'
        
        # 默認使用真實AI API
        else:
            return 'real_ai_api'
    
    def _prepare_tool_request(self, query: str, adapter_name: str) -> Dict[str, Any]:
        """為特定適配器準備工具請求"""
        base_request = {
            'action': 'execute_tool',
            'parameters': {}
        }
        
        if adapter_name == 'aci_dev':
            # ACI.dev適配器 - 使用智能分析器
            base_request['parameters'] = {
                'tool_name': 'intelligent_analyzer',
                'tool_params': {
                    'query': query,
                    'analysis_type': 'comprehensive'
                }
            }
        
        elif adapter_name == 'real_ai_api':
            # 真實AI API適配器 - 使用文本生成
            base_request['parameters'] = {
                'tool_name': 'generate_text',
                'tool_params': {
                    'prompt': f"Please answer this question accurately and concisely: {query}",
                    'max_tokens': 200,
                    'temperature': 0.1
                }
            }
        
        elif adapter_name == 'infinite_context':
            # 無限上下文適配器 - 使用上下文分析
            base_request['parameters'] = {
                'tool_name': 'analyze_context',
                'tool_params': {
                    'text': query,
                    'context_type': 'question_answering',
                    'analysis_depth': 'deep'
                }
            }
        
        elif adapter_name == 'zapier':
            # Zapier適配器 - 使用自動化構建器
            base_request['parameters'] = {
                'tool_name': 'automation_builder',
                'tool_params': {
                    'description': query,
                    'auto_execute': False
                }
            }
        
        elif adapter_name == 'mcp_so':
            # MCP.so適配器 - 使用數據分析器
            base_request['parameters'] = {
                'tool_name': 'data_analyzer',
                'tool_params': {
                    'query': query,
                    'analysis_type': 'comprehensive'
                }
            }
        
        else:
            # 默認請求
            base_request['parameters'] = {
                'tool_name': 'general_processor',
                'tool_params': {
                    'input': query
                }
            }
        
        return base_request

    def run_integration_test(self) -> Dict[str, Any]:
        """運行集成測試"""
        test_results = {}
        
        for adapter_name, adapter in self.adapters.items():
            test_results[adapter_name] = self._test_adapter(adapter_name, adapter)
        
        successful_tests = len([r for r in test_results.values() if r['status'] == 'success'])
        
        return {
            'status': 'success',
            'message': f'集成測試完成，{successful_tests}/{len(test_results)} 個適配器通過測試',
            'data': {
                'test_results': test_results,
                'total_tests': len(test_results),
                'successful_tests': successful_tests,
                'test_coverage': successful_tests / len(test_results) if test_results else 0
            }
        }
    
    def _test_adapter(self, adapter_name: str, adapter) -> Dict[str, Any]:
        """測試單個適配器"""
        try:
            # 測試基本功能
            tests = [
                {'action': 'list_tools', 'parameters': {}},
            ]
            
            # 根據適配器類型添加特定測試
            if adapter_name == 'aci_dev':
                tests.append({
                    'action': 'execute_tool',
                    'parameters': {
                        'tool_name': 'advanced_calculator',
                        'tool_params': {'expression': '2+2', 'precision': 2}
                    }
                })
            elif adapter_name == 'infinite_context':
                tests.append({
                    'action': 'execute_tool',
                    'parameters': {
                        'tool_name': 'analyze_context',
                        'tool_params': {'text': 'This is a test context.', 'context_type': 'test'}
                    }
                })
            elif adapter_name == 'real_ai_api':
                tests.append({
                    'action': 'execute_tool',
                    'parameters': {
                        'tool_name': 'generate_text',
                        'tool_params': {'prompt': 'Hello, world!', 'max_tokens': 50}
                    }
                })
            elif adapter_name == 'zapier':
                tests.append({
                    'action': 'execute_tool',
                    'parameters': {
                        'tool_name': 'list_apps',
                        'tool_params': {'category': 'Email'}
                    }
                })
            
            test_results = []
            for test in tests:
                try:
                    response = adapter.process(test)
                    test_results.append({
                        'test': test['action'],
                        'status': response.get('status', 'unknown'),
                        'success': response.get('status') == 'success'
                    })
                except Exception as e:
                    test_results.append({
                        'test': test['action'],
                        'status': 'error',
                        'error': str(e),
                        'success': False
                    })
            
            successful_tests = len([t for t in test_results if t['success']])
            
            return {
                'status': 'success' if successful_tests == len(test_results) else 'partial',
                'tests_run': len(test_results),
                'tests_passed': successful_tests,
                'test_details': test_results
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'tests_run': 0,
                'tests_passed': 0
            }

def create_cli_parser():
    """創建CLI解析器"""
    parser = argparse.ArgumentParser(description='PowerAutomation增強適配器統一CLI')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出適配器
    list_parser = subparsers.add_parser('list', help='列出所有適配器')
    
    # 執行適配器操作
    exec_parser = subparsers.add_parser('exec', help='執行適配器操作')
    exec_parser.add_argument('--adapter', required=True, help='適配器名稱')
    exec_parser.add_argument('--action', required=True, help='操作名稱')
    exec_parser.add_argument('--params', help='參數（JSON格式）')
    
    # 搜索工具
    search_parser = subparsers.add_parser('search', help='搜索工具')
    search_parser.add_argument('--query', required=True, help='搜索查詢')
    
    # 系統狀態
    status_parser = subparsers.add_parser('status', help='獲取系統狀態')
    
    # 集成測試
    test_parser = subparsers.add_parser('test', help='運行集成測試')
    
    return parser

def main():
    """主函數"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化CLI
    cli = UnifiedAdapterCLI()
    
    try:
        if args.command == 'list':
            result = cli.list_adapters()
        
        elif args.command == 'exec':
            params = {}
            if args.params:
                try:
                    params = json.loads(args.params)
                except json.JSONDecodeError:
                    print("錯誤: 參數必須是有效的JSON格式")
                    return
            
            result = cli.execute_adapter_action(args.adapter, args.action, params)
        
        elif args.command == 'search':
            result = cli.search_tools_across_adapters(args.query)
        
        elif args.command == 'status':
            result = cli.get_system_status()
        
        elif args.command == 'test':
            result = cli.run_integration_test()
        
        else:
            print(f"未知命令: {args.command}")
            return
        
        # 輸出結果
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    except Exception as e:
        print(f"執行命令時出錯: {e}")
        return 1

if __name__ == "__main__":
    main()

