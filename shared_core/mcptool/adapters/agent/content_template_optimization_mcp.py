#!/usr/bin/env python3
"""
內容模板優化MCP模塊

負責智能體的內容模板優化和管理
"""

import os
import logging
from typing import Dict, Any, List, Optional

from mcptool.core.base_mcp import AgentOptimizationMCP

class ContentTemplateOptimizationMCP(AgentOptimizationMCP):
    """內容模板優化MCP，負責智能體的內容模板優化和管理"""
    
    def __init__(self):
        """初始化內容模板優化MCP"""
        super().__init__(
            mcp_id="content_template_optimization",
            name="內容模板優化MCP",
            optimization_type="content_template"
        )
        self.description = "負責智能體的內容模板優化和管理"
        
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理内容模板优化
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        template_action = input_data.get("template_action")
        
        if not template_action:
            return {"status": "error", "message": "缺少template_action参数"}
            
        if template_action == "get_template":
            return self._get_template(input_data, context)
        elif template_action == "list_templates":
            return self._list_templates(input_data, context)
        elif template_action == "create_template":
            return self._create_template(input_data, context)
        elif template_action == "update_template":
            return self._update_template(input_data, context)
        else:
            return {"status": "error", "message": f"不支持的模板操作: {template_action}"}
    
    def _get_template(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取内容模板
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            模板数据字典
        """
        template_id = input_data.get("template_id")
        template_type = input_data.get("template_type", "general")
        industry = input_data.get("industry")
        
        if not template_id and not template_type:
            return {"status": "error", "message": "缺少template_id或template_type参数"}
        
        # 根据模板类型获取预定义模板
        templates = self._get_predefined_templates(template_type, industry)
        
        if template_id:
            # 查找指定ID的模板
            template = next((t for t in templates if t.get("id") == template_id), None)
            if not template:
                return {"status": "error", "message": f"未找到ID为{template_id}的模板"}
            return {
                "status": "success",
                "template": template
            }
        else:
            # 返回指定类型的第一个模板
            if not templates:
                return {"status": "error", "message": f"未找到类型为{template_type}的模板"}
            return {
                "status": "success",
                "template": templates[0]
            }
    
    def _list_templates(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        列出内容模板
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            模板列表字典
        """
        template_type = input_data.get("template_type")
        industry = input_data.get("industry")
        
        # 获取模板列表
        templates = self._get_predefined_templates(template_type, industry)
        
        return {
            "status": "success",
            "templates": templates,
            "count": len(templates)
        }
    
    def _create_template(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建内容模板
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            创建结果字典
        """
        # 在实际应用中，这里应该将模板保存到数据库或文件系统
        # 本示例仅返回成功信息
        return {
            "status": "success",
            "message": "模板创建功能在当前版本中不可用，请使用预定义模板"
        }
    
    def _update_template(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        更新内容模板
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            更新结果字典
        """
        # 在实际应用中，这里应该更新数据库或文件系统中的模板
        # 本示例仅返回成功信息
        return {
            "status": "success",
            "message": "模板更新功能在当前版本中不可用，请使用预定义模板"
        }
    
    def _get_predefined_templates(self, template_type: str = None, industry: str = None) -> List[Dict[str, Any]]:
        """
        获取预定义的内容模板
        
        参数:
            template_type: 模板类型
            industry: 行业
            
        返回:
            模板列表
        """
        # 预定义的模板库
        all_templates = [
            # 商业计划书模板
            {
                "id": "business_plan_1",
                "name": "商业计划书模板",
                "type": "business_plan",
                "industry": "general",
                "structure": [
                    {"title": "封面", "content": "{{company_name}} - 商业计划书"},
                    {"title": "目录", "content": "自动生成目录"},
                    {"title": "执行摘要", "content": "简要概述公司、产品/服务、市场机会和财务预测"},
                    {"title": "公司介绍", "content": "公司愿景、使命、目标和核心价值观"},
                    {"title": "产品/服务", "content": "详细描述产品/服务、特点和优势"},
                    {"title": "市场分析", "content": "目标市场、市场规模、趋势和竞争分析"},
                    {"title": "营销策略", "content": "定价、推广、分销和销售策略"},
                    {"title": "运营计划", "content": "生产、供应链、设施和人员需求"},
                    {"title": "管理团队", "content": "核心团队成员及其经验和专长"},
                    {"title": "财务预测", "content": "收入预测、成本结构、盈利能力和资金需求"},
                    {"title": "风险分析", "content": "潜在风险和缓解策略"},
                    {"title": "实施时间表", "content": "关键里程碑和时间表"},
                    {"title": "总结", "content": "总结要点和下一步行动"}
                ]
            },
            # 项目提案模板
            {
                "id": "project_proposal_1",
                "name": "项目提案模板",
                "type": "project_proposal",
                "industry": "general",
                "structure": [
                    {"title": "封面", "content": "{{project_name}} - 项目提案"},
                    {"title": "目录", "content": "自动生成目录"},
                    {"title": "项目概述", "content": "项目背景、目标和预期成果"},
                    {"title": "问题陈述", "content": "当前问题和挑战的详细描述"},
                    {"title": "解决方案", "content": "提议的解决方案和方法"},
                    {"title": "项目范围", "content": "包含和排除的内容"},
                    {"title": "实施计划", "content": "阶段、任务和时间表"},
                    {"title": "资源需求", "content": "人员、设备、材料和预算"},
                    {"title": "风险管理", "content": "潜在风险和缓解策略"},
                    {"title": "评估方法", "content": "如何衡量项目成功"},
                    {"title": "团队介绍", "content": "项目团队成员及其角色"},
                    {"title": "总结", "content": "总结要点和建议的下一步行动"}
                ]
            },
            # 市场营销计划模板
            {
                "id": "marketing_plan_1",
                "name": "市场营销计划模板",
                "type": "marketing_plan",
                "industry": "general",
                "structure": [
                    {"title": "封面", "content": "{{company_name}} - 市场营销计划"},
                    {"title": "目录", "content": "自动生成目录"},
                    {"title": "执行摘要", "content": "营销计划的简要概述"},
                    {"title": "市场分析", "content": "市场规模、趋势和目标受众分析"},
                    {"title": "竞争分析", "content": "主要竞争对手及其优势和劣势"},
                    {"title": "SWOT分析", "content": "优势、劣势、机会和威胁分析"},
                    {"title": "营销目标", "content": "具体、可衡量、可实现、相关和有时限的目标"},
                    {"title": "营销策略", "content": "定位、差异化和价值主张"},
                    {"title": "营销组合", "content": "产品、价格、渠道和促销策略"},
                    {"title": "数字营销", "content": "网站、SEO、社交媒体和内容营销策略"},
                    {"title": "预算", "content": "营销活动的预算分配"},
                    {"title": "实施时间表", "content": "营销活动的时间表和里程碑"},
                    {"title": "评估指标", "content": "如何衡量营销成功"},
                    {"title": "总结", "content": "总结要点和下一步行动"}
                ]
            },
            # 教育培训模板
            {
                "id": "education_training_1",
                "name": "教育培训模板",
                "type": "education",
                "industry": "education",
                "structure": [
                    {"title": "封面", "content": "{{course_name}} - 培训课程"},
                    {"title": "目录", "content": "自动生成目录"},
                    {"title": "课程介绍", "content": "课程概述和学习目标"},
                    {"title": "课程大纲", "content": "主要模块和主题"},
                    {"title": "学习成果", "content": "完成课程后学员将获得的知识和技能"},
                    {"title": "模块1", "content": "模块1的详细内容和练习"},
                    {"title": "模块2", "content": "模块2的详细内容和练习"},
                    {"title": "模块3", "content": "模块3的详细内容和练习"},
                    {"title": "案例研究", "content": "实际应用案例"},
                    {"title": "实践活动", "content": "互动练习和活动"},
                    {"title": "评估方法", "content": "如何评估学员的学习成果"},
                    {"title": "资源和参考", "content": "推荐阅读和其他资源"},
                    {"title": "总结", "content": "课程总结和下一步学习建议"}
                ]
            },
            # 科技产品介绍模板
            {
                "id": "tech_product_1",
                "name": "科技产品介绍模板",
                "type": "product_presentation",
                "industry": "technology",
                "structure": [
                    {"title": "封面", "content": "{{product_name}} - 产品介绍"},
                    {"title": "目录", "content": "自动生成目录"},
                    {"title": "市场痛点", "content": "当前市场面临的问题和挑战"},
                    {"title": "产品概述", "content": "产品的简要介绍和价值主张"},
                    {"title": "核心功能", "content": "产品的主要功能和特点"},
                    {"title": "技术优势", "content": "产品的技术创新和优势"},
                    {"title": "用户体验", "content": "产品的用户界面和体验设计"},
                    {"title": "应用场景", "content": "产品的实际应用场景和案例"},
                    {"title": "客户证言", "content": "现有客户的反馈和评价"},
                    {"title": "竞争优势", "content": "与竞争产品的对比和优势"},
                    {"title": "路线图", "content": "产品的未来发展计划"},
                    {"title": "定价和套餐", "content": "产品的定价策略和套餐选项"},
                    {"title": "总结", "content": "总结产品价值和行动号召"}
                ]
            }
        ]
        
        # 根据条件筛选模板
        filtered_templates = all_templates
        
        if template_type:
            filtered_templates = [t for t in filtered_templates if t.get("type") == template_type]
            
        if industry:
            # 如果指定了行业，优先返回该行业的模板，如果没有则返回通用模板
            industry_templates = [t for t in filtered_templates if t.get("industry") == industry]
            if industry_templates:
                filtered_templates = industry_templates
            else:
                filtered_templates = [t for t in filtered_templates if t.get("industry") == "general"]
        
        return filtered_templates
