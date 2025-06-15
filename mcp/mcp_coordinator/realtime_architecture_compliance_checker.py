"""
PowerAutomation 实时架构合规性检查器

基于现有developer_dashboard系统，添加实时MCP架构合规性检测：
- 实时代码分析
- MCP通信规范验证
- 架构违规检测
- 自动修复建议
- 开发介入工作流触发

作者: PowerAutomation团队
版本: 1.0.0
日期: 2025-06-14
"""

import os
import sys
import ast
import json
import time
import asyncio
import logging
import threading
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import re
import subprocess

# 导入现有的开发者仪表板
sys.path.append('/home/ubuntu/powerauto.ai_0.53/developer_dashboard')
try:
    from dashboard_core import DeveloperDashboard
    from git_monitor_engine import GitMonitorEngine
except ImportError:
    # 如果导入失败，定义基础类
    class DeveloperDashboard:
        def __init__(self):
            self.logger = logging.getLogger("DeveloperDashboard")
    
    class GitMonitorEngine:
        def __init__(self):
            self.logger = logging.getLogger("GitMonitorEngine")

logger = logging.getLogger("architecture_compliance_checker")

class ViolationType(Enum):
    """违规类型"""
    DIRECT_MCP_IMPORT = "direct_mcp_import"           # 直接导入其他MCP
    DIRECT_MCP_CALL = "direct_mcp_call"               # 直接调用其他MCP方法
    BYPASS_COORDINATOR = "bypass_coordinator"         # 绕过MCPCoordinator
    HARDCODED_DEPENDENCY = "hardcoded_dependency"     # 硬编码依赖关系
    CIRCULAR_DEPENDENCY = "circular_dependency"       # 循环依赖
    UNAUTHORIZED_DATA_FLOW = "unauthorized_data_flow" # 未授权数据流

class SeverityLevel(Enum):
    """严重程度"""
    LOW = "low"           # 警告级别
    MEDIUM = "medium"     # 需要修复
    HIGH = "high"         # 必须修复
    CRITICAL = "critical" # 阻止提交

@dataclass
class ArchitectureViolation:
    """架构违规记录"""
    file_path: str
    line_number: int
    column: int
    violation_type: ViolationType
    severity: SeverityLevel
    message: str
    code_snippet: str
    suggested_fix: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "violation_type": self.violation_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "code_snippet": self.code_snippet,
            "suggested_fix": self.suggested_fix,
            "timestamp": self.timestamp.isoformat()
        }

class MCPArchitectureRules:
    """MCP架构规则定义"""
    
    def __init__(self):
        # 禁止的直接导入模式
        self.forbidden_imports = [
            r"from\s+.*_mcp\s+import",           # from xxx_mcp import
            r"import\s+.*_mcp(?:\s|$)",          # import xxx_mcp
            r"from\s+.*\..*_mcp\s+import",       # from path.xxx_mcp import
        ]
        
        # 禁止的直接调用模式
        self.forbidden_calls = [
            r"\w+_mcp\.\w+\(",                   # xxx_mcp.method()
            r"\w+_mcp\[\w+\]",                   # xxx_mcp[key]
            r"await\s+\w+_mcp\.\w+\(",           # await xxx_mcp.method()
        ]
        
        # 必须通过协调器的模式
        self.required_coordinator_patterns = [
            r"coordinator\.route_to_mcp\(",      # coordinator.route_to_mcp()
            r"coordinator\.send_message\(",      # coordinator.send_message()
            r"coordinator\.execute_task\(",      # coordinator.execute_task()
        ]
        
        # 允许的MCP名称（这些MCP可以被直接使用）
        self.allowed_direct_mcps = {
            "base_mcp",           # 基础MCP类
            "mcp_coordinator",    # 协调器本身
            "enhanced_mcp_coordinator"  # 增强协调器
        }

