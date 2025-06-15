"""
意圖理解效果測試 - 綜合測試智能工具選擇和學習反饋系統

測試內容：
1. 智能工具選擇準確性
2. 學習反饋機制效果
3. 兜底機制觸發邏輯
4. MCP工具推薦準確性
"""

import sys
import json
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from intelligent_tool_selector import select_best_tool, ToolType
from learning_feedback_system import (
    record_tool_execution, ExecutionResult, 
    check_fallback_needed, get_mcp_tool_suggestions,
    get_learning_statistics
)

class IntentUnderstandingTester:
    """意圖理解測試器"""
    
    def __init__(self):
        """初始化測試器"""
        self.test_cases = [
            {
                "question": "什麼是機器學習？",
                "expected_primary": ToolType.GEMINI,
                "complexity": "simple",
                "description": "簡單知識問答"
            },
            {
                "question": "請詳細分析深度學習和傳統機器學習的區別，包括算法原理、應用場景和優缺點",
                "expected_primary": ToolType.CLAUDE,
                "complexity": "complex",
                "description": "複雜分析問題"
            },
            {
                "question": "Eliud Kipchoge的最新馬拉松世界紀錄是多少？什麼時候創造的？",
                "expected_primary": ToolType.WEBAGENT,
                "complexity": "medium",
                "description": "需要搜索最新信息"
            },
            {
                "question": "請計算從1加到100的和，並詳細說明計算步驟和數學原理",
                "expected_primary": ToolType.SEQUENTIAL_THINKING,
                "complexity": "medium",
                "description": "需要逐步計算"
            },
            {
                "question": "搜索並分析2024年最新的AI發展趨勢，然後與2023年進行對比",
                "expected_primary": ToolType.WEBAGENT,
                "complexity": "complex",
                "description": "混合模式：搜索+分析"
            },
            {
                "question": "我需要一個能夠自動記錄我每天學習進度的工具",
                "expected_primary": None,  # 可能觸發工具創建
                "complexity": "medium",
                "description": "可能需要新工具"
            }
        ]
        
        self.results = []
    
    def test_tool_selection_accuracy(self):
        """測試工具選擇準確性"""
        print("🎯 測試1: 智能工具選擇準確性")
        print("=" * 50)
        
        correct_selections = 0
        total_tests = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n測試案例 {i}: {test_case['description']}")
            print(f"問題: {test_case['question']}")
            
            # 執行工具選擇
            selection_result = select_best_tool(test_case['question'])
            
            primary_tool = selection_result['hybrid_strategy']['primary_tool']
            secondary_tools = selection_result['hybrid_strategy']['secondary_tools']
            execution_order = selection_result['hybrid_strategy']['execution_order']
            
            print(f"選擇結果:")
            print(f"  主工具: {primary_tool.value}")
            print(f"  輔助工具: {[tool.value for tool in secondary_tools]}")
            print(f"  執行順序: {[tool.value for tool in execution_order]}")
            print(f"  信心度: {selection_result['confidence']:.2f}")
            
            # 檢查準確性
            if test_case['expected_primary']:
                is_correct = primary_tool == test_case['expected_primary']
                correct_selections += 1 if is_correct else 0
                total_tests += 1
                
                status = "✅ 正確" if is_correct else "❌ 錯誤"
                print(f"  預期主工具: {test_case['expected_primary'].value}")
                print(f"  結果: {status}")
            else:
                print(f"  結果: 🔍 需要進一步分析")
            
            # 保存結果
            self.results.append({
                "test_case": test_case,
                "selection_result": selection_result,
                "is_correct": is_correct if test_case['expected_primary'] else None
            })
        
        if total_tests > 0:
            accuracy = correct_selections / total_tests
            print(f"\n📊 工具選擇準確率: {accuracy:.2%} ({correct_selections}/{total_tests})")
        
        return accuracy if total_tests > 0 else 0
    
    def test_learning_feedback(self):
        """測試學習反饋機制"""
        print("\n🧠 測試2: 學習反饋機制")
        print("=" * 50)
        
        # 模擬一些執行結果
        feedback_cases = [
            {
                "question": "什麼是人工智能？",
                "result": ExecutionResult.SUCCESS,
                "score": 0.9,
                "description": "成功案例"
            },
            {
                "question": "最新的量子計算突破是什麼？",
                "result": ExecutionResult.PARTIAL_SUCCESS,
                "score": 0.6,
                "description": "部分成功"
            },
            {
                "question": "幫我創建一個複雜的數據分析報告",
                "result": ExecutionResult.FAILURE,
                "score": 0.2,
                "description": "失敗案例"
            }
        ]
        
        print("記錄執行結果...")
        for case in feedback_cases:
            # 獲取工具選擇
            selection = select_best_tool(case['question'])
            
            # 記錄執行結果
            record_tool_execution(
                question=case['question'],
                tool_selection=selection,
                result=case['result'],
                success_score=case['score'],
                execution_time=1.5
            )
            
            print(f"  {case['description']}: {case['result'].value} (分數: {case['score']})")
        
        # 獲取學習統計
        stats = get_learning_statistics()
        print(f"\n📈 學習統計:")
        print(f"  總記錄數: {stats['total_records']}")
        print(f"  整體成功率: {stats['overall_success_rate']:.2%}")
        print(f"  工具權重更新: {len(stats['tool_weights'])} 個工具")
        
        return stats
    
    def test_fallback_mechanism(self):
        """測試兜底機制"""
        print("\n🛡️ 測試3: 兜底機制觸發")
        print("=" * 50)
        
        # 模擬連續失敗
        failure_cases = [
            "創建一個全新的區塊鏈應用",
            "設計一個火星殖民地的生態系統",
            "發明一個時間旅行裝置"
        ]
        
        print("模擬連續失敗案例...")
        for i, question in enumerate(failure_cases, 1):
            selection = select_best_tool(question)
            
            # 記錄失敗
            record_tool_execution(
                question=question,
                tool_selection=selection,
                result=ExecutionResult.COMPLETE_FAILURE,
                success_score=0.0,
                execution_time=2.0,
                error_message="所有工具都無法處理此問題"
            )
            
            print(f"  失敗案例 {i}: {question[:30]}...")
        
        # 檢查兜底機制
        fallback_check = check_fallback_needed(
            question="創建一個革命性的AI系統",
            failed_tools=["gemini", "claude", "sequential_thinking", "webagent"]
        )
        
        print(f"\n🔍 兜底機制檢查:")
        print(f"  是否觸發兜底: {fallback_check['should_fallback']}")
        
        if fallback_check['should_fallback']:
            strategy = fallback_check['fallback_strategy']
            print(f"  建議策略: {strategy['strategy']}")
            print(f"  處理層級: 第{strategy['level']}層")
            print(f"  描述: {strategy['description']}")
            
            if 'recommended_tools' in strategy:
                print(f"  推薦MCP工具: {strategy['recommended_tools']}")
            elif 'recommended_services' in strategy:
                print(f"  推薦外部服務: {strategy['recommended_services']}")
        
        return fallback_check
    
    def test_mcp_tool_recommendations(self):
        """測試MCP工具推薦"""
        print("\n🔧 測試4: MCP工具推薦")
        print("=" * 50)
        
        mcp_test_cases = [
            {
                "question": "我需要處理一個非常長的文檔，包含複雜的上下文關係",
                "failed_tools": ["gemini", "claude"],
                "expected_mcp": "infinite_context_adapter"
            },
            {
                "question": "幫我設計一個自動化的工作流程來處理日常任務",
                "failed_tools": ["webagent"],
                "expected_mcp": "intelligent_workflow_engine"
            },
            {
                "question": "我想要系統能夠記住我們之前的所有對話並從中學習",
                "failed_tools": ["sequential_thinking"],
                "expected_mcp": "supermemory_adapter"
            }
        ]
        
        for i, test_case in enumerate(mcp_test_cases, 1):
            print(f"\nMCP推薦案例 {i}:")
            print(f"問題: {test_case['question']}")
            print(f"已失敗工具: {test_case['failed_tools']}")
            
            recommendations = get_mcp_tool_suggestions(
                test_case['question'], 
                test_case['failed_tools']
            )
            
            print(f"推薦結果:")
            for j, rec in enumerate(recommendations, 1):
                print(f"  {j}. {rec['tool_name']}")
                print(f"     匹配分數: {rec['match_score']}")
                print(f"     匹配關鍵詞: {rec['matched_keywords']}")
                print(f"     描述: {rec['description']}")
                print(f"     信心度: {rec['confidence']:.2f}")
            
            # 檢查是否包含預期的MCP工具
            recommended_tools = [rec['tool_name'] for rec in recommendations]
            if test_case['expected_mcp'] in recommended_tools:
                print(f"  ✅ 正確推薦了 {test_case['expected_mcp']}")
            else:
                print(f"  ❌ 未推薦預期的 {test_case['expected_mcp']}")
        
        return recommendations
    
    def run_comprehensive_test(self):
        """運行綜合測試"""
        print("🚀 PowerAutomation 意圖理解效果綜合測試")
        print("=" * 60)
        
        # 執行所有測試
        accuracy = self.test_tool_selection_accuracy()
        learning_stats = self.test_learning_feedback()
        fallback_result = self.test_fallback_mechanism()
        mcp_recommendations = self.test_mcp_tool_recommendations()
        
        # 生成測試報告
        print("\n📋 測試總結報告")
        print("=" * 60)
        print(f"✅ 工具選擇準確率: {accuracy:.2%}")
        print(f"🧠 學習記錄數量: {learning_stats['total_records']}")
        print(f"🛡️ 兜底機制: {'正常工作' if fallback_result['should_fallback'] else '待觸發'}")
        print(f"🔧 MCP推薦功能: {'正常工作' if mcp_recommendations else '需要改進'}")
        
        # 整體評分
        overall_score = (
            accuracy * 0.4 +  # 工具選擇40%
            (1.0 if learning_stats['total_records'] > 0 else 0.0) * 0.3 +  # 學習機制30%
            (1.0 if fallback_result['should_fallback'] else 0.5) * 0.2 +  # 兜底機制20%
            (1.0 if mcp_recommendations else 0.0) * 0.1  # MCP推薦10%
        )
        
        print(f"\n🎯 整體評分: {overall_score:.2%}")
        
        if overall_score >= 0.8:
            print("🎉 意圖理解系統表現優秀！")
        elif overall_score >= 0.6:
            print("👍 意圖理解系統表現良好，有改進空間")
        else:
            print("⚠️ 意圖理解系統需要進一步優化")
        
        return {
            "accuracy": accuracy,
            "learning_stats": learning_stats,
            "fallback_result": fallback_result,
            "mcp_recommendations": mcp_recommendations,
            "overall_score": overall_score
        }

if __name__ == "__main__":
    tester = IntentUnderstandingTester()
    results = tester.run_comprehensive_test()

