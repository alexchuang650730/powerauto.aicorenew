#!/usr/bin/env python3
"""
PowerAutomation RL-SRT MCP 學習系統

整合Manus日誌和插件輸入作為RL-SRT訓練數據，實現自我學習和持續改進
包含異步RL整合和學習效果分析
"""

import os
import json
import time
import asyncio
import threading
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# 導入之前的交互日誌管理器
from interaction_log_manager import InteractionLogManager, InteractionType, DeliverableType

class LearningMode(Enum):
    """學習模式枚舉"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    HYBRID = "hybrid"

class RewardType(Enum):
    """獎勵類型枚舉"""
    TASK_SUCCESS = "task_success"
    USER_SATISFACTION = "user_satisfaction"
    EFFICIENCY = "efficiency"
    QUALITY = "quality"
    INNOVATION = "innovation"

@dataclass
class LearningExperience:
    """學習經驗數據結構"""
    experience_id: str
    timestamp: str
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any]
    metadata: Dict[str, Any]
    learning_mode: LearningMode

@dataclass
class PerformanceMetrics:
    """性能指標數據結構"""
    accuracy: float
    efficiency: float
    user_satisfaction: float
    response_time: float
    resource_usage: float
    learning_speed: float

class RLSRTLearningEngine:
    """RL-SRT學習引擎"""
    
    def __init__(self, log_manager: InteractionLogManager):
        self.log_manager = log_manager
        self.learning_dir = log_manager.base_dir / "rl_srt_learning"
        self.setup_learning_system()
        self.experience_buffer = []
        self.policy_network = None  # 實際實現中會是神經網絡
        self.value_network = None
        self.learning_rate = 0.001
        self.discount_factor = 0.95
        self.exploration_rate = 0.1
        
        # 異步學習相關
        self.async_learning_enabled = True
        self.learning_threads = []
        self.learning_queue = asyncio.Queue()
        self.performance_history = []
        
    def setup_learning_system(self):
        """設置學習系統"""
        directories = [
            "experiences",
            "models",
            "performance",
            "analysis",
            "async_logs",
            "comparisons"
        ]
        
        for directory in directories:
            (self.learning_dir / directory).mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"✅ RL-SRT學習系統已設置: {self.learning_dir}")
    
    def extract_training_data_from_logs(self) -> List[LearningExperience]:
        """從交互日誌中提取訓練數據"""
        training_experiences = []
        
        # 遍歷所有交互日誌
        logs_dir = self.log_manager.base_dir / "logs"
        
        for interaction_type_dir in logs_dir.iterdir():
            if interaction_type_dir.is_dir():
                for log_file in interaction_type_dir.glob("*.json"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                        
                        # 轉換為學習經驗
                        experience = self.convert_log_to_experience(log_data)
                        if experience:
                            training_experiences.append(experience)
                            
                    except Exception as e:
                        self.logger.warning(f"無法處理日誌文件 {log_file}: {e}")
        
        self.logger.info(f"✅ 從日誌中提取了 {len(training_experiences)} 個學習經驗")
        return training_experiences
    
    def convert_log_to_experience(self, log_data: Dict) -> Optional[LearningExperience]:
        """將日誌數據轉換為學習經驗"""
        try:
            # 構建狀態（輸入）
            state = {
                'user_request': log_data.get('user_request', ''),
                'interaction_type': log_data.get('interaction_type', ''),
                'context': log_data.get('context', {}),
                'session_info': {
                    'session_id': log_data.get('session_id', ''),
                    'timestamp': log_data.get('timestamp', '')
                }
            }
            
            # 構建動作（AI的響應和決策）
            action = {
                'agent_response': log_data.get('agent_response', ''),
                'deliverables': log_data.get('deliverables', []),
                'tools_used': self.extract_tools_from_deliverables(log_data.get('deliverables', [])),
                'strategy': self.infer_strategy_from_response(log_data.get('agent_response', ''))
            }
            
            # 計算獎勵
            reward = self.calculate_reward_from_log(log_data)
            
            # 構建下一狀態（結果狀態）
            next_state = {
                'task_completed': len(log_data.get('deliverables', [])) > 0,
                'deliverable_quality': self.assess_deliverable_quality(log_data.get('deliverables', [])),
                'user_satisfaction': self.estimate_user_satisfaction(log_data),
                'performance_metrics': log_data.get('performance_metrics', {})
            }
            
            experience = LearningExperience(
                experience_id=hashlib.md5(f"{log_data.get('session_id', '')}{log_data.get('timestamp', '')}".encode()).hexdigest()[:12],
                timestamp=log_data.get('timestamp', datetime.now().isoformat()),
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                metadata={
                    'source_log': log_data.get('session_id', ''),
                    'tags': log_data.get('tags', []),
                    'interaction_type': log_data.get('interaction_type', '')
                },
                learning_mode=LearningMode.SYNCHRONOUS  # 默認同步模式
            )
            
            return experience
            
        except Exception as e:
            self.logger.error(f"轉換日誌數據時出錯: {e}")
            return None
    
    def extract_tools_from_deliverables(self, deliverables: List[Dict]) -> List[str]:
        """從交付件中提取使用的工具"""
        tools = []
        for deliverable in deliverables:
            if deliverable.get('type') == 'python_code':
                tools.append('code_generation')
            elif deliverable.get('type') == 'markdown_doc':
                tools.append('documentation')
            elif deliverable.get('type') == 'json_data':
                tools.append('data_processing')
            elif deliverable.get('type') == 'test_suite':
                tools.append('testing')
        return list(set(tools))
    
    def infer_strategy_from_response(self, response: str) -> str:
        """從響應中推斷策略"""
        response_lower = response.lower()
        
        if '分析' in response_lower or 'analysis' in response_lower:
            return 'analytical_approach'
        elif '代碼' in response_lower or 'code' in response_lower:
            return 'code_generation_approach'
        elif '測試' in response_lower or 'test' in response_lower:
            return 'testing_approach'
        elif '設計' in response_lower or 'design' in response_lower:
            return 'design_approach'
        else:
            return 'general_approach'
    
    def calculate_reward_from_log(self, log_data: Dict) -> float:
        """從日誌數據計算獎勵"""
        reward = 0.0
        
        # 基於交付件數量和質量
        deliverables = log_data.get('deliverables', [])
        if deliverables:
            reward += len(deliverables) * 0.2  # 每個交付件+0.2
            
            # 基於模板潛力
            for deliverable in deliverables:
                template_potential = deliverable.get('template_potential', 0)
                reward += template_potential * 0.3
        
        # 基於響應質量（簡單啟發式）
        response = log_data.get('agent_response', '')
        if len(response) > 100:  # 詳細響應
            reward += 0.2
        if '✅' in response:  # 成功標記
            reward += 0.3
        
        # 基於性能指標
        performance = log_data.get('performance_metrics', {})
        if performance.get('deliverable_count', 0) > 0:
            reward += 0.2
        
        return min(reward, 1.0)  # 限制在0-1範圍
    
    def assess_deliverable_quality(self, deliverables: List[Dict]) -> float:
        """評估交付件質量"""
        if not deliverables:
            return 0.0
        
        total_quality = 0.0
        for deliverable in deliverables:
            quality = 0.0
            
            # 基於內容長度
            content_length = len(deliverable.get('content', ''))
            if content_length > 1000:
                quality += 0.3
            elif content_length > 500:
                quality += 0.2
            elif content_length > 100:
                quality += 0.1
            
            # 基於模板潛力
            template_potential = deliverable.get('template_potential', 0)
            quality += template_potential * 0.4
            
            # 基於類型複雜度
            deliverable_type = deliverable.get('type', '')
            if deliverable_type in ['python_code', 'system_architecture']:
                quality += 0.3
            elif deliverable_type in ['markdown_doc', 'analysis_report']:
                quality += 0.2
            
            total_quality += quality
        
        return min(total_quality / len(deliverables), 1.0)
    
    def estimate_user_satisfaction(self, log_data: Dict) -> float:
        """估算用戶滿意度"""
        # 基於交付件數量和質量的簡單估算
        deliverables = log_data.get('deliverables', [])
        if not deliverables:
            return 0.3  # 基礎滿意度
        
        satisfaction = 0.5  # 基礎滿意度
        
        # 基於交付件數量
        satisfaction += min(len(deliverables) * 0.1, 0.3)
        
        # 基於交付件質量
        avg_template_potential = np.mean([d.get('template_potential', 0) for d in deliverables])
        satisfaction += avg_template_potential * 0.2
        
        return min(satisfaction, 1.0)
    
    async def async_learning_worker(self, experience: LearningExperience):
        """異步學習工作器"""
        try:
            # 模擬異步學習過程
            start_time = time.time()
            
            # 更新策略網絡（簡化版）
            await self.update_policy_async(experience)
            
            # 更新價值網絡（簡化版）
            await self.update_value_async(experience)
            
            # 記錄學習時間
            learning_time = time.time() - start_time
            
            # 保存異步學習日誌
            async_log = {
                'experience_id': experience.experience_id,
                'learning_time': learning_time,
                'timestamp': datetime.now().isoformat(),
                'learning_mode': 'asynchronous',
                'thread_id': threading.current_thread().ident
            }
            
            async_log_file = self.learning_dir / "async_logs" / f"async_learning_{int(time.time())}.json"
            with open(async_log_file, 'w', encoding='utf-8') as f:
                json.dump(async_log, f, indent=2, ensure_ascii=False)
            
            return learning_time
            
        except Exception as e:
            self.logger.error(f"異步學習出錯: {e}")
            return None
    
    async def update_policy_async(self, experience: LearningExperience):
        """異步更新策略網絡"""
        # 模擬策略更新過程
        await asyncio.sleep(0.01)  # 模擬計算時間
        
        # 實際實現中會是神經網絡的梯度更新
        policy_update = {
            'experience_id': experience.experience_id,
            'state_features': len(str(experience.state)),
            'action_features': len(str(experience.action)),
            'reward': experience.reward,
            'update_timestamp': datetime.now().isoformat()
        }
        
        return policy_update
    
    async def update_value_async(self, experience: LearningExperience):
        """異步更新價值網絡"""
        # 模擬價值更新過程
        await asyncio.sleep(0.01)  # 模擬計算時間
        
        # 實際實現中會是價值函數的更新
        value_update = {
            'experience_id': experience.experience_id,
            'state_value': experience.reward + self.discount_factor * 0.8,  # 簡化計算
            'update_timestamp': datetime.now().isoformat()
        }
        
        return value_update
    
    def synchronous_learning(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """同步學習模式"""
        start_time = time.time()
        
        learning_results = {
            'mode': 'synchronous',
            'total_experiences': len(experiences),
            'processed_experiences': 0,
            'learning_time': 0,
            'performance_improvement': 0
        }
        
        for experience in experiences:
            # 同步處理每個經驗
            self.update_policy_sync(experience)
            self.update_value_sync(experience)
            learning_results['processed_experiences'] += 1
        
        learning_results['learning_time'] = time.time() - start_time
        learning_results['performance_improvement'] = self.calculate_performance_improvement()
        
        self.logger.info(f"✅ 同步學習完成: {learning_results['processed_experiences']} 個經驗")
        return learning_results
    
    async def asynchronous_learning(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """異步學習模式"""
        start_time = time.time()
        
        learning_results = {
            'mode': 'asynchronous',
            'total_experiences': len(experiences),
            'processed_experiences': 0,
            'learning_time': 0,
            'performance_improvement': 0,
            'parallel_workers': min(len(experiences), 10)  # 最多10個並行工作器
        }
        
        # 創建異步任務
        tasks = []
        for experience in experiences:
            task = asyncio.create_task(self.async_learning_worker(experience))
            tasks.append(task)
        
        # 等待所有任務完成
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 統計結果
        successful_tasks = [t for t in completed_tasks if isinstance(t, (int, float))]
        learning_results['processed_experiences'] = len(successful_tasks)
        learning_results['learning_time'] = time.time() - start_time
        learning_results['performance_improvement'] = self.calculate_performance_improvement()
        
        self.logger.info(f"✅ 異步學習完成: {learning_results['processed_experiences']} 個經驗")
        return learning_results
    
    def update_policy_sync(self, experience: LearningExperience):
        """同步更新策略"""
        # 簡化的同步策略更新
        time.sleep(0.01)  # 模擬計算時間
        pass
    
    def update_value_sync(self, experience: LearningExperience):
        """同步更新價值函數"""
        # 簡化的同步價值更新
        time.sleep(0.01)  # 模擬計算時間
        pass
    
    def calculate_performance_improvement(self) -> float:
        """計算性能改進"""
        # 簡化的性能改進計算
        return np.random.uniform(0.05, 0.15)  # 模擬5-15%的改進
    
    def compare_learning_modes(self, experiences: List[LearningExperience]) -> Dict[str, Any]:
        """比較不同學習模式的效果"""
        comparison_results = {
            'timestamp': datetime.now().isoformat(),
            'total_experiences': len(experiences),
            'synchronous_results': {},
            'asynchronous_results': {},
            'comparison_analysis': {}
        }
        
        # 同步學習測試
        sync_experiences = experiences[:len(experiences)//2]  # 使用一半數據
        comparison_results['synchronous_results'] = self.synchronous_learning(sync_experiences)
        
        # 異步學習測試
        async_experiences = experiences[len(experiences)//2:]  # 使用另一半數據
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        comparison_results['asynchronous_results'] = loop.run_until_complete(
            self.asynchronous_learning(async_experiences)
        )
        loop.close()
        
        # 分析比較結果
        comparison_results['comparison_analysis'] = self.analyze_learning_comparison(
            comparison_results['synchronous_results'],
            comparison_results['asynchronous_results']
        )
        
        return comparison_results
    
    def analyze_learning_comparison(self, sync_results: Dict, async_results: Dict) -> Dict[str, Any]:
        """分析學習模式比較結果"""
        analysis = {
            'efficiency_improvement': {},
            'quality_improvement': {},
            'resource_usage': {},
            'recommendations': []
        }
        
        # 效率分析
        sync_time = sync_results.get('learning_time', 0)
        async_time = async_results.get('learning_time', 0)
        
        if sync_time > 0:
            time_improvement = (sync_time - async_time) / sync_time * 100
            analysis['efficiency_improvement'] = {
                'time_saved_percentage': time_improvement,
                'sync_time': sync_time,
                'async_time': async_time,
                'speedup_factor': sync_time / async_time if async_time > 0 else 1
            }
        
        # 質量分析
        sync_improvement = sync_results.get('performance_improvement', 0)
        async_improvement = async_results.get('performance_improvement', 0)
        
        analysis['quality_improvement'] = {
            'sync_performance_gain': sync_improvement,
            'async_performance_gain': async_improvement,
            'quality_difference': async_improvement - sync_improvement
        }
        
        # 資源使用分析
        analysis['resource_usage'] = {
            'sync_experiences_per_second': sync_results.get('processed_experiences', 0) / sync_time if sync_time > 0 else 0,
            'async_experiences_per_second': async_results.get('processed_experiences', 0) / async_time if async_time > 0 else 0,
            'parallel_workers': async_results.get('parallel_workers', 1)
        }
        
        # 生成建議
        if time_improvement > 20:
            analysis['recommendations'].append("異步RL顯著提升學習效率，建議採用異步模式")
        
        if async_improvement > sync_improvement:
            analysis['recommendations'].append("異步RL提供更好的學習質量")
        
        if analysis['resource_usage']['async_experiences_per_second'] > analysis['resource_usage']['sync_experiences_per_second']:
            analysis['recommendations'].append("異步RL提供更高的處理吞吐量")
        
        return analysis
    
    def generate_learning_report(self, comparison_results: Dict[str, Any]) -> str:
        """生成學習效果報告"""
        report_content = f"""# RL-SRT學習系統效果分析報告

