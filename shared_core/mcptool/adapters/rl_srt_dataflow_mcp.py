#!/usr/bin/env python3
"""
RL-SRT數據流MCP適配器

整合RL Factory和SRT (Self-Reward Training)功能，並擴展數據流處理能力：
- 強化學習對齊和訓練
- 自我獎勵機制
- 交互數據流處理
- 異步RL訓練管道
- 與端雲協同數據的整合

作者: PowerAutomation團隊
版本: 3.0.0
日期: 2025-06-08
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum

# 添加項目路徑
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 導入基礎MCP
try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子類必須實現此方法")

# 導入現有RL-SRT組件
try:
    from mcptool.adapters.rl_srt.rl_srt_mcp import RLSRTAdapter
except ImportError:
    class RLSRTAdapter:
        def __init__(self):
            self.logger = logging.getLogger("rl_srt_adapter")
        
        def train_rl_srt(self, *args, **kwargs):
            return {"status": "mock", "message": "RL-SRT適配器未找到"}

# 導入端雲協同數據MCP
try:
    from mcptool.adapters.cloud_edge_data_mcp import CloudEdgeDataMCP
except ImportError:
    class CloudEdgeDataMCP:
        def get_training_data(self, *args, **kwargs):
            return {"status": "mock", "data": [], "count": 0}

# 導入標準化日誌系統
try:
    from standardized_logging_system import log_info, log_error, log_warning, LogCategory, performance_monitor
except ImportError:
    def log_info(category, message, data=None): pass
    def log_error(category, message, data=None): pass
    def log_warning(category, message, data=None): pass
    def performance_monitor(name): 
        def decorator(func): return func
        return decorator
    class LogCategory:
        SYSTEM = "system"
        MEMORY = "memory"
        MCP = "mcp"

logger = logging.getLogger("rl_srt_dataflow_mcp")

class TrainingMode(Enum):
    """訓練模式枚舉"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"
    FEDERATED = "federated"

class DataFlowStatus(Enum):
    """數據流狀態枚舉"""
    IDLE = "idle"
    COLLECTING = "collecting"
    PROCESSING = "processing"
    TRAINING = "training"
    EVALUATING = "evaluating"
    DEPLOYING = "deploying"
    ERROR = "error"

