#!/usr/bin/env python3
"""
PowerAutomation 智能调度算法实现
基于机器学习的智能任务调度和节点选择

作者: PowerAutomation团队
版本: 1.0.0-production
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import asyncio
import threading
from collections import defaultdict, deque

logger = logging.getLogger("PowerAutomation.SmartScheduler")

@dataclass
class NodePerformanceMetrics:
    """节点性能指标"""
    node_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    task_completion_rate: float
    average_execution_time: float
    error_rate: float
    concurrent_tasks: int
    
    def to_feature_vector(self) -> List[float]:
        """转换为特征向量"""
        return [
            self.cpu_usage,
            self.memory_usage,
            self.disk_io,
            self.network_io,
            self.task_completion_rate,
            self.average_execution_time,
            self.error_rate,
            self.concurrent_tasks
        ]

@dataclass
class TaskCharacteristics:
    """任务特征"""
    task_type: str
    test_level: str
    estimated_duration: float
    resource_requirements: Dict[str, Any]
    priority: int
    dependencies: List[str]
    
    def to_feature_vector(self) -> List[float]:
        """转换为特征向量"""
        # 任务类型编码
        task_type_encoding = {
            "unit_test": 1, "integration_test": 2, "ui_test": 3,
            "performance_test": 4, "security_test": 5, "api_test": 6,
            "load_test": 7, "stress_test": 8, "end_to_end_test": 9
        }
        
        # 测试级别编码
        level_encoding = {f"level{i}": i for i in range(1, 11)}
        
        return [
            task_type_encoding.get(self.task_type, 0),
            level_encoding.get(self.test_level, 0),
            self.estimated_duration,
            self.resource_requirements.get("cpu_cores", 1),
            self.resource_requirements.get("memory_gb", 2),
            self.priority,
            len(self.dependencies)
        ]

class NodePerformancePredictor:
    """节点性能预测器"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'cpu_usage', 'memory_usage', 'disk_io', 'network_io',
            'task_completion_rate', 'avg_execution_time', 'error_rate', 'concurrent_tasks'
        ]
        
    def train(self, historical_data: List[NodePerformanceMetrics], target_metrics: List[float]):
        """训练预测模型"""
        if len(historical_data) < 10:
            logger.warning("历史数据不足，无法训练预测模型")
            return False
        
        try:
            # 准备训练数据
            X = np.array([metrics.to_feature_vector() for metrics in historical_data])
            y = np.array(target_metrics)
            
            # 数据标准化
            X_scaled = self.scaler.fit_transform(X)
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            self.model.fit(X_train, y_train)
            
            # 评估模型
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            
            logger.info(f"节点性能预测模型训练完成，MSE: {mse:.4f}")
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"节点性能预测模型训练失败: {e}")
            return False
    
    def predict_performance(self, current_metrics: NodePerformanceMetrics) -> float:
        """预测节点性能"""
        if not self.is_trained:
            # 如果模型未训练，返回基于当前指标的简单评分
            return self._simple_performance_score(current_metrics)
        
        try:
            X = np.array([current_metrics.to_feature_vector()])
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)[0]
            return max(0, min(100, prediction))  # 限制在0-100范围内
            
        except Exception as e:
            logger.error(f"性能预测失败: {e}")
            return self._simple_performance_score(current_metrics)
    
    def _simple_performance_score(self, metrics: NodePerformanceMetrics) -> float:
        """简单性能评分算法"""
        score = 100.0
        
        # CPU使用率影响 (使用率越低越好)
        score -= metrics.cpu_usage * 0.5
        
        # 内存使用率影响
        score -= metrics.memory_usage * 0.3
        
        # 错误率影响
        score -= metrics.error_rate * 20
        
        # 任务完成率影响 (完成率越高越好)
        score += (metrics.task_completion_rate - 0.5) * 20
        
        # 并发任务负载影响
        if metrics.concurrent_tasks > 5:
            score -= (metrics.concurrent_tasks - 5) * 5
        
        return max(0, min(100, score))

