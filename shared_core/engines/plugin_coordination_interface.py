"""
PowerAutomation v0.57 - 插件協同接口
解決多前端插件協同和標準化接口問題

Author: PowerAutomation Team
Version: 0.57
Date: 2025-06-11
"""

import asyncio
import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid
import websockets
from abc import ABC, abstractmethod

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PluginType(Enum):
    """插件類型枚舉"""
    MANUS = "manus"
    TRAE = "trae"
    CURSOR = "cursor"
    WINDSURF = "windsurf"
    VSCODE = "vscode"
    KILOCODE = "kilocode"
    TONGYI = "tongyi"
    CODEBUDDY = "codebuddy"

class PluginStatus(Enum):
    """插件狀態枚舉"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ACTIVE = "active"
    ERROR = "error"

@dataclass
class PluginInfo:
    """插件信息"""
    plugin_id: str
    plugin_type: PluginType
    plugin_name: str
    version: str
    capabilities: List[str]
    status: PluginStatus
    last_heartbeat: float
    connection_info: Dict[str, Any]

@dataclass
class PluginMessage:
    """插件消息"""
    message_id: str
    timestamp: float
    source_plugin: str
    target_plugin: Optional[str]
    message_type: str
    payload: Dict[str, Any]
    priority: int = 1  # 1=低, 2=中, 3=高

@dataclass
class CoordinationTask:
    """協同任務"""
    task_id: str
    task_type: str
    involved_plugins: List[str]
    task_data: Dict[str, Any]
    status: str
    created_at: float
    updated_at: float

class PluginInterface(ABC):
    """插件接口抽象基類"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    async def send_message(self, message: PluginMessage) -> bool:
        """發送消息"""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[PluginMessage]:
        """接收消息"""
        pass
    
    @abstractmethod
    async def get_status(self) -> PluginStatus:
        """獲取狀態"""
        pass
    
    @abstractmethod
    async def heartbeat(self) -> bool:
        """心跳檢測"""
        pass

