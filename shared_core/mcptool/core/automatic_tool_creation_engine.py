#!/usr/bin/env python3
"""
自動工具創建引擎
基於錯誤分析結果自動創建修復工具，整合KiloCode和智能工具引擎
"""

import json
import logging
import time
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import uuid
import importlib.util

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

from mcptool.core.error_detection_analyzer import ErrorType, ErrorSeverity, ErrorAnalysisResult
from mcptool.adapters.kilocode_adapter.kilocode_mcp import KiloCodeMCP

logger = logging.getLogger(__name__)

@dataclass
class ToolCreationRequest:
    """工具創建請求"""
    tool_name: str
    tool_description: str
    error_type: ErrorType
    severity: ErrorSeverity
    requirements: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    implementation_hints: List[str]
    dependencies: List[str]
    estimated_complexity: str  # "simple", "medium", "complex"

@dataclass
class CreatedTool:
    """創建的工具"""
    tool_id: str
    tool_name: str
    file_path: str
    source_code: str
    test_code: str
    documentation: str
    creation_time: float
    creator_engine: str
    validation_status: str
    error_type: ErrorType

class AutomaticToolCreationEngine:
    """自動工具創建引擎"""
    
    def __init__(self):
        """初始化工具創建引擎"""
        self.kilocode_adapter = KiloCodeMCP()
        self.created_tools = {}
        self.tool_templates = self._initialize_tool_templates()
        self.creation_history = []
        
        # 工具存儲目錄
        self.tools_directory = Path("/home/ubuntu/projects/communitypowerautomation/mcptool/adapters/generated")
        self.tools_directory.mkdir(exist_ok=True)
        
        logger.info("自動工具創建引擎初始化完成")
    
    def _initialize_tool_templates(self) -> Dict[ErrorType, Dict[str, Any]]:
        """初始化工具模板"""
        return {
            ErrorType.API_FAILURE: {
                "template_name": "api_retry_tool",
                "base_imports": ["requests", "time", "random"],
                "core_functions": ["retry_with_backoff", "switch_api_endpoint", "validate_response"],
                "complexity": "medium"
            },
            ErrorType.ANSWER_FORMAT: {
                "template_name": "answer_formatter_tool",
                "base_imports": ["re", "json", "string"],
                "core_functions": ["format_answer", "validate_format", "extract_key_info"],
                "complexity": "simple"
            },
            ErrorType.KNOWLEDGE_GAP: {
                "template_name": "knowledge_search_tool",
                "base_imports": ["requests", "beautifulsoup4", "json"],
                "core_functions": ["search_multiple_sources", "aggregate_information", "validate_facts"],
                "complexity": "complex"
            },
            ErrorType.REASONING_ERROR: {
                "template_name": "logic_validator_tool",
                "base_imports": ["sympy", "logic", "reasoning"],
                "core_functions": ["validate_logic", "step_by_step_check", "find_logical_errors"],
                "complexity": "complex"
            },
            ErrorType.FILE_PROCESSING: {
                "template_name": "file_processor_tool",
                "base_imports": ["pandas", "openpyxl", "PyPDF2", "docx"],
                "core_functions": ["parse_file", "extract_data", "validate_content"],
                "complexity": "medium"
            },
            ErrorType.SEARCH_FAILURE: {
                "template_name": "enhanced_search_tool",
                "base_imports": ["requests", "selenium", "beautifulsoup4"],
                "core_functions": ["multi_engine_search", "result_aggregation", "relevance_scoring"],
                "complexity": "complex"
            },
            ErrorType.CALCULATION_ERROR: {
                "template_name": "math_solver_tool",
                "base_imports": ["sympy", "numpy", "scipy"],
                "core_functions": ["solve_equation", "validate_calculation", "step_by_step_solution"],
                "complexity": "medium"
            },
            ErrorType.CONTEXT_MISSING: {
                "template_name": "context_enricher_tool",
                "base_imports": ["requests", "json", "nltk"],
                "core_functions": ["gather_context", "enrich_information", "validate_relevance"],
                "complexity": "complex"
            },
            ErrorType.TOOL_LIMITATION: {
                "template_name": "capability_extender_tool",
                "base_imports": ["subprocess", "requests", "json"],
                "core_functions": ["extend_capability", "hybrid_approach", "fallback_mechanism"],
                "complexity": "complex"
            }
        }
    
    def analyze_and_create_tool(self, error_analysis: ErrorAnalysisResult, context: Dict[str, Any] = None) -> CreatedTool:
        """基於錯誤分析創建工具"""
        try:
            # 生成工具創建請求
            creation_request = self._generate_creation_request(error_analysis, context)
            
            # 選擇創建策略
            creation_strategy = self._select_creation_strategy(creation_request)
            
            # 創建工具
            if creation_strategy == "kilocode":
                created_tool = self._create_tool_with_kilocode(creation_request)
            elif creation_strategy == "template":
                created_tool = self._create_tool_with_template(creation_request)
            else:
                created_tool = self._create_tool_hybrid(creation_request)
            
            # 驗證工具
            validation_result = self._validate_created_tool(created_tool)
            created_tool.validation_status = validation_result["status"]
            
            # 保存工具
            self._save_created_tool(created_tool)
            
            # 記錄創建歷史
            self.creation_history.append({
                "timestamp": time.time(),
                "error_type": error_analysis.error_type.value,
                "tool_id": created_tool.tool_id,
                "creation_strategy": creation_strategy,
                "validation_status": validation_result["status"]
            })
            
            logger.info(f"成功創建工具: {created_tool.tool_name} (ID: {created_tool.tool_id})")
            return created_tool
            
        except Exception as e:
            logger.error(f"工具創建失敗: {e}")
            # 返回一個錯誤工具
            return self._create_error_tool(error_analysis, str(e))
    
    def _generate_creation_request(self, error_analysis: ErrorAnalysisResult, context: Dict[str, Any] = None) -> ToolCreationRequest:
        """生成工具創建請求"""
        context = context or {}
        
        # 基於錯誤類型生成工具名稱
        tool_name = f"{error_analysis.error_type.value}_repair_tool_{int(time.time())}"
        
        # 生成工具描述
        tool_description = f"自動生成的修復工具，用於解決{error_analysis.error_type.value}類型的錯誤"
        
        # 獲取模板信息
        template_info = self.tool_templates.get(error_analysis.error_type, {})
        
        # 生成需求列表
        requirements = [
            f"修復{error_analysis.error_type.value}錯誤",
            f"處理{error_analysis.severity.value}級別問題",
            "提供詳細的錯誤處理",
            "支持重試機制",
            "生成修復報告"
        ]
        
        # 生成輸入輸出模式
        input_schema = {
            "type": "object",
            "properties": {
                "input_data": {"type": "string", "description": "需要修復的輸入數據"},
                "error_context": {"type": "object", "description": "錯誤上下文信息"},
                "repair_options": {"type": "object", "description": "修復選項"}
            },
            "required": ["input_data"]
        }
        
        output_schema = {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "description": "修復是否成功"},
                "repaired_data": {"type": "string", "description": "修復後的數據"},
                "repair_report": {"type": "object", "description": "修復報告"},
                "confidence": {"type": "number", "description": "修復置信度"}
            },
            "required": ["success", "repaired_data"]
        }
        
        # 生成實現提示
        implementation_hints = [
            f"使用{error_analysis.repair_strategy}策略",
            f"重點關注{error_analysis.root_cause}問題",
            "實現錯誤檢測和恢復機制",
            "添加日誌記錄功能",
            "提供詳細的錯誤信息"
        ]
        
        # 生成依賴列表
        dependencies = template_info.get("base_imports", ["json", "logging", "time"])
        
        return ToolCreationRequest(
            tool_name=tool_name,
            tool_description=tool_description,
            error_type=error_analysis.error_type,
            severity=error_analysis.severity,
            requirements=requirements,
            input_schema=input_schema,
            output_schema=output_schema,
            implementation_hints=implementation_hints,
            dependencies=dependencies,
            estimated_complexity=template_info.get("complexity", "medium")
        )
    
    def _select_creation_strategy(self, request: ToolCreationRequest) -> str:
        """選擇工具創建策略"""
        # 如果KiloCode可用且複雜度較高，使用KiloCode
        if self.kilocode_adapter.available and request.estimated_complexity in ["medium", "complex"]:
            return "kilocode"
        
        # 如果有對應的模板，使用模板
        if request.error_type in self.tool_templates:
            return "template"
        
        # 否則使用混合方法
        return "hybrid"
    
    def _create_tool_with_kilocode(self, request: ToolCreationRequest) -> CreatedTool:
        """使用KiloCode創建工具"""
        # 生成詳細的代碼生成提示
        prompt = self._generate_kilocode_prompt(request)
        
        # 調用KiloCode生成代碼
        generation_result = self.kilocode_adapter.process({
            "action": "generate_code",
            "prompt": prompt,
            "language": "python"
        })
        
        if generation_result.get("status") == "success":
            source_code = generation_result["result"]["code"]
        else:
            # 如果KiloCode失敗，回退到模板方法
            logger.warning("KiloCode生成失敗，回退到模板方法")
            return self._create_tool_with_template(request)
        
        # 生成測試代碼
        test_code = self._generate_test_code(request, source_code)
        
        # 生成文檔
        documentation = self._generate_documentation(request, source_code)
        
        # 創建工具對象
        tool_id = str(uuid.uuid4())
        file_path = self.tools_directory / f"{request.tool_name}.py"
        
        return CreatedTool(
            tool_id=tool_id,
            tool_name=request.tool_name,
            file_path=str(file_path),
            source_code=source_code,
            test_code=test_code,
            documentation=documentation,
            creation_time=time.time(),
            creator_engine="kilocode",
            validation_status="pending",
            error_type=request.error_type
        )
    
    def _create_tool_with_template(self, request: ToolCreationRequest) -> CreatedTool:
        """使用模板創建工具"""
        template_info = self.tool_templates.get(request.error_type, {})
        
        # 生成基礎代碼結構
        source_code = self._generate_template_code(request, template_info)
        
        # 生成測試代碼
        test_code = self._generate_test_code(request, source_code)
        
        # 生成文檔
        documentation = self._generate_documentation(request, source_code)
        
        # 創建工具對象
        tool_id = str(uuid.uuid4())
        file_path = self.tools_directory / f"{request.tool_name}.py"
        
        return CreatedTool(
            tool_id=tool_id,
            tool_name=request.tool_name,
            file_path=str(file_path),
            source_code=source_code,
            test_code=test_code,
            documentation=documentation,
            creation_time=time.time(),
            creator_engine="template",
            validation_status="pending",
            error_type=request.error_type
        )
    
    def _create_tool_hybrid(self, request: ToolCreationRequest) -> CreatedTool:
        """使用混合方法創建工具"""
        # 結合模板和動態生成
        template_info = self.tool_templates.get(ErrorType.UNKNOWN, {})
        
        # 生成通用修復工具
        source_code = self._generate_generic_repair_tool(request)
        
        # 生成測試代碼
        test_code = self._generate_test_code(request, source_code)
        
        # 生成文檔
        documentation = self._generate_documentation(request, source_code)
        
        # 創建工具對象
        tool_id = str(uuid.uuid4())
        file_path = self.tools_directory / f"{request.tool_name}.py"
        
        return CreatedTool(
            tool_id=tool_id,
            tool_name=request.tool_name,
            file_path=str(file_path),
            source_code=source_code,
            test_code=test_code,
            documentation=documentation,
            creation_time=time.time(),
            creator_engine="hybrid",
            validation_status="pending",
            error_type=request.error_type
        )
    
    def _generate_kilocode_prompt(self, request: ToolCreationRequest) -> str:
        """生成KiloCode提示"""
        prompt = f"""
創建一個Python工具來修復{request.error_type.value}類型的錯誤。

工具需求：
{chr(10).join(f"- {req}" for req in request.requirements)}

實現提示：
{chr(10).join(f"- {hint}" for hint in request.implementation_hints)}

輸入格式：
{json.dumps(request.input_schema, indent=2)}

輸出格式：
{json.dumps(request.output_schema, indent=2)}

依賴庫：
{', '.join(request.dependencies)}

請生成完整的Python代碼，包括：
1. 必要的導入語句
2. 主要的修復函數
3. 錯誤處理機制
4. 日誌記錄功能
5. 輸入驗證
6. 輸出格式化

代碼應該是生產就緒的，包含適當的錯誤處理和文檔字符串。
"""
        return prompt
    
    def _generate_template_code(self, request: ToolCreationRequest, template_info: Dict[str, Any]) -> str:
        """生成模板代碼"""
        imports = template_info.get("base_imports", ["json", "logging", "time"])
        functions = template_info.get("core_functions", ["main_function"])
        
        code = f'''#!/usr/bin/env python3
"""
{request.tool_description}

自動生成的工具代碼
錯誤類型: {request.error_type.value}
嚴重程度: {request.severity.value}
生成時間: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

{chr(10).join(f"import {imp}" for imp in imports)}
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class {request.tool_name.replace("_", "").title()}:
    """自動生成的修復工具類"""
    
    def __init__(self):
        """初始化工具"""
        self.tool_name = "{request.tool_name}"
        self.error_type = "{request.error_type.value}"
        self.severity = "{request.severity.value}"
        logger.info(f"初始化修復工具: {{self.tool_name}}")
    
    def repair(self, input_data: str, error_context: Dict[str, Any] = None, repair_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """主要修復函數"""
        try:
            logger.info(f"開始修復{{self.error_type}}錯誤")
            
            # 驗證輸入
            if not self._validate_input(input_data):
                return {{
                    "success": False,
                    "repaired_data": "",
                    "repair_report": {{"error": "輸入驗證失敗"}},
                    "confidence": 0.0
                }}
            
            # 執行修復邏輯
            repaired_data = self._execute_repair(input_data, error_context or {{}}, repair_options or {{}})
            
            # 驗證修復結果
            confidence = self._validate_repair(repaired_data, input_data)
            
            return {{
                "success": True,
                "repaired_data": repaired_data,
                "repair_report": {{
                    "tool_used": self.tool_name,
                    "repair_strategy": "{request.implementation_hints[0] if request.implementation_hints else '通用修復'}",
                    "processing_time": time.time()
                }},
                "confidence": confidence
            }}
            
        except Exception as e:
            logger.error(f"修復過程中出錯: {{e}}")
            return {{
                "success": False,
                "repaired_data": "",
                "repair_report": {{"error": str(e)}},
                "confidence": 0.0
            }}
    
    def _validate_input(self, input_data: str) -> bool:
        """驗證輸入數據"""
        return input_data is not None and len(str(input_data).strip()) > 0
    
    def _execute_repair(self, input_data: str, error_context: Dict[str, Any], repair_options: Dict[str, Any]) -> str:
        """執行具體的修復邏輯"""
        # TODO: 實現具體的修復邏輯
        # 這裡是基礎模板，需要根據具體錯誤類型實現
        
        if self.error_type == "answer_format":
            return self._repair_answer_format(input_data)
        elif self.error_type == "api_failure":
            return self._repair_api_failure(input_data, error_context)
        else:
            return self._generic_repair(input_data)
    
    def _repair_answer_format(self, input_data: str) -> str:
        """修復答案格式錯誤"""
        # 清理和格式化答案
        cleaned = str(input_data).strip()
        # 移除多餘的標點符號
        cleaned = re.sub(r'[^\\w\\s\\d\\.]', '', cleaned) if 'import re' in globals() else cleaned
        return cleaned
    
    def _repair_api_failure(self, input_data: str, error_context: Dict[str, Any]) -> str:
        """修復API失敗錯誤"""
        # 實現重試邏輯
        max_retries = error_context.get("max_retries", 3)
        for attempt in range(max_retries):
            try:
                # 模擬API重試
                time.sleep(attempt * 0.5)  # 指數退避
                return f"修復後的數據: {{input_data}}"
            except Exception:
                continue
        return input_data
    
    def _generic_repair(self, input_data: str) -> str:
        """通用修復邏輯"""
        return f"通用修復: {{input_data}}"
    
    def _validate_repair(self, repaired_data: str, original_data: str) -> float:
        """驗證修復結果"""
        if not repaired_data:
            return 0.0
        
        # 簡單的相似度檢查
        if len(repaired_data) > len(original_data) * 0.5:
            return 0.8
        else:
            return 0.5

# 主要入口函數
def main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """主要處理函數"""
    tool = {request.tool_name.replace("_", "").title()}()
    return tool.repair(
        input_data.get("input_data", ""),
        input_data.get("error_context", {{}}),
        input_data.get("repair_options", {{}})
    )

if __name__ == "__main__":
    # 測試代碼
    test_input = {{
        "input_data": "測試數據",
        "error_context": {{}},
        "repair_options": {{}}
    }}
    result = main(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
'''
        return code
    
    def _generate_generic_repair_tool(self, request: ToolCreationRequest) -> str:
        """生成通用修復工具"""
        return f'''#!/usr/bin/env python3
"""
通用修復工具 - {request.tool_name}

{request.tool_description}
錯誤類型: {request.error_type.value}
生成時間: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def repair_error(input_data: str, error_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """通用錯誤修復函數"""
    try:
        # 基礎修復邏輯
        repaired_data = str(input_data).strip()
        
        return {{
            "success": True,
            "repaired_data": repaired_data,
            "repair_report": {{
                "tool_name": "{request.tool_name}",
                "error_type": "{request.error_type.value}",
                "repair_time": time.time()
            }},
            "confidence": 0.7
        }}
    except Exception as e:
        return {{
            "success": False,
            "repaired_data": "",
            "repair_report": {{"error": str(e)}},
            "confidence": 0.0
        }}

def main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """主要入口函數"""
    return repair_error(
        input_data.get("input_data", ""),
        input_data.get("error_context", {{}})
    )

if __name__ == "__main__":
    test_result = main({{"input_data": "測試"}})
    print(json.dumps(test_result, indent=2, ensure_ascii=False))
'''
    
    def _generate_test_code(self, request: ToolCreationRequest, source_code: str) -> str:
        """生成測試代碼"""
        return f'''#!/usr/bin/env python3
"""
{request.tool_name} 的測試代碼
"""

import unittest
import json
import sys
import os

# 添加工具路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Test{request.tool_name.replace("_", "").title()}(unittest.TestCase):
    """測試{request.tool_name}工具"""
    
    def setUp(self):
        """設置測試環境"""
        self.test_data = {{
            "input_data": "測試輸入數據",
            "error_context": {{"test": True}},
            "repair_options": {{}}
        }}
    
    def test_basic_repair(self):
        """測試基本修復功能"""
        from {request.tool_name} import main
        result = main(self.test_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("repaired_data", result)
        self.assertIn("confidence", result)
    
    def test_empty_input(self):
        """測試空輸入處理"""
        from {request.tool_name} import main
        result = main({{"input_data": ""}})
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_error_handling(self):
        """測試錯誤處理"""
        from {request.tool_name} import main
        result = main({{}})  # 缺少必要參數
        
        self.assertIsInstance(result, dict)

if __name__ == "__main__":
    unittest.main()
'''
    
    def _generate_documentation(self, request: ToolCreationRequest, source_code: str) -> str:
        """生成文檔"""
        return f'''# {request.tool_name} 工具文檔

## 概述
{request.tool_description}

## 錯誤類型
- **類型**: {request.error_type.value}
- **嚴重程度**: {request.severity.value}

## 功能需求
{chr(10).join(f"- {req}" for req in request.requirements)}

## 使用方法

### 基本用法
```python
from {request.tool_name} import main

input_data = {{
    "input_data": "需要修復的數據",
    "error_context": {{}},
    "repair_options": {{}}
}}

result = main(input_data)
print(result)
```

### 輸入格式
```json
{json.dumps(request.input_schema, indent=2)}
```

### 輸出格式
```json
{json.dumps(request.output_schema, indent=2)}
```

## 依賴項
{chr(10).join(f"- {dep}" for dep in request.dependencies)}

## 實現提示
{chr(10).join(f"- {hint}" for hint in request.implementation_hints)}

## 創建信息
- **創建時間**: {time.strftime("%Y-%m-%d %H:%M:%S")}
- **預估複雜度**: {request.estimated_complexity}
- **工具ID**: 將在創建時生成

## 注意事項
1. 此工具是自動生成的，可能需要進一步優化
2. 請在生產環境使用前進行充分測試
3. 如有問題，請檢查日誌輸出
'''
    
    def _validate_created_tool(self, tool: CreatedTool) -> Dict[str, Any]:
        """驗證創建的工具"""
        try:
            # 語法檢查
            compile(tool.source_code, tool.file_path, 'exec')
            
            # 基本結構檢查
            has_main_function = "def main(" in tool.source_code
            has_imports = any(line.strip().startswith("import") for line in tool.source_code.split('\n'))
            has_error_handling = "try:" in tool.source_code and "except" in tool.source_code
            
            validation_score = 0
            if has_main_function:
                validation_score += 0.4
            if has_imports:
                validation_score += 0.2
            if has_error_handling:
                validation_score += 0.4
            
            if validation_score >= 0.8:
                status = "valid"
            elif validation_score >= 0.5:
                status = "partial"
            else:
                status = "invalid"
            
            return {
                "status": status,
                "score": validation_score,
                "checks": {
                    "syntax": True,
                    "main_function": has_main_function,
                    "imports": has_imports,
                    "error_handling": has_error_handling
                }
            }
            
        except SyntaxError as e:
            return {
                "status": "invalid",
                "score": 0.0,
                "error": f"語法錯誤: {e}",
                "checks": {"syntax": False}
            }
        except Exception as e:
            return {
                "status": "error",
                "score": 0.0,
                "error": f"驗證失敗: {e}",
                "checks": {}
            }
    
    def _save_created_tool(self, tool: CreatedTool):
        """保存創建的工具"""
        try:
            # 保存源代碼
            with open(tool.file_path, 'w', encoding='utf-8') as f:
                f.write(tool.source_code)
            
            # 保存測試代碼
            test_file_path = tool.file_path.replace('.py', '_test.py')
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(tool.test_code)
            
            # 保存文檔
            doc_file_path = tool.file_path.replace('.py', '_doc.md')
            with open(doc_file_path, 'w', encoding='utf-8') as f:
                f.write(tool.documentation)
            
            # 保存工具元數據
            metadata = {
                "tool_id": tool.tool_id,
                "tool_name": tool.tool_name,
                "creation_time": tool.creation_time,
                "creator_engine": tool.creator_engine,
                "validation_status": tool.validation_status,
                "error_type": tool.error_type.value,
                "file_path": tool.file_path
            }
            
            metadata_file_path = tool.file_path.replace('.py', '_metadata.json')
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # 添加到已創建工具列表
            self.created_tools[tool.tool_id] = tool
            
            logger.info(f"工具已保存: {tool.file_path}")
            
        except Exception as e:
            logger.error(f"保存工具失敗: {e}")
            raise
    
    def _create_error_tool(self, error_analysis: ErrorAnalysisResult, error_message: str) -> CreatedTool:
        """創建錯誤工具（當工具創建失敗時）"""
        tool_id = str(uuid.uuid4())
        tool_name = f"error_tool_{int(time.time())}"
        file_path = self.tools_directory / f"{tool_name}.py"
        
        source_code = f'''#!/usr/bin/env python3
"""
錯誤工具 - 工具創建失敗時的備用工具
錯誤信息: {error_message}
"""

def main(input_data):
    return {{
        "success": False,
        "error": "工具創建失敗: {error_message}",
        "repaired_data": "",
        "confidence": 0.0
    }}
'''
        
        return CreatedTool(
            tool_id=tool_id,
            tool_name=tool_name,
            file_path=str(file_path),
            source_code=source_code,
            test_code="# 錯誤工具無測試代碼",
            documentation=f"# 錯誤工具\n\n工具創建失敗: {error_message}",
            creation_time=time.time(),
            creator_engine="error_handler",
            validation_status="error",
            error_type=error_analysis.error_type
        )
    
    def get_created_tools(self) -> List[CreatedTool]:
        """獲取所有已創建的工具"""
        return list(self.created_tools.values())
    
    def get_creation_statistics(self) -> Dict[str, Any]:
        """獲取創建統計信息"""
        total_tools = len(self.created_tools)
        
        if total_tools == 0:
            return {"total_tools": 0}
        
        # 按創建引擎統計
        engine_stats = {}
        validation_stats = {}
        error_type_stats = {}
        
        for tool in self.created_tools.values():
            engine = tool.creator_engine
            validation = tool.validation_status
            error_type = tool.error_type.value
            
            engine_stats[engine] = engine_stats.get(engine, 0) + 1
            validation_stats[validation] = validation_stats.get(validation, 0) + 1
            error_type_stats[error_type] = error_type_stats.get(error_type, 0) + 1
        
        return {
            "total_tools": total_tools,
            "engine_distribution": engine_stats,
            "validation_distribution": validation_stats,
            "error_type_distribution": error_type_stats,
            "creation_history_count": len(self.creation_history)
        }

def main():
    """測試函數"""
    from mcptool.core.error_detection_analyzer import ErrorAnalysisResult, ErrorType, ErrorSeverity
    
    # 創建測試錯誤分析結果
    test_analysis = ErrorAnalysisResult(
        error_type=ErrorType.ANSWER_FORMAT,
        severity=ErrorSeverity.MEDIUM,
        confidence=0.8,
        description="答案格式錯誤",
        root_cause="輸出格式不符合要求",
        suggested_tools=["answer_formatter_tool"],
        repair_strategy="創建答案格式化工具",
        estimated_fix_time=10
    )
    
    # 創建工具創建引擎
    engine = AutomaticToolCreationEngine()
    
    # 創建工具
    created_tool = engine.analyze_and_create_tool(test_analysis)
    
    print(f"創建的工具: {created_tool.tool_name}")
    print(f"工具ID: {created_tool.tool_id}")
    print(f"驗證狀態: {created_tool.validation_status}")
    print(f"創建引擎: {created_tool.creator_engine}")

if __name__ == "__main__":
    main()