class TaskNodeMatcher:
    """任务节点匹配器"""
    
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, training_data: List[Tuple[TaskCharacteristics, NodePerformanceMetrics, bool]]):
        """训练匹配模型"""
        if len(training_data) < 20:
            logger.warning("训练数据不足，无法训练匹配模型")
            return False
        
        try:
            # 准备训练数据
            X = []
            y = []
            
            for task_char, node_metrics, success in training_data:
                # 组合任务特征和节点特征
                features = task_char.to_feature_vector() + node_metrics.to_feature_vector()
                X.append(features)
                y.append(1 if success else 0)
            
            X = np.array(X)
            y = np.array(y)
            
            # 数据标准化
            X_scaled = self.scaler.fit_transform(X)
            
            # 分割训练和测试数据
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # 训练模型
            self.model.fit(X_train, y_train)
            
            # 评估模型
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"任务节点匹配模型训练完成，准确率: {accuracy:.4f}")
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"任务节点匹配模型训练失败: {e}")
            return False
    
    def predict_match_probability(self, task: TaskCharacteristics, node: NodePerformanceMetrics) -> float:
        """预测任务节点匹配概率"""
        if not self.is_trained:
            return self._simple_match_score(task, node)
        
        try:
            features = task.to_feature_vector() + node.to_feature_vector()
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # 获取匹配概率
            probabilities = self.model.predict_proba(X_scaled)[0]
            return probabilities[1] if len(probabilities) > 1 else 0.5
            
        except Exception as e:
            logger.error(f"匹配概率预测失败: {e}")
            return self._simple_match_score(task, node)
    
    def _simple_match_score(self, task: TaskCharacteristics, node: NodePerformanceMetrics) -> float:
        """简单匹配评分算法"""
        score = 0.5  # 基础分数
        
        # 资源匹配度
        required_cpu = task.resource_requirements.get("cpu_cores", 1)
        required_memory = task.resource_requirements.get("memory_gb", 2)
        
        # CPU匹配度 (假设节点有足够CPU)
        if node.cpu_usage < 70:  # CPU使用率低于70%
            score += 0.2
        elif node.cpu_usage > 90:
            score -= 0.3
        
        # 内存匹配度
        if node.memory_usage < 60:  # 内存使用率低于60%
            score += 0.2
        elif node.memory_usage > 85:
            score -= 0.3
        
        # 并发任务负载
        if node.concurrent_tasks < 3:
            score += 0.1
        elif node.concurrent_tasks > 8:
            score -= 0.2
        
        # 历史成功率
        if node.task_completion_rate > 0.9:
            score += 0.2
        elif node.task_completion_rate < 0.7:
            score -= 0.2
        
        return max(0, min(1, score))

