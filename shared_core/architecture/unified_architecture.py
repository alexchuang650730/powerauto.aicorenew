#!/usr/bin/env python3
"""
PowerAutomation v0.53 統一整合架構實現

基於統一架構設計文檔實現的核心組件整合代碼
包含標準數據模型、統一接口和組件整合邏輯
"""

import os
import json
import time
import asyncio
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import uuid

# ============================================================================
# 核心數據模型 (Core Data Models)
# ============================================================================

class InteractionSource(Enum):
    """交互來源枚舉"""
    MANUS_GUI = "manus_gui"
    MANUS_PLUGIN = "manus_plugin"
    TARAE_PLUGIN = "tarae_plugin"
    CODE_BUDDY_PLUGIN = "code_buddy_plugin"
    TONGYI_PLUGIN = "tongyi_plugin"
    SYSTEM_INTERNAL = "system_internal"
    EXTERNAL_API = "external_api"

class DeliverableType(Enum):
    """交付件類型枚舉"""
    PYTHON_CODE = "python_code"
    MARKDOWN_DOC = "markdown_doc"
    JSON_DATA = "json_data"
    HTML_SLIDES = "html_slides"
    TEST_SUITE = "test_suite"
    CONFIG_FILE = "config_file"
    ANALYSIS_REPORT = "analysis_report"
    SYSTEM_ARCHITECTURE = "system_architecture"
    API_SPECIFICATION = "api_specification"
    KILOCODE_TEMPLATE = "kilocode_template"

class DataLayer(Enum):
    """數據層級枚舉"""
    INTERACTION = "interaction"
    TRAINING = "training"
    TESTING = "testing"
    KNOWLEDGE = "knowledge"

@dataclass
class StandardDeliverable:
    """標準交付件數據模型"""
    deliverable_id: str
    deliverable_type: DeliverableType
    name: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_potential_score: Optional[float] = None
    quality_assessment_score: Optional[float] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        if not self.deliverable_id:
            self.deliverable_id = f"{self.deliverable_type.value}_{uuid.uuid4().hex[:8]}"

@dataclass
class StandardInteractionLog:
    """標準交互日誌數據模型"""
    log_id: str
    session_id: str
    timestamp: str
    interaction_source: InteractionSource
    user_request: Optional[Dict[str, Any]] = None
    agent_response: Optional[Dict[str, Any]] = None
    thought_process: Optional[List[Dict[str, Any]]] = None
    executed_actions: Optional[List[Dict[str, Any]]] = None
    deliverables: Optional[List[StandardDeliverable]] = None
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.log_id:
            self.log_id = f"log_{uuid.uuid4().hex[:12]}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class LearningExperience:
    """學習經驗數據模型"""
    experience_id: str
    timestamp: str
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any]
    source_interaction_log_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.experience_id:
            self.experience_id = f"exp_{uuid.uuid4().hex[:12]}"
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class KiloCodeTemplate:
    """KiloCode模板數據模型"""
    template_id: str
    name: str
    description: str
    template_type: DeliverableType
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    content_structure: str = ""
    usage_examples: List[str] = field(default_factory=list)
    version: str = "1.0"
    created_by: str = "unified_architecture"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        if not self.template_id:
            self.template_id = f"template_{uuid.uuid4().hex[:8]}"

# ============================================================================
# 統一接口定義 (Unified Interface Definitions)
# ============================================================================

class DataCollectorInterface(ABC):
    """數據收集器統一接口"""
    
    @abstractmethod
    async def collect_interaction(self, source: InteractionSource, 
                                 interaction_data: Dict[str, Any]) -> StandardInteractionLog:
        """收集交互數據"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取收集統計信息"""
        pass

class DataManagerInterface(ABC):
    """數據管理器統一接口"""
    
    @abstractmethod
    async def store_data(self, data: Union[StandardInteractionLog, LearningExperience, 
                                         KiloCodeTemplate], layer: DataLayer) -> str:
        """存儲數據"""
        pass
    
    @abstractmethod
    async def retrieve_data(self, data_id: str, layer: DataLayer) -> Optional[Dict[str, Any]]:
        """檢索數據"""
        pass
    
    @abstractmethod
    async def query_data(self, query: Dict[str, Any], layer: DataLayer) -> List[Dict[str, Any]]:
        """查詢數據"""
        pass

