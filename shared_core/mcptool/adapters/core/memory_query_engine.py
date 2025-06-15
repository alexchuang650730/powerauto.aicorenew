#!/usr/bin/env python3
"""
記憶查詢引擎 (Memory Query Engine)
PowerAutomation 記憶系統的統一查詢接口

提供跨GitHub、SuperMemory、RAG的統一記憶查詢功能
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import subprocess

# 導入其他記憶模塊
import sys
sys.path.append('memory-system/memory-storage')
sys.path.append('memory-system/rag-integration')

try:
    from memory_storage import MemoryStorage, StoredMemory
    from rag_integration import RAGIntegration
except ImportError:
    print("⚠️ 無法導入記憶模塊，某些功能可能不可用")

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """數據來源"""
    GITHUB = ("📁", "GitHub", "代碼版本控制和協作數據")
    SUPERMEMORY = ("🧠", "SuperMemory", "長期記憶和上下文數據")
    RAG = ("🔍", "RAG", "向量化語義檢索數據")
    LOCAL_MEMORY = ("💾", "LocalMemory", "本地記憶存儲數據")
    
    def __init__(self, emoji, display_name, description):
        self.emoji = emoji
        self.display_name = display_name
        self.description = description

@dataclass
class QueryResult:
    """查詢結果"""
    id: str
    content: str
    source: DataSource
    relevance_score: float
    metadata: Dict[str, Any]
    created_at: str
    importance_level: str
    memory_type: str

class MemoryQueryEngine:
    """記憶查詢引擎"""
    
    def __init__(self):
        # 初始化各個數據源
        self.memory_storage = None
        self.rag_integration = None
        self.github_data_path = "data/github"
        self.supermemory_data_path = "data/backup/supermemory_workspaces"
        
        self._init_data_sources()
        
    def _init_data_sources(self):
        """初始化數據源"""
        try:
            # 初始化本地記憶存儲
            self.memory_storage = MemoryStorage()
            logger.info("✅ 本地記憶存儲已初始化")
        except Exception as e:
            logger.warning(f"本地記憶存儲初始化失敗: {e}")
            
        try:
            # 初始化RAG整合
            self.rag_integration = RAGIntegration()
            logger.info("✅ RAG整合已初始化")
        except Exception as e:
            logger.warning(f"RAG整合初始化失敗: {e}")
            
    def unified_search(self, 
                      query: str,
                      sources: List[DataSource] = None,
                      memory_type: str = None,
                      importance_level: str = None,
                      time_range_hours: int = None,
                      limit: int = 20) -> List[QueryResult]:
        """統一搜索接口"""
        
        if sources is None:
            sources = list(DataSource)
            
        all_results = []
        
        # 搜索各個數據源
        for source in sources:
            try:
                if source == DataSource.LOCAL_MEMORY:
                    results = self._search_local_memory(query, memory_type, importance_level, time_range_hours)
                elif source == DataSource.RAG:
                    results = self._search_rag(query)
                elif source == DataSource.GITHUB:
                    results = self._search_github(query)
                elif source == DataSource.SUPERMEMORY:
                    results = self._search_supermemory(query)
                else:
                    continue
                    
                all_results.extend(results)
                
            except Exception as e:
                logger.error(f"搜索 {source.display_name} 失敗: {e}")
                
        # 按相關性排序並限制結果數量
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_results[:limit]
        
    def _search_local_memory(self, query: str, memory_type: str = None, 
                           importance_level: str = None, time_range_hours: int = None) -> List[QueryResult]:
        """搜索本地記憶存儲"""
        if not self.memory_storage:
            return []
            
        try:
            # 構建搜索參數
            search_params = {
                'query': query,
                'memory_type': memory_type,
                'limit': 50
            }
            
            if importance_level:
                # 根據重要性級別設置分數範圍
                importance_ranges = {
                    'Critical': (9, 10),
                    'Important': (6, 8),
                    'Normal': (3, 5),
                    'Low': (1, 2)
                }
                if importance_level in importance_ranges:
                    min_score, max_score = importance_ranges[importance_level]
                    search_params['min_importance'] = min_score
                    search_params['max_importance'] = max_score
                    
            memories = self.memory_storage.search_memories(**search_params)
            
            results = []
            for memory in memories:
                # 計算相關性分數（簡單的關鍵詞匹配）
                relevance = self._calculate_text_relevance(query, memory.content)
                
                result = QueryResult(
                    id=memory.id,
                    content=memory.content,
                    source=DataSource.LOCAL_MEMORY,
                    relevance_score=relevance,
                    metadata={
                        'tags': memory.tags,
                        'session_id': memory.session_id,
                        'access_count': memory.access_count
                    },
                    created_at=memory.created_at,
                    importance_level=memory.importance_level,
                    memory_type=memory.memory_type
                )
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"搜索本地記憶失敗: {e}")
            return []
            
    def _search_rag(self, query: str) -> List[QueryResult]:
        """搜索RAG向量數據庫"""
        if not self.rag_integration:
            return []
            
        try:
            # 語義搜索
            semantic_results = self.rag_integration.semantic_search(query, top_k=10, threshold=0.3)
            
            results = []
            for memory_id, similarity_score in semantic_results:
                # 獲取向量化記憶的詳細信息
                if memory_id in self.rag_integration.vectors_db:
                    vectorized_memory = self.rag_integration.vectors_db[memory_id]
                    
                    result = QueryResult(
                        id=memory_id,
                        content=vectorized_memory.content,
                        source=DataSource.RAG,
                        relevance_score=similarity_score,
                        metadata=vectorized_memory.metadata,
                        created_at=vectorized_memory.created_at,
                        importance_level="Unknown",
                        memory_type="semantic_vector"
                    )
                    results.append(result)
                    
            return results
            
        except Exception as e:
            logger.error(f"搜索RAG失敗: {e}")
            return []
            
    def _search_github(self, query: str) -> List[QueryResult]:
        """搜索GitHub數據"""
        try:
            results = []
            
            # 搜索Git提交記錄
            try:
                git_results = subprocess.run([
                    'git', 'log', '--grep', query, '--oneline', '-10'
                ], capture_output=True, text=True, cwd='.')
                
                if git_results.returncode == 0:
                    for line in git_results.stdout.strip().split('\n'):
                        if line.strip():
                            commit_hash = line.split()[0]
                            commit_msg = ' '.join(line.split()[1:])
                            
                            relevance = self._calculate_text_relevance(query, commit_msg)
                            
                            result = QueryResult(
                                id=f"git_{commit_hash}",
                                content=f"Commit: {commit_msg}",
                                source=DataSource.GITHUB,
                                relevance_score=relevance,
                                metadata={'commit_hash': commit_hash, 'type': 'commit'},
                                created_at=datetime.now().isoformat(),
                                importance_level="Normal",
                                memory_type="git_commit"
                            )
                            results.append(result)
                            
            except Exception as e:
                logger.warning(f"搜索Git提交失敗: {e}")
                
            # 搜索項目文件中的內容
            try:
                grep_results = subprocess.run([
                    'grep', '-r', '-i', '--include=*.py', '--include=*.md', 
                    '--include=*.json', query, '.'
                ], capture_output=True, text=True)
                
                if grep_results.returncode == 0:
                    for line in grep_results.stdout.strip().split('\n')[:5]:  # 限制結果數量
                        if ':' in line:
                            file_path, content = line.split(':', 1)
                            
                            relevance = self._calculate_text_relevance(query, content)
                            
                            result = QueryResult(
                                id=f"file_{hash(file_path + content)}",
                                content=f"File: {file_path}\nContent: {content.strip()}",
                                source=DataSource.GITHUB,
                                relevance_score=relevance,
                                metadata={'file_path': file_path, 'type': 'file_content'},
                                created_at=datetime.now().isoformat(),
                                importance_level="Normal",
                                memory_type="file_content"
                            )
                            results.append(result)
                            
            except Exception as e:
                logger.warning(f"搜索文件內容失敗: {e}")
                
            return results
            
        except Exception as e:
            logger.error(f"搜索GitHub失敗: {e}")
            return []
            
    def _search_supermemory(self, query: str) -> List[QueryResult]:
        """搜索SuperMemory數據"""
        try:
            results = []
            
            # 搜索SuperMemory工作區文件
            if os.path.exists(self.supermemory_data_path):
                for root, dirs, files in os.walk(self.supermemory_data_path):
                    for file in files:
                        if file.endswith(('.json', '.txt', '.md')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    
                                if query.lower() in content.lower():
                                    relevance = self._calculate_text_relevance(query, content)
                                    
                                    result = QueryResult(
                                        id=f"supermemory_{hash(file_path)}",
                                        content=f"SuperMemory: {file}\nContent: {content[:200]}...",
                                        source=DataSource.SUPERMEMORY,
                                        relevance_score=relevance,
                                        metadata={'file_path': file_path, 'type': 'supermemory_file'},
                                        created_at=datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                                        importance_level="Normal",
                                        memory_type="supermemory_data"
                                    )
                                    results.append(result)
                                    
                            except Exception as e:
                                logger.warning(f"讀取SuperMemory文件失敗 {file_path}: {e}")
                                
            return results
            
        except Exception as e:
            logger.error(f"搜索SuperMemory失敗: {e}")
            return []
            
    def _calculate_text_relevance(self, query: str, text: str) -> float:
        """計算文本相關性分數"""
        try:
            query_lower = query.lower()
            text_lower = text.lower()
            
            # 簡單的關鍵詞匹配評分
            query_words = query_lower.split()
            text_words = text_lower.split()
            
            if not query_words:
                return 0.0
                
            matches = 0
            for word in query_words:
                if word in text_lower:
                    matches += 1
                    
            # 基礎相關性分數
            base_score = matches / len(query_words)
            
            # 考慮完整匹配
            if query_lower in text_lower:
                base_score += 0.3
                
            # 考慮詞頻
            total_occurrences = sum(text_lower.count(word) for word in query_words)
            frequency_bonus = min(total_occurrences * 0.1, 0.5)
            
            return min(base_score + frequency_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"計算相關性失敗: {e}")
            return 0.0
            
    def get_data_source_statistics(self) -> Dict[str, Any]:
        """獲取各數據源統計信息"""
        stats = {}
        
        # 本地記憶存儲統計
        if self.memory_storage:
            try:
                local_stats = self.memory_storage.get_statistics()
                stats['local_memory'] = local_stats
            except Exception as e:
                stats['local_memory'] = {'error': str(e)}
                
        # RAG統計
        if self.rag_integration:
            try:
                rag_stats = self.rag_integration.get_statistics()
                stats['rag'] = rag_stats
            except Exception as e:
                stats['rag'] = {'error': str(e)}
                
        # GitHub統計
        try:
            git_commit_count = subprocess.run([
                'git', 'rev-list', '--count', 'HEAD'
            ], capture_output=True, text=True)
            
            if git_commit_count.returncode == 0:
                stats['github'] = {
                    'total_commits': int(git_commit_count.stdout.strip()),
                    'repository_path': os.getcwd()
                }
        except Exception as e:
            stats['github'] = {'error': str(e)}
            
        # SuperMemory統計
        try:
            supermemory_files = 0
            if os.path.exists(self.supermemory_data_path):
                for root, dirs, files in os.walk(self.supermemory_data_path):
                    supermemory_files += len(files)
                    
            stats['supermemory'] = {
                'total_files': supermemory_files,
                'workspace_path': self.supermemory_data_path
            }
        except Exception as e:
            stats['supermemory'] = {'error': str(e)}
            
        return stats
        
    def format_search_results(self, results: List[QueryResult]) -> str:
        """格式化搜索結果"""
        if not results:
            return "🔍 未找到相關記憶"
            
        output = [f"🔍 找到 {len(results)} 條相關記憶:\n"]
        
        for i, result in enumerate(results, 1):
            source_info = f"{result.source.emoji} [{result.source.display_name}]"
            relevance_info = f"相關性: {result.relevance_score:.2f}"
            
            output.append(f"{i}. {source_info} {relevance_info}")
            output.append(f"   {result.content[:100]}...")
            output.append(f"   類型: {result.memory_type} | 重要性: {result.importance_level}")
            output.append(f"   時間: {result.created_at}")
            output.append("")
            
        return "\n".join(output)

# 全局實例
memory_query_engine = MemoryQueryEngine()

# CLI接口函數
def search_memories(query: str, source: str = None, memory_type: str = None, 
                   importance: str = None, hours: int = None, limit: int = 20):
    """CLI搜索接口"""
    
    # 解析數據源
    sources = None
    if source:
        source_map = {
            'github': DataSource.GITHUB,
            'supermemory': DataSource.SUPERMEMORY,
            'rag': DataSource.RAG,
            'local': DataSource.LOCAL_MEMORY
        }
        if source.lower() in source_map:
            sources = [source_map[source.lower()]]
            
    # 執行搜索
    results = memory_query_engine.unified_search(
        query=query,
        sources=sources,
        memory_type=memory_type,
        importance_level=importance,
        time_range_hours=hours,
        limit=limit
    )
    
    return memory_query_engine.format_search_results(results)

def show_data_sources():
    """顯示數據源信息"""
    stats = memory_query_engine.get_data_source_statistics()
    
    output = ["📊 記憶系統數據源統計:\n"]
    
    for source in DataSource:
        output.append(f"{source.emoji} {source.display_name} - {source.description}")
        
        source_key = source.display_name.lower().replace('memory', '_memory')
        if source_key in stats:
            source_stats = stats[source_key]
            if 'error' in source_stats:
                output.append(f"   ❌ 錯誤: {source_stats['error']}")
            else:
                for key, value in source_stats.items():
                    output.append(f"   {key}: {value}")
        output.append("")
        
    return "\n".join(output)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 memory_query_engine.py search <查詢內容>")
        print("  python3 memory_query_engine.py search <查詢內容> --source github")
        print("  python3 memory_query_engine.py search <查詢內容> --type problem_solving")
        print("  python3 memory_query_engine.py search <查詢內容> --importance Critical")
        print("  python3 memory_query_engine.py sources")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        
        # 解析可選參數
        source = None
        memory_type = None
        importance = None
        
        for i in range(3, len(sys.argv), 2):
            if i + 1 < len(sys.argv):
                if sys.argv[i] == "--source":
                    source = sys.argv[i + 1]
                elif sys.argv[i] == "--type":
                    memory_type = sys.argv[i + 1]
                elif sys.argv[i] == "--importance":
                    importance = sys.argv[i + 1]
                    
        result = search_memories(query, source, memory_type, importance)
        print(result)
        
    elif command == "sources":
        result = show_data_sources()
        print(result)
        
    else:
        print("❌ 未知命令")
        sys.exit(1)