class SmartSchedulingEngine:
    """智能调度引擎"""
    
    def __init__(self):
        self.performance_predictor = NodePerformancePredictor()
        self.task_matcher = TaskNodeMatcher()
        self.historical_data = defaultdict(deque)
        self.training_data = deque(maxlen=1000)
        self.last_training_time = datetime.now()
        self.training_interval = timedelta(hours=6)  # 每6小时重新训练
        self._lock = threading.RLock()
        
    async def initialize(self):
        """初始化调度引擎"""
        logger.info("🧠 初始化智能调度引擎...")
        
        # 加载历史数据
        await self._load_historical_data()
        
        # 初始训练
        await self._train_models()
        
        # 启动定期重训练
        asyncio.create_task(self._periodic_retraining())
        
        logger.info("✅ 智能调度引擎初始化完成")
    
    async def select_optimal_node(
        self, 
        task: TaskCharacteristics, 
        available_nodes: List[NodePerformanceMetrics]
    ) -> Optional[str]:
        """选择最优节点"""
        if not available_nodes:
            return None
        
        try:
            # 计算每个节点的综合评分
            node_scores = []
            
            for node in available_nodes:
                # 性能预测评分
                performance_score = self.performance_predictor.predict_performance(node)
                
                # 匹配概率评分
                match_probability = self.task_matcher.predict_match_probability(task, node)
                
                # 综合评分 (性能占60%，匹配度占40%)
                combined_score = performance_score * 0.6 + match_probability * 100 * 0.4
                
                node_scores.append((node.node_id, combined_score))
            
            # 按评分排序，选择最高分的节点
            node_scores.sort(key=lambda x: x[1], reverse=True)
            
            best_node_id = node_scores[0][0]
            best_score = node_scores[0][1]
            
            logger.info(f"🎯 智能调度选择节点: {best_node_id} (评分: {best_score:.2f})")
            return best_node_id
            
        except Exception as e:
            logger.error(f"❌ 智能节点选择失败: {e}")
            # 降级到简单选择策略
            return available_nodes[0].node_id
    
    async def record_execution_result(
        self, 
        task: TaskCharacteristics, 
        node: NodePerformanceMetrics, 
        success: bool,
        execution_time: float
    ):
        """记录执行结果用于学习"""
        with self._lock:
            # 记录训练数据
            self.training_data.append((task, node, success))
            
            # 记录性能数据
            self.historical_data[node.node_id].append({
                'timestamp': datetime.now(),
                'metrics': node,
                'execution_time': execution_time,
                'success': success
            })
            
            # 保持最近1000条记录
            if len(self.historical_data[node.node_id]) > 1000:
                self.historical_data[node.node_id].popleft()
    
    async def get_scheduling_insights(self) -> Dict[str, Any]:
        """获取调度洞察"""
        insights = {
            'total_training_samples': len(self.training_data),
            'models_trained': {
                'performance_predictor': self.performance_predictor.is_trained,
                'task_matcher': self.task_matcher.is_trained
            },
            'last_training_time': self.last_training_time.isoformat(),
            'node_performance_history': {}
        }
        
        # 节点性能统计
        for node_id, history in self.historical_data.items():
            if history:
                recent_data = list(history)[-10:]  # 最近10条记录
                success_rate = sum(1 for d in recent_data if d['success']) / len(recent_data)
                avg_execution_time = sum(d['execution_time'] for d in recent_data) / len(recent_data)
                
                insights['node_performance_history'][node_id] = {
                    'recent_success_rate': success_rate,
                    'avg_execution_time': avg_execution_time,
                    'total_samples': len(history)
                }
        
        return insights
    
    async def _load_historical_data(self):
        """加载历史数据"""
        # 这里可以从数据库加载历史数据
        # 目前使用模拟数据
        logger.info("📊 加载历史调度数据...")
        
        # 生成一些模拟的历史数据用于初始训练
        await self._generate_mock_training_data()
    
    async def _generate_mock_training_data(self):
        """生成模拟训练数据"""
        import random
        
        task_types = ["unit_test", "integration_test", "ui_test", "performance_test"]
        test_levels = [f"level{i}" for i in range(1, 11)]
        
        for _ in range(100):
            # 模拟任务特征
            task = TaskCharacteristics(
                task_type=random.choice(task_types),
                test_level=random.choice(test_levels),
                estimated_duration=random.uniform(30, 600),
                resource_requirements={
                    "cpu_cores": random.randint(1, 8),
                    "memory_gb": random.randint(2, 16)
                },
                priority=random.randint(1, 5),
                dependencies=[]
            )
            
            # 模拟节点指标
            node = NodePerformanceMetrics(
                node_id=f"node_{random.randint(1, 10)}",
                timestamp=datetime.now(),
                cpu_usage=random.uniform(10, 90),
                memory_usage=random.uniform(20, 80),
                disk_io=random.uniform(0, 100),
                network_io=random.uniform(0, 100),
                task_completion_rate=random.uniform(0.7, 1.0),
                average_execution_time=random.uniform(60, 300),
                error_rate=random.uniform(0, 0.1),
                concurrent_tasks=random.randint(0, 10)
            )
            
            # 模拟执行结果 (性能好的节点成功率更高)
            success_probability = (100 - node.cpu_usage) / 100 * node.task_completion_rate
            success = random.random() < success_probability
            
            self.training_data.append((task, node, success))
    
    async def _train_models(self):
        """训练机器学习模型"""
        if len(self.training_data) < 20:
            logger.warning("训练数据不足，跳过模型训练")
            return
        
        logger.info("🤖 开始训练智能调度模型...")
        
        try:
            # 准备性能预测训练数据
            performance_data = []
            performance_targets = []
            
            # 准备匹配模型训练数据
            matching_data = list(self.training_data)
            
            for task, node, success in self.training_data:
                performance_data.append(node)
                # 目标是基于成功率和执行时间的综合性能评分
                performance_score = 100 * node.task_completion_rate - node.average_execution_time / 10
                performance_targets.append(performance_score)
            
            # 训练性能预测模型
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.performance_predictor.train, 
                performance_data, 
                performance_targets
            )
            
            # 训练任务匹配模型
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.task_matcher.train,
                matching_data
            )
            
            self.last_training_time = datetime.now()
            logger.info("✅ 智能调度模型训练完成")
            
        except Exception as e:
            logger.error(f"❌ 模型训练失败: {e}")
    
    async def _periodic_retraining(self):
        """定期重新训练模型"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时检查一次
                
                if datetime.now() - self.last_training_time > self.training_interval:
                    if len(self.training_data) >= 50:  # 有足够新数据时才重新训练
                        await self._train_models()
                
            except Exception as e:
                logger.error(f"❌ 定期重训练失败: {e}")
                await asyncio.sleep(1800)  # 出错时等待30分钟再试

# 导出主要类
__all__ = [
    'SmartSchedulingEngine',
    'NodePerformanceMetrics', 
    'TaskCharacteristics',
    'NodePerformancePredictor',
    'TaskNodeMatcher'
]

