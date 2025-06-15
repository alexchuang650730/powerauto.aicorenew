#!/usr/bin/env python3
"""
修復的統一MCP CLI
使用修復的組件避免初始化問題
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import readline
import cmd

# 添加項目路徑
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# 導入修復的組件
from mcptool.adapters.core.fixed_unified_adapter_registry import get_global_registry
from mcptool.adapters.core.fixed_event_loop_manager import get_loop_manager
from mcptool.adapters.core.serializable_mcp_types import serialize_mcp_data

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixedUnifiedMCPCLI(cmd.Cmd):
    """修復的統一MCP CLI交互式界面"""
    
    intro = '''
🚀 PowerAutomation 修復版統一MCP控制系統 v3.0
===============================================
✨ 修復功能: 解決循環依賴、JSON序列化、事件循環問題
輸入 'help' 查看可用命令
輸入 'quit' 或 'exit' 退出系統
'''
    prompt = '(Fixed-MCP) > '
    
    def __init__(self):
        super().__init__()
        try:
            self.registry = get_global_registry()
            self.loop_manager = get_loop_manager()
            self.current_adapter = None
            logger.info("修復版MCP CLI初始化成功")
        except Exception as e:
            logger.error(f"修復版MCP CLI初始化失敗: {e}")
            self.registry = None
            self.loop_manager = None
    
    def do_list(self, args):
        """列出適配器
        用法: list [category]
        例子: list core
        """
        if not self.registry:
            print("❌ 註冊表未初始化")
            return
            
        args = args.strip()
        category = args if args else None
        
        try:
            adapters = self.registry.list_adapters(category)
            
            if not adapters:
                print("❌ 沒有找到適配器")
                return
            
            print(f"\n📋 適配器列表 {'(分類: ' + category + ')' if category else ''}")
            print("=" * 60)
            
            current_category = None
            for adapter in adapters:
                if adapter['category'] != current_category:
                    current_category = adapter['category']
                    print(f"\n📁 {adapter['category_name']} ({adapter['category']})")
                    print("-" * 40)
                
                status = "✅ 已實例化" if adapter['has_instance'] else "⏳ 未實例化"
                print(f"  🔧 {adapter['id']} - {status}")
                print(f"     註冊時間: {adapter['registered_at']}")
                print()
                
        except Exception as e:
            print(f"❌ 列出適配器失敗: {e}")
    
    def do_categories(self, args):
        """顯示適配器分類統計
        用法: categories
        """
        if not self.registry:
            print("❌ 註冊表未初始化")
            return
            
        try:
            categories = self.registry.get_categories()
            
            print("\n📊 適配器分類統計")
            print("=" * 40)
            
            for cat_id, cat_info in categories.items():
                print(f"📁 {cat_info['name']} ({cat_id})")
                print(f"   適配器數量: {cat_info['count']}")
                print()
                
        except Exception as e:
            print(f"❌ 獲取分類統計失敗: {e}")
    
    def do_status(self, args):
        """顯示系統狀態
        用法: status
        """
        print("\n🔍 系統狀態檢查")
        print("=" * 40)
        
        # 檢查註冊表
        if self.registry:
            print("✅ 註冊表: 正常")
            try:
                adapters = self.registry.list_adapters()
                print(f"   已註冊適配器: {len(adapters)}個")
            except Exception as e:
                print(f"   ⚠️ 註冊表異常: {e}")
        else:
            print("❌ 註冊表: 未初始化")
        
        # 檢查事件循環管理器
        if self.loop_manager:
            print("✅ 事件循環管理器: 正常")
        else:
            print("❌ 事件循環管理器: 未初始化")
        
        # 檢查初始化堆棧
        if self.registry and hasattr(self.registry, 'initialization_stack'):
            stack_size = len(self.registry.initialization_stack)
            if stack_size == 0:
                print("✅ 初始化堆棧: 清空")
            else:
                print(f"⚠️ 初始化堆棧: {stack_size}個項目")
                print(f"   項目: {list(self.registry.initialization_stack)}")
    
    def do_clear_stack(self, args):
        """清理初始化堆棧
        用法: clear_stack
        """
        if not self.registry:
            print("❌ 註冊表未初始化")
            return
        
        try:
            self.registry.clear_initialization_stack()
            print("✅ 初始化堆棧已清理")
        except Exception as e:
            print(f"❌ 清理初始化堆棧失敗: {e}")
    
    def do_test_adapter(self, args):
        """測試適配器
        用法: test_adapter <adapter_id>
        """
        if not args.strip():
            print("❌ 請指定適配器ID")
            return
        
        adapter_id = args.strip()
        
        if not self.registry:
            print("❌ 註冊表未初始化")
            return
        
        try:
            print(f"🔍 測試適配器: {adapter_id}")
            
            # 獲取適配器實例
            instance = self.registry.get_adapter_instance(adapter_id)
            
            if instance:
                print(f"✅ 適配器 {adapter_id} 實例化成功")
                print(f"   類型: {type(instance).__name__}")
                print(f"   模組: {type(instance).__module__}")
            else:
                print(f"❌ 適配器 {adapter_id} 實例化失敗")
                
        except Exception as e:
            print(f"❌ 測試適配器失敗: {e}")
    
    def do_quit(self, args):
        """退出CLI"""
        print("👋 再見！")
        return True
    
    def do_exit(self, args):
        """退出CLI"""
        return self.do_quit(args)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="修復版PowerAutomation統一MCP CLI")
    parser.add_argument("--interactive", action="store_true", help="進入交互模式")
    parser.add_argument("--list", action="store_true", help="列出所有適配器")
    parser.add_argument("--status", action="store_true", help="顯示系統狀態")
    
    args = parser.parse_args()
    
    if args.list:
        cli = FixedUnifiedMCPCLI()
        cli.do_list("")
    elif args.status:
        cli = FixedUnifiedMCPCLI()
        cli.do_status("")
    elif args.interactive:
        cli = FixedUnifiedMCPCLI()
        cli.cmdloop()
    else:
        # 默認進入交互模式
        cli = FixedUnifiedMCPCLI()
        cli.cmdloop()

if __name__ == "__main__":
    main()

