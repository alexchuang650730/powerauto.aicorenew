"""
更新工具分類系統 - 集成ArXiv MCP服務器

基於mcp.so發現的ArXiv相關MCP服務器，更新工具分類和選擇邏輯
"""

from mcptool.adapters.tool_classification_system import (
    ToolCategory, ToolComplexity, ToolDomain, ToolInfo, 
    classification_system
)

def update_arxiv_tools():
    """更新ArXiv相關工具到分類系統"""
    
    # 添加ArXiv MCP服務器工具
    arxiv_tools = {
        "arxiv_search_mcp": ToolInfo(
            name="arxiv_search_mcp",
            category=ToolCategory.MCP_SO_SERVICES,
            complexity=ToolComplexity.MEDIUM,
            domains=[ToolDomain.RESEARCH],
            keywords=["arxiv", "academic", "paper", "research", "論文", "學術", "研究"],
            description="ArXiv搜索MCP服務器 - 用自然語言查詢搜索學術論文",
            use_cases=["學術論文搜索", "研究文獻查找", "科學論文檢索"],
            fallback_order=1
        ),
        
        "arxiv_mcp_server": ToolInfo(
            name="arxiv_mcp_server", 
            category=ToolCategory.MCP_SO_SERVICES,
            complexity=ToolComplexity.MEDIUM,
            domains=[ToolDomain.RESEARCH],
            keywords=["arxiv", "academic", "streamlined", "論文", "學術", "流線型"],
            description="ArXiv MCP服務器 - 連接AI助手到arXiv龐大的學術論文集合",
            use_cases=["學術資源訪問", "論文內容分析", "研究數據提取"],
            fallback_order=2
        ),
        
        "myarxivdb_mcp": ToolInfo(
            name="myarxivdb_mcp",
            category=ToolCategory.MCP_SO_SERVICES, 
            complexity=ToolComplexity.COMPLEX,
            domains=[ToolDomain.RESEARCH],
            keywords=["arxiv", "database", "personal", "論文", "數據庫", "個人"],
            description="MyArXivDB MCP服務器 - 個人化ArXiv數據庫管理",
            use_cases=["個人論文庫管理", "研究追蹤", "學術收藏"],
            fallback_order=3
        ),
        
        "openedu_mcp": ToolInfo(
            name="openedu_mcp",
            category=ToolCategory.MCP_SO_SERVICES,
            complexity=ToolComplexity.MEDIUM, 
            domains=[ToolDomain.RESEARCH],
            keywords=["education", "open", "academic", "教育", "開放", "學術"],
            description="OpenEdu MCP服務器 - 開放教育資源訪問",
            use_cases=["教育資源搜索", "開放課程", "學習材料"],
            fallback_order=4
        ),
        
        "mcp_arxiv_chatbot": ToolInfo(
            name="mcp_arxiv_chatbot",
            category=ToolCategory.MCP_SO_SERVICES,
            complexity=ToolComplexity.SIMPLE,
            domains=[ToolDomain.CONVERSATION, ToolDomain.RESEARCH],
            keywords=["chatbot", "arxiv", "conversation", "聊天機器人", "對話"],
            description="ArXiv聊天機器人 - 對話式學術論文查詢",
            use_cases=["對話式論文搜索", "學術問答", "研究助手"],
            fallback_order=5
        )
    }
    
    # 將新工具添加到分類系統
    for tool_name, tool_info in arxiv_tools.items():
        classification_system.tool_registry[tool_name] = tool_info
    
    # 重建分類層次結構
    classification_system.category_hierarchy = classification_system._build_category_hierarchy()
    
    print(f"✅ 已添加 {len(arxiv_tools)} 個ArXiv MCP工具到分類系統")
    return arxiv_tools

def get_academic_paper_recommendations(question: str) -> list:
    """為學術論文問題提供工具推薦"""
    question_lower = question.lower()
    
    # 學術論文關鍵詞
    academic_keywords = [
        'paper', 'research', 'study', 'university', 'journal', 'article',
        'arxiv', 'academic', 'publication', 'thesis', 'dissertation',
        '論文', '研究', '學術', '大學', '期刊', '文章', '發表'
    ]
    
    # 檢查是否為學術問題
    is_academic = any(keyword in question_lower for keyword in academic_keywords)
    
    if not is_academic:
        return []
    
    # 學術問題的推薦順序
    recommendations = [
        {
            'tool': 'arxiv_search_mcp',
            'reason': '專門的ArXiv論文搜索，支持自然語言查詢',
            'confidence': 0.9
        },
        {
            'tool': 'arxiv_mcp_server', 
            'reason': '連接ArXiv龐大論文集合，適合深度分析',
            'confidence': 0.85
        },
        {
            'tool': 'webagent',
            'reason': '通用網絡搜索，可訪問其他學術數據庫',
            'confidence': 0.7
        },
        {
            'tool': 'claude',
            'reason': '可能在訓練數據中見過該論文',
            'confidence': 0.6
        },
        {
            'tool': 'gemini',
            'reason': '備用AI助手，可能有相關知識',
            'confidence': 0.5
        }
    ]
    
    return recommendations

if __name__ == "__main__":
    print("🔧 更新工具分類系統 - 集成ArXiv MCP服務器")
    print("=" * 60)
    
    # 更新ArXiv工具
    arxiv_tools = update_arxiv_tools()
    
    # 測試學術問題推薦
    test_question = "What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper?"
    
    print(f"\n📋 測試學術問題: {test_question}")
    recommendations = get_academic_paper_recommendations(test_question)
    
    print("\n🎯 推薦工具順序:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['tool']} (信心度: {rec['confidence']:.1%})")
        print(f"   理由: {rec['reason']}")
    
    # 顯示更新後的MCP.so服務
    mcp_so_tools = classification_system.get_category_tools(ToolCategory.MCP_SO_SERVICES)
    print(f"\n📊 MCP.so服務工具總數: {len(mcp_so_tools)}")
    print(f"工具列表: {mcp_so_tools}")