class RealTimeCodeAnalyzer:
    """实时代码分析器"""
    
    def __init__(self, rules: MCPArchitectureRules):
        self.rules = rules
        self.logger = logging.getLogger("RealTimeCodeAnalyzer")
        
    def analyze_file(self, file_path: str) -> List[ArchitectureViolation]:
        """分析单个文件的架构合规性"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 语法树分析
            try:
                tree = ast.parse(content)
                violations.extend(self._analyze_ast(tree, file_path, lines))
            except SyntaxError as e:
                # 语法错误时跳过AST分析，只进行正则分析
                self.logger.warning(f"语法错误，跳过AST分析: {file_path} - {e}")
            
            # 正则表达式分析
            violations.extend(self._analyze_with_regex(content, file_path, lines))
            
        except Exception as e:
            self.logger.error(f"分析文件失败: {file_path} - {e}")
        
        return violations
    
    def _analyze_ast(self, tree: ast.AST, file_path: str, lines: List[str]) -> List[ArchitectureViolation]:
        """使用AST分析代码"""
        violations = []
        
        class MCPViolationVisitor(ast.NodeVisitor):
            def __init__(self, analyzer, file_path, lines):
                self.analyzer = analyzer
                self.file_path = file_path
                self.lines = lines
                self.violations = []
            
            def visit_Import(self, node):
                """检查import语句"""
                for alias in node.names:
                    if self._is_forbidden_mcp_import(alias.name):
                        violation = ArchitectureViolation(
                            file_path=self.file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            violation_type=ViolationType.DIRECT_MCP_IMPORT,
                            severity=SeverityLevel.HIGH,
                            message=f"禁止直接导入MCP: {alias.name}",
                            code_snippet=self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else "",
                            suggested_fix=f"使用 coordinator.get_mcp('{alias.name}') 替代",
                            timestamp=datetime.now()
                        )
                        self.violations.append(violation)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                """检查from import语句"""
                if node.module and self._is_forbidden_mcp_import(node.module):
                    violation = ArchitectureViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        violation_type=ViolationType.DIRECT_MCP_IMPORT,
                        severity=SeverityLevel.HIGH,
                        message=f"禁止直接从MCP模块导入: {node.module}",
                        code_snippet=self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else "",
                        suggested_fix="通过MCPCoordinator获取MCP实例",
                        timestamp=datetime.now()
                    )
                    self.violations.append(violation)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                """检查函数调用"""
                # 检查是否是直接MCP调用
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        obj_name = node.func.value.id
                        if obj_name.endswith('_mcp') and obj_name not in self.analyzer.rules.allowed_direct_mcps:
                            violation = ArchitectureViolation(
                                file_path=self.file_path,
                                line_number=node.lineno,
                                column=node.col_offset,
                                violation_type=ViolationType.DIRECT_MCP_CALL,
                                severity=SeverityLevel.MEDIUM,
                                message=f"禁止直接调用MCP方法: {obj_name}.{node.func.attr}()",
                                code_snippet=self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else "",
                                suggested_fix=f"使用 coordinator.route_to_mcp('{obj_name}', '{node.func.attr}', args) 替代",
                                timestamp=datetime.now()
                            )
                            self.violations.append(violation)
                self.generic_visit(node)
            
            def _is_forbidden_mcp_import(self, module_name: str) -> bool:
                """检查是否是禁止的MCP导入"""
                if not module_name:
                    return False
                
                # 检查是否以_mcp结尾且不在允许列表中
                if module_name.endswith('_mcp') and module_name not in self.analyzer.rules.allowed_direct_mcps:
                    return True
                
                # 检查是否包含_mcp路径
                if '_mcp' in module_name and not any(allowed in module_name for allowed in self.analyzer.rules.allowed_direct_mcps):
                    return True
                
                return False
        
        visitor = MCPViolationVisitor(self, file_path, lines)
        visitor.visit(tree)
        violations.extend(visitor.violations)
        
        return violations
    
    def _analyze_with_regex(self, content: str, file_path: str, lines: List[str]) -> List[ArchitectureViolation]:
        """使用正则表达式分析代码"""
        violations = []
        
        # 检查禁止的导入模式
        for pattern in self.rules.forbidden_imports:
            for match in re.finditer(pattern, content, re.MULTILINE):
                line_num = content[:match.start()].count('\n') + 1
                violation = ArchitectureViolation(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()) - 1,
                    violation_type=ViolationType.DIRECT_MCP_IMPORT,
                    severity=SeverityLevel.HIGH,
                    message=f"检测到禁止的MCP导入模式: {match.group()}",
                    code_snippet=lines[line_num - 1] if line_num <= len(lines) else "",
                    suggested_fix="使用MCPCoordinator进行MCP访问",
                    timestamp=datetime.now()
                )
                violations.append(violation)
        
        # 检查禁止的调用模式
        for pattern in self.rules.forbidden_calls:
            for match in re.finditer(pattern, content, re.MULTILINE):
                line_num = content[:match.start()].count('\n') + 1
                violation = ArchitectureViolation(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start() - content.rfind('\n', 0, match.start()) - 1,
                    violation_type=ViolationType.DIRECT_MCP_CALL,
                    severity=SeverityLevel.MEDIUM,
                    message=f"检测到禁止的MCP直接调用: {match.group()}",
                    code_snippet=lines[line_num - 1] if line_num <= len(lines) else "",
                    suggested_fix="使用coordinator.route_to_mcp()进行调用",
                    timestamp=datetime.now()
                )
                violations.append(violation)
        
        return violations

class AutoFixSuggestionEngine:
    """自动修复建议引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger("AutoFixSuggestionEngine")
        
        # 修复模板
        self.fix_templates = {
            ViolationType.DIRECT_MCP_IMPORT: {
                "pattern": r"from\s+(\w+_mcp)\s+import\s+(\w+)",
                "replacement": "# 使用MCPCoordinator获取MCP实例\n# {original_var} = coordinator.get_mcp('{mcp_name}')"
            },
            ViolationType.DIRECT_MCP_CALL: {
                "pattern": r"(\w+_mcp)\.(\w+)\((.*?)\)",
                "replacement": "coordinator.route_to_mcp('{mcp_name}', '{method_name}', {args})"
            }
        }
    
    def generate_fix_suggestion(self, violation: ArchitectureViolation) -> Dict[str, Any]:
        """生成修复建议"""
        suggestion = {
            "violation_id": f"{violation.file_path}:{violation.line_number}",
            "auto_fixable": False,
            "fix_description": "",
            "code_changes": [],
            "additional_steps": []
        }
        
        if violation.violation_type == ViolationType.DIRECT_MCP_IMPORT:
            suggestion.update({
                "auto_fixable": True,
                "fix_description": "将直接MCP导入替换为通过MCPCoordinator获取",
                "code_changes": [
                    {
                        "line": violation.line_number,
                        "original": violation.code_snippet,
                        "replacement": self._generate_coordinator_import_fix(violation.code_snippet)
                    }
                ],
                "additional_steps": [
                    "确保MCPCoordinator已正确初始化",
                    "检查MCP名称是否正确注册"
                ]
            })
        
        elif violation.violation_type == ViolationType.DIRECT_MCP_CALL:
            suggestion.update({
                "auto_fixable": True,
                "fix_description": "将直接MCP调用替换为通过MCPCoordinator路由",
                "code_changes": [
                    {
                        "line": violation.line_number,
                        "original": violation.code_snippet,
                        "replacement": self._generate_coordinator_call_fix(violation.code_snippet)
                    }
                ],
                "additional_steps": [
                    "确保coordinator实例可用",
                    "验证MCP方法参数格式"
                ]
            })
        
        return suggestion
    
    def _generate_coordinator_import_fix(self, original_code: str) -> str:
        """生成协调器导入修复代码"""
        # 解析原始导入语句
        import_match = re.search(r"from\s+(\w+_mcp)\s+import\s+(\w+)", original_code)
        if import_match:
            mcp_name = import_match.group(1)
            imported_item = import_match.group(2)
            return f"# 通过MCPCoordinator获取MCP实例\n{imported_item} = coordinator.get_mcp('{mcp_name}')"
        
        return f"# 请使用coordinator.get_mcp()替代直接导入\n# {original_code}"
    
    def _generate_coordinator_call_fix(self, original_code: str) -> str:
        """生成协调器调用修复代码"""
        # 解析原始调用语句
        call_match = re.search(r"(\w+_mcp)\.(\w+)\((.*?)\)", original_code)
        if call_match:
            mcp_name = call_match.group(1)
            method_name = call_match.group(2)
            args = call_match.group(3)
            
            if args.strip():
                return f"coordinator.route_to_mcp('{mcp_name}', '{method_name}', {args})"
            else:
                return f"coordinator.route_to_mcp('{mcp_name}', '{method_name}')"
        
        return f"# 请使用coordinator.route_to_mcp()替代直接调用\n# {original_code}"

