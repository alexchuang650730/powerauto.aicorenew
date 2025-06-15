"""
PowerAutomation 智慧路由MCP - 核心模块实现

版本: v1.0
创建时间: 2025-06-14
作者: PowerAutomation Team
"""

import asyncio
import json
import re
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """隐私级别枚举"""
    HIGH_SENSITIVE = "HIGH_SENSITIVE"
    MEDIUM_SENSITIVE = "MEDIUM_SENSITIVE"
    LOW_SENSITIVE = "LOW_SENSITIVE"


class RoutingStrategy(Enum):
    """路由策略枚举"""
    LOCAL_ONLY = "LOCAL_ONLY"
    LOCAL_PREFERRED = "LOCAL_PREFERRED"
    LOCAL_FORCED = "LOCAL_FORCED"
    CLOUD_DIRECT = "CLOUD_DIRECT"
    CLOUD_ANONYMIZED = "CLOUD_ANONYMIZED"
    HYBRID_PROCESSING = "HYBRID_PROCESSING"


class TaskComplexity(Enum):
    """任务复杂度枚举"""
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    COMPLEX = "COMPLEX"


class LocalCapability(Enum):
    """本地能力枚举"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class PrivacyAnalysisResult:
    """隐私分析结果"""
    privacy_level: PrivacyLevel
    confidence_score: float
    detected_patterns: List[Dict[str, Any]]
    rule_score: float
    ml_score: float
    recommendations: List[str]


@dataclass
class CapabilityAssessment:
    """能力评估结果"""
    task_type: str
    complexity: TaskComplexity
    capability_level: LocalCapability
    confidence: float
    estimated_quality: float
    processing_time_estimate: float


@dataclass
class RoutingDecision:
    """路由决策结果"""
    routing_strategy: RoutingStrategy
    confidence: float
    cost_impact: float
    privacy_score: float
    performance_estimate: float
    reasoning: str


@dataclass
class ExecutionResult:
    """执行结果"""
    result: str
    execution_time: float
    cost_estimate: float
    quality_score: float
    execution_location: str
    cost_savings: float
    error: Optional[str] = None


class AdvancedPrivacyClassifier:
    """高级隐私分类器"""
    
    def __init__(self):
        self.rule_patterns = {
            'CRITICAL_SECRETS': [
                r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)',
                r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?[\w@#$%^&*]+',
                r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
                r'(?i)mongodb://.*:.*@',
                r'(?i)mysql://.*:.*@',
                r'(?i)postgresql://.*:.*@'
            ],
            'PERSONAL_DATA': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
            ],
            'BUSINESS_LOGIC': [
                r'(?i)(proprietary|confidential|internal|trade[_-]?secret)',
                r'(?i)(business[_-]?logic|algorithm|formula)',
                r'(?i)(revenue|profit|cost|pricing|financial)'
            ]
        }
    
    def classify_content_privacy(self, content: str) -> PrivacyAnalysisResult:
        """分类内容隐私级别"""
        
        # 规则检测
        rule_score = 0
        detected_patterns = []
        
        for category, patterns in self.rule_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    detected_patterns.append({
                        'category': category,
                        'pattern': pattern,
                        'matches': len(matches),
                        'sample_matches': matches[:3]  # 只保留前3个匹配示例
                    })
                    if category == 'CRITICAL_SECRETS':
                        rule_score += 10
                    elif category == 'PERSONAL_DATA':
                        rule_score += 5
                    elif category == 'BUSINESS_LOGIC':
                        rule_score += 3
        
        # ML模型预测 (模拟实现)
        ml_score = self._simulate_ml_prediction(content)
        
        # 综合评分
        final_score = rule_score * 0.7 + ml_score * 0.3
        
        # 确定隐私级别
        if final_score >= 8 or any(p['category'] == 'CRITICAL_SECRETS' for p in detected_patterns):
            privacy_level = PrivacyLevel.HIGH_SENSITIVE
        elif final_score >= 3:
            privacy_level = PrivacyLevel.MEDIUM_SENSITIVE
        else:
            privacy_level = PrivacyLevel.LOW_SENSITIVE
        
        recommendations = self._generate_privacy_recommendations(privacy_level, detected_patterns)
        
        return PrivacyAnalysisResult(
            privacy_level=privacy_level,
            confidence_score=min(final_score / 10, 1.0),
            detected_patterns=detected_patterns,
            rule_score=rule_score,
            ml_score=ml_score,
            recommendations=recommendations
        )
    
    def _simulate_ml_prediction(self, content: str) -> float:
        """模拟ML模型预测 (实际实现中应该使用真实的ML模型)"""
        # 基于内容长度和关键词密度的简单启发式
        sensitive_keywords = ['secret', 'private', 'confidential', 'password', 'key', 'token']
        keyword_count = sum(1 for keyword in sensitive_keywords if keyword.lower() in content.lower())
        
        # 简单的评分逻辑
        content_length = len(content)
        keyword_density = keyword_count / max(content_length / 100, 1)
        
        return min(keyword_density * 5, 10)
    
    def _generate_privacy_recommendations(self, privacy_level: PrivacyLevel, patterns: List[Dict]) -> List[str]:
        """生成隐私保护建议"""
        recommendations = []
        
        if privacy_level == PrivacyLevel.HIGH_SENSITIVE:
            recommendations.extend([
                "强制本地处理，禁止上传到云端",
                "启用端到端加密存储",
                "定期清理本地缓存",
                "启用详细审计日志"
            ])
        
        if any(p['category'] == 'CRITICAL_SECRETS' for p in patterns):
            recommendations.extend([
                "立即移除或替换硬编码密钥",
                "使用环境变量或密钥管理服务",
                "启用密钥轮换机制"
            ])
        
        if any(p['category'] == 'PERSONAL_DATA' for p in patterns):
            recommendations.extend([
                "考虑数据脱敏处理",
                "确保符合GDPR/CCPA合规要求",
                "实施数据最小化原则"
            ])
        
        return recommendations


class LocalCapabilityAssessor:
    """本地能力评估器"""
    
    def __init__(self):
        self.capability_matrix = {
            'code_completion': {'complexity': TaskComplexity.SIMPLE, 'capability': 0.85},
            'syntax_checking': {'complexity': TaskComplexity.SIMPLE, 'capability': 0.95},
            'simple_refactoring': {'complexity': TaskComplexity.SIMPLE, 'capability': 0.80},
            'variable_naming': {'complexity': TaskComplexity.SIMPLE, 'capability': 0.90},
            'comment_generation': {'complexity': TaskComplexity.SIMPLE, 'capability': 0.75},
            'bug_detection': {'complexity': TaskComplexity.MEDIUM, 'capability': 0.70},
            'code_explanation': {'complexity': TaskComplexity.MEDIUM, 'capability': 0.65},
            'complex_generation': {'complexity': TaskComplexity.COMPLEX, 'capability': 0.40},
            'architecture_design': {'complexity': TaskComplexity.COMPLEX, 'capability': 0.30},
            'security_audit': {'complexity': TaskComplexity.COMPLEX, 'capability': 0.25}
        }
    
    def assess_local_capability(self, task_type: str) -> CapabilityAssessment:
        """评估本地处理能力"""
        
        task_info = self.capability_matrix.get(task_type, {
            'complexity': TaskComplexity.MEDIUM,
            'capability': 0.5
        })
        
        complexity = task_info['complexity']
        capability_score = task_info['capability']
        
        # 确定能力级别
        if capability_score >= 0.8:
            capability_level = LocalCapability.HIGH
        elif capability_score >= 0.6:
            capability_level = LocalCapability.MEDIUM
        else:
            capability_level = LocalCapability.LOW
        
        # 估算处理时间 (秒)
        base_time = {
            TaskComplexity.SIMPLE: 2.0,
            TaskComplexity.MEDIUM: 5.0,
            TaskComplexity.COMPLEX: 15.0
        }
        
        processing_time = base_time[complexity] * (2 - capability_score)
        
        return CapabilityAssessment(
            task_type=task_type,
            complexity=complexity,
            capability_level=capability_level,
            confidence=capability_score,
            estimated_quality=capability_score,
            processing_time_estimate=processing_time
        )


class CostOptimizationEngine:
    """成本优化引擎"""
    
    def __init__(self):
        self.cost_model = {
            'LOCAL_PROCESSING': {
                'fixed_cost_per_month': 202.67,  # 硬件+电力
                'variable_cost_per_token': 0.0,  # 本地无token成本
                'setup_cost': 500.0  # 初始硬件投资
            },
            'CLOUD_PROCESSING': {
                'fixed_cost_per_month': 0.0,
                'variable_cost_per_token': 0.000015,  # Claude 3 Sonnet价格
                'setup_cost': 0.0
            }
        }
        
        self.task_token_estimates = {
            'code_completion': 150,
            'syntax_checking': 50,
            'simple_refactoring': 200,
            'variable_naming': 80,
            'comment_generation': 120,
            'bug_detection': 300,
            'code_explanation': 250,
            'complex_generation': 800,
            'architecture_design': 1200,
            'security_audit': 600
        }
    
    def calculate_cost_impact(self, routing_strategy: RoutingStrategy, task_type: str) -> float:
        """计算成本影响"""
        
        estimated_tokens = self.task_token_estimates.get(task_type, 200)
        
        if routing_strategy in [RoutingStrategy.LOCAL_ONLY, RoutingStrategy.LOCAL_PREFERRED, RoutingStrategy.LOCAL_FORCED]:
            # 本地处理成本 (仅电力成本，忽略固定成本摊销)
            return 0.001  # 极低的电力成本
        elif routing_strategy == RoutingStrategy.CLOUD_DIRECT:
            # 云端处理成本
            return estimated_tokens * self.cost_model['CLOUD_PROCESSING']['variable_cost_per_token']
        elif routing_strategy == RoutingStrategy.CLOUD_ANONYMIZED:
            # 云端处理成本 + 脱敏处理开销
            base_cost = estimated_tokens * self.cost_model['CLOUD_PROCESSING']['variable_cost_per_token']
            return base_cost * 1.1  # 10%的脱敏开销
        else:  # HYBRID_PROCESSING
            # 混合处理成本
            local_portion = 0.7
            cloud_portion = 0.3
            local_cost = 0.001
            cloud_cost = estimated_tokens * cloud_portion * self.cost_model['CLOUD_PROCESSING']['variable_cost_per_token']
            return local_cost + cloud_cost
    
    def calculate_savings(self, routing_strategy: RoutingStrategy, task_type: str) -> float:
        """计算成本节省"""
        
        # 基准成本 (全云端处理)
        baseline_cost = self.calculate_cost_impact(RoutingStrategy.CLOUD_DIRECT, task_type)
        
        # 实际成本
        actual_cost = self.calculate_cost_impact(routing_strategy, task_type)
        
        # 节省金额
        savings = baseline_cost - actual_cost
        
        # 节省百分比
        savings_percentage = (savings / baseline_cost * 100) if baseline_cost > 0 else 0
        
        return savings_percentage


class SmartRoutingDecision:
    """智能路由决策器"""
    
    def __init__(self):
        self.decision_matrix = {
            # 隐私级别 × 任务复杂度 × 本地能力 → 路由策略
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.HIGH): RoutingStrategy.LOCAL_ONLY,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.MEDIUM): RoutingStrategy.LOCAL_ONLY,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.LOW): RoutingStrategy.LOCAL_FORCED,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.HIGH): RoutingStrategy.LOCAL_ONLY,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.MEDIUM): RoutingStrategy.LOCAL_FORCED,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.LOW): RoutingStrategy.LOCAL_FORCED,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.HIGH): RoutingStrategy.LOCAL_ONLY,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.MEDIUM): RoutingStrategy.LOCAL_FORCED,
            (PrivacyLevel.HIGH_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.LOW): RoutingStrategy.LOCAL_FORCED,
            
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.HIGH): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.MEDIUM): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.LOW): RoutingStrategy.CLOUD_ANONYMIZED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.HIGH): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.MEDIUM): RoutingStrategy.CLOUD_ANONYMIZED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.LOW): RoutingStrategy.CLOUD_ANONYMIZED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.HIGH): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.MEDIUM): RoutingStrategy.CLOUD_ANONYMIZED,
            (PrivacyLevel.MEDIUM_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.LOW): RoutingStrategy.CLOUD_ANONYMIZED,
            
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.HIGH): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.MEDIUM): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.SIMPLE, LocalCapability.LOW): RoutingStrategy.CLOUD_DIRECT,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.HIGH): RoutingStrategy.LOCAL_PREFERRED,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.MEDIUM): RoutingStrategy.CLOUD_DIRECT,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.MEDIUM, LocalCapability.LOW): RoutingStrategy.CLOUD_DIRECT,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.HIGH): RoutingStrategy.HYBRID_PROCESSING,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.MEDIUM): RoutingStrategy.CLOUD_DIRECT,
            (PrivacyLevel.LOW_SENSITIVE, TaskComplexity.COMPLEX, LocalCapability.LOW): RoutingStrategy.CLOUD_DIRECT,
        }
        
        self.cost_optimizer = CostOptimizationEngine()
    
    def make_routing_decision(self, privacy_level: PrivacyLevel, task_complexity: TaskComplexity, 
                            local_capability: LocalCapability, task_type: str,
                            cost_priority: float = 0.5) -> RoutingDecision:
        """制定路由决策"""
        
        # 基础决策
        base_decision = self.decision_matrix.get(
            (privacy_level, task_complexity, local_capability), 
            RoutingStrategy.CLOUD_DIRECT
        )
        
        # 成本优化调整
        if cost_priority > 0.7 and base_decision in [RoutingStrategy.CLOUD_DIRECT, RoutingStrategy.CLOUD_ANONYMIZED]:
            if local_capability in [LocalCapability.HIGH, LocalCapability.MEDIUM]:
                base_decision = RoutingStrategy.LOCAL_PREFERRED
        
        # 性能优化调整
        if task_complexity == TaskComplexity.SIMPLE and local_capability == LocalCapability.HIGH:
            if base_decision not in [RoutingStrategy.LOCAL_ONLY, RoutingStrategy.LOCAL_FORCED]:
                base_decision = RoutingStrategy.LOCAL_PREFERRED
        
        # 计算各项指标
        confidence = self._calculate_confidence(privacy_level, task_complexity, local_capability)
        cost_impact = self.cost_optimizer.calculate_cost_impact(base_decision, task_type)
        privacy_score = self._calculate_privacy_score(base_decision, privacy_level)
        performance_estimate = self._estimate_performance(base_decision, task_complexity)
        reasoning = self._generate_reasoning(base_decision, privacy_level, task_complexity, local_capability)
        
        return RoutingDecision(
            routing_strategy=base_decision,
            confidence=confidence,
            cost_impact=cost_impact,
            privacy_score=privacy_score,
            performance_estimate=performance_estimate,
            reasoning=reasoning
        )
    
    def _calculate_confidence(self, privacy_level: PrivacyLevel, task_complexity: TaskComplexity, 
                            local_capability: LocalCapability) -> float:
        """计算决策置信度"""
        
        # 基于隐私级别的置信度
        privacy_confidence = {
            PrivacyLevel.HIGH_SENSITIVE: 0.9,  # 高隐私要求决策明确
            PrivacyLevel.MEDIUM_SENSITIVE: 0.7,
            PrivacyLevel.LOW_SENSITIVE: 0.8
        }
        
        # 基于能力匹配的置信度
        capability_confidence = {
            LocalCapability.HIGH: 0.9,
            LocalCapability.MEDIUM: 0.7,
            LocalCapability.LOW: 0.5
        }
        
        # 基于任务复杂度的置信度
        complexity_confidence = {
            TaskComplexity.SIMPLE: 0.9,
            TaskComplexity.MEDIUM: 0.7,
            TaskComplexity.COMPLEX: 0.6
        }
        
        # 综合置信度
        confidence = (
            privacy_confidence[privacy_level] * 0.4 +
            capability_confidence[local_capability] * 0.4 +
            complexity_confidence[task_complexity] * 0.2
        )
        
        return confidence
    
    def _calculate_privacy_score(self, routing_strategy: RoutingStrategy, privacy_level: PrivacyLevel) -> float:
        """计算隐私保护评分"""
        
        # 路由策略的隐私保护评分
        strategy_scores = {
            RoutingStrategy.LOCAL_ONLY: 1.0,
            RoutingStrategy.LOCAL_FORCED: 1.0,
            RoutingStrategy.LOCAL_PREFERRED: 0.9,
            RoutingStrategy.CLOUD_ANONYMIZED: 0.7,
            RoutingStrategy.HYBRID_PROCESSING: 0.6,
            RoutingStrategy.CLOUD_DIRECT: 0.3
        }
        
        base_score = strategy_scores.get(routing_strategy, 0.5)
        
        # 根据隐私级别调整
        if privacy_level == PrivacyLevel.HIGH_SENSITIVE:
            if routing_strategy not in [RoutingStrategy.LOCAL_ONLY, RoutingStrategy.LOCAL_FORCED]:
                base_score *= 0.5  # 高隐私数据不应该上云
        
        return base_score
    
    def _estimate_performance(self, routing_strategy: RoutingStrategy, task_complexity: TaskComplexity) -> float:
        """估算性能表现"""
        
        # 基础性能估算 (响应时间，秒)
        base_times = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MEDIUM: 3.0,
            TaskComplexity.COMPLEX: 10.0
        }
        
        # 路由策略的性能影响
        strategy_multipliers = {
            RoutingStrategy.LOCAL_ONLY: 0.5,      # 本地最快
            RoutingStrategy.LOCAL_PREFERRED: 0.6,
            RoutingStrategy.LOCAL_FORCED: 0.8,    # 可能质量不够需要重试
            RoutingStrategy.CLOUD_DIRECT: 2.0,    # 网络延迟
            RoutingStrategy.CLOUD_ANONYMIZED: 2.5, # 脱敏处理开销
            RoutingStrategy.HYBRID_PROCESSING: 1.5 # 混合处理
        }
        
        estimated_time = base_times[task_complexity] * strategy_multipliers.get(routing_strategy, 1.0)
        
        # 转换为性能评分 (时间越短评分越高)
        performance_score = max(0.1, 1.0 / (1.0 + estimated_time / 5.0))
        
        return performance_score
    
    def _generate_reasoning(self, routing_strategy: RoutingStrategy, privacy_level: PrivacyLevel,
                          task_complexity: TaskComplexity, local_capability: LocalCapability) -> str:
        """生成决策推理"""
        
        reasoning_parts = []
        
        # 隐私考虑
        if privacy_level == PrivacyLevel.HIGH_SENSITIVE:
            reasoning_parts.append("高敏感数据要求本地处理")
        elif privacy_level == PrivacyLevel.MEDIUM_SENSITIVE:
            reasoning_parts.append("中等敏感数据优先本地处理")
        else:
            reasoning_parts.append("低敏感数据可以云端处理")
        
        # 能力考虑
        if local_capability == LocalCapability.HIGH:
            reasoning_parts.append("本地具备高处理能力")
        elif local_capability == LocalCapability.MEDIUM:
            reasoning_parts.append("本地具备中等处理能力")
        else:
            reasoning_parts.append("本地处理能力有限")
        
        # 复杂度考虑
        if task_complexity == TaskComplexity.SIMPLE:
            reasoning_parts.append("任务复杂度较低")
        elif task_complexity == TaskComplexity.MEDIUM:
            reasoning_parts.append("任务复杂度中等")
        else:
            reasoning_parts.append("任务复杂度较高")
        
        # 策略说明
        strategy_explanations = {
            RoutingStrategy.LOCAL_ONLY: "选择本地独占处理",
            RoutingStrategy.LOCAL_PREFERRED: "优先本地处理",
            RoutingStrategy.LOCAL_FORCED: "强制本地处理(隐私要求)",
            RoutingStrategy.CLOUD_DIRECT: "直接云端处理",
            RoutingStrategy.CLOUD_ANONYMIZED: "脱敏后云端处理",
            RoutingStrategy.HYBRID_PROCESSING: "混合处理策略"
        }
        
        reasoning_parts.append(strategy_explanations.get(routing_strategy, "未知策略"))
        
        return "，".join(reasoning_parts)


class DataAnonymizer:
    """数据脱敏器"""
    
    def __init__(self):
        self.anonymization_cache = {}
    
    def anonymize_content(self, content: str) -> Tuple[str, Dict[str, str]]:
        """脱敏处理内容"""
        
        anonymized_content = content
        mapping = {}
        
        # 替换变量名
        var_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        variables = set(re.findall(var_pattern, content))
        
        # 保留关键字
        keywords = {'if', 'else', 'for', 'while', 'def', 'class', 'import', 'from', 'return', 'try', 'except'}
        
        for var in variables:
            if var not in keywords and len(var) > 2:
                anonymous_var = f"var_{uuid.uuid4().hex[:8]}"
                mapping[anonymous_var] = var
                anonymized_content = re.sub(rf'\b{re.escape(var)}\b', anonymous_var, anonymized_content)
        
        # 替换字符串常量
        string_pattern = r'["\']([^"\']*)["\']'
        strings = re.findall(string_pattern, content)
        
        for i, string_val in enumerate(strings):
            if len(string_val) > 3:  # 只替换较长的字符串
                anonymous_str = f"string_{i}"
                mapping[anonymous_str] = string_val
                anonymized_content = re.sub(
                    rf'["\']({re.escape(string_val)})["\']', 
                    f'"{anonymous_str}"', 
                    anonymized_content
                )
        
        return anonymized_content, mapping
    
    def restore_content(self, anonymized_content: str, mapping: Dict[str, str]) -> str:
        """恢复原始内容"""
        restored_content = anonymized_content
        
        # 按长度倒序替换，避免短字符串覆盖长字符串
        for anonymous, original in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            restored_content = restored_content.replace(anonymous, original)
        
        return restored_content


class RoutingMonitor:
    """路由监控器"""
    
    def __init__(self):
        self.routing_events = []
        self.metrics = {
            'total_requests': 0,
            'local_requests': 0,
            'cloud_requests': 0,
            'hybrid_requests': 0,
            'privacy_violations': 0,
            'total_cost_savings': 0.0,
            'average_response_time': 0.0
        }
    
    def record_routing_event(self, event: Dict[str, Any]):
        """记录路由事件"""
        
        event['timestamp'] = datetime.now().isoformat()
        self.routing_events.append(event)
        
        # 更新指标
        self.metrics['total_requests'] += 1
        
        routing_strategy = event.get('routing_strategy')
        if routing_strategy in ['LOCAL_ONLY', 'LOCAL_PREFERRED', 'LOCAL_FORCED']:
            self.metrics['local_requests'] += 1
        elif routing_strategy in ['CLOUD_DIRECT', 'CLOUD_ANONYMIZED']:
            self.metrics['cloud_requests'] += 1
        elif routing_strategy == 'HYBRID_PROCESSING':
            self.metrics['hybrid_requests'] += 1
        
        # 更新成本节省
        cost_savings = event.get('cost_savings', 0)
        self.metrics['total_cost_savings'] += cost_savings
        
        # 更新平均响应时间
        execution_time = event.get('execution_time', 0)
        total_time = self.metrics['average_response_time'] * (self.metrics['total_requests'] - 1)
        self.metrics['average_response_time'] = (total_time + execution_time) / self.metrics['total_requests']
        
        logger.info(f"路由事件记录: {event['request_id']} -> {routing_strategy}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        
        total = self.metrics['total_requests']
        if total == 0:
            return self.metrics
        
        return {
            **self.metrics,
            'local_processing_rate': self.metrics['local_requests'] / total,
            'cloud_processing_rate': self.metrics['cloud_requests'] / total,
            'hybrid_processing_rate': self.metrics['hybrid_requests'] / total,
            'average_cost_savings': self.metrics['total_cost_savings'] / total,
            'privacy_compliance_rate': 1 - (self.metrics['privacy_violations'] / total)
        }
    
    def generate_report(self) -> str:
        """生成监控报告"""
        
        summary = self.get_metrics_summary()
        
        report = f"""
