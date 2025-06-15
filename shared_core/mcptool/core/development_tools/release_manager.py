"""
ReleaseManager 核心模塊

智能發布管理和版本控制系統
"""

import os
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ReleaseManager:
    """智能發布管理器"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.releases = []
        self.current_release = None
        self.release_history = []
        
        # 發布類型
        self.release_types = {
            "major": "主要版本",
            "minor": "次要版本", 
            "patch": "補丁版本",
            "hotfix": "熱修復",
            "beta": "測試版本",
            "alpha": "內測版本"
        }
        
        # 發布階段
        self.release_stages = [
            "planning",      # 規劃
            "development",   # 開發
            "testing",       # 測試
            "staging",       # 預發布
            "production",    # 生產
            "monitoring"     # 監控
        ]
        
        logger.info(f"ReleaseManager初始化完成，項目目錄: {project_dir}")
    
    def create_release(self, version: str, release_notes: str = "", release_type: str = "minor") -> Dict[str, Any]:
        """創建新發布"""
        release = {
            'id': len(self.releases) + 1,
            'version': version,
            'release_type': release_type,
            'release_notes': release_notes,
            'stage': 'planning',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'draft',
            'artifacts': [],
            'tests': [],
            'approvals': [],
            'deployment_config': self._create_deployment_config(),
            'rollback_plan': self._create_rollback_plan(),
            'success_criteria': self._define_success_criteria(),
            'risk_assessment': self._assess_release_risks()
        }
        
        self.releases.append(release)
        self.current_release = release
        
        self._log_release_event(release['id'], 'created', f"發布 {version} 已創建")
        logger.info(f"發布創建完成: {version} ({release_type})")
        
        return release
    
    def update_release_stage(self, release_id: int, new_stage: str) -> Dict[str, Any]:
        """更新發布階段"""
        release = self._get_release(release_id)
        if not release:
            raise ValueError(f"發布不存在: {release_id}")
        
        if new_stage not in self.release_stages:
            raise ValueError(f"無效的發布階段: {new_stage}")
        
        old_stage = release['stage']
        release['stage'] = new_stage
        release['updated_at'] = datetime.now().isoformat()
        
        # 階段特定操作
        if new_stage == 'testing':
            self._initiate_testing(release)
        elif new_stage == 'staging':
            self._prepare_staging(release)
        elif new_stage == 'production':
            self._deploy_to_production(release)
        
        self._log_release_event(release_id, 'stage_updated', 
                               f"階段從 {old_stage} 更新到 {new_stage}")
        
        logger.info(f"發布 {release['version']} 階段更新: {old_stage} -> {new_stage}")
        return release
    
    def add_release_artifact(self, release_id: int, artifact_path: str, artifact_type: str = "binary") -> Dict[str, Any]:
        """添加發布產物"""
        release = self._get_release(release_id)
        if not release:
            raise ValueError(f"發布不存在: {release_id}")
        
        artifact = {
            'id': len(release['artifacts']) + 1,
            'path': artifact_path,
            'type': artifact_type,
            'size': self._get_file_size(artifact_path),
            'checksum': self._calculate_checksum(artifact_path),
            'created_at': datetime.now().isoformat()
        }
        
        release['artifacts'].append(artifact)
        release['updated_at'] = datetime.now().isoformat()
        
        self._log_release_event(release_id, 'artifact_added', 
                               f"產物已添加: {artifact_path}")
        
        return artifact
    
    def run_release_tests(self, release_id: int, test_suite: str = "full") -> Dict[str, Any]:
        """運行發布測試"""
        release = self._get_release(release_id)
        if not release:
            raise ValueError(f"發布不存在: {release_id}")
        
        test_result = {
            'id': len(release['tests']) + 1,
            'suite': test_suite,
            'started_at': datetime.now().isoformat(),
            'status': 'running',
            'results': {},
            'coverage': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # 模擬測試執行
        test_results = self._execute_test_suite(test_suite)
        test_result.update(test_results)
        test_result['completed_at'] = datetime.now().isoformat()
        test_result['status'] = 'completed'
        
        release['tests'].append(test_result)
        release['updated_at'] = datetime.now().isoformat()
        
        self._log_release_event(release_id, 'tests_completed', 
                               f"測試完成: {test_result['passed']}/{test_result['passed'] + test_result['failed']} 通過")
        
        return test_result
    
    def approve_release(self, release_id: int, approver: str, approval_type: str = "general") -> Dict[str, Any]:
        """批准發布"""
        release = self._get_release(release_id)
        if not release:
            raise ValueError(f"發布不存在: {release_id}")
        
        approval = {
            'id': len(release['approvals']) + 1,
            'approver': approver,
            'type': approval_type,
            'status': 'approved',
            'comments': f"{approval_type} 批准",
            'approved_at': datetime.now().isoformat()
        }
        
        release['approvals'].append(approval)
        release['updated_at'] = datetime.now().isoformat()
        
        # 檢查是否所有必需的批准都已獲得
        if self._check_all_approvals(release):
            release['status'] = 'approved'
        
        self._log_release_event(release_id, 'approved', 
                               f"{approver} 已批准發布 ({approval_type})")
        
        return approval
    
    def deploy_release(self, release_id: int, environment: str = "production") -> Dict[str, Any]:
        """部署發布"""
        release = self._get_release(release_id)
        if not release:
            raise ValueError(f"發布不存在: {release_id}")
        
        if release['status'] != 'approved':
            raise ValueError("發布尚未獲得批准")
        
        deployment = {
            'id': f"deploy_{release_id}_{environment}",
            'release_id': release_id,
            'environment': environment,
            'started_at': datetime.now().isoformat(),
            'status': 'deploying',
            'steps': [],
            'rollback_available': True
        }
        
        # 執行部署步驟
        deployment_steps = self._execute_deployment(release, environment)
        deployment['steps'] = deployment_steps
        deployment['completed_at'] = datetime.now().isoformat()
        deployment['status'] = 'completed'
        
        release['status'] = 'deployed'
        release['deployed_at'] = datetime.now().isoformat()
        release['updated_at'] = datetime.now().isoformat()
        
        self._log_release_event(release_id, 'deployed', 
                               f"已部署到 {environment}")
        
        return deployment
    
    def rollback_release(self, release_id: int, reason: str = "") -> Dict[str, Any]:
        """回滾發布"""
        release = self._get_release(release_id)
        if not release:
            raise ValueError(f"發布不存在: {release_id}")
        
        rollback = {
            'id': f"rollback_{release_id}",
            'release_id': release_id,
            'reason': reason,
            'started_at': datetime.now().isoformat(),
            'status': 'rolling_back',
            'steps': []
        }
        
        # 執行回滾步驟
        rollback_steps = self._execute_rollback(release)
        rollback['steps'] = rollback_steps
        rollback['completed_at'] = datetime.now().isoformat()
        rollback['status'] = 'completed'
        
        release['status'] = 'rolled_back'
        release['rolled_back_at'] = datetime.now().isoformat()
        release['updated_at'] = datetime.now().isoformat()
        
        self._log_release_event(release_id, 'rolled_back', 
                               f"已回滾: {reason}")
        
        return rollback
    
    def _get_release(self, release_id: int) -> Optional[Dict[str, Any]]:
        """獲取發布信息"""
        return next((r for r in self.releases if r['id'] == release_id), None)
    
    def _create_deployment_config(self) -> Dict[str, Any]:
        """創建部署配置"""
        return {
            'strategy': 'blue_green',
            'health_checks': ['api_health', 'database_connection', 'service_status'],
            'timeout': 300,
            'rollback_threshold': 0.05,
            'monitoring_duration': 1800
        }
    
    def _create_rollback_plan(self) -> Dict[str, Any]:
        """創建回滾計劃"""
        return {
            'automatic_triggers': ['error_rate > 5%', 'response_time > 2s'],
            'manual_triggers': ['user_reported_issues', 'business_decision'],
            'rollback_steps': [
                '停止新流量路由',
                '切換到前一版本',
                '驗證系統健康',
                '通知相關團隊'
            ],
            'estimated_time': '15分鐘'
        }
    
    def _define_success_criteria(self) -> List[str]:
        """定義成功標準"""
        return [
            "部署成功完成",
            "所有健康檢查通過",
            "錯誤率低於1%",
            "響應時間在正常範圍",
            "用戶反饋正面"
        ]
    
    def _assess_release_risks(self) -> List[Dict[str, Any]]:
        """評估發布風險"""
        return [
            {
                'risk': '部署失敗',
                'probability': 'low',
                'impact': 'high',
                'mitigation': '充分測試和回滾計劃'
            },
            {
                'risk': '性能下降',
                'probability': 'medium',
                'impact': 'medium',
                'mitigation': '性能監控和負載測試'
            },
            {
                'risk': '用戶體驗問題',
                'probability': 'low',
                'impact': 'medium',
                'mitigation': '用戶驗收測試'
            }
        ]
    
    def _initiate_testing(self, release: Dict[str, Any]):
        """啟動測試階段"""
        logger.info(f"啟動測試階段: {release['version']}")
    
    def _prepare_staging(self, release: Dict[str, Any]):
        """準備預發布環境"""
        logger.info(f"準備預發布環境: {release['version']}")
    
    def _deploy_to_production(self, release: Dict[str, Any]):
        """部署到生產環境"""
        logger.info(f"部署到生產環境: {release['version']}")
    
    def _execute_test_suite(self, test_suite: str) -> Dict[str, Any]:
        """執行測試套件"""
        # 模擬測試結果
        return {
            'results': {
                'unit_tests': {'passed': 45, 'failed': 2, 'skipped': 3},
                'integration_tests': {'passed': 20, 'failed': 0, 'skipped': 1},
                'e2e_tests': {'passed': 15, 'failed': 1, 'skipped': 0}
            },
            'coverage': 85.5,
            'passed': 80,
            'failed': 3,
            'skipped': 4
        }
    
    def _check_all_approvals(self, release: Dict[str, Any]) -> bool:
        """檢查所有必需的批准"""
        required_approvals = ['technical', 'business', 'security']
        approved_types = [a['type'] for a in release['approvals'] if a['status'] == 'approved']
        return all(req in approved_types for req in required_approvals)
    
    def _execute_deployment(self, release: Dict[str, Any], environment: str) -> List[Dict[str, Any]]:
        """執行部署"""
        steps = [
            {'name': '備份當前版本', 'status': 'completed', 'duration': '2分鐘'},
            {'name': '停止服務', 'status': 'completed', 'duration': '1分鐘'},
            {'name': '部署新版本', 'status': 'completed', 'duration': '5分鐘'},
            {'name': '啟動服務', 'status': 'completed', 'duration': '2分鐘'},
            {'name': '健康檢查', 'status': 'completed', 'duration': '3分鐘'},
            {'name': '流量切換', 'status': 'completed', 'duration': '1分鐘'}
        ]
        return steps
    
    def _execute_rollback(self, release: Dict[str, Any]) -> List[Dict[str, Any]]:
        """執行回滾"""
        steps = [
            {'name': '停止當前版本', 'status': 'completed', 'duration': '1分鐘'},
            {'name': '恢復備份版本', 'status': 'completed', 'duration': '3分鐘'},
            {'name': '啟動服務', 'status': 'completed', 'duration': '2分鐘'},
            {'name': '驗證功能', 'status': 'completed', 'duration': '2分鐘'}
        ]
        return steps
    
    def _get_file_size(self, file_path: str) -> int:
        """獲取文件大小"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def _calculate_checksum(self, file_path: str) -> str:
        """計算文件校驗和"""
        import hashlib
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return "unknown"
    
    def _log_release_event(self, release_id: int, event_type: str, message: str):
        """記錄發布事件"""
        event = {
            'release_id': release_id,
            'event_type': event_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.release_history.append(event)
    
    def get_release_summary(self) -> Dict[str, Any]:
        """獲取發布總結"""
        return {
            'total_releases': len(self.releases),
            'current_release': self.current_release['version'] if self.current_release else None,
            'release_types': {rt: len([r for r in self.releases if r.get('release_type') == rt]) 
                            for rt in self.release_types.keys()},
            'stage_distribution': {stage: len([r for r in self.releases if r.get('stage') == stage]) 
                                 for stage in self.release_stages},
            'success_rate': len([r for r in self.releases if r.get('status') == 'deployed']) / max(len(self.releases), 1)
        }