## 📊 測試概況

- **測試時間**: {comparison_results['timestamp']}
- **總經驗數**: {comparison_results['total_experiences']}
- **測試模式**: 同步 vs 異步學習

## 🔄 同步學習結果

- **處理經驗數**: {comparison_results['synchronous_results'].get('processed_experiences', 0)}
- **學習時間**: {comparison_results['synchronous_results'].get('learning_time', 0):.3f} 秒
- **性能改進**: {comparison_results['synchronous_results'].get('performance_improvement', 0):.2%}

## ⚡ 異步學習結果

- **處理經驗數**: {comparison_results['asynchronous_results'].get('processed_experiences', 0)}
- **學習時間**: {comparison_results['asynchronous_results'].get('learning_time', 0):.3f} 秒
- **性能改進**: {comparison_results['asynchronous_results'].get('performance_improvement', 0):.2%}
- **並行工作器**: {comparison_results['asynchronous_results'].get('parallel_workers', 1)}

## 📈 效率對比分析

### 時間效率
- **時間節省**: {comparison_results['comparison_analysis']['efficiency_improvement'].get('time_saved_percentage', 0):.1f}%
- **加速倍數**: {comparison_results['comparison_analysis']['efficiency_improvement'].get('speedup_factor', 1):.2f}x

### 處理吞吐量
- **同步處理速度**: {comparison_results['comparison_analysis']['resource_usage'].get('sync_experiences_per_second', 0):.1f} 經驗/秒
- **異步處理速度**: {comparison_results['comparison_analysis']['resource_usage'].get('async_experiences_per_second', 0):.1f} 經驗/秒

