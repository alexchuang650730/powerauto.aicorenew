#!/usr/bin/env python3
"""
無限上下文適配器 - mcptool/adapters集成版本

實現智能上下文管理、記憶增強和動態推理能力
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("infinite_context")

class InfiniteContextAdapterMCP:
    """無限上下文適配器"""
    
    def __init__(self):
        """初始化適配器"""
        self.adapter_name = "infinite_context"
        self.version = "1.0.0"
        self.is_available = True
        
        # 上下文存儲
        self.context_store = {}
        self.memory_bank = defaultdict(list)
        self.conversation_history = deque(maxlen=1000)
        self.knowledge_graph = defaultdict(dict)
        
        # 配置參數
        self.max_context_length = 100000  # 最大上下文長度
        self.memory_retention_days = 30   # 記憶保持天數
        self.similarity_threshold = 0.7   # 相似度閾值
        
        # 上下文分析能力
        self.context_capabilities = {
            "memory_management": "智能記憶管理",
            "context_compression": "上下文壓縮",
            "relevance_scoring": "相關性評分",
            "knowledge_extraction": "知識提取",
            "pattern_recognition": "模式識別",
            "semantic_search": "語義搜索",
            "context_synthesis": "上下文合成",
            "adaptive_learning": "自適應學習"
        }
        
        # 工具註冊表
        self.tools = {
            "analyze_context": {
                "name": "上下文分析器",
                "description": "分析和理解複雜的上下文信息",
                "category": "analysis",
                "parameters": ["text", "context_type", "analysis_depth"]
            },
            "manage_memory": {
                "name": "記憶管理器",
                "description": "管理長期和短期記憶",
                "category": "memory",
                "parameters": ["memory_type", "content", "retention_policy"]
            },
            "compress_context": {
                "name": "上下文壓縮器",
                "description": "智能壓縮長文本保留關鍵信息",
                "category": "compression",
                "parameters": ["text", "compression_ratio", "preserve_keywords"]
            },
            "search_knowledge": {
                "name": "知識搜索器",
                "description": "在知識圖譜中搜索相關信息",
                "category": "search",
                "parameters": ["query", "search_type", "max_results"]
            },
            "synthesize_context": {
                "name": "上下文合成器",
                "description": "合成多個上下文源的信息",
                "category": "synthesis",
                "parameters": ["contexts", "synthesis_method", "output_format"]
            },
            "learn_patterns": {
                "name": "模式學習器",
                "description": "從數據中學習和識別模式",
                "category": "learning",
                "parameters": ["data", "pattern_type", "learning_algorithm"]
            }
        }
        
        logger.info(f"無限上下文適配器初始化完成，支持 {len(self.tools)} 個工具")
    
    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """處理MCP請求"""
        try:
            action = request.get('action', '')
            parameters = request.get('parameters', {})
            
            if action == 'list_tools':
                return self._list_tools()
            elif action == 'get_tool_info':
                return self._get_tool_info(parameters.get('tool_name'))
            elif action == 'execute_tool':
                return self._execute_tool(parameters.get('tool_name'), parameters.get('tool_params', {}))
            elif action == 'search_tools':
                return self._search_tools(parameters.get('query', ''))
            elif action == 'get_capabilities':
                return self._get_capabilities()
            elif action == 'get_context_stats':
                return self._get_context_stats()
            else:
                return {
                    'status': 'error',
                    'message': f'未知操作: {action}',
                    'data': None
                }
        
        except Exception as e:
            logger.error(f"處理請求時出錯: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }
    
    def _list_tools(self) -> Dict[str, Any]:
        """列出所有上下文工具"""
        return {
            'status': 'success',
            'message': '上下文工具列表獲取成功',
            'data': {
                'tools': list(self.tools.keys()),
                'tool_details': self.tools,
                'capabilities': self.context_capabilities,
                'total_count': len(self.tools),
                'adapter_info': {
                    'name': self.adapter_name,
                    'version': self.version,
                    'is_available': self.is_available,
                    'max_context_length': self.max_context_length
                }
            }
        }
    
    def _get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """獲取工具詳細信息"""
        if tool_name not in self.tools:
            return {
                'status': 'error',
                'message': f'上下文工具不存在: {tool_name}',
                'data': None
            }
        
        return {
            'status': 'success',
            'message': '上下文工具信息獲取成功',
            'data': {
                'tool_name': tool_name,
                'tool_info': self.tools[tool_name]
            }
        }
    
    def _search_tools(self, query: str) -> Dict[str, Any]:
        """搜索相關工具"""
        relevant_tools = []
        query_lower = query.lower()
        
        for tool_name, tool_info in self.tools.items():
            if (query_lower in tool_name.lower() or 
                query_lower in tool_info['description'].lower() or
                query_lower in tool_info['category'].lower()):
                relevant_tools.append({
                    'tool_name': tool_name,
                    'tool_info': tool_info
                })
        
        return {
            'status': 'success',
            'message': f'找到 {len(relevant_tools)} 個相關上下文工具',
            'data': {
                'query': query,
                'relevant_tools': relevant_tools,
                'total_found': len(relevant_tools)
            }
        }
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """獲取上下文能力信息"""
        return {
            'status': 'success',
            'message': '上下文能力信息獲取成功',
            'data': {
                'capabilities': self.context_capabilities,
                'configuration': {
                    'max_context_length': self.max_context_length,
                    'memory_retention_days': self.memory_retention_days,
                    'similarity_threshold': self.similarity_threshold
                },
                'performance_metrics': {
                    'context_entries': len(self.context_store),
                    'memory_entries': sum(len(memories) for memories in self.memory_bank.values()),
                    'conversation_history_length': len(self.conversation_history),
                    'knowledge_graph_nodes': len(self.knowledge_graph)
                }
            }
        }
    
    def _get_context_stats(self) -> Dict[str, Any]:
        """獲取上下文統計信息"""
        total_memory_size = sum(len(str(memories)) for memories in self.memory_bank.values())
        
        return {
            'status': 'success',
            'message': '上下文統計信息獲取成功',
            'data': {
                'storage_stats': {
                    'context_store_entries': len(self.context_store),
                    'memory_bank_categories': len(self.memory_bank),
                    'total_memory_size_bytes': total_memory_size,
                    'conversation_history_length': len(self.conversation_history),
                    'knowledge_graph_nodes': len(self.knowledge_graph)
                },
                'performance_stats': {
                    'average_context_length': self._calculate_average_context_length(),
                    'memory_utilization': min(total_memory_size / (self.max_context_length * 10), 1.0),
                    'knowledge_density': len(self.knowledge_graph) / max(len(self.context_store), 1)
                },
                'recent_activity': {
                    'last_context_update': self._get_last_update_time(),
                    'active_memory_categories': list(self.memory_bank.keys())[:5]
                }
            }
        }
    
    def _calculate_average_context_length(self) -> float:
        """計算平均上下文長度"""
        if not self.context_store:
            return 0.0
        
        total_length = sum(len(str(context)) for context in self.context_store.values())
        return total_length / len(self.context_store)
    
    def _get_last_update_time(self) -> str:
        """獲取最後更新時間"""
        return datetime.now().isoformat()
    
    def _execute_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> Dict[str, Any]:
        """執行上下文工具"""
        if tool_name not in self.tools:
            return {
                'status': 'error',
                'message': f'上下文工具不存在: {tool_name}',
                'data': None
            }
        
        try:
            if tool_name == 'analyze_context':
                result = self._execute_analyze_context(tool_params)
            elif tool_name == 'manage_memory':
                result = self._execute_manage_memory(tool_params)
            elif tool_name == 'compress_context':
                result = self._execute_compress_context(tool_params)
            elif tool_name == 'search_knowledge':
                result = self._execute_search_knowledge(tool_params)
            elif tool_name == 'synthesize_context':
                result = self._execute_synthesize_context(tool_params)
            elif tool_name == 'learn_patterns':
                result = self._execute_learn_patterns(tool_params)
            else:
                result = {'error': f'上下文工具 {tool_name} 尚未實現'}
            
            return {
                'status': 'success',
                'message': f'上下文工具 {tool_name} 執行成功',
                'data': {
                    'tool_name': tool_name,
                    'parameters': tool_params,
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'adapter': self.adapter_name
                }
            }
        
        except Exception as e:
            logger.error(f"執行上下文工具 {tool_name} 時出錯: {e}")
            return {
                'status': 'error',
                'message': f'上下文工具執行失敗: {str(e)}',
                'data': {
                    'tool_name': tool_name,
                    'parameters': tool_params,
                    'error': str(e)
                }
            }
    
    def _execute_analyze_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行上下文分析"""
        text = params.get('text', '')
        context_type = params.get('context_type', 'general')
        analysis_depth = params.get('analysis_depth', 'standard')
        
        if not text:
            return {'error': '分析文本不能為空'}
        
        # 生成上下文ID
        context_id = hashlib.md5(text.encode()).hexdigest()
        
        # 基本分析
        analysis_result = {
            'context_id': context_id,
            'text_length': len(text),
            'word_count': len(text.split()),
            'context_type': context_type,
            'analysis_depth': analysis_depth
        }
        
        # 深度分析
        if analysis_depth in ['deep', 'comprehensive']:
            analysis_result.update({
                'key_concepts': self._extract_key_concepts(text),
                'sentiment_analysis': self._analyze_sentiment(text),
                'complexity_score': self._calculate_complexity(text),
                'information_density': self._calculate_information_density(text)
            })
        
        # 全面分析
        if analysis_depth == 'comprehensive':
            analysis_result.update({
                'semantic_structure': self._analyze_semantic_structure(text),
                'knowledge_entities': self._extract_knowledge_entities(text),
                'contextual_relationships': self._identify_relationships(text),
                'reasoning_patterns': self._identify_reasoning_patterns(text)
            })
        
        # 存儲上下文
        self.context_store[context_id] = {
            'text': text,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat(),
            'type': context_type
        }
        
        return analysis_result
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """提取關鍵概念"""
        # 簡化的關鍵概念提取
        words = text.lower().split()
        
        # 常見的重要概念關鍵詞
        important_keywords = [
            'algorithm', 'data', 'analysis', 'research', 'study', 'method',
            'result', 'conclusion', 'theory', 'model', 'system', 'process',
            'problem', 'solution', 'approach', 'technique', 'framework',
            'calculate', 'compute', 'measure', 'evaluate', 'assess'
        ]
        
        concepts = []
        for word in words:
            if len(word) > 4 and (word in important_keywords or word.endswith('tion') or word.endswith('ment')):
                if word not in concepts:
                    concepts.append(word)
        
        return concepts[:10]  # 返回前10個概念
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析情感傾向"""
        # 簡化的情感分析
        positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'effective', 'optimal']
        negative_words = ['bad', 'poor', 'negative', 'failure', 'ineffective', 'problem', 'error']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            confidence = 0.5
        else:
            if positive_count > negative_count:
                sentiment = 'positive'
                confidence = positive_count / total_sentiment_words
            elif negative_count > positive_count:
                sentiment = 'negative'
                confidence = negative_count / total_sentiment_words
            else:
                sentiment = 'neutral'
                confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }
    
    def _calculate_complexity(self, text: str) -> float:
        """計算文本複雜度"""
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return 0.0
        
        # 基於詞彙長度和句子長度的複雜度計算
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        # 標準化複雜度分數 (0-1)
        complexity = min((avg_word_length * avg_sentence_length) / 100, 1.0)
        
        return round(complexity, 3)
    
    def _calculate_information_density(self, text: str) -> float:
        """計算信息密度"""
        words = text.split()
        unique_words = set(word.lower() for word in words)
        
        if not words:
            return 0.0
        
        # 信息密度 = 唯一詞彙數 / 總詞彙數
        density = len(unique_words) / len(words)
        
        return round(density, 3)
    
    def _analyze_semantic_structure(self, text: str) -> Dict[str, Any]:
        """分析語義結構"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        return {
            'sentence_count': len(sentences),
            'average_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            'structure_type': 'narrative' if len(sentences) > 5 else 'descriptive',
            'coherence_score': 0.8  # 簡化的連貫性分數
        }
    
    def _extract_knowledge_entities(self, text: str) -> List[Dict[str, Any]]:
        """提取知識實體"""
        # 簡化的實體提取
        import re
        
        entities = []
        
        # 提取數字
        numbers = re.findall(r'\d+\.?\d*', text)
        for num in numbers[:5]:  # 限制數量
            entities.append({
                'type': 'number',
                'value': num,
                'context': 'numerical_data'
            })
        
        # 提取大寫詞（可能是專有名詞）
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        for noun in proper_nouns[:5]:  # 限制數量
            entities.append({
                'type': 'proper_noun',
                'value': noun,
                'context': 'named_entity'
            })
        
        return entities
    
    def _identify_relationships(self, text: str) -> List[Dict[str, Any]]:
        """識別上下文關係"""
        relationships = []
        
        # 簡化的關係識別
        if 'because' in text.lower() or 'due to' in text.lower():
            relationships.append({
                'type': 'causal',
                'description': 'Causal relationship detected',
                'confidence': 0.7
            })
        
        if 'compare' in text.lower() or 'versus' in text.lower() or 'vs' in text.lower():
            relationships.append({
                'type': 'comparative',
                'description': 'Comparative relationship detected',
                'confidence': 0.8
            })
        
        if 'result' in text.lower() or 'conclusion' in text.lower():
            relationships.append({
                'type': 'consequential',
                'description': 'Result-based relationship detected',
                'confidence': 0.6
            })
        
        return relationships
    
    def _identify_reasoning_patterns(self, text: str) -> List[Dict[str, Any]]:
        """識別推理模式"""
        patterns = []
        
        # 檢測推理模式
        if any(word in text.lower() for word in ['therefore', 'thus', 'hence', 'consequently']):
            patterns.append({
                'type': 'deductive',
                'description': 'Deductive reasoning pattern',
                'indicators': ['therefore', 'thus', 'hence']
            })
        
        if any(word in text.lower() for word in ['for example', 'such as', 'including']):
            patterns.append({
                'type': 'inductive',
                'description': 'Inductive reasoning pattern',
                'indicators': ['for example', 'such as']
            })
        
        if any(word in text.lower() for word in ['if', 'suppose', 'assume', 'given that']):
            patterns.append({
                'type': 'hypothetical',
                'description': 'Hypothetical reasoning pattern',
                'indicators': ['if', 'suppose', 'assume']
            })
        
        return patterns
    
    def _execute_manage_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行記憶管理"""
        memory_type = params.get('memory_type', 'short_term')
        content = params.get('content', '')
        retention_policy = params.get('retention_policy', 'default')
        
        if not content:
            return {'error': '記憶內容不能為空'}
        
        # 生成記憶ID
        memory_id = hashlib.md5(f"{memory_type}_{content}_{datetime.now()}".encode()).hexdigest()
        
        # 創建記憶條目
        memory_entry = {
            'id': memory_id,
            'content': content,
            'type': memory_type,
            'retention_policy': retention_policy,
            'created_at': datetime.now().isoformat(),
            'access_count': 0,
            'importance_score': self._calculate_importance(content)
        }
        
        # 存儲記憶
        self.memory_bank[memory_type].append(memory_entry)
        
        # 記憶管理
        if len(self.memory_bank[memory_type]) > 100:  # 限制記憶數量
            self._cleanup_memory(memory_type)
        
        return {
            'memory_id': memory_id,
            'memory_type': memory_type,
            'content_length': len(content),
            'importance_score': memory_entry['importance_score'],
            'retention_policy': retention_policy,
            'total_memories': len(self.memory_bank[memory_type]),
            'storage_status': 'success'
        }
    
    def _calculate_importance(self, content: str) -> float:
        """計算記憶重要性分數"""
        # 基於內容特徵計算重要性
        importance_keywords = [
            'important', 'critical', 'key', 'essential', 'significant',
            'result', 'conclusion', 'finding', 'discovery', 'breakthrough'
        ]
        
        content_lower = content.lower()
        importance_score = 0.5  # 基礎分數
        
        # 關鍵詞加分
        for keyword in importance_keywords:
            if keyword in content_lower:
                importance_score += 0.1
        
        # 長度加分（較長的內容可能更重要）
        if len(content) > 200:
            importance_score += 0.1
        
        # 數字和數據加分
        import re
        if re.search(r'\d+', content):
            importance_score += 0.1
        
        return min(importance_score, 1.0)
    
    def _cleanup_memory(self, memory_type: str):
        """清理記憶"""
        memories = self.memory_bank[memory_type]
        
        # 按重要性和訪問次數排序，保留前80個
        memories.sort(key=lambda x: (x['importance_score'], x['access_count']), reverse=True)
        self.memory_bank[memory_type] = memories[:80]
        
        logger.info(f"清理 {memory_type} 記憶，保留 {len(self.memory_bank[memory_type])} 條")
    
    def _execute_compress_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行上下文壓縮"""
        text = params.get('text', '')
        compression_ratio = params.get('compression_ratio', 0.5)
        preserve_keywords = params.get('preserve_keywords', [])
        
        if not text:
            return {'error': '壓縮文本不能為空'}
        
        # 簡化的文本壓縮
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        target_sentences = max(1, int(len(sentences) * compression_ratio))
        
        # 計算句子重要性
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0.5  # 基礎分數
            
            # 關鍵詞加分
            for keyword in preserve_keywords:
                if keyword.lower() in sentence.lower():
                    score += 0.3
            
            # 長度加分（適中長度的句子更重要）
            word_count = len(sentence.split())
            if 10 <= word_count <= 30:
                score += 0.2
            
            # 數字和數據加分
            import re
            if re.search(r'\d+', sentence):
                score += 0.2
            
            sentence_scores.append((score, i, sentence))
        
        # 選擇最重要的句子
        sentence_scores.sort(reverse=True)
        selected_sentences = sentence_scores[:target_sentences]
        selected_sentences.sort(key=lambda x: x[1])  # 按原順序排列
        
        compressed_text = '. '.join([s[2] for s in selected_sentences]) + '.'
        
        return {
            'original_length': len(text),
            'compressed_length': len(compressed_text),
            'compression_ratio': len(compressed_text) / len(text),
            'target_ratio': compression_ratio,
            'sentences_original': len(sentences),
            'sentences_compressed': len(selected_sentences),
            'preserved_keywords': preserve_keywords,
            'compressed_text': compressed_text
        }
    
    def _execute_search_knowledge(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行知識搜索"""
        query = params.get('query', '')
        search_type = params.get('search_type', 'semantic')
        max_results = params.get('max_results', 10)
        
        if not query:
            return {'error': '搜索查詢不能為空'}
        
        search_results = []
        query_lower = query.lower()
        
        # 搜索上下文存儲
        for context_id, context_data in self.context_store.items():
            relevance_score = self._calculate_relevance(query_lower, context_data)
            
            if relevance_score > self.similarity_threshold:
                search_results.append({
                    'context_id': context_id,
                    'relevance_score': relevance_score,
                    'context_type': context_data.get('type', 'unknown'),
                    'timestamp': context_data.get('timestamp', ''),
                    'text_preview': context_data.get('text', '')[:200] + '...'
                })
        
        # 搜索記憶庫
        for memory_type, memories in self.memory_bank.items():
            for memory in memories:
                if query_lower in memory['content'].lower():
                    search_results.append({
                        'memory_id': memory['id'],
                        'memory_type': memory_type,
                        'relevance_score': 0.8,
                        'importance_score': memory['importance_score'],
                        'content_preview': memory['content'][:200] + '...'
                    })
        
        # 排序和限制結果
        search_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        search_results = search_results[:max_results]
        
        return {
            'query': query,
            'search_type': search_type,
            'results': search_results,
            'total_found': len(search_results),
            'search_domains': ['context_store', 'memory_bank'],
            'similarity_threshold': self.similarity_threshold
        }
    
    def _calculate_relevance(self, query: str, context_data: Dict[str, Any]) -> float:
        """計算相關性分數"""
        text = context_data.get('text', '').lower()
        
        # 簡單的相關性計算
        query_words = query.split()
        text_words = text.split()
        
        matches = sum(1 for word in query_words if word in text_words)
        relevance = matches / len(query_words) if query_words else 0
        
        return relevance
    
    def _execute_synthesize_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行上下文合成"""
        contexts = params.get('contexts', [])
        synthesis_method = params.get('synthesis_method', 'merge')
        output_format = params.get('output_format', 'text')
        
        if not contexts:
            return {'error': '合成上下文列表不能為空'}
        
        synthesis_result = {
            'method': synthesis_method,
            'input_contexts': len(contexts),
            'output_format': output_format
        }
        
        if synthesis_method == 'merge':
            # 簡單合併
            merged_text = '\n\n'.join(contexts)
            synthesis_result.update({
                'synthesized_content': merged_text,
                'total_length': len(merged_text),
                'merge_strategy': 'sequential'
            })
        
        elif synthesis_method == 'summarize':
            # 提取關鍵信息
            key_points = []
            for context in contexts:
                # 提取每個上下文的關鍵句子
                sentences = [s.strip() for s in context.split('.') if s.strip()]
                if sentences:
                    key_points.append(sentences[0])  # 取第一句作為關鍵點
            
            summary = '. '.join(key_points) + '.'
            synthesis_result.update({
                'synthesized_content': summary,
                'key_points_extracted': len(key_points),
                'compression_ratio': len(summary) / sum(len(c) for c in contexts)
            })
        
        elif synthesis_method == 'analyze':
            # 分析合成
            total_words = sum(len(c.split()) for c in contexts)
            unique_concepts = set()
            
            for context in contexts:
                concepts = self._extract_key_concepts(context)
                unique_concepts.update(concepts)
            
            analysis = {
                'total_contexts': len(contexts),
                'total_words': total_words,
                'unique_concepts': list(unique_concepts),
                'concept_count': len(unique_concepts),
                'average_context_length': total_words / len(contexts)
            }
            
            synthesis_result.update({
                'synthesized_content': analysis,
                'analysis_type': 'conceptual_analysis'
            })
        
        return synthesis_result
    
    def _execute_learn_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """執行模式學習"""
        data = params.get('data', [])
        pattern_type = params.get('pattern_type', 'sequence')
        learning_algorithm = params.get('learning_algorithm', 'frequency')
        
        if not data:
            return {'error': '學習數據不能為空'}
        
        learning_result = {
            'data_size': len(data),
            'pattern_type': pattern_type,
            'learning_algorithm': learning_algorithm
        }
        
        if pattern_type == 'sequence':
            # 序列模式學習
            if learning_algorithm == 'frequency':
                # 頻率分析
                from collections import Counter
                if isinstance(data[0], str):
                    # 文本序列
                    word_freq = Counter()
                    for text in data:
                        words = text.lower().split()
                        word_freq.update(words)
                    
                    patterns = {
                        'most_common_words': word_freq.most_common(10),
                        'vocabulary_size': len(word_freq),
                        'total_words': sum(word_freq.values())
                    }
                else:
                    # 數值序列
                    value_freq = Counter(data)
                    patterns = {
                        'most_common_values': value_freq.most_common(10),
                        'unique_values': len(value_freq),
                        'total_values': len(data)
                    }
                
                learning_result['patterns'] = patterns
        
        elif pattern_type == 'trend':
            # 趨勢模式學習
            if isinstance(data[0], (int, float)):
                # 數值趨勢
                if len(data) > 1:
                    differences = [data[i+1] - data[i] for i in range(len(data)-1)]
                    avg_change = sum(differences) / len(differences)
                    
                    trend = 'increasing' if avg_change > 0 else 'decreasing' if avg_change < 0 else 'stable'
                    
                    patterns = {
                        'trend_direction': trend,
                        'average_change': avg_change,
                        'volatility': sum(abs(d) for d in differences) / len(differences),
                        'data_range': {'min': min(data), 'max': max(data)}
                    }
                    
                    learning_result['patterns'] = patterns
        
        elif pattern_type == 'classification':
            # 分類模式學習
            from collections import defaultdict
            categories = defaultdict(list)
            
            for item in data:
                if isinstance(item, dict) and 'category' in item:
                    categories[item['category']].append(item)
                elif isinstance(item, str):
                    # 簡單的文本分類
                    if any(word in item.lower() for word in ['question', '?', 'what', 'how', 'why']):
                        categories['question'].append(item)
                    elif any(word in item.lower() for word in ['calculate', 'compute', 'math']):
                        categories['calculation'].append(item)
                    else:
                        categories['statement'].append(item)
            
            patterns = {
                'categories_found': list(categories.keys()),
                'category_distribution': {cat: len(items) for cat, items in categories.items()},
                'total_categories': len(categories)
            }
            
            learning_result['patterns'] = patterns
        
        # 存儲學習結果到知識圖譜
        pattern_id = hashlib.md5(str(learning_result).encode()).hexdigest()
        self.knowledge_graph[pattern_id] = {
            'type': 'learned_pattern',
            'result': learning_result,
            'timestamp': datetime.now().isoformat()
        }
        
        learning_result['pattern_id'] = pattern_id
        
        return learning_result

def create_cli_interface():
    """創建CLI接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='無限上下文適配器CLI')
    parser.add_argument('--action', required=True, 
                       choices=['list_tools', 'execute_tool', 'search_tools', 'get_tool_info', 'get_capabilities', 'get_context_stats'],
                       help='要執行的操作')
    parser.add_argument('--tool-name', help='工具名稱')
    parser.add_argument('--query', help='搜索查詢')
    parser.add_argument('--params', help='工具參數（JSON格式）')
    
    return parser

def main():
    """主函數 - CLI入口"""
    parser = create_cli_interface()
    args = parser.parse_args()
    
    # 初始化適配器
    adapter = InfiniteContextAdapterMCP()
    
    # 構建請求
    request = {'action': args.action}
    
    if args.action == 'execute_tool':
        if not args.tool_name:
            print("錯誤: 執行工具需要指定 --tool-name")
            return
        
        params = {}
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                print("錯誤: 參數必須是有效的JSON格式")
                return
        
        request['parameters'] = {
            'tool_name': args.tool_name,
            'tool_params': params
        }
    
    elif args.action == 'search_tools':
        if not args.query:
            print("錯誤: 搜索工具需要指定 --query")
            return
        
        request['parameters'] = {'query': args.query}
    
    elif args.action == 'get_tool_info':
        if not args.tool_name:
            print("錯誤: 獲取工具信息需要指定 --tool-name")
            return
        
        request['parameters'] = {'tool_name': args.tool_name}
    
    # 執行請求
    result = adapter.process(request)
    
    # 輸出結果
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

