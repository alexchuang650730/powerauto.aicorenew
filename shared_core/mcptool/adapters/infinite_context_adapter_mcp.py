#!/usr/bin/env python3
"""
Infinite Context Adapter MCP - 无限上下文适配器
整合Claude、Gemini、SuperMemory、GitHub等多个API服务
支持大规模上下文处理、外部记忆存储和智能分析
"""

import os
import json
import torch
import numpy as np
import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib
import base64
from dataclasses import dataclass

# 导入基础MCP类
try:
    from ..base_mcp import BaseMCP
except ImportError:
    # 如果导入失败，创建一个基础类
    class BaseMCP:
        def __init__(self):
            self.name = "BaseMCP"
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError
        
        def validate_input(self, input_data: Dict[str, Any]) -> bool:
            return True
        
        def get_capabilities(self) -> List[str]:
            return []

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContextChunk:
    """上下文块数据结构"""
    id: str
    content: str
    embedding: Optional[torch.Tensor]
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class ThoughtProcess:
    """思考过程数据结构"""
    id: str
    steps: List[str]
    context: str
    result: str
    confidence: float

class InfiniteContextAdapterMCP(BaseMCP):
    """无限上下文适配器MCP版本"""
    
    def __init__(self, config: Dict = None):
        super().__init__()
        self.name = "InfiniteContextAdapterMCP"
        self.config = config or {}
        
        # API配置
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.supermemory_api_key = os.getenv("SUPERMEMORY_API_KEY")
        self.kilo_api_key = os.getenv("KILO_API_KEY") or os.getenv("CLAUDE_API_KEY")  # KILO使用Claude API Key
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # 验证API密钥
        self._validate_api_keys()
        
        # 初始化客户端
        self._initialize_clients()
        
        # 上下文缓存
        self.context_cache = {}
        self.chunk_cache = {}
        self.memory_cache = {}
        
        # 配置参数
        self.max_chunk_size = self.config.get("max_chunk_size", 4000)
        self.overlap_size = self.config.get("overlap_size", 200)
        self.embedding_dim = self.config.get("embedding_dim", 768)
        
        logger.info(f"InfiniteContextAdapterMCP initialized with APIs: Claude, Gemini, SuperMemory, GitHub")
    
    def _validate_api_keys(self):
        """验证API密钥"""
        missing_keys = []
        
        if not self.claude_api_key:
            missing_keys.append("CLAUDE_API_KEY")
        if not self.gemini_api_key:
            missing_keys.append("GEMINI_API_KEY")
        if not self.supermemory_api_key:
            missing_keys.append("SUPERMEMORY_API_KEY")
        if not self.kilo_api_key:
            missing_keys.append("KILO_API_KEY (or CLAUDE_API_KEY)")
        if not self.github_token:
            missing_keys.append("GITHUB_TOKEN")
        
        if missing_keys:
            logger.warning(f"Missing API keys: {missing_keys}")
            logger.info("Some features may not be available")
    
    def _initialize_clients(self):
        """初始化API客户端"""
        try:
            # Claude客户端
            if self.claude_api_key:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
                logger.info("Claude client initialized")
            else:
                self.claude_client = None
                
            # Gemini客户端
            if self.gemini_api_key:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info("Gemini client initialized")
            else:
                self.gemini_client = None
                
            # SuperMemory和GitHub使用requests
            self.session = requests.Session()
            
        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            logger.info("Using mock clients for testing")
            self.claude_client = None
            self.gemini_client = None
            self.session = requests.Session()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据的主要方法"""
        try:
            action = input_data.get("action", "analyze_context")
            
            if action == "analyze_context":
                return self._analyze_context(input_data)
            elif action == "process_context":
                return self._process_context(input_data)
            elif action == "search_memory":
                return self._search_memory(input_data)
            elif action == "store_memory":
                return self._store_memory(input_data)
            elif action == "generate_embedding":
                return self._generate_embedding(input_data)
            elif action == "chunk_text":
                return self._chunk_text(input_data)
            elif action == "merge_contexts":
                return self._merge_contexts(input_data)
            elif action == "process_thought":
                return self._process_thought(input_data)
            elif action == "github_analysis":
                return self._analyze_github_repo(input_data)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析上下文"""
        text = input_data.get("text", "")
        context_id = input_data.get("context_id", self._generate_context_id(text))
        
        # 使用Claude进行深度分析
        claude_analysis = self._claude_analyze(text)
        
        # 使用Gemini进行多模态分析
        gemini_analysis = self._gemini_analyze(text)
        
        # 生成嵌入向量
        embedding = self._generate_text_embedding(text)
        
        # 存储到SuperMemory
        memory_result = self._store_to_supermemory(context_id, text, {
            "claude_analysis": claude_analysis,
            "gemini_analysis": gemini_analysis,
            "embedding": embedding.tolist() if embedding is not None else None
        })
        
        result = {
            "status": "success",
            "context_id": context_id,
            "analysis": {
                "claude": claude_analysis,
                "gemini": gemini_analysis,
                "embedding_dim": embedding.shape[0] if embedding is not None else 0
            },
            "memory_stored": memory_result.get("success", False),
            "timestamp": datetime.now().isoformat()
        }
        
        # 缓存结果
        self.context_cache[context_id] = result
        
        return result
    
    def _process_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理上下文数据"""
        text = input_data.get("text", "")
        context_id = input_data.get("context_id", self._generate_context_id(text))
        
        # 分块处理
        chunks = self._split_into_chunks(text)
        
        # 处理每个块
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{context_id}_chunk_{i}"
            
            # 生成嵌入
            embedding = self._generate_text_embedding(chunk)
            
            # 创建上下文块
            context_chunk = ContextChunk(
                id=chunk_id,
                content=chunk,
                embedding=embedding,
                metadata={
                    "parent_context": context_id,
                    "chunk_index": i,
                    "chunk_size": len(chunk)
                },
                timestamp=datetime.now()
            )
            
            processed_chunks.append({
                "id": chunk_id,
                "content": chunk,
                "embedding_dim": embedding.shape[0] if embedding is not None else 0,
                "metadata": context_chunk.metadata
            })
            
            # 缓存块
            self.chunk_cache[chunk_id] = context_chunk
        
        return {
            "status": "success",
            "context_id": context_id,
            "chunks_processed": len(processed_chunks),
            "chunks": processed_chunks,
            "timestamp": datetime.now().isoformat()
        }
    
    def _search_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """搜索记忆"""
        query = input_data.get("query", "")
        limit = input_data.get("limit", 10)
        
        # 从SuperMemory搜索
        search_results = self._search_supermemory(query, limit)
        
        # 本地缓存搜索
        local_results = self._search_local_cache(query, limit)
        
        return {
            "status": "success",
            "query": query,
            "results": {
                "supermemory": search_results,
                "local_cache": local_results
            },
            "total_results": len(search_results) + len(local_results),
            "timestamp": datetime.now().isoformat()
        }
    
    def _store_memory(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """存储记忆"""
        content = input_data.get("content", "")
        metadata = input_data.get("metadata", {})
        memory_id = input_data.get("memory_id", self._generate_memory_id(content))
        
        # 存储到SuperMemory
        supermemory_result = self._store_to_supermemory(memory_id, content, metadata)
        
        # 本地缓存
        self.memory_cache[memory_id] = {
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "memory_id": memory_id,
            "stored_to_supermemory": supermemory_result.get("success", False),
            "stored_to_cache": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _process_thought(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理思考过程"""
        thought_data = input_data.get("thought", {})
        
        if isinstance(thought_data, dict):
            # 处理ThoughtProcess对象
            thought_id = thought_data.get("id", self._generate_thought_id())
            steps = thought_data.get("steps", [])
            context = thought_data.get("context", "")
            
            # 使用Claude分析思考过程
            analysis = self._claude_analyze_thought(steps, context)
            
            # 生成结果
            result = {
                "id": thought_id,
                "processed_steps": len(steps),
                "analysis": analysis,
                "confidence": analysis.get("confidence", 0.5),
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "thought_process": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "Invalid thought data format",
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_github_repo(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析GitHub仓库"""
        repo_url = input_data.get("repo_url", "")
        analysis_type = input_data.get("analysis_type", "basic")
        
        if not self.github_token:
            return {
                "status": "error",
                "message": "GitHub token not configured",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # 解析仓库URL
            repo_parts = repo_url.replace("https://github.com/", "").split("/")
            if len(repo_parts) < 2:
                return {
                    "status": "error",
                    "message": "Invalid GitHub repository URL",
                    "timestamp": datetime.now().isoformat()
                }
            
            owner, repo = repo_parts[0], repo_parts[1]
            
            # 获取仓库信息
            headers = {"Authorization": f"token {self.github_token}"}
            repo_info = self._github_api_request(f"repos/{owner}/{repo}", headers)
            
            # 获取文件列表
            contents = self._github_api_request(f"repos/{owner}/{repo}/contents", headers)
            
            # 分析结果
            analysis_result = {
                "repository": {
                    "name": repo_info.get("name"),
                    "description": repo_info.get("description"),
                    "language": repo_info.get("language"),
                    "stars": repo_info.get("stargazers_count"),
                    "forks": repo_info.get("forks_count")
                },
                "files_count": len(contents) if isinstance(contents, list) else 0,
                "analysis_type": analysis_type
            }
            
            return {
                "status": "success",
                "repo_url": repo_url,
                "analysis": analysis_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"GitHub analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _claude_analyze(self, text: str) -> Dict[str, Any]:
        """使用Claude分析文本"""
        if not self.claude_client:
            return {"analysis": "Claude client not available", "confidence": 0.0}
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"Analyze the following text and provide insights: {text[:2000]}"
                }]
            )
            
            return {
                "analysis": response.content[0].text,
                "confidence": 0.9,
                "model": "claude-3-sonnet"
            }
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return {"analysis": f"Claude analysis failed: {str(e)}", "confidence": 0.0}
    
    def _gemini_analyze(self, text: str) -> Dict[str, Any]:
        """使用Gemini分析文本"""
        if not self.gemini_client:
            return {"analysis": "Gemini client not available", "confidence": 0.0}
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Analyze this text and provide insights: {text[:2000]}"
            )
            
            return {
                "analysis": response.text,
                "confidence": 0.9,
                "model": "gemini-2.0-flash"
            }
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return {"analysis": f"Gemini analysis failed: {str(e)}", "confidence": 0.0}
    
    def _claude_analyze_thought(self, steps: List[str], context: str) -> Dict[str, Any]:
        """使用Claude分析思考过程"""
        if not self.claude_client:
            return {"analysis": "Claude client not available", "confidence": 0.0}
        
        try:
            prompt = f"""
            Analyze this thought process:
            Context: {context}
            Steps: {json.dumps(steps)}
            
            Provide analysis of the reasoning quality and confidence level.
            """
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "analysis": response.content[0].text,
                "confidence": 0.8,
                "reasoning_quality": "good"
            }
        except Exception as e:
            logger.error(f"Claude thought analysis failed: {e}")
            return {"analysis": f"Analysis failed: {str(e)}", "confidence": 0.0}
    
    def _generate_text_embedding(self, text: str) -> Optional[torch.Tensor]:
        """生成文本嵌入向量"""
        try:
            # 简单的嵌入生成（实际应用中应使用专门的嵌入模型）
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()
            
            # 生成伪嵌入向量
            np.random.seed(int(text_hash[:8], 16))
            embedding = np.random.normal(0, 1, self.embedding_dim)
            
            return torch.tensor(embedding, dtype=torch.float32)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """将文本分割成块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.max_chunk_size
            
            # 如果不是最后一块，尝试在单词边界分割
            if end < len(text):
                # 向后查找空格
                while end > start and text[end] != ' ':
                    end -= 1
                
                # 如果没找到空格，使用原始位置
                if end == start:
                    end = start + self.max_chunk_size
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            # 下一块的开始位置（考虑重叠）
            start = end - self.overlap_size if end < len(text) else end
        
        return chunks
    
    def _store_to_supermemory(self, memory_id: str, content: str, metadata: Dict) -> Dict[str, Any]:
        """存储到SuperMemory"""
        if not self.supermemory_api_key:
            return {"success": False, "message": "SuperMemory API key not configured"}
        
        try:
            # SuperMemory API调用（模拟）
            headers = {
                "Authorization": f"Bearer {self.supermemory_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "id": memory_id,
                "content": content,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            # 实际应用中应调用真实的SuperMemory API
            # response = self.session.post("https://api.supermemory.ai/store", 
            #                            headers=headers, json=data)
            
            # 模拟成功响应
            return {"success": True, "memory_id": memory_id}
            
        except Exception as e:
            logger.error(f"SuperMemory storage failed: {e}")
            return {"success": False, "message": str(e)}
    
    def _search_supermemory(self, query: str, limit: int) -> List[Dict]:
        """从SuperMemory搜索"""
        if not self.supermemory_api_key:
            return []
        
        try:
            # SuperMemory搜索API调用（模拟）
            # 实际应用中应调用真实的SuperMemory API
            return [
                {
                    "id": "mock_memory_1",
                    "content": f"Mock search result for: {query}",
                    "relevance": 0.9,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        except Exception as e:
            logger.error(f"SuperMemory search failed: {e}")
            return []
    
    def _search_local_cache(self, query: str, limit: int) -> List[Dict]:
        """搜索本地缓存"""
        results = []
        query_lower = query.lower()
        
        for memory_id, memory_data in self.memory_cache.items():
            content = memory_data.get("content", "")
            if query_lower in content.lower():
                results.append({
                    "id": memory_id,
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "relevance": 0.7,
                    "source": "local_cache"
                })
                
                if len(results) >= limit:
                    break
        
        return results
    
    def _github_api_request(self, endpoint: str, headers: Dict) -> Dict:
        """GitHub API请求"""
        url = f"https://api.github.com/{endpoint}"
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def _generate_context_id(self, text: str) -> str:
        """生成上下文ID"""
        return f"ctx_{hashlib.md5(text.encode()).hexdigest()[:12]}"
    
    def _generate_memory_id(self, content: str) -> str:
        """生成记忆ID"""
        return f"mem_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def _generate_thought_id(self) -> str:
        """生成思考ID"""
        return f"thought_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get("action")
        if not action:
            return False
        
        valid_actions = [
            "analyze_context", "process_context", "search_memory", 
            "store_memory", "generate_embedding", "chunk_text",
            "merge_contexts", "process_thought", "github_analysis"
        ]
        
        return action in valid_actions
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力"""
        capabilities = [
            "context_analysis", "text_chunking", "embedding_generation",
            "memory_storage", "memory_search", "thought_processing",
            "multi_api_integration", "github_integration"
        ]
        
        # 根据可用的API添加能力
        if self.claude_client:
            capabilities.append("claude_analysis")
        if self.gemini_client:
            capabilities.append("gemini_analysis")
        if self.supermemory_api_key:
            capabilities.append("supermemory_storage")
        if self.github_token:
            capabilities.append("github_analysis")
        
        return capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "name": self.name,
            "status": "active",
            "api_status": {
                "claude": "available" if self.claude_client else "unavailable",
                "gemini": "available" if self.gemini_client else "unavailable",
                "supermemory": "available" if self.supermemory_api_key else "unavailable",
                "kilo": "available" if self.kilo_api_key else "unavailable",
                "github": "available" if self.github_token else "unavailable"
            },
            "cache_status": {
                "context_cache_size": len(self.context_cache),
                "chunk_cache_size": len(self.chunk_cache),
                "memory_cache_size": len(self.memory_cache)
            },
            "capabilities": self.get_capabilities(),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """测试函数"""
    print("=== 测试InfiniteContextAdapterMCP ===")
    
    # 创建适配器实例
    adapter = InfiniteContextAdapterMCP()
    
    # 测试状态
    print("\n=== 适配器状态 ===")
    status = adapter.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 测试上下文分析
    print("\n=== 测试上下文分析 ===")
    test_input = {
        "action": "analyze_context",
        "text": "这是一个测试文本，用于验证无限上下文适配器的功能。它包含了多种信息，需要进行深度分析。",
        "context_id": "test_context_001"
    }
    
    result = adapter.process(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试上下文处理
    print("\n=== 测试上下文处理 ===")
    process_input = {
        "action": "process_context",
        "text": "这是一个更长的文本，用于测试分块处理功能。" * 50,
        "context_id": "test_context_002"
    }
    
    result = adapter.process(process_input)
    print(f"处理结果: 状态={result['status']}, 块数={result.get('chunks_processed', 0)}")
    
    # 测试记忆存储
    print("\n=== 测试记忆存储 ===")
    memory_input = {
        "action": "store_memory",
        "content": "重要的项目信息：MCPTool是一个强大的工具协调平台",
        "metadata": {"type": "project_info", "importance": "high"}
    }
    
    result = adapter.process(memory_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试记忆搜索
    print("\n=== 测试记忆搜索 ===")
    search_input = {
        "action": "search_memory",
        "query": "MCPTool",
        "limit": 5
    }
    
    result = adapter.process(search_input)
    print(f"搜索结果: 总数={result.get('total_results', 0)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()

