#!/usr/bin/env python3
"""
MCP核心適配器CLI命令
為核心適配器提供CLI支持
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from mcptool.adapters.core.unified_adapter_registry import UnifiedAdapterRegistry

logger = logging.getLogger(__name__)

class MCPCoreCLI:
    """MCP核心適配器CLI"""
    
    def __init__(self):
        self.registry = UnifiedAdapterRegistry()
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """創建命令行解析器"""
        parser = argparse.ArgumentParser(description="MCP核心適配器CLI")
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        # 列出所有核心適配器
        list_parser = subparsers.add_parser("list", help="列出所有核心適配器")
        list_parser.add_argument("--category", help="按類別過濾")
        
        # 獲取適配器信息
        info_parser = subparsers.add_parser("info", help="獲取適配器信息")
        info_parser.add_argument("adapter_id", help="適配器ID")
        
        # 執行適配器
        exec_parser = subparsers.add_parser("exec", help="執行適配器")
        exec_parser.add_argument("adapter_id", help="適配器ID")
        exec_parser.add_argument("--input", help="輸入數據 (JSON格式)")
        
        # 註冊表管理
        registry_parser = subparsers.add_parser("registry", help="註冊表管理")
        registry_parser.add_argument("--refresh", action="store_true", help="刷新註冊表")
        registry_parser.add_argument("--stats", action="store_true", help="顯示註冊表統計")
        
        # 配置管理
        config_parser = subparsers.add_parser("config", help="配置管理")
        config_parser.add_argument("--list", action="store_true", help="列出配置")
        config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="設置配置")
        
        # 工具引擎
        tools_parser = subparsers.add_parser("tools", help="工具引擎")
        tools_parser.add_argument("--list", action="store_true", help="列出可用工具")
        tools_parser.add_argument("--create", help="創建新工具")
        
        # 思維行動記錄
        recorder_parser = subparsers.add_parser("recorder", help="思維行動記錄")
        recorder_parser.add_argument("--list", action="store_true", help="列出記錄")
        recorder_parser.add_argument("--clear", action="store_true", help="清除記錄")
        
        # 發現適配器
        discovery_parser = subparsers.add_parser("discovery", help="發現適配器")
        discovery_parser.add_argument("--scan", action="store_true", help="掃描新適配器")
        
        return parser
    
    def run(self, args=None):
        """運行CLI"""
        args = self.parser.parse_args(args)
        
        if not args.command:
            self.parser.print_help()
            return 1
        
        try:
            # 根據命令執行相應的方法
            if args.command == "list":
                self._list_adapters(args.category)
            elif args.command == "info":
                self._show_adapter_info(args.adapter_id)
            elif args.command == "exec":
                self._exec_adapter(args.adapter_id, args.input)
            elif args.command == "registry":
                self._manage_registry(args)
            elif args.command == "config":
                self._manage_config(args)
            elif args.command == "tools":
                self._manage_tools(args)
            elif args.command == "recorder":
                self._manage_recorder(args)
            elif args.command == "discovery":
                self._manage_discovery(args)
            else:
                print(f"未知命令: {args.command}")
                return 1
            
            return 0
        
        except Exception as e:
            print(f"錯誤: {e}")
            return 1
    
    def _list_adapters(self, category=None):
        """列出所有適配器"""
        print("MCP適配器列表:")
        print("-" * 60)
        print(f"{'ID':<30} {'類別':<15} {'狀態':<10}")
        print("-" * 60)
        
        for adapter_id, adapter_info in self.registry.registered_adapters.items():
            adapter_category = adapter_info.get("category", "Unknown")
            
            if category and adapter_category != category:
                continue
            
            status = adapter_info.get("status", "Active")
            print(f"{adapter_id:<30} {adapter_category:<15} {status:<10}")
    
    def _show_adapter_info(self, adapter_id):
        """顯示適配器信息"""
        if adapter_id not in self.registry.registered_adapters:
            print(f"適配器不存在: {adapter_id}")
            return
        
        adapter_info = self.registry.registered_adapters[adapter_id]
        print(f"適配器信息: {adapter_id}")
        print("-" * 60)
        
        for key, value in adapter_info.items():
            if key == "class":
                print(f"類: {value.__name__ if value else 'None'}")
            else:
                print(f"{key}: {value}")
    
    def _exec_adapter(self, adapter_id, input_data=None):
        """執行適配器"""
        if adapter_id not in self.registry.registered_adapters:
            print(f"適配器不存在: {adapter_id}")
            return
        
        adapter_info = self.registry.registered_adapters[adapter_id]
        adapter_class = adapter_info.get("class")
        
        if not adapter_class:
            print(f"適配器類不可用: {adapter_id}")
            return
        
        try:
            # 創建適配器實例
            adapter = adapter_class()
            
            # 準備輸入數據
            input_data = input_data or "{}"
            import json
            data = json.loads(input_data)
            
            # 執行適配器
            result = adapter.process(data)
            
            # 顯示結果
            print("執行結果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        except Exception as e:
            print(f"執行錯誤: {e}")
    
    def _manage_registry(self, args):
        """管理註冊表"""
        if args.refresh:
            print("刷新註冊表...")
            # 重新初始化註冊表
            self.registry = UnifiedAdapterRegistry()
            print(f"註冊表已刷新，共 {len(self.registry.registered_adapters)} 個適配器")
        
        if args.stats:
            print("註冊表統計:")
            categories = {}
            statuses = {}
            
            for adapter_id, adapter_info in self.registry.registered_adapters.items():
                category = adapter_info.get("category", "Unknown")
                status = adapter_info.get("status", "Active")
                
                categories[category] = categories.get(category, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
            
            print(f"總適配器數: {len(self.registry.registered_adapters)}")
            print("\n類別分佈:")
            for category, count in categories.items():
                print(f"- {category}: {count}")
            
            print("\n狀態分佈:")
            for status, count in statuses.items():
                print(f"- {status}: {count}")
    
    def _manage_config(self, args):
        """管理配置"""
        if args.list:
            print("配置列表:")
            # 這裡需要實際的配置管理器
            print("配置管理功能尚未實現")
        
        if args.set:
            key, value = args.set
            print(f"設置配置: {key} = {value}")
            # 這裡需要實際的配置管理器
            print("配置管理功能尚未實現")
    
    def _manage_tools(self, args):
        """管理工具引擎"""
        if args.list:
            print("可用工具列表:")
            # 這裡需要實際的工具引擎
            print("工具引擎功能尚未實現")
        
        if args.create:
            print(f"創建新工具: {args.create}")
            # 這裡需要實際的工具引擎
            print("工具引擎功能尚未實現")
    
    def _manage_recorder(self, args):
        """管理思維行動記錄"""
        if args.list:
            print("思維行動記錄列表:")
            # 這裡需要實際的記錄器
            print("記錄器功能尚未實現")
        
        if args.clear:
            print("清除思維行動記錄")
            # 這裡需要實際的記錄器
            print("記錄器功能尚未實現")
    
    def _manage_discovery(self, args):
        """管理適配器發現"""
        if args.scan:
            print("掃描新適配器...")
            # 這裡需要實際的發現機制
            print("適配器發現功能尚未實現")

def main():
    """主函數"""
    cli = MCPCoreCLI()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main())

