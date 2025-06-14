# powerauto.aicorenew/mcp/mcp_coordinator/dialog_classifier.py

import logging
import re
from typing import Dict, Any, Tuple
from enum import Enum

class DialogType(Enum):
    """对话类型枚举 - 基于"思考-观察确认-动作"三分类"""
    THINKING = "thinking"      # 思考类：需要深度分析、推理的复杂问题
    OBSERVING = "observing"    # 观察确认类：需要获取信息、验证状态的查询
    ACTION = "action"          # 动作类：需要直接执行操作的指令

class DialogClassifier:
    """
    对话分类器 - 实现"思考-观察确认-动作"三分类逻辑
    用于智能编辑器和Manus对话框的快速分类和建议生成
    """
    
    def __init__(self):
        self.logger = logging.getLogger("DialogClassifier")
        
        # 思考类关键词
        self.thinking_keywords = [
            "如何", "怎么", "为什么", "分析", "设计", "架构", "方案", "策略",
            "思考", "考虑", "评估", "比较", "优化", "改进", "建议", "推荐",
            "原理", "机制", "逻辑", "算法", "模式", "框架", "理念", "哲学"
        ]
        
        # 观察确认类关键词
        self.observing_keywords = [
            "查看", "检查", "确认", "验证", "测试", "状态", "信息", "数据",
            "显示", "列出", "获取", "读取", "监控", "观察", "发现", "找到",
            "是否", "有没有", "存在", "包含", "支持", "可以", "能否", "会不会"
        ]
        
        # 动作类关键词
        self.action_keywords = [
            "执行", "运行", "启动", "停止", "创建", "删除", "修改", "更新",
            "安装", "配置", "部署", "发布", "下载", "上传", "保存", "导出",
            "生成", "构建", "编译", "打包", "发送", "提交", "推送", "拉取"
        ]

    def classify_dialog(self, dialog_content: str, context: Dict[str, Any] = None) -> Tuple[DialogType, float, Dict[str, Any]]:
        """
        分类对话内容
        
        Args:
            dialog_content: 对话内容
            context: 上下文信息
            
        Returns:
            Tuple[DialogType, confidence_score, analysis_details]
        """
        self.logger.info(f"Classifying dialog: {dialog_content[:50]}...")
        
        # 预处理对话内容
        content_lower = dialog_content.lower()
        
        # 计算各类型的匹配分数
        thinking_score = self._calculate_keyword_score(content_lower, self.thinking_keywords)
        observing_score = self._calculate_keyword_score(content_lower, self.observing_keywords)
        action_score = self._calculate_keyword_score(content_lower, self.action_keywords)
        
        # 语法模式分析
        thinking_pattern_score = self._analyze_thinking_patterns(content_lower)
        observing_pattern_score = self._analyze_observing_patterns(content_lower)
        action_pattern_score = self._analyze_action_patterns(content_lower)
        
        # 综合评分
        final_thinking_score = thinking_score + thinking_pattern_score
        final_observing_score = observing_score + observing_pattern_score
        final_action_score = action_score + action_pattern_score
        
        # 确定最终分类
        scores = {
            DialogType.THINKING: final_thinking_score,
            DialogType.OBSERVING: final_observing_score,
            DialogType.ACTION: final_action_score
        }
        
        # 找到最高分的类型
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type] / (sum(scores.values()) + 0.001)  # 避免除零
        
        analysis_details = {
            "keyword_scores": {
                "thinking": thinking_score,
                "observing": observing_score,
                "action": action_score
            },
            "pattern_scores": {
                "thinking": thinking_pattern_score,
                "observing": observing_pattern_score,
                "action": action_pattern_score
            },
            "final_scores": scores,
            "content_length": len(dialog_content),
            "has_question_mark": "?" in dialog_content,
            "has_exclamation": "!" in dialog_content
        }
        
        self.logger.info(f"Classification result: {best_type.value} (confidence: {confidence:.2f})")
        return best_type, confidence, analysis_details

    def _calculate_keyword_score(self, content: str, keywords: list) -> float:
        """计算关键词匹配分数"""
        score = 0
        for keyword in keywords:
            if keyword in content:
                score += 1
        return score / len(keywords)  # 归一化

    def _analyze_thinking_patterns(self, content: str) -> float:
        """分析思考类语法模式"""
        patterns = [
            r'如何.*?',
            r'怎么.*?',
            r'为什么.*?',
            r'.*?的原理.*?',
            r'.*?的机制.*?',
            r'.*?比较.*?',
            r'.*?分析.*?',
            r'.*?设计.*?'
        ]
        return self._match_patterns(content, patterns)

    def _analyze_observing_patterns(self, content: str) -> float:
        """分析观察确认类语法模式"""
        patterns = [
            r'.*?状态.*?',
            r'.*?是否.*?',
            r'.*?有没有.*?',
            r'查看.*?',
            r'检查.*?',
            r'确认.*?',
            r'.*?信息.*?',
            r'.*?数据.*?'
        ]
        return self._match_patterns(content, patterns)

    def _analyze_action_patterns(self, content: str) -> float:
        """分析动作类语法模式"""
        patterns = [
            r'执行.*?',
            r'运行.*?',
            r'创建.*?',
            r'删除.*?',
            r'修改.*?',
            r'生成.*?',
            r'.*?开始.*?',
            r'.*?完成.*?'
        ]
        return self._match_patterns(content, patterns)

    def _match_patterns(self, content: str, patterns: list) -> float:
        """匹配语法模式"""
        matches = 0
        for pattern in patterns:
            if re.search(pattern, content):
                matches += 1
        return matches / len(patterns)  # 归一化

