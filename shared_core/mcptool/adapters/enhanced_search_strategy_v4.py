"""
增強搜索策略v4.0 - 智能工具發現和匹配算法

基於工具選擇器v4.0的成功，進一步增強搜索策略
目標：提高外部工具發現的準確性和匹配度
"""

import re
import json
import random
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class SearchResult:
    """搜索結果"""
    tool_name: str
    description: str
    confidence: float
    service_type: str
    match_reasons: List[str]
    search_query: str

@dataclass
class ToolMatch:
    """工具匹配結果"""
    tool: SearchResult
    match_score: float
    relevance_factors: Dict[str, float]

class EnhancedSearchStrategyV4:
    """增強搜索策略v4.0"""
    
    def __init__(self):
        """初始化搜索策略"""
        self.search_templates = self._build_search_templates()
        self.tool_databases = self._build_tool_databases()
        self.matching_algorithms = self._build_matching_algorithms()
        self.service_priorities = self._build_service_priorities()
        
    def _build_search_templates(self) -> Dict[str, List[str]]:
        """構建搜索模板"""
        return {
            "factual_search": [
                "{entity} current information API",
                "real-time {entity} data service",
                "{entity} fact checking tool",
                "current {entity} status API",
                "live {entity} information service",
                "{entity} verification tool MCP",
                "real-time fact API {entity}",
                "{entity} current data connector"
            ],
            "academic_paper": [
                "{topic} research paper API",
                "academic paper search {topic}",
                "{topic} scholarly article tool",
                "research database {topic} API",
                "{topic} citation analysis tool",
                "academic search engine {topic}",
                "{topic} paper analysis service",
                "scholarly {topic} research tool"
            ],
            "automation": [
                "{process} automation tool",
                "workflow automation {process}",
                "{process} process automation API",
                "automated {process} service",
                "{process} workflow connector",
                "business process {process} tool",
                "{process} automation platform",
                "robotic {process} automation"
            ],
            "calculation": [
                "{problem} mathematical solver",
                "calculation API {problem}",
                "{problem} computation service",
                "mathematical {problem} tool",
                "{problem} solver API",
                "computational {problem} engine",
                "{problem} calculation platform",
                "math API {problem} solver"
            ],
            "complex_analysis": [
                "{topic} analysis service",
                "analytical {topic} tool",
                "{topic} comparison API",
                "deep analysis {topic} service",
                "{topic} evaluation tool",
                "comprehensive {topic} analyzer",
                "{topic} assessment platform",
                "analytical reasoning {topic} API"
            ],
            "simple_qa": [
                "{topic} knowledge API",
                "general {topic} information service",
                "{topic} Q&A tool",
                "knowledge base {topic} API",
                "{topic} information retrieval",
                "general knowledge {topic} service",
                "{topic} definition API",
                "encyclopedia {topic} tool"
            ]
        }
    
    def _build_tool_databases(self) -> Dict[str, List[Dict[str, Any]]]:
        """構建工具數據庫（模擬外部服務）"""
        return {
            "mcp.so": [
                {
                    "name": "arxiv_mcp_server",
                    "description": "Academic paper search and analysis from ArXiv database",
                    "categories": ["academic", "research", "paper", "scientific"],
                    "capabilities": ["search", "analysis", "citation", "full_text"],
                    "confidence_base": 0.90
                },
                {
                    "name": "realtime_fact_checker",
                    "description": "Real-time fact verification and current information retrieval",
                    "categories": ["factual", "current", "verification", "real-time"],
                    "capabilities": ["fact_check", "current_data", "verification"],
                    "confidence_base": 0.88
                },
                {
                    "name": "knowledge_graph_api",
                    "description": "Comprehensive knowledge graph for general information",
                    "categories": ["knowledge", "general", "information", "qa"],
                    "capabilities": ["knowledge_retrieval", "entity_info", "relationships"],
                    "confidence_base": 0.85
                },
                {
                    "name": "math_solver_pro",
                    "description": "Advanced mathematical problem solver and calculator",
                    "categories": ["math", "calculation", "solver", "computation"],
                    "capabilities": ["calculation", "equation_solving", "formula_evaluation"],
                    "confidence_base": 0.92
                }
            ],
            "aci.dev": [
                {
                    "name": "ai_analysis_engine",
                    "description": "Advanced AI-powered analysis and comparison service",
                    "categories": ["analysis", "comparison", "evaluation", "reasoning"],
                    "capabilities": ["deep_analysis", "comparison", "evaluation", "reasoning"],
                    "confidence_base": 0.87
                },
                {
                    "name": "intelligent_data_processor",
                    "description": "Intelligent data processing and analysis platform",
                    "categories": ["data", "processing", "analysis", "intelligence"],
                    "capabilities": ["data_analysis", "pattern_recognition", "insights"],
                    "confidence_base": 0.84
                },
                {
                    "name": "concept_analyzer",
                    "description": "Advanced concept analysis and definition service",
                    "categories": ["concept", "definition", "explanation", "analysis"],
                    "capabilities": ["concept_analysis", "definition", "explanation"],
                    "confidence_base": 0.82
                }
            ],
            "zapier": [
                {
                    "name": "workflow_automation_hub",
                    "description": "Comprehensive workflow automation and integration platform",
                    "categories": ["workflow", "automation", "integration", "process"],
                    "capabilities": ["workflow_design", "automation", "integration", "scheduling"],
                    "confidence_base": 0.86
                },
                {
                    "name": "process_optimizer",
                    "description": "Business process optimization and automation tool",
                    "categories": ["process", "optimization", "business", "automation"],
                    "capabilities": ["process_analysis", "optimization", "automation_design"],
                    "confidence_base": 0.83
                },
                {
                    "name": "integration_connector",
                    "description": "Universal integration and connection service",
                    "categories": ["integration", "connection", "api", "sync"],
                    "capabilities": ["api_integration", "data_sync", "connection_management"],
                    "confidence_base": 0.80
                }
            ]
        }
    
    def _build_matching_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """構建匹配算法"""
        return {
            "keyword_matching": {
                "weight": 0.35,
                "algorithm": self._keyword_match_score
            },
            "category_matching": {
                "weight": 0.25,
                "algorithm": self._category_match_score
            },
            "capability_matching": {
                "weight": 0.25,
                "algorithm": self._capability_match_score
            },
            "semantic_similarity": {
                "weight": 0.15,
                "algorithm": self._semantic_similarity_score
            }
        }
    
    def _build_service_priorities(self) -> Dict[str, float]:
        """構建服務優先級"""
        return {
            "mcp.so": 1.0,      # 最高優先級，專門的MCP工具
            "aci.dev": 0.9,     # 高優先級，AI服務
            "zapier": 0.8       # 中等優先級，自動化平台
        }
    
    def generate_search_queries(self, question: str, question_type: str) -> List[str]:
        """生成搜索查詢"""
        templates = self.search_templates.get(question_type, [])
        
        # 提取關鍵實體和主題
        entities = self._extract_entities(question)
        topics = self._extract_topics(question, question_type)
        
        queries = []
        
        # 基於模板生成查詢
        for template in templates:
            # 處理實體模板
            if "{entity}" in template:
                for entity in entities[:2]:  # 最多使用2個實體
                    query = template.format(entity=entity)
                    queries.append(query)
            
            # 處理主題模板
            if "{topic}" in template:
                for topic in topics[:2]:  # 最多使用2個主題
                    query = template.format(topic=topic)
                    queries.append(query)
            
            # 處理問題模板
            if "{problem}" in template:
                for topic in topics[:2]:
                    query = template.format(problem=topic)
                    queries.append(query)
            
            # 處理流程模板
            if "{process}" in template:
                for topic in topics[:2]:
                    query = template.format(process=topic)
                    queries.append(query)
        
        # 添加通用查詢
        queries.extend([
            f"{question_type} tool API",
            f"{question_type} service MCP",
            f"best {question_type} automation tool"
        ])
        
        return list(set(queries))  # 去重
    
    def _extract_entities(self, question: str) -> List[str]:
        """提取實體"""
        # 簡化的實體提取
        entities = []
        
        # 提取方括號中的實體
        bracket_entities = re.findall(r'\[([^\]]+)\]', question)
        entities.extend(bracket_entities)
        
        # 提取#後的數字實體
        number_entities = re.findall(r'#(\d+)', question)
        entities.extend([f"item_{num}" for num in number_entities])
        
        # 提取常見實體模式
        entity_patterns = [
            r'about\s+(\w+)',
            r'of\s+(\w+)',
            r'for\s+(\w+)',
            r'(\w+)\s+record',
            r'(\w+)\s+problem'
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, question.lower())
            entities.extend(matches)
        
        return entities[:5]  # 最多返回5個實體
    
    def _extract_topics(self, question: str, question_type: str) -> List[str]:
        """提取主題"""
        topics = []
        
        # 基於問題類型的主題提取
        type_topics = {
            "factual_search": ["information", "data", "facts"],
            "academic_paper": ["research", "academic", "scholarly"],
            "automation": ["workflow", "process", "automation"],
            "calculation": ["mathematical", "computation", "calculation"],
            "complex_analysis": ["analysis", "comparison", "evaluation"],
            "simple_qa": ["knowledge", "information", "general"]
        }
        
        topics.extend(type_topics.get(question_type, []))
        
        # 提取問題中的關鍵詞作為主題
        keywords = re.findall(r'\b\w{4,}\b', question.lower())
        topics.extend(keywords[:3])
        
        return topics[:5]  # 最多返回5個主題
    
    def search_tools(self, queries: List[str], question_type: str) -> List[SearchResult]:
        """搜索工具"""
        all_results = []
        
        for service, tools in self.tool_databases.items():
            for tool in tools:
                for query in queries:
                    match_score = self._calculate_match_score(query, tool, question_type)
                    
                    if match_score > 0.3:  # 最低匹配閾值
                        confidence = tool["confidence_base"] * match_score
                        confidence *= self.service_priorities[service]  # 服務優先級調整
                        
                        result = SearchResult(
                            tool_name=tool["name"],
                            description=tool["description"],
                            confidence=confidence,
                            service_type=service,
                            match_reasons=self._get_match_reasons(query, tool),
                            search_query=query
                        )
                        all_results.append(result)
        
        # 去重並排序
        unique_results = {}
        for result in all_results:
            if result.tool_name not in unique_results or result.confidence > unique_results[result.tool_name].confidence:
                unique_results[result.tool_name] = result
        
        sorted_results = sorted(unique_results.values(), key=lambda x: x.confidence, reverse=True)
        return sorted_results[:10]  # 返回前10個結果
    
    def _calculate_match_score(self, query: str, tool: Dict[str, Any], question_type: str) -> float:
        """計算匹配分數"""
        total_score = 0.0
        
        for algorithm_name, config in self.matching_algorithms.items():
            algorithm = config["algorithm"]
            weight = config["weight"]
            score = algorithm(query, tool, question_type)
            total_score += score * weight
        
        return min(1.0, total_score)
    
    def _keyword_match_score(self, query: str, tool: Dict[str, Any], question_type: str) -> float:
        """關鍵詞匹配分數"""
        query_words = set(query.lower().split())
        tool_words = set()
        
        # 收集工具的所有文本
        tool_words.update(tool["name"].lower().split())
        tool_words.update(tool["description"].lower().split())
        tool_words.update(tool["categories"])
        tool_words.update(tool["capabilities"])
        
        # 計算交集
        intersection = query_words.intersection(tool_words)
        union = query_words.union(tool_words)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(query_words)  # Jaccard相似度的變體
    
    def _category_match_score(self, query: str, tool: Dict[str, Any], question_type: str) -> float:
        """類別匹配分數"""
        query_lower = query.lower()
        categories = tool["categories"]
        
        matches = sum(1 for category in categories if category in query_lower)
        return matches / len(categories) if categories else 0.0
    
    def _capability_match_score(self, query: str, tool: Dict[str, Any], question_type: str) -> float:
        """能力匹配分數"""
        # 問題類型到能力的映射
        type_capabilities = {
            "factual_search": ["fact_check", "current_data", "verification", "real_time"],
            "academic_paper": ["search", "analysis", "citation", "research"],
            "automation": ["workflow_design", "automation", "integration", "process"],
            "calculation": ["calculation", "equation_solving", "computation", "math"],
            "complex_analysis": ["deep_analysis", "comparison", "evaluation", "reasoning"],
            "simple_qa": ["knowledge_retrieval", "information", "qa", "general"]
        }
        
        required_capabilities = type_capabilities.get(question_type, [])
        tool_capabilities = tool["capabilities"]
        
        if not required_capabilities:
            return 0.5
        
        matches = sum(1 for cap in required_capabilities if any(tc in cap or cap in tc for tc in tool_capabilities))
        return matches / len(required_capabilities)
    
    def _semantic_similarity_score(self, query: str, tool: Dict[str, Any], question_type: str) -> float:
        """語義相似度分數（簡化版）"""
        # 簡化的語義相似度計算
        query_lower = query.lower()
        tool_text = f"{tool['name']} {tool['description']}".lower()
        
        # 計算共同的語義詞根
        semantic_matches = 0
        semantic_pairs = [
            ("search", "find"), ("analysis", "analyze"), ("automation", "automate"),
            ("calculation", "compute"), ("information", "data"), ("current", "real-time"),
            ("academic", "scholarly"), ("paper", "research"), ("fact", "truth"),
            ("workflow", "process"), ("tool", "service"), ("api", "connector")
        ]
        
        for word1, word2 in semantic_pairs:
            if (word1 in query_lower and word2 in tool_text) or (word2 in query_lower and word1 in tool_text):
                semantic_matches += 1
        
        return min(1.0, semantic_matches * 0.2)
    
    def _get_match_reasons(self, query: str, tool: Dict[str, Any]) -> List[str]:
        """獲取匹配原因"""
        reasons = []
        
        query_words = set(query.lower().split())
        tool_words = set(tool["name"].lower().split() + tool["description"].lower().split())
        
        common_words = query_words.intersection(tool_words)
        if common_words:
            reasons.append(f"關鍵詞匹配: {', '.join(list(common_words)[:3])}")
        
        category_matches = [cat for cat in tool["categories"] if cat in query.lower()]
        if category_matches:
            reasons.append(f"類別匹配: {', '.join(category_matches[:2])}")
        
        return reasons
    
    def execute_enhanced_search(self, question: str, question_type: str) -> List[SearchResult]:
        """執行增強搜索"""
        print(f"🔍 增強搜索策略v4.0: {question[:50]}...")
        print(f"📊 問題類型: {question_type}")
        
        # 生成搜索查詢
        queries = self.generate_search_queries(question, question_type)
        print(f"🔎 生成查詢: {len(queries)}個")
        
        # 搜索工具
        results = self.search_tools(queries, question_type)
        print(f"🛠️ 發現工具: {len(results)}個")
        
        # 顯示前3個結果
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. {result.tool_name} ({result.service_type})")
            print(f"     信心度: {result.confidence:.2%}")
            print(f"     匹配原因: {'; '.join(result.match_reasons)}")
        
        return results

