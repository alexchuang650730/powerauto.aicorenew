"""
智能意圖處理系統

當用戶下intent指令時：
1. 檢查現有工具 - 如果有對應工具就直接使用
2. 動態創建工具 - 如果沒有工具，透過kilo code來建立工具代碼
3. 反饋機制 - 提供創建過程和結果的反饋
4. 學習機制 - 將過程記錄到RAG和RL-SRT系統

整合ai_enhanced_intent_understanding_mcp.py的現有功能
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import re

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from mcptool.adapters.base_mcp import BaseMCP
    from mcptool.adapters.core.unified_adapter_registry import UnifiedAdapterRegistry
    from mcptool.adapters.thought_action_recorder_mcp import ThoughtActionRecorderMCP
    from test.dynamic_adapter_discovery import DynamicAdapterDiscovery, ToolRequirement
    IMPORTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"導入失敗: {e}")
    IMPORTS_AVAILABLE = False
    # 創建Mock類
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
    
    class UnifiedAdapterRegistry:
        def __init__(self):
            self.adapters = {}
        def list_adapters(self):
            return []
    
    class ThoughtActionRecorderMCP:
        def __init__(self, config=None):
            pass
        def process(self, input_data):
            return {"success": False, "error": "Mock implementation"}
    
    class DynamicAdapterDiscovery:
        def __init__(self, project_root=None):
            pass
        async def discover_adapter(self, requirement):
            return type('AdapterDiscoveryResult', (), {
                'found': False, 
                'created_new': False,
                'adapter_id': None,
                'adapter_name': None,
                'match_score': 0.0,
                'creation_details': {"error": "Mock implementation"}
            })()
    
    class ToolRequirement:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentAnalyzer:
    """意圖分析器"""
    
    def __init__(self):
        """初始化意圖分析器"""
        # 意圖模式匹配
        self.intent_patterns = {
            'create_tool': [
                r'創建.*工具',
                r'建立.*功能',
                r'需要.*工具',
                r'開發.*模塊',
                r'實現.*功能'
            ],
            'search_tool': [
                r'查找.*工具',
                r'搜索.*功能',
                r'有沒有.*工具',
                r'是否存在.*功能'
            ],
            'execute_task': [
                r'執行.*任務',
                r'運行.*程序',
                r'處理.*數據',
                r'分析.*內容'
            ],
            'get_help': [
                r'幫助',
                r'如何.*',
                r'怎麼.*',
                r'教我.*'
            ],
            'optimize_system': [
                r'優化.*系統',
                r'改進.*性能',
                r'提升.*效率'
            ]
        }
        
        # 能力關鍵詞映射
        self.capability_keywords = {
            'document': ['文檔', '文件', 'PDF', 'Word', '報告'],
            'data_analysis': ['數據', '分析', '統計', '圖表', '可視化'],
            'web_scraping': ['爬蟲', '抓取', '網頁', '數據採集'],
            'api_testing': ['API', '測試', '接口', '端點'],
            'automation': ['自動化', '批處理', '腳本', '流程'],
            'machine_learning': ['機器學習', 'AI', '模型', '訓練'],
            'database': ['數據庫', 'SQL', '查詢', '存儲'],
            'image_processing': ['圖像', '圖片', '處理', '識別'],
            'text_processing': ['文本', '自然語言', 'NLP', '語言處理']
        }
    
    def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """分析用戶意圖"""
        user_input_lower = user_input.lower()
        
        # 檢測主要意圖
        primary_intent = self._detect_primary_intent(user_input_lower)
        
        # 提取所需能力
        required_capabilities = self._extract_capabilities(user_input_lower)
        
        # 提取關鍵參數
        parameters = self._extract_parameters(user_input)
        
        # 計算信心度
        confidence = self._calculate_confidence(user_input_lower, primary_intent, required_capabilities)
        
        return {
            'primary_intent': primary_intent,
            'required_capabilities': required_capabilities,
            'parameters': parameters,
            'confidence': confidence,
            'original_input': user_input,
            'processed_input': user_input_lower,
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_primary_intent(self, user_input: str) -> str:
        """檢測主要意圖"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input):
                    return intent
        
        # 默認意圖
        return 'execute_task'
    
    def _extract_capabilities(self, user_input: str) -> List[str]:
        """提取所需能力"""
        capabilities = []
        
        for capability, keywords in self.capability_keywords.items():
            for keyword in keywords:
                if keyword.lower() in user_input:
                    capabilities.append(capability)
                    break
        
        return capabilities
    
    def _extract_parameters(self, user_input: str) -> Dict[str, Any]:
        """提取關鍵參數"""
        parameters = {}
        
        # 提取文件路徑
        file_patterns = [
            r'文件路徑[：:]\s*([^\s]+)',
            r'路徑[：:]\s*([^\s]+)',
            r'文件[：:]\s*([^\s]+)'
        ]
        
        for pattern in file_patterns:
            match = re.search(pattern, user_input)
            if match:
                parameters['file_path'] = match.group(1)
                break
        
        # 提取URL
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, user_input)
        if url_match:
            parameters['url'] = url_match.group(0)
        
        # 提取數量
        number_pattern = r'(\d+)\s*個'
        number_match = re.search(number_pattern, user_input)
        if number_match:
            parameters['count'] = int(number_match.group(1))
        
        return parameters
    
    def _calculate_confidence(self, user_input: str, intent: str, capabilities: List[str]) -> float:
        """計算信心度"""
        confidence = 0.5  # 基礎信心度
        
        # 意圖匹配度
        if intent != 'execute_task':  # 非默認意圖
            confidence += 0.3
        
        # 能力匹配度
        if capabilities:
            confidence += min(0.2, len(capabilities) * 0.05)
        
        # 輸入長度和詳細度
        if len(user_input) > 20:
            confidence += 0.1
        
        return min(1.0, confidence)