class OneStepSuggestionGenerator:
    """
    一步直达建议生成器
    基于对话分类结果生成相应的智能建议
    """
    
    def __init__(self):
        self.logger = logging.getLogger("OneStepSuggestionGenerator")
        self.classifier = DialogClassifier()

    def generate_suggestion(self, dialog_content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成一步直达建议
        
        Args:
            dialog_content: 对话内容
            context: 上下文信息
            
        Returns:
            Dict包含建议类型、具体建议、执行指令等
        """
        # 1. 分类对话
        dialog_type, confidence, analysis = self.classifier.classify_dialog(dialog_content, context)
        
        # 2. 根据分类生成建议
        if dialog_type == DialogType.THINKING:
            suggestion = self._generate_thinking_suggestion(dialog_content, context, analysis)
        elif dialog_type == DialogType.OBSERVING:
            suggestion = self._generate_observing_suggestion(dialog_content, context, analysis)
        elif dialog_type == DialogType.ACTION:
            suggestion = self._generate_action_suggestion(dialog_content, context, analysis)
        else:
            suggestion = self._generate_fallback_suggestion(dialog_content, context)
        
        # 3. 添加元数据
        suggestion.update({
            "dialog_type": dialog_type.value,
            "confidence": confidence,
            "analysis_details": analysis,
            "timestamp": time.time(),
            "source": context.get("source", "unknown") if context else "unknown"
        })
        
        self.logger.info(f"Generated {dialog_type.value} suggestion with confidence {confidence:.2f}")
        return suggestion

    def _generate_thinking_suggestion(self, content: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成思考类建议"""
        return {
            "suggestion_type": "thinking",
            "title": "深度分析建议",
            "primary_action": "启动AI分析引擎进行深度思考",
            "steps": [
                "调用多AI并行分析",
                "生成思考框架",
                "提供多角度解决方案",
                "输出结构化分析报告"
            ],
            "executable_command": {
                "action": "ai_deep_analysis",
                "params": {
                    "content": content,
                    "analysis_type": "comprehensive",
                    "output_format": "structured_report"
                }
            },
            "estimated_time": "2-5分钟",
            "complexity": "high"
        }

    def _generate_observing_suggestion(self, content: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成观察确认类建议"""
        return {
            "suggestion_type": "observing",
            "title": "信息查询建议",
            "primary_action": "执行智能信息收集和状态检查",
            "steps": [
                "识别查询目标",
                "选择最佳数据源",
                "执行信息收集",
                "格式化查询结果"
            ],
            "executable_command": {
                "action": "smart_query",
                "params": {
                    "query": content,
                    "sources": ["system_status", "database", "api", "logs"],
                    "format": "summary"
                }
            },
            "estimated_time": "30秒-2分钟",
            "complexity": "medium"
        }

    def _generate_action_suggestion(self, content: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成动作类建议"""
        return {
            "suggestion_type": "action",
            "title": "直接执行建议",
            "primary_action": "准备并执行指定操作",
            "steps": [
                "解析执行指令",
                "验证执行权限",
                "准备执行环境",
                "执行并监控结果"
            ],
            "executable_command": {
                "action": "direct_execution",
                "params": {
                    "command": content,
                    "safety_check": True,
                    "rollback_enabled": True
                }
            },
            "estimated_time": "即时-1分钟",
            "complexity": "low"
        }

    def _generate_fallback_suggestion(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成兜底建议"""
        return {
            "suggestion_type": "fallback",
            "title": "通用智能建议",
            "primary_action": "使用通用AI助手处理请求",
            "steps": [
                "内容预处理",
                "调用通用AI引擎",
                "生成初步建议",
                "用户确认执行"
            ],
            "executable_command": {
                "action": "general_ai_assist",
                "params": {
                    "content": content,
                    "mode": "adaptive"
                }
            },
            "estimated_time": "1-3分钟",
            "complexity": "medium"
        }

# 导入time模块
import time

