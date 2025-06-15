"""
ThoughtActionRecorder MCP適配器

完整的思維行動記錄MCP適配器，支持：
- 用戶與Manus交互記錄
- RAG系統學習數據生成
- RL-SRT對齊訓練數據
- 工作流分析和優化
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子類必須實現此方法")
        
        def validate_input(self, input_data: Dict[str, Any]) -> bool:
            return True
        
        def get_capabilities(self) -> List[str]:
            return ["基礎MCP適配功能"]

# 導入核心ThoughtActionRecorder
try:
    from mcptool.core.development_tools.thought_action_recorder import ThoughtActionRecorder
    THOUGHT_ACTION_RECORDER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ThoughtActionRecorder導入失敗: {e}")
    THOUGHT_ACTION_RECORDER_AVAILABLE = False
    
    # 創建Mock實現
    class ThoughtActionRecorder:
        def __init__(self, storage_path: str = None):
            self.storage_path = storage_path or "/tmp/thought_action_records"
            self.records = []
            self.sessions = {}
            self.current_session = None
        
        def start_session(self, agent_type: str = "default", context: Dict = None) -> str:
            session_id = f"session_{len(self.sessions) + 1}"
            self.sessions[session_id] = {
                'id': session_id,
                'agent_type': agent_type,
                'context': context or {},
                'started_at': datetime.now().isoformat(),
                'status': 'active',
                'interactions': []
            }
            self.current_session = session_id
            return session_id
        
        def record_interaction(self, session_id: str, interaction_type: str, 
                              content: Dict[str, Any], metadata: Dict = None) -> str:
            interaction_id = f"interaction_{len(self.records) + 1}"
            interaction = {
                'id': interaction_id,
                'session_id': session_id,
                'type': interaction_type,
                'content': content,
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat()
            }
            self.records.append(interaction)
            if session_id in self.sessions:
                self.sessions[session_id]['interactions'].append(interaction)
            return interaction_id

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("thought_action_recorder_mcp")

class ThoughtActionRecorderMCP(BaseMCP):
    """ThoughtActionRecorder的完整MCP包裝器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="ThoughtActionRecorderMCP")
        
        # 解析配置
        config = config or {}
        storage_path = config.get('storage_path', '/tmp/manus_thought_action_records')
        
        # 初始化ThoughtActionRecorder
        try:
            self.recorder = ThoughtActionRecorder(storage_path)
            self.is_available = THOUGHT_ACTION_RECORDER_AVAILABLE
        except Exception as e:
            self.logger.error(f"ThoughtActionRecorder初始化失敗: {e}")
            self.recorder = None
            self.is_available = False
        
        # MCP工具註冊表
        self.tools = {
            "start_session": self._start_session_tool,
            "record_thought": self._record_thought_tool,
            "record_action": self._record_action_tool,
            "record_user_input": self._record_user_input_tool,
            "record_agent_response": self._record_agent_response_tool,
            "record_workflow_step": self._record_workflow_step_tool,
            "end_session": self._end_session_tool,
            "get_session_summary": self._get_session_summary_tool,
            "analyze_patterns": self._analyze_patterns_tool,
            "generate_rag_data": self._generate_rag_data_tool,
            "generate_rl_srt_data": self._generate_rl_srt_data_tool,
            "export_learning_data": self._export_learning_data_tool
        }
        
        # 執行統計
        self.metrics = {
            'total_sessions': 0,
            'total_interactions': 0,
            'active_sessions': 0,
            'rag_data_generated': 0,
            'rl_srt_data_generated': 0,
            'learning_exports': 0
        }
        
        self.logger.info(f"ThoughtActionRecorder MCP適配器初始化完成，可用性: {self.is_available}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """處理MCP請求"""
        try:
            if not self.validate_input(input_data):
                return {"error": "輸入數據驗證失敗", "success": False}
            
            tool_name = input_data.get('tool')
            if not tool_name or tool_name not in self.tools:
                return {
                    "error": f"未知工具: {tool_name}",
                    "available_tools": list(self.tools.keys()),
                    "success": False
                }
            
            # 執行工具
            tool_func = self.tools[tool_name]
            result = tool_func(input_data.get('parameters', {}))
            
            # 更新統計
            self._update_metrics(tool_name, True)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"處理請求失敗: {e}")
            self._update_metrics(input_data.get('tool', 'unknown'), False)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """驗證輸入數據"""
        if not isinstance(input_data, dict):
            return False
        
        if 'tool' not in input_data:
            return False
        
        return True
    
    def get_capabilities(self) -> List[str]:
        """獲取MCP適配器能力"""
        return [
            "session_management",
            "thought_recording",
            "action_recording", 
            "interaction_tracking",
            "workflow_analysis",
            "pattern_recognition",
            "rag_data_generation",
            "rl_srt_data_generation",
            "learning_data_export",
            "performance_analytics"
        ]
    
    # MCP工具實現
    def _start_session_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """開始新的記錄會話"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        agent_type = params.get('agent_type', 'manus')
        context = params.get('context', {})
        
        session_id = self.recorder.start_session(agent_type, context)
        self.metrics['total_sessions'] += 1
        self.metrics['active_sessions'] += 1
        
        return {
            "session_id": session_id,
            "agent_type": agent_type,
            "context": context,
            "started_at": datetime.now().isoformat()
        }
    
    def _record_thought_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """記錄思維過程"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        thought = params.get('thought', '')
        reasoning = params.get('reasoning', '')
        confidence = params.get('confidence', 0.8)
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        interaction_id = self.recorder.record_thought_process(
            session_id, thought, reasoning, confidence
        )
        
        self.metrics['total_interactions'] += 1
        
        return {
            "interaction_id": interaction_id,
            "thought": thought,
            "reasoning": reasoning,
            "confidence": confidence,
            "recorded_at": datetime.now().isoformat()
        }
    
    def _record_action_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """記錄執行動作"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        action = params.get('action', '')
        parameters = params.get('parameters', {})
        result = params.get('result')
        success = params.get('success', True)
        execution_time = params.get('execution_time', 0.0)
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        interaction_id = self.recorder.record_action(
            session_id, action, parameters, result, success, execution_time
        )
        
        self.metrics['total_interactions'] += 1
        
        return {
            "interaction_id": interaction_id,
            "action": action,
            "success": success,
            "execution_time": execution_time,
            "recorded_at": datetime.now().isoformat()
        }
    
    def _record_user_input_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """記錄用戶輸入"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        user_input = params.get('user_input', '')
        intent = params.get('intent', '')
        context = params.get('context', {})
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        interaction_id = self.recorder.record_user_input(
            session_id, user_input, intent, context
        )
        
        self.metrics['total_interactions'] += 1
        
        return {
            "interaction_id": interaction_id,
            "user_input": user_input,
            "intent": intent,
            "recorded_at": datetime.now().isoformat()
        }
    
    def _record_agent_response_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """記錄智能體響應"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        response = params.get('response', '')
        response_type = params.get('response_type', 'text')
        confidence = params.get('confidence', 0.8)
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        interaction_id = self.recorder.record_agent_response(
            session_id, response, response_type, confidence
        )
        
        self.metrics['total_interactions'] += 1
        
        return {
            "interaction_id": interaction_id,
            "response": response,
            "response_type": response_type,
            "confidence": confidence,
            "recorded_at": datetime.now().isoformat()
        }
    
    def _record_workflow_step_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """記錄工作流步驟"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        step_name = params.get('step_name', '')
        step_data = params.get('step_data', {})
        status = params.get('status', 'completed')
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        step_id = self.recorder.record_workflow_step(
            session_id, step_name, step_data, status
        )
        
        return {
            "step_id": step_id,
            "step_name": step_name,
            "status": status,
            "recorded_at": datetime.now().isoformat()
        }
    
    def _end_session_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """結束記錄會話"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        summary = params.get('summary', '')
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        session_data = self.recorder.end_session(session_id, summary)
        self.metrics['active_sessions'] = max(0, self.metrics['active_sessions'] - 1)
        
        return {
            "session_id": session_id,
            "summary": summary,
            "session_data": session_data,
            "ended_at": datetime.now().isoformat()
        }
    
    def _get_session_summary_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """獲取會話摘要"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        
        if not session_id:
            return {"error": "缺少session_id"}
        
        summary = self.recorder.get_session_summary(session_id)
        
        return {
            "session_id": session_id,
            "summary": summary,
            "retrieved_at": datetime.now().isoformat()
        }
    
    def _analyze_patterns_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """分析交互模式"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')  # 可選，如果不提供則分析所有會話
        
        patterns = self.recorder.analyze_interaction_patterns(session_id)
        
        return {
            "session_id": session_id,
            "patterns": patterns,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _generate_rag_data_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成RAG訓練數據"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')  # 可選
        
        rag_data = self.recorder.generate_rag_training_data(session_id)
        self.metrics['rag_data_generated'] += len(rag_data)
        
        return {
            "session_id": session_id,
            "rag_data_count": len(rag_data),
            "rag_data": rag_data,
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_rl_srt_data_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """生成RL-SRT訓練數據"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        session_id = params.get('session_id')
        
        # 生成RL-SRT對齊數據
        rl_srt_data = self._extract_rl_srt_training_data(session_id)
        self.metrics['rl_srt_data_generated'] += len(rl_srt_data)
        
        return {
            "session_id": session_id,
            "rl_srt_data_count": len(rl_srt_data),
            "rl_srt_data": rl_srt_data,
            "generated_at": datetime.now().isoformat()
        }
    
    def _export_learning_data_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """導出學習數據"""
        if not self.recorder:
            return {"error": "記錄器不可用"}
        
        export_format = params.get('format', 'json')
        include_rag = params.get('include_rag', True)
        include_rl_srt = params.get('include_rl_srt', True)
        output_path = params.get('output_path')
        
        # 生成學習數據
        learning_data = {}
        
        if include_rag:
            learning_data['rag_data'] = self.recorder.generate_rag_training_data()
        
        if include_rl_srt:
            learning_data['rl_srt_data'] = self._extract_rl_srt_training_data()
        
        # 導出數據
        if output_path:
            self._save_learning_data(learning_data, output_path, export_format)
        
        self.metrics['learning_exports'] += 1
        
        return {
            "export_format": export_format,
            "output_path": output_path,
            "data_summary": {
                "rag_items": len(learning_data.get('rag_data', [])),
                "rl_srt_items": len(learning_data.get('rl_srt_data', []))
            },
            "exported_at": datetime.now().isoformat()
        }
    
    def _extract_rl_srt_training_data(self, session_id: str = None) -> List[Dict[str, Any]]:
        """提取RL-SRT訓練數據"""
        if not self.recorder:
            return []
        
        # 獲取會話數據
        if session_id:
            sessions = [self.recorder.sessions.get(session_id)]
        else:
            sessions = list(self.recorder.sessions.values())
        
        rl_srt_data = []
        
        for session in sessions:
            if not session:
                continue
            
            interactions = session.get('interactions', [])
            
            # 提取思維-行動對
            for i, interaction in enumerate(interactions):
                if interaction['type'] == 'thought_process':
                    # 查找後續的行動
                    action_interaction = None
                    for j in range(i + 1, min(i + 3, len(interactions))):
                        if interactions[j]['type'] == 'action_taken':
                            action_interaction = interactions[j]
                            break
                    
                    if action_interaction:
                        rl_srt_item = {
                            'session_id': session['id'],
                            'thought': interaction['content']['thought'],
                            'reasoning': interaction['content'].get('reasoning', ''),
                            'confidence': interaction['content'].get('confidence', 0.8),
                            'action': action_interaction['content']['action'],
                            'action_success': action_interaction['content'].get('success', True),
                            'execution_time': action_interaction['content'].get('execution_time', 0.0),
                            'reward_signal': self._calculate_reward_signal(interaction, action_interaction),
                            'alignment_score': self._calculate_alignment_score(interaction, action_interaction),
                            'timestamp': interaction['timestamp']
                        }
                        rl_srt_data.append(rl_srt_item)
        
        return rl_srt_data
    
    def _calculate_reward_signal(self, thought_interaction: Dict, action_interaction: Dict) -> float:
        """計算獎勵信號"""
        # 基於行動成功率和思維信心度計算獎勵
        action_success = action_interaction['content'].get('success', True)
        thought_confidence = thought_interaction['content'].get('confidence', 0.8)
        execution_time = action_interaction['content'].get('execution_time', 0.0)
        
        # 基礎獎勵
        base_reward = 1.0 if action_success else -0.5
        
        # 信心度調整
        confidence_bonus = (thought_confidence - 0.5) * 0.5
        
        # 執行時間懲罰（執行時間越長，獎勵越低）
        time_penalty = min(0.2, execution_time / 10.0)
        
        return base_reward + confidence_bonus - time_penalty
    
    def _calculate_alignment_score(self, thought_interaction: Dict, action_interaction: Dict) -> float:
        """計算對齊分數"""
        # 簡化的對齊分數計算
        thought_confidence = thought_interaction['content'].get('confidence', 0.8)
        action_success = action_interaction['content'].get('success', True)
        
        if action_success:
            return min(1.0, thought_confidence + 0.2)
        else:
            return max(0.0, thought_confidence - 0.3)
    
    def _save_learning_data(self, data: Dict[str, Any], output_path: str, format: str):
        """保存學習數據"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            self.logger.info(f"學習數據已保存: {output_path}")
        
        except Exception as e:
            self.logger.error(f"保存學習數據失敗: {e}")
            raise
    
    def _update_metrics(self, tool_name: str, success: bool):
        """更新執行統計"""
        # 可以根據需要添加更詳細的統計
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """獲取執行統計"""
        return {
            "metrics": self.metrics,
            "is_available": self.is_available,
            "tools_count": len(self.tools),
            "capabilities_count": len(self.get_capabilities()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """獲取工具信息"""
        return {
            "name": "ThoughtActionRecorderMCP",
            "description": "思維行動記錄MCP適配器，支持用戶與Manus交互記錄、RAG學習和RL-SRT對齊",
            "version": "1.0.0",
            "capabilities": self.get_capabilities(),
            "tools": list(self.tools.keys()),
            "is_available": self.is_available,
            "metrics": self.metrics,
            "created_at": datetime.now().isoformat()
        }


# 創建適配器實例的工廠函數
def create_thought_action_recorder_mcp(config: Optional[Dict] = None) -> ThoughtActionRecorderMCP:
    """創建ThoughtActionRecorder MCP適配器實例"""
    return ThoughtActionRecorderMCP(config)


if __name__ == "__main__":
    # 測試示例
    mcp = create_thought_action_recorder_mcp()
    
    # 測試開始會話
    result = mcp.process({
        "tool": "start_session",
        "parameters": {
            "agent_type": "manus",
            "context": {"user_id": "test_user", "task": "test_interaction"}
        }
    })
    print("開始會話結果:", json.dumps(result, indent=2, ensure_ascii=False))
    
    # 獲取工具信息
    info = mcp.get_tool_info()
    print("工具信息:", json.dumps(info, indent=2, ensure_ascii=False))

