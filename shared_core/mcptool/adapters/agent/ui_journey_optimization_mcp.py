"""
用户界面旅程优化MCP模块

负责PPT智能体的用户界面交互和旅程优化
"""

import logging
from typing import Dict, Any, List, Optional

from mcptool.core.base_mcp import AgentOptimizationMCP

class UIJourneyOptimizationMCP(AgentOptimizationMCP):
    """用户界面旅程优化MCP，负责PPT智能体的用户界面交互和旅程优化"""
    
    def __init__(self):
        """初始化用户界面旅程优化MCP"""
        super().__init__(
            mcp_id="ui_journey_optimization",
            name="用户界面旅程优化MCP",
            description="负责PPT智能体的用户界面交互和旅程优化"
        )
        
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户界面旅程优化
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        ui_action = input_data.get("ui_action")
        
        if not ui_action:
            return {"status": "error", "message": "缺少ui_action参数"}
            
        if ui_action == "get_template_selection_ui":
            return self._get_template_selection_ui(input_data, context)
        elif ui_action == "get_content_input_ui":
            return self._get_content_input_ui(input_data, context)
        elif ui_action == "get_preview_ui":
            return self._get_preview_ui(input_data, context)
        elif ui_action == "get_export_options_ui":
            return self._get_export_options_ui(input_data, context)
        else:
            return {"status": "error", "message": f"不支持的UI操作: {ui_action}"}
    
    def _get_template_selection_ui(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取模板选择界面
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            界面数据字典
        """
        templates = input_data.get("templates", [])
        selected_template = input_data.get("selected_template")
        
        # 构建模板选择界面数据
        ui_data = {
            "component": "template_selection",
            "title": "选择PPT模板",
            "description": "请选择一个适合您需求的PPT模板",
            "templates": templates,
            "selected_template": selected_template,
            "actions": [
                {
                    "type": "button",
                    "label": "下一步",
                    "action": "next",
                    "disabled": not selected_template
                },
                {
                    "type": "button",
                    "label": "取消",
                    "action": "cancel",
                    "variant": "secondary"
                }
            ]
        }
        
        return {
            "status": "success",
            "ui_data": ui_data
        }
    
    def _get_content_input_ui(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取内容输入界面
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            界面数据字典
        """
        input_type = input_data.get("input_type", "text")
        title = input_data.get("title", "")
        content = input_data.get("content", "")
        
        # 构建内容输入界面数据
        ui_data = {
            "component": "content_input",
            "title": "输入PPT内容",
            "description": "请输入您的PPT标题和内容",
            "fields": [
                {
                    "type": "text",
                    "label": "演示文稿标题",
                    "value": title,
                    "placeholder": "请输入标题",
                    "required": True
                }
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "生成PPT",
                    "action": "generate",
                    "disabled": not title
                },
                {
                    "type": "button",
                    "label": "返回",
                    "action": "back",
                    "variant": "secondary"
                }
            ]
        }
        
        # 根据输入类型添加不同的内容输入字段
        if input_type == "text":
            ui_data["fields"].append({
                "type": "textarea",
                "label": "演示文稿内容",
                "value": content,
                "placeholder": "请输入内容，使用#开头的行作为幻灯片标题",
                "rows": 10,
                "required": True
            })
        elif input_type == "mindmap":
            ui_data["fields"].append({
                "type": "mindmap_editor",
                "label": "思维导图",
                "value": content,
                "placeholder": "请创建思维导图",
                "required": True
            })
        elif input_type == "upload":
            ui_data["fields"].append({
                "type": "file_upload",
                "label": "上传文件",
                "accept": ".txt,.md,.docx,.pdf",
                "required": True
            })
        
        return {
            "status": "success",
            "ui_data": ui_data
        }
    
    def _get_preview_ui(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取预览界面
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            界面数据字典
        """
        ppt_path = input_data.get("ppt_path", "")
        slides = input_data.get("slides", [])
        
        # 构建预览界面数据
        ui_data = {
            "component": "preview",
            "title": "预览PPT",
            "description": "您的PPT已生成，请预览并确认",
            "ppt_path": ppt_path,
            "slides": slides,
            "actions": [
                {
                    "type": "button",
                    "label": "导出",
                    "action": "export"
                },
                {
                    "type": "button",
                    "label": "修改",
                    "action": "edit",
                    "variant": "secondary"
                }
            ]
        }
        
        return {
            "status": "success",
            "ui_data": ui_data
        }
    
    def _get_export_options_ui(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取导出选项界面
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            界面数据字典
        """
        ppt_path = input_data.get("ppt_path", "")
        
        # 构建导出选项界面数据
        ui_data = {
            "component": "export_options",
            "title": "导出PPT",
            "description": "请选择导出选项",
            "ppt_path": ppt_path,
            "options": [
                {
                    "type": "radio",
                    "label": "导出格式",
                    "options": [
                        {"value": "pptx", "label": "PowerPoint (.pptx)"},
                        {"value": "pdf", "label": "PDF (.pdf)"},
                        {"value": "png", "label": "图片 (.png)"}
                    ],
                    "default": "pptx"
                }
            ],
            "actions": [
                {
                    "type": "button",
                    "label": "下载",
                    "action": "download"
                },
                {
                    "type": "button",
                    "label": "返回",
                    "action": "back",
                    "variant": "secondary"
                }
            ]
        }
        
        return {
            "status": "success",
            "ui_data": ui_data
        }
