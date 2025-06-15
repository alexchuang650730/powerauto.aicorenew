"""
學習反饋系統 - 觀察成功失敗原因，優化意圖理解和工具選擇

核心功能：
1. 記錄每次工具選擇的結果
2. 分析成功失敗的原因
3. 動態調整工具選擇權重
4. 讓成功率高的工具組合優先排序
"""

import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict

class ExecutionResult(Enum):
    """執行結果枚舉"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    COMPLETE_FAILURE = "complete_failure"
    FALLBACK_TRIGGERED = "fallback_triggered"  # 觸發兜底機制

@dataclass
class ToolExecutionRecord:
    """工具執行記錄"""
    question_hash: str
    question: str
    selected_tools: List[str]
    execution_order: List[str]
    primary_tool: str
    secondary_tools: List[str]
    result: ExecutionResult
    success_score: float  # 0.0 - 1.0
    execution_time: float
    error_message: Optional[str]
    user_feedback: Optional[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = asdict(self)
        # 轉換枚舉為字符串
        data['result'] = self.result.value
        return data

class LearningFeedbackSystem:
    """學習反饋系統"""
    
    def __init__(self, data_dir: str = "data/learning_feedback"):
        """初始化學習反饋系統"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.records_file = self.data_dir / "execution_records.jsonl"
        self.weights_file = self.data_dir / "tool_weights.json"
        self.patterns_file = self.data_dir / "success_patterns.json"
        
        self.logger = logging.getLogger(__name__)
        
        # 載入歷史數據
        self.execution_records: List[ToolExecutionRecord] = []
        self.tool_weights: Dict[str, float] = {}
        self.success_patterns: Dict[str, Any] = {}
        
        self._load_data()
        
        # 學習參數
        self.learning_rate = 0.1
        self.min_samples_for_learning = 3
        self.weight_decay = 0.95  # 舊記錄的權重衰減
    
    def _load_data(self):
        """載入歷史數據"""
        try:
            # 載入執行記錄
            if self.records_file.exists():
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            record_dict = json.loads(line)
                            # 轉換result字符串回枚舉
                            record_dict['result'] = ExecutionResult(record_dict['result'])
                            record = ToolExecutionRecord(**record_dict)
                            self.execution_records.append(record)
            
            # 載入工具權重
            if self.weights_file.exists():
                with open(self.weights_file, 'r', encoding='utf-8') as f:
                    self.tool_weights = json.load(f)
            
            # 載入成功模式
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.success_patterns = json.load(f)
                    
            self.logger.info(f"載入了 {len(self.execution_records)} 條執行記錄")
            
        except Exception as e:
            self.logger.error(f"載入數據失敗: {e}")
    
    def _save_data(self):
        """保存數據"""
        try:
            # 保存執行記錄（追加模式）
            with open(self.records_file, 'a', encoding='utf-8') as f:
                # 只保存最新的記錄
                if self.execution_records:
                    latest_record = self.execution_records[-1]
                    f.write(json.dumps(latest_record.to_dict(), ensure_ascii=False) + '\n')
            
            # 保存工具權重
            with open(self.weights_file, 'w', encoding='utf-8') as f:
                json.dump(self.tool_weights, f, ensure_ascii=False, indent=2)
            
            # 保存成功模式
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.success_patterns, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存數據失敗: {e}")
    
    def record_execution(self, question: str, tool_selection: Dict[str, Any], 
                        result: ExecutionResult, success_score: float,
                        execution_time: float, error_message: Optional[str] = None,
                        user_feedback: Optional[str] = None):
        """記錄工具執行結果"""
        
        # 生成問題哈希
        question_hash = hashlib.md5(question.encode('utf-8')).hexdigest()
        
        # 提取工具信息
        hybrid_strategy = tool_selection.get('hybrid_strategy', {})
        primary_tool = hybrid_strategy.get('primary_tool', 'unknown')
        secondary_tools = hybrid_strategy.get('secondary_tools', [])
        execution_order = hybrid_strategy.get('execution_order', [])
        
        # 轉換工具名稱為字符串
        if hasattr(primary_tool, 'value'):
            primary_tool = primary_tool.value
        secondary_tools = [tool.value if hasattr(tool, 'value') else str(tool) for tool in secondary_tools]
        execution_order = [tool.value if hasattr(tool, 'value') else str(tool) for tool in execution_order]
        
        # 創建執行記錄
        record = ToolExecutionRecord(
            question_hash=question_hash,
            question=question,
            selected_tools=[primary_tool] + secondary_tools,
            execution_order=execution_order,
            primary_tool=primary_tool,
            secondary_tools=secondary_tools,
            result=result,
            success_score=success_score,
            execution_time=execution_time,
            error_message=error_message,
            user_feedback=user_feedback,
            timestamp=datetime.now().isoformat()
        )
        
        # 添加到記錄列表
        self.execution_records.append(record)
        
        # 觸發學習
        self._learn_from_record(record)
        
        # 保存數據
        self._save_data()
        
        self.logger.info(f"記錄執行結果: {result.value}, 成功分數: {success_score}")
    
    def _learn_from_record(self, record: ToolExecutionRecord):
        """從單個記錄中學習"""
        
        # 更新工具權重
        self._update_tool_weights(record)
        
        # 更新成功模式
        self._update_success_patterns(record)
        
        # 清理舊記錄（保留最近1000條）
        if len(self.execution_records) > 1000:
            self.execution_records = self.execution_records[-1000:]
    
    def _update_tool_weights(self, record: ToolExecutionRecord):
        """更新工具權重"""
        
        # 為每個工具更新權重
        for tool in record.selected_tools:
            if tool not in self.tool_weights:
                self.tool_weights[tool] = 1.0
            
            # 根據成功分數調整權重
            if record.result in [ExecutionResult.SUCCESS, ExecutionResult.PARTIAL_SUCCESS]:
                # 成功時增加權重
                adjustment = self.learning_rate * record.success_score
                self.tool_weights[tool] += adjustment
            else:
                # 失敗時減少權重
                adjustment = self.learning_rate * (1 - record.success_score)
                self.tool_weights[tool] = max(0.1, self.tool_weights[tool] - adjustment)
        
        # 應用權重衰減到所有工具
        for tool in self.tool_weights:
            self.tool_weights[tool] *= self.weight_decay
            self.tool_weights[tool] = max(0.1, self.tool_weights[tool])  # 最小權重
    
    def _update_success_patterns(self, record: ToolExecutionRecord):
        """更新成功模式"""
        
        # 提取問題特徵
        question_features = self._extract_question_features(record.question)
        
        # 創建模式鍵
        pattern_key = f"{record.primary_tool}_{len(record.secondary_tools)}"
        
        if pattern_key not in self.success_patterns:
            self.success_patterns[pattern_key] = {
                'total_count': 0,
                'success_count': 0,
                'success_rate': 0.0,
                'avg_score': 0.0,
                'question_features': {},
                'best_combinations': []
            }
        
        pattern = self.success_patterns[pattern_key]
        pattern['total_count'] += 1
        
        if record.result in [ExecutionResult.SUCCESS, ExecutionResult.PARTIAL_SUCCESS]:
            pattern['success_count'] += 1
        
        # 更新成功率
        pattern['success_rate'] = pattern['success_count'] / pattern['total_count']
        
        # 更新平均分數
        pattern['avg_score'] = (pattern['avg_score'] * (pattern['total_count'] - 1) + record.success_score) / pattern['total_count']
        
        # 更新問題特徵統計
        for feature, value in question_features.items():
            if feature not in pattern['question_features']:
                pattern['question_features'][feature] = {}
            if value not in pattern['question_features'][feature]:
                pattern['question_features'][feature][value] = 0
            pattern['question_features'][feature][value] += 1
    
    def _extract_question_features(self, question: str) -> Dict[str, str]:
        """提取問題特徵"""
        question_lower = question.lower()
        
        features = {
            'length': 'short' if len(question.split()) < 10 else 'medium' if len(question.split()) < 25 else 'long',
            'has_search_keywords': 'yes' if any(word in question_lower for word in ['latest', 'current', 'search', '最新', '搜索']) else 'no',
            'has_calculation': 'yes' if any(word in question_lower for word in ['calculate', 'compute', '計算']) else 'no',
            'has_analysis': 'yes' if any(word in question_lower for word in ['analyze', 'compare', '分析', '比較']) else 'no',
            'language': 'chinese' if any('\u4e00' <= char <= '\u9fff' for char in question) else 'english'
        }
        
        return features
    
    def get_optimized_tool_weights(self, question: str) -> Dict[str, float]:
        """獲取針對特定問題優化的工具權重"""
        
        # 基礎權重
        base_weights = self.tool_weights.copy()
        
        # 如果沒有足夠的學習數據，返回默認權重
        if len(self.execution_records) < self.min_samples_for_learning:
            return {
                'gemini': 1.0,
                'claude': 1.0,
                'sequential_thinking': 1.0,
                'webagent': 1.0
            }
        
        # 根據問題特徵調整權重
        question_features = self._extract_question_features(question)
        
        # 查找相似問題的成功模式
        for pattern_key, pattern in self.success_patterns.items():
            if pattern['success_rate'] > 0.7:  # 只考慮成功率高的模式
                # 檢查問題特徵匹配度
                feature_match_score = self._calculate_feature_match(question_features, pattern['question_features'])
                
                if feature_match_score > 0.6:  # 特徵匹配度閾值
                    # 提取主工具並增加權重
                    primary_tool = pattern_key.split('_')[0]
                    if primary_tool in base_weights:
                        base_weights[primary_tool] *= (1 + feature_match_score * pattern['success_rate'])
        
        return base_weights
    
    def _calculate_feature_match(self, question_features: Dict[str, str], 
                                pattern_features: Dict[str, Dict[str, int]]) -> float:
        """計算特徵匹配度"""
        matches = 0
        total_features = len(question_features)
        
        for feature, value in question_features.items():
            if feature in pattern_features and value in pattern_features[feature]:
                # 根據該特徵值在模式中的頻率計算匹配分數
                feature_total = sum(pattern_features[feature].values())
                feature_frequency = pattern_features[feature][value] / feature_total
                matches += feature_frequency
        
        return matches / total_features if total_features > 0 else 0.0
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """獲取學習統計信息"""
        if not self.execution_records:
            return {"message": "沒有執行記錄"}
        
        # 計算總體統計
        total_records = len(self.execution_records)
        success_records = len([r for r in self.execution_records if r.result in [ExecutionResult.SUCCESS, ExecutionResult.PARTIAL_SUCCESS]])
        overall_success_rate = success_records / total_records
        
        # 計算各工具的統計
        tool_stats = {}
        for record in self.execution_records:
            for tool in record.selected_tools:
                if tool not in tool_stats:
                    tool_stats[tool] = {'total': 0, 'success': 0, 'avg_score': 0.0}
                
                tool_stats[tool]['total'] += 1
                if record.result in [ExecutionResult.SUCCESS, ExecutionResult.PARTIAL_SUCCESS]:
                    tool_stats[tool]['success'] += 1
                tool_stats[tool]['avg_score'] += record.success_score
        
        # 計算平均分數和成功率
        for tool in tool_stats:
            tool_stats[tool]['success_rate'] = tool_stats[tool]['success'] / tool_stats[tool]['total']
            tool_stats[tool]['avg_score'] /= tool_stats[tool]['total']
        
        return {
            'total_records': total_records,
            'overall_success_rate': overall_success_rate,
            'tool_weights': self.tool_weights,
            'tool_stats': tool_stats,
            'success_patterns_count': len(self.success_patterns),
            'recent_records': [r.to_dict() for r in self.execution_records[-5:]]  # 最近5條記錄
        }

