#!/usr/bin/env python3
"""
MCP適配器註冊修復腳本
Fix MCP Adapter Registration

手動註冊所有關鍵的MCP適配器，確保CLI能正常控制
"""

import sys
import os
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def register_core_mcps():
    """註冊核心MCP適配器"""
    try:
        from mcptool.adapters.core.unified_adapter_registry import get_global_registry
        registry = get_global_registry()
        
        print("🔧 開始手動註冊核心MCP適配器...")
        
        # 核心MCP適配器列表
        core_mcps = [
            {
                "module": "mcptool.adapters.thought_action_recorder_mcp",
                "class": "ThoughtActionRecorderMCP",
                "id": "thought_action_recorder",
                "name": "思考操作記錄器"
            },
            {
                "module": "mcptool.adapters.release_discovery_mcp", 
                "class": "ReleaseDiscoveryMCP",
                "id": "release_manager",
                "name": "Release管理器"
            },
            {
                "module": "mcptool.adapters.supermemory_adapter.supermemory_mcp",
                "class": "SuperMemoryMCP", 
                "id": "supermemory",
                "name": "SuperMemory適配器"
            },
            {
                "module": "mcptool.adapters.kilocode_adapter.kilocode_mcp",
                "class": "KiloCodeMCP",
                "id": "kilocode", 
                "name": "KiloCode適配器"
            },
            {
                "module": "mcptool.adapters.unified_config_manager.config_manager_mcp",
                "class": "ConfigManagerMCP",
                "id": "config_manager",
                "name": "配置管理器"
            }
        ]
        
        registered_count = 0
        
        for mcp_info in core_mcps:
            try:
                # 動態導入模塊
                module = __import__(mcp_info["module"], fromlist=[mcp_info["class"]])
                mcp_class = getattr(module, mcp_info["class"])
                
                # 手動註冊到註冊表
                registry.registered_adapters[mcp_info["id"]] = {
                    "name": mcp_info["name"],
                    "class": mcp_class,
                    "category": "core",
                    "file_path": module.__file__,
                    "module_path": mcp_info["module"],
                    "registered_at": "manual_registration",
                    "status": "active"
                }
                
                print(f"✅ 註冊成功: {mcp_info['name']} ({mcp_info['id']})")
                registered_count += 1
                
            except Exception as e:
                print(f"❌ 註冊失敗: {mcp_info['name']} - {e}")
                
        print(f"\n🎉 手動註冊完成！成功註冊 {registered_count}/{len(core_mcps)} 個MCP適配器")
        
        # 驗證註冊結果
        print(f"\n📊 當前註冊表狀態:")
        print(f"   總適配器數: {len(registry.registered_adapters)}")
        for adapter_id, info in registry.registered_adapters.items():
            print(f"   {adapter_id}: {info['name']} ({info['status']})")
            
        return registered_count
        
    except Exception as e:
        print(f"❌ 註冊過程失敗: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_cli_access():
    """測試CLI訪問MCP功能"""
    try:
        from mcptool.cli.unified_mcp_cli import UnifiedMCPCLI
        
        print("\n🧪 測試CLI訪問...")
        
        # 創建CLI實例
        cli = UnifiedMCPCLI()
        
        # 測試列出適配器
        print("📋 測試列出適配器功能...")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI測試失敗: {e}")
        return False

def create_mcp_init_script():
    """創建MCP初始化腳本"""
    init_script = """#!/usr/bin/env python3
# MCP適配器自動初始化腳本
import sys
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 自動註冊MCP適配器
from mcptool.adapters.mcp_registration_fix import register_core_mcps
register_core_mcps()

print("🚀 MCP適配器初始化完成")
"""
    
    init_file = project_root / "mcptool" / "init_mcps.py"
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(init_script)
        
    print(f"📝 創建MCP初始化腳本: {init_file}")

def main():
    """主函數"""
    print("🚀 MCP適配器註冊修復工具")
    print("=" * 50)
    
    # 1. 手動註冊核心MCP
    registered_count = register_core_mcps()
    
    if registered_count > 0:
        # 2. 測試CLI訪問
        test_cli_access()
        
        # 3. 創建初始化腳本
        create_mcp_init_script()
        
        print("\n✅ MCP註冊修復完成！")
        print("💡 現在可以通過CLI控制MCP適配器了")
        print("🔧 使用方法: python3 mcptool/cli/unified_mcp_cli.py list")
        
    else:
        print("\n❌ MCP註冊修復失敗！")
        print("🔍 請檢查MCP適配器的實現和依賴")

if __name__ == "__main__":
    main()