class KiloCodeIntegration:
    """Kilo Code集成模塊"""
    
    def __init__(self, api_key: str = None):
        """初始化Kilo Code集成"""
        self.api_key = api_key or os.getenv('KILOCODE_API_KEY')
        self.base_url = "https://api.kilocode.com/v1"  # 假設的API端點
        
        # 代碼生成模板
        self.code_templates = {
            'document_processor': '''
def process_document(file_path: str) -> Dict[str, Any]:
    """處理文檔文件"""
    import os
    from pathlib import Path
    
    if not os.path.exists(file_path):
        return {"error": "文件不存在", "success": False}
    
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return process_pdf(file_path)
    elif file_ext in ['.doc', '.docx']:
        return process_word(file_path)
    elif file_ext == '.txt':
        return process_text(file_path)
    else:
        return {"error": f"不支持的文件格式: {file_ext}", "success": False}

def process_pdf(file_path: str) -> Dict[str, Any]:
    """處理PDF文件"""
    try:
        # TODO: 實現PDF處理邏輯
        return {"content": "PDF內容", "pages": 1, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}
''',
            
            'data_analyzer': '''
def analyze_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析數據"""
    import statistics
    from collections import Counter
    
    if not data:
        return {"error": "數據為空", "success": False}
    
    try:
        # 基本統計
        total_records = len(data)
        
        # 數值字段分析
        numeric_analysis = {}
        for key in data[0].keys():
            values = [record.get(key) for record in data if isinstance(record.get(key), (int, float))]
            if values:
                numeric_analysis[key] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values)
                }
        
        return {
            "total_records": total_records,
            "numeric_analysis": numeric_analysis,
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}
''',
            
            'web_scraper': '''
def scrape_website(url: str, selectors: Dict[str, str] = None) -> Dict[str, Any]:
    """網頁抓取"""
    import requests
    from bs4 import BeautifulSoup
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if selectors:
            results = {}
            for key, selector in selectors.items():
                elements = soup.select(selector)
                results[key] = [elem.get_text(strip=True) for elem in elements]
        else:
            results = {"title": soup.title.string if soup.title else ""}
        
        return {"data": results, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}
'''
        }
    
    async def generate_tool_code(self, requirement: ToolRequirement) -> Dict[str, Any]:
        """使用Kilo Code生成工具代碼"""
        try:
            # 選擇合適的模板
            template = self._select_template(requirement)
            
            if template:
                # 使用模板生成代碼
                code = self._customize_template(template, requirement)
            else:
                # 使用Kilo Code API生成代碼
                code = await self._call_kilocode_api(requirement)
            
            return {
                "success": True,
                "code": code,
                "template_used": template is not None,
                "requirement": requirement.name,
                "generated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"代碼生成失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "requirement": requirement.name
            }
    
    def _select_template(self, requirement: ToolRequirement) -> Optional[str]:
        """選擇合適的代碼模板"""
        capabilities = requirement.capabilities
        
        if 'document_parsing' in capabilities or 'content_extraction' in capabilities:
            return self.code_templates['document_processor']
        elif 'data_analysis' in capabilities or 'data_visualization' in capabilities:
            return self.code_templates['data_analyzer']
        elif 'web_scraping' in capabilities or 'data_collection' in capabilities:
            return self.code_templates['web_scraper']
        
        return None
    
    def _customize_template(self, template: str, requirement: ToolRequirement) -> str:
        """自定義模板代碼"""
        # 添加需求特定的註釋和文檔
        customized_code = f'''"""
{requirement.description}

自動生成的工具代碼
需求: {requirement.name}
能力: {", ".join(requirement.capabilities)}
生成時間: {datetime.now().isoformat()}
"""

{template}

# 主要入口函數
def main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """主要處理函數"""
    try:
        # TODO: 根據具體需求實現主邏輯
        return {{"success": True, "message": "功能實現中", "data": input_data}}
    except Exception as e:
        return {{"success": False, "error": str(e)}}

if __name__ == "__main__":
    # 測試代碼
    test_data = {{"test": True}}
    result = main(test_data)
    print(f"測試結果: {{result}}")
'''
        
        return customized_code
    
    async def _call_kilocode_api(self, requirement: ToolRequirement) -> str:
        """調用Kilo Code API生成代碼"""
        # 模擬API調用
        await asyncio.sleep(1)  # 模擬網絡延遲
        
        # 生成基礎代碼結構
        code = f'''"""
{requirement.description}

使用Kilo Code API生成的工具
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class {requirement.name.replace(" ", "")}Tool:
    """自動生成的{requirement.name}工具"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.capabilities = {requirement.capabilities}
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具主邏輯"""
        try:
            # TODO: 實現具體功能
            return {{
                "success": True,
                "message": "工具執行完成",
                "result": input_data,
                "timestamp": datetime.now().isoformat()
            }}
        except Exception as e:
            return {{
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }}
    
    def get_info(self) -> Dict[str, Any]:
        """獲取工具信息"""
        return {{
            "name": "{requirement.name}",
            "description": "{requirement.description}",
            "capabilities": self.capabilities,
            "category": "{requirement.category}",
            "auto_generated": True,
            "generated_by": "KiloCode API"
        }}

# 創建工具實例
def create_tool(config: Dict[str, Any] = None):
    return {requirement.name.replace(" ", "")}Tool(config)
'''
        
        return code


