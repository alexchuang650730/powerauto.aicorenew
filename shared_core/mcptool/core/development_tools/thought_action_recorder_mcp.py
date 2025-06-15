#!/usr/bin/env python3
"""
ThoughtActionRecorder MCP适配器

此模块为ThoughtActionRecorder提供MCP协议合规的包装，支持思考-行动训练流程。
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目路径
sys.path.append('/home/ubuntu/powerautomation')

try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子类必须实现此方法")
        
        def validate_input(self, input_data: Dict[str, Any]) -> bool:
            return True
        
        def get_capabilities(self) -> List[str]:
            return ["基础MCP适配功能"]

# 尝试导入原始ThoughtActionRecorder
try:
    from .thought_action_recorder import ThoughtActionRecorder
    THOUGHT_ACTION_RECORDER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ThoughtActionRecorder導入失敗: {e}")
    THOUGHT_ACTION_RECORDER_AVAILABLE = False
    
    # 创建Mock实现
    class ThoughtActionRecorder:
        def __init__(self):
            self.records = []
            self.sessions = {}
            
        def start_session(self, agent_type: str = "default") -> str:
            session_id = f"session_{len(self.sessions) + 1}"
            self.sessions[session_id] = {
                'agent_type': agent_type,
                'start_time': datetime.now().isoformat(),
                'status': 'active',
                'records': []
            }
            return session_id
            
        def record_thought(self, session_id: str, thought: str, context: Dict = None):
            record = {
                'id': len(self.records) + 1,
                'session_id': session_id,
                'type': 'thought',
                'content': thought,
                'context': context or {},
                'timestamp': datetime.now().isoformat()
            }
            self.records.append(record)
            if session_id in self.sessions:
                self.sessions[session_id]['records'].append(record)
            return record
            
        def record_action(self, session_id: str, action: Dict, result: Dict = None):
            record = {
                'id': len(self.records) + 1,
                'session_id': session_id,
                'type': 'action',
                'content': action,
                'result': result or {},
                'timestamp': datetime.now().isoformat()
            }
            self.records.append(record)
            if session_id in self.sessions:
                self.sessions[session_id]['records'].append(record)
            return record

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("thought_action_recorder_mcp")

class ThoughtActionRecorderMCP(BaseMCP):
    """ThoughtActionRecorder的MCP包装器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="ThoughtActionRecorderMCP")
        
        # 解析配置
        config = config or {}
        
        # 初始化ThoughtActionRecorder
        try:
            self.recorder = ThoughtActionRecorder()
            self.is_available = THOUGHT_ACTION_RECORDER_AVAILABLE
        except Exception as e:
            self.logger.error(f"ThoughtActionRecorder初始化失败: {e}")
            self.recorder = None
            self.is_available = False
        
        # 初始化指标
        self.metrics = {
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0,
            'total_execution_time': 0,
            'thoughts_recorded': 0,
            'actions_recorded': 0,
            'sessions_created': 0
        }
        
        self.logger.info(f"ThoughtActionRecorder MCP适配器初始化完成，可用性: {self.is_available}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP协议标准处理方法"""
        start_time = datetime.now()
        
        try:
            # 1. 输入验证
            if not self.validate_input(input_data):
                return self._create_error_response("输入验证失败", "INVALID_INPUT")
            
            # 2. 检查适配器可用性
            if not self.is_available:
                return self._create_error_response("ThoughtActionRecorder不可用", "ADAPTER_UNAVAILABLE")
            
            # 3. 解析操作类型
            action = input_data.get('action', 'record_thought')
            parameters = input_data.get('parameters', {})
            
            # 4. 执行相应操作
            if action == 'start_session':
                result = self._start_session(parameters)
            elif action == 'record_thought':
                result = self._record_thought(parameters)
            elif action == 'record_action':
                result = self._record_action(parameters)
            elif action == 'get_session_data':
                result = self._get_session_data(parameters)
            elif action == 'get_training_data':
                result = self._get_training_data(parameters)
            elif action == 'export_data':
                result = self._export_data(parameters)
            elif action == 'get_capabilities':
                result = {'capabilities': self.get_capabilities()}
            elif action == 'get_status':
                result = self._get_status()
            else:
                return self._create_error_response(f"不支持的操作: {action}", "UNSUPPORTED_ACTION")
            
            # 5. 记录成功指标
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(execution_time, True)
            
            # 6. 返回标准化结果
            return {
                'status': 'success',
                'data': {
                    'result': result,
                    'metrics': self._get_execution_metrics()
                },
                'metadata': {
                    'adapter_name': self.name,
                    'action': action,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
            }
            
        except Exception as e:
            # 记录错误指标
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(execution_time, False)
            
            self.logger.error(f"ThoughtActionRecorder执行失败: {str(e)}")
            return self._create_error_response(str(e), "EXECUTION_ERROR")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get('action', 'record_thought')
        parameters = input_data.get('parameters', {})
        
        # 验证必需参数
        if action == 'start_session':
            return True  # agent_type是可选的
        elif action == 'record_thought':
            return 'session_id' in parameters and 'thought' in parameters
        elif action == 'record_action':
            return 'session_id' in parameters and 'action' in parameters
        elif action == 'get_session_data':
            return 'session_id' in parameters
        elif action in ['get_training_data', 'export_data', 'get_capabilities', 'get_status']:
            return True
        else:
            return False
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力列表"""
        return [
            "thought_recording",
            "action_logging",
            "session_management",
            "training_data_collection",
            "data_export",
            "analytics_support",
            "srt_integration",
            "context_tracking"
        ]
    
    def _start_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """启动新会话"""
        agent_type = parameters.get('agent_type', 'default')
        
        if self.recorder and hasattr(self.recorder, 'start_session'):
            session_id = self.recorder.start_session(agent_type)
        else:
            # Mock实现
            session_id = f"session_{self.metrics['sessions_created'] + 1}"
        
        self.metrics['sessions_created'] += 1
        
        return {
            'action': 'start_session',
            'session_id': session_id,
            'agent_type': agent_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def _record_thought(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """记录思考"""
        session_id = parameters.get('session_id')
        thought = parameters.get('thought')
        context = parameters.get('context', {})
        
        if self.recorder and hasattr(self.recorder, 'record_thought'):
            record = self.recorder.record_thought(session_id, thought, context)
        else:
            # Mock实现
            record = {
                'id': self.metrics['thoughts_recorded'] + 1,
                'session_id': session_id,
                'type': 'thought',
                'content': thought,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
        
        self.metrics['thoughts_recorded'] += 1
        
        return {
            'action': 'record_thought',
            'record': record,
            'timestamp': datetime.now().isoformat()
        }
    
    def _record_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """记录行动"""
        session_id = parameters.get('session_id')
        action = parameters.get('action')
        result = parameters.get('result', {})
        
        if self.recorder and hasattr(self.recorder, 'record_action'):
            record = self.recorder.record_action(session_id, action, result)
        else:
            # Mock实现
            record = {
                'id': self.metrics['actions_recorded'] + 1,
                'session_id': session_id,
                'type': 'action',
                'content': action,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
        
        self.metrics['actions_recorded'] += 1
        
        return {
            'action': 'record_action',
            'record': record,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_session_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取会话数据"""
        session_id = parameters.get('session_id')
        
        if self.recorder and hasattr(self.recorder, 'sessions'):
            session_data = self.recorder.sessions.get(session_id, {})
        else:
            session_data = {}
        
        return {
            'action': 'get_session_data',
            'session_id': session_id,
            'session_data': session_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_training_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取训练数据"""
        session_id = parameters.get('session_id')
        format_type = parameters.get('format', 'srt')  # srt, json, csv
        
        if self.recorder and hasattr(self.recorder, 'records'):
            if session_id:
                records = [r for r in self.recorder.records if r.get('session_id') == session_id]
            else:
                records = self.recorder.records
        else:
            records = []
        
        # 转换为训练数据格式
        training_data = self._format_training_data(records, format_type)
        
        return {
            'action': 'get_training_data',
            'session_id': session_id,
            'format': format_type,
            'training_data': training_data,
            'record_count': len(records),
            'timestamp': datetime.now().isoformat()
        }
    
    def _export_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """导出数据"""
        export_format = parameters.get('format', 'json')
        session_id = parameters.get('session_id')
        
        if self.recorder and hasattr(self.recorder, 'records'):
            if session_id:
                data = [r for r in self.recorder.records if r.get('session_id') == session_id]
            else:
                data = self.recorder.records
        else:
            data = []
        
        # 生成导出文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thought_action_export_{timestamp}.{export_format}"
        
        return {
            'action': 'export_data',
            'format': export_format,
            'filename': filename,
            'record_count': len(data),
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _format_training_data(self, records: List[Dict], format_type: str) -> List[Dict]:
        """格式化训练数据"""
        if format_type == 'srt':
            # SRT (Self-Reward Training) 格式
            training_pairs = []
            thoughts = [r for r in records if r.get('type') == 'thought']
            actions = [r for r in records if r.get('type') == 'action']
            
            for thought in thoughts:
                # 找到对应的行动
                corresponding_actions = [
                    a for a in actions 
                    if a.get('session_id') == thought.get('session_id') and 
                    a.get('timestamp', '') > thought.get('timestamp', '')
                ]
                
                if corresponding_actions:
                    action = corresponding_actions[0]  # 取最近的行动
                    training_pairs.append({
                        'thought': thought.get('content', ''),
                        'action': action.get('content', {}),
                        'result': action.get('result', {}),
                        'reward': self._calculate_reward(action.get('result', {}))
                    })
            
            return training_pairs
        else:
            return records
    
    def _calculate_reward(self, result: Dict) -> float:
        """计算奖励值"""
        # 简单的奖励计算逻辑
        if result.get('success', False):
            return 1.0
        elif result.get('partial_success', False):
            return 0.5
        else:
            return 0.0
    
    def _get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            'action': 'get_status',
            'status': {
                'is_available': self.is_available,
                'thoughts_recorded': self.metrics['thoughts_recorded'],
                'actions_recorded': self.metrics['actions_recorded'],
                'sessions_created': self.metrics['sessions_created'],
                'success_rate': self._calculate_success_rate(),
                'uptime': 'active'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if self.metrics['execution_count'] > 0:
            return self.metrics['success_count'] / self.metrics['execution_count']
        return 0.0
    
    def _create_error_response(self, message: str, error_code: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            'status': 'error',
            'error': {
                'code': error_code,
                'message': message,
                'timestamp': datetime.now().isoformat()
            },
            'metadata': {
                'adapter_name': self.name,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _record_execution(self, execution_time: float, success: bool):
        """记录执行指标"""
        self.metrics['execution_count'] += 1
        self.metrics['total_execution_time'] += execution_time
        
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
    
    def _get_execution_metrics(self) -> Dict[str, Any]:
        """获取执行指标"""
        if self.metrics['execution_count'] > 0:
            avg_time = self.metrics['total_execution_time'] / self.metrics['execution_count']
            success_rate = self.metrics['success_count'] / self.metrics['execution_count']
        else:
            avg_time = 0
            success_rate = 0
        
        return {
            'execution_count': self.metrics['execution_count'],
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'thoughts_recorded': self.metrics['thoughts_recorded'],
            'actions_recorded': self.metrics['actions_recorded'],
            'sessions_created': self.metrics['sessions_created'],
            'availability': self.is_available
        }

def test_thought_action_recorder_mcp():
    """测试ThoughtActionRecorder MCP适配器"""
    print("=== 测试ThoughtActionRecorder MCP适配器 ===")
    
    # 创建适配器实例
    adapter = ThoughtActionRecorderMCP()
    
    # 测试启动会话
    start_input = {
        'action': 'start_session',
        'parameters': {
            'agent_type': 'test_agent'
        }
    }
    
    result = adapter.process(start_input)
    print(f"启动会话结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result['status'] == 'success':
        session_id = result['data']['result']['session_id']
        
        # 测试记录思考
        thought_input = {
            'action': 'record_thought',
            'parameters': {
                'session_id': session_id,
                'thought': '我需要分析这个问题的根本原因',
                'context': {'problem_type': 'performance', 'severity': 'high'}
            }
        }
        
        result = adapter.process(thought_input)
        print(f"记录思考结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 测试记录行动
        action_input = {
            'action': 'record_action',
            'parameters': {
                'session_id': session_id,
                'action': {
                    'type': 'analyze_logs',
                    'target': 'application_logs',
                    'method': 'pattern_analysis'
                },
                'result': {
                    'success': True,
                    'findings': ['高CPU使用率', '内存泄漏'],
                    'confidence': 0.9
                }
            }
        }
        
        result = adapter.process(action_input)
        print(f"记录行动结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 测试获取训练数据
        training_input = {
            'action': 'get_training_data',
            'parameters': {
                'session_id': session_id,
                'format': 'srt'
            }
        }
        
        result = adapter.process(training_input)
        print(f"获取训练数据结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_thought_action_recorder_mcp()