def test_enhanced_search_strategy():
    """測試增強搜索策略v4.0"""
    print("🧪 測試增強搜索策略v4.0")
    print("=" * 60)
    
    search_strategy = EnhancedSearchStrategyV4()
    
    # 測試不同類型的問題
    test_cases = [
        ("What is the current record/fact about entity_13?", "factual_search"),
        ("What is the specific value mentioned in research paper #40?", "academic_paper"),
        ("How to automate workflow process?", "automation"),
        ("Calculate the result of mathematical problem #1", "calculation"),
        ("Analyze and compare deep learning vs traditional ML", "complex_analysis"),
        ("What is artificial intelligence?", "simple_qa")
    ]
    
    results_summary = []
    
    for question, question_type in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 測試問題: {question}")
        
        results = search_strategy.execute_enhanced_search(question, question_type)
        
        if results:
            best_result = results[0]
            results_summary.append({
                "question_type": question_type,
                "best_tool": best_result.tool_name,
                "confidence": best_result.confidence,
                "service": best_result.service_type,
                "found_tools": len(results)
            })
        else:
            results_summary.append({
                "question_type": question_type,
                "best_tool": "none",
                "confidence": 0.0,
                "service": "none",
                "found_tools": 0
            })
    
    # 統計結果
    print(f"\n{'='*60}")
    print("📊 搜索策略測試總結:")
    
    avg_confidence = sum(r["confidence"] for r in results_summary) / len(results_summary)
    avg_tools_found = sum(r["found_tools"] for r in results_summary) / len(results_summary)
    success_rate = sum(1 for r in results_summary if r["confidence"] > 0.7) / len(results_summary)
    
    print(f"平均信心度: {avg_confidence:.2%}")
    print(f"平均發現工具數: {avg_tools_found:.1f}")
    print(f"高信心度匹配率: {success_rate:.1%} (信心度>70%)")
    
    # 按服務類型統計
    service_stats = {}
    for result in results_summary:
        service = result["service"]
        if service != "none":
            service_stats[service] = service_stats.get(service, 0) + 1
    
    print(f"服務分佈: {service_stats}")
    
    return results_summary

if __name__ == "__main__":
    test_enhanced_search_strategy()

