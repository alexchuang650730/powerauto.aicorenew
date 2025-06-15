#!/usr/bin/env python3
"""
修復版的統一MCP CLI
使用安全的MCP註冊表，避免循環依賴問題
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

class SafeUnifiedMCPCLI:
    """安全的統一MCP CLI"""
    
    def __init__(self):
        self.registry = None
        self.available_adapters = {}
        self.test_results = {}
        
        # 初始化註冊表
        self._init_registry()
    
    def _init_registry(self):
        """初始化MCP註冊表"""
        try:
            from mcptool.adapters.core.safe_mcp_registry import get_registry
            self.registry = get_registry()
            
            # 獲取可用適配器列表
            self.available_adapters = {name: True for name in self.registry.list_adapters()}
            
            logger.info("安全MCP CLI初始化成功")
            
        except Exception as e:
            logger.error(f"MCP註冊表初始化失敗: {e}")
            raise
    
    def list_adapters(self):
        """列出所有可用的適配器"""
        print("\\n=== 可用的MCP適配器 ===")
        
        if not self.available_adapters:
            print("沒有可用的適配器")
            return
        
        for adapter_id, info in self.available_adapters.items():
            status_icon = "✅" if info["status"] == "registered" else "❌" if info["status"] == "failed" else "⚠️"
            print(f"{status_icon} {adapter_id}: {info['name']} ({info['category']}) - {info['status']}")
        
        # 顯示統計信息
        stats = self.registry.get_adapter_stats()
        print(f"\\n統計: {stats['registered_adapters']}/{stats['total_core_adapters']} 適配器可用")
        
        if stats['failed_adapters'] > 0:
            print(f"失敗的適配器: {', '.join(stats['failed_adapter_list'])}")
    
    def test_adapter(self, adapter_id: str):
        """測試單個適配器"""
        print(f"\\n=== 測試適配器: {adapter_id} ===")
        
        if adapter_id not in self.available_adapters:
            print(f"❌ 適配器不存在: {adapter_id}")
            return False
        
        try:
            # 測試適配器
            success = self.registry.test_adapter(adapter_id)
            
            if success:
                print(f"✅ 適配器測試成功: {adapter_id}")
                self.test_results[adapter_id] = "success"
                return True
            else:
                print(f"❌ 適配器測試失敗: {adapter_id}")
                self.test_results[adapter_id] = "failed"
                return False
                
        except Exception as e:
            print(f"❌ 適配器測試異常 {adapter_id}: {e}")
            self.test_results[adapter_id] = f"error: {e}"
            return False
    
    def test_all_adapters(self):
        """測試所有適配器"""
        print("\\n=== 測試所有適配器 ===")
        
        success_count = 0
        total_count = len(self.available_adapters)
        
        for adapter_id in self.available_adapters:
            if self.test_adapter(adapter_id):
                success_count += 1
        
        print(f"\\n測試完成: {success_count}/{total_count} 適配器通過測試")
        
        return success_count, total_count
    
    def run_gaia_test(self, level: int = 1, max_tasks: int = 10):
        """運行GAIA測試"""
        print(f"\\n=== 運行GAIA Level {level} 測試 (最多 {max_tasks} 個問題) ===")
        
        try:
            # 檢查必要的適配器是否可用
            required_adapters = ["gemini", "claude"]
            available_required = []
            
            for adapter_id in required_adapters:
                if adapter_id in self.available_adapters and self.available_adapters[adapter_id]["status"] == "registered":
                    available_required.append(adapter_id)
            
            if not available_required:
                print("❌ 沒有可用的AI適配器，無法運行GAIA測試")
                return
            
            print(f"✅ 可用的AI適配器: {', '.join(available_required)}")
            
            # 創建GAIA測試器
            from mcptool.cli.gaia_tester import GAIATester
            
            tester = GAIATester(
                registry=self.registry,
                available_adapters=available_required
            )
            
            # 運行測試
            results = tester.run_test(level=level, max_tasks=max_tasks)
            
            # 顯示結果
            self._display_gaia_results(results)
            
        except Exception as e:
            logger.error(f"GAIA測試失敗: {e}")
            print(f"❌ GAIA測試失敗: {e}")
    
    def _display_gaia_results(self, results: Dict[str, Any]):
        """顯示GAIA測試結果"""
        print("\\n=== GAIA測試結果 ===")
        
        if "accuracy" in results:
            accuracy = results["accuracy"] * 100
            print(f"準確率: {accuracy:.1f}%")
        
        if "total_questions" in results:
            print(f"總問題數: {results['total_questions']}")
        
        if "correct_answers" in results:
            print(f"正確答案: {results['correct_answers']}")
        
        if "processing_time" in results:
            print(f"處理時間: {results['processing_time']:.2f}秒")
        
        if "adapter_usage" in results:
            print("\\n適配器使用統計:")
            for adapter, count in results["adapter_usage"].items():
                print(f"  {adapter}: {count}次")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="安全的統一MCP CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list命令
    list_parser = subparsers.add_parser("list", help="列出所有適配器")
    
    # test命令
    test_parser = subparsers.add_parser("test", help="測試適配器")
    test_parser.add_argument("adapter", nargs="?", help="要測試的適配器ID (留空測試所有)")
    
    # gaia命令
    gaia_parser = subparsers.add_parser("gaia", help="運行GAIA測試")
    gaia_parser.add_argument("--level", type=int, default=1, choices=[1, 2, 3], help="GAIA測試級別")
    gaia_parser.add_argument("--max-tasks", type=int, default=10, help="最大測試任務數")
    
    args = parser.parse_args()
    
    try:
        # 創建CLI實例
        cli = SafeUnifiedMCPCLI()
        
        if args.command == "list":
            cli.list_adapters()
        
        elif args.command == "test":
            if args.adapter:
                cli.test_adapter(args.adapter)
            else:
                cli.test_all_adapters()
        
        elif args.command == "gaia":
            cli.run_gaia_test(level=args.level, max_tasks=args.max_tasks)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\\n用戶中斷操作")
    except Exception as e:
        logger.error(f"CLI執行失敗: {e}")
        print(f"❌ 執行失敗: {e}")

if __name__ == "__main__":
    main()

