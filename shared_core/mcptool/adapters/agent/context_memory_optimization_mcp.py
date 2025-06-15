#!/usr/bin/env python3
"""
上下文記憶優化MCP模塊

負責智能體的上下文記憶管理，使用SuperMemory.ai API
"""

import logging
import requests
import json
from typing import Dict, Any, List, Optional

from mcptool.core.base_mcp import AgentOptimizationMCP

class ContextMemoryOptimizationMCP(AgentOptimizationMCP):
    """上下文記憶優化MCP，負責智能體的上下文記憶管理"""
    
    def __init__(self):
        """初始化上下文記憶優化MCP"""
        super().__init__(
            mcp_id="context_memory_optimization",
            name="上下文記憶優化MCP",
            description="負責智能體的上下文記憶管理，使用SuperMemory.ai API"
        )
        # SuperMemory.ai API配置
        self.api_key = "sm_ohYKVYxdyurx5qGri5VqCi_IQubZkKtpalCUphaVpzcpTNJQiimJwRpuLNRkmgwZNzYKoCUSKUpUqWQewJEJQZc"
        self.api_base_url = "https://api.supermemory.ai/v1"
        
    def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        處理上下文記憶優化
        
        參數:
            input_data: 輸入數據字典
            context: 上下文信息字典
            
        返回:
            處理結果字典
        """
        memory_action = input_data.get("memory_action")
        
        if not memory_action:
            return {"status": "error", "message": "缺少memory_action参数"}
            
        if memory_action == "store":
            return self._store_memory(input_data, context)
        elif memory_action == "retrieve":
            return self._retrieve_memory(input_data, context)
        elif memory_action == "update":
            return self._update_memory(input_data, context)
        elif memory_action == "delete":
            return self._delete_memory(input_data, context)
        else:
            return {"status": "error", "message": f"不支持的记忆操作: {memory_action}"}
    
    def _store_memory(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        存储项目记忆
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        project_id = input_data.get("project_id")
        memory_type = input_data.get("memory_type", "ppt_project")
        memory_data = input_data.get("memory_data", {})
        
        if not project_id:
            return {"status": "error", "message": "缺少project_id参数"}
        
        if not memory_data:
            return {"status": "error", "message": "缺少memory_data参数"}
        
        try:
            # 准备请求数据
            payload = {
                "project_id": project_id,
                "memory_type": memory_type,
                "data": memory_data
            }
            
            # 调用SuperMemory.ai API存储记忆
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base_url}/memories",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                return {
                    "status": "success",
                    "memory_id": result.get("memory_id"),
                    "message": "记忆存储成功"
                }
            else:
                self.logger.error(f"记忆存储失败: {response.text}")
                return {
                    "status": "error",
                    "message": f"记忆存储失败: {response.text}"
                }
                
        except Exception as e:
            self.logger.error(f"记忆存储异常: {str(e)}")
            return {
                "status": "error",
                "message": f"记忆存储异常: {str(e)}"
            }
    
    def _retrieve_memory(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        检索项目记忆
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        project_id = input_data.get("project_id")
        memory_id = input_data.get("memory_id")
        query = input_data.get("query")
        
        if not project_id and not memory_id and not query:
            return {"status": "error", "message": "缺少检索条件，需要提供project_id、memory_id或query参数"}
        
        try:
            # 准备请求参数
            params = {}
            if project_id:
                params["project_id"] = project_id
            if memory_id:
                params["memory_id"] = memory_id
            if query:
                params["query"] = query
            
            # 调用SuperMemory.ai API检索记忆
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                f"{self.api_base_url}/memories",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "memories": result.get("memories", []),
                    "message": "记忆检索成功"
                }
            else:
                self.logger.error(f"记忆检索失败: {response.text}")
                return {
                    "status": "error",
                    "message": f"记忆检索失败: {response.text}"
                }
                
        except Exception as e:
            self.logger.error(f"记忆检索异常: {str(e)}")
            return {
                "status": "error",
                "message": f"记忆检索异常: {str(e)}"
            }
    
    def _update_memory(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        更新项目记忆
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        memory_id = input_data.get("memory_id")
        memory_data = input_data.get("memory_data", {})
        
        if not memory_id:
            return {"status": "error", "message": "缺少memory_id参数"}
        
        if not memory_data:
            return {"status": "error", "message": "缺少memory_data参数"}
        
        try:
            # 准备请求数据
            payload = {
                "data": memory_data
            }
            
            # 调用SuperMemory.ai API更新记忆
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.put(
                f"{self.api_base_url}/memories/{memory_id}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "记忆更新成功"
                }
            else:
                self.logger.error(f"记忆更新失败: {response.text}")
                return {
                    "status": "error",
                    "message": f"记忆更新失败: {response.text}"
                }
                
        except Exception as e:
            self.logger.error(f"记忆更新异常: {str(e)}")
            return {
                "status": "error",
                "message": f"记忆更新异常: {str(e)}"
            }
    
    def _delete_memory(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        删除项目记忆
        
        参数:
            input_data: 输入数据字典
            context: 上下文信息字典
            
        返回:
            处理结果字典
        """
        memory_id = input_data.get("memory_id")
        
        if not memory_id:
            return {"status": "error", "message": "缺少memory_id参数"}
        
        try:
            # 调用SuperMemory.ai API删除记忆
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.delete(
                f"{self.api_base_url}/memories/{memory_id}",
                headers=headers
            )
            
            if response.status_code == 200 or response.status_code == 204:
                return {
                    "status": "success",
                    "message": "记忆删除成功"
                }
            else:
                self.logger.error(f"记忆删除失败: {response.text}")
                return {
                    "status": "error",
                    "message": f"记忆删除失败: {response.text}"
                }
                
        except Exception as e:
            self.logger.error(f"记忆删除异常: {str(e)}")
            return {
                "status": "error",
                "message": f"记忆删除异常: {str(e)}"
            }
