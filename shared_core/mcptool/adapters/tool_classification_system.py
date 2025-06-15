"""
工具分類系統 - 按功能、複雜度、領域進行精細分類

目標：
1. 快速定位合適的工具類別
2. 精準匹配用戶需求
3. 階梯式兜底機制
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

class ToolCategory(Enum):
    """工具主分類"""
    CONTENT_PROCESSING = "content_processing"  # 內容處理
    SEARCH_VERIFICATION = "search_verification"  # 搜索驗證
    WORKFLOW_AUTOMATION = "workflow_automation"  # 工作流自動化
    LEARNING_OPTIMIZATION = "learning_optimization"  # 學習優化
    RECORDING_TRACKING = "recording_tracking"  # 記錄追蹤
    MEMORY_CONTEXT = "memory_context"  # 記憶上下文
    
    # 動態外部服務類別
    ZAPIER_SERVICES = "zapier_services"  # Zapier自動化服務
    MCP_SO_SERVICES = "mcp_so_services"  # MCP.so平台服務
    ACI_DEV_SERVICES = "aci_dev_services"  # ACI.dev AI服務

class ToolComplexity(Enum):
    """工具複雜度"""
    SIMPLE = "simple"  # 簡單問題
    MEDIUM = "medium"  # 中等問題
    COMPLEX = "complex"  # 複雜問題

class ToolDomain(Enum):
    """工具應用領域"""
    CONVERSATION = "conversation"  # 對話問答
    ANALYSIS = "analysis"  # 數據分析
    AUTOMATION = "automation"  # 自動化
    RESEARCH = "research"  # 搜索研究
    CREATION = "creation"  # 內容創建
    TRACKING = "tracking"  # 追蹤記錄

@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    category: ToolCategory
    complexity: ToolComplexity
    domains: List[ToolDomain]
    keywords: List[str]
    description: str
    use_cases: List[str]
    fallback_order: int  # 兜底順序，數字越小優先級越高

class ToolClassificationSystem:
    """工具分類系統"""
    
    def __init__(self):
        """初始化工具分類系統"""
        self.tool_registry = self._build_tool_registry()
        self.category_hierarchy = self._build_category_hierarchy()
    
    def _build_tool_registry(self) -> Dict[str, ToolInfo]:
        """構建工具註冊表"""
        tools = {
            # 內容處理類
            "gemini": ToolInfo(
                name="gemini",
                category=ToolCategory.CONTENT_PROCESSING,
                complexity=ToolComplexity.SIMPLE,
                domains=[ToolDomain.CONVERSATION],
                keywords=["什麼是", "介紹", "解釋", "簡單", "基礎"],
                description="通用AI助手，適合簡單問答",
                use_cases=["基礎知識問答", "簡單解釋", "日常對話"],
                fallback_order=1
            ),
            
            "claude": ToolInfo(
                name="claude",
                category=ToolCategory.CONTENT_PROCESSING,
                complexity=ToolComplexity.COMPLEX,
                domains=[ToolDomain.ANALYSIS, ToolDomain.CREATION],
                keywords=["分析", "比較", "詳細", "深入", "複雜", "評估"],
                description="高級AI分析師，適合複雜分析",
                use_cases=["深度分析", "複雜比較", "專業評估"],
                fallback_order=2
            ),
            
            "sequential_thinking": ToolInfo(
                name="sequential_thinking",
                category=ToolCategory.CONTENT_PROCESSING,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.ANALYSIS],
                keywords=["步驟", "計算", "推理", "邏輯", "過程"],
                description="逐步推理工具，適合邏輯分析",
                use_cases=["數學計算", "邏輯推理", "步驟分解"],
                fallback_order=3
            ),
            
            # 搜索驗證類
            "webagent": ToolInfo(
                name="webagent",
                category=ToolCategory.SEARCH_VERIFICATION,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.RESEARCH],
                keywords=["最新", "搜索", "查找", "當前", "實時", "網上"],
                description="網絡搜索代理，獲取最新信息",
                use_cases=["最新資訊", "事實查證", "實時數據"],
                fallback_order=1
            ),
            
            "supermemory_adapter": ToolInfo(
                name="supermemory_adapter",
                category=ToolCategory.MEMORY_CONTEXT,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.RESEARCH],
                keywords=["記憶", "歷史", "回憶", "之前", "記住"],
                description="超級記憶系統，檢索歷史信息",
                use_cases=["歷史查詢", "知識檢索", "上下文回憶"],
                fallback_order=2
            ),
            
            # 記錄追蹤類 - 細分
            "thought_action_recorder": ToolInfo(
                name="thought_action_recorder",
                category=ToolCategory.RECORDING_TRACKING,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.TRACKING],
                keywords=["思維記錄", "決策記錄", "過程記錄"],
                description="思維行動記錄器",
                use_cases=["思維過程記錄", "決策軌跡", "行為分析"],
                fallback_order=1
            ),
            
            "learning_progress_recorder": ToolInfo(
                name="learning_progress_recorder",
                category=ToolCategory.RECORDING_TRACKING,
                complexity=ToolComplexity.SIMPLE,
                domains=[ToolDomain.TRACKING],
                keywords=["學習記錄", "進度追蹤", "學習進度"],
                description="學習進度記錄器",
                use_cases=["學習進度", "知識積累", "技能提升"],
                fallback_order=2
            ),
            
            "workflow_recorder": ToolInfo(
                name="workflow_recorder",
                category=ToolCategory.RECORDING_TRACKING,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.TRACKING, ToolDomain.AUTOMATION],
                keywords=["流程記錄", "工作流記錄", "步驟記錄"],
                description="工作流程記錄器",
                use_cases=["流程優化", "操作記錄", "效率分析"],
                fallback_order=3
            ),
            
            # 工作流自動化類
            "intelligent_workflow_engine": ToolInfo(
                name="intelligent_workflow_engine",
                category=ToolCategory.WORKFLOW_AUTOMATION,
                complexity=ToolComplexity.COMPLEX,
                domains=[ToolDomain.AUTOMATION],
                keywords=["工作流", "自動化", "流程", "批處理"],
                description="智能工作流引擎",
                use_cases=["複雜自動化", "流程設計", "批量處理"],
                fallback_order=1
            ),
            
            # 學習優化類
            "rl_srt_mcp": ToolInfo(
                name="rl_srt_mcp",
                category=ToolCategory.LEARNING_OPTIMIZATION,
                complexity=ToolComplexity.COMPLEX,
                domains=[ToolDomain.ANALYSIS],
                keywords=["學習", "優化", "改進", "反思", "提升"],
                description="強化學習和自我反思工具",
                use_cases=["學習優化", "性能改進", "自我反思"],
                fallback_order=1
            ),
            
            # 外部服務類別 - 動態發現
            "zapier": ToolInfo(
                name="zapier",
                category=ToolCategory.ZAPIER_SERVICES,
                complexity=ToolComplexity.COMPLEX,
                domains=[ToolDomain.AUTOMATION],
                keywords=["自動化", "集成", "連接", "工作流", "zapier"],
                description="Zapier自動化平台 - 部署後動態發現具體工具",
                use_cases=["應用集成", "自動化流程", "數據同步"],
                fallback_order=1
            ),
            
            "mcp.so": ToolInfo(
                name="mcp.so",
                category=ToolCategory.MCP_SO_SERVICES,
                complexity=ToolComplexity.SIMPLE,
                domains=[ToolDomain.CONVERSATION, ToolDomain.AUTOMATION],
                keywords=["mcp", "服務", "工具", "平台"],
                description="MCP.so服務平台 - 部署後動態發現可用MCP工具",
                use_cases=["MCP工具集成", "服務調用", "工具擴展"],
                fallback_order=1
            ),
            
            "aci.dev": ToolInfo(
                name="aci.dev",
                category=ToolCategory.ACI_DEV_SERVICES,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.ANALYSIS, ToolDomain.CREATION],
                keywords=["ai", "服務", "高級", "專業", "定制"],
                description="ACI.dev AI服務平台 - 部署後動態發現AI服務",
                use_cases=["專業AI服務", "高級分析", "定制功能"],
                fallback_order=1
            )
        }
        
        return tools
    
    def _build_category_hierarchy(self) -> Dict[ToolCategory, List[str]]:
        """構建分類層次結構"""
        hierarchy = {}
        
        for tool_name, tool_info in self.tool_registry.items():
            category = tool_info.category
            if category not in hierarchy:
                hierarchy[category] = []
            hierarchy[category].append(tool_name)
        
        # 按兜底順序排序
        for category in hierarchy:
            hierarchy[category].sort(key=lambda x: self.tool_registry[x].fallback_order)
        
        return hierarchy
    
    def classify_question(self, question: str) -> Dict[str, Any]:
        """對問題進行分類分析"""
        question_lower = question.lower()
        
        # 計算各工具的匹配分數
        tool_scores = {}
        category_scores = {}
        domain_scores = {}
        
        for tool_name, tool_info in self.tool_registry.items():
            score = 0
            matched_keywords = []
            
            # 關鍵詞匹配
            for keyword in tool_info.keywords:
                if keyword in question_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # 複雜度匹配
            word_count = len(question.split())
            if word_count < 10 and tool_info.complexity == ToolComplexity.SIMPLE:
                score += 0.5
            elif 10 <= word_count < 25 and tool_info.complexity == ToolComplexity.MEDIUM:
                score += 0.5
            elif word_count >= 25 and tool_info.complexity == ToolComplexity.COMPLEX:
                score += 0.5
            
            tool_scores[tool_name] = {
                'score': score,
                'matched_keywords': matched_keywords,
                'tool_info': tool_info
            }
            
            # 累計分類分數
            category = tool_info.category
            if category not in category_scores:
                category_scores[category] = 0
            category_scores[category] += score
            
            # 累計領域分數
            for domain in tool_info.domains:
                if domain not in domain_scores:
                    domain_scores[domain] = 0
                domain_scores[domain] += score
        
        # 排序結果
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'tool_scores': dict(sorted_tools),
            'category_ranking': sorted_categories,
            'domain_ranking': sorted_domains,
            'recommended_category': sorted_categories[0][0] if sorted_categories else None,
            'recommended_tools': [item[0] for item in sorted_tools[:3]]
        }
    
    def get_fallback_sequence(self, failed_tools: List[str], question: str) -> List[Dict[str, Any]]:
        """獲取兜底序列"""
        classification = self.classify_question(question)
        recommended_category = classification['recommended_category']
        
        fallback_sequence = []
        
        # 第一層：同類別內的其他工具
        if recommended_category and recommended_category in self.category_hierarchy:
            category_tools = self.category_hierarchy[recommended_category]
            for tool_name in category_tools:
                if tool_name not in failed_tools:
                    fallback_sequence.append({
                        'level': 1,
                        'tool': tool_name,
                        'reason': f'同類別({recommended_category.value})內的替代工具',
                        'tool_info': self.tool_registry[tool_name]
                    })
        
        # 第二層：其他類別的相關工具
        for category, tools in self.category_hierarchy.items():
            if category != recommended_category:
                for tool_name in tools:
                    if tool_name not in failed_tools and tool_name not in [item['tool'] for item in fallback_sequence]:
                        # 檢查是否有關鍵詞匹配
                        tool_info = self.tool_registry[tool_name]
                        question_lower = question.lower()
                        has_match = any(keyword in question_lower for keyword in tool_info.keywords)
                        
                        if has_match:
                            fallback_sequence.append({
                                'level': 2,
                                'tool': tool_name,
                                'reason': f'跨類別({category.value})的相關工具',
                                'tool_info': tool_info
                            })
        
        # 第三層：外部服務（按新分類）
        external_categories = [
            ToolCategory.ZAPIER_SERVICES,
            ToolCategory.MCP_SO_SERVICES, 
            ToolCategory.ACI_DEV_SERVICES
        ]
        
        for category in external_categories:
            if category in self.category_hierarchy:
                category_tools = self.category_hierarchy[category]
                for tool_name in category_tools:
                    if tool_name not in failed_tools and tool_name not in [item['tool'] for item in fallback_sequence]:
                        fallback_sequence.append({
                            'level': 3,
                            'tool': tool_name,
                            'reason': f'外部服務兜底({category.value})',
                            'tool_info': self.tool_registry[tool_name]
                        })
        
        return fallback_sequence[:5]  # 最多返回5個建議
    
    def get_category_tools(self, category: ToolCategory) -> List[str]:
        """獲取指定分類的所有工具"""
        return self.category_hierarchy.get(category, [])
    
    def get_tool_info(self, tool_name: str) -> Optional[ToolInfo]:
        """獲取工具信息"""
        return self.tool_registry.get(tool_name)

# 創建全局分類系統實例
classification_system = ToolClassificationSystem()

def classify_user_question(question: str) -> Dict[str, Any]:
    """分類用戶問題（全局函數接口）"""
    return classification_system.classify_question(question)

def get_tool_fallback_sequence(failed_tools: List[str], question: str) -> List[Dict[str, Any]]:
    """獲取工具兜底序列（全局函數接口）"""
    return classification_system.get_fallback_sequence(failed_tools, question)

if __name__ == "__main__":
    # 測試工具分類系統
    print("🚀 測試動態工具分類系統")
    print("=" * 50)
    
    # 初始化並進行服務發現
    classification_system.initialize_with_discovery()
    
    test_questions = [
        "我需要記錄我的學習進度",
        "請詳細分析深度學習和傳統機器學習的區別", 
        "搜索最新的AI發展趨勢",
        "幫我設計一個自動化郵件處理流程"
    ]
    
    print("\n📋 測試問題分類:")
    for question in test_questions:
        print(f"\n問題: {question}")
        classification = classify_user_question(question)
        print(f"推薦分類: {classification['recommended_category'].value if classification['recommended_category'] else 'None'}")
        print(f"推薦工具: {classification['recommended_tools'][:3]}")
        
        # 測試兜底序列
        fallback = get_tool_fallback_sequence(['gemini', 'claude'], question)
        print(f"兜底序列: {[item['tool'] for item in fallback[:3]]}")
    
    print(f"\n📊 總工具數量: {len(classification_system.tool_registry)}")
    print(f"分類數量: {len(classification_system.category_hierarchy)}")
    
    # 顯示各分類的工具
    print("\n🗂️ 各分類工具:")
    for category, tools in classification_system.category_hierarchy.items():
        print(f"{category.value}: {tools}")
        """動態發現外部服務的具體工具"""
        discovered_services = {
            'zapier_services': [],
            'mcp_so_services': [],
            'aci_dev_services': []
        }
        
        # 這裡可以添加實際的服務發現邏輯
        # 例如：調用API獲取可用工具列表
        
        # 模擬發現的服務
        discovered_services['zapier_services'] = [
            'zapier_email_automation',
            'zapier_calendar_sync', 
            'zapier_data_transfer',
            'zapier_notification_system'
        ]
        
        discovered_services['mcp_so_services'] = [
            'mcp_so_text_processor',
            'mcp_so_data_analyzer',
            'mcp_so_file_manager',
            'mcp_so_api_connector'
        ]
        
        discovered_services['aci_dev_services'] = [
            'aci_dev_advanced_nlp',
            'aci_dev_image_analysis',
            'aci_dev_code_generator',
            'aci_dev_data_scientist'
        ]
        
        return discovered_services
    
    def register_discovered_tools(self, discovered_services: Dict[str, List[str]]):
        """註冊發現的外部工具"""
        
        # Zapier服務工具
        for tool_name in discovered_services.get('zapier_services', []):
            self.tool_registry[tool_name] = ToolInfo(
                name=tool_name,
                category=ToolCategory.ZAPIER_SERVICES,
                complexity=ToolComplexity.MEDIUM,
                domains=[ToolDomain.AUTOMATION],
                keywords=self._extract_keywords_from_name(tool_name),
                description=f"Zapier工具: {tool_name}",
                use_cases=[f"{tool_name}的自動化應用"],
                fallback_order=2
            )
        
        # MCP.so服務工具
        for tool_name in discovered_services.get('mcp_so_services', []):
            self.tool_registry[tool_name] = ToolInfo(
                name=tool_name,
                category=ToolCategory.MCP_SO_SERVICES,
                complexity=ToolComplexity.SIMPLE,
                domains=[ToolDomain.CONVERSATION, ToolDomain.AUTOMATION],
                keywords=self._extract_keywords_from_name(tool_name),
                description=f"MCP.so工具: {tool_name}",
                use_cases=[f"{tool_name}的MCP應用"],
                fallback_order=2
            )
        
        # ACI.dev服務工具
        for tool_name in discovered_services.get('aci_dev_services', []):
            self.tool_registry[tool_name] = ToolInfo(
                name=tool_name,
                category=ToolCategory.ACI_DEV_SERVICES,
                complexity=ToolComplexity.COMPLEX,
                domains=[ToolDomain.ANALYSIS, ToolDomain.CREATION],
                keywords=self._extract_keywords_from_name(tool_name),
                description=f"ACI.dev工具: {tool_name}",
                use_cases=[f"{tool_name}的AI服務應用"],
                fallback_order=2
            )
        
        # 重建分類層次結構
        self.category_hierarchy = self._build_category_hierarchy()
    
    def _extract_keywords_from_name(self, tool_name: str) -> List[str]:
        """從工具名稱提取關鍵詞"""
        # 簡單的關鍵詞提取邏輯
        keywords = []
        name_parts = tool_name.lower().replace('_', ' ').split()
        
        # 移除平台前綴
        filtered_parts = [part for part in name_parts if part not in ['zapier', 'mcp', 'so', 'aci', 'dev']]
        
        keywords.extend(filtered_parts)
        return keywords
    
    def initialize_with_discovery(self):
        """初始化並進行服務發現"""
        print("🔍 開始動態發現外部服務...")
        discovered = self.discover_external_services()
        
        print(f"發現 Zapier 工具: {len(discovered['zapier_services'])} 個")
        print(f"發現 MCP.so 工具: {len(discovered['mcp_so_services'])} 個") 
        print(f"發現 ACI.dev 工具: {len(discovered['aci_dev_services'])} 個")
        
        self.register_discovered_tools(discovered)
        print("✅ 外部服務工具註冊完成")
        
        return discovered

