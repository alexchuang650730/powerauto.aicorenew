#!/usr/bin/env python3
"""
增強版統一MCP CLI系統
整合核心載入器，提供完整的MCP管理和測試功能
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from mcptool.core.unified_mcp_manager import get_global_manager, initialize_unified_mcp_system

class EnhancedMCPCLI:
    """增強版MCP CLI系統"""
    
    def __init__(self):
        """初始化CLI系統"""
        self.manager = get_global_manager()
        self.setup_logging()
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def cmd_init(self, args):
        """初始化MCP系統"""
        print("🔄 初始化MCP系統...")
        success = self.manager.initialize()
        
        if success:
            status = self.manager.get_system_status()
            print("✅ MCP系統初始化成功")
            print(f"📊 載入統計: {status['loaded_mcps']}/{status['total_mcps']} 個MCP")
            
            if status['error_mcps'] > 0:
                print(f"⚠️  {status['error_mcps']} 個MCP載入失敗")
                if args.verbose:
                    self._show_errors(status['mcp_details'])
        else:
            print("❌ MCP系統初始化失敗")
            return 1
        
        return 0
    
    def cmd_status(self, args):
        """顯示系統狀態"""
        if not self.manager.initialized:
            print("⚠️  MCP系統未初始化，正在初始化...")
            self.manager.initialize()
        
        status = self.manager.get_system_status()
        
        print("📊 PowerAutomation MCP系統狀態")
        print("=" * 50)
        print(f"🔧 總MCP數量: {status['total_mcps']}")
        print(f"✅ 已載入: {status['loaded_mcps']}")
        print(f"❌ 載入失敗: {status['error_mcps']}")
        print(f"📋 註冊表適配器: {status['registry_adapters']}")
        print(f"📁 適配器分類: {status['registry_categories']}")
        
        if args.verbose:
            print("\n📋 詳細狀態:")
            for name, info in status['mcp_details'].items():
                status_icon = self._get_status_icon(info['status'])
                print(f"  {status_icon} {name}")
                print(f"    描述: {info['description']}")
                print(f"    版本: {info['version']}")
                if info['error']:
                    print(f"    錯誤: {info['error']}")
        
        return 0
    
    def cmd_list(self, args):
        """列出所有MCP"""
        if not self.manager.initialized:
            self.manager.initialize()
        
        mcps = self.manager.list_mcps()
        
        print(f"📋 MCP適配器列表 (共 {len(mcps)} 個)")
        print("=" * 60)
        
        # 按狀態分組
        loaded = []
        errors = []
        
        for name, info in mcps.items():
            if info['status'] == 'loaded':
                loaded.append((name, info))
            else:
                errors.append((name, info))
        
        # 顯示已載入的MCP
        if loaded:
            print(f"\n✅ 已載入 ({len(loaded)} 個):")
            for name, info in loaded:
                print(f"  🔧 {name}")
                print(f"     {info['description']}")
                if args.verbose:
                    print(f"     版本: {info['version']}")
                    if info['dependencies']:
                        print(f"     依賴: {', '.join(info['dependencies'])}")
        
        # 顯示載入失敗的MCP
        if errors:
            print(f"\n❌ 載入失敗 ({len(errors)} 個):")
            for name, info in errors:
                print(f"  ⚠️  {name}: {info['error']}")
        
        return 0
    
    def cmd_info(self, args):
        """顯示MCP詳細信息"""
        if not self.manager.initialized:
            self.manager.initialize()
        
        mcp_name = args.mcp_name
        mcps = self.manager.list_mcps()
        
        if mcp_name not in mcps:
            print(f"❌ 未找到MCP: {mcp_name}")
            return 1
        
        info = mcps[mcp_name]
        instance = self.manager.get_mcp_instance(mcp_name)
        
        print(f"📋 MCP詳細信息: {mcp_name}")
        print("=" * 50)
        print(f"📝 描述: {info['description']}")
        print(f"🏷️  版本: {info['version']}")
        print(f"📊 狀態: {self._get_status_icon(info['status'])} {info['status']}")
        
        if info['dependencies']:
            print(f"📦 依賴: {', '.join(info['dependencies'])}")
        
        if info['error']:
            print(f"❌ 錯誤: {info['error']}")
        
        if instance:
            capabilities = self.manager.get_mcp_capabilities(mcp_name)
            print(f"\n🔧 可用方法 ({len(capabilities)} 個):")
            for cap in capabilities:
                print(f"  • {cap}")
        
        return 0
    
    def cmd_exec(self, args):
        """執行MCP方法"""
        if not self.manager.initialized:
            self.manager.initialize()
        
        mcp_name = args.mcp_name
        method = args.method
        
        try:
            # 解析參數
            method_args = []
            method_kwargs = {}
            
            if args.args:
                for arg in args.args:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        # 嘗試解析JSON
                        try:
                            value = json.loads(value)
                        except:
                            pass
                        method_kwargs[key] = value
                    else:
                        # 嘗試解析JSON
                        try:
                            arg = json.loads(arg)
                        except:
                            pass
                        method_args.append(arg)
            
            print(f"🔄 執行 {mcp_name}.{method}...")
            result = self.manager.execute_mcp(mcp_name, method, *method_args, **method_kwargs)
            
            print("✅ 執行成功")
            if result is not None:
                print("📊 結果:")
                if isinstance(result, (dict, list)):
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                else:
                    print(result)
            
            return 0
            
        except Exception as e:
            print(f"❌ 執行失敗: {e}")
            return 1
    
    def cmd_test(self, args):
        """運行MCP測試"""
        if not self.manager.initialized:
            self.manager.initialize()
        
        test_type = args.test_type
        
        print(f"🧪 運行 {test_type} 測試...")
        
        if test_type == "basic":
            return self._run_basic_tests()
        elif test_type == "capabilities":
            return self._run_capability_tests()
        elif test_type == "integration":
            return self._run_integration_tests()
        elif test_type == "all":
            results = []
            results.append(self._run_basic_tests())
            results.append(self._run_capability_tests())
            results.append(self._run_integration_tests())
            return max(results)
        else:
            print(f"❌ 未知測試類型: {test_type}")
            return 1
    
    def _run_basic_tests(self) -> int:
        """運行基礎測試"""
        print("\n🔧 基礎功能測試")
        print("-" * 30)
        
        loaded_mcps = self.manager.core_loader.get_loaded_mcps()
        passed = 0
        total = len(loaded_mcps)
        
        for name, mcp_info in loaded_mcps.items():
            try:
                instance = mcp_info.instance
                if instance and hasattr(instance, 'get_capabilities'):
                    capabilities = instance.get_capabilities()
                    print(f"  ✅ {name}: {len(capabilities)} 個能力")
                    passed += 1
                else:
                    print(f"  ⚠️  {name}: 無標準接口")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
        
        print(f"\n📊 基礎測試結果: {passed}/{total} 通過")
        return 0 if passed == total else 1
    
    def _run_capability_tests(self) -> int:
        """運行能力測試"""
        print("\n🎯 能力測試")
        print("-" * 30)
        
        # 測試核心能力
        tests = [
            ("系統初始化", lambda: self.manager.initialized),
            ("MCP發現", lambda: len(self.manager.list_mcps()) > 0),
            ("實例獲取", lambda: any(self.manager.get_mcp_instance(name) 
                                   for name in self.manager.list_mcps())),
        ]
        
        passed = 0
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    print(f"  ✅ {test_name}")
                    passed += 1
                else:
                    print(f"  ❌ {test_name}")
            except Exception as e:
                print(f"  ❌ {test_name}: {e}")
        
        print(f"\n📊 能力測試結果: {passed}/{len(tests)} 通過")
        return 0 if passed == len(tests) else 1
    
    def _run_integration_tests(self) -> int:
        """運行集成測試"""
        print("\n🔗 集成測試")
        print("-" * 30)
        
        # 測試MCP間協作
        loaded_mcps = list(self.manager.core_loader.get_loaded_mcps().keys())
        
        if len(loaded_mcps) < 2:
            print("  ⚠️  需要至少2個MCP進行集成測試")
            return 1
        
        # 簡單的集成測試
        passed = 0
        total = min(3, len(loaded_mcps))  # 最多測試3個
        
        for i, mcp_name in enumerate(loaded_mcps[:total]):
            try:
                capabilities = self.manager.get_mcp_capabilities(mcp_name)
                if capabilities:
                    print(f"  ✅ {mcp_name}: 集成正常")
                    passed += 1
                else:
                    print(f"  ❌ {mcp_name}: 無可用能力")
            except Exception as e:
                print(f"  ❌ {mcp_name}: {e}")
        
        print(f"\n📊 集成測試結果: {passed}/{total} 通過")
        return 0 if passed == total else 1
    
    def _get_status_icon(self, status: str) -> str:
        """獲取狀態圖標"""
        icons = {
            "loaded": "✅",
            "loading": "🔄",
            "error": "❌",
            "unloaded": "⚪",
            "disabled": "🚫"
        }
        return icons.get(status, "❓")
    
    def _show_errors(self, mcp_details: Dict[str, Any]):
        """顯示錯誤詳情"""
        print("\n❌ 載入錯誤詳情:")
        for name, info in mcp_details.items():
            if info['error']:
                print(f"  • {name}: {info['error']}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="PowerAutomation MCP CLI系統")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細輸出")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init命令
    init_parser = subparsers.add_parser("init", help="初始化MCP系統")
    
    # status命令
    status_parser = subparsers.add_parser("status", help="顯示系統狀態")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出所有MCP")
    
    # info命令
    info_parser = subparsers.add_parser("info", help="顯示MCP詳細信息")
    info_parser.add_argument("mcp_name", help="MCP名稱")
    
    # exec命令
    exec_parser = subparsers.add_parser("exec", help="執行MCP方法")
    exec_parser.add_argument("mcp_name", help="MCP名稱")
    exec_parser.add_argument("method", help="方法名稱")
    exec_parser.add_argument("args", nargs="*", help="方法參數")
    
    # test命令
    test_parser = subparsers.add_parser("test", help="運行測試")
    test_parser.add_argument("test_type", choices=["basic", "capabilities", "integration", "all"], 
                           help="測試類型")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = EnhancedMCPCLI()
    
    # 執行命令
    command_map = {
        "init": cli.cmd_init,
        "status": cli.cmd_status,
        "list": cli.cmd_list,
        "info": cli.cmd_info,
        "exec": cli.cmd_exec,
        "test": cli.cmd_test,
    }
    
    if args.command in command_map:
        return command_map[args.command](args)
    else:
        print(f"❌ 未知命令: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