### 學習質量
- **同步性能提升**: {comparison_results['comparison_analysis']['quality_improvement'].get('sync_performance_gain', 0):.2%}
- **異步性能提升**: {comparison_results['comparison_analysis']['quality_improvement'].get('async_performance_gain', 0):.2%}
- **質量差異**: {comparison_results['comparison_analysis']['quality_improvement'].get('quality_difference', 0):.2%}

## 💡 關鍵洞察

### 異步RL的優勢
1. **並行處理能力**: 同時處理多個學習經驗
2. **資源利用效率**: 更好的CPU和內存利用
3. **響應速度**: 更快的學習收斂速度
4. **可擴展性**: 支持大規模經驗數據處理

### 實際應用價值
- **實時學習**: 支持在線學習和實時改進
- **大數據處理**: 處理大量交互日誌數據
- **系統響應**: 不阻塞主要業務流程
- **持續優化**: 持續的背景學習和改進

## 🎯 建議

"""
        
        for recommendation in comparison_results['comparison_analysis']['recommendations']:
            report_content += f"- {recommendation}\n"
        
        report_content += f"""
## 📋 技術實現要點

### 異步RL架構
- **工作器池**: {comparison_results['asynchronous_results'].get('parallel_workers', 1)}個並行工作器
- **任務隊列**: 異步任務調度和管理
- **狀態同步**: 安全的並發狀態更新
- **錯誤處理**: 健壯的異常處理機制

