"""
AgentProblemSolver 核心模塊

智能問題分析和解決方案生成器
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentProblemSolver:
    """智能問題解決器"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.problems = []
        self.solutions = []
        self.analysis_history = []
        
        # 問題分類
        self.problem_categories = {
            "technical": "技術問題",
            "performance": "性能問題", 
            "integration": "集成問題",
            "configuration": "配置問題",
            "dependency": "依賴問題",
            "logic": "邏輯問題",
            "data": "數據問題",
            "security": "安全問題"
        }
        
        logger.info(f"AgentProblemSolver初始化完成，項目目錄: {project_dir}")
    
    def analyze_problem(self, problem_description: str, context: Dict = None) -> Dict[str, Any]:
        """分析問題並生成詳細報告"""
        context = context or {}
        
        # 問題分析
        analysis = {
            'id': len(self.problems) + 1,
            'description': problem_description,
            'context': context,
            'category': self._categorize_problem(problem_description),
            'severity': self._assess_severity(problem_description, context),
            'root_causes': self._identify_root_causes(problem_description, context),
            'impact_analysis': self._analyze_impact(problem_description, context),
            'complexity_score': self._calculate_complexity(problem_description, context),
            'timestamp': datetime.now().isoformat(),
            'analysis_version': "1.0"
        }
        
        self.problems.append(analysis)
        self.analysis_history.append({
            'problem_id': analysis['id'],
            'action': 'analyze',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"問題分析完成: {analysis['id']} - {analysis['category']}")
        return analysis
    
    def solve_problem(self, problem_id: int) -> Dict[str, Any]:
        """為指定問題生成解決方案"""
        problem = next((p for p in self.problems if p['id'] == problem_id), None)
        if not problem:
            raise ValueError(f"問題不存在: {problem_id}")
        
        # 生成解決方案
        solution = {
            'id': len(self.solutions) + 1,
            'problem_id': problem_id,
            'solution_type': self._determine_solution_type(problem),
            'solution_steps': self._generate_solution_steps(problem),
            'implementation_plan': self._create_implementation_plan(problem),
            'risk_assessment': self._assess_solution_risks(problem),
            'success_criteria': self._define_success_criteria(problem),
            'estimated_effort': self._estimate_effort(problem),
            'confidence': self._calculate_confidence(problem),
            'alternatives': self._generate_alternatives(problem),
            'timestamp': datetime.now().isoformat()
        }
        
        self.solutions.append(solution)
        self.analysis_history.append({
            'problem_id': problem_id,
            'solution_id': solution['id'],
            'action': 'solve',
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"解決方案生成完成: {solution['id']} for 問題 {problem_id}")
        return solution
    
    def _categorize_problem(self, description: str) -> str:
        """問題分類"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['import', 'module', 'dependency', '依賴']):
            return "dependency"
        elif any(keyword in description_lower for keyword in ['performance', 'slow', '性能', '緩慢']):
            return "performance"
        elif any(keyword in description_lower for keyword in ['config', 'setting', '配置']):
            return "configuration"
        elif any(keyword in description_lower for keyword in ['integration', 'api', '集成']):
            return "integration"
        elif any(keyword in description_lower for keyword in ['security', 'auth', '安全', '認證']):
            return "security"
        elif any(keyword in description_lower for keyword in ['data', 'database', '數據']):
            return "data"
        elif any(keyword in description_lower for keyword in ['logic', 'algorithm', '邏輯', '算法']):
            return "logic"
        else:
            return "technical"
    
    def _assess_severity(self, description: str, context: Dict) -> str:
        """評估問題嚴重程度"""
        severity_keywords = {
            'critical': ['crash', 'fail', 'error', '崩潰', '失敗', '錯誤'],
            'high': ['slow', 'timeout', '緩慢', '超時'],
            'medium': ['warning', 'issue', '警告', '問題'],
            'low': ['minor', 'cosmetic', '輕微', '外觀']
        }
        
        description_lower = description.lower()
        
        for severity, keywords in severity_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return severity
        
        return 'medium'
    
    def _identify_root_causes(self, description: str, context: Dict) -> List[str]:
        """識別根本原因"""
        causes = []
        description_lower = description.lower()
        
        if 'import' in description_lower or 'module' in description_lower:
            causes.append("模塊導入路徑問題")
            causes.append("依賴包未安裝")
        
        if 'path' in description_lower:
            causes.append("文件路徑配置錯誤")
        
        if 'config' in description_lower:
            causes.append("配置文件錯誤")
        
        if not causes:
            causes.append("需要進一步調查")
        
        return causes
    
    def _analyze_impact(self, description: str, context: Dict) -> Dict[str, Any]:
        """分析影響範圍"""
        return {
            'affected_components': self._identify_affected_components(description),
            'user_impact': self._assess_user_impact(description),
            'system_impact': self._assess_system_impact(description),
            'business_impact': self._assess_business_impact(description)
        }
    
    def _calculate_complexity(self, description: str, context: Dict) -> float:
        """計算問題複雜度 (0-1)"""
        complexity_factors = 0
        
        if len(description) > 100:
            complexity_factors += 0.2
        
        if 'multiple' in description.lower() or '多個' in description:
            complexity_factors += 0.3
        
        if 'integration' in description.lower() or '集成' in description:
            complexity_factors += 0.3
        
        if context and len(context) > 3:
            complexity_factors += 0.2
        
        return min(1.0, complexity_factors)
    
    def _determine_solution_type(self, problem: Dict) -> str:
        """確定解決方案類型"""
        category = problem['category']
        
        solution_types = {
            'dependency': 'installation_fix',
            'configuration': 'config_update',
            'performance': 'optimization',
            'integration': 'api_fix',
            'security': 'security_patch',
            'data': 'data_migration',
            'logic': 'algorithm_improvement',
            'technical': 'code_refactor'
        }
        
        return solution_types.get(category, 'general_fix')
    
    def _generate_solution_steps(self, problem: Dict) -> List[str]:
        """生成解決步驟"""
        category = problem['category']
        
        if category == 'dependency':
            return [
                "檢查依賴包是否已安裝",
                "驗證導入路徑是否正確",
                "安裝缺失的依賴包",
                "更新sys.path配置",
                "測試導入是否成功"
            ]
        elif category == 'configuration':
            return [
                "檢查配置文件語法",
                "驗證配置參數有效性",
                "備份原始配置",
                "應用新配置",
                "重啟相關服務"
            ]
        else:
            return [
                "識別問題根本原因",
                "制定解決策略",
                "實施解決方案",
                "驗證修復效果",
                "監控系統穩定性"
            ]
    
    def _create_implementation_plan(self, problem: Dict) -> Dict[str, Any]:
        """創建實施計劃"""
        return {
            'phases': [
                {'name': '準備階段', 'duration': '30分鐘', 'tasks': ['環境檢查', '備份數據']},
                {'name': '實施階段', 'duration': '1小時', 'tasks': ['執行修復', '測試驗證']},
                {'name': '驗證階段', 'duration': '30分鐘', 'tasks': ['功能測試', '性能檢查']}
            ],
            'total_duration': '2小時',
            'resources_needed': ['開發環境', '測試數據', '備份空間'],
            'rollback_plan': '如果修復失敗，恢復備份並回滾更改'
        }
    
    def _assess_solution_risks(self, problem: Dict) -> List[Dict[str, Any]]:
        """評估解決方案風險"""
        return [
            {
                'risk': '修復可能引入新問題',
                'probability': 'medium',
                'impact': 'medium',
                'mitigation': '充分測試和備份'
            },
            {
                'risk': '系統停機時間',
                'probability': 'low',
                'impact': 'high',
                'mitigation': '在維護窗口執行'
            }
        ]
    
    def _define_success_criteria(self, problem: Dict) -> List[str]:
        """定義成功標準"""
        return [
            "問題症狀完全消失",
            "系統功能正常運行",
            "性能指標達到預期",
            "無新問題引入",
            "用戶滿意度提升"
        ]
    
    def _estimate_effort(self, problem: Dict) -> Dict[str, Any]:
        """估算工作量"""
        complexity = problem.get('complexity_score', 0.5)
        
        if complexity < 0.3:
            effort_level = 'low'
            hours = '1-2小時'
        elif complexity < 0.7:
            effort_level = 'medium'
            hours = '2-4小時'
        else:
            effort_level = 'high'
            hours = '4-8小時'
        
        return {
            'level': effort_level,
            'estimated_hours': hours,
            'complexity_factor': complexity,
            'skill_level_required': 'intermediate' if complexity > 0.5 else 'basic'
        }
    
    def _calculate_confidence(self, problem: Dict) -> float:
        """計算解決方案信心度"""
        base_confidence = 0.7
        
        # 根據問題類別調整信心度
        category_confidence = {
            'dependency': 0.9,
            'configuration': 0.85,
            'performance': 0.7,
            'integration': 0.6,
            'security': 0.65,
            'data': 0.75,
            'logic': 0.6,
            'technical': 0.7
        }
        
        category = problem.get('category', 'technical')
        return category_confidence.get(category, base_confidence)
    
    def _generate_alternatives(self, problem: Dict) -> List[Dict[str, Any]]:
        """生成替代方案"""
        return [
            {
                'name': '快速修復',
                'description': '臨時解決方案，快速恢復功能',
                'pros': ['快速實施', '風險較低'],
                'cons': ['可能不是根本解決', '需要後續優化']
            },
            {
                'name': '完整重構',
                'description': '從根本上重新設計解決方案',
                'pros': ['徹底解決問題', '提升系統質量'],
                'cons': ['耗時較長', '風險較高']
            }
        ]
    
    def _identify_affected_components(self, description: str) -> List[str]:
        """識別受影響的組件"""
        components = []
        if 'adapter' in description.lower():
            components.append('適配器系統')
        if 'mcp' in description.lower():
            components.append('MCP協議')
        if 'api' in description.lower():
            components.append('API接口')
        return components or ['核心系統']
    
    def _assess_user_impact(self, description: str) -> str:
        """評估用戶影響"""
        if any(keyword in description.lower() for keyword in ['crash', 'fail', '崩潰']):
            return 'high'
        elif any(keyword in description.lower() for keyword in ['slow', '緩慢']):
            return 'medium'
        else:
            return 'low'
    
    def _assess_system_impact(self, description: str) -> str:
        """評估系統影響"""
        if 'system' in description.lower() or '系統' in description:
            return 'high'
        else:
            return 'medium'
    
    def _assess_business_impact(self, description: str) -> str:
        """評估業務影響"""
        return 'medium'  # 默認中等影響
    
    def get_problem_summary(self) -> Dict[str, Any]:
        """獲取問題總結"""
        return {
            'total_problems': len(self.problems),
            'total_solutions': len(self.solutions),
            'categories': {cat: len([p for p in self.problems if p.get('category') == cat]) 
                          for cat in self.problem_categories.keys()},
            'severity_distribution': {sev: len([p for p in self.problems if p.get('severity') == sev]) 
                                    for sev in ['low', 'medium', 'high', 'critical']},
            'average_confidence': sum(s.get('confidence', 0) for s in self.solutions) / max(len(self.solutions), 1)
        }