class PluginCoordinationManager:
    """插件協同管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_interfaces: Dict[str, PluginInterface] = {}
        self.message_queue: List[PluginMessage] = []
        self.coordination_tasks: Dict[str, CoordinationTask] = {}
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self.is_running = False
        self.heartbeat_interval = 30.0  # 30秒心跳間隔
        
        # 初始化事件類型
        self.event_types = [
            'plugin_connected',
            'plugin_disconnected',
            'message_received',
            'coordination_started',
            'coordination_completed',
            'quality_assessment',
            'intervention_triggered'
        ]
        
        for event_type in self.event_types:
            self.event_callbacks[event_type] = []
        
        logger.info("插件協同管理器初始化完成")
    
    async def start_coordination(self) -> bool:
        """啟動協同服務"""
        try:
            self.is_running = True
            
            # 啟動心跳檢測
            asyncio.create_task(self._heartbeat_monitor())
            
            # 啟動消息處理
            asyncio.create_task(self._message_processor())
            
            logger.info("插件協同服務啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"插件協同服務啟動失敗: {e}")
            return False
    
    async def stop_coordination(self):
        """停止協同服務"""
        self.is_running = False
        
        # 斷開所有插件連接
        for plugin_id in list(self.plugins.keys()):
            await self.disconnect_plugin(plugin_id)
        
        logger.info("插件協同服務已停止")
    
    async def register_plugin(self, plugin_info: PluginInfo, 
                            plugin_interface: PluginInterface) -> bool:
        """註冊插件"""
        try:
            plugin_id = plugin_info.plugin_id
            
            # 初始化插件接口
            init_success = await plugin_interface.initialize({
                'plugin_id': plugin_id,
                'coordination_manager': self
            })
            
            if not init_success:
                logger.error(f"插件初始化失敗: {plugin_id}")
                return False
            
            # 註冊插件
            self.plugins[plugin_id] = plugin_info
            self.plugin_interfaces[plugin_id] = plugin_interface
            
            # 更新狀態
            plugin_info.status = PluginStatus.CONNECTED
            plugin_info.last_heartbeat = time.time()
            
            # 觸發事件
            await self._trigger_event('plugin_connected', {
                'plugin_id': plugin_id,
                'plugin_info': asdict(plugin_info)
            })
            
            logger.info(f"插件註冊成功: {plugin_id} ({plugin_info.plugin_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"插件註冊失敗: {e}")
            return False
    
    async def disconnect_plugin(self, plugin_id: str) -> bool:
        """斷開插件連接"""
        try:
            if plugin_id in self.plugins:
                plugin_info = self.plugins[plugin_id]
                plugin_info.status = PluginStatus.DISCONNECTED
                
                # 移除插件
                del self.plugins[plugin_id]
                if plugin_id in self.plugin_interfaces:
                    del self.plugin_interfaces[plugin_id]
                
                # 觸發事件
                await self._trigger_event('plugin_disconnected', {
                    'plugin_id': plugin_id
                })
                
                logger.info(f"插件斷開連接: {plugin_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"插件斷開失敗: {e}")
            return False
    
    async def send_message(self, message: PluginMessage) -> bool:
        """發送消息到插件"""
        try:
            target_plugin = message.target_plugin
            
            if target_plugin and target_plugin in self.plugin_interfaces:
                # 發送到特定插件
                interface = self.plugin_interfaces[target_plugin]
                success = await interface.send_message(message)
                
                if success:
                    logger.info(f"消息發送成功: {message.source_plugin} -> {target_plugin}")
                else:
                    logger.error(f"消息發送失敗: {message.source_plugin} -> {target_plugin}")
                
                return success
            
            elif not target_plugin:
                # 廣播消息
                success_count = 0
                for plugin_id, interface in self.plugin_interfaces.items():
                    if plugin_id != message.source_plugin:
                        if await interface.send_message(message):
                            success_count += 1
                
                logger.info(f"廣播消息完成: {success_count}/{len(self.plugin_interfaces)} 成功")
                return success_count > 0
            
            else:
                logger.warning(f"目標插件不存在: {target_plugin}")
                return False
                
        except Exception as e:
            logger.error(f"消息發送異常: {e}")
            return False
    
    async def create_coordination_task(self, task_type: str, 
                                     involved_plugins: List[str],
                                     task_data: Dict[str, Any]) -> str:
        """創建協同任務"""
        try:
            task_id = str(uuid.uuid4())
            
            coordination_task = CoordinationTask(
                task_id=task_id,
                task_type=task_type,
                involved_plugins=involved_plugins,
                task_data=task_data,
                status='created',
                created_at=time.time(),
                updated_at=time.time()
            )
            
            self.coordination_tasks[task_id] = coordination_task
            
            # 觸發事件
            await self._trigger_event('coordination_started', {
                'task_id': task_id,
                'task_type': task_type,
                'involved_plugins': involved_plugins
            })
            
            # 通知相關插件
            for plugin_id in involved_plugins:
                if plugin_id in self.plugin_interfaces:
                    message = PluginMessage(
                        message_id=str(uuid.uuid4()),
                        timestamp=time.time(),
                        source_plugin='coordination_manager',
                        target_plugin=plugin_id,
                        message_type='coordination_task_created',
                        payload={
                            'task_id': task_id,
                            'task_type': task_type,
                            'task_data': task_data
                        },
                        priority=2
                    )
                    await self.send_message(message)
            
            logger.info(f"協同任務創建成功: {task_id} - {task_type}")
            return task_id
            
        except Exception as e:
            logger.error(f"協同任務創建失敗: {e}")
            return ""
    
    async def update_coordination_task(self, task_id: str, 
                                     status: str, 
                                     result_data: Optional[Dict[str, Any]] = None) -> bool:
        """更新協同任務狀態"""
        try:
            if task_id not in self.coordination_tasks:
                logger.warning(f"協同任務不存在: {task_id}")
                return False
            
            task = self.coordination_tasks[task_id]
            task.status = status
            task.updated_at = time.time()
            
            if result_data:
                task.task_data.update(result_data)
            
            # 如果任務完成，觸發事件
            if status in ['completed', 'failed']:
                await self._trigger_event('coordination_completed', {
                    'task_id': task_id,
                    'status': status,
                    'task_data': task.task_data
                })
            
            logger.info(f"協同任務狀態更新: {task_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"協同任務更新失敗: {e}")
            return False
    
    async def trigger_quality_assessment(self, content: str, 
                                       source_plugin: str,
                                       assessment_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """觸發質量評估"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # 創建質量評估任務
            task_id = await self.create_coordination_task(
                task_type='quality_assessment',
                involved_plugins=[source_plugin, 'kilocode'],
                task_data={
                    'assessment_id': assessment_id,
                    'content': content,
                    'criteria': assessment_criteria,
                    'source_plugin': source_plugin
                }
            )
            
            # 觸發質量評估事件
            await self._trigger_event('quality_assessment', {
                'assessment_id': assessment_id,
                'task_id': task_id,
                'source_plugin': source_plugin,
                'content_length': len(content)
            })
            
            # 模擬質量評估結果（實際應該調用AI模型）
            quality_score = 0.75  # 示例分數
            
            assessment_result = {
                'assessment_id': assessment_id,
                'task_id': task_id,
                'quality_score': quality_score,
                'needs_intervention': quality_score < 0.8,
                'assessment_details': {
                    'content_quality': quality_score,
                    'structure_score': 0.8,
                    'completeness_score': 0.7,
                    'professional_score': 0.75
                },
                'recommendations': [
                    '建議增強內容的專業性',
                    '優化結構組織',
                    '補充更多細節'
                ]
            }
            
            # 更新任務狀態
            await self.update_coordination_task(task_id, 'completed', {
                'assessment_result': assessment_result
            })
            
            logger.info(f"質量評估完成: {assessment_id} - 分數: {quality_score}")
            return assessment_result
            
        except Exception as e:
            logger.error(f"質量評估失敗: {e}")
            return {}
    
    async def trigger_intervention(self, assessment_result: Dict[str, Any]) -> Dict[str, Any]:
        """觸發智能介入"""
        try:
            intervention_id = str(uuid.uuid4())
            
            # 創建介入任務
            task_id = await self.create_coordination_task(
                task_type='intelligent_intervention',
                involved_plugins=['kilocode'],
                task_data={
                    'intervention_id': intervention_id,
                    'assessment_result': assessment_result,
                    'intervention_type': 'quality_enhancement'
                }
            )
            
            # 觸發介入事件
            await self._trigger_event('intervention_triggered', {
                'intervention_id': intervention_id,
                'task_id': task_id,
                'quality_score': assessment_result.get('quality_score', 0),
                'intervention_type': 'quality_enhancement'
            })
            
            # 模擬介入結果
            intervention_result = {
                'intervention_id': intervention_id,
                'task_id': task_id,
                'success': True,
                'enhanced_content': '經過KiloCode增強的內容...',
                'improvement_score': 0.25,  # 提升了25%
                'final_quality_score': assessment_result.get('quality_score', 0) + 0.25,
                'intervention_details': {
                    'enhanced_sections': ['結構優化', '內容補充', '專業性提升'],
                    'processing_time': 2.5,
                    'confidence': 0.92
                }
            }
            
            # 更新任務狀態
            await self.update_coordination_task(task_id, 'completed', {
                'intervention_result': intervention_result
            })
            
            logger.info(f"智能介入完成: {intervention_id} - 提升: {intervention_result['improvement_score']}")
            return intervention_result
            
        except Exception as e:
            logger.error(f"智能介入失敗: {e}")
            return {}
    
    async def _heartbeat_monitor(self):
        """心跳監控"""
        while self.is_running:
            try:
                current_time = time.time()
                
                for plugin_id, plugin_info in list(self.plugins.items()):
                    # 檢查心跳超時
                    if current_time - plugin_info.last_heartbeat > self.heartbeat_interval * 2:
                        logger.warning(f"插件心跳超時: {plugin_id}")
                        plugin_info.status = PluginStatus.ERROR
                        
                        # 嘗試重新連接
                        if plugin_id in self.plugin_interfaces:
                            interface = self.plugin_interfaces[plugin_id]
                            heartbeat_success = await interface.heartbeat()
                            
                            if heartbeat_success:
                                plugin_info.status = PluginStatus.CONNECTED
                                plugin_info.last_heartbeat = current_time
                                logger.info(f"插件心跳恢復: {plugin_id}")
                            else:
                                logger.error(f"插件心跳失敗，斷開連接: {plugin_id}")
                                await self.disconnect_plugin(plugin_id)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"心跳監控異常: {e}")
                await asyncio.sleep(5)
    
    async def _message_processor(self):
        """消息處理器"""
        while self.is_running:
            try:
                # 處理消息隊列
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    
                    # 觸發消息接收事件
                    await self._trigger_event('message_received', {
                        'message_id': message.message_id,
                        'source_plugin': message.source_plugin,
                        'target_plugin': message.target_plugin,
                        'message_type': message.message_type
                    })
                    
                    # 處理特殊消息類型
                    if message.message_type == 'quality_assessment_request':
                        await self._handle_quality_assessment_request(message)
                    elif message.message_type == 'intervention_request':
                        await self._handle_intervention_request(message)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"消息處理異常: {e}")
                await asyncio.sleep(1)
    
    async def _handle_quality_assessment_request(self, message: PluginMessage):
        """處理質量評估請求"""
        try:
            payload = message.payload
            content = payload.get('content', '')
            criteria = payload.get('criteria', {})
            
            assessment_result = await self.trigger_quality_assessment(
                content, message.source_plugin, criteria
            )
            
            # 發送評估結果回源插件
            response_message = PluginMessage(
                message_id=str(uuid.uuid4()),
                timestamp=time.time(),
                source_plugin='coordination_manager',
                target_plugin=message.source_plugin,
                message_type='quality_assessment_result',
                payload={'assessment_result': assessment_result},
                priority=2
            )
            
            await self.send_message(response_message)
            
        except Exception as e:
            logger.error(f"質量評估請求處理失敗: {e}")
    
    async def _handle_intervention_request(self, message: PluginMessage):
        """處理介入請求"""
        try:
            payload = message.payload
            assessment_result = payload.get('assessment_result', {})
            
            intervention_result = await self.trigger_intervention(assessment_result)
            
            # 發送介入結果回源插件
            response_message = PluginMessage(
                message_id=str(uuid.uuid4()),
                timestamp=time.time(),
                source_plugin='coordination_manager',
                target_plugin=message.source_plugin,
                message_type='intervention_result',
                payload={'intervention_result': intervention_result},
                priority=3
            )
            
            await self.send_message(response_message)
            
        except Exception as e:
            logger.error(f"介入請求處理失敗: {e}")
    
    async def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """觸發事件"""
        try:
            if event_type in self.event_callbacks:
                for callback in self.event_callbacks[event_type]:
                    try:
                        await callback(event_data)
                    except Exception as e:
                        logger.error(f"事件回調失敗: {event_type} - {e}")
        
        except Exception as e:
            logger.error(f"事件觸發失敗: {event_type} - {e}")
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """添加事件回調"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def remove_event_callback(self, event_type: str, callback: Callable):
        """移除事件回調"""
        if event_type in self.event_callbacks and callback in self.event_callbacks[event_type]:
            self.event_callbacks[event_type].remove(callback)
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """獲取所有插件狀態"""
        status = {}
        for plugin_id, plugin_info in self.plugins.items():
            status[plugin_id] = {
                'plugin_type': plugin_info.plugin_type.value,
                'plugin_name': plugin_info.plugin_name,
                'status': plugin_info.status.value,
                'last_heartbeat': plugin_info.last_heartbeat,
                'capabilities': plugin_info.capabilities
            }
        return status
    
    def get_coordination_tasks(self) -> Dict[str, Any]:
        """獲取協同任務狀態"""
        tasks = {}
        for task_id, task in self.coordination_tasks.items():
            tasks[task_id] = asdict(task)
        return tasks

# 全局插件協同管理器實例
plugin_coordination_manager = PluginCoordinationManager()

async def main():
    """測試插件協同接口"""
    print("🚀 PowerAutomation 插件協同接口測試")
    
    # 啟動協同服務
    success = await plugin_coordination_manager.start_coordination()
    print(f"協同服務啟動: {'成功' if success else '失敗'}")
    
    if success:
        # 模擬質量評估流程
        print("\n📊 測試質量評估流程...")
        assessment_result = await plugin_coordination_manager.trigger_quality_assessment(
            content="這是一個測試內容",
            source_plugin="manus",
            assessment_criteria={'min_quality': 0.8}
        )
        print(f"質量評估結果: {json.dumps(assessment_result, indent=2, ensure_ascii=False)}")
        
        # 如果需要介入，觸發介入
        if assessment_result.get('needs_intervention', False):
            print("\n🤖 觸發智能介入...")
            intervention_result = await plugin_coordination_manager.trigger_intervention(assessment_result)
            print(f"介入結果: {json.dumps(intervention_result, indent=2, ensure_ascii=False)}")
        
        # 顯示協同任務狀態
        print("\n📋 協同任務狀態:")
        tasks = plugin_coordination_manager.get_coordination_tasks()
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
        
        print("\n插件協同接口測試完成")
        await plugin_coordination_manager.stop_coordination()

if __name__ == "__main__":
    asyncio.run(main())