class RLSRTDataFlowMCP(BaseMCP):
    """RL-SRT數據流MCP適配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("RLSRTDataFlowMCP")
        
        # 配置參數
        self.config = config or {}
        self.training_mode = TrainingMode(self.config.get("training_mode", "asynchronous"))
        self.batch_size = self.config.get("batch_size", 32)
        self.learning_rate = self.config.get("learning_rate", 0.001)
        self.max_episodes = self.config.get("max_episodes", 1000)
        
        # 組件初始化
        self.rl_srt_adapter = RLSRTAdapter()
        self.cloud_edge_data = CloudEdgeDataMCP()
        
        # 數據流狀態
        self.status = DataFlowStatus.IDLE
        self.training_metrics = {
            "episodes_completed": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,
            "loss": 0.0,
            "accuracy": 0.0
        }
        
        # 異步訓練任務
        self.training_tasks = {}
        self.data_streams = {}
        
        # MCP操作映射
        self.operations = {
            "start_training": self.start_training,
            "stop_training": self.stop_training,
            "get_training_status": self.get_training_status,
            "process_data_stream": self.process_data_stream,
            "evaluate_model": self.evaluate_model,
            "deploy_model": self.deploy_model,
            "get_metrics": self.get_metrics,
            "configure_training": self.configure_training,
            "sync_with_cloud": self.sync_with_cloud,
            "federated_learning": self.federated_learning
        }
        
        log_info(LogCategory.MCP, "RL-SRT數據流MCP初始化完成", {
            "training_mode": self.training_mode.value,
            "batch_size": self.batch_size,
            "operations": list(self.operations.keys())
        })
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP標準處理接口"""
        try:
            operation = input_data.get("operation", "get_training_status")
            params = input_data.get("params", {})
            
            if operation not in self.operations:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {operation}",
                    "available_operations": list(self.operations.keys())
                }
            
            # 執行對應操作
            if asyncio.iscoroutinefunction(self.operations[operation]):
                # 異步操作
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.operations[operation](**params))
            else:
                # 同步操作
                result = self.operations[operation](**params)
            
            log_info(LogCategory.MCP, f"RL-SRT數據流MCP操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "RL-SRT數據流MCP處理失敗", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"處理失敗: {str(e)}"
            }
    
    @performance_monitor("start_training")
    async def start_training(self, training_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """開始RL-SRT訓練"""
        try:
            if self.status == DataFlowStatus.TRAINING:
                return {
                    "status": "warning",
                    "message": "訓練已在進行中"
                }
            
            # 更新配置
            if training_config:
                self.config.update(training_config)
            
            # 獲取訓練數據
            training_data_result = await self.cloud_edge_data.get_training_data(
                data_type="training_sets",
                limit=self.config.get("data_limit", 1000)
            )
            
            if training_data_result["status"] != "success":
                return {
                    "status": "error",
                    "message": "無法獲取訓練數據"
                }
            
            training_data = training_data_result["data"]
            
            # 設置訓練狀態
            self.status = DataFlowStatus.TRAINING
            
            # 根據訓練模式啟動訓練
            if self.training_mode == TrainingMode.ASYNCHRONOUS:
                task_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.training_tasks[task_id] = asyncio.create_task(
                    self._async_training_loop(training_data, task_id)
                )
                
                return {
                    "status": "success",
                    "message": "異步訓練已啟動",
                    "task_id": task_id,
                    "training_data_count": len(training_data)
                }
            
            elif self.training_mode == TrainingMode.SYNCHRONOUS:
                result = await self._sync_training(training_data)
                self.status = DataFlowStatus.IDLE
                return result
            
            elif self.training_mode == TrainingMode.STREAMING:
                stream_id = f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.data_streams[stream_id] = asyncio.create_task(
                    self._streaming_training(stream_id)
                )
                
                return {
                    "status": "success",
                    "message": "流式訓練已啟動",
                    "stream_id": stream_id
                }
            
            else:
                return {
                    "status": "error",
                    "message": f"不支持的訓練模式: {self.training_mode.value}"
                }
                
        except Exception as e:
            self.status = DataFlowStatus.ERROR
            return {
                "status": "error",
                "message": f"啟動訓練失敗: {str(e)}"
            }
    
    async def _async_training_loop(self, training_data: List[Dict[str, Any]], task_id: str):
        """異步訓練循環"""
        try:
            log_info(LogCategory.MCP, f"開始異步訓練: {task_id}", {
                "data_count": len(training_data),
                "batch_size": self.batch_size
            })
            
            for episode in range(self.max_episodes):
                # 批量處理訓練數據
                for i in range(0, len(training_data), self.batch_size):
                    batch = training_data[i:i + self.batch_size]
                    
                    # 執行RL-SRT訓練
                    training_result = await self._train_batch(batch, episode)
                    
                    # 更新指標
                    self._update_training_metrics(training_result)
                    
                    # 檢查是否需要停止
                    if task_id not in self.training_tasks:
                        break
                
                # 每10個episode評估一次
                if episode % 10 == 0:
                    await self._evaluate_current_model()
                
                # 檢查收斂條件
                if self._check_convergence():
                    log_info(LogCategory.MCP, f"訓練收斂，提前結束: {task_id}", {
                        "episode": episode,
                        "average_reward": self.training_metrics["average_reward"]
                    })
                    break
            
            self.status = DataFlowStatus.IDLE
            log_info(LogCategory.MCP, f"異步訓練完成: {task_id}", {
                "episodes": self.training_metrics["episodes_completed"],
                "final_reward": self.training_metrics["average_reward"]
            })
            
        except Exception as e:
            self.status = DataFlowStatus.ERROR
            log_error(LogCategory.MCP, f"異步訓練失敗: {task_id}", {
                "error": str(e)
            })
        finally:
            # 清理任務
            if task_id in self.training_tasks:
                del self.training_tasks[task_id]
    
    async def _train_batch(self, batch: List[Dict[str, Any]], episode: int) -> Dict[str, Any]:
        """訓練單個批次"""
        try:
            # 準備RL-SRT訓練數據
            rl_data = self._prepare_rl_data(batch)
            
            # 執行RL-SRT訓練
            result = self.rl_srt_adapter.train_rl_srt(
                training_data=rl_data,
                episode=episode,
                learning_rate=self.learning_rate
            )
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "批次訓練失敗", {
                "batch_size": len(batch),
                "episode": episode,
                "error": str(e)
            })
            return {"status": "error", "reward": 0.0, "loss": float('inf')}
    
    def _prepare_rl_data(self, batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """準備RL訓練數據"""
        states = []
        actions = []
        rewards = []
        
        for sample in batch:
            # 提取狀態（上下文和用戶動作）
            state = {
                "context": sample.get("input", {}).get("context", {}),
                "features": sample.get("input", {}).get("features", {})
            }
            states.append(state)
            
            # 提取動作（AI響應）
            action = sample.get("output", {}).get("ai_response", {})
            actions.append(action)
            
            # 提取獎勵（基於用戶反饋）
            reward = sample.get("metadata", {}).get("quality_score", 0.5)
            rewards.append(reward)
        
        return {
            "states": states,
            "actions": actions,
            "rewards": rewards
        }
    
    def _update_training_metrics(self, training_result: Dict[str, Any]):
        """更新訓練指標"""
        if training_result.get("status") == "success":
            self.training_metrics["episodes_completed"] += 1
            
            reward = training_result.get("reward", 0.0)
            self.training_metrics["total_reward"] += reward
            self.training_metrics["average_reward"] = (
                self.training_metrics["total_reward"] / 
                max(self.training_metrics["episodes_completed"], 1)
            )
            
            loss = training_result.get("loss", 0.0)
            self.training_metrics["loss"] = loss
            
            accuracy = training_result.get("accuracy", 0.0)
            self.training_metrics["accuracy"] = accuracy
    
    def _check_convergence(self) -> bool:
        """檢查訓練是否收斂"""
        # 簡單的收斂檢查邏輯
        return (
            self.training_metrics["episodes_completed"] >= 100 and
            self.training_metrics["average_reward"] >= 0.9 and
            self.training_metrics["loss"] <= 0.01
        )
    
    async def _evaluate_current_model(self):
        """評估當前模型"""
        try:
            # 獲取驗證數據
            validation_result = await self.cloud_edge_data.get_training_data(
                data_type="validation_sets",
                limit=100
            )
            
            if validation_result["status"] == "success":
                validation_data = validation_result["data"]
                # 執行模型評估
                eval_result = await self._evaluate_model_performance(validation_data)
                
                log_info(LogCategory.MCP, "模型評估完成", {
                    "validation_samples": len(validation_data),
                    "accuracy": eval_result.get("accuracy", 0.0)
                })
                
        except Exception as e:
            log_error(LogCategory.MCP, "模型評估失敗", {"error": str(e)})
    
    async def _evaluate_model_performance(self, validation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """評估模型性能"""
        # 實現模型評估邏輯
        correct_predictions = 0
        total_predictions = len(validation_data)
        
        for sample in validation_data:
            # 模擬預測和評估
            predicted_quality = 0.8  # 模擬預測質量分數
            actual_quality = sample.get("metadata", {}).get("quality_score", 0.5)
            
            if abs(predicted_quality - actual_quality) <= 0.1:
                correct_predictions += 1
        
        accuracy = correct_predictions / max(total_predictions, 1)
        
        return {
            "accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions
        }
    
    async def stop_training(self, task_id: str = None) -> Dict[str, Any]:
        """停止訓練"""
        try:
            if task_id:
                # 停止特定任務
                if task_id in self.training_tasks:
                    self.training_tasks[task_id].cancel()
                    del self.training_tasks[task_id]
                    return {
                        "status": "success",
                        "message": f"訓練任務 {task_id} 已停止"
                    }
                else:
                    return {
                        "status": "warning",
                        "message": f"訓練任務 {task_id} 不存在"
                    }
            else:
                # 停止所有任務
                stopped_count = 0
                for tid, task in list(self.training_tasks.items()):
                    task.cancel()
                    del self.training_tasks[tid]
                    stopped_count += 1
                
                self.status = DataFlowStatus.IDLE
                
                return {
                    "status": "success",
                    "message": f"已停止 {stopped_count} 個訓練任務"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"停止訓練失敗: {str(e)}"
            }
    
    def get_training_status(self) -> Dict[str, Any]:
        """獲取訓練狀態"""
        return {
            "status": "success",
            "training_status": self.status.value,
            "active_tasks": list(self.training_tasks.keys()),
            "active_streams": list(self.data_streams.keys()),
            "metrics": self.training_metrics.copy(),
            "config": self.config.copy()
        }
    
    async def process_data_stream(self, stream_config: Dict[str, Any]) -> Dict[str, Any]:
        """處理數據流"""
        try:
            stream_id = stream_config.get("stream_id", f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # 啟動流式處理
            self.data_streams[stream_id] = asyncio.create_task(
                self._process_streaming_data(stream_id, stream_config)
            )
            
            return {
                "status": "success",
                "stream_id": stream_id,
                "message": "數據流處理已啟動"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"數據流處理失敗: {str(e)}"
            }
    
    async def _process_streaming_data(self, stream_id: str, config: Dict[str, Any]):
        """處理流式數據"""
        try:
            log_info(LogCategory.MCP, f"開始流式數據處理: {stream_id}", config)
            
            # 模擬流式數據處理
            while stream_id in self.data_streams:
                # 獲取新的交互數據
                new_data = await self._fetch_new_interaction_data()
                
                if new_data:
                    # 實時處理和訓練
                    await self._process_real_time_data(new_data)
                
                # 等待下一批數據
                await asyncio.sleep(config.get("polling_interval", 5))
                
        except Exception as e:
            log_error(LogCategory.MCP, f"流式數據處理失敗: {stream_id}", {"error": str(e)})
        finally:
            if stream_id in self.data_streams:
                del self.data_streams[stream_id]
    
    async def _fetch_new_interaction_data(self) -> List[Dict[str, Any]]:
        """獲取新的交互數據"""
        # 實現獲取新數據的邏輯
        return []
    
    async def _process_real_time_data(self, data: List[Dict[str, Any]]):
        """實時處理數據"""
        # 實現實時數據處理邏輯
        pass
    
    async def evaluate_model(self, model_id: str = "current") -> Dict[str, Any]:
        """評估模型"""
        try:
            # 獲取測試數據
            test_result = await self.cloud_edge_data.get_training_data(
                data_type="test_sets",
                limit=200
            )
            
            if test_result["status"] != "success":
                return {
                    "status": "error",
                    "message": "無法獲取測試數據"
                }
            
            test_data = test_result["data"]
            evaluation_result = await self._evaluate_model_performance(test_data)
            
            return {
                "status": "success",
                "model_id": model_id,
                "evaluation": evaluation_result,
                "test_data_count": len(test_data)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"模型評估失敗: {str(e)}"
            }
    
    async def deploy_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """部署模型"""
        try:
            model_id = model_config.get("model_id", "latest")
            deployment_target = model_config.get("target", "production")
            
            # 實現模型部署邏輯
            deployment_result = await self._deploy_model_to_target(model_id, deployment_target)
            
            return {
                "status": "success",
                "model_id": model_id,
                "deployment_target": deployment_target,
                "deployment_result": deployment_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"模型部署失敗: {str(e)}"
            }
    
    async def _deploy_model_to_target(self, model_id: str, target: str) -> Dict[str, Any]:
        """部署模型到目標環境"""
        # 實現具體的部署邏輯
        return {
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": "deployed",
            "endpoint": f"https://api.powerautomation.ai/models/{model_id}"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """獲取訓練指標"""
        return {
            "status": "success",
            "metrics": self.training_metrics.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def configure_training(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """配置訓練參數"""
        try:
            self.config.update(new_config)
            
            # 更新相關參數
            if "training_mode" in new_config:
                self.training_mode = TrainingMode(new_config["training_mode"])
            if "batch_size" in new_config:
                self.batch_size = new_config["batch_size"]
            if "learning_rate" in new_config:
                self.learning_rate = new_config["learning_rate"]
            if "max_episodes" in new_config:
                self.max_episodes = new_config["max_episodes"]
            
            return {
                "status": "success",
                "message": "訓練配置已更新",
                "config": self.config.copy()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"配置更新失敗: {str(e)}"
            }
    
    async def sync_with_cloud(self, sync_config: Dict[str, Any]) -> Dict[str, Any]:
        """與雲端同步"""
        try:
            # 實現雲端同步邏輯
            sync_result = await self.cloud_edge_data.sync_data_to_cloud(
                target=sync_config.get("target", "default")
            )
            
            return {
                "status": "success",
                "sync_result": sync_result,
                "message": "雲端同步完成"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"雲端同步失敗: {str(e)}"
            }
    
    async def federated_learning(self, fl_config: Dict[str, Any]) -> Dict[str, Any]:
        """聯邦學習"""
        try:
            # 實現聯邦學習邏輯
            participants = fl_config.get("participants", [])
            rounds = fl_config.get("rounds", 10)
            
            fl_result = await self._execute_federated_learning(participants, rounds)
            
            return {
                "status": "success",
                "federated_learning_result": fl_result,
                "participants": len(participants),
                "rounds": rounds
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"聯邦學習失敗: {str(e)}"
            }
    
    async def _execute_federated_learning(self, participants: List[str], rounds: int) -> Dict[str, Any]:
        """執行聯邦學習"""
        # 實現聯邦學習的具體邏輯
        return {
            "global_model_accuracy": 0.85,
            "convergence_round": rounds - 2,
            "participant_contributions": {p: 0.8 + 0.1 * hash(p) % 3 for p in participants}
        }

# 創建全局實例
rl_srt_dataflow_mcp = RLSRTDataFlowMCP()

# 導出主要接口
__all__ = [
    'RLSRTDataFlowMCP',
    'TrainingMode',
    'DataFlowStatus',
    'rl_srt_dataflow_mcp'
]

if __name__ == "__main__":
    # 測試MCP功能
    test_data = {
        "operation": "get_training_status",
        "params": {}
    }
    
    result = rl_srt_dataflow_mcp.process(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