class RealTimeComplianceMonitor:
    """实时合规性监控器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rules = MCPArchitectureRules()
        self.analyzer = RealTimeCodeAnalyzer(self.rules)
        self.fix_engine = AutoFixSuggestionEngine()
        self.logger = logging.getLogger("RealTimeComplianceMonitor")
        
        # 监控状态
        self.is_monitoring = False
        self.monitored_files = set()
        self.violation_cache = {}
        self.file_watchers = {}
        
        # 统计信息
        self.stats = {
            "total_violations": 0,
            "fixed_violations": 0,
            "files_monitored": 0,
            "last_scan_time": None
        }
    
    async def start_monitoring(self):
        """启动实时监控"""
        self.is_monitoring = True
        self.logger.info("启动实时架构合规性监控")
        
        # 初始扫描
        await self._initial_scan()
        
        # 启动文件监控
        await self._start_file_watching()
    
    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        self.logger.info("停止实时架构合规性监控")
    
    async def _initial_scan(self):
        """初始扫描所有Python文件"""
        self.logger.info("开始初始架构合规性扫描")
        
        python_files = list(self.project_root.rglob("*.py"))
        self.stats["files_monitored"] = len(python_files)
        
        for file_path in python_files:
            if self._should_monitor_file(file_path):
                violations = self.analyzer.analyze_file(str(file_path))
                if violations:
                    self.violation_cache[str(file_path)] = violations
                    self.stats["total_violations"] += len(violations)
                    
                    # 记录违规
                    for violation in violations:
                        self.logger.warning(f"架构违规: {violation.message} in {violation.file_path}:{violation.line_number}")
        
        self.stats["last_scan_time"] = datetime.now()
        self.logger.info(f"初始扫描完成，发现 {self.stats['total_violations']} 个违规")
    
    async def _start_file_watching(self):
        """启动文件监控"""
        # 这里可以集成文件系统监控库如watchdog
        # 为了简化，我们使用定时检查
        while self.is_monitoring:
            await asyncio.sleep(2)  # 每2秒检查一次
            await self._check_file_changes()
    
    async def _check_file_changes(self):
        """检查文件变更"""
        for file_path in self.monitored_files.copy():
            if Path(file_path).exists():
                # 检查文件修改时间
                mtime = Path(file_path).stat().st_mtime
                if file_path not in self.file_watchers or self.file_watchers[file_path] < mtime:
                    self.file_watchers[file_path] = mtime
                    await self._analyze_file_change(file_path)
    
    async def _analyze_file_change(self, file_path: str):
        """分析文件变更"""
        violations = self.analyzer.analyze_file(file_path)
        
        # 更新违规缓存
        old_violations = self.violation_cache.get(file_path, [])
        self.violation_cache[file_path] = violations
        
        # 计算新增违规
        new_violations = [v for v in violations if v not in old_violations]
        if new_violations:
            self.logger.warning(f"检测到新的架构违规 in {file_path}: {len(new_violations)} 个")
            
            # 触发开发介入工作流
            await self._trigger_intervention_workflow(file_path, new_violations)
    
    async def _trigger_intervention_workflow(self, file_path: str, violations: List[ArchitectureViolation]):
        """触发开发介入工作流"""
        self.logger.info(f"触发开发介入工作流: {file_path}")
        
        for violation in violations:
            # 生成修复建议
            fix_suggestion = self.fix_engine.generate_fix_suggestion(violation)
            
            # 记录到开发者仪表板
            await self._report_to_dashboard(violation, fix_suggestion)
            
            # 如果是高严重性违规，阻止操作
            if violation.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                await self._block_operation(violation)
    
    async def _report_to_dashboard(self, violation: ArchitectureViolation, fix_suggestion: Dict[str, Any]):
        """报告到开发者仪表板"""
        report = {
            "type": "architecture_violation",
            "violation": violation.to_dict(),
            "fix_suggestion": fix_suggestion,
            "timestamp": datetime.now().isoformat()
        }
        
        # 这里可以集成到现有的dashboard_core系统
        self.logger.info(f"报告架构违规到仪表板: {violation.message}")
    
    async def _block_operation(self, violation: ArchitectureViolation):
        """阻止操作（高严重性违规）"""
        self.logger.error(f"阻止操作 - 严重架构违规: {violation.message}")
        
        # 可以集成到Git hooks或CI/CD系统
        # 例如：阻止提交、阻止构建等
    
    def _should_monitor_file(self, file_path: Path) -> bool:
        """判断是否应该监控该文件"""
        # 排除测试文件、临时文件等
        exclude_patterns = [
            "test_",
            "__pycache__",
            ".git",
            "venv",
            "node_modules"
        ]
        
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                return False
        
        # 只监控MCP相关文件
        if "_mcp" in str(file_path) or "coordinator" in str(file_path):
            self.monitored_files.add(str(file_path))
            return True
        
        return False
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """获取合规性报告"""
        total_files = len(self.monitored_files)
        violation_files = len([f for f in self.violation_cache if self.violation_cache[f]])
        compliance_rate = (total_files - violation_files) / total_files if total_files > 0 else 1.0
        
        return {
            "compliance_rate": f"{compliance_rate:.2%}",
            "total_files_monitored": total_files,
            "files_with_violations": violation_files,
            "total_violations": self.stats["total_violations"],
            "fixed_violations": self.stats["fixed_violations"],
            "last_scan_time": self.stats["last_scan_time"].isoformat() if self.stats["last_scan_time"] else None,
            "violation_summary": self._get_violation_summary()
        }
    
    def _get_violation_summary(self) -> Dict[str, int]:
        """获取违规汇总"""
        summary = {}
        for violations in self.violation_cache.values():
            for violation in violations:
                violation_type = violation.violation_type.value
                summary[violation_type] = summary.get(violation_type, 0) + 1
        return summary

class EnhancedDeveloperDashboard(DeveloperDashboard):
    """增强的开发者仪表板 - 集成架构合规性检查"""
    
    def __init__(self, project_root: str):
        super().__init__()
        self.compliance_monitor = RealTimeComplianceMonitor(project_root)
        self.logger = logging.getLogger("EnhancedDeveloperDashboard")
    
    async def initialize(self):
        """初始化增强仪表板"""
        # 初始化基础仪表板
        await super().initialize() if hasattr(super(), 'initialize') else None
        
        # 启动架构合规性监控
        await self.compliance_monitor.start_monitoring()
        
        self.logger.info("增强开发者仪表板初始化完成 - 架构合规性监控已启动")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        # 获取基础数据
        base_data = await super().get_dashboard_data() if hasattr(super(), 'get_dashboard_data') else {}
        
        # 添加架构合规性数据
        compliance_data = self.compliance_monitor.get_compliance_report()
        
        return {
            **base_data,
            "architecture_compliance": compliance_data,
            "real_time_monitoring": {
                "status": "active" if self.compliance_monitor.is_monitoring else "inactive",
                "monitored_files": len(self.compliance_monitor.monitored_files)
            }
        }

# 使用示例
async def main():
    """测试实时架构合规性检查"""
    project_root = "/home/ubuntu/powerauto.aicorenew"
    
    # 创建增强仪表板
    dashboard = EnhancedDeveloperDashboard(project_root)
    await dashboard.initialize()
    
    # 运行一段时间进行监控
    await asyncio.sleep(10)
    
    # 获取合规性报告
    report = dashboard.compliance_monitor.get_compliance_report()
    print("架构合规性报告:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

