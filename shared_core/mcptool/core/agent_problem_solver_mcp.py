#!/usr/bin/env python3
"""
AgentProblemSolver MCP适配器

此模块为AgentProblemSolver提供MCP协议合规的包装，解决初始化问题并提供统一接口。
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
    # 如果导入失败，创建一个简化的BaseMCP
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

# 尝试导入原始AgentProblemSolver
try:
    from mcptool.core.development_tools.agent_problem_solver import AgentProblemSolver
    AGENT_PROBLEM_SOLVER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AgentProblemSolver導入失敗: {e}")
    AGENT_PROBLEM_SOLVER_AVAILABLE = False
    
    # 创建Mock实现
    class AgentProblemSolver:
        def __init__(self, project_dir: str):
            self.project_dir = project_dir
            self.problems = []
            self.solutions = []
            
        def analyze_problem(self, problem_description: str, context: Dict = None):
            problem = {
                'id': len(self.problems) + 1,
                'description': problem_description,
                'context': context or {},
                'analysis': f"分析结果: {problem_description}",
                'severity': 'medium',
                'timestamp': datetime.now().isoformat()
            }
            self.problems.append(problem)
            return problem
            
        def solve_problem(self, problem_id: int):
            problem = next((p for p in self.problems if p['id'] == problem_id), None)
            if not problem:
                raise ValueError(f"问题不存在: {problem_id}")
            
            solution = {
                'id': len(self.solutions) + 1,
                'problem_id': problem_id,
                'solution': f"针对问题 {problem_id} 的解决方案",
                'steps': ["识别根本原因", "制定解决策略", "实施解决方案", "验证结果"],
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat()
            }
            self.solutions.append(solution)
            return solution

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_problem_solver_mcp")

class AgentProblemSolverMCP(BaseMCP):
    """AgentProblemSolver的MCP包装器"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(name="AgentProblemSolverMCP")
        
        # 解析配置
        config = config or {}
        project_dir = config.get('project_dir', '/home/ubuntu/powerautomation')
        
        # 修复初始化问题 - 提供默认project_dir
        try:
            self.problem_solver = AgentProblemSolver(project_dir)
            self.is_available = AGENT_PROBLEM_SOLVER_AVAILABLE
        except Exception as e:
            self.logger.error(f"AgentProblemSolver初始化失败: {e}")
            self.problem_solver = None
            self.is_available = False
        
        # 初始化指标
        self.metrics = {
            'execution_count': 0,
            'success_count': 0,
            'error_count': 0,
            'total_execution_time': 0,
            'problems_analyzed': 0,
            'problems_solved': 0
        }
        
        self.logger.info(f"AgentProblemSolver MCP适配器初始化完成，可用性: {self.is_available}")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP协议标准处理方法"""
        start_time = datetime.now()
        
        try:
            # 1. 输入验证
            if not self.validate_input(input_data):
                return self._create_error_response("输入验证失败", "INVALID_INPUT")
            
            # 2. 检查适配器可用性
            if not self.is_available:
                return self._create_error_response("AgentProblemSolver不可用", "ADAPTER_UNAVAILABLE")
            
            # 3. 解析操作类型
            action = input_data.get('action', 'analyze_problem')
            parameters = input_data.get('parameters', {})
            
            # 4. 执行相应操作
            if action == 'analyze_problem':
                result = self._analyze_problem(parameters)
            elif action == 'solve_problem':
                result = self._solve_problem(parameters)
            elif action == 'get_problem_history':
                result = self._get_problem_history(parameters)
            elif action == 'get_solution_history':
                result = self._get_solution_history(parameters)
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
            
            self.logger.error(f"AgentProblemSolver执行失败: {str(e)}")
            return self._create_error_response(str(e), "EXECUTION_ERROR")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        
        action = input_data.get('action', 'analyze_problem')
        parameters = input_data.get('parameters', {})
        
        # 验证必需参数
        if action == 'analyze_problem':
            return 'problem_description' in parameters
        elif action == 'solve_problem':
            return 'problem_id' in parameters
        elif action in ['get_problem_history', 'get_solution_history', 'get_capabilities', 'get_status']:
            return True
        else:
            return False
    
    def get_capabilities(self) -> List[str]:
        """获取适配器能力列表"""
        return [
            "problem_analysis",
            "automated_solution",
            "supermemory_integration",
            "solution_tracking",
            "proactive_monitoring",
            "context_awareness",
            "confidence_scoring",
            "history_management"
        ]
    
    def _analyze_problem(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """分析问题"""
        problem_description = parameters.get('problem_description', '')
        context = parameters.get('context', {})
        
        if self.problem_solver and hasattr(self.problem_solver, 'analyze_problem'):
            result = self.problem_solver.analyze_problem(problem_description, context)
        else:
            # Mock实现
            result = {
                'id': self.metrics['problems_analyzed'] + 1,
                'description': problem_description,
                'context': context,
                'analysis': f"分析结果: {problem_description}",
                'severity': 'medium',
                'category': 'general',
                'timestamp': datetime.now().isoformat()
            }
        
        self.metrics['problems_analyzed'] += 1
        
        return {
            'action': 'analyze_problem',
            'problem': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _solve_problem(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """解决问题"""
        problem_id = parameters.get('problem_id')
        
        if self.problem_solver and hasattr(self.problem_solver, 'solve_problem'):
            result = self.problem_solver.solve_problem(problem_id)
        else:
            # Mock实现
            result = {
                'id': self.metrics['problems_solved'] + 1,
                'problem_id': problem_id,
                'solution': f"针对问题 {problem_id} 的解决方案",
                'steps': ["识别根本原因", "制定解决策略", "实施解决方案", "验证结果"],
                'confidence': 0.85,
                'timestamp': datetime.now().isoformat()
            }
        
        self.metrics['problems_solved'] += 1
        
        return {
            'action': 'solve_problem',
            'solution': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_problem_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取问题历史"""
        limit = parameters.get('limit', 10)
        
        if self.problem_solver and hasattr(self.problem_solver, 'problems'):
            problems = self.problem_solver.problems[-limit:]
        else:
            problems = []
        
        return {
            'action': 'get_problem_history',
            'problems': problems,
            'total_count': len(problems),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_solution_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """获取解决方案历史"""
        limit = parameters.get('limit', 10)
        
        if self.problem_solver and hasattr(self.problem_solver, 'solutions'):
            solutions = self.problem_solver.solutions[-limit:]
        else:
            solutions = []
        
        return {
            'action': 'get_solution_history',
            'solutions': solutions,
            'total_count': len(solutions),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            'action': 'get_status',
            'status': {
                'is_available': self.is_available,
                'problems_analyzed': self.metrics['problems_analyzed'],
                'problems_solved': self.metrics['problems_solved'],
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
            'problems_analyzed': self.metrics['problems_analyzed'],
            'problems_solved': self.metrics['problems_solved'],
            'availability': self.is_available
        }

def test_agent_problem_solver_mcp():
    """测试AgentProblemSolver MCP适配器"""
    print("=== 测试AgentProblemSolver MCP适配器 ===")
    
    # 创建适配器实例
    config = {'project_dir': '/home/ubuntu/powerautomation'}
    adapter = AgentProblemSolverMCP(config)
    
    # 测试问题分析
    analyze_input = {
        'action': 'analyze_problem',
        'parameters': {
            'problem_description': '系统响应缓慢，用户体验差',
            'context': {
                'environment': 'production',
                'severity': 'high',
                'affected_users': 1000
            }
        }
    }
    
    result = adapter.process(analyze_input)
    print(f"问题分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 获取问题ID
    if result['status'] == 'success':
        problem_id = result['data']['result']['problem']['id']
        
        # 测试问题解决
        solve_input = {
            'action': 'solve_problem',
            'parameters': {
                'problem_id': problem_id
            }
        }
        
        result = adapter.process(solve_input)
        print(f"问题解决结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试状态查询
    status_input = {
        'action': 'get_status',
        'parameters': {}
    }
    
    result = adapter.process(status_input)
    print(f"状态查询结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 测试能力查询
    capabilities_input = {
        'action': 'get_capabilities',
        'parameters': {}
    }
    
    result = adapter.process(capabilities_input)
    print(f"能力查询结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_agent_problem_solver_mcp()

