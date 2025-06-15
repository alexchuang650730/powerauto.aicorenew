#!/usr/bin/env python3
"""
多適配器答案合成邏輯優化器
整合多個適配器的輸出，生成最佳答案
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("answer_synthesizer")

class ConfidenceLevel(Enum):
    """置信度級別"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

class AnswerType(Enum):
    """答案類型"""
    FACTUAL = "factual"          # 事實性答案
    NUMERICAL = "numerical"      # 數值答案
    BOOLEAN = "boolean"          # 是非答案
    DESCRIPTIVE = "descriptive"  # 描述性答案
    LIST = "list"               # 列表答案
    UNKNOWN = "unknown"         # 未知類型

@dataclass
class AdapterResponse:
    """適配器響應數據結構"""
    adapter_name: str
    content: str
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None

@dataclass
class SynthesizedAnswer:
    """合成答案數據結構"""
    final_answer: str
    confidence: float
    answer_type: AnswerType
    contributing_adapters: List[str]
    synthesis_method: str
    reasoning: str
    metadata: Dict[str, Any]

class MultiAdapterAnswerSynthesizer:
    """多適配器答案合成器"""
    
    def __init__(self):
        """初始化答案合成器"""
        self.adapter_weights = {
            'aci_dev': 0.25,        # ACI.dev工具
            'mcp_so': 0.20,         # MCP.so專業工具
            'infinite_context': 0.15, # 無限上下文
            'real_ai_api': 0.30,    # 真實AI API
            'zapier': 0.10          # Zapier自動化
        }
        
        self.synthesis_strategies = {
            'consensus': self._consensus_synthesis,
            'weighted_average': self._weighted_average_synthesis,
            'best_confidence': self._best_confidence_synthesis,
            'majority_vote': self._majority_vote_synthesis,
            'expert_selection': self._expert_selection_synthesis
        }
        
        self.answer_patterns = self._load_answer_patterns()
        
        logger.info("多適配器答案合成器初始化完成")
    
    def _load_answer_patterns(self) -> Dict[str, Any]:
        """加載答案模式"""
        return {
            'numerical': {
                'patterns': [r'\d+\.?\d*', r'\d+/\d+', r'\d+%'],
                'extractors': ['extract_number', 'extract_fraction', 'extract_percentage']
            },
            'boolean': {
                'patterns': [r'\b(yes|no|true|false|是|否)\b'],
                'extractors': ['extract_boolean']
            },
            'factual': {
                'patterns': [r'\b[A-Z][a-z]+\b', r'\d{4}', r'\b\w+\s+\w+\b'],
                'extractors': ['extract_entity', 'extract_year', 'extract_phrase']
            },
            'list': {
                'patterns': [r'\d+\.\s+', r'•\s+', r'-\s+'],
                'extractors': ['extract_numbered_list', 'extract_bullet_list']
            }
        }
    
    def synthesize_answers(self, adapter_responses: List[AdapterResponse], 
                          question: str = "", strategy: str = "consensus") -> SynthesizedAnswer:
        """合成多個適配器的答案"""
        if not adapter_responses:
            return self._create_empty_answer("沒有適配器響應")
        
        # 過濾成功的響應
        successful_responses = [r for r in adapter_responses if r.success]
        
        if not successful_responses:
            return self._create_empty_answer("所有適配器響應都失敗")
        
        # 分析答案類型
        answer_type = self._detect_answer_type(question, successful_responses)
        
        # 選擇合成策略
        if strategy not in self.synthesis_strategies:
            strategy = "consensus"
        
        synthesis_func = self.synthesis_strategies[strategy]
        
        try:
            # 執行答案合成
            synthesized = synthesis_func(successful_responses, answer_type, question)
            
            # 後處理和驗證
            synthesized = self._post_process_answer(synthesized, answer_type)
            
            logger.info(f"答案合成完成，使用策略: {strategy}, 置信度: {synthesized.confidence:.2f}")
            
            return synthesized
        
        except Exception as e:
            logger.error(f"答案合成失敗: {e}")
            return self._create_fallback_answer(successful_responses, str(e))
    
    def _detect_answer_type(self, question: str, responses: List[AdapterResponse]) -> AnswerType:
        """檢測答案類型"""
        question_lower = question.lower()
        
        # 基於問題關鍵詞檢測
        if any(word in question_lower for word in ['how many', 'how much', 'count', '多少', '幾個', '數量']):
            return AnswerType.NUMERICAL
        
        elif any(word in question_lower for word in ['is', 'are', 'can', 'will', 'does', '是否', '能否', '會不會']):
            return AnswerType.BOOLEAN
        
        elif any(word in question_lower for word in ['list', 'enumerate', 'name', '列出', '列舉', '說出']):
            return AnswerType.LIST
        
        elif any(word in question_lower for word in ['who', 'what', 'when', 'where', '誰', '什麼', '何時', '哪裡']):
            return AnswerType.FACTUAL
        
        # 基於響應內容檢測
        response_texts = [r.content for r in responses]
        combined_text = " ".join(response_texts)
        
        # 數值檢測
        import re
        if re.search(r'\b\d+\.?\d*\b', combined_text):
            return AnswerType.NUMERICAL
        
        # 布爾檢測
        if re.search(r'\b(yes|no|true|false|是|否)\b', combined_text.lower()):
            return AnswerType.BOOLEAN
        
        # 列表檢測
        if re.search(r'(\d+\.\s+|•\s+|-\s+)', combined_text):
            return AnswerType.LIST
        
        # 默認為描述性
        return AnswerType.DESCRIPTIVE
    
    def _consensus_synthesis(self, responses: List[AdapterResponse], 
                           answer_type: AnswerType, question: str) -> SynthesizedAnswer:
        """共識合成策略"""
        # 提取關鍵答案
        extracted_answers = []
        for response in responses:
            answer = self._extract_key_answer(response.content, answer_type)
            if answer:
                extracted_answers.append({
                    'answer': answer,
                    'adapter': response.adapter_name,
                    'confidence': response.confidence,
                    'weight': self.adapter_weights.get(response.adapter_name, 0.1)
                })
        
        if not extracted_answers:
            # 沒有提取到關鍵答案，使用最高置信度響應
            best_response = max(responses, key=lambda r: r.confidence)
            return SynthesizedAnswer(
                final_answer=best_response.content,
                confidence=best_response.confidence * 0.8,  # 降低置信度
                answer_type=answer_type,
                contributing_adapters=[best_response.adapter_name],
                synthesis_method="fallback_best_confidence",
                reasoning="無法提取關鍵答案，使用最高置信度響應",
                metadata={'fallback': True}
            )
        
        # 尋找共識答案
        answer_groups = {}
        for item in extracted_answers:
            answer = item['answer']
            if answer not in answer_groups:
                answer_groups[answer] = []
            answer_groups[answer].append(item)
        
        # 計算每個答案的權重分數
        answer_scores = {}
        for answer, items in answer_groups.items():
            score = 0
            for item in items:
                score += item['confidence'] * item['weight']
            answer_scores[answer] = {
                'score': score,
                'count': len(items),
                'adapters': [item['adapter'] for item in items],
                'avg_confidence': sum(item['confidence'] for item in items) / len(items)
            }
        
        # 選擇最佳答案
        best_answer = max(answer_scores.keys(), key=lambda a: answer_scores[a]['score'])
        best_info = answer_scores[best_answer]
        
        # 計算最終置信度
        final_confidence = min(0.95, best_info['avg_confidence'] * (1 + 0.1 * best_info['count']))
        
        return SynthesizedAnswer(
            final_answer=best_answer,
            confidence=final_confidence,
            answer_type=answer_type,
            contributing_adapters=best_info['adapters'],
            synthesis_method="consensus",
            reasoning=f"基於 {best_info['count']} 個適配器的共識，權重分數: {best_info['score']:.2f}",
            metadata={
                'answer_groups': len(answer_groups),
                'consensus_score': best_info['score'],
                'supporting_adapters': best_info['count']
            }
        )
    
    def _weighted_average_synthesis(self, responses: List[AdapterResponse], 
                                  answer_type: AnswerType, question: str) -> SynthesizedAnswer:
        """加權平均合成策略"""
        if answer_type == AnswerType.NUMERICAL:
            return self._numerical_weighted_average(responses)
        else:
            return self._text_weighted_synthesis(responses, answer_type)
    
    def _numerical_weighted_average(self, responses: List[AdapterResponse]) -> SynthesizedAnswer:
        """數值加權平均"""
        numerical_values = []
        total_weight = 0
        
        for response in responses:
            value = self._extract_numerical_value(response.content)
            if value is not None:
                weight = self.adapter_weights.get(response.adapter_name, 0.1) * response.confidence
                numerical_values.append({
                    'value': value,
                    'weight': weight,
                    'adapter': response.adapter_name
                })
                total_weight += weight
        
        if not numerical_values:
            # 沒有數值，回退到最佳響應
            best_response = max(responses, key=lambda r: r.confidence)
            return SynthesizedAnswer(
                final_answer=best_response.content,
                confidence=best_response.confidence * 0.7,
                answer_type=AnswerType.NUMERICAL,
                contributing_adapters=[best_response.adapter_name],
                synthesis_method="numerical_fallback",
                reasoning="無法提取數值，使用最佳響應",
                metadata={'fallback': True}
            )
        
        # 計算加權平均
        weighted_sum = sum(item['value'] * item['weight'] for item in numerical_values)
        weighted_average = weighted_sum / total_weight
        
        # 根據數值類型格式化答案
        if all(isinstance(item['value'], int) for item in numerical_values):
            final_answer = str(round(weighted_average))
        else:
            final_answer = f"{weighted_average:.4f}".rstrip('0').rstrip('.')
        
        # 計算置信度
        confidence = min(0.9, total_weight / len(responses))
        
        return SynthesizedAnswer(
            final_answer=final_answer,
            confidence=confidence,
            answer_type=AnswerType.NUMERICAL,
            contributing_adapters=[item['adapter'] for item in numerical_values],
            synthesis_method="numerical_weighted_average",
            reasoning=f"基於 {len(numerical_values)} 個數值的加權平均",
            metadata={
                'raw_values': [item['value'] for item in numerical_values],
                'weights': [item['weight'] for item in numerical_values],
                'weighted_average': weighted_average
            }
        )
    
    def _text_weighted_synthesis(self, responses: List[AdapterResponse], 
                               answer_type: AnswerType) -> SynthesizedAnswer:
        """文本加權合成"""
        # 計算每個響應的權重分數
        weighted_responses = []
        for response in responses:
            weight = self.adapter_weights.get(response.adapter_name, 0.1)
            score = weight * response.confidence
            weighted_responses.append({
                'response': response,
                'score': score,
                'weight': weight
            })
        
        # 按分數排序
        weighted_responses.sort(key=lambda x: x['score'], reverse=True)
        
        # 選擇最高分數的響應作為主答案
        best_item = weighted_responses[0]
        best_response = best_item['response']
        
        # 嘗試從其他響應中補充信息
        supplementary_info = []
        for item in weighted_responses[1:3]:  # 取前2個補充響應
            if item['score'] > 0.3:  # 只考慮高質量響應
                key_info = self._extract_key_information(item['response'].content, answer_type)
                if key_info and key_info != best_response.content:
                    supplementary_info.append(key_info)
        
        # 構建最終答案
        final_answer = best_response.content
        if supplementary_info:
            final_answer += f" (補充信息: {'; '.join(supplementary_info)})"
        
        # 計算最終置信度
        final_confidence = min(0.9, best_item['score'] + 0.05 * len(supplementary_info))
        
        contributing_adapters = [best_response.adapter_name]
        if supplementary_info:
            contributing_adapters.extend([item['response'].adapter_name for item in weighted_responses[1:1+len(supplementary_info)]])
        
        return SynthesizedAnswer(
            final_answer=final_answer,
            confidence=final_confidence,
            answer_type=answer_type,
            contributing_adapters=contributing_adapters,
            synthesis_method="text_weighted",
            reasoning=f"主答案來自 {best_response.adapter_name}，權重分數: {best_item['score']:.2f}",
            metadata={
                'primary_score': best_item['score'],
                'supplementary_count': len(supplementary_info),
                'all_scores': [item['score'] for item in weighted_responses]
            }
        )
    
    def _best_confidence_synthesis(self, responses: List[AdapterResponse], 
                                 answer_type: AnswerType, question: str) -> SynthesizedAnswer:
        """最佳置信度合成策略"""
        # 選擇置信度最高的響應
        best_response = max(responses, key=lambda r: r.confidence)
        
        return SynthesizedAnswer(
            final_answer=best_response.content,
            confidence=best_response.confidence,
            answer_type=answer_type,
            contributing_adapters=[best_response.adapter_name],
            synthesis_method="best_confidence",
            reasoning=f"選擇置信度最高的響應: {best_response.confidence:.2f}",
            metadata={
                'all_confidences': [r.confidence for r in responses],
                'selected_adapter': best_response.adapter_name
            }
        )
    
    def _majority_vote_synthesis(self, responses: List[AdapterResponse], 
                               answer_type: AnswerType, question: str) -> SynthesizedAnswer:
        """多數投票合成策略"""
        # 提取關鍵答案
        answers = []
        for response in responses:
            answer = self._extract_key_answer(response.content, answer_type)
            if answer:
                answers.append({
                    'answer': answer,
                    'adapter': response.adapter_name,
                    'confidence': response.confidence
                })
        
        if not answers:
            return self._best_confidence_synthesis(responses, answer_type, question)
        
        # 統計投票
        vote_counts = {}
        for item in answers:
            answer = item['answer']
            if answer not in vote_counts:
                vote_counts[answer] = []
            vote_counts[answer].append(item)
        
        # 選擇得票最多的答案
        winner = max(vote_counts.keys(), key=lambda a: len(vote_counts[a]))
        winner_votes = vote_counts[winner]
        
        # 計算平均置信度
        avg_confidence = sum(vote['confidence'] for vote in winner_votes) / len(winner_votes)
        
        # 多數獎勵
        majority_bonus = min(0.2, 0.05 * len(winner_votes))
        final_confidence = min(0.95, avg_confidence + majority_bonus)
        
        return SynthesizedAnswer(
            final_answer=winner,
            confidence=final_confidence,
            answer_type=answer_type,
            contributing_adapters=[vote['adapter'] for vote in winner_votes],
            synthesis_method="majority_vote",
            reasoning=f"獲得 {len(winner_votes)} 票，共 {len(answers)} 個有效答案",
            metadata={
                'vote_distribution': {answer: len(votes) for answer, votes in vote_counts.items()},
                'total_votes': len(answers),
                'winner_votes': len(winner_votes)
            }
        )
    
    def _expert_selection_synthesis(self, responses: List[AdapterResponse], 
                                  answer_type: AnswerType, question: str) -> SynthesizedAnswer:
        """專家選擇合成策略"""
        # 根據問題類型選擇最適合的適配器
        expert_preferences = {
            AnswerType.NUMERICAL: ['aci_dev', 'real_ai_api', 'mcp_so'],
            AnswerType.FACTUAL: ['real_ai_api', 'mcp_so', 'infinite_context'],
            AnswerType.BOOLEAN: ['real_ai_api', 'aci_dev', 'mcp_so'],
            AnswerType.LIST: ['mcp_so', 'real_ai_api', 'aci_dev'],
            AnswerType.DESCRIPTIVE: ['real_ai_api', 'infinite_context', 'mcp_so']
        }
        
        preferred_adapters = expert_preferences.get(answer_type, ['real_ai_api', 'aci_dev'])
        
        # 按專家偏好排序響應
        expert_responses = []
        other_responses = []
        
        for response in responses:
            if response.adapter_name in preferred_adapters:
                expert_responses.append(response)
            else:
                other_responses.append(response)
        
        # 優先選擇專家響應
        if expert_responses:
            # 在專家響應中選擇最佳的
            best_expert = max(expert_responses, key=lambda r: r.confidence)
            
            return SynthesizedAnswer(
                final_answer=best_expert.content,
                confidence=min(0.95, best_expert.confidence * 1.1),  # 專家獎勵
                answer_type=answer_type,
                contributing_adapters=[best_expert.adapter_name],
                synthesis_method="expert_selection",
                reasoning=f"選擇 {answer_type.value} 類型問題的專家適配器: {best_expert.adapter_name}",
                metadata={
                    'expert_adapters': preferred_adapters,
                    'expert_responses_count': len(expert_responses),
                    'selected_expert': best_expert.adapter_name,
                    'expert_bonus': 0.1
                }
            )
        else:
            # 沒有專家響應，回退到最佳置信度
            return self._best_confidence_synthesis(responses, answer_type, question)
    
    def _extract_key_answer(self, content: str, answer_type: AnswerType) -> Optional[str]:
        """提取關鍵答案"""
        if not content:
            return None
        
        content = content.strip()
        
        if answer_type == AnswerType.NUMERICAL:
            return self._extract_numerical_answer(content)
        elif answer_type == AnswerType.BOOLEAN:
            return self._extract_boolean_answer(content)
        elif answer_type == AnswerType.FACTUAL:
            return self._extract_factual_answer(content)
        elif answer_type == AnswerType.LIST:
            return self._extract_list_answer(content)
        else:
            # 對於描述性答案，返回前100個字符
            return content[:100] + "..." if len(content) > 100 else content
    
    def _extract_numerical_answer(self, content: str) -> Optional[str]:
        """提取數值答案"""
        import re
        
        # 尋找數字模式
        patterns = [
            r'\b(\d+\.?\d*)\b',  # 普通數字
            r'\b(\d+/\d+)\b',    # 分數
            r'\b(\d+%)\b',       # 百分比
            r'\b(\d+,\d+)\b'     # 帶逗號的數字
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_numerical_value(self, content: str) -> Optional[float]:
        """提取數值"""
        import re
        
        # 尋找數字
        match = re.search(r'\b(\d+\.?\d*)\b', content)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _extract_boolean_answer(self, content: str) -> Optional[str]:
        """提取布爾答案"""
        import re
        
        content_lower = content.lower()
        
        # 英文布爾值
        if re.search(r'\byes\b', content_lower):
            return "yes"
        elif re.search(r'\bno\b', content_lower):
            return "no"
        elif re.search(r'\btrue\b', content_lower):
            return "true"
        elif re.search(r'\bfalse\b', content_lower):
            return "false"
        
        # 中文布爾值
        if re.search(r'\b是\b', content):
            return "是"
        elif re.search(r'\b否\b', content):
            return "否"
        
        return None
    
    def _extract_factual_answer(self, content: str) -> Optional[str]:
        """提取事實性答案"""
        # 對於事實性答案，嘗試提取第一個句子或關鍵短語
        sentences = content.split('。')
        if sentences:
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 5:  # 確保不是太短
                return first_sentence
        
        # 如果沒有句號，返回前50個字符
        return content[:50] + "..." if len(content) > 50 else content
    
    def _extract_list_answer(self, content: str) -> Optional[str]:
        """提取列表答案"""
        import re
        
        # 尋找列表項
        list_patterns = [
            r'(\d+\.\s+[^\n]+)',  # 數字列表
            r'(•\s+[^\n]+)',      # 項目符號列表
            r'(-\s+[^\n]+)'       # 破折號列表
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, content)
            if matches:
                return '; '.join(matches[:3])  # 返回前3項
        
        return None
    
    def _extract_key_information(self, content: str, answer_type: AnswerType) -> Optional[str]:
        """提取關鍵信息"""
        # 簡化版本，返回內容的摘要
        if len(content) <= 50:
            return content
        
        # 提取前30個字符作為關鍵信息
        return content[:30] + "..."
    
    def _post_process_answer(self, answer: SynthesizedAnswer, answer_type: AnswerType) -> SynthesizedAnswer:
        """後處理答案"""
        # 清理答案格式
        final_answer = answer.final_answer.strip()
        
        # 根據答案類型進行特定處理
        if answer_type == AnswerType.NUMERICAL:
            # 確保數值答案格式正確
            import re
            match = re.search(r'\b(\d+\.?\d*)\b', final_answer)
            if match:
                final_answer = match.group(1)
        
        elif answer_type == AnswerType.BOOLEAN:
            # 標準化布爾答案
            final_answer_lower = final_answer.lower()
            if 'yes' in final_answer_lower or '是' in final_answer:
                final_answer = "yes"
            elif 'no' in final_answer_lower or '否' in final_answer:
                final_answer = "no"
        
        # 更新答案
        answer.final_answer = final_answer
        
        return answer
    
    def _create_empty_answer(self, reason: str) -> SynthesizedAnswer:
        """創建空答案"""
        return SynthesizedAnswer(
            final_answer="無法生成答案",
            confidence=0.0,
            answer_type=AnswerType.UNKNOWN,
            contributing_adapters=[],
            synthesis_method="empty",
            reasoning=reason,
            metadata={'error': True, 'reason': reason}
        )
    
    def _create_fallback_answer(self, responses: List[AdapterResponse], error: str) -> SynthesizedAnswer:
        """創建回退答案"""
        if responses:
            best_response = max(responses, key=lambda r: r.confidence)
            return SynthesizedAnswer(
                final_answer=best_response.content,
                confidence=best_response.confidence * 0.5,  # 降低置信度
                answer_type=AnswerType.UNKNOWN,
                contributing_adapters=[best_response.adapter_name],
                synthesis_method="fallback",
                reasoning=f"合成失敗，使用最佳響應: {error}",
                metadata={'error': True, 'fallback': True, 'error_message': error}
            )
        else:
            return self._create_empty_answer(f"合成失敗且無可用響應: {error}")

# 全局合成器實例
_synthesizer = None

def get_answer_synthesizer() -> MultiAdapterAnswerSynthesizer:
    """獲取全局答案合成器實例"""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = MultiAdapterAnswerSynthesizer()
    return _synthesizer

def synthesize_adapter_responses(responses: List[Dict[str, Any]], 
                               question: str = "", 
                               strategy: str = "consensus") -> Dict[str, Any]:
    """便捷的答案合成函數"""
    synthesizer = get_answer_synthesizer()
    
    # 轉換響應格式
    adapter_responses = []
    for resp in responses:
        adapter_responses.append(AdapterResponse(
            adapter_name=resp.get('adapter_name', 'unknown'),
            content=resp.get('content', ''),
            confidence=resp.get('confidence', 0.5),
            processing_time=resp.get('processing_time', 0.0),
            metadata=resp.get('metadata', {}),
            success=resp.get('success', True),
            error=resp.get('error')
        ))
    
    # 執行合成
    result = synthesizer.synthesize_answers(adapter_responses, question, strategy)
    
    # 轉換為字典格式
    return {
        'final_answer': result.final_answer,
        'confidence': result.confidence,
        'answer_type': result.answer_type.value,
        'contributing_adapters': result.contributing_adapters,
        'synthesis_method': result.synthesis_method,
        'reasoning': result.reasoning,
        'metadata': result.metadata
    }

if __name__ == "__main__":
    # 測試答案合成器
    synthesizer = MultiAdapterAnswerSynthesizer()
    
    print("=== 答案合成器測試 ===")
    
    # 模擬適配器響應
    test_responses = [
        AdapterResponse(
            adapter_name="aci_dev",
            content="答案是42",
            confidence=0.8,
            processing_time=0.5,
            metadata={},
            success=True
        ),
        AdapterResponse(
            adapter_name="real_ai_api",
            content="根據計算，結果是42",
            confidence=0.9,
            processing_time=1.2,
            metadata={},
            success=True
        ),
        AdapterResponse(
            adapter_name="mcp_so",
            content="經過分析，答案應該是41或42",
            confidence=0.7,
            processing_time=0.8,
            metadata={},
            success=True
        )
    ]
    
    # 測試不同合成策略
    strategies = ["consensus", "weighted_average", "best_confidence", "majority_vote", "expert_selection"]
    
    for strategy in strategies:
        result = synthesizer.synthesize_answers(test_responses, "What is the answer?", strategy)
        print(f"\n策略: {strategy}")
        print(f"最終答案: {result.final_answer}")
        print(f"置信度: {result.confidence:.2f}")
        print(f"推理: {result.reasoning}")

