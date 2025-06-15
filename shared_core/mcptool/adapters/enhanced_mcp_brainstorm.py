"""
增强版MCP头脑风暴器 - 集成Playwright自动化能力
该模块扩展了原有的MCP头脑风暴器，添加了信息获取、验证反馈和交互式探索能力。
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional

# 导入原有MCP头脑风暴器 - 调整导入路径以适应主仓库结构
from agents.ppt_agent.core.mcp.mcp_brainstorm import MCPCentralCoordinator
# 导入Playwright适配器 - 调整导入路径以适应主仓库结构
from agents.ppt_agent.core.mcp.playwright_adapter import PlaywrightAdapter
# 导入WebAgentB适配器 - 调整导入路径以适应主仓库结构
from agents.ppt_agent.core.mcp.webagent_adapter import WebAgentBAdapter

class EnhancedMCPBrainstorm:
    """增强版MCP头脑风暴器，集成Playwright自动化能力"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化增强版MCP头脑风暴器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 初始化原有头脑风暴器
        self.original_brainstorm = MCPCentralCoordinator(config_path)
        # 初始化Playwright适配器
        self.playwright = PlaywrightAdapter()
        # 初始化WebAgentB适配器
        self.webagent = WebAgentBAdapter()
        # 初始化日志
        self.logger = logging.getLogger("EnhancedMCPBrainstorm")
        
        self.logger.info("增强版MCP头脑风暴器初始化完成")
    
    def generate(self, topic: str, context: Optional[Dict] = None) -> Dict:
        """
        生成创意和方案
        
        Args:
            topic: 主题
            context: 上下文信息
            
        Returns:
            Dict: 生成的创意和方案
        """
        self.logger.info(f"开始头脑风暴: {topic}")
        
        # 使用WebAgentB收集相关信息
        search_results = self.webagent.enhanced_search(topic, depth=2)
        
        # 访问并提取关键页面内容
        page_contents = []
        for result in search_results[:3]:  # 限制处理前3个结果
            content = self.webagent.semantic_extract(result["url"])
            if content:
                page_contents.append(content)
        
        # 扩充上下文
        enhanced_context = context or {}
        enhanced_context.update({
            "search_results": search_results,
            "page_contents": page_contents
        })
        
        # 使用原始头脑风暴器生成创意
        brainstorm_task = f"基于以下信息，对'{topic}'进行头脑风暴: {json.dumps(enhanced_context, ensure_ascii=False)}"
        ideas = self.original_brainstorm.execute_task(brainstorm_task)
        
        # 提取和结构化创意
        structured_ideas = self._structure_ideas(ideas)
        
        # 使用Playwright验证创意可行性
        validated_ideas = []
        for idea in structured_ideas:
            validation_result = self.playwright.validate_idea(idea)
            validated_ideas.append({
                "idea": idea,
                "validation": validation_result
            })
        
        return {
            "topic": topic,
            "context": enhanced_context,
            "raw_ideas": ideas,
            "structured_ideas": structured_ideas,
            "validated_ideas": validated_ideas
        }
    
    def _structure_ideas(self, raw_ideas: Dict) -> List[Dict]:
        """将原始创意结构化"""
        # 这里假设raw_ideas中包含创意列表
        if isinstance(raw_ideas, dict) and "ideas" in raw_ideas:
            return raw_ideas["ideas"]
        
        # 如果没有明确的结构，尝试解析文本
        structured_ideas = []
        
        if isinstance(raw_ideas, dict) and "content" in raw_ideas:
            content = raw_ideas["content"]
        elif isinstance(raw_ideas, str):
            content = raw_ideas
        else:
            content = str(raw_ideas)
        
        # 简单的解析逻辑，实际应用中可能需要更复杂的处理
        ideas_text = content.split("\n\n")
        for i, idea_text in enumerate(ideas_text):
            if idea_text.strip():
                structured_ideas.append({
                    "id": f"idea_{i+1}",
                    "content": idea_text.strip(),
                    "source": "brainstorm"
                })
        
        return structured_ideas
    
    def explore_idea(self, idea: Dict) -> Dict:
        """
        交互式探索创意
        
        Args:
            idea: 创意信息
            
        Returns:
            Dict: 探索结果
        """
        self.logger.info(f"交互式探索创意: {idea.get('id', 'unknown')}")
        
        # 使用WebAgentB进行交互式探索
        exploration_result = self.webagent.interactive_task(
            "https://example.com", 
            f"探索创意: {idea['content']}"
        )
        
        # 基于探索结果优化创意
        optimized_idea = self.original_brainstorm.execute_task(
            f"基于以下探索结果，优化创意: {json.dumps(exploration_result, ensure_ascii=False)}"
        )
        
        return {
            "original_idea": idea,
            "exploration_result": exploration_result,
            "optimized_idea": optimized_idea
        }
    
    def visualize_idea(self, idea: Dict) -> Dict:
        """
        可视化创意
        
        Args:
            idea: 创意信息
            
        Returns:
            Dict: 可视化结果
        """
        self.logger.info(f"可视化创意: {idea.get('id', 'unknown')}")
        
        # 使用Playwright截取相关页面截图
        screenshots = []
        
        # 搜索相关图片
        search_results = self.webagent.enhanced_search(f"{idea['content']} visualization", depth=1)
        
        for result in search_results[:2]:  # 限制处理前2个结果
            screenshot_path = self.playwright.take_screenshot(result["url"])
            if screenshot_path:
                screenshots.append({
                    "url": result["url"],
                    "path": screenshot_path
                })
        
        return {
            "idea": idea,
            "screenshots": screenshots
        }
