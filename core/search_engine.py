"""
搜索引擎 - 第一层架构
负责快速搜索和工具发现
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

class SearchEngine:
    """搜索引擎 - 搜索+工具发现"""
    
    def __init__(self):
        """初始化搜索引擎"""
        self.logger = logging.getLogger("SearchEngine")
        
        # 工具库 - 简单的工具映射
        self.tool_registry = {
            # 编程相关
            "python": "python_helper",
            "javascript": "js_helper", 
            "react": "react_helper",
            "api": "api_generator",
            "代码": "code_analyzer",
            
            # 搜索相关
            "搜索": "web_search",
            "查找": "web_search",
            "search": "web_search",
            
            # 文档相关
            "文档": "doc_generator",
            "说明": "doc_generator",
            "documentation": "doc_generator",
            
            # 分析相关
            "分析": "analyzer",
            "analyze": "analyzer",
            "性能": "performance_analyzer"
        }
        
        # 知识库 - 简单的问答库
        self.knowledge_base = {
            "python异步编程": {
                "tool": "python_helper",
                "result": "Python异步编程最佳实践：使用async/await、避免阻塞操作、合理使用asyncio.gather()等"
            },
            "react组件": {
                "tool": "react_helper", 
                "result": "React组件创建：使用函数组件、hooks、props传递、状态管理等"
            }
        }
        
        self.logger.info("搜索引擎初始化完成")
    
    async def search(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        搜索处理 - 核心逻辑：搜索+工具
        
        Args:
            query: 搜索查询
            context: 上下文
            
        Returns:
            搜索结果
        """
        self.logger.info(f"搜索: {query}")
        
        # 1. 先在知识库中搜索
        knowledge_result = self._search_knowledge(query)
        if knowledge_result:
            return {
                "success": True,
                "result": knowledge_result["result"],
                "tool": knowledge_result["tool"],
                "source": "knowledge_base"
            }
        
        # 2. 搜索合适的工具
        tool = self._find_tool(query)
        if tool:
            # 找到工具，调用工具处理
            tool_result = await self._call_tool(tool, query, context)
            if tool_result:
                return {
                    "success": True,
                    "result": tool_result,
                    "tool": tool,
                    "source": "tool_call"
                }
        
        # 3. 搜索失败，交给下一层
        return {
            "success": False,
            "reason": "搜索层无法处理",
            "query": query
        }
    
    def _search_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        """在知识库中搜索"""
        query_lower = query.lower()
        
        for key, value in self.knowledge_base.items():
            if key in query_lower or any(word in query_lower for word in key.split()):
                self.logger.info(f"知识库命中: {key}")
                return value
        
        return None
    
    def _find_tool(self, query: str) -> Optional[str]:
        """查找合适的工具"""
        query_lower = query.lower()
        
        for keyword, tool in self.tool_registry.items():
            if keyword in query_lower:
                self.logger.info(f"工具匹配: {keyword} -> {tool}")
                return tool
        
        return None
    
    async def _call_tool(self, tool: str, query: str, context: Dict[str, Any] = None) -> Optional[str]:
        """调用工具处理"""
        self.logger.info(f"调用工具: {tool}")
        
        # 模拟工具调用
        tool_responses = {
            "python_helper": f"Python助手处理: {query}",
            "js_helper": f"JavaScript助手处理: {query}",
            "react_helper": f"React助手处理: {query}",
            "api_generator": f"API生成器处理: {query}",
            "code_analyzer": f"代码分析器处理: {query}",
            "web_search": f"网络搜索结果: {query}",
            "doc_generator": f"文档生成器处理: {query}",
            "analyzer": f"分析器处理: {query}",
            "performance_analyzer": f"性能分析器处理: {query}"
        }
        
        # 模拟异步处理
        await asyncio.sleep(0.1)
        
        return tool_responses.get(tool, f"未知工具 {tool} 处理: {query}")
    
    def add_tool(self, keywords: List[str], tool_name: str):
        """添加新工具"""
        for keyword in keywords:
            self.tool_registry[keyword] = tool_name
        self.logger.info(f"添加工具: {keywords} -> {tool_name}")
    
    def add_knowledge(self, key: str, tool: str, result: str):
        """添加知识"""
        self.knowledge_base[key] = {"tool": tool, "result": result}
        self.logger.info(f"添加知识: {key}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "tools_count": len(self.tool_registry),
            "knowledge_count": len(self.knowledge_base),
            "available": True
        }