智慧路由监控报告
================

总体统计:
- 总请求数: {summary['total_requests']}
- 本地处理率: {summary.get('local_processing_rate', 0):.1%}
- 云端处理率: {summary.get('cloud_processing_rate', 0):.1%}
- 混合处理率: {summary.get('hybrid_processing_rate', 0):.1%}

性能指标:
- 平均响应时间: {summary['average_response_time']:.2f}秒
- 隐私合规率: {summary.get('privacy_compliance_rate', 1):.1%}

成本效益:
- 总成本节省: ${summary['total_cost_savings']:.2f}
- 平均每请求节省: ${summary.get('average_cost_savings', 0):.4f}

最近事件: {len(self.routing_events[-10:])}条
"""
        
        return report


class SmartRoutingMCP:
    """智慧路由MCP主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # 初始化组件
        self.privacy_classifier = AdvancedPrivacyClassifier()
        self.capability_assessor = LocalCapabilityAssessor()
        self.route_decider = SmartRoutingDecision()
        self.data_anonymizer = DataAnonymizer()
        self.monitor = RoutingMonitor()
        
        logger.info("智慧路由MCP初始化完成")
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            'privacy_mode': 'strict',
            'cost_priority': 0.5,
            'local_processing_threshold': 0.7,
            'anonymization_enabled': True,
            'audit_logging': True
        }
    
    async def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """智能路由请求处理"""
        
        start_time = time.time()
        request_id = request.get('request_id', str(uuid.uuid4()))
        
        try:
            # 1. 提取请求信息
            content = request.get('content', '')
            task_type = request.get('task_type', 'unknown')
            user_preferences = request.get('preferences', {})
            
            logger.info(f"处理路由请求: {request_id}, 任务类型: {task_type}")
            
            # 2. 隐私分析
            privacy_analysis = self.privacy_classifier.classify_content_privacy(content)
            
            # 3. 能力评估
            capability_assessment = self.capability_assessor.assess_local_capability(task_type)
            
            # 4. 路由决策
            routing_decision = self.route_decider.make_routing_decision(
                privacy_level=privacy_analysis.privacy_level,
                task_complexity=capability_assessment.complexity,
                local_capability=capability_assessment.capability_level,
                task_type=task_type,
                cost_priority=user_preferences.get('cost_priority', self.config['cost_priority'])
            )
            
            # 5. 执行路由
            execution_result = await self._execute_routing(
                content=content,
                task_type=task_type,
                routing_decision=routing_decision,
                privacy_analysis=privacy_analysis
            )
            
            # 6. 记录监控事件
            execution_time = time.time() - start_time
            self.monitor.record_routing_event({
                'request_id': request_id,
                'task_type': task_type,
                'privacy_level': privacy_analysis.privacy_level.value,
                'routing_strategy': routing_decision.routing_strategy.value,
                'execution_time': execution_time,
                'cost_estimate': execution_result.cost_estimate,
                'quality_score': execution_result.quality_score,
                'cost_savings': execution_result.cost_savings
            })
            
            # 7. 构建响应
            response = {
                'result': execution_result.result,
                'routing_info': {
                    'strategy': routing_decision.routing_strategy.value,
                    'privacy_level': privacy_analysis.privacy_level.value,
                    'cost_savings': execution_result.cost_savings,
                    'execution_location': execution_result.execution_location,
                    'confidence': routing_decision.confidence,
                    'reasoning': routing_decision.reasoning
                },
                'performance_metrics': {
                    'execution_time': execution_time,
                    'quality_score': execution_result.quality_score,
                    'cost_estimate': execution_result.cost_estimate
                },
                'privacy_analysis': {
                    'level': privacy_analysis.privacy_level.value,
                    'confidence': privacy_analysis.confidence_score,
                    'recommendations': privacy_analysis.recommendations
                },
                'request_id': request_id
            }
            
            logger.info(f"路由请求完成: {request_id}, 策略: {routing_decision.routing_strategy.value}")
            return response
            
        except Exception as e:
            logger.error(f"路由请求失败: {request_id}, 错误: {str(e)}")
            
            # 记录错误事件
            execution_time = time.time() - start_time
            self.monitor.record_routing_event({
                'request_id': request_id,
                'task_type': request.get('task_type', 'unknown'),
                'error': str(e),
                'execution_time': execution_time
            })
            
            return {
                'error': str(e),
                'request_id': request_id,
                'execution_time': execution_time
            }
    
    async def _execute_routing(self, content: str, task_type: str, 
                             routing_decision: RoutingDecision,
                             privacy_analysis: PrivacyAnalysisResult) -> ExecutionResult:
        """执行路由策略"""
        
        start_time = time.time()
        
        try:
            if routing_decision.routing_strategy in [RoutingStrategy.LOCAL_ONLY, RoutingStrategy.LOCAL_PREFERRED, RoutingStrategy.LOCAL_FORCED]:
                result = await self._process_locally(content, task_type)
                execution_location = "local"
                
            elif routing_decision.routing_strategy == RoutingStrategy.CLOUD_ANONYMIZED:
                # 脱敏处理
                anonymized_content, mapping = self.data_anonymizer.anonymize_content(content)
                cloud_result = await self._process_in_cloud(anonymized_content, task_type)
                result = self.data_anonymizer.restore_content(cloud_result, mapping)
                execution_location = "cloud_anonymized"
                
            elif routing_decision.routing_strategy == RoutingStrategy.CLOUD_DIRECT:
                result = await self._process_in_cloud(content, task_type)
                execution_location = "cloud"
                
            else:  # HYBRID_PROCESSING
                result = await self._process_hybrid(content, task_type)
                execution_location = "hybrid"
            
            execution_time = time.time() - start_time
            
            # 计算成本节省
            cost_optimizer = CostOptimizationEngine()
            cost_savings = cost_optimizer.calculate_savings(routing_decision.routing_strategy, task_type)
            
            return ExecutionResult(
                result=result,
                execution_time=execution_time,
                cost_estimate=routing_decision.cost_impact,
                quality_score=0.85,  # 模拟质量评分
                execution_location=execution_location,
                cost_savings=cost_savings
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"路由执行失败: {str(e)}")
            
            return ExecutionResult(
                result="",
                execution_time=execution_time,
                cost_estimate=0.0,
                quality_score=0.0,
                execution_location="error",
                cost_savings=0.0,
                error=str(e)
            )
    
    async def _process_locally(self, content: str, task_type: str) -> str:
        """本地处理"""
        # 模拟本地处理
        await asyncio.sleep(0.5)  # 模拟处理时间
        return f"本地处理结果: {task_type} - {content[:50]}..."
    
    async def _process_in_cloud(self, content: str, task_type: str) -> str:
        """云端处理"""
        # 模拟云端处理
        await asyncio.sleep(2.0)  # 模拟网络延迟和处理时间
        return f"云端处理结果: {task_type} - {content[:50]}..."
    
    async def _process_hybrid(self, content: str, task_type: str) -> str:
        """混合处理"""
        # 模拟混合处理
        local_result = await self._process_locally(content[:len(content)//2], task_type)
        cloud_result = await self._process_in_cloud(content[len(content)//2:], task_type)
        return f"混合处理结果: {local_result} + {cloud_result}"
    
    def get_monitoring_report(self) -> str:
        """获取监控报告"""
        return self.monitor.generate_report()
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标"""
        return self.monitor.get_metrics_summary()


# 导出主要类
__all__ = [
    'SmartRoutingMCP',
    'PrivacyLevel',
    'RoutingStrategy',
    'TaskComplexity',
    'LocalCapability',
    'PrivacyAnalysisResult',
    'CapabilityAssessment',
    'RoutingDecision',
    'ExecutionResult'
]


if __name__ == "__main__":
    # 测试代码
    async def test_smart_routing():
        """测试智慧路由功能"""
        
        # 创建智慧路由实例
        smart_router = SmartRoutingMCP()
        
        # 测试用例1: 高敏感代码
        test_request_1 = {
            'content': 'api_key = "sk-1234567890abcdef"\\npassword = "secret123"',
            'task_type': 'code_completion',
            'request_id': 'test-001'
        }
        
        print("测试用例1: 高敏感代码")
        result_1 = await smart_router.route_request(test_request_1)
        print(f"路由策略: {result_1['routing_info']['strategy']}")
        print(f"隐私级别: {result_1['routing_info']['privacy_level']}")
        print(f"推理: {result_1['routing_info']['reasoning']}")
        print()
        
        # 测试用例2: 普通代码
        test_request_2 = {
            'content': 'def hello_world():\\n    print("Hello, World!")',
            'task_type': 'syntax_checking',
            'request_id': 'test-002'
        }
        
        print("测试用例2: 普通代码")
        result_2 = await smart_router.route_request(test_request_2)
        print(f"路由策略: {result_2['routing_info']['strategy']}")
        print(f"隐私级别: {result_2['routing_info']['privacy_level']}")
        print(f"推理: {result_2['routing_info']['reasoning']}")
        print()
        
        # 测试用例3: 复杂架构设计
        test_request_3 = {
            'content': 'Design a microservices architecture for e-commerce platform',
            'task_type': 'architecture_design',
            'request_id': 'test-003'
        }
        
        print("测试用例3: 复杂架构设计")
        result_3 = await smart_router.route_request(test_request_3)
        print(f"路由策略: {result_3['routing_info']['strategy']}")
        print(f"隐私级别: {result_3['routing_info']['privacy_level']}")
        print(f"推理: {result_3['routing_info']['reasoning']}")
        print()
        
        # 打印监控报告
        print("监控报告:")
        print(smart_router.get_monitoring_report())
    
    # 运行测试
    asyncio.run(test_smart_routing())