# 創建全局實例
learning_system = LearningFeedbackSystem()

def record_tool_execution(question: str, tool_selection: Dict[str, Any], 
                         result: ExecutionResult, success_score: float,
                         execution_time: float, error_message: Optional[str] = None,
                         user_feedback: Optional[str] = None):
    """記錄工具執行結果（全局函數接口）"""
    return learning_system.record_execution(
        question, tool_selection, result, success_score, 
        execution_time, error_message, user_feedback
    )

def get_optimized_weights(question: str) -> Dict[str, float]:
    """獲取優化的工具權重（全局函數接口）"""
    return learning_system.get_optimized_tool_weights(question)

def get_learning_statistics() -> Dict[str, Any]:
    """獲取學習統計信息（全局函數接口）"""
    return learning_system.get_learning_stats()

if __name__ == "__main__":
    # 測試學習反饋系統
    from intelligent_tool_selector import ToolType
    
    # 模擬一些執行記錄
    test_cases = [
        {
            'question': '什麼是人工智能？',
            'tool_selection': {
                'hybrid_strategy': {
                    'primary_tool': ToolType.GEMINI,
                    'secondary_tools': [],
                    'execution_order': [ToolType.GEMINI]
                }
            },
            'result': ExecutionResult.SUCCESS,
            'success_score': 0.9
        },
        {
            'question': 'Eliud Kipchoge的馬拉松世界紀錄是多少？',
            'tool_selection': {
                'hybrid_strategy': {
                    'primary_tool': ToolType.WEBAGENT,
                    'secondary_tools': [ToolType.GEMINI],
                    'execution_order': [ToolType.WEBAGENT, ToolType.GEMINI]
                }
            },
            'result': ExecutionResult.SUCCESS,
            'success_score': 1.0
        }
    ]
    
    # 記錄測試案例
    for case in test_cases:
        record_tool_execution(
            case['question'],
            case['tool_selection'],
            case['result'],
            case['success_score'],
            1.5  # 執行時間
        )
    
    # 顯示學習統計
    stats = get_learning_statistics()
    print("學習統計信息:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


# 添加兜底機制檢查函數
def check_fallback_needed(question: str, failed_tools: List[str] = None) -> Dict[str, Any]:
    """檢查是否需要觸發兜底機制（全局函數接口）"""
    fallback_check = learning_system.should_trigger_fallback()
    
    if failed_tools:
        mcp_recommendations = learning_system.get_mcp_tool_recommendations(question, failed_tools)
        fallback_check["mcp_recommendations"] = mcp_recommendations
    
    return fallback_check

def get_mcp_tool_suggestions(question: str, failed_tools: List[str]) -> List[Dict[str, Any]]:
    """獲取MCP工具建議（全局函數接口）"""
    return learning_system.get_mcp_tool_recommendations(question, failed_tools)