class IntelligentIntentProcessor:
    """智能意圖處理系統"""
    
    def __init__(self, project_root: str = None):
        """初始化智能意圖處理系統"""
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        
        # 初始化組件
        try:
            self.intent_analyzer = IntentAnalyzer()
            self.adapter_registry = UnifiedAdapterRegistry()
            self.dynamic_discovery = DynamicAdapterDiscovery(str(self.project_root))
            self.thought_recorder = ThoughtActionRecorderMCP()
            self.kilo_code = KiloCodeIntegration()
            self.components_available = IMPORTS_AVAILABLE
        except Exception as e:
            logger.warning(f"組件初始化失敗: {e}")
            self.intent_analyzer = IntentAnalyzer()
            self.adapter_registry = UnifiedAdapterRegistry()
            self.dynamic_discovery = DynamicAdapterDiscovery(str(self.project_root))
            self.thought_recorder = ThoughtActionRecorderMCP()
            self.kilo_code = KiloCodeIntegration()
            self.components_available = False
        
        # 處理歷史
        self.processing_history: List[Dict[str, Any]] = []
        
        # 統計信息
        self.metrics = {
            'total_intents_processed': 0,
            'tools_found': 0,
            'tools_created': 0,
            'success_rate': 0.0,
            'average_processing_time': 0.0
        }
        
        logger.info("智能意圖處理系統初始化完成")
    
    async def process_intent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理用戶意圖"""
        start_time = datetime.now()
        processing_id = f"intent_{int(start_time.timestamp())}"
        
        logger.info(f"開始處理意圖: {processing_id}")
        
        try:
            # 1. 開始記錄會話
            session_id = await self._start_recording_session(user_input, context)
            
            # 2. 分析用戶意圖
            intent_analysis = self.intent_analyzer.analyze_intent(user_input)
            await self._record_thought_process(session_id, "意圖分析", intent_analysis)
            
            # 3. 搜索現有工具
            tool_search_result = await self._search_existing_tools(intent_analysis)
            await self._record_action(session_id, "搜索現有工具", tool_search_result)
            
            # 4. 如果找到工具，直接使用
            if tool_search_result['found']:
                execution_result = await self._execute_existing_tool(
                    tool_search_result['tool'], intent_analysis, context
                )
                await self._record_action(session_id, "執行現有工具", execution_result)
                
                result = {
                    "processing_id": processing_id,
                    "session_id": session_id,
                    "status": "success",
                    "method": "existing_tool",
                    "tool_used": tool_search_result['tool']['name'],
                    "intent_analysis": intent_analysis,
                    "execution_result": execution_result,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 5. 如果沒有找到工具，創建新工具
            else:
                creation_result = await self._create_new_tool(intent_analysis, session_id)
                
                result = {
                    "processing_id": processing_id,
                    "session_id": session_id,
                    "status": "success",
                    "method": "tool_creation",
                    "tool_created": creation_result.get('tool_name'),
                    "intent_analysis": intent_analysis,
                    "creation_result": creation_result,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # 6. 結束記錄會話
            await self._end_recording_session(session_id, result)
            
            # 7. 更新統計
            self._update_metrics(result)
            
            # 8. 記錄處理歷史
            self.processing_history.append(result)
            
            logger.info(f"意圖處理完成: {processing_id}")
            return result
        
        except Exception as e:
            logger.error(f"意圖處理失敗: {e}")
            
            error_result = {
                "processing_id": processing_id,
                "status": "error",
                "error": str(e),
                "intent_analysis": intent_analysis if 'intent_analysis' in locals() else None,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
            
            self.processing_history.append(error_result)
            return error_result
    
    async def _start_recording_session(self, user_input: str, context: Dict[str, Any]) -> str:
        """開始記錄會話"""
        try:
            if hasattr(self.thought_recorder, 'process') and self.components_available:
                session_result = self.thought_recorder.process({
                    "tool": "start_session",
                    "parameters": {
                        "agent_type": "intelligent_intent_processor",
                        "context": {
                            "user_input": user_input,
                            "context": context or {},
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                })
                
                if session_result.get('success'):
                    return session_result['result']['session_id']
                else:
                    logger.warning("記錄會話開始失敗，使用臨時ID")
                    return f"temp_session_{int(datetime.now().timestamp())}"
            else:
                logger.info("使用臨時會話ID（記錄器不可用）")
                return f"temp_session_{int(datetime.now().timestamp())}"
        
        except Exception as e:
            logger.warning(f"記錄會話開始失敗: {e}")
            return f"temp_session_{int(datetime.now().timestamp())}"
    
    async def _record_thought_process(self, session_id: str, thought: str, details: Dict[str, Any]):
        """記錄思維過程"""
        try:
            if hasattr(self.thought_recorder, 'process') and self.components_available:
                self.thought_recorder.process({
                    "tool": "record_thought",
                    "parameters": {
                        "session_id": session_id,
                        "thought": thought,
                        "reasoning": json.dumps(details, ensure_ascii=False),
                        "confidence": details.get('confidence', 0.8)
                    }
                })
        except Exception as e:
            logger.warning(f"記錄思維過程失敗: {e}")
    
    async def _record_action(self, session_id: str, action: str, result: Dict[str, Any]):
        """記錄執行動作"""
        try:
            if hasattr(self.thought_recorder, 'process') and self.components_available:
                self.thought_recorder.process({
                    "tool": "record_action",
                    "parameters": {
                        "session_id": session_id,
                        "action": action,
                        "parameters": {},
                        "result": result,
                        "success": result.get('success', True)
                    }
                })
        except Exception as e:
            logger.warning(f"記錄執行動作失敗: {e}")
    
    async def _search_existing_tools(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """搜索現有工具"""
        try:
            # 獲取所有適配器
            adapters = self.adapter_registry.list_adapters()
            
            best_match = None
            best_score = 0.0
            
            required_capabilities = intent_analysis['required_capabilities']
            
            for adapter in adapters:
                # 計算匹配分數
                score = self._calculate_tool_match_score(adapter, required_capabilities)
                if score > best_score:
                    best_score = score
                    best_match = adapter
            
            if best_match and best_score > 0.6:  # 閾值可調整
                return {
                    "found": True,
                    "tool": best_match,
                    "match_score": best_score,
                    "search_method": "adapter_registry"
                }
            else:
                return {
                    "found": False,
                    "searched_adapters": len(adapters),
                    "best_score": best_score,
                    "search_method": "adapter_registry"
                }
        
        except Exception as e:
            logger.error(f"搜索現有工具失敗: {e}")
            return {"found": False, "error": str(e)}
    
    def _calculate_tool_match_score(self, adapter: Dict[str, Any], required_capabilities: List[str]) -> float:
        """計算工具匹配分數"""
        if not required_capabilities:
            return 0.1
        
        adapter_capabilities = adapter.get('capabilities', [])
        if not adapter_capabilities:
            return 0.0
        
        # 計算能力匹配度
        matches = 0
        for req_cap in required_capabilities:
            for adapter_cap in adapter_capabilities:
                if req_cap.lower() in adapter_cap.lower() or adapter_cap.lower() in req_cap.lower():
                    matches += 1
                    break
        
        return matches / len(required_capabilities)
    
    async def _execute_existing_tool(self, tool: Dict[str, Any], intent_analysis: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """執行現有工具"""
        try:
            # 準備工具輸入
            tool_input = {
                "intent": intent_analysis['primary_intent'],
                "parameters": intent_analysis['parameters'],
                "context": context or {},
                "capabilities_requested": intent_analysis['required_capabilities']
            }
            
            # 模擬工具執行
            # 實際實現中，這裡應該調用具體的適配器
            execution_result = {
                "success": True,
                "tool_name": tool['name'],
                "tool_id": tool['id'],
                "input": tool_input,
                "output": {
                    "message": f"工具 {tool['name']} 執行完成",
                    "processed_intent": intent_analysis['primary_intent'],
                    "capabilities_used": intent_analysis['required_capabilities']
                },
                "execution_time": 0.5
            }
            
            return execution_result
        
        except Exception as e:
            logger.error(f"執行現有工具失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool.get('name', 'unknown')
            }
    
    async def _create_new_tool(self, intent_analysis: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """創建新工具"""
        try:
            # 1. 創建工具需求
            requirement = ToolRequirement(
                name=f"Intent_{intent_analysis['primary_intent']}_Tool",
                description=f"為意圖 '{intent_analysis['primary_intent']}' 自動創建的工具",
                capabilities=intent_analysis['required_capabilities'],
                input_schema={"intent": "string", "parameters": "object", "context": "object"},
                output_schema={"success": "boolean", "result": "object", "message": "string"},
                priority=5,
                category="auto_generated"
            )
            
            await self._record_thought_process(session_id, "創建工具需求", {
                "requirement": requirement.name,
                "capabilities": requirement.capabilities
            })
            
            # 2. 使用動態發現系統創建適配器
            discovery_result = await self.dynamic_discovery.discover_adapter(requirement)
            
            await self._record_action(session_id, "動態適配器發現", {
                "found": discovery_result.found,
                "created_new": discovery_result.created_new
            })
            
            # 3. 如果動態發現失敗，使用Kilo Code生成代碼
            if not discovery_result.found:
                kilo_result = await self.kilo_code.generate_tool_code(requirement)
                
                await self._record_action(session_id, "Kilo Code代碼生成", {
                    "success": kilo_result['success'],
                    "template_used": kilo_result.get('template_used', False)
                })
                
                if kilo_result['success']:
                    # 保存生成的代碼
                    code_file = await self._save_generated_code(requirement, kilo_result['code'])
                    
                    return {
                        "success": True,
                        "method": "kilo_code_generation",
                        "tool_name": requirement.name,
                        "code_file": code_file,
                        "code_length": len(kilo_result['code']),
                        "template_used": kilo_result.get('template_used', False)
                    }
                else:
                    return {
                        "success": False,
                        "method": "kilo_code_generation",
                        "error": kilo_result.get('error', 'Unknown error')
                    }
            
            # 4. 動態發現成功
            else:
                return {
                    "success": True,
                    "method": "dynamic_discovery",
                    "tool_name": discovery_result.adapter_name,
                    "adapter_id": discovery_result.adapter_id,
                    "created_new": discovery_result.created_new,
                    "match_score": discovery_result.match_score,
                    "creation_details": discovery_result.creation_details
                }
        
        except Exception as e:
            logger.error(f"創建新工具失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "tool_creation"
            }
    
    async def _save_generated_code(self, requirement: ToolRequirement, code: str) -> str:
        """保存生成的代碼"""
        try:
            # 創建生成代碼目錄
            generated_dir = self.project_root / "mcptool" / "adapters" / "generated"
            generated_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            filename = f"{requirement.name.lower().replace(' ', '_')}_tool.py"
            file_path = generated_dir / filename
            
            # 保存代碼
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            logger.info(f"生成的代碼已保存: {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"保存生成代碼失敗: {e}")
            return ""
    
    async def _end_recording_session(self, session_id: str, result: Dict[str, Any]):
        """結束記錄會話"""
        try:
            if hasattr(self.thought_recorder, 'process') and self.components_available:
                summary = f"意圖處理完成: {result['status']}, 方法: {result.get('method', 'unknown')}"
                
                self.thought_recorder.process({
                    "tool": "end_session",
                    "parameters": {
                        "session_id": session_id,
                        "summary": summary
                    }
                })
        except Exception as e:
            logger.warning(f"結束記錄會話失敗: {e}")
    
    def _update_metrics(self, result: Dict[str, Any]):
        """更新統計信息"""
        self.metrics['total_intents_processed'] += 1
        
        if result['status'] == 'success':
            if result.get('method') == 'existing_tool':
                self.metrics['tools_found'] += 1
            elif result.get('method') in ['dynamic_discovery', 'kilo_code_generation']:
                self.metrics['tools_created'] += 1
        
        # 計算成功率
        successful = len([r for r in self.processing_history if r.get('status') == 'success'])
        self.metrics['success_rate'] = successful / len(self.processing_history) if self.processing_history else 0
        
        # 計算平均處理時間
        total_time = sum(r.get('processing_time', 0) for r in self.processing_history)
        self.metrics['average_processing_time'] = total_time / len(self.processing_history) if self.processing_history else 0
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """獲取處理統計"""
        return {
            "metrics": self.metrics,
            "total_history_records": len(self.processing_history),
            "recent_processing": self.processing_history[-5:] if self.processing_history else [],
            "timestamp": datetime.now().isoformat()
        }
    
    async def export_learning_data(self) -> Dict[str, Any]:
        """導出學習數據"""
        try:
            if hasattr(self.thought_recorder, 'process') and self.components_available:
                # 生成RAG數據
                rag_result = self.thought_recorder.process({
                    "tool": "generate_rag_data",
                    "parameters": {}
                })
                
                # 生成RL-SRT數據
                rl_srt_result = self.thought_recorder.process({
                    "tool": "generate_rl_srt_data", 
                    "parameters": {}
                })
                
                # 導出學習數據
                export_result = self.thought_recorder.process({
                    "tool": "export_learning_data",
                    "parameters": {
                        "format": "json",
                        "include_rag": True,
                        "include_rl_srt": True,
                        "output_path": str(self.project_root / "test" / "results" / "intent_learning_data.json")
                    }
                })
                
                return {
                    "success": True,
                    "rag_data_count": rag_result.get('result', {}).get('rag_data_count', 0),
                    "rl_srt_data_count": rl_srt_result.get('result', {}).get('rl_srt_data_count', 0),
                    "export_path": export_result.get('result', {}).get('output_path'),
                    "exported_at": datetime.now().isoformat()
                }
            else:
                # 模擬導出（當組件不可用時）
                return {
                    "success": True,
                    "rag_data_count": 0,
                    "rl_srt_data_count": 0,
                    "export_path": "mock_export_path",
                    "exported_at": datetime.now().isoformat(),
                    "note": "模擬導出（組件不可用）"
                }
        
        except Exception as e:
            logger.error(f"導出學習數據失敗: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# 全局智能意圖處理器實例
_intent_processor = None

def get_intent_processor() -> IntelligentIntentProcessor:
    """獲取全局智能意圖處理器實例"""
    global _intent_processor
    if _intent_processor is None:
        _intent_processor = IntelligentIntentProcessor()
    return _intent_processor


if __name__ == "__main__":
    # 測試示例
    async def main():
        processor = get_intent_processor()
        
        # 測試意圖處理
        test_inputs = [
            "我需要一個分析PDF文檔的工具",
            "創建一個數據可視化工具，能夠生成圖表",
            "幫我建立一個API測試工具",
            "需要一個網頁爬蟲工具來抓取數據"
        ]
        
        for user_input in test_inputs:
            print(f"\n處理意圖: {user_input}")
            result = await processor.process_intent(user_input)
            print(f"處理結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 獲取統計信息
        stats = processor.get_processing_statistics()
        print(f"\n處理統計: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        # 導出學習數據
        learning_data = await processor.export_learning_data()
        print(f"\n學習數據導出: {json.dumps(learning_data, indent=2, ensure_ascii=False)}")
    
    asyncio.run(main())

