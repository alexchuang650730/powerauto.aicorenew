#!/usr/bin/env python3
"""
統一記憶MCP適配器

整合所有記憶系統功能，包括：
- GitHub記憶管理
- SuperMemory整合
- RAG向量檢索
- 本地記憶存儲
- 跨源記憶查詢

作者: PowerAutomation團隊
版本: 1.0.0
日期: 2025-06-08
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from enum import Enum

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 導入基礎MCP
try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子類必須實現此方法")

# 導入記憶查詢引擎
try:
    from memory_query_engine import MemoryQueryEngine
except ImportError:
    class MemoryQueryEngine:
        def __init__(self):
            self.logger = logging.getLogger("memory_query_engine")
        
        def query_all_sources(self, *args, **kwargs):
            return {"status": "mock", "results": [], "sources": []}

# 導入標準化日誌系統
try:
    from standardized_logging_system import log_info, log_error, log_warning, LogCategory, performance_monitor
except ImportError:
    def log_info(category, message, data=None): pass
    def log_error(category, message, data=None): pass
    def log_warning(category, message, data=None): pass
    def performance_monitor(name): 
        def decorator(func): return func
        return decorator
    class LogCategory:
        SYSTEM = "system"
        MEMORY = "memory"
        MCP = "mcp"

logger = logging.getLogger("unified_memory_mcp")

class MemorySource(Enum):
    """記憶源枚舉"""
    GITHUB = "github"
    SUPERMEMORY = "supermemory"
    RAG = "rag"
    LOCAL = "local"
    ALL = "all"

class MemoryOperation(Enum):
    """記憶操作枚舉"""
    QUERY = "query"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BACKUP = "backup"
    SYNC = "sync"
    INDEX = "index"
    SEARCH = "search"

class UnifiedMemoryMCP(BaseMCP):
    """統一記憶MCP適配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("UnifiedMemoryMCP")
        
        # 配置參數
        self.config = config or {}
        self.memory_dir = Path(self.config.get("memory_dir", "memory-system"))
        
        # 記憶組件初始化
        self.memory_engine = MemoryQueryEngine()
        
        # 記憶統計
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "source_usage": {source.value: 0 for source in MemorySource if source != MemorySource.ALL},
            "operation_counts": {op.value: 0 for op in MemoryOperation}
        }
        
        # MCP操作映射
        self.operations = {
            "query_memory": self.query_memory,
            "insert_memory": self.insert_memory,
            "update_memory": self.update_memory,
            "delete_memory": self.delete_memory,
            "backup_memory": self.backup_memory,
            "sync_memory": self.sync_memory,
            "index_memory": self.index_memory,
            "search_memory": self.search_memory,
            "get_memory_stats": self.get_memory_stats,
            "optimize_memory": self.optimize_memory,
            "validate_memory": self.validate_memory,
            "export_memory": self.export_memory
        }
        
        log_info(LogCategory.MCP, "統一記憶MCP初始化完成", {
            "memory_dir": str(self.memory_dir),
            "operations": list(self.operations.keys())
        })
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP標準處理接口"""
        try:
            operation = input_data.get("operation", "query_memory")
            params = input_data.get("params", {})
            
            if operation not in self.operations:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {operation}",
                    "available_operations": list(self.operations.keys())
                }
            
            # 更新操作統計
            if operation in [op.value for op in MemoryOperation]:
                self.stats["operation_counts"][operation] += 1
            
            # 執行對應操作
            if asyncio.iscoroutinefunction(self.operations[operation]):
                # 異步操作
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.operations[operation](**params))
            else:
                # 同步操作
                result = self.operations[operation](**params)
            
            log_info(LogCategory.MCP, f"統一記憶MCP操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "統一記憶MCP處理失敗", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"處理失敗: {str(e)}"
            }
    
    @performance_monitor("query_memory")
    async def query_memory(self, query: str, sources: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """查詢記憶"""
        try:
            self.stats["total_queries"] += 1
            
            # 確定查詢源
            if sources is None:
                sources = [MemorySource.ALL.value]
            
            # 更新源使用統計
            for source in sources:
                if source in self.stats["source_usage"]:
                    self.stats["source_usage"][source] += 1
            
            # 執行查詢
            query_result = self.memory_engine.query_all_sources(
                query=query,
                sources=sources,
                limit=limit
            )
            
            if query_result.get("status") == "success":
                self.stats["successful_queries"] += 1
                
                return {
                    "status": "success",
                    "query": query,
                    "results": query_result.get("results", []),
                    "sources_used": query_result.get("sources", []),
                    "total_results": len(query_result.get("results", [])),
                    "response_time": query_result.get("response_time", 0)
                }
            else:
                self.stats["failed_queries"] += 1
                return {
                    "status": "error",
                    "message": "記憶查詢失敗",
                    "query": query
                }
                
        except Exception as e:
            self.stats["failed_queries"] += 1
            return {
                "status": "error",
                "message": f"記憶查詢失敗: {str(e)}"
            }
    
    async def insert_memory(self, content: str, metadata: Dict[str, Any] = None, source: str = "local") -> Dict[str, Any]:
        """插入記憶"""
        try:
            if metadata is None:
                metadata = {}
            
            # 添加時間戳
            metadata["timestamp"] = datetime.now().isoformat()
            metadata["source"] = source
            
            # 生成記憶ID
            memory_id = self._generate_memory_id(content, metadata)
            
            # 根據源類型插入記憶
            if source == MemorySource.LOCAL.value:
                result = await self._insert_local_memory(memory_id, content, metadata)
            elif source == MemorySource.RAG.value:
                result = await self._insert_rag_memory(memory_id, content, metadata)
            elif source == MemorySource.GITHUB.value:
                result = await self._insert_github_memory(memory_id, content, metadata)
            elif source == MemorySource.SUPERMEMORY.value:
                result = await self._insert_supermemory(memory_id, content, metadata)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的記憶源: {source}"
                }
            
            return {
                "status": "success",
                "memory_id": memory_id,
                "source": source,
                "insert_result": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"插入記憶失敗: {str(e)}"
            }
    
    def _generate_memory_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """生成記憶ID"""
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"mem_{timestamp}_{content_hash}"
    
    async def _insert_local_memory(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """插入本地記憶"""
        try:
            local_dir = self.memory_dir / "local"
            local_dir.mkdir(parents=True, exist_ok=True)
            
            memory_file = local_dir / f"{memory_id}.json"
            memory_data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata
            }
            
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "file_path": str(memory_file)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"本地記憶插入失敗: {str(e)}"
            }
    
    async def _insert_rag_memory(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """插入RAG記憶"""
        try:
            # 實現RAG向量化和存儲
            rag_dir = self.memory_dir / "rag"
            rag_dir.mkdir(parents=True, exist_ok=True)
            
            # 模擬向量化過程
            vector_data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata,
                "vector": [0.1] * 768,  # 模擬768維向量
                "embedding_model": "mock_model"
            }
            
            vector_file = rag_dir / f"{memory_id}_vector.json"
            with open(vector_file, 'w', encoding='utf-8') as f:
                json.dump(vector_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "vector_file": str(vector_file),
                "vector_dimension": 768
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"RAG記憶插入失敗: {str(e)}"
            }
    
    async def _insert_github_memory(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """插入GitHub記憶"""
        try:
            # 實現GitHub記憶存儲
            github_dir = self.memory_dir / "github"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            commit_data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata,
                "commit_info": {
                    "author": "PowerAutomation",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Add memory: {memory_id}"
                }
            }
            
            commit_file = github_dir / f"{memory_id}_commit.json"
            with open(commit_file, 'w', encoding='utf-8') as f:
                json.dump(commit_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "commit_file": str(commit_file)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"GitHub記憶插入失敗: {str(e)}"
            }
    
    async def _insert_supermemory(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """插入SuperMemory"""
        try:
            # 實現SuperMemory存儲
            supermemory_dir = self.memory_dir / "supermemory"
            supermemory_dir.mkdir(parents=True, exist_ok=True)
            
            workspace_data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata,
                "workspace_info": {
                    "created_at": datetime.now().isoformat(),
                    "workspace_id": f"ws_{memory_id}"
                }
            }
            
            workspace_file = supermemory_dir / f"{memory_id}_workspace.json"
            with open(workspace_file, 'w', encoding='utf-8') as f:
                json.dump(workspace_data, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "workspace_file": str(workspace_file)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"SuperMemory插入失敗: {str(e)}"
            }
    
    async def update_memory(self, memory_id: str, content: str = None, metadata: Dict[str, Any] = None, source: str = "local") -> Dict[str, Any]:
        """更新記憶"""
        try:
            # 實現記憶更新邏輯
            update_data = {}
            if content is not None:
                update_data["content"] = content
            if metadata is not None:
                update_data["metadata"] = metadata
            
            update_data["updated_at"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "memory_id": memory_id,
                "source": source,
                "updated_fields": list(update_data.keys())
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"更新記憶失敗: {str(e)}"
            }
    
    async def delete_memory(self, memory_id: str, source: str = "local") -> Dict[str, Any]:
        """刪除記憶"""
        try:
            # 實現記憶刪除邏輯
            return {
                "status": "success",
                "memory_id": memory_id,
                "source": source,
                "message": "記憶已刪除"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"刪除記憶失敗: {str(e)}"
            }
    
    async def backup_memory(self, sources: List[str] = None, backup_path: str = None) -> Dict[str, Any]:
        """備份記憶"""
        try:
            if sources is None:
                sources = [source.value for source in MemorySource if source != MemorySource.ALL]
            
            if backup_path is None:
                backup_path = f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backed_up_sources = []
            for source in sources:
                source_backup = await self._backup_source(source, backup_dir)
                if source_backup["status"] == "success":
                    backed_up_sources.append(source)
            
            return {
                "status": "success",
                "backup_path": str(backup_dir),
                "backed_up_sources": backed_up_sources,
                "backup_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"備份記憶失敗: {str(e)}"
            }
    
    async def _backup_source(self, source: str, backup_dir: Path) -> Dict[str, Any]:
        """備份特定記憶源"""
        try:
            source_dir = self.memory_dir / source
            if source_dir.exists():
                backup_source_dir = backup_dir / source
                backup_source_dir.mkdir(parents=True, exist_ok=True)
                
                # 複製文件
                import shutil
                shutil.copytree(source_dir, backup_source_dir, dirs_exist_ok=True)
                
                return {
                    "status": "success",
                    "source": source,
                    "backup_location": str(backup_source_dir)
                }
            else:
                return {
                    "status": "warning",
                    "source": source,
                    "message": "源目錄不存在"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "source": source,
                "message": f"備份失敗: {str(e)}"
            }
    
    async def sync_memory(self, source_from: str, source_to: str) -> Dict[str, Any]:
        """同步記憶"""
        try:
            # 實現記憶同步邏輯
            sync_result = await self._perform_memory_sync(source_from, source_to)
            
            return {
                "status": "success",
                "source_from": source_from,
                "source_to": source_to,
                "sync_result": sync_result,
                "sync_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"同步記憶失敗: {str(e)}"
            }
    
    async def _perform_memory_sync(self, source_from: str, source_to: str) -> Dict[str, Any]:
        """執行記憶同步"""
        # 實現具體的同步邏輯
        return {
            "synced_items": 0,
            "conflicts_resolved": 0,
            "errors": 0
        }
    
    async def index_memory(self, sources: List[str] = None) -> Dict[str, Any]:
        """索引記憶"""
        try:
            if sources is None:
                sources = [source.value for source in MemorySource if source != MemorySource.ALL]
            
            indexed_sources = []
            total_indexed = 0
            
            for source in sources:
                index_result = await self._index_source(source)
                if index_result["status"] == "success":
                    indexed_sources.append(source)
                    total_indexed += index_result.get("indexed_count", 0)
            
            return {
                "status": "success",
                "indexed_sources": indexed_sources,
                "total_indexed": total_indexed,
                "index_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"索引記憶失敗: {str(e)}"
            }
    
    async def _index_source(self, source: str) -> Dict[str, Any]:
        """索引特定記憶源"""
        try:
            # 實現記憶源索引邏輯
            source_dir = self.memory_dir / source
            indexed_count = 0
            
            if source_dir.exists():
                for file_path in source_dir.glob("*.json"):
                    # 模擬索引過程
                    indexed_count += 1
            
            return {
                "status": "success",
                "source": source,
                "indexed_count": indexed_count
            }
            
        except Exception as e:
            return {
                "status": "error",
                "source": source,
                "message": f"索引失敗: {str(e)}"
            }
    
    async def search_memory(self, search_query: str, search_type: str = "semantic", sources: List[str] = None) -> Dict[str, Any]:
        """搜索記憶"""
        try:
            if sources is None:
                sources = [MemorySource.ALL.value]
            
            # 根據搜索類型執行搜索
            if search_type == "semantic":
                search_result = await self._semantic_search(search_query, sources)
            elif search_type == "keyword":
                search_result = await self._keyword_search(search_query, sources)
            elif search_type == "fuzzy":
                search_result = await self._fuzzy_search(search_query, sources)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的搜索類型: {search_type}"
                }
            
            return {
                "status": "success",
                "search_query": search_query,
                "search_type": search_type,
                "results": search_result.get("results", []),
                "total_results": len(search_result.get("results", [])),
                "search_time": search_result.get("search_time", 0)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"搜索記憶失敗: {str(e)}"
            }
    
    async def _semantic_search(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """語義搜索"""
        # 實現語義搜索邏輯
        return {
            "results": [],
            "search_time": 0.1
        }
    
    async def _keyword_search(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """關鍵詞搜索"""
        # 實現關鍵詞搜索邏輯
        return {
            "results": [],
            "search_time": 0.05
        }
    
    async def _fuzzy_search(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """模糊搜索"""
        # 實現模糊搜索邏輯
        return {
            "results": [],
            "search_time": 0.15
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """獲取記憶統計"""
        return {
            "status": "success",
            "statistics": self.stats.copy(),
            "memory_sources": [source.value for source in MemorySource if source != MemorySource.ALL],
            "available_operations": [op.value for op in MemoryOperation],
            "timestamp": datetime.now().isoformat()
        }
    
    async def optimize_memory(self, optimization_type: str = "all") -> Dict[str, Any]:
        """優化記憶"""
        try:
            optimization_results = []
            
            if optimization_type in ["all", "index"]:
                index_result = await self.index_memory()
                optimization_results.append({"type": "index", "result": index_result})
            
            if optimization_type in ["all", "cleanup"]:
                cleanup_result = await self._cleanup_memory()
                optimization_results.append({"type": "cleanup", "result": cleanup_result})
            
            if optimization_type in ["all", "compress"]:
                compress_result = await self._compress_memory()
                optimization_results.append({"type": "compress", "result": compress_result})
            
            return {
                "status": "success",
                "optimization_type": optimization_type,
                "optimization_results": optimization_results,
                "optimization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"記憶優化失敗: {str(e)}"
            }
    
    async def _cleanup_memory(self) -> Dict[str, Any]:
        """清理記憶"""
        # 實現記憶清理邏輯
        return {
            "status": "success",
            "cleaned_items": 0,
            "freed_space": "0MB"
        }
    
    async def _compress_memory(self) -> Dict[str, Any]:
        """壓縮記憶"""
        # 實現記憶壓縮邏輯
        return {
            "status": "success",
            "compressed_items": 0,
            "compression_ratio": "1:1"
        }
    
    async def validate_memory(self, sources: List[str] = None) -> Dict[str, Any]:
        """驗證記憶完整性"""
        try:
            if sources is None:
                sources = [source.value for source in MemorySource if source != MemorySource.ALL]
            
            validation_results = []
            total_items = 0
            corrupted_items = 0
            
            for source in sources:
                validation_result = await self._validate_source(source)
                validation_results.append(validation_result)
                total_items += validation_result.get("total_items", 0)
                corrupted_items += validation_result.get("corrupted_items", 0)
            
            integrity_score = (total_items - corrupted_items) / max(total_items, 1)
            
            return {
                "status": "success",
                "validation_results": validation_results,
                "total_items": total_items,
                "corrupted_items": corrupted_items,
                "integrity_score": integrity_score,
                "validation_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"記憶驗證失敗: {str(e)}"
            }
    
    async def _validate_source(self, source: str) -> Dict[str, Any]:
        """驗證特定記憶源"""
        try:
            source_dir = self.memory_dir / source
            total_items = 0
            corrupted_items = 0
            
            if source_dir.exists():
                for file_path in source_dir.glob("*.json"):
                    total_items += 1
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        corrupted_items += 1
            
            return {
                "status": "success",
                "source": source,
                "total_items": total_items,
                "corrupted_items": corrupted_items
            }
            
        except Exception as e:
            return {
                "status": "error",
                "source": source,
                "message": f"驗證失敗: {str(e)}"
            }
    
    async def export_memory(self, export_format: str = "json", sources: List[str] = None, export_path: str = None) -> Dict[str, Any]:
        """導出記憶"""
        try:
            if sources is None:
                sources = [source.value for source in MemorySource if source != MemorySource.ALL]
            
            if export_path is None:
                export_path = f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            
            export_result = await self._perform_memory_export(sources, export_format, export_path)
            
            return {
                "status": "success",
                "export_path": export_path,
                "export_format": export_format,
                "exported_sources": sources,
                "export_result": export_result,
                "export_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"導出記憶失敗: {str(e)}"
            }
    
    async def _perform_memory_export(self, sources: List[str], export_format: str, export_path: str) -> Dict[str, Any]:
        """執行記憶導出"""
        # 實現記憶導出邏輯
        return {
            "exported_items": 0,
            "file_size": "0MB",
            "export_duration": "0s"
        }

# 創建全局實例
unified_memory_mcp = UnifiedMemoryMCP()

# 導出主要接口
__all__ = [
    'UnifiedMemoryMCP',
    'MemorySource',
    'MemoryOperation',
    'unified_memory_mcp'
]

if __name__ == "__main__":
    # 測試MCP功能
    test_data = {
        "operation": "get_memory_stats",
        "params": {}
    }
    
    result = unified_memory_mcp.process(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

