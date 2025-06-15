"""
MCP头脑风暴器模块 - MCPBrainstorm

负责处理MCPPlanner没有的工具类型，自进化产生新工具并进行端到端测试。
"""

import os
import sys
import json
import importlib
import inspect
from datetime import datetime
from ..development_tools.thought_action_recorder import ThoughtActionRecorder
from ..development_tools.agent_problem_solver import AgentProblemSolver

class MCPBrainstorm:
    def __init__(self):
        """初始化MCP头脑风暴器"""
        self.recorder = ThoughtActionRecorder()
        self.problem_solver = AgentProblemSolver()
        
        # 新工具注册表
        self.new_tools_registry = {}
        
        # 工具模板库
        self.tool_templates = {}
        self._load_tool_templates()
        
        # 会话ID
        self.session_id = None
        
        # 能力分析器
        self.capability_analyzer = self._create_capability_analyzer()
    
    def _load_tool_templates(self):
        """加载工具模板库"""
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith('.py'):
                    template_name = filename[:-3]
                    template_path = os.path.join(templates_dir, filename)
                    
                    try:
                        spec = importlib.util.spec_from_file_location(template_name, template_path)
                        template_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(template_module)
                        
                        # 提取模板类
                        for name, obj in inspect.getmembers(template_module):
                            if inspect.isclass(obj) and name.endswith('Template'):
                                self.tool_templates[name] = obj
                    except Exception as e:
                        print(f"加载工具模板时出错 {template_path}: {e}")
    
    def _create_capability_analyzer(self):
        """创建能力分析器"""
        class CapabilityAnalyzer:
            def analyze(self, tool_description):
                """分析工具描述，确定所需能力"""
                capabilities = {
                    "io_operations": "文件读写" in tool_description or "IO" in tool_description,
                    "network_operations": "网络" in tool_description or "HTTP" in tool_description,
                    "data_processing": "数据处理" in tool_description or "分析" in tool_description,
                    "visualization": "可视化" in tool_description or "图表" in tool_description,
                    "ai_integration": "AI" in tool_description or "智能" in tool_description
                }
                return capabilities
        
        return CapabilityAnalyzer()
    
    def start_session(self, agent_type):
        """启动新的会话"""
        self.session_id = self.recorder.start_session(agent_type)
        return self.session_id
    
    def brainstorm_tool(self, tool_description, context=None):
        """头脑风暴新工具"""
        if not self.session_id:
            self.start_session("mcp_brainstorm")
        
        self.recorder.record_thought(self.session_id, f"开始头脑风暴新工具: {tool_description}")
        
        # 分析工具所需能力
        capabilities = self.capability_analyzer.analyze(tool_description)
        self.recorder.record_thought(self.session_id, f"工具能力分析结果: {capabilities}")
        
        # 选择最合适的模板
        template_class = self._select_template(capabilities)
        if not template_class:
            self.recorder.record_thought(self.session_id, "找不到合适的模板，使用通用模板")
            template_class = self._get_generic_template()
        
        # 生成工具代码
        tool_code = self._generate_tool_code(tool_description, template_class, capabilities)
        
        # 创建工具实例
        tool_instance = self._create_tool_instance(tool_description, tool_code)
        
        # 注册新工具
        tool_name = self._generate_tool_name(tool_description)
        self.new_tools_registry[tool_name] = tool_instance
        
        self.recorder.record_action(self.session_id, "brainstorm_tool", {
            "tool_description": tool_description,
            "capabilities": capabilities
        }, {"tool_name": tool_name})
        
        return {
            "tool_name": tool_name,
            "tool_description": tool_description,
            "capabilities": capabilities,
            "code": tool_code
        }
    
    def _select_template(self, capabilities):
        """选择最合适的模板"""
        # 简单的模板选择逻辑，可以根据实际需求扩展
        if capabilities.get("data_processing") and capabilities.get("visualization"):
            return self.tool_templates.get("DataVisualizationTemplate")
        elif capabilities.get("network_operations"):
            return self.tool_templates.get("NetworkOperationTemplate")
        elif capabilities.get("io_operations"):
            return self.tool_templates.get("FileOperationTemplate")
        elif capabilities.get("ai_integration"):
            return self.tool_templates.get("AIIntegrationTemplate")
        
        return None
    
    def _get_generic_template(self):
        """获取通用模板"""
        return self.tool_templates.get("GenericToolTemplate") or type("GenericToolTemplate", (), {
            "generate_code": lambda desc, caps: f"""
class GenericTool:
    def __init__(self):
        self.description = "{desc}"
    
    def execute(self, **kwargs):
        return {{"status": "success", "message": "执行通用工具", "params": kwargs}}
"""
        })
    
    def _generate_tool_code(self, tool_description, template_class, capabilities):
        """生成工具代码"""
        try:
            return template_class.generate_code(tool_description, capabilities)
        except Exception as e:
            self.recorder.record_thought(self.session_id, f"生成工具代码时出错: {e}")
            return self._get_generic_template().generate_code(tool_description, capabilities)
    
    def _create_tool_instance(self, tool_description, tool_code):
        """创建工具实例"""
        try:
            # 创建临时模块
            module_name = f"dynamic_tool_{hash(tool_description) % 10000}"
            exec(tool_code, globals())
            
            # 查找工具类
            tool_class = None
            for name, obj in list(globals().items()):
                if inspect.isclass(obj) and name not in ["MCPBrainstorm", "ThoughtActionRecorder", "AgentProblemSolver"]:
                    tool_class = obj
                    break
            
            if not tool_class:
                raise ValueError("无法在生成的代码中找到工具类")
            
            # 创建实例
            return tool_class()
        
        except Exception as e:
            self.recorder.record_thought(self.session_id, f"创建工具实例时出错: {e}")
            
            # 创建一个简单的替代实例
            class SimpleTool:
                def execute(self, **kwargs):
                    return {"status": "error", "message": f"工具创建失败: {e}", "params": kwargs}
            
            return SimpleTool()
    
    def _generate_tool_name(self, tool_description):
        """生成工具名称"""
        # 简单的名称生成逻辑，可以根据实际需求扩展
        words = tool_description.split()
        if len(words) >= 2:
            name = ''.join(word.capitalize() for word in words[:2])
        else:
            name = tool_description.capitalize()
        
        name = ''.join(c for c in name if c.isalnum())
        name = f"{name}Tool"
        
        # 确保名称唯一
        if name in self.new_tools_registry:
            name = f"{name}_{len(self.new_tools_registry)}"
        
        return name
    
    def get_tool(self, tool_name):
        """获取工具实例"""
        return self.new_tools_registry.get(tool_name)
    
    def list_tools(self):
        """列出所有可用工具"""
        return list(self.new_tools_registry.keys())
    
    def enhance_capability(self, tool_name, new_capabilities):
        """增强工具能力"""
        if not self.session_id:
            self.start_session("mcp_brainstorm")
        
        self.recorder.record_thought(self.session_id, f"开始增强工具能力: {tool_name}")
        
        tool = self.get_tool(tool_name)
        if not tool:
            self.recorder.record_thought(self.session_id, f"找不到工具: {tool_name}")
            return {"status": "error", "reason": f"Tool not found: {tool_name}"}
        
        # 使用问题解决器增强工具能力
        enhancement_request = {
            "tool_name": tool_name,
            "current_capabilities": getattr(tool, "capabilities", {}),
            "new_capabilities": new_capabilities
        }
        
        enhancement_result = self.problem_solver.solve_problem(
            problem_type="tool_enhancement",
            problem_description=f"增强工具 {tool_name} 的能力",
            problem_context=enhancement_request
        )
        
        self.recorder.record_action(self.session_id, "enhance_capability", enhancement_request, enhancement_result)
        
        return enhancement_result
    
    def run_e2e_test(self, tool_name, test_parameters=None):
        """运行端到端测试"""
        if not self.session_id:
            self.start_session("mcp_brainstorm")
        
        self.recorder.record_thought(self.session_id, f"开始运行工具端到端测试: {tool_name}")
        
        tool = self.get_tool(tool_name)
        if not tool:
            self.recorder.record_thought(self.session_id, f"找不到工具: {tool_name}")
            return {"status": "error", "reason": f"Tool not found: {tool_name}"}
        
        # 准备测试用例
        test_cases = self._prepare_test_cases(tool, test_parameters)
        
        # 执行测试
        test_results = []
        for i, test_case in enumerate(test_cases):
            try:
                self.recorder.record_thought(self.session_id, f"执行测试用例 {i+1}: {test_case.get('description', '未命名')}")
                
                # 执行测试
                params = test_case.get("params", {})
                result = tool.execute(**params)
                
                # 验证结果
                expected = test_case.get("expected", {})
                validation = self._validate_test_result(result, expected)
                
                test_results.append({
                    "case": i + 1,
                    "description": test_case.get("description", "未命名"),
                    "params": params,
                    "result": result,
                    "validation": validation
                })
            
            except Exception as e:
                self.recorder.record_thought(self.session_id, f"测试用例执行出错: {e}")
                test_results.append({
                    "case": i + 1,
                    "description": test_case.get("description", "未命名"),
                    "params": test_case.get("params", {}),
                    "error": str(e),
                    "validation": {"status": "error", "reason": str(e)}
                })
        
        # 汇总测试结果
        summary = {
            "tool_name": tool_name,
            "total_cases": len(test_cases),
            "passed": sum(1 for r in test_results if r.get("validation", {}).get("status") == "passed"),
            "failed": sum(1 for r in test_results if r.get("validation", {}).get("status") == "failed"),
            "error": sum(1 for r in test_results if r.get("validation", {}).get("status") == "error"),
            "results": test_results
        }
        
        self.recorder.record_action(self.session_id, "run_e2e_test", {
            "tool_name": tool_name,
            "test_parameters": test_parameters
        }, summary)
        
        return summary
    
    def _prepare_test_cases(self, tool, test_parameters=None):
        """准备测试用例"""
        # 如果提供了测试参数，使用它们
        if test_parameters and isinstance(test_parameters, list):
            return test_parameters
        
        # 否则，生成默认测试用例
        default_cases = []
        
        # 检查工具方法
        methods = [name for name, func in inspect.getmembers(tool, inspect.ismethod)
                  if not name.startswith('_')]
        
        for method_name in methods:
            method = getattr(tool, method_name)
            sig = inspect.signature(method)
            
            # 为每个方法创建一个基本测试用例
            params = {}
            for param_name, param in sig.parameters.items():
                if param.default is inspect.Parameter.empty:
                    # 必需参数，提供一个默认值
                    if param_name in ["text", "content", "message", "query"]:
                        params[param_name] = "测试内容"
                    elif param_name in ["id", "name", "key"]:
                        params[param_name] = "test_id"
                    elif param_name in ["file", "path", "filename"]:
                        params[param_name] = "/tmp/test_file.txt"
                    elif param_name in ["url"]:
                        params[param_name] = "https://example.com"
                    else:
                        params[param_name] = "test_value"
            
            default_cases.append({
                "description": f"测试 {method_name} 方法的基本功能",
                "method": method_name,
                "params": params,
                "expected": {"status": "success"}
            })
        
        # 如果没有找到方法，使用execute方法
        if not default_cases:
            default_cases.append({
                "description": "测试 execute 方法的基本功能",
                "method": "execute",
                "params": {},
                "expected": {"status": "success"}
            })
        
        return default_cases
    
    def _validate_test_result(self, result, expected):
        """验证测试结果"""
        # 简单的验证逻辑，可以根据实际需求扩展
        if not isinstance(result, dict):
            return {"status": "failed", "reason": "结果不是字典类型"}
        
        # 检查状态
        if "status" in expected and result.get("status") != expected["status"]:
            return {
                "status": "failed",
                "reason": f"状态不匹配，期望 {expected['status']}，实际 {result.get('status')}"
            }
        
        # 检查其他期望字段
        for key, value in expected.items():
            if key != "status" and (key not in result or result[key] != value):
                return {
                    "status": "failed",
                    "reason": f"字段 {key} 不匹配，期望 {value}，实际 {result.get(key)}"
                }
        
        return {"status": "passed"}
