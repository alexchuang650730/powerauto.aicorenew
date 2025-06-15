"""
智能工具選擇器v3.0 - 改進工具選擇邏輯和搜索策略

基於兜底機制v3.0的成功，進一步改進主要工具的選擇邏輯
目標：減少需要兜底的情況，提高首次成功率
"""

import re
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ToolType(Enum):
    """工具類型枚舉"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    SEQUENTIAL_THINKING = "sequential_thinking"
    WEBAGENT = "webagent"
    HYBRID = "hybrid"

@dataclass
class ToolSelection:
    """工具選擇結果"""
    primary_tool: ToolType
    secondary_tools: List[ToolType]
    confidence: float
    reasoning: str
    strategy: str

class EnhancedToolSelectorV3:
    """增強工具選擇器v3.0"""
    
    def __init__(self):
        """初始化選擇器"""
        self.tool_capabilities = self._build_tool_capabilities()
        self.question_patterns = self._build_question_patterns()
        self.success_history = self._load_success_history()
        
    def _build_tool_capabilities(self) -> Dict[ToolType, Dict[str, Any]]:
        """構建工具能力矩陣"""
        return {
            ToolType.GEMINI: {
                "strengths": ["simple_qa", "general_knowledge", "definitions", "explanations"],
                "weaknesses": ["complex_analysis", "real_time_data", "calculations"],
                "optimal_question_length": (5, 20),  # 詞數範圍
                "confidence_factors": {
                    "simple_qa": 0.95,
                    "general_knowledge": 0.90,
                    "definitions": 0.92,
                    "short_questions": 0.88
                }
            },
            ToolType.CLAUDE: {
                "strengths": ["complex_analysis", "detailed_comparison", "reasoning", "long_form"],
                "weaknesses": ["real_time_data", "simple_facts", "calculations"],
                "optimal_question_length": (15, 50),
                "confidence_factors": {
                    "complex_analysis": 0.92,
                    "detailed_comparison": 0.90,
                    "reasoning": 0.88,
                    "long_questions": 0.85
                }
            },
            ToolType.SEQUENTIAL_THINKING: {
                "strengths": ["calculations", "step_by_step", "logical_reasoning", "math"],
                "weaknesses": ["creative_writing", "subjective_analysis", "real_time_data"],
                "optimal_question_length": (10, 30),
                "confidence_factors": {
                    "calculations": 0.96,
                    "step_by_step": 0.90,
                    "logical_reasoning": 0.88,
                    "math": 0.94
                }
            },
            ToolType.WEBAGENT: {
                "strengths": ["real_time_data", "current_facts", "search_required", "verification"],
                "weaknesses": ["abstract_concepts", "calculations", "analysis"],
                "optimal_question_length": (8, 25),
                "confidence_factors": {
                    "real_time_data": 0.88,
                    "current_facts": 0.85,
                    "search_required": 0.82,
                    "verification": 0.80
                }
            }
        }
    
    def _build_question_patterns(self) -> Dict[str, Dict[str, Any]]:
        """構建問題模式識別"""
        return {
            "simple_qa": {
                "patterns": [
                    r"what is\s+\w+\?",
                    r"define\s+\w+",
                    r"explain\s+\w+",
                    r"meaning of\s+\w+"
                ],
                "keywords": ["what is", "define", "explain", "meaning", "describe"],
                "length_range": (3, 15),
                "preferred_tool": ToolType.GEMINI,
                "confidence_boost": 0.1
            },
            "complex_analysis": {
                "patterns": [
                    r"analyze.*compare",
                    r"detailed.*analysis",
                    r"advantages.*disadvantages",
                    r"pros.*cons",
                    r"difference.*between"
                ],
                "keywords": ["analyze", "compare", "detailed", "advantages", "disadvantages", 
                           "pros", "cons", "difference", "contrast", "evaluate"],
                "length_range": (15, 100),
                "preferred_tool": ToolType.CLAUDE,
                "confidence_boost": 0.15
            },
            "calculation": {
                "patterns": [
                    r"calculate.*\d+",
                    r"compute.*result",
                    r"solve.*equation",
                    r"sum.*\d+.*\d+",
                    r"formula.*\w+"
                ],
                "keywords": ["calculate", "compute", "solve", "sum", "formula", 
                           "equation", "result", "math", "number"],
                "length_range": (5, 30),
                "preferred_tool": ToolType.SEQUENTIAL_THINKING,
                "confidence_boost": 0.2
            },
            "real_time_search": {
                "patterns": [
                    r"current.*record",
                    r"latest.*\w+",
                    r"recent.*\w+",
                    r"world record.*\w+",
                    r"who is.*currently"
                ],
                "keywords": ["current", "latest", "recent", "record", "now", 
                           "today", "this year", "currently"],
                "length_range": (5, 25),
                "preferred_tool": ToolType.WEBAGENT,
                "confidence_boost": 0.12
            },
            "academic_paper": {
                "patterns": [
                    r"paper.*university",
                    r"research.*study",
                    r"journal.*article",
                    r"academic.*publication"
                ],
                "keywords": ["paper", "research", "study", "university", "journal", 
                           "academic", "publication", "scholar", "arxiv"],
                "length_range": (10, 50),
                "preferred_tool": ToolType.WEBAGENT,  # 改為WebAgent，因為需要搜索
                "confidence_boost": 0.1
            }
        }
    
    def _load_success_history(self) -> Dict[str, float]:
        """載入成功歷史（模擬）"""
        return {
            "gemini_simple_qa": 0.95,
            "claude_complex_analysis": 0.88,
            "sequential_thinking_calculation": 0.92,
            "webagent_real_time": 0.85,
            "webagent_academic": 0.78
        }
    
    def analyze_question_features(self, question: str) -> Dict[str, Any]:
        """分析問題特徵"""
        question_lower = question.lower()
        word_count = len(question.split())
        
        features = {
            "word_count": word_count,
            "question_length": "short" if word_count < 10 else "medium" if word_count < 25 else "long",
            "has_numbers": bool(re.search(r'\d+', question)),
            "has_comparison": any(word in question_lower for word in ["vs", "versus", "compare", "difference"]),
            "has_calculation": any(word in question_lower for word in ["calculate", "compute", "sum", "formula"]),
            "has_time_reference": any(word in question_lower for word in ["current", "latest", "recent", "now"]),
            "has_academic_reference": any(word in question_lower for word in ["paper", "research", "university", "study"]),
            "question_type": self._identify_question_type(question_lower),
            "complexity_score": self._calculate_complexity(question, word_count)
        }
        
        return features
    
    def _identify_question_type(self, question_lower: str) -> str:
        """識別問題類型"""
        for pattern_name, pattern_info in self.question_patterns.items():
            # 檢查正則表達式模式
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, question_lower):
                    return pattern_name
            
            # 檢查關鍵詞
            keyword_matches = sum(1 for keyword in pattern_info["keywords"] 
                                if keyword in question_lower)
            if keyword_matches >= 2:  # 至少匹配2個關鍵詞
                return pattern_name
        
        return "general"
    
    def _calculate_complexity(self, question: str, word_count: int) -> float:
        """計算問題複雜度"""
        complexity = 0.0
        question_lower = question.lower()
        
        # 基於長度的複雜度
        if word_count > 30:
            complexity += 0.3
        elif word_count > 15:
            complexity += 0.2
        elif word_count < 8:
            complexity += 0.1  # 太短也可能複雜
        
        # 基於內容的複雜度
        complexity_indicators = [
            ("analyze", 0.2), ("compare", 0.2), ("evaluate", 0.2),
            ("detailed", 0.15), ("comprehensive", 0.15),
            ("advantages", 0.1), ("disadvantages", 0.1),
            ("multiple", 0.1), ("various", 0.1)
        ]
        
        for indicator, weight in complexity_indicators:
            if indicator in question_lower:
                complexity += weight
        
        return min(complexity, 1.0)  # 限制在0-1範圍
    
    def calculate_tool_confidence(self, tool: ToolType, features: Dict[str, Any]) -> float:
        """計算工具信心度"""
        tool_info = self.tool_capabilities[tool]
        base_confidence = 0.5
        
        # 基於問題類型的信心度
        question_type = features["question_type"]
        if question_type in tool_info["confidence_factors"]:
            base_confidence = tool_info["confidence_factors"][question_type]
        
        # 基於問題長度的調整
        word_count = features["word_count"]
        optimal_range = tool_info["optimal_question_length"]
        if optimal_range[0] <= word_count <= optimal_range[1]:
            length_bonus = 0.05
        else:
            length_penalty = min(0.1, abs(word_count - optimal_range[1]) * 0.01)
            length_bonus = -length_penalty
        
        # 基於工具優勢的調整
        strength_bonus = 0.0
        for strength in tool_info["strengths"]:
            if strength in features["question_type"] or any(
                keyword in strength for keyword in features.get("keywords", [])
            ):
                strength_bonus += 0.08
        
        # 基於歷史成功率的調整
        history_key = f"{tool.value}_{question_type}"
        history_bonus = (self.success_history.get(history_key, 0.7) - 0.7) * 0.2
        
        # 複雜度調整
        complexity_adjustment = -features["complexity_score"] * 0.1
        
        final_confidence = base_confidence + length_bonus + strength_bonus + history_bonus + complexity_adjustment
        return max(0.1, min(0.98, final_confidence))  # 限制在0.1-0.98範圍
    
    def select_optimal_tool(self, question: str) -> ToolSelection:
        """選擇最優工具"""
        features = self.analyze_question_features(question)
        
        # 計算每個工具的信心度
        tool_confidences = {}
        for tool in ToolType:
            if tool != ToolType.HYBRID:  # 暫時跳過HYBRID
                confidence = self.calculate_tool_confidence(tool, features)
                tool_confidences[tool] = confidence
        
        # 排序工具
        sorted_tools = sorted(tool_confidences.items(), key=lambda x: x[1], reverse=True)
        
        # 選擇主要工具
        primary_tool, primary_confidence = sorted_tools[0]
        
        # 選擇輔助工具
        secondary_tools = [tool for tool, _ in sorted_tools[1:3]]
        
        # 生成推理說明
        reasoning = self._generate_reasoning(features, primary_tool, primary_confidence)
        
        # 確定策略
        strategy = self._determine_strategy(primary_confidence, features)
        
        return ToolSelection(
            primary_tool=primary_tool,
            secondary_tools=secondary_tools,
            confidence=primary_confidence,
            reasoning=reasoning,
            strategy=strategy
        )
    
    def _generate_reasoning(self, features: Dict[str, Any], tool: ToolType, confidence: float) -> str:
        """生成推理說明"""
        question_type = features["question_type"]
        word_count = features["word_count"]
        
        reasoning_parts = [
            f"問題類型: {question_type}",
            f"問題長度: {word_count}詞 ({features['question_length']})",
            f"複雜度: {features['complexity_score']:.2f}",
            f"選擇 {tool.value}: 信心度 {confidence:.2%}"
        ]
        
        if features["has_calculation"]:
            reasoning_parts.append("包含計算需求")
        if features["has_time_reference"]:
            reasoning_parts.append("需要實時信息")
        if features["has_academic_reference"]:
            reasoning_parts.append("涉及學術內容")
        
        return " | ".join(reasoning_parts)
    
    def _determine_strategy(self, confidence: float, features: Dict[str, Any]) -> str:
        """確定執行策略"""
        if confidence >= 0.85:
            return "direct_execution"  # 直接執行
        elif confidence >= 0.70:
            return "monitored_execution"  # 監控執行
        elif confidence >= 0.55:
            return "backup_ready"  # 準備備用方案
        else:
            return "immediate_fallback"  # 立即兜底

def test_enhanced_tool_selector():
    """測試增強工具選擇器"""
    print("🧪 測試增強工具選擇器v3.0")
    print("=" * 60)
    
    selector = EnhancedToolSelectorV3()
    
    test_cases = [
        "什麼是人工智能？",
        "請詳細分析深度學習和傳統機器學習的區別，包括算法原理、應用場景和優缺點",
        "What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper?",
        "Eliud Kipchoge的馬拉松世界紀錄是多少？",
        "請計算1到100的和，並說明計算步驟"
    ]
    
    results = []
    for i, question in enumerate(test_cases, 1):
        print(f"\n🧪 測試案例 {i}: {question[:40]}...")
        selection = selector.select_optimal_tool(question)
        results.append(selection)
        
        print(f"🎯 主要工具: {selection.primary_tool.value}")
        print(f"📈 信心度: {selection.confidence:.2%}")
        print(f"🔄 策略: {selection.strategy}")
        print(f"🧠 推理: {selection.reasoning}")
        print(f"🔧 備用工具: {[t.value for t in selection.secondary_tools]}")
    
    # 統計結果
    high_confidence_count = sum(1 for r in results if r.confidence >= 0.8)
    avg_confidence = sum(r.confidence for r in results) / len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 增強工具選擇器測試結果:")
    print(f"平均信心度: {avg_confidence:.2%}")
    print(f"高信心度案例: {high_confidence_count}/{len(results)} ({high_confidence_count/len(results):.1%})")
    print(f"預期減少兜底: {'✅ 是' if avg_confidence >= 0.75 else '❌ 否'}")
    
    return avg_confidence

if __name__ == "__main__":
    test_enhanced_tool_selector()