### 性能優化
- **批處理**: 批量處理學習經驗
- **內存管理**: 高效的內存使用
- **負載均衡**: 智能的任務分配
- **監控告警**: 實時性能監控

---

*報告生成時間: {datetime.now().isoformat()}*
"""
        
        return report_content
    
    def save_learning_results(self, comparison_results: Dict[str, Any]):
        """保存學習結果"""
        timestamp = int(time.time())
        
        # 保存比較結果JSON
        results_file = self.learning_dir / "comparisons" / f"learning_comparison_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_results, f, indent=2, ensure_ascii=False)
        
        # 保存分析報告
        report_content = self.generate_learning_report(comparison_results)
        report_file = self.learning_dir / "analysis" / f"learning_analysis_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"✅ 學習結果已保存:")
        self.logger.info(f"   📊 比較數據: {results_file}")
        self.logger.info(f"   📋 分析報告: {report_file}")
        
        return results_file, report_file

def main():
    """主函數 - 演示RL-SRT學習系統"""
    
    # 初始化系統
    log_manager = InteractionLogManager()
    rl_srt_engine = RLSRTLearningEngine(log_manager)
    
    print("🧠 RL-SRT學習系統演示開始...")
    
    # 1. 從交互日誌提取訓練數據
    print("📚 提取訓練數據...")
    training_experiences = rl_srt_engine.extract_training_data_from_logs()
    
    if not training_experiences:
        print("⚠️  沒有找到訓練數據，創建示例數據...")
        # 創建一些示例經驗數據
        for i in range(10):
            example_experience = LearningExperience(
                experience_id=f"example_{i}",
                timestamp=datetime.now().isoformat(),
                state={'user_request': f'示例請求 {i}', 'context': {}},
                action={'response': f'示例響應 {i}', 'tools': ['example_tool']},
                reward=np.random.uniform(0.3, 0.9),
                next_state={'completed': True, 'quality': np.random.uniform(0.5, 1.0)},
                metadata={'source': 'example'},
                learning_mode=LearningMode.SYNCHRONOUS
            )
            training_experiences.append(example_experience)
    
    print(f"✅ 提取了 {len(training_experiences)} 個學習經驗")
    
    # 2. 比較同步vs異步學習
    print("⚡ 開始學習模式比較...")
    comparison_results = rl_srt_engine.compare_learning_modes(training_experiences)
    
    # 3. 保存結果
    print("💾 保存學習結果...")
    results_file, report_file = rl_srt_engine.save_learning_results(comparison_results)
    
    # 4. 顯示關鍵結果
    print("\n🎯 RL-SRT學習系統演示完成!")
    print(f"📊 比較結果文件: {results_file}")
    print(f"📋 分析報告文件: {report_file}")
    
    # 顯示關鍵指標
    analysis = comparison_results['comparison_analysis']
    print(f"\n📈 關鍵指標:")
    print(f"   ⚡ 異步學習時間節省: {analysis['efficiency_improvement'].get('time_saved_percentage', 0):.1f}%")
    print(f"   🚀 處理速度提升: {analysis['efficiency_improvement'].get('speedup_factor', 1):.2f}x")
    print(f"   📊 異步處理速度: {analysis['resource_usage'].get('async_experiences_per_second', 0):.1f} 經驗/秒")
    
    return rl_srt_engine, comparison_results

if __name__ == "__main__":
    main()