class LearningEngineInterface(ABC):
    """學習引擎統一接口"""
    
    @abstractmethod
    async def learn_from_experience(self, experience: LearningExperience) -> Dict[str, Any]:
        """從經驗中學習"""
        pass
    
    @abstractmethod
    async def get_optimization_suggestions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """獲取優化建議"""
        pass

class ToolEngineInterface(ABC):
    """工具引擎統一接口"""
    
    @abstractmethod
    async def generate_tool(self, request: Dict[str, Any]) -> StandardDeliverable:
        """生成工具"""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool: StandardDeliverable, 
                          parameters: Dict[str, Any]) -> Dict[str, Any]:
        """執行工具"""
        pass

# ============================================================================
# 統一交互收集器 (Unified Interaction Collector)
# ============================================================================

class UnifiedInteractionCollector(DataCollectorInterface):
    """統一交互收集器 - 整合ManusInteractionCollector和InteractionLogManager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.interaction_buffer: List[StandardInteractionLog] = []
        self.statistics = {
            'total_collected': 0,
            'by_source': {},
            'by_type': {},
            'last_collection_time': None
        }
        
    async def collect_interaction(self, source: InteractionSource, 
                                 interaction_data: Dict[str, Any]) -> StandardInteractionLog:
        """收集交互數據"""
        try:
            # 提取基本信息
            user_request = interaction_data.get('user_request', {})
            agent_response = interaction_data.get('agent_response', {})
            
            # 提取思考過程（來自ManusInteractionCollector的邏輯）
            thought_process = self._extract_thought_process(agent_response)
            
            # 提取執行動作
            executed_actions = self._extract_actions(agent_response)
            
            # 處理交付件
            deliverables = []
            if 'deliverables' in interaction_data:
                for deliverable_data in interaction_data['deliverables']:
                    deliverable = self._process_deliverable(deliverable_data)
                    if deliverable:
                        deliverables.append(deliverable)
            
            # 創建標準交互日誌
            interaction_log = StandardInteractionLog(
                log_id="",  # 將在__post_init__中生成
                session_id=interaction_data.get('session_id', f"session_{int(time.time())}"),
                timestamp="",  # 將在__post_init__中生成
                interaction_source=source,
                user_request=user_request,
                agent_response=agent_response,
                thought_process=thought_process,
                executed_actions=executed_actions,
                deliverables=deliverables,
                context_snapshot=interaction_data.get('context', {}),
                performance_metrics=interaction_data.get('performance_metrics', {}),
                tags=self._generate_tags(user_request, agent_response, deliverables)
            )
            
            # 添加到緩衝區
            self.interaction_buffer.append(interaction_log)
            
            # 更新統計信息
            self._update_statistics(source, interaction_log)
            
            self.logger.info(f"✅ 交互數據已收集: {interaction_log.log_id}")
            return interaction_log
            
        except Exception as e:
            self.logger.error(f"❌ 收集交互數據失敗: {e}")
            raise
    
    def _extract_thought_process(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取思考過程（整合ManusInteractionCollector邏輯）"""
        thought_process = []
        
        if isinstance(response, dict):
            response_text = json.dumps(response)
        else:
            response_text = str(response)
        
        # 提取<thought>標籤內容
        import re
        thought_pattern = r"<thought>(.*?)</thought>"
        thoughts = re.findall(thought_pattern, response_text, re.DOTALL)
        
        for i, thought in enumerate(thoughts):
            thought_process.append({
                'step': i + 1,
                'content': thought.strip(),
                'timestamp': datetime.now().isoformat()
            })
        
        return thought_process
    
    def _extract_actions(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取執行動作"""
        actions = []
        
        if isinstance(response, dict):
            response_text = json.dumps(response)
        else:
            response_text = str(response)
        
        # 提取<action>標籤內容
        import re
        action_pattern = r"<action>(.*?)</action>"
        action_matches = re.findall(action_pattern, response_text, re.DOTALL)
        
        for i, action in enumerate(action_matches):
            actions.append({
                'step': i + 1,
                'action': action.strip(),
                'timestamp': datetime.now().isoformat()
            })
        
        return actions
    
    def _process_deliverable(self, deliverable_data: Dict[str, Any]) -> Optional[StandardDeliverable]:
        """處理交付件數據"""
        try:
            # 確定交付件類型
            deliverable_type = self._classify_deliverable_type(deliverable_data)
            
            # 計算模板潛力評分
            template_potential = self._calculate_template_potential(deliverable_data, deliverable_type)
            
            # 計算質量評估評分
            quality_score = self._calculate_quality_score(deliverable_data, deliverable_type)
            
            deliverable = StandardDeliverable(
                deliverable_id="",  # 將在__post_init__中生成
                deliverable_type=deliverable_type,
                name=deliverable_data.get('name', 'unnamed'),
                content=deliverable_data.get('content'),
                file_path=deliverable_data.get('file_path'),
                metadata=deliverable_data.get('metadata', {}),
                template_potential_score=template_potential,
                quality_assessment_score=quality_score
            )
            
            return deliverable
            
        except Exception as e:
            self.logger.warning(f"處理交付件失敗: {e}")
            return None
    
    def _classify_deliverable_type(self, deliverable_data: Dict[str, Any]) -> DeliverableType:
        """分類交付件類型（整合InteractionLogManager邏輯）"""
        file_path = deliverable_data.get('file_path', '')
        content = deliverable_data.get('content', '')
        
        if file_path:
            file_ext = Path(file_path).suffix.lower()
            if file_ext == '.py':
                return DeliverableType.PYTHON_CODE
            elif file_ext == '.md':
                return DeliverableType.MARKDOWN_DOC
            elif file_ext == '.json':
                return DeliverableType.JSON_DATA
            elif file_ext == '.html':
                return DeliverableType.HTML_SLIDES
        
        # 基於內容分類
        content_lower = content.lower()
        if 'def ' in content_lower or 'class ' in content_lower:
            return DeliverableType.PYTHON_CODE
        elif 'test' in content_lower or 'unittest' in content_lower:
            return DeliverableType.TEST_SUITE
        elif 'analysis' in content_lower or 'report' in content_lower:
            return DeliverableType.ANALYSIS_REPORT
        
        return DeliverableType.MARKDOWN_DOC  # 默認類型
    
    def _calculate_template_potential(self, deliverable_data: Dict[str, Any], 
                                    deliverable_type: DeliverableType) -> float:
        """計算模板潛力評分"""
        content = deliverable_data.get('content', '')
        score = 0.0
        
        # 基於類型的基礎評分
        if deliverable_type == DeliverableType.PYTHON_CODE:
            if 'class ' in content:
                score += 0.3
            if 'def ' in content:
                score += 0.2
            if 'import ' in content:
                score += 0.1
        elif deliverable_type == DeliverableType.MARKDOWN_DOC:
            if content.count('#') >= 3:
                score += 0.3
            if '```' in content:
                score += 0.2
        
        # 基於內容豐富度
        if len(content) > 1000:
            score += 0.2
        if len(content.split('\n')) > 20:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_quality_score(self, deliverable_data: Dict[str, Any], 
                               deliverable_type: DeliverableType) -> float:
        """計算質量評估評分"""
        content = deliverable_data.get('content', '')
        score = 0.5  # 基礎分數
        
        # 基於內容長度
        content_length = len(content)
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        elif content_length > 100:
            score += 0.1
        
        # 基於結構化程度
        if deliverable_type == DeliverableType.PYTHON_CODE:
            if 'docstring' in content or '"""' in content:
                score += 0.1
            if 'try:' in content and 'except' in content:
                score += 0.1
        
        return min(score, 1.0)
    
    def _generate_tags(self, user_request: Dict[str, Any], agent_response: Dict[str, Any], 
                      deliverables: List[StandardDeliverable]) -> List[str]:
        """生成標籤"""
        tags = []
        
        # 基於請求內容的標籤
        request_text = str(user_request).lower()
        common_tags = ['gaia', 'test', 'analysis', 'code', 'mcp', 'ai', 'automation']
        tags.extend([tag for tag in common_tags if tag in request_text])
        
        # 基於交付件類型的標籤
        for deliverable in deliverables:
            tags.append(deliverable.deliverable_type.value)
            if deliverable.template_potential_score and deliverable.template_potential_score > 0.7:
                tags.append('high_template_potential')
        
        return list(set(tags))
    
    def _update_statistics(self, source: InteractionSource, log: StandardInteractionLog):
        """更新統計信息"""
        self.statistics['total_collected'] += 1
        self.statistics['last_collection_time'] = datetime.now().isoformat()
        
        # 按來源統計
        source_key = source.value
        if source_key not in self.statistics['by_source']:
            self.statistics['by_source'][source_key] = 0
        self.statistics['by_source'][source_key] += 1
        
        # 按類型統計
        for deliverable in log.deliverables or []:
            type_key = deliverable.deliverable_type.value
            if type_key not in self.statistics['by_type']:
                self.statistics['by_type'][type_key] = 0
            self.statistics['by_type'][type_key] += 1
    
    async def get_statistics(self) -> Dict[str, Any]:
        """獲取收集統計信息"""
        return {
            **self.statistics,
            'buffer_size': len(self.interaction_buffer),
            'config': self.config
        }
    
    async def flush_buffer(self) -> List[StandardInteractionLog]:
        """清空緩衝區並返回數據"""
        buffer_data = self.interaction_buffer.copy()
        self.interaction_buffer.clear()
        return buffer_data

# ============================================================================
# 統一數據流管理器 (Unified Data Flow Manager)
# ============================================================================

class UnifiedDataFlowManager(DataManagerInterface):
    """統一數據流管理器 - 整合DataFlowManager功能"""
    
    def __init__(self, base_dir: str = "/home/ubuntu/Powerauto.ai"):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "unified_data"
        self.logger = logging.getLogger(__name__)
        self.setup_directories()
        
        # 存儲配置
        self.storage_config = {
            'local_storage': True,
            'github_sync': False,  # 可配置
            'supermemory_sync': False,  # 可配置
            'rag_indexing': True
        }
    
    def setup_directories(self):
        """設置目錄結構"""
        directories = [
            "interaction_logs",
            "learning_experiences", 
            "kilocode_templates",
            "models",
            "knowledge_base",
            "rag_index",
            "backups"
        ]
        
        for directory in directories:
            (self.data_dir / directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"✅ 統一數據目錄已設置: {self.data_dir}")
    
    async def store_data(self, data: Union[StandardInteractionLog, LearningExperience, 
                                         KiloCodeTemplate], layer: DataLayer) -> str:
        """存儲數據"""
        try:
            # 確定存儲路徑
            if isinstance(data, StandardInteractionLog):
                storage_path = self.data_dir / "interaction_logs"
                file_name = f"{data.log_id}.json"
            elif isinstance(data, LearningExperience):
                storage_path = self.data_dir / "learning_experiences"
                file_name = f"{data.experience_id}.json"
            elif isinstance(data, KiloCodeTemplate):
                storage_path = self.data_dir / "kilocode_templates"
                file_name = f"{data.template_id}.json"
            else:
                raise ValueError(f"不支持的數據類型: {type(data)}")
            
            # 確保目錄存在
            storage_path.mkdir(parents=True, exist_ok=True)
            
            # 保存數據
            file_path = storage_path / file_name
            with open(file_path, 'w', encoding='utf-8') as f:
                if hasattr(data, '__dict__'):
                    # 處理dataclass
                    data_dict = asdict(data)
                    # 遞歸處理Enum類型
                    data_dict = self._serialize_enums(data_dict)
                    json.dump(data_dict, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ 數據已存儲: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"❌ 存儲數據失敗: {e}")
            raise
    
    def _serialize_enums(self, obj):
        """遞歸序列化Enum類型"""
        if isinstance(obj, dict):
            return {key: self._serialize_enums(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_enums(item) for item in obj]
        elif hasattr(obj, 'value'):  # Enum類型
            return obj.value
        else:
            return obj
    
    async def retrieve_data(self, data_id: str, layer: DataLayer) -> Optional[Dict[str, Any]]:
        """檢索數據"""
        try:
            # 根據layer確定搜索路徑
            search_paths = []
            if layer == DataLayer.INTERACTION:
                search_paths.append(self.data_dir / "interaction_logs")
            elif layer == DataLayer.TRAINING:
                search_paths.append(self.data_dir / "learning_experiences")
            elif layer == DataLayer.KNOWLEDGE:
                search_paths.append(self.data_dir / "kilocode_templates")
            else:
                # 搜索所有路徑
                search_paths = [
                    self.data_dir / "interaction_logs",
                    self.data_dir / "learning_experiences",
                    self.data_dir / "kilocode_templates"
                ]
            
            # 搜索文件
            for search_path in search_paths:
                if search_path.exists():
                    for file_path in search_path.glob(f"{data_id}.json"):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return json.load(f)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ 檢索數據失敗: {e}")
            return None
    
    async def query_data(self, query: Dict[str, Any], layer: DataLayer) -> List[Dict[str, Any]]:
        """查詢數據"""
        try:
            results = []
            
            # 確定搜索路徑
            if layer == DataLayer.INTERACTION:
                search_path = self.data_dir / "interaction_logs"
            elif layer == DataLayer.TRAINING:
                search_path = self.data_dir / "learning_experiences"
            elif layer == DataLayer.KNOWLEDGE:
                search_path = self.data_dir / "kilocode_templates"
            else:
                # 搜索所有路徑
                for sub_layer in [DataLayer.INTERACTION, DataLayer.TRAINING, DataLayer.KNOWLEDGE]:
                    sub_results = await self.query_data(query, sub_layer)
                    results.extend(sub_results)
                return results
            
            # 搜索文件
            if search_path.exists():
                for file_path in search_path.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # 簡單的查詢匹配
                        match = True
                        for key, value in query.items():
                            if key not in data or data[key] != value:
                                match = False
                                break
                        
                        if match:
                            results.append(data)
                            
                    except Exception as e:
                        self.logger.warning(f"讀取文件失敗 {file_path}: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ 查詢數據失敗: {e}")
            return []

# ============================================================================
# 統一架構協調器 (Unified Architecture Coordinator)
# ============================================================================

class UnifiedArchitectureCoordinator:
    """統一架構協調器 - 協調各個組件的工作"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 初始化核心組件
        self.interaction_collector = UnifiedInteractionCollector(config.get('collector', {}))
        self.data_manager = UnifiedDataFlowManager(config.get('base_dir', '/home/ubuntu/Powerauto.ai'))
        
        # 組件狀態
        self.status = {
            'initialized': True,
            'running': False,
            'last_activity': None,
            'processed_interactions': 0,
            'errors': []
        }
        
        self.logger.info("✅ 統一架構協調器已初始化")
    
    async def process_interaction(self, source: InteractionSource, 
                                 interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理交互的完整流程"""
        try:
            # 1. 收集交互數據
            interaction_log = await self.interaction_collector.collect_interaction(
                source, interaction_data
            )
            
            # 2. 存儲交互日誌
            storage_path = await self.data_manager.store_data(
                interaction_log, DataLayer.INTERACTION
            )
            
            # 3. 生成學習經驗（如果適用）
            learning_experience = self._generate_learning_experience(interaction_log)
            if learning_experience:
                await self.data_manager.store_data(
                    learning_experience, DataLayer.TRAINING
                )
            
            # 4. 生成KiloCode模板（如果適用）
            templates = self._generate_kilocode_templates(interaction_log)
            for template in templates:
                await self.data_manager.store_data(
                    template, DataLayer.KNOWLEDGE
                )
            
            # 5. 更新狀態
            self.status['processed_interactions'] += 1
            self.status['last_activity'] = datetime.now().isoformat()
            
            result = {
                'success': True,
                'interaction_log_id': interaction_log.log_id,
                'storage_path': storage_path,
                'learning_experiences_generated': 1 if learning_experience else 0,
                'templates_generated': len(templates),
                'processing_time': time.time()
            }
            
            self.logger.info(f"✅ 交互處理完成: {interaction_log.log_id}")
            return result
            
        except Exception as e:
            error_msg = f"處理交互失敗: {e}"
            self.logger.error(f"❌ {error_msg}")
            self.status['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': error_msg
            })
            return {
                'success': False,
                'error': error_msg
            }
    
    def _generate_learning_experience(self, interaction_log: StandardInteractionLog) -> Optional[LearningExperience]:
        """從交互日誌生成學習經驗"""
        try:
            # 構建狀態
            state = {
                'user_request': interaction_log.user_request or {},
                'context': interaction_log.context_snapshot,
                'source': interaction_log.interaction_source.value
            }
            
            # 構建動作
            action = {
                'response': interaction_log.agent_response or {},
                'deliverables': [asdict(d) for d in interaction_log.deliverables or []],
                'tools_used': self._extract_tools_used(interaction_log)
            }
            
            # 計算獎勵
            reward = self._calculate_reward(interaction_log)
            
            # 構建下一狀態
            next_state = {
                'task_completed': len(interaction_log.deliverables or []) > 0,
                'deliverable_quality': self._assess_deliverable_quality(interaction_log.deliverables or []),
                'performance_metrics': interaction_log.performance_metrics
            }
            
            return LearningExperience(
                experience_id="",  # 將在__post_init__中生成
                timestamp="",  # 將在__post_init__中生成
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                source_interaction_log_id=interaction_log.log_id,
                metadata={
                    'tags': interaction_log.tags,
                    'source': interaction_log.interaction_source.value
                }
            )
            
        except Exception as e:
            self.logger.warning(f"生成學習經驗失敗: {e}")
            return None
    
    def _extract_tools_used(self, interaction_log: StandardInteractionLog) -> List[str]:
        """提取使用的工具"""
        tools = []
        
        # 從執行動作中提取
        for action in interaction_log.executed_actions or []:
            action_content = action.get('action', '').lower()
            if 'file_write' in action_content:
                tools.append('file_writer')
            elif 'shell_exec' in action_content:
                tools.append('shell_executor')
            elif 'browser' in action_content:
                tools.append('browser')
        
        # 從交付件類型推斷
        for deliverable in interaction_log.deliverables or []:
            if deliverable.deliverable_type == DeliverableType.PYTHON_CODE:
                tools.append('code_generator')
            elif deliverable.deliverable_type == DeliverableType.MARKDOWN_DOC:
                tools.append('document_generator')
        
        return list(set(tools))
    
    def _calculate_reward(self, interaction_log: StandardInteractionLog) -> float:
        """計算獎勵值"""
        reward = 0.0
        
        # 基於交付件數量和質量
        deliverables = interaction_log.deliverables or []
        if deliverables:
            reward += len(deliverables) * 0.2
            
            # 基於質量評分
            quality_scores = [d.quality_assessment_score for d in deliverables 
                            if d.quality_assessment_score is not None]
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                reward += avg_quality * 0.3
        
        # 基於性能指標
        performance = interaction_log.performance_metrics
        if performance.get('response_time', 0) < 5.0:  # 快速響應
            reward += 0.2
        
        return min(reward, 1.0)
    
    def _assess_deliverable_quality(self, deliverables: List[StandardDeliverable]) -> float:
        """評估交付件質量"""
        if not deliverables:
            return 0.0
        
        quality_scores = [d.quality_assessment_score for d in deliverables 
                         if d.quality_assessment_score is not None]
        
        if quality_scores:
            return sum(quality_scores) / len(quality_scores)
        else:
            return 0.5  # 默認中等質量
    
    def _generate_kilocode_templates(self, interaction_log: StandardInteractionLog) -> List[KiloCodeTemplate]:
        """生成KiloCode模板"""
        templates = []
        
        for deliverable in interaction_log.deliverables or []:
            # 只為高潛力交付件生成模板
            if (deliverable.template_potential_score and 
                deliverable.template_potential_score > 0.6):
                
                template = KiloCodeTemplate(
                    template_id="",  # 將在__post_init__中生成
                    name=f"{deliverable.name}_template",
                    description=f"Auto-generated template from {deliverable.name}",
                    template_type=deliverable.deliverable_type,
                    parameters=self._extract_template_parameters(deliverable),
                    content_structure=deliverable.content or "",
                    usage_examples=[f"Example usage of {deliverable.name}"],
                    version="1.0",
                    created_by="unified_architecture"
                )
                
                templates.append(template)
        
        return templates
    
    def _extract_template_parameters(self, deliverable: StandardDeliverable) -> List[Dict[str, Any]]:
        """提取模板參數"""
        parameters = []
        content = deliverable.content or ""
        
        # 簡單的參數提取邏輯
        if deliverable.deliverable_type == DeliverableType.PYTHON_CODE:
            # 提取函數參數
            import re
            functions = re.findall(r'def\s+(\w+)\s*\((.*?)\):', content)
            for func_name, params in functions:
                if params.strip():
                    parameters.append({
                        'name': f"{func_name}_params",
                        'type': 'function_parameters',
                        'description': f"Parameters for function {func_name}",
                        'default_value': params
                    })
        
        return parameters
    
    async def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        collector_stats = await self.interaction_collector.get_statistics()
        
        return {
            'coordinator_status': self.status,
            'collector_statistics': collector_stats,
            'data_manager_config': self.data_manager.storage_config,
            'timestamp': datetime.now().isoformat()
        }
    
    async def start_processing(self):
        """啟動處理"""
        self.status['running'] = True
        self.logger.info("🚀 統一架構協調器已啟動")
    
    async def stop_processing(self):
        """停止處理"""
        self.status['running'] = False
        self.logger.info("⏹️ 統一架構協調器已停止")

# ============================================================================
# 配置和初始化
# ============================================================================

def create_default_config() -> Dict[str, Any]:
    """創建默認配置"""
    return {
        'base_dir': '/home/ubuntu/Powerauto.ai',
        'collector': {
            'batch_size': 10,
            'auto_flush_interval': 30,
            'log_level': 'INFO'
        },
        'data_manager': {
            'local_storage': True,
            'github_sync': False,
            'supermemory_sync': False,
            'rag_indexing': True
        },
        'learning': {
            'enabled': True,
            'async_mode': True,
            'learning_rate': 0.001
        }
    }

def initialize_unified_architecture(config: Optional[Dict[str, Any]] = None) -> UnifiedArchitectureCoordinator:
    """初始化統一架構"""
    if config is None:
        config = create_default_config()
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 創建協調器
    coordinator = UnifiedArchitectureCoordinator(config)
    
    return coordinator

# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == "__main__":
    async def main():
        """主程序"""
        print("🚀 PowerAutomation v0.53 統一整合架構")
        
        # 初始化架構
        coordinator = initialize_unified_architecture()
        
        # 啟動處理
        await coordinator.start_processing()
        
        # 測試交互處理
        test_interaction = {
            'user_request': {
                'text': '創建一個Python函數來計算斐波那契數列',
                'type': 'code_generation'
            },
            'agent_response': {
                'text': '我將為您創建一個計算斐波那契數列的Python函數',
                'thought_process': '<thought>用戶需要一個斐波那契函數</thought>'
            },
            'deliverables': [{
                'name': 'fibonacci.py',
                'content': 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
                'file_path': '/tmp/fibonacci.py',
                'metadata': {'lines': 4, 'functions': 1}
            }],
            'context': {'session_type': 'coding_assistance'},
            'performance_metrics': {'response_time': 2.5}
        }
        
        # 處理測試交互
        result = await coordinator.process_interaction(
            InteractionSource.MANUS_GUI, 
            test_interaction
        )
        
        print(f"✅ 測試交互處理結果: {result}")
        
        # 獲取系統狀態
        status = await coordinator.get_system_status()
        print(f"📊 系統狀態: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # 停止處理
        await coordinator.stop_processing()
        
        print("✅ 統一架構測試完成")
    
    # 運行主程序
    asyncio.run(main())

