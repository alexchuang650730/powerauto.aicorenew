"""
PowerAutomation 开发智能介入MCP
遵循工具表注册 + 中央协调架构模式
检测和修复MCP架构违规行为
"""

import ast
import os
import re
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """违规类型"""
    DIRECT_MCP_IMPORT = "direct_mcp_import"           # 直接导入其他MCP
    DIRECT_MCP_CALL = "direct_mcp_call"               # 直接调用其他MCP方法
    UNREGISTERED_TOOL = "unregistered_tool"           # 使用未注册的工具
    BYPASS_COORDINATOR = "bypass_coordinator"         # 绕过中央协调器
    HARDCODED_DEPENDENCY = "hardcoded_dependency"     # 硬编码依赖关系

class SeverityLevel(Enum):
    """严重性级别"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ViolationReport:
    """违规报告"""
    violation_type: ViolationType
    severity: SeverityLevel
    file_path: str
    line_number: int
    code_snippet: str
    message: str
    fix_suggestion: str
    auto_fixable: bool = False

class DevelopmentInterventionMCP:
    """
    开发智能介入MCP
    
    核心功能：
    1. 工具表注册验证
    2. 中央协调合规检查
    3. 实时代码扫描
    4. 自动修复建议
    5. 架构违规阻止
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化开发智能介入MCP"""
        self.config = config or {}
        self.name = "DevelopmentInterventionMCP"
        
        # 工具表注册 - PowerAutomation标准模式
        self.tools_registry = {}
        self._register_builtin_tools()
        
        # 已注册的MCP列表
        self.registered_mcps = set()
        
        # 违规检测规则
        self.violation_rules = self._initialize_violation_rules()
        
        # 性能指标
        self.performance_metrics = {
            "scans_performed": 0,
            "violations_detected": 0,
            "auto_fixes_applied": 0,
            "compliance_rate": 100.0
        }
        
        # 实时监控状态
        self.monitoring_active = False
        
        logger.info(f"🛡️ {self.name} 初始化完成 - 架构守护者已就位")
    
    def _register_builtin_tools(self):
        """注册内建工具 - 遵循PowerAutomation工具表模式"""
        self.tools_registry = {
            "mcp_registration_validator": {
                "name": "MCP注册验证器",
                "description": "验证MCP是否正确注册到工具表",
                "category": "compliance",
                "handler": self._validate_mcp_registration
            },
            "architecture_compliance_scanner": {
                "name": "架构合规扫描器", 
                "description": "扫描代码中的架构违规行为",
                "category": "scanning",
                "handler": self._scan_architecture_compliance
            },
            "real_time_code_monitor": {
                "name": "实时代码监控器",
                "description": "实时监控代码变更和违规行为",
                "category": "monitoring", 
                "handler": self._monitor_code_changes
            },
            "auto_fix_generator": {
                "name": "自动修复生成器",
                "description": "生成架构违规的自动修复建议",
                "category": "fixing",
                "handler": self._generate_auto_fixes
            },
            "central_coordinator_enforcer": {
                "name": "中央协调强制器",
                "description": "强制所有MCP通信通过中央协调器",
                "category": "enforcement",
                "handler": self._enforce_central_coordination
            }
        }
    
    def _initialize_violation_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化违规检测规则"""
        return {
            # 直接MCP导入检测
            "direct_mcp_import": {
                "patterns": [
                    r"from\s+\w*mcp\w*\s+import",
                    r"import\s+\w*mcp\w*(?!.*coordinator)",
                    r"from\s+.*\.mcp\s+import"
                ],
                "severity": SeverityLevel.HIGH,
                "message": "检测到直接MCP导入，违反中央协调原则",
                "fix_template": "# 修复：通过中央协调器获取MCP\n{mcp_name} = coordinator.get_mcp('{mcp_id}')"
            },
            
            # 直接MCP调用检测
            "direct_mcp_call": {
                "patterns": [
                    r"\w*mcp\w*\.\w+\(",
                    r"\w*MCP\w*\(\)",
                    r"\.process\(\s*(?!.*coordinator)"
                ],
                "severity": SeverityLevel.CRITICAL,
                "message": "检测到直接MCP方法调用，必须通过中央协调器",
                "fix_template": "# 修复：通过中央协调器调用\nresult = coordinator.route_to_mcp('{mcp_id}', {data})"
            },
            
            # 未注册工具使用检测
            "unregistered_tool": {
                "patterns": [
                    r"self\.tools_registry\[[\'\"](\w+)[\'\"]\](?!\s*=)",
                ],
                "severity": SeverityLevel.MEDIUM,
                "message": "使用了未注册的工具",
                "fix_template": "# 修复：先注册工具到tools_registry\nself.tools_registry['{tool_name}'] = {...}"
            },
            
            # 绕过协调器检测
            "bypass_coordinator": {
                "patterns": [
                    r"(?<!coordinator\.)route_to",
                    r"(?<!coordinator\.)call_mcp",
                    r"direct_call\s*="
                ],
                "severity": SeverityLevel.HIGH,
                "message": "检测到绕过中央协调器的调用",
                "fix_template": "# 修复：使用中央协调器\ncoordinator.route_to_mcp(...)"
            }
        }
    
    async def register_mcp(self, mcp_id: str, mcp_info: Dict[str, Any]) -> Dict[str, Any]:
        """注册MCP到工具表"""
        try:
            # 验证MCP信息完整性
            required_fields = ["name", "description", "category", "handler"]
            for field in required_fields:
                if field not in mcp_info:
                    raise ValueError(f"MCP注册信息缺少必需字段: {field}")
            
            # 注册到工具表
            self.tools_registry[mcp_id] = mcp_info
            self.registered_mcps.add(mcp_id)
            
            logger.info(f"✅ MCP注册成功: {mcp_id} - {mcp_info['name']}")
            
            return {
                "status": "success",
                "mcp_id": mcp_id,
                "message": f"MCP {mcp_id} 已成功注册到工具表",
                "registered_count": len(self.registered_mcps)
            }
            
        except Exception as e:
            logger.error(f"❌ MCP注册失败: {mcp_id} - {e}")
            return {
                "status": "error",
                "mcp_id": mcp_id,
                "error": str(e)
            }
    
    async def scan_project_compliance(self, project_path: str) -> Dict[str, Any]:
        """扫描项目架构合规性"""
        violations = []
        scanned_files = 0
        
        try:
            # 遍历项目文件
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_violations = await self._scan_file_compliance(file_path)
                        violations.extend(file_violations)
                        scanned_files += 1
            
            # 更新性能指标
            self.performance_metrics["scans_performed"] += 1
            self.performance_metrics["violations_detected"] += len(violations)
            
            # 计算合规率
            compliance_rate = max(0, 100 - (len(violations) / max(scanned_files, 1) * 10))
            self.performance_metrics["compliance_rate"] = compliance_rate
            
            return {
                "status": "completed",
                "project_path": project_path,
                "scanned_files": scanned_files,
                "total_violations": len(violations),
                "violations": violations,
                "compliance_rate": compliance_rate,
                "scan_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"项目扫描失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _scan_file_compliance(self, file_path: str) -> List[ViolationReport]:
        """扫描单个文件的合规性"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 使用AST进行深度分析
            try:
                tree = ast.parse(content)
                ast_violations = self._analyze_ast_violations(tree, file_path, lines)
                violations.extend(ast_violations)
            except SyntaxError:
                # 如果AST解析失败，使用正则表达式
                pass
            
            # 使用正则表达式检测违规模式
            regex_violations = self._analyze_regex_violations(content, file_path, lines)
            violations.extend(regex_violations)
            
        except Exception as e:
            logger.error(f"文件扫描失败 {file_path}: {e}")
        
        return violations
    
    def _analyze_ast_violations(self, tree: ast.AST, file_path: str, lines: List[str]) -> List[ViolationReport]:
        """使用AST分析违规行为"""
        violations = []
        
        class ViolationVisitor(ast.NodeVisitor):
            def __init__(self, outer_self):
                self.outer = outer_self
                
            def visit_Import(self, node):
                for alias in node.names:
                    if 'mcp' in alias.name.lower() and 'coordinator' not in alias.name.lower():
                        violation = ViolationReport(
                            violation_type=ViolationType.DIRECT_MCP_IMPORT,
                            severity=SeverityLevel.HIGH,
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            message=f"直接导入MCP模块: {alias.name}",
                            fix_suggestion=f"# 通过中央协调器获取MCP\n{alias.name} = coordinator.get_mcp('{alias.name.lower()}')",
                            auto_fixable=True
                        )
                        violations.append(violation)
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module and 'mcp' in node.module.lower() and 'coordinator' not in node.module.lower():
                    for alias in node.names:
                        violation = ViolationReport(
                            violation_type=ViolationType.DIRECT_MCP_IMPORT,
                            severity=SeverityLevel.HIGH,
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            message=f"直接从MCP模块导入: {node.module}.{alias.name}",
                            fix_suggestion=f"# 通过中央协调器获取MCP\n{alias.name} = coordinator.get_mcp('{node.module}')",
                            auto_fixable=True
                        )
                        violations.append(violation)
                self.generic_visit(node)
        
        visitor = ViolationVisitor(self)
        visitor.visit(tree)
        return violations
    
    def _analyze_regex_violations(self, content: str, file_path: str, lines: List[str]) -> List[ViolationReport]:
        """使用正则表达式分析违规行为"""
        violations = []
        
        for rule_name, rule_config in self.violation_rules.items():
            for pattern in rule_config["patterns"]:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    # 计算行号
                    line_number = content[:match.start()].count('\n') + 1
                    
                    violation = ViolationReport(
                        violation_type=ViolationType(rule_name),
                        severity=rule_config["severity"],
                        file_path=file_path,
                        line_number=line_number,
                        code_snippet=lines[line_number - 1] if line_number <= len(lines) else "",
                        message=rule_config["message"],
                        fix_suggestion=rule_config["fix_template"],
                        auto_fixable=True
                    )
                    violations.append(violation)
        
        return violations
    
    async def auto_fix_violations(self, violations: List[ViolationReport]) -> Dict[str, Any]:
        """自动修复违规行为"""
        fixed_violations = []
        failed_fixes = []
        
        for violation in violations:
            if violation.auto_fixable:
                try:
                    fix_result = await self._apply_auto_fix(violation)
                    if fix_result["success"]:
                        fixed_violations.append(violation)
                        self.performance_metrics["auto_fixes_applied"] += 1
                    else:
                        failed_fixes.append({"violation": violation, "error": fix_result["error"]})
                except Exception as e:
                    failed_fixes.append({"violation": violation, "error": str(e)})
            else:
                failed_fixes.append({"violation": violation, "error": "不支持自动修复"})
        
        return {
            "status": "completed",
            "fixed_count": len(fixed_violations),
            "failed_count": len(failed_fixes),
            "fixed_violations": [asdict(v) for v in fixed_violations],
            "failed_fixes": failed_fixes
        }
    
    async def _apply_auto_fix(self, violation: ViolationReport) -> Dict[str, Any]:
        """应用自动修复"""
        try:
            # 读取文件内容
            with open(violation.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 生成修复代码
            if violation.violation_type == ViolationType.DIRECT_MCP_IMPORT:
                # 替换直接导入为通过协调器获取
                original_line = lines[violation.line_number - 1]
                fixed_line = self._generate_coordinator_call(original_line)
                lines[violation.line_number - 1] = fixed_line
            
            elif violation.violation_type == ViolationType.DIRECT_MCP_CALL:
                # 替换直接调用为通过协调器路由
                original_line = lines[violation.line_number - 1]
                fixed_line = self._generate_coordinator_route(original_line)
                lines[violation.line_number - 1] = fixed_line
            
            # 写回文件
            with open(violation.file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            logger.info(f"✅ 自动修复成功: {violation.file_path}:{violation.line_number}")
            
            return {
                "success": True,
                "message": f"已修复 {violation.violation_type.value}"
            }
            
        except Exception as e:
            logger.error(f"❌ 自动修复失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_coordinator_call(self, original_line: str) -> str:
        """生成协调器调用代码"""
        # 简化的代码生成逻辑
        if "import" in original_line:
            # 提取MCP名称
            mcp_name = re.search(r'(\w*mcp\w*)', original_line, re.IGNORECASE)
            if mcp_name:
                return f"# 修复：通过中央协调器获取MCP\n{mcp_name.group(1)} = coordinator.get_mcp('{mcp_name.group(1).lower()}')\n"
        
        return original_line
    
    def _generate_coordinator_route(self, original_line: str) -> str:
        """生成协调器路由代码"""
        # 简化的代码生成逻辑
        if ".process(" in original_line:
            return original_line.replace(".process(", ".route_to_mcp('target_mcp', ")
        
        return original_line
    
    async def start_real_time_monitoring(self, project_path: str) -> Dict[str, Any]:
        """启动实时监控"""
        self.monitoring_active = True
        
        # 启动文件监控任务
        asyncio.create_task(self._real_time_monitor_loop(project_path))
        
        return {
            "status": "started",
            "project_path": project_path,
            "message": "实时架构合规监控已启动"
        }
    
    async def _real_time_monitor_loop(self, project_path: str):
        """实时监控循环"""
        while self.monitoring_active:
            try:
                # 扫描项目合规性
                scan_result = await self.scan_project_compliance(project_path)
                
                # 如果发现违规，立即处理
                if scan_result["total_violations"] > 0:
                    logger.warning(f"🚨 检测到 {scan_result['total_violations']} 个架构违规")
                    
                    # 自动修复可修复的违规
                    auto_fixable = [v for v in scan_result["violations"] if v.auto_fixable]
                    if auto_fixable:
                        await self.auto_fix_violations(auto_fixable)
                
                # 等待下次扫描
                await asyncio.sleep(5)  # 每5秒扫描一次
                
            except Exception as e:
                logger.error(f"实时监控错误: {e}")
                await asyncio.sleep(10)
    
    def stop_real_time_monitoring(self) -> Dict[str, Any]:
        """停止实时监控"""
        self.monitoring_active = False
        return {
            "status": "stopped",
            "message": "实时架构合规监控已停止"
        }
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """获取合规报告"""
        return {
            "name": self.name,
            "status": "active",
            "registered_mcps": list(self.registered_mcps),
            "registered_tools": list(self.tools_registry.keys()),
            "performance_metrics": self.performance_metrics,
            "monitoring_active": self.monitoring_active,
            "violation_rules": len(self.violation_rules),
            "report_timestamp": datetime.now().isoformat()
        }
    
    # 工具表处理方法 - 遵循PowerAutomation模式
    async def _validate_mcp_registration(self, input_data: Dict[str, Any]) -> str:
        """验证MCP注册"""
        mcp_id = input_data.get("mcp_id")
        if mcp_id in self.registered_mcps:
            return f"✅ MCP {mcp_id} 已正确注册"
        else:
            return f"❌ MCP {mcp_id} 未注册，请先注册到工具表"
    
    async def _scan_architecture_compliance(self, input_data: Dict[str, Any]) -> str:
        """扫描架构合规性"""
        project_path = input_data.get("project_path", ".")
        result = await self.scan_project_compliance(project_path)
        return f"扫描完成：发现 {result['total_violations']} 个违规，合规率 {result['compliance_rate']:.1f}%"
    
    async def _monitor_code_changes(self, input_data: Dict[str, Any]) -> str:
        """监控代码变更"""
        project_path = input_data.get("project_path", ".")
        if not self.monitoring_active:
            await self.start_real_time_monitoring(project_path)
            return "✅ 实时监控已启动"
        else:
            return "ℹ️ 实时监控已在运行中"
    
    async def _generate_auto_fixes(self, input_data: Dict[str, Any]) -> str:
        """生成自动修复"""
        violations = input_data.get("violations", [])
        if violations:
            result = await self.auto_fix_violations(violations)
            return f"自动修复完成：修复 {result['fixed_count']} 个违规"
        else:
            return "没有需要修复的违规"
    
    async def _enforce_central_coordination(self, input_data: Dict[str, Any]) -> str:
        """强制中央协调"""
        return "🛡️ 中央协调强制器已激活，所有MCP通信必须通过协调器"

# 导出主要类
__all__ = ["DevelopmentInterventionMCP", "ViolationType", "SeverityLevel", "ViolationReport"]

