#!/usr/bin/env python3
"""
提示詞優化MCP模塊

負責智能體的提示詞優化和生成
"""

import logging
from typing import Dict, Any, List, Optional

from mcptool.core.base_mcp import AgentOptimizationMCP

class PromptOptimizationMCP(AgentOptimizationMCP):
    """提示詞優化MCP，負責智能體的提示詞優化和生成"""
    
    def __init__(self):
        """初始化提示詞優化MCP"""
        super().__init__(
            mcp_id="prompt_optimization",
            name="提示詞優化MCP",
            description="負責智能體的提示詞優化和生成"
        )
        
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理提示词优化
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        prompt_type = input_data.get("prompt_type")
        
        if not prompt_type:
            return {"status": "error", "message": "缺少prompt_type参数"}
            
        if prompt_type == "content_generation":
            return self._generate_content_prompt(input_data, context)
        elif prompt_type == "style_optimization":
            return self._generate_style_prompt(input_data, context)
        elif prompt_type == "structure_optimization":
            return self._generate_structure_prompt(input_data, context)
        else:
            return {"status": "error", "message": f"不支持的提示词类型: {prompt_type}"}
    
    def _generate_content_prompt(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成内容创建提示词
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            提示词结果字典
        """
        title = input_data.get("title", "")
        topic = input_data.get("topic", "")
        audience = input_data.get("audience", "通用")
        purpose = input_data.get("purpose", "信息展示")
        length = input_data.get("length", "中等")
        
        # 构建提示词模板
        prompt_template = """
        请为以下PPT创建高质量的内容:
        
        标题: {title}
        主题: {topic}
        目标受众: {audience}
        目的: {purpose}
        长度: {length}
        
        要求:
        1. 内容应该清晰、简洁、有吸引力
        2. 使用适合目标受众的语言和术语
        3. 包含引人入胜的开场和有力的结论
        4. 每张幻灯片应有明确的主题和要点
        5. 适当使用数据、案例和故事来支持观点
        
        请提供完整的PPT内容大纲，包括:
        - 封面幻灯片
        - 目录幻灯片
        - 主要内容幻灯片（每张包含标题和要点）
        - 总结幻灯片
        """
        
        # 填充提示词模板
        prompt = prompt_template.format(
            title=title,
            topic=topic,
            audience=audience,
            purpose=purpose,
            length=length
        )
        
        return {
            "status": "success",
            "prompt": prompt,
            "parameters": {
                "title": title,
                "topic": topic,
                "audience": audience,
                "purpose": purpose,
                "length": length
            }
        }
    
    def _generate_style_prompt(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成样式优化提示词
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            提示词结果字典
        """
        style = input_data.get("style", "专业")
        color_scheme = input_data.get("color_scheme", "蓝色")
        industry = input_data.get("industry", "通用")
        
        # 构建提示词模板
        prompt_template = """
        请为以下PPT优化视觉样式:
        
        风格: {style}
        配色方案: {color_scheme}
        行业: {industry}
        
        要求:
        1. 提供符合{style}风格的设计建议
        2. 推荐适合{industry}行业的视觉元素
        3. 基于{color_scheme}配色方案提供具体的颜色代码
        4. 建议适合的字体、图标和图片风格
        5. 提供幻灯片布局的最佳实践
        
        请提供详细的样式指南，包括:
        - 主色和辅助色的RGB/HEX值
        - 推荐的字体组合（标题和正文）
        - 幻灯片背景设计建议
        - 图表和图形的样式建议
        - 整体视觉一致性的技巧
        """
        
        # 填充提示词模板
        prompt = prompt_template.format(
            style=style,
            color_scheme=color_scheme,
            industry=industry
        )
        
        return {
            "status": "success",
            "prompt": prompt,
            "parameters": {
                "style": style,
                "color_scheme": color_scheme,
                "industry": industry
            }
        }
    
    def _generate_structure_prompt(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成结构优化提示词
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            提示词结果字典
        """
        presentation_type = input_data.get("presentation_type", "信息展示")
        duration = input_data.get("duration", "15分钟")
        complexity = input_data.get("complexity", "中等")
        
        # 构建提示词模板
        prompt_template = """
        请为以下PPT优化结构:
        
        演示类型: {presentation_type}
        时长: {duration}
        复杂度: {complexity}
        
        要求:
        1. 提供适合{presentation_type}类型的最佳结构
        2. 考虑{duration}的时间限制，优化幻灯片数量和内容密度
        3. 根据{complexity}复杂度调整内容深度和广度
        4. 确保逻辑流畅，层次分明
        5. 提供引人入胜的开场和有力的结束
        
        请提供详细的结构建议，包括:
        - 建议的幻灯片总数
        - 各部分的比例分配（开场、主体、结论）
        - 关键幻灯片的内容建议
        - 过渡和连接的技巧
        - 时间分配建议
        """
        
        # 填充提示词模板
        prompt = prompt_template.format(
            presentation_type=presentation_type,
            duration=duration,
            complexity=complexity
        )
        
        return {
            "status": "success",
            "prompt": prompt,
            "parameters": {
                "presentation_type": presentation_type,
                "duration": duration,
                "complexity": complexity
            }
        }
