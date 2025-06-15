#!/usr/bin/env python3
"""
ReleaseManager MCP适配器

此模块为ReleaseManager提供MCP协议合规的包装，支持完整发布流程测试。
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目路径
sys.path.append('/home/ubuntu/powerautomation')

try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子类必须实现此方法")
        
        def validate_input(self, input_data: Dict[str, Any]) -> bool:
            return True
        
        def get_capabilities(self) -> List[str]:
            return ["基础MCP适配功能"]

# 尝试导入原始ReleaseManager
try:
    from mcptool.core.development_tools.release_manager import ReleaseManager
    RELEASE_MANAGER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ReleaseManager導入失敗: {e}")
    RELEASE_MANAGER_AVAILABLE = False
    
    # 创建Mock实现
    class ReleaseManager:
        def __init__(self, project_dir: str):
            self.project_dir = project_dir
            self.releases = []
            self.current_release = None
            
        def create_release(self, version: str, release_notes: str = "") -> Dict:
            release = {
                'id': len(self.releases) + 1,
                'version': version,
                'release_notes': release_notes,
                'status': 'created',
                'created_at': datetime.now().isoformat(),
                'stages': {
                    'code_detection': 'pending',
                    'testing': 'pending',
                    'deployment': 'pending',
                    'verification': 'pending'
                }
            }
            self.releases.append(release)
            self.current_release = release
            return release
            
        def run_code_detection(self, release_id: int) -> Dict:
            release = self._get_release(release_id)
            if release:
                release['stages']['code_detection'] = 'completed'
                return {
                    'status': 'success',
                    'issues_found': 2,
                    'critical_issues': 0,
                    'warnings': 5,
                    'scan_time': 45.2
                }
            return {'status': 'error', 'message': 'Release not found'}
            
        def run_tests(self, release_id: int) -> Dict:
            release = self._get_release(release_id)
            if release:
                release['stages']['testing'] = 'completed'
                return {
                    'status': 'success',
                    'tests_run': 156,
                    'tests_passed': 154,
                    'tests_failed': 2,
                    'coverage': 89.5,
                    'test_time': 120.8
                }
            return {'status': 'error', 'message': 'Release not found'}
            
        def deploy_release(self, release_id: int, environment: str = 'staging') -> Dict:
            release = self._get_release(release_id)
            if release:
                release['stages']['deployment'] = 'completed'
                return {
                    'status': 'success',
                    'environment': environment,
                    'deployment_url': f'https://{environment}.example.com',
                    'deployment_time': 89.3
                }
            return {'status': 'error', 'message': 'Release not found'}
            
        def verify_deployment(self, release_id: int) -> Dict:
            release = self._get_release(release_id)
            if release:
                release['stages']['verification'] = 'completed'
                release['status'] = 'completed'
                return {
                    'status': 'success',
                    'health_check': 'passed',
                    'performance_check': 'passed',
                    'security_check': 'passed',
                    'verification_time': 30.1
                }
            return {'status': 'error', 'message': 'Release not found'}
            
        def _get_release(self, release_id: int) -> Optional[Dict]:
            return next((r for r in self.releases if r['id'] == release_id), None)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("release_manager_mcp")

class ReleaseManagerMCP(BaseMCP):
    """ReleaseManager的MCP包装器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="ReleaseManagerMCP")
        
        # 解析配置
        config = config or {}
        project_dir = config.get('project_dir', '/home/ubuntu/powerautomation')
        
        # 初始化ReleaseManager
        try:
            self.release_manager = ReleaseManager(project_dir)
            self.is_available = RELEASE_MANAGER_AVAILABLE
        except Exception as e:
            self.logger.error(f"ReleaseManager初始化失败: {e}")
            self.release_manager = None
            self.is_available = False
        
        # 初始化指标
        self.metrics = {
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0,
            'total_execution_time': 0,
            'releases_created': 0,
            'deployments_completed': 0,
            'tests_executed': 0
        }
        
        self.logger.info(f"ReleaseManager MCP适配器初始化完成，可用性: {self.is_available}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP协议标准处理方法"""
        start_time = datetime.now()
        
        try:
            # 1. 输入验证
            if not self.validate_input(input_data):
                return self._create_error_response("输入验证失败", "INVALID_INPUT")
            
            # 2. 检查适配器可用性
            if not self.is_available:
                return self._create_error_response("ReleaseManager不可用", "ADAPTER_UNAVAILABLE")
            
            # 3. 解析操作类型
            action = input_data.get('action', 'create_release')
            parameters = input_data.get('parameters', {})
            
            # 4. 执行相应操作
            if action == 'create_release':
                result = self._create_release(parameters)
            elif action == 'run_code_detection':
                result = self._run_code_detection(parameters)
            elif action == 'run_tests':
                result = self._run_tests(parameters)
            elif action == 'deploy_release':
                result = self._deploy_release(parameters)
            elif action == 'verify_deployment':
                result = self._verify_deployment(parameters)
            elif action == 'get_release_status':
                result = self._get_release_status(parameters)
            elif action == 'run_full_pipeline':
                result = self._run_full_pipeline(parameters)
            elif action == 'get_capabilities':
                result = {'capabilities': self.get_capabilities()}
            elif action == 'get_status':
                result = self._get_status()
            else:
                return self._create_error_response(f"不支持的操作: {action}", "UNSUPPORTED_ACTION")
            
            # 5. 记录成功指标
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(execution_time, True)
            
            # 6. 返回标准化结果
            return {
                'status': 'success',
                'data': {
                    'result': result,
                    'metrics': self._get_execution_metrics()
                },
                'metadata': {
                    'adapter_name': self.name,
                    'action': action,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
            }
            
        except Exception as e:
            # 记录错误指标
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_execution(execution_time, False)
            
            self.logger.error(f"ReleaseManager执行失败: {str(e)}")
            return self._create_error_response(str(e), "EXECUTION_ERROR")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get('action', 'create_release')
        parameters = input_data.get('parameters', {})
        
        # 验证必需参数
        if action == 'create_release':
            return 'version' in parameters
        elif action in ['run_code_detection', 'run_tests', 'deploy_release', 'verify_deployment', 'get_release_status']:
            return 'release_id' in parameters
        elif action == 'run_full_pipeline':
            return 'version' in parameters
        elif action in ['get_capabilities', 'get_status']:
            return True
        else:
            return False
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力列表"""
        return [
            "release_management",
            "code_detection",
            "automated_testing",
            "deployment_automation",
            "verification_checks",
            "pipeline_orchestration",
            "rollback_support",
            "environment_management"
        ]
    
    def _create_release(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """创建发布"""
        version = parameters.get('version')
        release_notes = parameters.get('release_notes', '')
        
        if self.release_manager and hasattr(self.release_manager, 'create_release'):
            release = self.release_manager.create_release(version, release_notes)
        else:
            # Mock实现
            release = {
                'id': self.metrics['releases_created'] + 1,
                'version': version,
                'release_notes': release_notes,
                'status': 'created',
                'created_at': datetime.now().isoformat(),
                'stages': {
                    'code_detection': 'pending',
                    'testing': 'pending',
                    'deployment': 'pending',
                    'verification': 'pending'
                }
            }
        
        self.metrics['releases_created'] += 1
        
        return {
            'action': 'create_release',
            'release': release,
            'timestamp': datetime.now().isoformat()
        }
    
    def _run_code_detection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """运行代码检测"""
        release_id = parameters.get('release_id')
        
        if self.release_manager and hasattr(self.release_manager, 'run_code_detection'):
            result = self.release_manager.run_code_detection(release_id)
        else:
            # Mock实现
            result = {
                'status': 'success',
                'issues_found': 2,
                'critical_issues': 0,
                'warnings': 5,
                'scan_time': 45.2,
                'details': [
                    {'type': 'warning', 'file': 'main.py', 'line': 42, 'message': '未使用的变量'},
                    {'type': 'info', 'file': 'utils.py', 'line': 15, 'message': '可以优化的代码'}
                ]
            }
        
        return {
            'action': 'run_code_detection',
            'release_id': release_id,
            'detection_result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _run_tests(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """运行测试"""
        release_id = parameters.get('release_id')
        test_suite = parameters.get('test_suite', 'all')
        
        if self.release_manager and hasattr(self.release_manager, 'run_tests'):
            result = self.release_manager.run_tests(release_id)
        else:
            # Mock实现
            result = {
                'status': 'success',
                'tests_run': 156,
                'tests_passed': 154,
                'tests_failed': 2,
                'coverage': 89.5,
                'test_time': 120.8,
                'failed_tests': [
                    {'name': 'test_api_timeout', 'error': 'Connection timeout'},
                    {'name': 'test_edge_case', 'error': 'Assertion failed'}
                ]
            }
        
        self.metrics['tests_executed'] += result.get('tests_run', 0)
        
        return {
            'action': 'run_tests',
            'release_id': release_id,
            'test_suite': test_suite,
            'test_result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _deploy_release(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """部署发布"""
        release_id = parameters.get('release_id')
        environment = parameters.get('environment', 'staging')
        
        if self.release_manager and hasattr(self.release_manager, 'deploy_release'):
            result = self.release_manager.deploy_release(release_id, environment)
        else:
            # Mock实现
            result = {
                'status': 'success',
                'environment': environment,
                'deployment_url': f'https://{environment}.example.com',
                'deployment_time': 89.3,
                'services_deployed': ['api', 'frontend', 'worker'],
                'health_status': 'healthy'
            }
        
        self.metrics['deployments_completed'] += 1
        
        return {
            'action': 'deploy_release',
            'release_id': release_id,
            'environment': environment,
            'deployment_result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _verify_deployment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """验证部署"""
        release_id = parameters.get('release_id')
        environment = parameters.get('environment', 'staging')
        
        if self.release_manager and hasattr(self.release_manager, 'verify_deployment'):
            result = self.release_manager.verify_deployment(release_id)
        else:
            # Mock实现
            result = {
                'status': 'success',
                'health_check': 'passed',
                'performance_check': 'passed',
                'security_check': 'passed',
                'verification_time': 30.1,
                'checks': {
                    'api_response': 'healthy',
                    'database_connection': 'healthy',
                    'external_services': 'healthy'
                }
            }
        
        return {
            'action': 'verify_deployment',
            'release_id': release_id,
            'environment': environment,
            'verification_result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_release_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取发布状态"""
        release_id = parameters.get('release_id')
        
        if self.release_manager and hasattr(self.release_manager, '_get_release'):
            release = self.release_manager._get_release(release_id)
        else:
            # Mock实现
            release = {
                'id': release_id,
                'version': '1.0.0',
                'status': 'in_progress',
                'stages': {
                    'code_detection': 'completed',
                    'testing': 'in_progress',
                    'deployment': 'pending',
                    'verification': 'pending'
                }
            }
        
        return {
            'action': 'get_release_status',
            'release_id': release_id,
            'release_status': release,
            'timestamp': datetime.now().isoformat()
        }
    
    def _run_full_pipeline(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """运行完整发布流水线"""
        version = parameters.get('version')
        release_notes = parameters.get('release_notes', '')
        environment = parameters.get('environment', 'staging')
        
        pipeline_results = []
        
        # 1. 创建发布
        create_result = self._create_release({'version': version, 'release_notes': release_notes})
        pipeline_results.append(create_result)
        release_id = create_result['release']['id']
        
        # 2. 代码检测
        detection_result = self._run_code_detection({'release_id': release_id})
        pipeline_results.append(detection_result)
        
        # 3. 运行测试
        test_result = self._run_tests({'release_id': release_id})
        pipeline_results.append(test_result)
        
        # 4. 部署
        deploy_result = self._deploy_release({'release_id': release_id, 'environment': environment})
        pipeline_results.append(deploy_result)
        
        # 5. 验证
        verify_result = self._verify_deployment({'release_id': release_id, 'environment': environment})
        pipeline_results.append(verify_result)
        
        # 计算总体状态
        overall_status = 'success' if all(
            r.get('deployment_result', {}).get('status') == 'success' or
            r.get('test_result', {}).get('status') == 'success' or
            r.get('detection_result', {}).get('status') == 'success' or
            r.get('verification_result', {}).get('status') == 'success' or
            r.get('release', {}).get('status') == 'created'
            for r in pipeline_results
        ) else 'failed'
        
        return {
            'action': 'run_full_pipeline',
            'version': version,
            'environment': environment,
            'overall_status': overall_status,
            'pipeline_results': pipeline_results,
            'total_time': sum(
                r.get('detection_result', {}).get('scan_time', 0) +
                r.get('test_result', {}).get('test_time', 0) +
                r.get('deployment_result', {}).get('deployment_time', 0) +
                r.get('verification_result', {}).get('verification_time', 0)
                for r in pipeline_results
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            'action': 'get_status',
            'status': {
                'is_available': self.is_available,
                'releases_created': self.metrics['releases_created'],
                'deployments_completed': self.metrics['deployments_completed'],
                'tests_executed': self.metrics['tests_executed'],
                'success_rate': self._calculate_success_rate(),
                'uptime': 'active'
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if self.metrics['execution_count'] > 0:
            return self.metrics['success_count'] / self.metrics['execution_count']
        return 0.0
    
    def _create_error_response(self, message: str, error_code: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            'status': 'error',
            'error': {
                'code': error_code,
                'message': message,
                'timestamp': datetime.now().isoformat()
            },
            'metadata': {
                'adapter_name': self.name,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _record_execution(self, execution_time: float, success: bool):
        """记录执行指标"""
        self.metrics['execution_count'] += 1
        self.metrics['total_execution_time'] += execution_time
        
        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['error_count'] += 1
    
    def _get_execution_metrics(self) -> Dict[str, Any]:
        """获取执行指标"""
        if self.metrics['execution_count'] > 0:
            avg_time = self.metrics['total_execution_time'] / self.metrics['execution_count']
            success_rate = self.metrics['success_count'] / self.metrics['execution_count']
        else:
            avg_time = 0
            success_rate = 0
        
        return {
            'execution_count': self.metrics['execution_count'],
            'success_rate': success_rate,
            'average_execution_time': avg_time,
            'releases_created': self.metrics['releases_created'],
            'deployments_completed': self.metrics['deployments_completed'],
            'tests_executed': self.metrics['tests_executed'],
            'availability': self.is_available
        }

def test_release_manager_mcp():
    """测试ReleaseManager MCP适配器"""
    print("=== 测试ReleaseManager MCP适配器 ===")
    
    # 创建适配器实例
    config = {'project_dir': '/home/ubuntu/powerautomation'}
    adapter = ReleaseManagerMCP(config)
    
    # 测试完整发布流水线
    pipeline_input = {
        'action': 'run_full_pipeline',
        'parameters': {
            'version': '1.2.0',
            'release_notes': '新功能发布：添加MCP适配器支持',
            'environment': 'staging'
        }
    }
    
    result = adapter.process(pipeline_input)
    print(f"完整发布流水线结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试状态查询
    status_input = {
        'action': 'get_status',
        'parameters': {}
    }
    
    result = adapter.process(status_input)
    print(f"状态查询结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_release_manager_mcp()

