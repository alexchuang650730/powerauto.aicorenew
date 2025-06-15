#!/usr/bin/env python3
"""
PowerAutomation 智慧路由系統

基於InteractionLogManager實現Token節省的端雲混合智慧路由，
整合隱私保護、成本優化和性能監控功能。
"""

import os
import json
import time
import hashlib
import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
import uuid

# 導入基礎組件
from interaction_log_manager import InteractionLogManager, InteractionType

class ProcessingLocation(Enum):
    """處理位置枚舉"""
    LOCAL_ONLY = "local_only"
    LOCAL_PREFERRED = "local_preferred"
    CLOUD_ALLOWED = "cloud_allowed"
    CLOUD_ANONYMIZED = "cloud_anonymized"
    HYBRID_PROCESSING = "hybrid_processing"

class PrivacySensitivity(Enum):
    """隱私敏感度枚舉"""
    HIGH_SENSITIVE = "high_sensitive"
    MEDIUM_SENSITIVE = "medium_sensitive"
    LOW_SENSITIVE = "low_sensitive"

class TaskComplexity(Enum):
    """任務複雜度枚舉"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ULTRA_COMPLEX = "ultra_complex"

@dataclass
class RoutingDecision:
    """路由決策結果"""
    processing_location: ProcessingLocation
    privacy_level: PrivacySensitivity
    task_complexity: TaskComplexity
    confidence_score: float
    estimated_cost: float
    estimated_tokens: int
    reasoning: str
    fallback_options: List[ProcessingLocation]

@dataclass
class CostMetrics:
    """成本指標"""
    cloud_tokens_used: int
    local_processing_time: float
    total_cost_usd: float
    cost_savings_usd: float
    privacy_compliance_score: float
    performance_score: float

class PrivacyClassifier:
    """隱私敏感度分類器"""
    
    def __init__(self):
        self.sensitive_patterns = {
            'api_keys': [
                r'api[_-]?key', r'secret[_-]?key', r'access[_-]?token',
                r'bearer\s+[a-zA-Z0-9]+', r'sk-[a-zA-Z0-9]+'
            ],
            'passwords': [
                r'password\s*[:=]\s*["\']?[^"\'\s]+',
                r'passwd\s*[:=]\s*["\']?[^"\'\s]+',
                r'pwd\s*[:=]\s*["\']?[^"\'\s]+'
            ],
            'personal_data': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # emails
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # phone numbers
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'  # credit cards
            ],
            'infrastructure': [
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP addresses
                r'mongodb://', r'mysql://', r'postgresql://',  # database URLs
                r'-----BEGIN.*PRIVATE KEY-----'  # private keys
            ],
            'business_secrets': [
                r'proprietary', r'confidential', r'trade\s+secret',
                r'internal\s+only', r'classified'
            ]
        }
        
    def classify_sensitivity(self, content: str) -> PrivacySensitivity:
        """分類內容隱私敏感度"""
        content_lower = content.lower()
        
        # 檢測高敏感內容
        high_sensitive_categories = ['api_keys', 'passwords', 'personal_data', 'infrastructure']
        for category in high_sensitive_categories:
            patterns = self.sensitive_patterns[category]
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return PrivacySensitivity.HIGH_SENSITIVE
        
        # 檢測中等敏感內容
        medium_sensitive_categories = ['business_secrets']
        for category in medium_sensitive_categories:
            patterns = self.sensitive_patterns[category]
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return PrivacySensitivity.MEDIUM_SENSITIVE
        
        # 檢測業務邏輯關鍵詞
        business_keywords = ['business', 'company', 'client', 'customer', 'revenue', 'profit']
        if any(keyword in content_lower for keyword in business_keywords):
            return PrivacySensitivity.MEDIUM_SENSITIVE
            
        return PrivacySensitivity.LOW_SENSITIVE

class TaskComplexityAnalyzer:
    """任務複雜度分析器"""
    
    def __init__(self):
        self.complexity_indicators = {
            'simple': {
                'keywords': ['syntax', 'format', 'lint', 'style', 'rename', 'comment'],
                'max_lines': 50,
                'max_functions': 3
            },
            'medium': {
                'keywords': ['refactor', 'optimize', 'debug', 'test', 'implement'],
                'max_lines': 200,
                'max_functions': 10
            },
            'complex': {
                'keywords': ['design', 'architecture', 'algorithm', 'pattern', 'framework'],
                'max_lines': 500,
                'max_functions': 25
            },
            'ultra_complex': {
                'keywords': ['system', 'distributed', 'microservice', 'scalable', 'enterprise'],
                'max_lines': float('inf'),
                'max_functions': float('inf')
            }
        }
    
    def analyze_complexity(self, content: str, task_type: str) -> TaskComplexity:
        """分析任務複雜度"""
        content_lower = content.lower()
        lines_count = len(content.split('\n'))
        functions_count = len(re.findall(r'def\s+\w+', content))
        
        # 基於關鍵詞判斷
        for complexity, indicators in self.complexity_indicators.items():
            keywords = indicators['keywords']
            if any(keyword in content_lower for keyword in keywords):
                # 進一步檢查代碼規模
                if (lines_count <= indicators['max_lines'] and 
                    functions_count <= indicators['max_functions']):
                    return TaskComplexity(complexity.upper())
        
        # 基於代碼規模判斷
        if lines_count <= 50 and functions_count <= 3:
            return TaskComplexity.SIMPLE
        elif lines_count <= 200 and functions_count <= 10:
            return TaskComplexity.MEDIUM
        elif lines_count <= 500 and functions_count <= 25:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.ULTRA_COMPLEX

class LocalCapabilityAssessor:
    """本地處理能力評估器"""
    
    def __init__(self):
        self.local_model_capabilities = {
            # 基礎能力 (Qwen 3 8B 擅長)
            'syntax_checking': 0.95,
            'code_formatting': 0.90,
            'variable_renaming': 0.88,
            'comment_generation': 0.85,
            'simple_refactoring': 0.82,
            'bug_detection': 0.78,
            'code_completion': 0.80,
            
            # 中等能力
            'function_generation': 0.70,
            'test_generation': 0.68,
            'code_explanation': 0.65,
            'optimization_suggestions': 0.60,
            
            # 複雜能力 (需要雲端支持)
            'architecture_design': 0.35,
            'complex_algorithm': 0.30,
            'security_audit': 0.25,
            'performance_analysis': 0.40,
            'system_design': 0.20
        }
        
        # 任務類型到能力的映射
        self.task_capability_mapping = {
            InteractionType.CODE_GENERATION: 'function_generation',
            InteractionType.TESTING: 'test_generation',
            InteractionType.DEBUGGING: 'bug_detection',
            InteractionType.OPTIMIZATION: 'optimization_suggestions',
            InteractionType.TECHNICAL_ANALYSIS: 'code_explanation',
            InteractionType.SYSTEM_DESIGN: 'architecture_design',
            InteractionType.DOCUMENTATION: 'comment_generation'
        }
    
    def assess_local_capability(self, task_type: InteractionType, 
                              complexity: TaskComplexity) -> float:
        """評估本地處理能力"""
        base_capability = self.local_model_capabilities.get(
            self.task_capability_mapping.get(task_type, 'function_generation'), 0.5
        )
        
        # 根據複雜度調整能力評分
        complexity_multipliers = {
            TaskComplexity.SIMPLE: 1.2,
            TaskComplexity.MEDIUM: 1.0,
            TaskComplexity.COMPLEX: 0.7,
            TaskComplexity.ULTRA_COMPLEX: 0.4
        }
        
        multiplier = complexity_multipliers.get(complexity, 1.0)
        adjusted_capability = min(base_capability * multiplier, 1.0)
        
        return adjusted_capability

class CostCalculator:
    """成本計算器"""
    
    def __init__(self):
        # 定價模型 (USD per 1K tokens)
        self.pricing = {
            'claude_3_sonnet': {
                'input': 0.003,
                'output': 0.015
            },
            'gpt_4': {
                'input': 0.03,
                'output': 0.06
            },
            'local_qwen_3_8b': {
                'electricity_per_hour': 0.12,  # GPU功耗成本
                'hardware_depreciation_per_hour': 0.05
            }
        }
        
        # Token估算模型
        self.token_estimation = {
            'chars_per_token': 4,  # 平均字符數
            'response_multiplier': 1.5  # 響應通常比輸入長50%
        }
    
    def estimate_tokens(self, content: str) -> Tuple[int, int]:
        """估算輸入和輸出token數"""
        input_tokens = len(content) // self.token_estimation['chars_per_token']
        output_tokens = int(input_tokens * self.token_estimation['response_multiplier'])
        return input_tokens, output_tokens
    
    def calculate_cloud_cost(self, input_tokens: int, output_tokens: int, 
                           model: str = 'claude_3_sonnet') -> float:
        """計算雲端處理成本"""
        pricing = self.pricing.get(model, self.pricing['claude_3_sonnet'])
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        
        return input_cost + output_cost
    
    def calculate_local_cost(self, processing_time_seconds: float) -> float:
        """計算本地處理成本"""
        processing_hours = processing_time_seconds / 3600
        pricing = self.pricing['local_qwen_3_8b']
        
        electricity_cost = processing_hours * pricing['electricity_per_hour']
        depreciation_cost = processing_hours * pricing['hardware_depreciation_per_hour']
        
        return electricity_cost + depreciation_cost

class SmartRouter:
    """智慧路由器核心"""
    
    def __init__(self, interaction_log_manager: InteractionLogManager):
        self.log_manager = interaction_log_manager
        self.privacy_classifier = PrivacyClassifier()
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.capability_assessor = LocalCapabilityAssessor()
        self.cost_calculator = CostCalculator()
        
        # 路由配置
        self.config = {
            'privacy_mode': 'STRICT',  # STRICT, BALANCED, PERMISSIVE
            'cost_optimization': True,
            'quality_threshold': 0.7,
            'max_cloud_cost_per_request': 0.50,  # USD
            'local_processing_timeout': 30,  # seconds
        }
        
        # 統計數據
        self.routing_stats = {
            'total_requests': 0,
            'local_processed': 0,
            'cloud_processed': 0,
            'hybrid_processed': 0,
            'total_cost_saved': 0.0,
            'privacy_violations': 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def route_request(self, user_request: str, context: Dict = None) -> RoutingDecision:
        """智慧路由決策"""
        self.routing_stats['total_requests'] += 1
        
        # 1. 分析請求特徵
        privacy_level = self.privacy_classifier.classify_sensitivity(user_request)
        task_type = self.log_manager.classify_interaction(user_request, "")
        complexity = self.complexity_analyzer.analyze_complexity(user_request, task_type.value)
        
        # 2. 評估本地處理能力
        local_capability = self.capability_assessor.assess_local_capability(task_type, complexity)
        
        # 3. 計算成本
        input_tokens, output_tokens = self.cost_calculator.estimate_tokens(user_request)
        cloud_cost = self.cost_calculator.calculate_cloud_cost(input_tokens, output_tokens)
        local_cost = self.cost_calculator.calculate_local_cost(30)  # 假設30秒處理時間
        
        # 4. 路由決策邏輯
        decision = self._make_routing_decision(
            privacy_level, complexity, local_capability, 
            cloud_cost, local_cost, input_tokens + output_tokens
        )
        
        # 5. 記錄決策
        self._log_routing_decision(decision, user_request, context)
        
        return decision
    
    def _make_routing_decision(self, privacy_level: PrivacySensitivity,
                             complexity: TaskComplexity, local_capability: float,
                             cloud_cost: float, local_cost: float,
                             estimated_tokens: int) -> RoutingDecision:
        """核心路由決策邏輯"""
        
        # 隱私優先規則
        if privacy_level == PrivacySensitivity.HIGH_SENSITIVE:
            if local_capability >= 0.5:  # 降低門檻，優先保護隱私
                return RoutingDecision(
                    processing_location=ProcessingLocation.LOCAL_ONLY,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=local_capability,
                    estimated_cost=local_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning="High sensitivity data must be processed locally",
                    fallback_options=[]
                )
            else:
                # 高敏感但本地能力不足，拒絕處理或降級
                return RoutingDecision(
                    processing_location=ProcessingLocation.LOCAL_ONLY,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=0.3,
                    estimated_cost=local_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning="High sensitivity data, local processing with reduced quality",
                    fallback_options=[]
                )
        
        # 成本優化規則
        if self.config['cost_optimization']:
            cost_savings = cloud_cost - local_cost
            
            # 如果本地處理能力足夠且成本更低
            if (local_capability >= self.config['quality_threshold'] and 
                cost_savings > 0.01):  # 至少節省1分錢
                return RoutingDecision(
                    processing_location=ProcessingLocation.LOCAL_PREFERRED,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=local_capability,
                    estimated_cost=local_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning=f"Local processing saves ${cost_savings:.3f} with quality {local_capability:.2f}",
                    fallback_options=[ProcessingLocation.CLOUD_ALLOWED]
                )
        
        # 質量優先規則
        if local_capability >= 0.8:
            # 本地能力很強，優先本地處理
            return RoutingDecision(
                processing_location=ProcessingLocation.LOCAL_PREFERRED,
                privacy_level=privacy_level,
                task_complexity=complexity,
                confidence_score=local_capability,
                estimated_cost=local_cost,
                estimated_tokens=estimated_tokens,
                reasoning=f"High local capability ({local_capability:.2f})",
                fallback_options=[ProcessingLocation.CLOUD_ALLOWED]
            )
        elif local_capability >= self.config['quality_threshold']:
            # 本地能力足夠，根據隱私級別決定
            if privacy_level == PrivacySensitivity.MEDIUM_SENSITIVE:
                return RoutingDecision(
                    processing_location=ProcessingLocation.CLOUD_ANONYMIZED,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=0.8,
                    estimated_cost=cloud_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning="Medium sensitivity, cloud processing with anonymization",
                    fallback_options=[ProcessingLocation.LOCAL_PREFERRED]
                )
            else:
                return RoutingDecision(
                    processing_location=ProcessingLocation.CLOUD_ALLOWED,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=0.9,
                    estimated_cost=cloud_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning="Low sensitivity, cloud processing for better quality",
                    fallback_options=[ProcessingLocation.LOCAL_PREFERRED]
                )
        else:
            # 本地能力不足，必須雲端處理
            if privacy_level == PrivacySensitivity.MEDIUM_SENSITIVE:
                return RoutingDecision(
                    processing_location=ProcessingLocation.CLOUD_ANONYMIZED,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=0.8,
                    estimated_cost=cloud_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning="Insufficient local capability, cloud processing with anonymization",
                    fallback_options=[ProcessingLocation.LOCAL_PREFERRED]
                )
            else:
                return RoutingDecision(
                    processing_location=ProcessingLocation.CLOUD_ALLOWED,
                    privacy_level=privacy_level,
                    task_complexity=complexity,
                    confidence_score=0.9,
                    estimated_cost=cloud_cost,
                    estimated_tokens=estimated_tokens,
                    reasoning="Insufficient local capability, cloud processing required",
                    fallback_options=[ProcessingLocation.LOCAL_PREFERRED]
                )
    
    def _log_routing_decision(self, decision: RoutingDecision, 
                            user_request: str, context: Dict):
        """記錄路由決策"""
        # 更新統計
        if decision.processing_location == ProcessingLocation.LOCAL_ONLY:
            self.routing_stats['local_processed'] += 1
        elif decision.processing_location in [ProcessingLocation.CLOUD_ALLOWED, 
                                            ProcessingLocation.CLOUD_ANONYMIZED]:
            self.routing_stats['cloud_processed'] += 1
        else:
            self.routing_stats['hybrid_processed'] += 1
        
        # 記錄到InteractionLogManager
        routing_context = {
            'routing_decision': asdict(decision),
            'original_context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        # 這裡可以調用log_manager的記錄方法
        self.logger.info(f"Routing decision: {decision.processing_location.value} "
                        f"for {decision.task_complexity.value} task "
                        f"with {decision.privacy_level.value} sensitivity")
    
    def get_routing_statistics(self) -> Dict:
        """獲取路由統計信息"""
        total = self.routing_stats['total_requests']
        if total == 0:
            return self.routing_stats
        
        return {
            **self.routing_stats,
            'local_percentage': (self.routing_stats['local_processed'] / total) * 100,
            'cloud_percentage': (self.routing_stats['cloud_processed'] / total) * 100,
            'hybrid_percentage': (self.routing_stats['hybrid_processed'] / total) * 100,
            'average_cost_savings': self.routing_stats['total_cost_saved'] / total
        }
    
    def update_config(self, new_config: Dict):
        """更新路由配置"""
        self.config.update(new_config)
        self.logger.info(f"Router configuration updated: {new_config}")

class SmartRoutingManager:
    """智慧路由管理器 - 整合InteractionLogManager"""
    
    def __init__(self, base_dir: str = "/home/ubuntu/Powerauto.ai/smart_routing"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化組件
        self.interaction_log_manager = InteractionLogManager()
        self.smart_router = SmartRouter(self.interaction_log_manager)
        
        # 設置日誌
        self.setup_logging()
        
        self.logger.info("✅ SmartRoutingManager initialized")
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_request(self, user_request: str, context: Dict = None) -> Dict:
        """處理用戶請求"""
        # 1. 路由決策
        routing_decision = self.smart_router.route_request(user_request, context)
        
        # 2. 根據決策處理請求
        if routing_decision.processing_location == ProcessingLocation.LOCAL_ONLY:
            response = self._process_locally(user_request, routing_decision)
        elif routing_decision.processing_location == ProcessingLocation.CLOUD_ANONYMIZED:
            response = self._process_cloud_anonymized(user_request, routing_decision)
        elif routing_decision.processing_location == ProcessingLocation.CLOUD_ALLOWED:
            response = self._process_cloud(user_request, routing_decision)
        else:
            response = self._process_hybrid(user_request, routing_decision)
        
        # 3. 記錄完整交互
        self.interaction_log_manager.log_interaction(
            user_request=user_request,
            agent_response=response['content'],
            deliverables=[],
            context={
                'routing_decision': asdict(routing_decision),
                'processing_metrics': response['metrics'],
                'original_context': context or {}
            }
        )
        
        return {
            'response': response['content'],
            'routing_decision': routing_decision,
            'processing_metrics': response['metrics'],
            'cost_info': {
                'estimated_cost': routing_decision.estimated_cost,
                'actual_cost': response['metrics'].get('actual_cost', 0),
                'tokens_used': response['metrics'].get('tokens_used', 0)
            }
        }
    
    def _process_locally(self, request: str, decision: RoutingDecision) -> Dict:
        """本地處理"""
        start_time = time.time()
        
        # 模擬本地處理 (實際實現中會調用本地模型)
        response_content = f"[LOCAL] Processed request: {request[:100]}..."
        
        processing_time = time.time() - start_time
        actual_cost = self.smart_router.cost_calculator.calculate_local_cost(processing_time)
        
        return {
            'content': response_content,
            'metrics': {
                'processing_time': processing_time,
                'actual_cost': actual_cost,
                'tokens_used': 0,  # 本地處理不計算tokens
                'location': 'local'
            }
        }
    
    def _process_cloud_anonymized(self, request: str, decision: RoutingDecision) -> Dict:
        """雲端匿名化處理"""
        start_time = time.time()
        
        # 1. 數據脫敏 (簡化實現)
        anonymized_request = self._anonymize_content(request)
        
        # 2. 雲端處理 (模擬)
        response_content = f"[CLOUD_ANON] Processed anonymized request"
        
        # 3. 恢復數據 (簡化實現)
        final_response = self._restore_content(response_content)
        
        processing_time = time.time() - start_time
        
        return {
            'content': final_response,
            'metrics': {
                'processing_time': processing_time,
                'actual_cost': decision.estimated_cost,
                'tokens_used': decision.estimated_tokens,
                'location': 'cloud_anonymized'
            }
        }
    
    def _process_cloud(self, request: str, decision: RoutingDecision) -> Dict:
        """雲端處理"""
        start_time = time.time()
        
        # 模擬雲端處理
        response_content = f"[CLOUD] High-quality processed request: {request[:100]}..."
        
        processing_time = time.time() - start_time
        
        return {
            'content': response_content,
            'metrics': {
                'processing_time': processing_time,
                'actual_cost': decision.estimated_cost,
                'tokens_used': decision.estimated_tokens,
                'location': 'cloud'
            }
        }
    
    def _process_hybrid(self, request: str, decision: RoutingDecision) -> Dict:
        """混合處理"""
        start_time = time.time()
        
        # 模擬混合處理邏輯
        response_content = f"[HYBRID] Combined local and cloud processing"
        
        processing_time = time.time() - start_time
        
        return {
            'content': response_content,
            'metrics': {
                'processing_time': processing_time,
                'actual_cost': decision.estimated_cost * 0.7,  # 混合處理成本優化
                'tokens_used': decision.estimated_tokens // 2,
                'location': 'hybrid'
            }
        }
    
    def _anonymize_content(self, content: str) -> str:
        """內容匿名化 (簡化實現)"""
        # 實際實現中會使用更複雜的匿名化算法
        anonymized = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', 'VAR_X', content)
        return anonymized
    
    def _restore_content(self, anonymized_content: str) -> str:
        """恢復匿名化內容 (簡化實現)"""
        # 實際實現中會使用映射表恢復
        return anonymized_content.replace('VAR_X', 'restored_var')
    
    def get_dashboard_data(self) -> Dict:
        """獲取儀表板數據"""
        routing_stats = self.smart_router.get_routing_statistics()
        
        return {
            'routing_statistics': routing_stats,
            'cost_analysis': {
                'total_requests': routing_stats['total_requests'],
                'total_cost_saved': routing_stats['total_cost_saved'],
                'average_cost_per_request': routing_stats.get('average_cost_savings', 0)
            },
            'privacy_compliance': {
                'high_sensitive_local_rate': 100,  # 高敏感數據100%本地處理
                'privacy_violations': routing_stats['privacy_violations'],
                'compliance_score': 95.5  # 示例合規分數
            },
            'performance_metrics': {
                'average_response_time': 2.5,  # 秒
                'local_success_rate': 92.3,   # %
                'cloud_success_rate': 98.7    # %
            }
        }

# 使用示例
if __name__ == "__main__":
    # 初始化智慧路由管理器
    routing_manager = SmartRoutingManager()
    
    # 測試不同類型的請求
    test_requests = [
        {
            'request': 'Please help me format this Python code',
            'context': {'task_type': 'formatting'}
        },
        {
            'request': 'Design a microservices architecture for our e-commerce platform',
            'context': {'task_type': 'architecture'}
        },
        {
            'request': 'Fix this bug in my authentication system with API key sk-1234567890',
            'context': {'task_type': 'debugging'}
        }
    ]
    
    print("🚀 Smart Routing System Test Results:")
    print("=" * 50)
    
    for i, test in enumerate(test_requests, 1):
        print(f"\n📝 Test {i}: {test['request'][:50]}...")
        
        result = routing_manager.process_request(
            test['request'], 
            test['context']
        )
        
        decision = result['routing_decision']
        print(f"🎯 Routing Decision: {decision.processing_location.value}")
        print(f"🔒 Privacy Level: {decision.privacy_level.value}")
        print(f"⚡ Complexity: {decision.task_complexity.value}")
        print(f"💰 Estimated Cost: ${decision.estimated_cost:.4f}")
        print(f"🧠 Confidence: {decision.confidence_score:.2f}")
        print(f"💡 Reasoning: {decision.reasoning}")
    
    # 顯示統計信息
    print(f"\n📊 Overall Statistics:")
    dashboard_data = routing_manager.get_dashboard_data()
    stats = dashboard_data['routing_statistics']
    
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Local Processing: {stats.get('local_percentage', 0):.1f}%")
    print(f"Cloud Processing: {stats.get('cloud_percentage', 0):.1f}%")
    print(f"Total Cost Saved: ${stats['total_cost_saved']:.4f}")
    
    print("\n✅ Smart Routing System initialized successfully!")

