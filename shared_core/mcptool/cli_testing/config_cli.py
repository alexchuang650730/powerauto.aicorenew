#!/usr/bin/env python3
"""
統一配置器CLI接口 - PowerAutomation配置管理命令行工具
提供所有配置器的統一命令行接口
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List
from datetime import datetime

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_cli")

class ConfigCLI:
    """統一配置器CLI"""
    
    def __init__(self):
        """初始化CLI"""
        self.config_manager = None
        self._load_config_manager()
    
    def _load_config_manager(self):
        """加載統一配置器管理器"""
        try:
            from mcptool.adapters.unified_config_manager.config_manager_mcp import UnifiedConfigManagerMCP
            self.config_manager = UnifiedConfigManagerMCP()
            logger.info("統一配置器管理器加載成功")
        except Exception as e:
            logger.error(f"統一配置器管理器加載失敗: {e}")
            self.config_manager = None
    
    def run_config_command(self, args) -> Dict[str, Any]:
        """運行配置命令"""
        if not self.config_manager:
            return {
                'status': 'error',
                'message': '配置管理器未初始化',
                'data': None
            }
        
        try:
            if args.command == 'list':
                return self._list_configs(args)
            elif args.command == 'get':
                return self._get_config(args)
            elif args.command == 'set':
                return self._set_config(args)
            elif args.command == 'switch-api':
                return self._switch_api_mode(args)
            elif args.command == 'manage-keys':
                return self._manage_api_keys(args)
            elif args.command == 'test-api':
                return self._test_api_connection(args)
            elif args.command == 'export':
                return self._export_config(args)
            elif args.command == 'import':
                return self._import_config(args)
            elif args.command == 'reset':
                return self._reset_config(args)
            elif args.command == 'status':
                return self._get_system_status(args)
            else:
                return {
                    'status': 'error',
                    'message': f'未知命令: {args.command}',
                    'data': None
                }
        
        except Exception as e:
            logger.error(f"執行配置命令時出錯: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }
    
    def _list_configs(self, args) -> Dict[str, Any]:
        """列出配置"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'list_configs',
                'tool_params': {
                    'detailed': args.detailed if hasattr(args, 'detailed') else False
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _get_config(self, args) -> Dict[str, Any]:
        """獲取配置"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'get_config',
                'tool_params': {
                    'config_type': args.type,
                    'section': getattr(args, 'section', '')
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _set_config(self, args) -> Dict[str, Any]:
        """設置配置"""
        # 解析值
        value = args.value
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'set_config',
                'tool_params': {
                    'config_type': args.type,
                    'section': getattr(args, 'section', ''),
                    'key': args.key,
                    'value': value
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _switch_api_mode(self, args) -> Dict[str, Any]:
        """切換API模式"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'switch_api_mode',
                'tool_params': {
                    'mode': args.mode,
                    'api_provider': getattr(args, 'provider', 'all')
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _manage_api_keys(self, args) -> Dict[str, Any]:
        """管理API密鑰"""
        tool_params = {
            'action': args.action,
            'provider': getattr(args, 'provider', '')
        }
        
        if hasattr(args, 'key') and args.key:
            tool_params['api_key'] = args.key
        
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'manage_api_keys',
                'tool_params': tool_params
            }
        }
        
        return self.config_manager.process(request)
    
    def _test_api_connection(self, args) -> Dict[str, Any]:
        """測試API連接"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'test_api_connection',
                'tool_params': {
                    'provider': args.provider,
                    'test_type': getattr(args, 'test_type', 'basic')
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _export_config(self, args) -> Dict[str, Any]:
        """導出配置"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'export_config',
                'tool_params': {
                    'config_type': getattr(args, 'type', 'all'),
                    'format': getattr(args, 'format', 'json'),
                    'file_path': getattr(args, 'output', '')
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _import_config(self, args) -> Dict[str, Any]:
        """導入配置"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'import_config',
                'tool_params': {
                    'config_type': getattr(args, 'type', ''),
                    'file_path': args.file,
                    'merge': getattr(args, 'merge', True)
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _reset_config(self, args) -> Dict[str, Any]:
        """重置配置"""
        request = {
            'action': 'execute_tool',
            'parameters': {
                'tool_name': 'reset_config',
                'tool_params': {
                    'config_type': args.type,
                    'confirm': getattr(args, 'confirm', False)
                }
            }
        }
        
        return self.config_manager.process(request)
    
    def _get_system_status(self, args) -> Dict[str, Any]:
        """獲取系統狀態"""
        # 獲取所有配置的狀態
        status_info = {
            'timestamp': datetime.now().isoformat(),
            'config_manager': 'available' if self.config_manager else 'unavailable',
            'configs': {},
            'api_status': {},
            'system_health': 'unknown'
        }
        
        if self.config_manager:
            # 獲取配置列表
            list_request = {
                'action': 'execute_tool',
                'parameters': {
                    'tool_name': 'list_configs',
                    'tool_params': {'detailed': False}
                }
            }
            
            list_result = self.config_manager.process(list_request)
            if list_result.get('status') == 'success':
                status_info['configs'] = list_result['data']['result']['configs']
            
            # 獲取API密鑰狀態
            keys_request = {
                'action': 'execute_tool',
                'parameters': {
                    'tool_name': 'manage_api_keys',
                    'tool_params': {'action': 'list'}
                }
            }
            
            keys_result = self.config_manager.process(keys_request)
            if keys_result.get('status') == 'success':
                # 修正數據結構訪問
                result_data = keys_result.get('data', {}).get('result', {})
                if 'providers' in result_data:
                    status_info['api_status'] = result_data['providers']
                else:
                    # 如果沒有providers鍵，嘗試其他可能的結構
                    status_info['api_status'] = result_data
            
            # 計算系統健康狀態
            if status_info['api_status']:
                configured_apis = sum(1 for api_info in status_info['api_status'].values() 
                                    if api_info.get('status') == 'configured')
                total_apis = len(status_info['api_status'])
                
                if configured_apis >= total_apis * 0.75:
                    status_info['system_health'] = 'good'
                elif configured_apis >= total_apis * 0.5:
                    status_info['system_health'] = 'fair'
                else:
                    status_info['system_health'] = 'poor'
            else:
                status_info['system_health'] = 'unknown'
        
        return {
            'status': 'success',
            'message': '系統狀態獲取成功',
            'data': status_info
        }
    
    def _print_result(self, result: Dict[str, Any], format_type: str = 'pretty'):
        """打印結果"""
        if format_type == 'json':
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # 美化輸出
            if result.get('status') == 'success':
                print(f"✅ {result.get('message', '操作成功')}")
                
                data = result.get('data', {})
                if 'result' in data:
                    self._print_data(data['result'])
                elif data:
                    self._print_data(data)
            else:
                print(f"❌ {result.get('message', '操作失敗')}")
                if 'data' in result and result['data']:
                    self._print_data(result['data'])
    
    def _print_data(self, data: Any, indent: int = 0):
        """打印數據"""
        prefix = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}:")
                    self._print_data(value, indent + 1)
                else:
                    print(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                print(f"{prefix}[{i}]:")
                self._print_data(item, indent + 1)
        else:
            print(f"{prefix}{data}")

def create_cli_parser():
    """創建CLI解析器"""
    parser = argparse.ArgumentParser(description='PowerAutomation統一配置器CLI')
    parser.add_argument('--format', choices=['pretty', 'json'], default='pretty', help='輸出格式')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出配置
    list_parser = subparsers.add_parser('list', help='列出所有配置')
    list_parser.add_argument('--detailed', action='store_true', help='顯示詳細信息')
    
    # 獲取配置
    get_parser = subparsers.add_parser('get', help='獲取配置')
    get_parser.add_argument('--type', required=True, 
                           choices=['api_config', 'api_keys', 'intent_understanding', 'workflow_engine', 'system_settings'],
                           help='配置類型')
    get_parser.add_argument('--section', help='配置節')
    
    # 設置配置
    set_parser = subparsers.add_parser('set', help='設置配置')
    set_parser.add_argument('--type', required=True,
                           choices=['api_config', 'api_keys', 'intent_understanding', 'workflow_engine', 'system_settings'],
                           help='配置類型')
    set_parser.add_argument('--section', help='配置節')
    set_parser.add_argument('--key', required=True, help='配置鍵')
    set_parser.add_argument('--value', required=True, help='配置值')
    
    # 切換API模式
    switch_parser = subparsers.add_parser('switch-api', help='切換API模式')
    switch_parser.add_argument('--mode', required=True, choices=['mock', 'real', 'hybrid'], help='API模式')
    switch_parser.add_argument('--provider', choices=['claude', 'gemini', 'openai', 'manus', 'all'], 
                              default='all', help='API提供商')
    
    # 管理API密鑰
    keys_parser = subparsers.add_parser('manage-keys', help='管理API密鑰')
    keys_parser.add_argument('--action', required=True, choices=['add', 'update', 'delete', 'list'], help='操作')
    keys_parser.add_argument('--provider', choices=['claude', 'gemini', 'openai', 'manus'], help='API提供商')
    keys_parser.add_argument('--key', help='API密鑰')
    
    # 測試API連接
    test_parser = subparsers.add_parser('test-api', help='測試API連接')
    test_parser.add_argument('--provider', required=True, choices=['claude', 'gemini', 'openai', 'manus'], 
                            help='API提供商')
    test_parser.add_argument('--test-type', choices=['basic', 'full'], default='basic', help='測試類型')
    
    # 導出配置
    export_parser = subparsers.add_parser('export', help='導出配置')
    export_parser.add_argument('--type', choices=['api_config', 'api_keys', 'intent_understanding', 'workflow_engine', 'system_settings', 'all'],
                              default='all', help='配置類型')
    export_parser.add_argument('--format', choices=['json'], default='json', help='導出格式')
    export_parser.add_argument('--output', help='輸出文件路徑')
    
    # 導入配置
    import_parser = subparsers.add_parser('import', help='導入配置')
    import_parser.add_argument('--type', choices=['api_config', 'api_keys', 'intent_understanding', 'workflow_engine', 'system_settings'],
                              help='配置類型')
    import_parser.add_argument('--file', required=True, help='配置文件路徑')
    import_parser.add_argument('--no-merge', dest='merge', action='store_false', help='不合併，直接覆蓋')
    
    # 重置配置
    reset_parser = subparsers.add_parser('reset', help='重置配置')
    reset_parser.add_argument('--type', required=True,
                             choices=['api_config', 'api_keys', 'intent_understanding', 'workflow_engine', 'system_settings'],
                             help='配置類型')
    reset_parser.add_argument('--confirm', action='store_true', help='確認重置')
    
    # 系統狀態
    status_parser = subparsers.add_parser('status', help='獲取系統狀態')
    
    return parser

def main():
    """主函數"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ConfigCLI()
    
    try:
        result = cli.run_config_command(args)
        cli._print_result(result, args.format)
        
        # 根據結果設置退出碼
        if result.get('status') == 'error':
            return 1
        
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用戶中斷")
        return 1
    except Exception as e:
        logger.error(f"執行失敗: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

