#!/usr/bin/env python3
"""
思維上下文匹配優化MCP模塊

負責智能體的思維上下文匹配和優化
"""

import logging
from typing import Dict, Any, List, Optional

from mcptool.core.base_mcp import AgentOptimizationMCP

class ContextMatchingOptimizationMCP(AgentOptimizationMCP):
    """思維上下文匹配優化MCP，負責智能體的思維上下文匹配和優化"""
    
    def __init__(self):
        """初始化思維上下文匹配優化MCP"""
        super().__init__(
            mcp_id="context_matching_optimization",
            name="思維上下文匹配優化MCP",
            optimization_type="context_matching"
        )
        
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理思维上下文匹配优化
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        context_action = input_data.get("context_action")
        
        if not context_action:
            return {"status": "error", "message": "缺少context_action参数"}
            
        if context_action == "analyze_context":
            return self._analyze_context(input_data, context)
        elif context_action == "match_templates":
            return self._match_templates(input_data, context)
        elif context_action == "optimize_content":
            return self._optimize_content(input_data, context)
        elif context_action == "extract_keywords":
            return self._extract_keywords(input_data, context)
        else:
            return {"status": "error", "message": f"不支持的上下文操作: {context_action}"}
    
    def _analyze_context(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析思维上下文
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            分析结果字典
        """
        content = input_data.get("content", "")
        context_type = input_data.get("context_type", "general")
        
        if not content:
            return {"status": "error", "message": "缺少content参数"}
        
        # 分析内容的上下文特征
        context_features = self._extract_context_features(content, context_type)
        
        return {
            "status": "success",
            "context_features": context_features
        }
    
    def _match_templates(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        匹配适合的模板
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            匹配结果字典
        """
        content = input_data.get("content", "")
        context_features = input_data.get("context_features")
        
        if not content and not context_features:
            return {"status": "error", "message": "缺少content或context_features参数"}
        
        # 如果没有提供上下文特征，先进行分析
        if not context_features:
            context_features = self._extract_context_features(content, "general")
        
        # 匹配适合的模板
        matched_templates = self._find_matching_templates(context_features)
        
        return {
            "status": "success",
            "matched_templates": matched_templates
        }
    
    def _optimize_content(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        根据上下文优化内容
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            优化结果字典
        """
        content = input_data.get("content", "")
        context_features = input_data.get("context_features")
        template_id = input_data.get("template_id")
        
        if not content:
            return {"status": "error", "message": "缺少content参数"}
        
        # 如果没有提供上下文特征，先进行分析
        if not context_features:
            context_features = self._extract_context_features(content, "general")
        
        # 优化内容
        optimized_content = self._optimize_content_with_context(content, context_features, template_id)
        
        return {
            "status": "success",
            "optimized_content": optimized_content
        }
    
    def _extract_keywords(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        从内容中提取关键词
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            关键词结果字典
        """
        content = input_data.get("content", "")
        max_keywords = input_data.get("max_keywords", 10)
        
        if not content:
            return {"status": "error", "message": "缺少content参数"}
        
        # 提取关键词
        keywords = self._extract_content_keywords(content, max_keywords)
        
        return {
            "status": "success",
            "keywords": keywords
        }
    
    def _extract_context_features(self, content: str, context_type: str) -> Dict[str, Any]:
        """
        提取内容的上下文特征
        
        参数:
            content: 内容文本
            context_type: 上下文类型
            
        返回:
            上下文特征字典
        """
        # 简单的上下文特征提取逻辑
        words = content.lower().split()
        total_words = len(words)
        
        # 计算行业相关词汇频率
        industry_keywords = {
            "technology": ["技术", "创新", "数字", "智能", "软件", "硬件", "算法", "数据", "云计算", "人工智能"],
            "finance": ["金融", "投资", "资产", "股票", "基金", "银行", "保险", "风险", "收益", "市场"],
            "education": ["教育", "学习", "培训", "课程", "学生", "教师", "知识", "技能", "学校", "教学"],
            "healthcare": ["健康", "医疗", "患者", "治疗", "诊断", "医院", "医生", "药物", "疾病", "护理"],
            "marketing": ["营销", "品牌", "广告", "市场", "客户", "消费者", "销售", "推广", "策略", "渠道"]
        }
        
        industry_scores = {}
        for industry, keywords in industry_keywords.items():
            count = sum(1 for word in words if any(keyword in word for keyword in keywords))
            industry_scores[industry] = count / total_words if total_words > 0 else 0
        
        # 确定主要行业
        primary_industry = max(industry_scores.items(), key=lambda x: x[1])[0] if industry_scores else "general"
        
        # 分析内容复杂度
        avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        avg_sentence_length = total_words / sentence_count if sentence_count > 0 else 0
        
        complexity = "high" if avg_sentence_length > 20 or avg_word_length > 5 else "medium" if avg_sentence_length > 10 else "low"
        
        # 分析内容目的
        purpose_keywords = {
            "informative": ["介绍", "说明", "描述", "解释", "分析", "总结"],
            "persuasive": ["说服", "推荐", "建议", "促进", "鼓励", "证明"],
            "educational": ["教育", "学习", "培训", "指导", "教学", "讲解"],
            "entertaining": ["娱乐", "有趣", "幽默", "故事", "轻松", "趣味"]
        }
        
        purpose_scores = {}
        for purpose, keywords in purpose_keywords.items():
            count = sum(1 for word in words if any(keyword in word for keyword in keywords))
            purpose_scores[purpose] = count / total_words if total_words > 0 else 0
        
        primary_purpose = max(purpose_scores.items(), key=lambda x: x[1])[0] if purpose_scores else "informative"
        
        # 返回上下文特征
        return {
            "industry": primary_industry,
            "complexity": complexity,
            "purpose": primary_purpose,
            "word_count": total_words,
            "sentence_count": sentence_count,
            "avg_word_length": avg_word_length,
            "avg_sentence_length": avg_sentence_length,
            "industry_scores": industry_scores,
            "purpose_scores": purpose_scores
        }
    
    def _find_matching_templates(self, context_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据上下文特征匹配适合的模板
        
        参数:
            context_features: 上下文特征字典
            
        返回:
            匹配的模板列表
        """
        industry = context_features.get("industry", "general")
        complexity = context_features.get("complexity", "medium")
        purpose = context_features.get("purpose", "informative")
        
        # 预定义的模板库
        templates = [
            {
                "id": "tech_presentation_high",
                "name": "高级技术演示模板",
                "industry": "technology",
                "complexity": "high",
                "purpose": "informative",
                "score": 0
            },
            {
                "id": "tech_pitch_medium",
                "name": "技术推介模板",
                "industry": "technology",
                "complexity": "medium",
                "purpose": "persuasive",
                "score": 0
            },
            {
                "id": "finance_report_high",
                "name": "高级财务报告模板",
                "industry": "finance",
                "complexity": "high",
                "purpose": "informative",
                "score": 0
            },
            {
                "id": "education_course_medium",
                "name": "教育课程模板",
                "industry": "education",
                "complexity": "medium",
                "purpose": "educational",
                "score": 0
            },
            {
                "id": "healthcare_presentation_medium",
                "name": "医疗演示模板",
                "industry": "healthcare",
                "complexity": "medium",
                "purpose": "informative",
                "score": 0
            },
            {
                "id": "marketing_pitch_low",
                "name": "营销推介模板",
                "industry": "marketing",
                "complexity": "low",
                "purpose": "persuasive",
                "score": 0
            },
            {
                "id": "general_presentation_medium",
                "name": "通用演示模板",
                "industry": "general",
                "complexity": "medium",
                "purpose": "informative",
                "score": 0
            }
        ]
        
        # 计算每个模板的匹配分数
        for template in templates:
            score = 0
            
            # 行业匹配
            if template["industry"] == industry:
                score += 3
            elif template["industry"] == "general":
                score += 1
                
            # 复杂度匹配
            if template["complexity"] == complexity:
                score += 2
            elif abs(["low", "medium", "high"].index(template["complexity"]) - ["low", "medium", "high"].index(complexity)) == 1:
                score += 1
                
            # 目的匹配
            if template["purpose"] == purpose:
                score += 2
                
            template["score"] = score
        
        # 按分数排序
        sorted_templates = sorted(templates, key=lambda x: x["score"], reverse=True)
        
        # 返回前3个最匹配的模板
        return sorted_templates[:3]
    
    def _optimize_content_with_context(self, content: str, context_features: Dict[str, Any], template_id: str = None) -> Dict[str, Any]:
        """
        根据上下文特征和模板优化内容
        
        参数:
            content: 原始内容
            context_features: 上下文特征字典
            template_id: 模板ID
            
        返回:
            优化后的内容字典
        """
        industry = context_features.get("industry", "general")
        complexity = context_features.get("complexity", "medium")
        purpose = context_features.get("purpose", "informative")
        
        # 提取关键词
        keywords = self._extract_content_keywords(content, 10)
        
        # 根据行业添加相关术语
        industry_terms = {
            "technology": ["创新技术", "数字化转型", "技术架构", "系统集成", "用户体验"],
            "finance": ["财务分析", "投资策略", "风险管理", "资产配置", "市场趋势"],
            "education": ["学习成果", "教学方法", "知识传递", "技能培养", "教育创新"],
            "healthcare": ["医疗服务", "患者护理", "健康管理", "临床研究", "医疗创新"],
            "marketing": ["品牌策略", "市场定位", "客户洞察", "营销渠道", "消费者行为"]
        }
        
        relevant_terms = industry_terms.get(industry, ["关键概念", "核心要点", "重要信息", "主要内容", "关键因素"])
        
        # 根据复杂度调整内容结构
        structure_suggestions = {
            "low": {
                "slides_count": "5-7张",
                "points_per_slide": "3-4个要点",
                "language": "简单直接的语言",
                "visuals": "大量图片和图表"
            },
            "medium": {
                "slides_count": "8-12张",
                "points_per_slide": "4-5个要点",
                "language": "平衡专业术语和通俗表达",
                "visuals": "适量的图片、图表和文字"
            },
            "high": {
                "slides_count": "12-20张",
                "points_per_slide": "5-7个要点",
                "language": "专业术语和深入分析",
                "visuals": "详细的图表、数据和文字说明"
            }
        }
        
        structure = structure_suggestions.get(complexity, structure_suggestions["medium"])
        
        # 根据目的提供内容建议
        purpose_suggestions = {
            "informative": "注重清晰的信息传递，使用事实和数据支持观点",
            "persuasive": "强调价值主张和好处，包含有力的号召性用语",
            "educational": "采用循序渐进的结构，包含示例和练习",
            "entertaining": "使用故事、幽默和互动元素增强趣味性"
        }
        
        content_suggestion = purpose_suggestions.get(purpose, purpose_suggestions["informative"])
        
        # 返回优化建议
        return {
            "original_content": content,
            "keywords": keywords,
            "relevant_terms": relevant_terms,
            "structure": structure,
            "content_suggestion": content_suggestion,
            "industry_focus": industry,
            "complexity_level": complexity,
            "primary_purpose": purpose
        }
    
    def _extract_content_keywords(self, content: str, max_keywords: int) -> List[str]:
        """
        从内容中提取关键词
        
        参数:
            content: 内容文本
            max_keywords: 最大关键词数量
            
        返回:
            关键词列表
        """
        # 简单的关键词提取逻辑
        # 在实际应用中，应该使用更复杂的NLP算法
        
        # 停用词列表
        stop_words = ["的", "了", "和", "是", "在", "我们", "可以", "这个", "那个", "一个", "有", "与", "为", "以", "及", "或", "等"]
        
        # 分词并过滤停用词
        words = [word for word in content.lower().split() if word not in stop_words and len(word) > 1]
        
        # 计算词频
        word_freq = {}
        for word in words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # 按频率排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前N个关键词
        return [word for word, freq in sorted_words[:max_keywords]]
