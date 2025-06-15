#!/usr/bin/env python3
"""
MCP核心載入器
負責統一載入和管理所有MCP適配器
"""

import os
import sys
import logging
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from enum import Enum

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)

class MCPStatus(Enum):
    """MCP狀態枚舉"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class MCPInfo:
    """MCP信息數據結構"""
    name: str
    module_path: str
    class_name: str
    description: str
    version: str
    dependencies: List[str]
    status: MCPStatus
    instance: Optional[Any] = None
    error_message: Optional[str] = None

class MCPCoreLoader:
    """MCP核心載入器"""
    
    def __init__(self, adapters_root: str = None):
        """初始化MCP核心載入器"""
        if adapters_root is None:
            adapters_root = str(Path(__file__).parent.parent / "adapters")
        
        self.adapters_root = adapters_root
        self.loaded_mcps: Dict[str, MCPInfo] = {}
        self.mcp_registry: Dict[str, Type] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # 配置日誌
        logging.basicConfig(level=logging.INFO)
        logger.info(f"MCP核心載入器初始化，適配器根目錄: {adapters_root}")
    
    def discover_mcps(self) -> List[MCPInfo]:
        """發現所有MCP適配器"""
        mcps = []
        adapters_path = Path(self.adapters_root)
        
        if not adapters_path.exists():
            logger.warning(f"適配器目錄不存在: {adapters_path}")
            return mcps
        
        # 遍歷所有Python文件
        for py_file in adapters_path.rglob("*.py"):
            if py_file.name.startswith("__") or py_file.name in ["base_mcp.py"]:
                continue
            
            try:
                mcp_info = self._analyze_mcp_file(py_file)
                if mcp_info:
                    mcps.append(mcp_info)
            except Exception as e:
                logger.warning(f"分析MCP文件失敗 {py_file}: {e}")
        
        logger.info(f"發現 {len(mcps)} 個MCP適配器")
        return mcps
    
    def _analyze_mcp_file(self, py_file: Path) -> Optional[MCPInfo]:
        """分析MCP文件"""
        try:
            # 計算模塊路徑 - 修復路徑問題
            adapters_parent = Path(self.adapters_root).parent
            relative_path = py_file.relative_to(adapters_parent)
            module_path = str(relative_path.with_suffix("")).replace(os.sep, ".")
            
            # 讀取文件內容分析
            content = py_file.read_text(encoding='utf-8')
            
            # 查找MCP類
            class_name = self._extract_mcp_class(content)
            if not class_name:
                return None
            
            # 提取描述和版本
            description = self._extract_description(content)
            version = self._extract_version(content)
            dependencies = self._extract_dependencies(content)
            
            return MCPInfo(
                name=py_file.stem,
                module_path=module_path,
                class_name=class_name,
                description=description,
                version=version,
                dependencies=dependencies,
                status=MCPStatus.UNLOADED
            )
        
        except Exception as e:
            logger.error(f"分析MCP文件失敗 {py_file}: {e}")
            return None
    
    def _extract_mcp_class(self, content: str) -> Optional[str]:
        """提取MCP類名"""
        import re
        
        # 查找繼承自BaseMCP的類
        pattern = r'class\s+(\w+)\s*\([^)]*BaseMCP[^)]*\):'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        
        # 查找包含MCP的類名
        pattern = r'class\s+(\w*MCP\w*)\s*\([^)]*\):'
        match = re.search(pattern, content)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_description(self, content: str) -> str:
        """提取描述"""
        import re
        
        # 查找文檔字符串
        pattern = r'"""([^"]+)"""'
        match = re.search(pattern, content)
        if match:
            desc = match.group(1).strip()
            # 取第一行作為描述
            return desc.split('\n')[0]
        
        return "無描述"
    
    def _extract_version(self, content: str) -> str:
        """提取版本"""
        import re
        
        pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return "1.0.0"
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """提取依賴"""
        dependencies = []
        
        # 分析import語句
        import re
        imports = re.findall(r'from\s+([^\s]+)\s+import|import\s+([^\s,]+)', content)
        
        for imp in imports:
            module = imp[0] or imp[1]
            if module and not module.startswith('.') and module not in ['os', 'sys', 'logging', 'typing']:
                dependencies.append(module)
        
        return list(set(dependencies))
    
    def load_mcp(self, mcp_name: str) -> bool:
        """載入指定MCP"""
        if mcp_name in self.loaded_mcps:
            mcp_info = self.loaded_mcps[mcp_name]
            if mcp_info.status == MCPStatus.LOADED:
                return True
        
        # 發現MCP
        mcps = self.discover_mcps()
        mcp_info = next((m for m in mcps if m.name == mcp_name), None)
        
        if not mcp_info:
            logger.error(f"未找到MCP: {mcp_name}")
            return False
        
        return self._load_mcp_instance(mcp_info)
    
    def _load_mcp_instance(self, mcp_info: MCPInfo) -> bool:
        """載入MCP實例"""
        try:
            mcp_info.status = MCPStatus.LOADING
            
            # 動態導入模塊
            module = importlib.import_module(mcp_info.module_path)
            
            # 獲取MCP類
            mcp_class = getattr(module, mcp_info.class_name)
            
            # 創建實例
            mcp_instance = mcp_class()
            
            # 更新信息
            mcp_info.instance = mcp_instance
            mcp_info.status = MCPStatus.LOADED
            self.loaded_mcps[mcp_info.name] = mcp_info
            self.mcp_registry[mcp_info.name] = mcp_class
            
            logger.info(f"MCP載入成功: {mcp_info.name}")
            return True
        
        except Exception as e:
            mcp_info.status = MCPStatus.ERROR
            mcp_info.error_message = str(e)
            logger.error(f"MCP載入失敗 {mcp_info.name}: {e}")
            return False
    
    def load_all_mcps(self) -> Dict[str, bool]:
        """載入所有MCP"""
        results = {}
        mcps = self.discover_mcps()
        
        # 按依賴順序載入
        loaded_order = self._resolve_dependencies(mcps)
        
        for mcp_info in loaded_order:
            success = self._load_mcp_instance(mcp_info)
            results[mcp_info.name] = success
        
        logger.info(f"MCP載入完成，成功: {sum(results.values())}/{len(results)}")
        return results
    
    def _resolve_dependencies(self, mcps: List[MCPInfo]) -> List[MCPInfo]:
        """解析依賴順序"""
        # 簡單的拓撲排序
        # 這裡先返回原順序，後續可以實現更複雜的依賴解析
        return mcps
    
    def get_mcp_instance(self, mcp_name: str) -> Optional[Any]:
        """獲取MCP實例"""
        if mcp_name in self.loaded_mcps:
            mcp_info = self.loaded_mcps[mcp_name]
            if mcp_info.status == MCPStatus.LOADED:
                return mcp_info.instance
        return None
    
    def get_loaded_mcps(self) -> Dict[str, MCPInfo]:
        """獲取已載入的MCP列表"""
        return {name: info for name, info in self.loaded_mcps.items() 
                if info.status == MCPStatus.LOADED}
    
    def get_mcp_status(self) -> Dict[str, Dict[str, Any]]:
        """獲取MCP狀態報告"""
        status_report = {}
        
        for name, info in self.loaded_mcps.items():
            status_report[name] = {
                "status": info.status.value,
                "description": info.description,
                "version": info.version,
                "dependencies": info.dependencies,
                "error": info.error_message
            }
        
        return status_report
    
    def reload_mcp(self, mcp_name: str) -> bool:
        """重新載入MCP"""
        if mcp_name in self.loaded_mcps:
            # 卸載現有實例
            del self.loaded_mcps[mcp_name]
            if mcp_name in self.mcp_registry:
                del self.mcp_registry[mcp_name]
        
        # 重新載入
        return self.load_mcp(mcp_name)

# 全局載入器實例
_global_loader = None

def get_global_loader() -> MCPCoreLoader:
    """獲取全局MCP載入器"""
    global _global_loader
    if _global_loader is None:
        _global_loader = MCPCoreLoader()
    return _global_loader

def initialize_mcp_system() -> bool:
    """初始化MCP系統"""
    loader = get_global_loader()
    results = loader.load_all_mcps()
    success_count = sum(results.values())
    total_count = len(results)
    
    logger.info(f"MCP系統初始化完成: {success_count}/{total_count} 個適配器載入成功")
    return success_count > 0

if __name__ == "__main__":
    # 測試載入器
    loader = MCPCoreLoader()
    mcps = loader.discover_mcps()
    
    print(f"發現 {len(mcps)} 個MCP適配器:")
    for mcp in mcps:
        print(f"  - {mcp.name}: {mcp.description}")
    
    # 載入所有MCP
    results = loader.load_all_mcps()
    print(f"\n載入結果:")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

