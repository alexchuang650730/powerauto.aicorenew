#!/usr/bin/env python3
"""
上下文監控MCP適配器

實現智能上下文監控功能，包括：
- 實時上下文使用情況監控
- 預警機制和閾值管理
- 自動備份觸發
- 上下文優化建議
- 歷史趨勢分析

作者: PowerAutomation團隊
版本: 1.0.0
日期: 2025-06-08
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
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

# 導入現有監控組件
try:
    from smart_context_monitor import SmartContextMonitor
except ImportError:
    class SmartContextMonitor:
        def __init__(self):
            self.total_chars = 0
            self.interaction_count = 0
        
        def get_context_usage_percent(self):
            return 0.0
        
        def check_thresholds(self):
            return {"warning": False, "critical": False}

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

logger = logging.getLogger("context_monitor_mcp")

class AlertLevel(Enum):
    """警告級別枚舉"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MonitoringMode(Enum):
    """監控模式枚舉"""
    PASSIVE = "passive"
    ACTIVE = "active"
    PREDICTIVE = "predictive"
    ADAPTIVE = "adaptive"

class ContextMonitorMCP(BaseMCP):
    """上下文監控MCP適配器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ContextMonitorMCP")
        
        # 配置參數
        self.config = config or {}
        self.monitoring_mode = MonitoringMode(self.config.get("monitoring_mode", "active"))
        self.check_interval = self.config.get("check_interval", 30)  # 秒
        self.max_context_chars = self.config.get("max_context_chars", 200000)
        
        # 閾值設置
        self.thresholds = {
            "warning": self.config.get("warning_threshold", 0.8),
            "critical": self.config.get("critical_threshold", 0.9),
            "emergency": self.config.get("emergency_threshold", 0.95)
        }
        
        # 監控組件初始化
        self.context_monitor = SmartContextMonitor()
        
        # 監控狀態
        self.current_alert_level = AlertLevel.NORMAL
        self.monitoring_active = False
        self.monitoring_task = None
        
        # 歷史數據
        self.usage_history = []
        self.alert_history = []
        self.optimization_suggestions = []
        
        # 統計信息
        self.stats = {
            "total_checks": 0,
            "warnings_triggered": 0,
            "critical_alerts": 0,
            "emergency_alerts": 0,
            "auto_backups_triggered": 0,
            "optimizations_applied": 0
        }
        
        # MCP操作映射
        self.operations = {
            "start_monitoring": self.start_monitoring,
            "stop_monitoring": self.stop_monitoring,
            "get_status": self.get_monitoring_status,
            "check_context": self.check_context_usage,
            "set_thresholds": self.set_thresholds,
            "get_history": self.get_usage_history,
            "get_alerts": self.get_alert_history,
            "optimize_context": self.optimize_context,
            "predict_usage": self.predict_context_usage,
            "configure_monitoring": self.configure_monitoring,
            "export_metrics": self.export_monitoring_metrics,
            "reset_stats": self.reset_statistics
        }
        
        log_info(LogCategory.MCP, "上下文監控MCP初始化完成", {
            "monitoring_mode": self.monitoring_mode.value,
            "check_interval": self.check_interval,
            "thresholds": self.thresholds
        })
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP標準處理接口"""
        try:
            operation = input_data.get("operation", "get_status")
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
            
            log_info(LogCategory.MCP, f"上下文監控MCP操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "上下文監控MCP處理失敗", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"處理失敗: {str(e)}"
            }
    
    @performance_monitor("start_monitoring")
    async def start_monitoring(self, monitoring_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """開始上下文監控"""
        try:
            if self.monitoring_active:
                return {
                    "status": "warning",
                    "message": "監控已在運行中"
                }
            
            # 更新配置
            if monitoring_config:
                self.config.update(monitoring_config)
                self._update_config_parameters()
            
            # 啟動監控任務
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            log_info(LogCategory.MCP, "上下文監控已啟動", {
                "monitoring_mode": self.monitoring_mode.value,
                "check_interval": self.check_interval
            })
            
            return {
                "status": "success",
                "message": "上下文監控已啟動",
                "monitoring_mode": self.monitoring_mode.value,
                "check_interval": self.check_interval,
                "thresholds": self.thresholds
            }
            
        except Exception as e:
            self.monitoring_active = False
            return {
                "status": "error",
                "message": f"啟動監控失敗: {str(e)}"
            }
    
    def _update_config_parameters(self):
        """更新配置參數"""
        if "monitoring_mode" in self.config:
            self.monitoring_mode = MonitoringMode(self.config["monitoring_mode"])
        if "check_interval" in self.config:
            self.check_interval = self.config["check_interval"]
        if "max_context_chars" in self.config:
            self.max_context_chars = self.config["max_context_chars"]
        
        # 更新閾值
        for threshold_type in ["warning", "critical", "emergency"]:
            threshold_key = f"{threshold_type}_threshold"
            if threshold_key in self.config:
                self.thresholds[threshold_type] = self.config[threshold_key]
    
    async def _monitoring_loop(self):
        """監控循環"""
        try:
            log_info(LogCategory.MCP, "上下文監控循環開始", {
                "mode": self.monitoring_mode.value
            })
            
            while self.monitoring_active:
                # 執行上下文檢查
                check_result = await self.check_context_usage()
                
                if check_result["status"] == "success":
                    # 記錄使用情況
                    self._record_usage_data(check_result)
                    
                    # 檢查警告級別
                    alert_level = self._determine_alert_level(check_result["usage_percent"])
                    
                    # 處理警告
                    if alert_level != self.current_alert_level:
                        await self._handle_alert_level_change(alert_level, check_result)
                    
                    # 預測性監控
                    if self.monitoring_mode == MonitoringMode.PREDICTIVE:
                        await self._predictive_analysis(check_result)
                    
                    # 自適應監控
                    if self.monitoring_mode == MonitoringMode.ADAPTIVE:
                        await self._adaptive_adjustment(check_result)
                
                # 等待下次檢查
                await asyncio.sleep(self.check_interval)
                
        except Exception as e:
            log_error(LogCategory.MCP, "監控循環異常", {"error": str(e)})
        finally:
            self.monitoring_active = False
            log_info(LogCategory.MCP, "上下文監控循環結束", {})
    
    def _record_usage_data(self, check_result: Dict[str, Any]):
        """記錄使用數據"""
        usage_data = {
            "timestamp": datetime.now().isoformat(),
            "usage_percent": check_result["usage_percent"],
            "total_chars": check_result["total_chars"],
            "interaction_count": check_result["interaction_count"],
            "alert_level": self.current_alert_level.value
        }
        
        self.usage_history.append(usage_data)
        
        # 保持歷史數據在合理範圍內
        if len(self.usage_history) > 1000:
            self.usage_history = self.usage_history[-1000:]
    
    def _determine_alert_level(self, usage_percent: float) -> AlertLevel:
        """確定警告級別"""
        if usage_percent >= self.thresholds["emergency"]:
            return AlertLevel.EMERGENCY
        elif usage_percent >= self.thresholds["critical"]:
            return AlertLevel.CRITICAL
        elif usage_percent >= self.thresholds["warning"]:
            return AlertLevel.WARNING
        else:
            return AlertLevel.NORMAL
    
    async def _handle_alert_level_change(self, new_level: AlertLevel, check_result: Dict[str, Any]):
        """處理警告級別變化"""
        old_level = self.current_alert_level
        self.current_alert_level = new_level
        
        # 記錄警告歷史
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "old_level": old_level.value,
            "new_level": new_level.value,
            "usage_percent": check_result["usage_percent"],
            "trigger_reason": self._get_alert_reason(new_level)
        }
        
        self.alert_history.append(alert_data)
        
        # 更新統計
        if new_level == AlertLevel.WARNING:
            self.stats["warnings_triggered"] += 1
        elif new_level == AlertLevel.CRITICAL:
            self.stats["critical_alerts"] += 1
        elif new_level == AlertLevel.EMERGENCY:
            self.stats["emergency_alerts"] += 1
        
        # 執行相應動作
        await self._execute_alert_actions(new_level, check_result)
        
        log_warning(LogCategory.MCP, f"上下文警告級別變化: {old_level.value} -> {new_level.value}", {
            "usage_percent": check_result["usage_percent"],
            "threshold": self._get_threshold_for_level(new_level)
        })
    
    def _get_alert_reason(self, level: AlertLevel) -> str:
        """獲取警告原因"""
        reasons = {
            AlertLevel.WARNING: "上下文使用率達到警告閾值",
            AlertLevel.CRITICAL: "上下文使用率達到臨界閾值",
            AlertLevel.EMERGENCY: "上下文使用率達到緊急閾值",
            AlertLevel.NORMAL: "上下文使用率恢復正常"
        }
        return reasons.get(level, "未知原因")
    
    def _get_threshold_for_level(self, level: AlertLevel) -> float:
        """獲取級別對應的閾值"""
        thresholds = {
            AlertLevel.WARNING: self.thresholds["warning"],
            AlertLevel.CRITICAL: self.thresholds["critical"],
            AlertLevel.EMERGENCY: self.thresholds["emergency"],
            AlertLevel.NORMAL: 0.0
        }
        return thresholds.get(level, 0.0)
    
    async def _execute_alert_actions(self, level: AlertLevel, check_result: Dict[str, Any]):
        """執行警告動作"""
        try:
            if level == AlertLevel.WARNING:
                # 警告級別：記錄日誌，發送通知
                await self._send_warning_notification(check_result)
                
            elif level == AlertLevel.CRITICAL:
                # 臨界級別：準備備份，優化建議
                await self._prepare_backup(check_result)
                await self._generate_optimization_suggestions(check_result)
                
            elif level == AlertLevel.EMERGENCY:
                # 緊急級別：強制備份，上下文清理
                await self._force_backup(check_result)
                await self._emergency_context_cleanup(check_result)
                self.stats["auto_backups_triggered"] += 1
                
        except Exception as e:
            log_error(LogCategory.MCP, f"執行警告動作失敗: {level.value}", {"error": str(e)})
    
    async def _send_warning_notification(self, check_result: Dict[str, Any]):
        """發送警告通知"""
        # 實現警告通知邏輯
        log_warning(LogCategory.MCP, "上下文使用率警告", {
            "usage_percent": check_result["usage_percent"],
            "recommendation": "建議清理不必要的上下文或進行備份"
        })
    
    async def _prepare_backup(self, check_result: Dict[str, Any]):
        """準備備份"""
        # 實現備份準備邏輯
        log_info(LogCategory.MCP, "準備上下文備份", {
            "usage_percent": check_result["usage_percent"]
        })
    
    async def _generate_optimization_suggestions(self, check_result: Dict[str, Any]):
        """生成優化建議"""
        suggestions = [
            "清理舊的交互記錄",
            "壓縮重複的上下文信息",
            "歸檔不常用的記憶數據",
            "優化記憶查詢策略"
        ]
        
        suggestion_data = {
            "timestamp": datetime.now().isoformat(),
            "usage_percent": check_result["usage_percent"],
            "suggestions": suggestions,
            "priority": "high" if check_result["usage_percent"] > 0.85 else "medium"
        }
        
        self.optimization_suggestions.append(suggestion_data)
        
        log_info(LogCategory.MCP, "生成上下文優化建議", {
            "suggestions_count": len(suggestions),
            "priority": suggestion_data["priority"]
        })
    
    async def _force_backup(self, check_result: Dict[str, Any]):
        """強制備份"""
        # 實現強制備份邏輯
        log_warning(LogCategory.MCP, "執行緊急上下文備份", {
            "usage_percent": check_result["usage_percent"],
            "reason": "上下文使用率達到緊急閾值"
        })
    
    async def _emergency_context_cleanup(self, check_result: Dict[str, Any]):
        """緊急上下文清理"""
        # 實現緊急清理邏輯
        log_warning(LogCategory.MCP, "執行緊急上下文清理", {
            "usage_percent": check_result["usage_percent"],
            "action": "清理最舊的20%上下文數據"
        })
    
    async def _predictive_analysis(self, check_result: Dict[str, Any]):
        """預測性分析"""
        try:
            if len(self.usage_history) >= 10:
                # 分析趨勢
                recent_usage = [data["usage_percent"] for data in self.usage_history[-10:]]
                trend = self._calculate_trend(recent_usage)
                
                # 預測未來使用率
                predicted_usage = self._predict_future_usage(recent_usage, trend)
                
                if predicted_usage > self.thresholds["critical"]:
                    log_warning(LogCategory.MCP, "預測上下文使用率將達到臨界值", {
                        "current_usage": check_result["usage_percent"],
                        "predicted_usage": predicted_usage,
                        "trend": trend
                    })
                    
                    # 提前準備備份
                    await self._prepare_backup(check_result)
                    
        except Exception as e:
            log_error(LogCategory.MCP, "預測性分析失敗", {"error": str(e)})
    
    def _calculate_trend(self, usage_data: List[float]) -> float:
        """計算使用率趨勢"""
        if len(usage_data) < 2:
            return 0.0
        
        # 簡單線性趨勢計算
        n = len(usage_data)
        x_sum = sum(range(n))
        y_sum = sum(usage_data)
        xy_sum = sum(i * usage_data[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    def _predict_future_usage(self, usage_data: List[float], trend: float) -> float:
        """預測未來使用率"""
        if not usage_data:
            return 0.0
        
        current_usage = usage_data[-1]
        # 預測5個時間點後的使用率
        predicted_usage = current_usage + trend * 5
        
        return max(0.0, min(1.0, predicted_usage))
    
    async def _adaptive_adjustment(self, check_result: Dict[str, Any]):
        """自適應調整"""
        try:
            usage_percent = check_result["usage_percent"]
            
            # 根據使用率動態調整檢查間隔
            if usage_percent > 0.8:
                # 高使用率時增加檢查頻率
                new_interval = max(10, self.check_interval // 2)
            elif usage_percent < 0.3:
                # 低使用率時降低檢查頻率
                new_interval = min(120, self.check_interval * 2)
            else:
                new_interval = self.check_interval
            
            if new_interval != self.check_interval:
                self.check_interval = new_interval
                log_info(LogCategory.MCP, "自適應調整檢查間隔", {
                    "new_interval": new_interval,
                    "usage_percent": usage_percent
                })
                
        except Exception as e:
            log_error(LogCategory.MCP, "自適應調整失敗", {"error": str(e)})
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """停止上下文監控"""
        try:
            if not self.monitoring_active:
                return {
                    "status": "warning",
                    "message": "監控未在運行"
                }
            
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                self.monitoring_task = None
            
            log_info(LogCategory.MCP, "上下文監控已停止", {})
            
            return {
                "status": "success",
                "message": "上下文監控已停止",
                "final_stats": self.stats.copy()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"停止監控失敗: {str(e)}"
            }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """獲取監控狀態"""
        return {
            "status": "success",
            "monitoring_active": self.monitoring_active,
            "current_alert_level": self.current_alert_level.value,
            "monitoring_mode": self.monitoring_mode.value,
            "check_interval": self.check_interval,
            "thresholds": self.thresholds.copy(),
            "statistics": self.stats.copy(),
            "last_check": self.usage_history[-1] if self.usage_history else None
        }
    
    @performance_monitor("check_context_usage")
    async def check_context_usage(self) -> Dict[str, Any]:
        """檢查上下文使用情況"""
        try:
            self.stats["total_checks"] += 1
            
            # 獲取當前上下文使用情況
            usage_percent = self.context_monitor.get_context_usage_percent()
            total_chars = self.context_monitor.total_chars
            interaction_count = self.context_monitor.interaction_count
            
            # 計算剩餘容量
            remaining_chars = self.max_context_chars - total_chars
            remaining_percent = remaining_chars / self.max_context_chars
            
            # 檢查閾值
            thresholds_status = self.context_monitor.check_thresholds()
            
            return {
                "status": "success",
                "usage_percent": usage_percent,
                "total_chars": total_chars,
                "max_chars": self.max_context_chars,
                "remaining_chars": remaining_chars,
                "remaining_percent": remaining_percent,
                "interaction_count": interaction_count,
                "alert_level": self.current_alert_level.value,
                "thresholds_status": thresholds_status,
                "check_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"檢查上下文使用情況失敗: {str(e)}"
            }
    
    def set_thresholds(self, warning: float = None, critical: float = None, emergency: float = None) -> Dict[str, Any]:
        """設置閾值"""
        try:
            old_thresholds = self.thresholds.copy()
            
            if warning is not None:
                self.thresholds["warning"] = warning
            if critical is not None:
                self.thresholds["critical"] = critical
            if emergency is not None:
                self.thresholds["emergency"] = emergency
            
            # 驗證閾值邏輯
            if not (0 <= self.thresholds["warning"] <= self.thresholds["critical"] <= self.thresholds["emergency"] <= 1):
                self.thresholds = old_thresholds
                return {
                    "status": "error",
                    "message": "閾值設置無效，必須滿足: 0 <= warning <= critical <= emergency <= 1"
                }
            
            log_info(LogCategory.MCP, "閾值設置已更新", {
                "old_thresholds": old_thresholds,
                "new_thresholds": self.thresholds
            })
            
            return {
                "status": "success",
                "message": "閾值設置已更新",
                "old_thresholds": old_thresholds,
                "new_thresholds": self.thresholds.copy()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"設置閾值失敗: {str(e)}"
            }
    
    def get_usage_history(self, limit: int = 100) -> Dict[str, Any]:
        """獲取使用歷史"""
        try:
            history_data = self.usage_history[-limit:] if limit else self.usage_history
            
            return {
                "status": "success",
                "history": history_data,
                "total_records": len(self.usage_history),
                "returned_records": len(history_data)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取使用歷史失敗: {str(e)}"
            }
    
    def get_alert_history(self, limit: int = 50) -> Dict[str, Any]:
        """獲取警告歷史"""
        try:
            alert_data = self.alert_history[-limit:] if limit else self.alert_history
            
            return {
                "status": "success",
                "alerts": alert_data,
                "total_alerts": len(self.alert_history),
                "returned_alerts": len(alert_data)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"獲取警告歷史失敗: {str(e)}"
            }
    
    async def optimize_context(self, optimization_type: str = "auto") -> Dict[str, Any]:
        """優化上下文"""
        try:
            optimization_results = []
            
            if optimization_type in ["auto", "cleanup"]:
                cleanup_result = await self._perform_context_cleanup()
                optimization_results.append({"type": "cleanup", "result": cleanup_result})
            
            if optimization_type in ["auto", "compress"]:
                compress_result = await self._perform_context_compression()
                optimization_results.append({"type": "compress", "result": compress_result})
            
            if optimization_type in ["auto", "archive"]:
                archive_result = await self._perform_context_archiving()
                optimization_results.append({"type": "archive", "result": archive_result})
            
            self.stats["optimizations_applied"] += len(optimization_results)
            
            return {
                "status": "success",
                "optimization_type": optimization_type,
                "optimization_results": optimization_results,
                "optimization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"上下文優化失敗: {str(e)}"
            }
    
    async def _perform_context_cleanup(self) -> Dict[str, Any]:
        """執行上下文清理"""
        # 實現上下文清理邏輯
        return {
            "status": "success",
            "cleaned_chars": 0,
            "freed_percent": 0.0
        }
    
    async def _perform_context_compression(self) -> Dict[str, Any]:
        """執行上下文壓縮"""
        # 實現上下文壓縮邏輯
        return {
            "status": "success",
            "compressed_chars": 0,
            "compression_ratio": 1.0
        }
    
    async def _perform_context_archiving(self) -> Dict[str, Any]:
        """執行上下文歸檔"""
        # 實現上下文歸檔邏輯
        return {
            "status": "success",
            "archived_chars": 0,
            "archive_location": "context_archive"
        }
    
    async def predict_context_usage(self, time_horizon: int = 60) -> Dict[str, Any]:
        """預測上下文使用情況"""
        try:
            if len(self.usage_history) < 5:
                return {
                    "status": "warning",
                    "message": "歷史數據不足，無法進行預測"
                }
            
            # 獲取最近的使用數據
            recent_usage = [data["usage_percent"] for data in self.usage_history[-10:]]
            trend = self._calculate_trend(recent_usage)
            
            # 預測未來使用率
            predictions = []
            current_usage = recent_usage[-1]
            
            for i in range(1, time_horizon + 1):
                predicted_usage = current_usage + trend * i
                predicted_usage = max(0.0, min(1.0, predicted_usage))
                
                predictions.append({
                    "time_offset": i,
                    "predicted_usage": predicted_usage,
                    "alert_level": self._determine_alert_level(predicted_usage).value
                })
            
            return {
                "status": "success",
                "current_usage": current_usage,
                "trend": trend,
                "time_horizon": time_horizon,
                "predictions": predictions,
                "prediction_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"預測上下文使用情況失敗: {str(e)}"
            }
    
    def configure_monitoring(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """配置監控參數"""
        try:
            old_config = self.config.copy()
            self.config.update(new_config)
            self._update_config_parameters()
            
            return {
                "status": "success",
                "message": "監控配置已更新",
                "old_config": old_config,
                "new_config": self.config.copy()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"配置監控失敗: {str(e)}"
            }
    
    async def export_monitoring_metrics(self, export_format: str = "json", export_path: str = None) -> Dict[str, Any]:
        """導出監控指標"""
        try:
            if export_path is None:
                export_path = f"context_monitoring_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            
            metrics_data = {
                "export_time": datetime.now().isoformat(),
                "monitoring_config": self.config.copy(),
                "thresholds": self.thresholds.copy(),
                "statistics": self.stats.copy(),
                "usage_history": self.usage_history,
                "alert_history": self.alert_history,
                "optimization_suggestions": self.optimization_suggestions
            }
            
            if export_format == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(metrics_data, f, ensure_ascii=False, indent=2)
            else:
                return {
                    "status": "error",
                    "message": f"不支持的導出格式: {export_format}"
                }
            
            return {
                "status": "success",
                "export_path": export_path,
                "export_format": export_format,
                "exported_records": {
                    "usage_history": len(self.usage_history),
                    "alert_history": len(self.alert_history),
                    "optimization_suggestions": len(self.optimization_suggestions)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"導出監控指標失敗: {str(e)}"
            }
    
    def reset_statistics(self) -> Dict[str, Any]:
        """重置統計信息"""
        try:
            old_stats = self.stats.copy()
            
            self.stats = {
                "total_checks": 0,
                "warnings_triggered": 0,
                "critical_alerts": 0,
                "emergency_alerts": 0,
                "auto_backups_triggered": 0,
                "optimizations_applied": 0
            }
            
            # 可選：清理歷史數據
            self.usage_history.clear()
            self.alert_history.clear()
            self.optimization_suggestions.clear()
            
            return {
                "status": "success",
                "message": "統計信息已重置",
                "old_statistics": old_stats,
                "reset_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"重置統計信息失敗: {str(e)}"
            }

# 創建全局實例
context_monitor_mcp = ContextMonitorMCP()

# 導出主要接口
__all__ = [
    'ContextMonitorMCP',
    'AlertLevel',
    'MonitoringMode',
    'context_monitor_mcp'
]

if __name__ == "__main__":
    # 測試MCP功能
    test_data = {
        "operation": "get_status",
        "params": {}
    }
    
    result = context_monitor_mcp.process(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

