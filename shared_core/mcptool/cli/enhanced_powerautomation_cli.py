#!/usr/bin/env python3
"""
增強的PowerAutomation CLI接口

添加query處理功能，支持GAIA測試
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedPowerAutomationCLI:
    """增強的PowerAutomation CLI"""
    
    def __init__(self):
        self.registry = None
        self.unified_registry = None
        self.available_adapters = {}
        
        # 初始化組件
        self._init_components()
    
    def _init_components(self):
        """初始化所有組件"""
        try:
            # 初始化MCP註冊表
            from mcptool.adapters.core.safe_mcp_registry import CompleteMCPRegistry
            self.registry = CompleteMCPRegistry()
            
            # 初始化統一適配器接口
            from mcptool.core.unified_adapter_interface import UnifiedAdapterRegistry
            self.unified_registry = UnifiedAdapterRegistry(self.registry)
            
            # 獲取可用適配器
            adapter_names = self.unified_registry.list_adapters()
            self.available_adapters = {name: True for name in adapter_names}
            
            logger.info(f"增強CLI初始化成功，{len(adapter_names)}個適配器可用")
            
        except Exception as e:
            logger.error(f"CLI初始化失敗: {e}")
            raise
    
    def list_adapters(self):
        """列出所有可用的適配器"""
        print("\\n=== 可用的MCP適配器 ===")
        
        if not self.available_adapters:
            print("沒有可用的適配器")
            return
        
        adapter_names = self.unified_registry.list_adapters()
        for i, adapter_name in enumerate(adapter_names, 1):
            adapter = self.unified_registry.get_adapter(adapter_name)
            if adapter:
                info = adapter.get_adapter_info()
                print(f"{i:2d}. ✅ {adapter_name}: {info['adapter_type']} ({info['call_method']})")
            else:
                print(f"{i:2d}. ❌ {adapter_name}: 不可用")
        
        print(f"\\n總計: {len(adapter_names)} 個適配器")
    
    def test_adapter(self, adapter_name: str):
        """測試單個適配器"""
        print(f"\\n=== 測試適配器: {adapter_name} ===")
        
        if adapter_name not in self.available_adapters:
            print(f"❌ 適配器不存在: {adapter_name}")
            return False
        
        try:
            adapter = self.unified_registry.get_adapter(adapter_name)
            if not adapter:
                print(f"❌ 無法獲取適配器: {adapter_name}")
                return False
            
            # 測試基本功能
            test_query = "Hello, this is a test."
            print(f"測試查詢: {test_query}")
            
            result = adapter.process(test_query)
            
            if result.get("success"):
                print(f"✅ 適配器測試成功: {adapter_name}")
                print(f"響應: {result.get('data', 'N/A')}")
                return True
            else:
                print(f"❌ 適配器測試失敗: {adapter_name}")
                print(f"錯誤: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ 適配器測試異常 {adapter_name}: {e}")
            return False
    
    def query_adapter(self, adapter_name: str, query: str, format_output: str = "text"):
        """使用指定適配器處理查詢"""
        print(f"\\n=== 查詢適配器: {adapter_name} ===")
        print(f"查詢: {query}")
        
        if adapter_name not in self.available_adapters:
            error_msg = f"適配器不存在: {adapter_name}"
            if format_output == "json":
                print(json.dumps({"success": False, "error": error_msg}, ensure_ascii=False))
            else:
                print(f"❌ {error_msg}")
            return False
        
        try:
            adapter = self.unified_registry.get_adapter(adapter_name)
            if not adapter:
                error_msg = f"無法獲取適配器: {adapter_name}"
                if format_output == "json":
                    print(json.dumps({"success": False, "error": error_msg}, ensure_ascii=False))
                else:
                    print(f"❌ {error_msg}")
                return False
            
            # 處理查詢
            result = adapter.process(query)
            
            if format_output == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                if result.get("success"):
                    print(f"✅ 查詢成功")
                    print(f"響應: {result.get('data', 'N/A')}")
                else:
                    print(f"❌ 查詢失敗")
                    print(f"錯誤: {result.get('error', 'Unknown error')}")
            
            return result.get("success", False)
                
        except Exception as e:
            error_msg = f"查詢處理異常: {e}"
            if format_output == "json":
                print(json.dumps({"success": False, "error": error_msg}, ensure_ascii=False))
            else:
                print(f"❌ {error_msg}")
            return False
    
    def run_gaia_test(self, level: int = 1, max_tasks: int = 10):
        """運行GAIA測試"""
        print(f"\\n=== GAIA Level {level} 測試 ===")
        print(f"最大任務數: {max_tasks}")
        
        try:
            # 使用內置的GAIA測試器
            from mcptool.core.robust_gaia_tester import RobustGAIATester
            
            tester = RobustGAIATester()
            results = tester.run_gaia_test(question_limit=max_tasks)
            
            # 顯示結果
            tester.print_summary(results)
            
            # 保存結果
            result_file = tester.save_results(results)
            if result_file:
                print(f"\\n📄 測試結果已保存: {result_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ GAIA測試失敗: {e}")
            return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="增強的PowerAutomation CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出所有適配器")
    
    # test命令
    test_parser = subparsers.add_parser("test", help="測試適配器")
    test_parser.add_argument("adapter", help="要測試的適配器名稱")
    
    # query命令
    query_parser = subparsers.add_parser("query", help="查詢適配器")
    query_parser.add_argument("adapter", help="要使用的適配器名稱")
    query_parser.add_argument("query", help="查詢內容")
    query_parser.add_argument("--format", choices=["text", "json"], default="text", help="輸出格式")
    
    # gaia命令
    gaia_parser = subparsers.add_parser("gaia", help="運行GAIA測試")
    gaia_parser.add_argument("--level", type=int, default=1, choices=[1, 2, 3], help="GAIA測試級別")
    gaia_parser.add_argument("--max-tasks", type=int, default=10, help="最大測試任務數")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # 創建CLI實例
        cli = EnhancedPowerAutomationCLI()
        
        if args.command == "list":
            cli.list_adapters()
        
        elif args.command == "test":
            cli.test_adapter(args.adapter)
        
        elif args.command == "query":
            cli.query_adapter(args.adapter, args.query, args.format)
        
        elif args.command == "gaia":
            cli.run_gaia_test(args.level, args.max_tasks)
        
        else:
            print(f"❌ 未知命令: {args.command}")
            parser.print_help()
    
    except Exception as e:
        logger.error(f"CLI執行失敗: {e}")
        print(f"❌ 執行失敗: {e}")

if __name__ == "__main__":
    main()

