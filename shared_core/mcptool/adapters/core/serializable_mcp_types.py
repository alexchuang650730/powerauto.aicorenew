#!/usr/bin/env python3
"""
修復的MCP能力類
解決JSON序列化問題
"""

import json
from enum import Enum
from typing import Dict, Any

class SerializableMCPCapability(Enum):
    """可序列化的MCP能力枚舉"""
    DATA_PROCESSING = "data_processing"
    MEMORY_MANAGEMENT = "memory_management"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    AI_ENHANCEMENT = "ai_enhancement"
    MONITORING = "monitoring"
    BACKUP_RECOVERY = "backup_recovery"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    DEVELOPMENT = "development"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"MCPCapability.{self.name}"
    
    def to_dict(self) -> Dict[str, str]:
        """轉換為字典格式"""
        return {
            "name": self.name,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'SerializableMCPCapability':
        """從字典創建實例"""
        return cls(data["value"])

class SerializableIntentCategory(Enum):
    """可序列化的意圖分類枚舉"""
    DATA_OPERATION = "data_operation"
    MEMORY_QUERY = "memory_query"
    WORKFLOW_EXECUTION = "workflow_execution"
    SYSTEM_MONITORING = "system_monitoring"
    BACKUP_RESTORE = "backup_restore"
    OPTIMIZATION_REQUEST = "optimization_request"
    DEVELOPMENT_TASK = "development_task"
    INTEGRATION_SETUP = "integration_setup"
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"IntentCategory.{self.name}"
    
    def to_dict(self) -> Dict[str, str]:
        """轉換為字典格式"""
        return {
            "name": self.name,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'SerializableIntentCategory':
        """從字典創建實例"""
        return cls(data["value"])

class MCPCapabilityEncoder(json.JSONEncoder):
    """MCP能力JSON編碼器"""
    
    def default(self, obj):
        if isinstance(obj, (SerializableMCPCapability, SerializableIntentCategory)):
            return obj.to_dict()
        return super().default(obj)

def serialize_mcp_data(data: Any) -> str:
    """序列化MCP數據"""
    return json.dumps(data, cls=MCPCapabilityEncoder, ensure_ascii=False, indent=2)

def deserialize_mcp_data(json_str: str) -> Any:
    """反序列化MCP數據"""
    return json.loads(json_str)

