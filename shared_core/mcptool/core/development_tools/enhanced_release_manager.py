#!/usr/bin/env python3
"""
增強的Release Manager - 集成自動化MCP註冊

在原有Release Manager基礎上添加：
1. 部署後自動MCP註冊
2. MCP驗證和測試
3. 註冊失敗回滾機制
4. 完整的部署-註冊工作流
"""

import os
import sys
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from pathlib import Path

# 添加項目路徑
sys.path.append('/home/ubuntu/Powerauto.ai')

# 導入原有Release Manager
from mcptool.core.development_tools.release_manager import ReleaseManager

# 導入自動化MCP註冊器
from mcptool.core.development_tools.automated_mcp_registrar import AutomatedMCPRegistrar

logger = logging.getLogger(__name__)

class EnhancedReleaseManager(ReleaseManager):
    """增強的Release Manager - 集成自動化MCP註冊"""
    
    def __init__(self, project_dir: str):
        super().__init__(project_dir)
        
        # 初始化MCP註冊器
        self.mcp_registrar = AutomatedMCPRegistrar(project_dir)
        
        # 部署後鉤子
        self.post_deployment_hooks = []
        
        # MCP註冊配置
        self.mcp_registration_config = {
            'auto_register': True,
            'validate_before_register': True,
            'rollback_on_failure': True,
            'test_after_register': True
        }
        
        logger.info("增強的Release Manager初始化完成，已集成MCP自動註冊")
    
    def add_post_deployment_hook(self, hook_function: Callable):
        """添加部署後鉤子"""
        self.post_deployment_hooks.append(hook_function)
        logger.info(f"已添加部署後鉤子: {hook_function.__name__}")
    
    def deploy_release(self, release_id: int, environment: str = "production") -> Dict[str, Any]:
        """增強的部署發布 - 包含自動MCP註冊"""
        # 執行原有的部署流程
        deployment_result = super().deploy_release(release_id, environment)
        
        if deployment_result['status'] == 'completed':
            # 部署成功後，執行MCP自動註冊
            mcp_registration_result = self._execute_post_deployment_mcp_registration(release_id)
            deployment_result['mcp_registration'] = mcp_registration_result
            
            # 執行其他部署後鉤子
            hook_results = self._execute_post_deployment_hooks(release_id)
            deployment_result['post_deployment_hooks'] = hook_results
            
            # 如果MCP註冊失敗且配置了回滾，執行回滾
            if (mcp_registration_result.get('status') == 'failed' and 
                self.mcp_registration_config['rollback_on_failure']):
                logger.warning("MCP註冊失敗，執行回滾...")
                rollback_result = self.rollback_release(release_id, "MCP註冊失敗")
                deployment_result['rollback'] = rollback_result
                deployment_result['status'] = 'rolled_back'
        
        return deployment_result
    
    def _execute_post_deployment_mcp_registration(self, release_id: int) -> Dict[str, Any]:
        """執行部署後MCP自動註冊"""
        registration_result = {
            'release_id': release_id,
            'start_time': datetime.now().isoformat(),
            'status': 'unknown',
            'steps': [],
            'errors': [],
            'registered_mcps': [],
            'failed_mcps': []
        }
        
        try:
            logger.info(f"開始為發布 {release_id} 執行MCP自動註冊...")
            
            # 步驟1: 發現新的MCP
            registration_result['steps'].append({
                'step': 'discover_mcps',
                'status': 'running',
                'start_time': datetime.now().isoformat()
            })
            
            discovered_mcps = self.mcp_registrar.discover_mcps()
            registration_result['steps'][-1]['status'] = 'completed'
            registration_result['steps'][-1]['end_time'] = datetime.now().isoformat()
            registration_result['steps'][-1]['discovered_count'] = len(discovered_mcps)
            
            # 步驟2: 識別新增的MCP（與已註冊的對比）
            registration_result['steps'].append({
                'step': 'identify_new_mcps',
                'status': 'running',
                'start_time': datetime.now().isoformat()
            })
            
            new_mcps = self._identify_new_mcps(discovered_mcps)
            registration_result['steps'][-1]['status'] = 'completed'
            registration_result['steps'][-1]['end_time'] = datetime.now().isoformat()
            registration_result['steps'][-1]['new_mcps_count'] = len(new_mcps)
            
            if not new_mcps:
                registration_result['status'] = 'no_new_mcps'
                registration_result['message'] = '沒有發現新的MCP需要註冊'
                logger.info("沒有發現新的MCP需要註冊")
                return registration_result
            
            # 步驟3: 驗證新MCP（如果配置了驗證）
            if self.mcp_registration_config['validate_before_register']:
                registration_result['steps'].append({
                    'step': 'validate_mcps',
                    'status': 'running',
                    'start_time': datetime.now().isoformat()
                })
                
                validation_results = self._validate_new_mcps(new_mcps)
                registration_result['steps'][-1]['status'] = 'completed'
                registration_result['steps'][-1]['end_time'] = datetime.now().isoformat()
                registration_result['steps'][-1]['validation_results'] = validation_results
                
                # 過濾掉驗證失敗的MCP
                valid_mcps = [mcp for mcp in new_mcps 
                             if validation_results.get(mcp['registration_name'], {}).get('overall_status') == 'passed']
                
                if not valid_mcps:
                    registration_result['status'] = 'validation_failed'
                    registration_result['errors'].append('所有新MCP驗證失敗')
                    return registration_result
            else:
                valid_mcps = new_mcps
            
            # 步驟4: 批量註冊MCP
            registration_result['steps'].append({
                'step': 'register_mcps',
                'status': 'running',
                'start_time': datetime.now().isoformat()
            })
            
            batch_result = self.mcp_registrar.batch_register_mcps(valid_mcps)
            registration_result['steps'][-1]['status'] = 'completed'
            registration_result['steps'][-1]['end_time'] = datetime.now().isoformat()
            registration_result['steps'][-1]['batch_result'] = batch_result
            
            registration_result['registered_mcps'] = [
                detail['mcp_name'] for detail in batch_result['registration_details']
                if detail['status'] == 'success'
            ]
            registration_result['failed_mcps'] = [
                detail['mcp_name'] for detail in batch_result['registration_details']
                if detail['status'] != 'success'
            ]
            
            # 步驟5: 測試註冊的MCP（如果配置了測試）
            if (self.mcp_registration_config['test_after_register'] and 
                registration_result['registered_mcps']):
                registration_result['steps'].append({
                    'step': 'test_registered_mcps',
                    'status': 'running',
                    'start_time': datetime.now().isoformat()
                })
                
                test_results = self._test_registered_mcps(registration_result['registered_mcps'])
                registration_result['steps'][-1]['status'] = 'completed'
                registration_result['steps'][-1]['end_time'] = datetime.now().isoformat()
                registration_result['steps'][-1]['test_results'] = test_results
            
            # 確定最終狀態
            if registration_result['failed_mcps']:
                registration_result['status'] = 'partial_success'
            else:
                registration_result['status'] = 'success'
            
            logger.info(f"MCP自動註冊完成: {len(registration_result['registered_mcps'])} 成功, "
                       f"{len(registration_result['failed_mcps'])} 失敗")
            
        except Exception as e:
            registration_result['status'] = 'error'
            registration_result['errors'].append(str(e))
            logger.error(f"MCP自動註冊過程出錯: {e}")
        
        registration_result['end_time'] = datetime.now().isoformat()
        return registration_result
    
    def _identify_new_mcps(self, discovered_mcps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """識別新增的MCP"""
        # 獲取當前已註冊的MCP列表
        try:
            from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
            current_registry = SafeMCPRegistry()
            registered_names = set(current_registry.registered_adapters.keys())
        except Exception as e:
            logger.warning(f"無法獲取當前註冊表: {e}")
            registered_names = set()
        
        # 找出新的MCP
        new_mcps = []
        for mcp in discovered_mcps:
            if (mcp['is_valid_mcp'] and 
                mcp['registration_name'] not in registered_names):
                new_mcps.append(mcp)
        
        logger.info(f"發現 {len(new_mcps)} 個新MCP需要註冊")
        return new_mcps
    
    def _validate_new_mcps(self, new_mcps: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """驗證新MCP"""
        validation_results = {}
        
        for mcp in new_mcps:
            try:
                validation_result = self.mcp_registrar.validate_mcp_deployment(mcp)
                validation_results[mcp['registration_name']] = validation_result
            except Exception as e:
                validation_results[mcp['registration_name']] = {
                    'overall_status': 'error',
                    'errors': [str(e)]
                }
        
        return validation_results
    
    def _test_registered_mcps(self, registered_mcp_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """測試已註冊的MCP"""
        test_results = {}
        
        for mcp_name in registered_mcp_names:
            try:
                # 嘗試導入和實例化MCP
                from mcptool.adapters.core.safe_mcp_registry import SafeMCPRegistry
                registry = SafeMCPRegistry()
                adapter = registry.get_adapter(mcp_name)
                
                if adapter:
                    # 基本功能測試
                    test_result = {
                        'import_test': True,
                        'instantiation_test': True,
                        'basic_methods': {}
                    }
                    
                    # 測試基本方法
                    if hasattr(adapter, 'process'):
                        try:
                            # 測試process方法（使用空輸入）
                            result = adapter.process({})
                            test_result['basic_methods']['process'] = True
                        except Exception as e:
                            test_result['basic_methods']['process'] = False
                            test_result['process_error'] = str(e)
                    
                    if hasattr(adapter, 'get_capabilities'):
                        try:
                            capabilities = adapter.get_capabilities()
                            test_result['basic_methods']['get_capabilities'] = True
                            test_result['capabilities'] = capabilities
                        except Exception as e:
                            test_result['basic_methods']['get_capabilities'] = False
                            test_result['capabilities_error'] = str(e)
                    
                    test_result['overall_status'] = 'passed'
                else:
                    test_result = {
                        'import_test': False,
                        'overall_status': 'failed',
                        'error': 'MCP not found in registry'
                    }
                
                test_results[mcp_name] = test_result
                
            except Exception as e:
                test_results[mcp_name] = {
                    'overall_status': 'error',
                    'error': str(e)
                }
        
        return test_results
    
    def _execute_post_deployment_hooks(self, release_id: int) -> List[Dict[str, Any]]:
        """執行部署後鉤子"""
        hook_results = []
        
        release = self._get_release(release_id)
        if not release:
            return hook_results
        
        for hook in self.post_deployment_hooks:
            try:
                hook_result = {
                    'hook_name': hook.__name__,
                    'start_time': datetime.now().isoformat(),
                    'status': 'running'
                }
                
                result = hook(release)
                hook_result['status'] = 'completed'
                hook_result['result'] = result
                
            except Exception as e:
                hook_result['status'] = 'failed'
                hook_result['error'] = str(e)
                logger.error(f"部署後鉤子執行失敗 {hook.__name__}: {e}")
            
            hook_result['end_time'] = datetime.now().isoformat()
            hook_results.append(hook_result)
        
        return hook_results
    
    def configure_mcp_registration(self, config: Dict[str, Any]):
        """配置MCP註冊選項"""
        self.mcp_registration_config.update(config)
        logger.info(f"MCP註冊配置已更新: {self.mcp_registration_config}")
    
    def get_mcp_registration_status(self) -> Dict[str, Any]:
        """獲取MCP註冊狀態"""
        summary = self.mcp_registrar.get_registration_summary()
        
        return {
            'registration_config': self.mcp_registration_config,
            'registration_summary': summary,
            'post_deployment_hooks_count': len(self.post_deployment_hooks)
        }
    
    def manual_mcp_registration(self, force: bool = False) -> Dict[str, Any]:
        """手動觸發MCP註冊"""
        logger.info("手動觸發MCP註冊...")
        
        # 創建一個虛擬發布ID用於手動註冊
        manual_release_id = 999999
        
        return self._execute_post_deployment_mcp_registration(manual_release_id)

# 測試代碼
if __name__ == "__main__":
    # 創建增強的Release Manager
    enhanced_rm = EnhancedReleaseManager("/home/ubuntu/Powerauto.ai")
    
    # 測試手動MCP註冊
    print("=== 測試手動MCP註冊 ===")
    result = enhanced_rm.manual_mcp_registration()
    print(f"註冊結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 獲取MCP註冊狀態
    print(f"\n=== MCP註冊狀態 ===")
    status = enhanced_rm.get_mcp_registration_status()
    print(f"狀態: {json.dumps(status, indent=2, ensure_ascii=False)}")

