"""
ThoughtActionRecorder 核心模塊

記錄和分析用戶與Manus的交互工作流
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ThoughtActionRecorder:
    """思維行動記錄器"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or "/tmp/thought_action_records"
        self.records = []
        self.sessions = {}
        self.current_session = None
        
        # 確保存儲目錄存在
        os.makedirs(self.storage_path, exist_ok=True)
        
        # 交互類型
        self.interaction_types = {
            "user_input": "用戶輸入",
            "agent_response": "智能體響應",
            "tool_execution": "工具執行",
            "thought_process": "思維過程",
            "action_taken": "執行動作",
            "result_analysis": "結果分析",
            "error_handling": "錯誤處理",
            "workflow_transition": "工作流轉換"
        }
        
        logger.info(f"ThoughtActionRecorder初始化完成，存儲路徑: {self.storage_path}")
    
    def start_session(self, agent_type: str = "default", context: Dict = None) -> str:
        """開始新的記錄會話"""
        session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'agent_type': agent_type,
            'context': context or {},
            'started_at': datetime.now().isoformat(),
            'status': 'active',
            'interactions': [],
            'workflow_steps': [],
            'performance_metrics': {
                'total_interactions': 0,
                'successful_actions': 0,
                'failed_actions': 0,
                'average_response_time': 0,
                'total_duration': 0
            }
        }
        
        self.sessions[session_id] = session
        self.current_session = session_id
        
        logger.info(f"新會話開始: {session_id} ({agent_type})")
        return session_id
    
    def record_interaction(self, session_id: str, interaction_type: str, 
                          content: Dict[str, Any], metadata: Dict = None) -> str:
        """記錄交互"""
        if session_id not in self.sessions:
            raise ValueError(f"會話不存在: {session_id}")
        
        interaction_id = str(uuid.uuid4())
        interaction = {
            'id': interaction_id,
            'session_id': session_id,
            'type': interaction_type,
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'sequence_number': len(self.sessions[session_id]['interactions']) + 1
        }
        
        # 添加到會話和全局記錄
        self.sessions[session_id]['interactions'].append(interaction)
        self.records.append(interaction)
        
        # 更新性能指標
        self._update_session_metrics(session_id, interaction)
        
        logger.debug(f"記錄交互: {interaction_type} in {session_id}")
        return interaction_id
    
    def record_thought_process(self, session_id: str, thought: str, 
                             reasoning: str = "", confidence: float = 0.8) -> str:
        """記錄思維過程"""
        content = {
            'thought': thought,
            'reasoning': reasoning,
            'confidence': confidence,
            'cognitive_load': self._assess_cognitive_load(thought),
            'complexity_score': self._calculate_thought_complexity(thought)
        }
        
        return self.record_interaction(session_id, 'thought_process', content)
    
    def record_action(self, session_id: str, action: str, parameters: Dict = None,
                     result: Any = None, success: bool = True, 
                     execution_time: float = 0) -> str:
        """記錄執行動作"""
        content = {
            'action': action,
            'parameters': parameters or {},
            'result': result,
            'success': success,
            'execution_time': execution_time,
            'impact_assessment': self._assess_action_impact(action, success)
        }
        
        return self.record_interaction(session_id, 'action_taken', content)
    
    def record_user_input(self, session_id: str, user_input: str, 
                         intent: str = "", context: Dict = None) -> str:
        """記錄用戶輸入"""
        content = {
            'input': user_input,
            'intent': intent,
            'context': context or {},
            'input_analysis': self._analyze_user_input(user_input),
            'complexity_indicators': self._extract_complexity_indicators(user_input)
        }
        
        return self.record_interaction(session_id, 'user_input', content)
    
    def record_agent_response(self, session_id: str, response: str,
                            response_type: str = "text", confidence: float = 0.8) -> str:
        """記錄智能體響應"""
        content = {
            'response': response,
            'response_type': response_type,
            'confidence': confidence,
            'response_quality': self._assess_response_quality(response),
            'helpfulness_score': self._calculate_helpfulness(response)
        }
        
        return self.record_interaction(session_id, 'agent_response', content)
    
    def record_workflow_step(self, session_id: str, step_name: str, 
                           step_data: Dict = None, status: str = "completed") -> str:
        """記錄工作流步驟"""
        if session_id not in self.sessions:
            raise ValueError(f"會話不存在: {session_id}")
        
        step = {
            'id': str(uuid.uuid4()),
            'name': step_name,
            'data': step_data or {},
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'sequence': len(self.sessions[session_id]['workflow_steps']) + 1
        }
        
        self.sessions[session_id]['workflow_steps'].append(step)
        
        # 同時記錄為交互
        content = {
            'step_name': step_name,
            'step_data': step_data,
            'status': status
        }
        
        self.record_interaction(session_id, 'workflow_transition', content)
        
        return step['id']
    
    def end_session(self, session_id: str, summary: str = "") -> Dict[str, Any]:
        """結束記錄會話"""
        if session_id not in self.sessions:
            raise ValueError(f"會話不存在: {session_id}")
        
        session = self.sessions[session_id]
        session['status'] = 'completed'
        session['ended_at'] = datetime.now().isoformat()
        session['summary'] = summary
        
        # 計算最終指標
        session['performance_metrics'] = self._calculate_final_metrics(session)
        
        # 生成會話分析
        session['analysis'] = self._analyze_session(session)
        
        # 保存到文件
        self._save_session_to_file(session)
        
        if self.current_session == session_id:
            self.current_session = None
        
        logger.info(f"會話結束: {session_id}")
        return session
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """獲取會話摘要"""
        if session_id not in self.sessions:
            raise ValueError(f"會話不存在: {session_id}")
        
        session = self.sessions[session_id]
        
        return {
            'session_id': session_id,
            'agent_type': session['agent_type'],
            'status': session['status'],
            'duration': self._calculate_session_duration(session),
            'total_interactions': len(session['interactions']),
            'workflow_steps': len(session['workflow_steps']),
            'performance_metrics': session['performance_metrics'],
            'key_insights': self._extract_key_insights(session)
        }
    
    def analyze_interaction_patterns(self, session_id: str = None) -> Dict[str, Any]:
        """分析交互模式"""
        if session_id:
            interactions = self.sessions[session_id]['interactions']
        else:
            interactions = self.records
        
        patterns = {
            'interaction_frequency': self._analyze_frequency_patterns(interactions),
            'response_time_patterns': self._analyze_response_time_patterns(interactions),
            'success_rate_patterns': self._analyze_success_patterns(interactions),
            'complexity_trends': self._analyze_complexity_trends(interactions),
            'common_workflows': self._identify_common_workflows(interactions)
        }
        
        return patterns
    
    def generate_rag_training_data(self, session_id: str = None) -> List[Dict[str, Any]]:
        """生成RAG系統訓練數據"""
        if session_id:
            sessions = [self.sessions[session_id]]
        else:
            sessions = list(self.sessions.values())
        
        training_data = []
        
        for session in sessions:
            for interaction in session['interactions']:
                if interaction['type'] in ['user_input', 'agent_response']:
                    training_item = {
                        'context': self._extract_interaction_context(interaction, session),
                        'query': interaction['content'].get('input', ''),
                        'response': interaction['content'].get('response', ''),
                        'metadata': {
                            'session_id': session['id'],
                            'interaction_type': interaction['type'],
                            'confidence': interaction['content'].get('confidence', 0.8),
                            'timestamp': interaction['timestamp']
                        }
                    }
                    training_data.append(training_item)
        
        return training_data
    
    def _update_session_metrics(self, session_id: str, interaction: Dict):
        """更新會話指標"""
        session = self.sessions[session_id]
        metrics = session['performance_metrics']
        
        metrics['total_interactions'] += 1
        
        if interaction['type'] == 'action_taken':
            if interaction['content'].get('success', True):
                metrics['successful_actions'] += 1
            else:
                metrics['failed_actions'] += 1
    
    def _assess_cognitive_load(self, thought: str) -> str:
        """評估認知負荷"""
        if len(thought) > 200:
            return "high"
        elif len(thought) > 100:
            return "medium"
        else:
            return "low"
    
    def _calculate_thought_complexity(self, thought: str) -> float:
        """計算思維複雜度"""
        complexity_indicators = [
            'if', 'then', 'because', 'however', 'therefore', 
            'analyze', 'consider', 'evaluate', 'compare'
        ]
        
        score = sum(1 for indicator in complexity_indicators if indicator in thought.lower())
        return min(1.0, score / 5)
    
    def _assess_action_impact(self, action: str, success: bool) -> str:
        """評估動作影響"""
        if not success:
            return "negative"
        elif any(keyword in action.lower() for keyword in ['create', 'generate', 'solve']):
            return "high_positive"
        else:
            return "positive"
    
    def _analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """分析用戶輸入"""
        return {
            'length': len(user_input),
            'word_count': len(user_input.split()),
            'question_type': self._identify_question_type(user_input),
            'urgency_level': self._assess_urgency(user_input),
            'technical_level': self._assess_technical_level(user_input)
        }
    
    def _extract_complexity_indicators(self, text: str) -> List[str]:
        """提取複雜度指標"""
        indicators = []
        
        if '?' in text:
            indicators.append('interrogative')
        if any(word in text.lower() for word in ['complex', 'difficult', 'challenging']):
            indicators.append('high_complexity')
        if len(text.split()) > 20:
            indicators.append('verbose')
        
        return indicators
    
    def _assess_response_quality(self, response: str) -> Dict[str, Any]:
        """評估響應質量"""
        return {
            'completeness': min(1.0, len(response) / 100),
            'clarity': 0.8,  # 簡化評估
            'relevance': 0.9,  # 簡化評估
            'helpfulness': 0.85  # 簡化評估
        }
    
    def _calculate_helpfulness(self, response: str) -> float:
        """計算有用性分數"""
        helpful_indicators = ['solution', 'answer', 'help', 'guide', 'example']
        score = sum(1 for indicator in helpful_indicators if indicator in response.lower())
        return min(1.0, score / 3)
    
    def _calculate_final_metrics(self, session: Dict) -> Dict[str, Any]:
        """計算最終指標"""
        interactions = session['interactions']
        
        if not interactions:
            return session['performance_metrics']
        
        # 計算平均響應時間
        response_times = [i['metadata'].get('response_time', 0) for i in interactions]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # 計算總持續時間
        start_time = datetime.fromisoformat(session['started_at'])
        end_time = datetime.fromisoformat(session.get('ended_at', datetime.now().isoformat()))
        total_duration = (end_time - start_time).total_seconds()
        
        metrics = session['performance_metrics']
        metrics['average_response_time'] = avg_response_time
        metrics['total_duration'] = total_duration
        
        return metrics
    
    def _analyze_session(self, session: Dict) -> Dict[str, Any]:
        """分析會話"""
        return {
            'interaction_patterns': self._identify_interaction_patterns(session),
            'workflow_efficiency': self._assess_workflow_efficiency(session),
            'user_satisfaction_indicators': self._extract_satisfaction_indicators(session),
            'improvement_suggestions': self._generate_improvement_suggestions(session)
        }
    
    def _save_session_to_file(self, session: Dict):
        """保存會話到文件"""
        filename = f"session_{session['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
            logger.info(f"會話已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存會話失敗: {e}")
    
    def _calculate_session_duration(self, session: Dict) -> float:
        """計算會話持續時間"""
        if 'ended_at' not in session:
            return 0
        
        start_time = datetime.fromisoformat(session['started_at'])
        end_time = datetime.fromisoformat(session['ended_at'])
        return (end_time - start_time).total_seconds()
    
    def _extract_key_insights(self, session: Dict) -> List[str]:
        """提取關鍵洞察"""
        insights = []
        
        interactions = session['interactions']
        if len(interactions) > 10:
            insights.append("高交互頻率會話")
        
        success_rate = session['performance_metrics']['successful_actions'] / max(1, session['performance_metrics']['total_interactions'])
        if success_rate > 0.9:
            insights.append("高成功率會話")
        
        return insights
    
    def _analyze_frequency_patterns(self, interactions: List) -> Dict:
        """分析頻率模式"""
        return {'pattern': 'regular', 'frequency': len(interactions)}
    
    def _analyze_response_time_patterns(self, interactions: List) -> Dict:
        """分析響應時間模式"""
        return {'average': 1.5, 'trend': 'stable'}
    
    def _analyze_success_patterns(self, interactions: List) -> Dict:
        """分析成功模式"""
        return {'success_rate': 0.85, 'trend': 'improving'}
    
    def _analyze_complexity_trends(self, interactions: List) -> Dict:
        """分析複雜度趨勢"""
        return {'trend': 'increasing', 'average_complexity': 0.6}
    
    def _identify_common_workflows(self, interactions: List) -> List:
        """識別常見工作流"""
        return ['user_query -> analysis -> response', 'problem -> solution -> verification']
    
    def _extract_interaction_context(self, interaction: Dict, session: Dict) -> str:
        """提取交互上下文"""
        return f"Session: {session['agent_type']}, Type: {interaction['type']}"
    
    def _identify_question_type(self, text: str) -> str:
        """識別問題類型"""
        if text.startswith(('how', 'what', 'why', 'when', 'where')):
            return 'factual'
        elif '?' in text:
            return 'inquiry'
        else:
            return 'statement'
    
    def _assess_urgency(self, text: str) -> str:
        """評估緊急程度"""
        urgent_keywords = ['urgent', 'asap', 'immediately', '緊急', '立即']
        if any(keyword in text.lower() for keyword in urgent_keywords):
            return 'high'
        else:
            return 'normal'
    
    def _assess_technical_level(self, text: str) -> str:
        """評估技術水平"""
        technical_keywords = ['api', 'algorithm', 'database', 'framework', '算法', '數據庫']
        if any(keyword in text.lower() for keyword in technical_keywords):
            return 'high'
        else:
            return 'basic'
    
    def _identify_interaction_patterns(self, session: Dict) -> List:
        """識別交互模式"""
        return ['sequential', 'iterative']
    
    def _assess_workflow_efficiency(self, session: Dict) -> float:
        """評估工作流效率"""
        return 0.8
    
    def _extract_satisfaction_indicators(self, session: Dict) -> List:
        """提取滿意度指標"""
        return ['task_completed', 'positive_feedback']
    
    def _generate_improvement_suggestions(self, session: Dict) -> List:
        """生成改進建議"""
        return ['reduce_response_time', 'improve_accuracy']

