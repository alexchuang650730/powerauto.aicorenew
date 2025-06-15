"""
智能工具選擇器 - 基於意圖理解選擇最適合的AI工具

根據用戶問題的特徵，智能選擇以下工具之一或組合：
1. Gemini API - 一般推理和知識問答
2. Claude API - 複雜分析和推理
3. Sequential thinking - 逐步邏輯推理
4. WebAgent - 搜索和事實驗證
5. 混合模式 - 多工具協作
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

class ToolType(Enum):
    """工具類型枚舉"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    SEQUENTIAL_THINKING = "sequential_thinking"
    WEBAGENT = "webagent"
    HYBRID = "hybrid"

class QuestionComplexity(Enum):
    """問題複雜度枚舉"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class IntelligentToolSelector:
    """智能工具選擇器"""
    
    def __init__(self):
        """初始化工具選擇器"""
        self.logger = logging.getLogger(__name__)
        
        # 工具特徵關鍵詞
        self.tool_keywords = {
            ToolType.WEBAGENT: {
                'triggers': [
                    'latest', 'recent', 'current', 'published', 'new',
                    'wikipedia', 'website', 'arxiv', 'google', 'search',
                    'record', 'world record', 'achievement', 'winner',
                    '最新', '當前', '最近', '發布', '網站', '搜索', '查找',
                    '紀錄', '世界紀錄', '成就', '獲勝者', '冠軍'
                ],
                'indicators': [
                    'who is', 'what is the latest', 'current status',
                    'world record', 'fastest time', 'best performance',
                    '誰是', '最新的', '當前狀態', '最近發生',
                    '世界紀錄', '最快時間', '最佳表現'
                ]
            },
            ToolType.SEQUENTIAL_THINKING: {
                'triggers': [
                    'calculate', 'how many', 'step by step', 'solve', 'prove',
                    'computation', 'mathematical', 'formula', 'equation',
                    '計算', '多少', '步驟', '解決', '證明', '數學', '公式', '方程'
                ],
                'indicators': [
                    'step 1', 'first', 'then', 'finally', 'because',
                    'show steps', 'explain process', 'calculation steps',
                    '第一步', '首先', '然後', '最後', '因為', '顯示步驟', '計算過程'
                ]
            },
            ToolType.CLAUDE: {
                'triggers': [
                    'detailed analysis', 'complex analysis', 'comprehensive analysis',
                    'detailed explanation', 'reasoning', 'philosophical', 'ethical', 
                    'critical thinking', 'compare', 'contrast', 'evaluate',
                    'advantages and disadvantages', 'pros and cons', 'differences',
                    '詳細分析', '複雜分析', '全面分析', '詳細解釋', '推理', 
                    '哲學', '倫理', '批判思維', '比較', '對比', '評估',
                    '優缺點', '差異', '區別', '不同', '異同'
                ],
                'indicators': [
                    'explain why', 'what are the implications', 'analyze the impact',
                    'including', 'such as', 'for example', 'detailed',
                    '解釋為什麼', '影響是什麼', '分析影響', '包括', '例如', '詳細'
                ]
            },
            ToolType.GEMINI: {
                'triggers': [
                    'general question', 'simple answer', 'basic information',
                    'definition', 'overview', 'summary',
                    '一般問題', '簡單回答', '基本信息', '定義', '概述', '總結'
                ],
                'indicators': [
                    'what is', 'tell me about', 'explain',
                    '什麼是', '告訴我', '解釋'
                ]
            }
        }
        
        # 複雜度指標
        self.complexity_indicators = {
            QuestionComplexity.SIMPLE: {
                'word_count': (1, 10),
                'keywords': ['what', 'who', 'when', 'where', '什麼', '誰', '何時', '哪裡'],
                'patterns': [r'^(what|who|when|where)\s+is\s+', r'^(什麼|誰|何時|哪裡)']
            },
            QuestionComplexity.MEDIUM: {
                'word_count': (11, 25),
                'keywords': ['how', 'why', 'explain', 'describe', '如何', '為什麼', '解釋', '描述'],
                'patterns': [r'^(how|why)\s+', r'^(如何|為什麼)']
            },
            QuestionComplexity.COMPLEX: {
                'word_count': (26, 50),
                'keywords': ['analyze', 'compare', 'evaluate', 'discuss', '分析', '比較', '評估', '討論'],
                'patterns': [r'(analyze|compare|evaluate)', r'(分析|比較|評估)']
            },
            QuestionComplexity.VERY_COMPLEX: {
                'word_count': (51, float('inf')),
                'keywords': ['comprehensive', 'detailed', 'in-depth', '全面', '詳細', '深入'],
                'patterns': [r'(comprehensive|detailed|in-depth)', r'(全面|詳細|深入)']
            }
        }
        
        # 混合模式觸發條件
        self.hybrid_triggers = [
            'verify and analyze', 'search and explain', 'find and compare',
            '驗證並分析', '搜索並解釋', '查找並比較'
        ]
    
    def select_tool(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        選擇最適合的工具 - 預設使用Hybrid mode，根據意圖選擇主工具
        
        Args:
            question: 用戶問題
            context: 上下文信息
            
        Returns:
            Dict: 工具選擇結果（總是Hybrid mode）
        """
        self.logger.info(f"分析問題並選擇工具: {question[:50]}...")
        
        # 分析問題複雜度
        complexity = self._analyze_complexity(question)
        
        # 預設使用Hybrid mode，根據意圖理解選擇主工具和執行策略
        return self._create_hybrid_strategy(question, complexity, context)
    
    def _analyze_complexity(self, question: str) -> QuestionComplexity:
        """分析問題複雜度"""
        word_count = len(question.split())
        question_lower = question.lower()
        
        for complexity, indicators in self.complexity_indicators.items():
            # 檢查詞數範圍
            min_words, max_words = indicators['word_count']
            if min_words <= word_count <= max_words:
                # 檢查關鍵詞
                for keyword in indicators['keywords']:
                    if keyword in question_lower:
                        return complexity
                
                # 檢查模式
                for pattern in indicators['patterns']:
                    if re.search(pattern, question_lower):
                        return complexity
        
        # 默認為中等複雜度
        return QuestionComplexity.MEDIUM
    
    def _needs_hybrid_mode(self, question: str) -> bool:
        """檢測是否需要混合模式"""
        question_lower = question.lower()
        
        for trigger in self.hybrid_triggers:
            if trigger in question_lower:
                return True
        
        # 檢測多個工具關鍵詞
        tool_matches = 0
        for tool_type, keywords in self.tool_keywords.items():
            for keyword in keywords['triggers']:
                if keyword in question_lower:
                    tool_matches += 1
                    break
        
        return tool_matches >= 2
    
    def _calculate_tool_scores(self, question: str, complexity: QuestionComplexity) -> Dict[ToolType, float]:
        """計算各工具的匹配分數"""
        scores = {tool: 0.0 for tool in ToolType if tool != ToolType.HYBRID}
        question_lower = question.lower()
        
        # 基於關鍵詞計算分數
        for tool_type, keywords in self.tool_keywords.items():
            if tool_type == ToolType.HYBRID:
                continue
                
            # 觸發詞分數
            for trigger in keywords['triggers']:
                if trigger in question_lower:
                    scores[tool_type] += 1.0
            
            # 指示詞分數
            for indicator in keywords['indicators']:
                if indicator in question_lower:
                    scores[tool_type] += 0.5
        
        # 基於複雜度調整分數
        complexity_adjustments = {
            QuestionComplexity.SIMPLE: {
                ToolType.GEMINI: 1.2,
                ToolType.CLAUDE: 0.8,
                ToolType.SEQUENTIAL_THINKING: 0.7,
                ToolType.WEBAGENT: 1.0
            },
            QuestionComplexity.MEDIUM: {
                ToolType.GEMINI: 1.0,
                ToolType.CLAUDE: 1.1,
                ToolType.SEQUENTIAL_THINKING: 1.0,
                ToolType.WEBAGENT: 1.0
            },
            QuestionComplexity.COMPLEX: {
                ToolType.GEMINI: 0.8,
                ToolType.CLAUDE: 1.3,
                ToolType.SEQUENTIAL_THINKING: 1.2,
                ToolType.WEBAGENT: 0.9
            },
            QuestionComplexity.VERY_COMPLEX: {
                ToolType.GEMINI: 0.6,
                ToolType.CLAUDE: 1.5,
                ToolType.SEQUENTIAL_THINKING: 1.4,
                ToolType.WEBAGENT: 0.8
            }
        }
        
        # 應用複雜度調整
        for tool_type in scores:
            scores[tool_type] *= complexity_adjustments[complexity][tool_type]
        
        # 確保至少有一個工具有基礎分數
        if all(score == 0 for score in scores.values()):
            scores[ToolType.GEMINI] = 0.5  # 默認使用Gemini
        
        return scores
    
    def _create_hybrid_strategy(self, question: str, complexity: QuestionComplexity, 
                              context: Optional[Dict] = None) -> Dict[str, Any]:
        """創建混合模式策略 - 根據意圖理解選擇主工具和執行順序"""
        
        # 計算各工具的匹配分數，確定主工具
        tool_scores = self._calculate_tool_scores(question, complexity)
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 選擇主工具（分數最高的）
        primary_tool = sorted_tools[0][0]
        primary_confidence = sorted_tools[0][1]
        
        # 根據問題特徵決定輔助工具
        secondary_tools = self._select_secondary_tools(question, primary_tool, sorted_tools)
        
        # 決定執行順序
        execution_order = self._determine_execution_order(question, primary_tool, secondary_tools)
        
        # 決定組合邏輯
        combination_logic = self._determine_combination_logic(question, primary_tool, secondary_tools)
        
        strategy = {
            'selected_tool': ToolType.HYBRID,
            'confidence': min(0.95, primary_confidence + 0.2),  # Hybrid mode增加信心度
            'complexity': complexity,
            'hybrid_strategy': {
                'primary_tool': primary_tool,
                'secondary_tools': secondary_tools,
                'execution_order': execution_order,
                'combination_logic': combination_logic,
                'tool_scores': dict(sorted_tools)
            },
            'reasoning': self._generate_hybrid_reasoning(question, primary_tool, secondary_tools, complexity),
            'timestamp': datetime.now().isoformat()
        }
        
        return strategy
    
    def _select_secondary_tools(self, question: str, primary_tool: ToolType, 
                               sorted_tools: List[Tuple[ToolType, float]]) -> List[ToolType]:
        """選擇輔助工具"""
        secondary_tools = []
        question_lower = question.lower()
        
        # 根據主工具特徵添加互補工具
        if primary_tool == ToolType.WEBAGENT:
            # WebAgent主導時，添加分析工具
            if any(word in question_lower for word in ['analyze', 'compare', '分析', '比較']):
                secondary_tools.append(ToolType.CLAUDE)
            else:
                secondary_tools.append(ToolType.GEMINI)
                
        elif primary_tool == ToolType.SEQUENTIAL_THINKING:
            # Sequential thinking主導時，可能需要搜索驗證
            if any(word in question_lower for word in ['latest', 'current', 'recent', '最新', '當前']):
                secondary_tools.append(ToolType.WEBAGENT)
            secondary_tools.append(ToolType.CLAUDE)  # 添加深度分析
            
        elif primary_tool == ToolType.CLAUDE:
            # Claude主導時，添加搜索和驗證
            secondary_tools.append(ToolType.WEBAGENT)
            secondary_tools.append(ToolType.GEMINI)
            
        elif primary_tool == ToolType.GEMINI:
            # Gemini主導時，根據複雜度添加工具
            if any(word in question_lower for word in ['verify', 'check', '驗證', '檢查']):
                secondary_tools.append(ToolType.WEBAGENT)
            if len(question.split()) > 15:  # 較複雜的問題
                secondary_tools.append(ToolType.CLAUDE)
        
        # 確保不重複添加主工具
        secondary_tools = [tool for tool in secondary_tools if tool != primary_tool]
        
        # 限制輔助工具數量（最多2個）
        return secondary_tools[:2]
    
    def _determine_execution_order(self, question: str, primary_tool: ToolType, 
                                 secondary_tools: List[ToolType]) -> List[ToolType]:
        """決定執行順序"""
        question_lower = question.lower()
        
        # 如果需要搜索，WebAgent通常先執行
        if ToolType.WEBAGENT in [primary_tool] + secondary_tools:
            if any(word in question_lower for word in ['latest', 'current', 'search', '最新', '搜索']):
                order = [ToolType.WEBAGENT]
                # 添加其他工具
                for tool in [primary_tool] + secondary_tools:
                    if tool != ToolType.WEBAGENT and tool not in order:
                        order.append(tool)
                return order
        
        # 默認順序：主工具 -> 輔助工具
        order = [primary_tool]
        for tool in secondary_tools:
            if tool not in order:
                order.append(tool)
        
        return order
    
    def _determine_combination_logic(self, question: str, primary_tool: ToolType, 
                                   secondary_tools: List[ToolType]) -> str:
        """決定組合邏輯"""
        question_lower = question.lower()
        
        # 檢測並行處理需求
        if any(word in question_lower for word in ['compare', 'versus', 'vs', '比較', '對比']):
            return 'parallel'
        
        # 檢測驗證需求
        if any(word in question_lower for word in ['verify', 'check', 'confirm', '驗證', '檢查', '確認']):
            return 'verification'
        
        # 檢測增強需求
        if any(word in question_lower for word in ['detailed', 'comprehensive', '詳細', '全面']):
            return 'enhancement'
        
        # 默認為順序執行
        return 'sequential'
    
    def _generate_hybrid_reasoning(self, question: str, primary_tool: ToolType, 
                                 secondary_tools: List[ToolType], complexity: QuestionComplexity) -> str:
        """生成混合模式推理說明"""
        tool_names = {
            ToolType.GEMINI: "Gemini",
            ToolType.CLAUDE: "Claude", 
            ToolType.SEQUENTIAL_THINKING: "Sequential thinking",
            ToolType.WEBAGENT: "WebAgent"
        }
        
        primary_name = tool_names[primary_tool]
        secondary_names = [tool_names[tool] for tool in secondary_tools]
        
        reasoning = f"使用Hybrid模式：以{primary_name}為主工具"
        
        if secondary_names:
            reasoning += f"，輔以{', '.join(secondary_names)}"
        
        reasoning += f"。問題複雜度: {complexity.value}，需要多工具協作以確保答案的準確性和完整性。"
        
        return reasoning
    
    def _generate_reasoning(self, question: str, selected_tool: ToolType, 
                          complexity: QuestionComplexity) -> str:
        """生成工具選擇推理"""
        reasoning_templates = {
            ToolType.GEMINI: "問題相對簡單，適合使用Gemini進行一般推理和知識問答",
            ToolType.CLAUDE: "問題需要複雜分析和深度推理，Claude更適合處理此類問題",
            ToolType.SEQUENTIAL_THINKING: "問題需要逐步推理和計算，Sequential thinking能提供詳細的解題步驟",
            ToolType.WEBAGENT: "問題涉及最新信息或需要事實驗證，WebAgent能提供準確的搜索結果",
            ToolType.HYBRID: "問題複雜且需要多種能力，混合模式能提供最佳解決方案"
        }
        
        base_reasoning = reasoning_templates.get(selected_tool, "基於分析選擇的最佳工具")
        complexity_note = f"問題複雜度: {complexity.value}"
        
        return f"{base_reasoning}。{complexity_note}"

# 創建全局實例
tool_selector = IntelligentToolSelector()

def select_best_tool(question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    選擇最適合的工具（全局函數接口）
    
    Args:
        question: 用戶問題
        context: 上下文信息
        
    Returns:
        Dict: 工具選擇結果
    """
    return tool_selector.select_tool(question, context)

if __name__ == "__main__":
    # 測試工具選擇器
    test_questions = [
        "什麼是人工智能？",
        "請分析深度學習和傳統機器學習的區別",
        "Eliud Kipchoge的馬拉松世界紀錄是多少？",
        "請計算1到100的和，並說明計算步驟",
        "搜索並分析最新的AI發展趨勢"
    ]
    
    for question in test_questions:
        result = select_best_tool(question)
        print(f"\n問題: {question}")
        print(f"選擇工具: {result['selected_tool'].value}")
        print(f"信心度: {result['confidence']:.2f}")
        print(f"推理: {result['reasoning']}")

