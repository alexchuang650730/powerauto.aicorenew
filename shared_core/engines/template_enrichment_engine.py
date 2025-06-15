#!/usr/bin/env python3
"""
PowerAutomation v0.574 - 黑白盒模板豐富系統

核心技術難點1解決方案：
透過黑盒及白盒文本描述來豐富我們的模板

技術架構：
1. 文本分析引擎 - 解析黑白盒描述
2. 模板學習系統 - 從描述中提取模板特徵
3. 模板豐富引擎 - 自動生成和優化模板
4. 知識圖譜構建 - 建立模板間的關聯關係
"""

import os
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import hashlib
import pickle
from collections import defaultdict, Counter
import numpy as np

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BoxType(Enum):
    """盒子類型枚舉"""
    BLACK_BOX = "black_box"  # 黑盒：只知道輸入輸出，不知道內部實現
    WHITE_BOX = "white_box"  # 白盒：知道內部實現細節
    GRAY_BOX = "gray_box"    # 灰盒：部分了解內部實現

class TemplateCategory(Enum):
    """模板類別枚舉"""
    FUNCTIONAL = "functional"        # 功能性模板
    PERFORMANCE = "performance"      # 性能測試模板
    SECURITY = "security"           # 安全測試模板
    INTEGRATION = "integration"     # 集成測試模板
    UI_UX = "ui_ux"                # 用戶界面測試模板
    API = "api"                    # API測試模板
    DATABASE = "database"          # 數據庫測試模板

@dataclass
class TextDescription:
    """文本描述數據結構"""
    description_id: str
    box_type: BoxType
    category: TemplateCategory
    title: str
    content: str
    input_description: str
    output_description: str
    implementation_details: Optional[str] = None  # 白盒才有
    constraints: List[str] = None
    examples: List[Dict[str, Any]] = None
    tags: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.constraints is None:
            self.constraints = []
        if self.examples is None:
            self.examples = []
        if self.tags is None:
            self.tags = []

@dataclass
class TemplatePattern:
    """模板模式"""
    pattern_id: str
    pattern_type: str
    pattern_content: str
    confidence: float
    frequency: int
    related_patterns: List[str] = None
    
    def __post_init__(self):
        if self.related_patterns is None:
            self.related_patterns = []

@dataclass
class EnrichedTemplate:
    """豐富化的模板"""
    template_id: str
    original_description: TextDescription
    extracted_patterns: List[TemplatePattern]
    generated_variations: List[Dict[str, Any]]
    test_cases: List[Dict[str, Any]]
    quality_score: float
    enrichment_metadata: Dict[str, Any]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class TextAnalysisEngine:
    """文本分析引擎"""
    
    def __init__(self):
        self.keyword_patterns = self._load_keyword_patterns()
        self.structure_patterns = self._load_structure_patterns()
        self.domain_knowledge = self._load_domain_knowledge()
    
    def _load_keyword_patterns(self) -> Dict[str, List[str]]:
        """加載關鍵詞模式"""
        return {
            "input_keywords": [
                "輸入", "參數", "數據", "請求", "調用", "傳入", "接收",
                "input", "parameter", "data", "request", "call", "receive"
            ],
            "output_keywords": [
                "輸出", "返回", "結果", "響應", "回傳", "產生", "生成",
                "output", "return", "result", "response", "generate", "produce"
            ],
            "process_keywords": [
                "處理", "執行", "運行", "計算", "轉換", "驗證", "檢查",
                "process", "execute", "run", "calculate", "transform", "validate", "check"
            ],
            "condition_keywords": [
                "如果", "當", "條件", "情況", "狀態", "模式",
                "if", "when", "condition", "case", "state", "mode"
            ],
            "constraint_keywords": [
                "限制", "約束", "規則", "要求", "標準", "規範",
                "constraint", "limitation", "rule", "requirement", "standard", "specification"
            ]
        }
    
    def _load_structure_patterns(self) -> Dict[str, str]:
        """加載結構模式"""
        return {
            "input_output_pattern": r"輸入[:：]\s*(.+?)\s*輸出[:：]\s*(.+)",
            "step_pattern": r"步驟\s*(\d+)[:：]\s*(.+)",
            "condition_pattern": r"(如果|當|若)\s*(.+?)\s*(則|那麼)\s*(.+)",
            "example_pattern": r"例如[:：]\s*(.+)",
            "constraint_pattern": r"(限制|約束|要求)[:：]\s*(.+)"
        }
    
    def _load_domain_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """加載領域知識"""
        return {
            "web_testing": {
                "common_inputs": ["URL", "表單數據", "用戶憑證", "HTTP頭"],
                "common_outputs": ["頁面內容", "狀態碼", "響應時間", "錯誤信息"],
                "common_actions": ["點擊", "輸入", "提交", "導航", "驗證"]
            },
            "api_testing": {
                "common_inputs": ["請求參數", "認證令牌", "請求體", "查詢參數"],
                "common_outputs": ["JSON響應", "狀態碼", "響應頭", "錯誤碼"],
                "common_actions": ["GET", "POST", "PUT", "DELETE", "驗證響應"]
            },
            "database_testing": {
                "common_inputs": ["SQL查詢", "數據記錄", "連接參數", "事務"],
                "common_outputs": ["查詢結果", "影響行數", "執行時間", "錯誤信息"],
                "common_actions": ["查詢", "插入", "更新", "刪除", "驗證數據"]
            }
        }
    
    def analyze_description(self, description: TextDescription) -> Dict[str, Any]:
        """分析文本描述"""
        logger.info(f"🔍 分析文本描述: {description.title}")
        
        analysis_result = {
            "input_analysis": self._analyze_input_section(description),
            "output_analysis": self._analyze_output_section(description),
            "process_analysis": self._analyze_process_section(description),
            "structure_analysis": self._analyze_structure(description),
            "domain_analysis": self._analyze_domain(description),
            "complexity_analysis": self._analyze_complexity(description)
        }
        
        return analysis_result
    
    def _analyze_input_section(self, description: TextDescription) -> Dict[str, Any]:
        """分析輸入部分"""
        input_text = description.input_description
        
        # 提取輸入類型
        input_types = []
        for keyword in self.keyword_patterns["input_keywords"]:
            if keyword in input_text.lower():
                input_types.append(keyword)
        
        # 提取參數信息
        parameters = self._extract_parameters(input_text)
        
        # 分析數據類型
        data_types = self._extract_data_types(input_text)
        
        return {
            "input_types": input_types,
            "parameters": parameters,
            "data_types": data_types,
            "complexity": len(parameters)
        }
    
    def _analyze_output_section(self, description: TextDescription) -> Dict[str, Any]:
        """分析輸出部分"""
        output_text = description.output_description
        
        # 提取輸出類型
        output_types = []
        for keyword in self.keyword_patterns["output_keywords"]:
            if keyword in output_text.lower():
                output_types.append(keyword)
        
        # 提取返回值信息
        return_values = self._extract_return_values(output_text)
        
        # 分析輸出格式
        output_formats = self._extract_output_formats(output_text)
        
        return {
            "output_types": output_types,
            "return_values": return_values,
            "output_formats": output_formats,
            "complexity": len(return_values)
        }
    
    def _analyze_process_section(self, description: TextDescription) -> Dict[str, Any]:
        """分析處理過程部分"""
        content = description.content
        implementation = description.implementation_details or ""
        
        # 提取處理步驟
        steps = self._extract_steps(content + " " + implementation)
        
        # 提取條件邏輯
        conditions = self._extract_conditions(content + " " + implementation)
        
        # 分析算法複雜度
        algorithm_complexity = self._analyze_algorithm_complexity(implementation)
        
        return {
            "steps": steps,
            "conditions": conditions,
            "algorithm_complexity": algorithm_complexity,
            "has_loops": "循環" in content or "loop" in content.lower(),
            "has_recursion": "遞歸" in content or "recursion" in content.lower()
        }
    
    def _analyze_structure(self, description: TextDescription) -> Dict[str, Any]:
        """分析文本結構"""
        full_text = f"{description.content} {description.input_description} {description.output_description}"
        
        structure_info = {}
        
        # 檢查各種結構模式
        for pattern_name, pattern in self.structure_patterns.items():
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                structure_info[pattern_name] = matches
        
        return structure_info
    
    def _analyze_domain(self, description: TextDescription) -> Dict[str, Any]:
        """分析領域特徵"""
        full_text = f"{description.title} {description.content}".lower()
        
        domain_scores = {}
        for domain, knowledge in self.domain_knowledge.items():
            score = 0
            total_terms = 0
            
            for category, terms in knowledge.items():
                for term in terms:
                    total_terms += 1
                    if term.lower() in full_text:
                        score += 1
            
            domain_scores[domain] = score / total_terms if total_terms > 0 else 0
        
        # 找出最匹配的領域
        best_domain = max(domain_scores.items(), key=lambda x: x[1])
        
        return {
            "domain_scores": domain_scores,
            "primary_domain": best_domain[0],
            "domain_confidence": best_domain[1]
        }
    
    def _analyze_complexity(self, description: TextDescription) -> Dict[str, Any]:
        """分析複雜度"""
        content_length = len(description.content)
        num_examples = len(description.examples)
        num_constraints = len(description.constraints)
        
        # 計算文本複雜度
        text_complexity = min(content_length / 1000, 1.0)  # 標準化到0-1
        
        # 計算邏輯複雜度
        logic_keywords = ["如果", "否則", "循環", "遞歸", "if", "else", "loop", "recursion"]
        logic_count = sum(1 for keyword in logic_keywords if keyword in description.content.lower())
        logic_complexity = min(logic_count / 10, 1.0)  # 標準化到0-1
        
        # 計算整體複雜度
        overall_complexity = (text_complexity + logic_complexity + num_constraints * 0.1) / 3
        
        return {
            "text_complexity": text_complexity,
            "logic_complexity": logic_complexity,
            "overall_complexity": overall_complexity,
            "complexity_level": self._get_complexity_level(overall_complexity)
        }
    
    def _extract_parameters(self, text: str) -> List[Dict[str, str]]:
        """提取參數信息"""
        parameters = []
        
        # 簡單的參數提取邏輯
        param_patterns = [
            r"參數\s*[:：]\s*(\w+)",
            r"輸入\s*[:：]\s*(\w+)",
            r"parameter\s*[:：]\s*(\w+)"
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                parameters.append({"name": match, "type": "unknown"})
        
        return parameters
    
    def _extract_data_types(self, text: str) -> List[str]:
        """提取數據類型"""
        type_keywords = [
            "字符串", "數字", "整數", "浮點", "布爾", "數組", "對象", "JSON",
            "string", "number", "integer", "float", "boolean", "array", "object", "json"
        ]
        
        found_types = []
        for type_keyword in type_keywords:
            if type_keyword.lower() in text.lower():
                found_types.append(type_keyword)
        
        return found_types
    
    def _extract_return_values(self, text: str) -> List[Dict[str, str]]:
        """提取返回值信息"""
        return_values = []
        
        # 簡單的返回值提取邏輯
        return_patterns = [
            r"返回\s*[:：]\s*(\w+)",
            r"輸出\s*[:：]\s*(\w+)",
            r"return\s*[:：]\s*(\w+)"
        ]
        
        for pattern in return_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                return_values.append({"name": match, "type": "unknown"})
        
        return return_values
    
    def _extract_output_formats(self, text: str) -> List[str]:
        """提取輸出格式"""
        format_keywords = [
            "JSON", "XML", "HTML", "CSV", "PDF", "圖片", "文本",
            "json", "xml", "html", "csv", "pdf", "image", "text"
        ]
        
        found_formats = []
        for format_keyword in format_keywords:
            if format_keyword.lower() in text.lower():
                found_formats.append(format_keyword)
        
        return found_formats
    
    def _extract_steps(self, text: str) -> List[str]:
        """提取處理步驟"""
        steps = []
        
        # 查找編號步驟
        step_pattern = r"步驟\s*(\d+)[:：]\s*(.+?)(?=步驟\s*\d+|$)"
        matches = re.findall(step_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for step_num, step_content in matches:
            steps.append(f"步驟{step_num}: {step_content.strip()}")
        
        # 如果沒有找到編號步驟，嘗試其他模式
        if not steps:
            # 查找以數字開頭的行
            numbered_lines = re.findall(r"^\d+\.\s*(.+)$", text, re.MULTILINE)
            steps.extend(numbered_lines)
        
        return steps
    
    def _extract_conditions(self, text: str) -> List[str]:
        """提取條件邏輯"""
        conditions = []
        
        condition_patterns = [
            r"(如果|若|當)\s*(.+?)\s*(則|那麼)\s*(.+)",
            r"if\s*(.+?)\s*then\s*(.+)",
            r"when\s*(.+?)\s*do\s*(.+)"
        ]
        
        for pattern in condition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    conditions.append(f"條件: {match[1]} -> 動作: {match[-1]}")
        
        return conditions
    
    def _analyze_algorithm_complexity(self, implementation: str) -> str:
        """分析算法複雜度"""
        if not implementation:
            return "unknown"
        
        impl_lower = implementation.lower()
        
        # 簡單的複雜度分析
        if "nested loop" in impl_lower or "雙重循環" in impl_lower:
            return "O(n²)"
        elif "loop" in impl_lower or "循環" in impl_lower:
            return "O(n)"
        elif "recursion" in impl_lower or "遞歸" in impl_lower:
            return "O(log n) or higher"
        else:
            return "O(1)"
    
    def _get_complexity_level(self, complexity_score: float) -> str:
        """獲取複雜度等級"""
        if complexity_score < 0.3:
            return "簡單"
        elif complexity_score < 0.6:
            return "中等"
        else:
            return "複雜"

class TemplateLearningSystem:
    """模板學習系統"""
    
    def __init__(self):
        self.pattern_database = {}
        self.template_cache = {}
        self.learning_history = []
    
    def learn_from_description(self, description: TextDescription, 
                             analysis_result: Dict[str, Any]) -> List[TemplatePattern]:
        """從描述中學習模板模式"""
        logger.info(f"📚 從描述中學習模板: {description.title}")
        
        patterns = []
        
        # 學習輸入模式
        input_patterns = self._learn_input_patterns(description, analysis_result)
        patterns.extend(input_patterns)
        
        # 學習輸出模式
        output_patterns = self._learn_output_patterns(description, analysis_result)
        patterns.extend(output_patterns)
        
        # 學習處理模式
        process_patterns = self._learn_process_patterns(description, analysis_result)
        patterns.extend(process_patterns)
        
        # 學習結構模式
        structure_patterns = self._learn_structure_patterns(description, analysis_result)
        patterns.extend(structure_patterns)
        
        # 更新模式數據庫
        self._update_pattern_database(patterns)
        
        return patterns
    
    def _learn_input_patterns(self, description: TextDescription, 
                            analysis: Dict[str, Any]) -> List[TemplatePattern]:
        """學習輸入模式"""
        patterns = []
        input_analysis = analysis.get("input_analysis", {})
        
        # 學習參數模式
        parameters = input_analysis.get("parameters", [])
        if parameters:
            pattern_content = {
                "parameter_count": len(parameters),
                "parameter_types": [p.get("type", "unknown") for p in parameters],
                "parameter_names": [p.get("name", "") for p in parameters]
            }
            
            pattern = TemplatePattern(
                pattern_id=f"input_param_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                pattern_type="input_parameters",
                pattern_content=json.dumps(pattern_content),
                confidence=0.8,
                frequency=1
            )
            patterns.append(pattern)
        
        # 學習數據類型模式
        data_types = input_analysis.get("data_types", [])
        if data_types:
            pattern_content = {
                "data_types": data_types,
                "type_count": len(data_types)
            }
            
            pattern = TemplatePattern(
                pattern_id=f"input_types_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                pattern_type="input_data_types",
                pattern_content=json.dumps(pattern_content),
                confidence=0.7,
                frequency=1
            )
            patterns.append(pattern)
        
        return patterns
    
    def _learn_output_patterns(self, description: TextDescription, 
                             analysis: Dict[str, Any]) -> List[TemplatePattern]:
        """學習輸出模式"""
        patterns = []
        output_analysis = analysis.get("output_analysis", {})
        
        # 學習返回值模式
        return_values = output_analysis.get("return_values", [])
        if return_values:
            pattern_content = {
                "return_count": len(return_values),
                "return_types": [r.get("type", "unknown") for r in return_values],
                "return_names": [r.get("name", "") for r in return_values]
            }
            
            pattern = TemplatePattern(
                pattern_id=f"output_return_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                pattern_type="output_returns",
                pattern_content=json.dumps(pattern_content),
                confidence=0.8,
                frequency=1
            )
            patterns.append(pattern)
        
        # 學習輸出格式模式
        output_formats = output_analysis.get("output_formats", [])
        if output_formats:
            pattern_content = {
                "formats": output_formats,
                "format_count": len(output_formats)
            }
            
            pattern = TemplatePattern(
                pattern_id=f"output_formats_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                pattern_type="output_formats",
                pattern_content=json.dumps(pattern_content),
                confidence=0.7,
                frequency=1
            )
            patterns.append(pattern)
        
        return patterns
    
    def _learn_process_patterns(self, description: TextDescription, 
                              analysis: Dict[str, Any]) -> List[TemplatePattern]:
        """學習處理模式"""
        patterns = []
        process_analysis = analysis.get("process_analysis", {})
        
        # 學習步驟模式
        steps = process_analysis.get("steps", [])
        if steps:
            pattern_content = {
                "step_count": len(steps),
                "steps": steps,
                "has_conditions": len(process_analysis.get("conditions", [])) > 0,
                "has_loops": process_analysis.get("has_loops", False),
                "has_recursion": process_analysis.get("has_recursion", False)
            }
            
            pattern = TemplatePattern(
                pattern_id=f"process_steps_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                pattern_type="process_steps",
                pattern_content=json.dumps(pattern_content),
                confidence=0.9,
                frequency=1
            )
            patterns.append(pattern)
        
        # 學習算法複雜度模式
        algorithm_complexity = process_analysis.get("algorithm_complexity", "unknown")
        if algorithm_complexity != "unknown":
            pattern_content = {
                "complexity": algorithm_complexity,
                "box_type": description.box_type.value
            }
            
            pattern = TemplatePattern(
                pattern_id=f"algorithm_complexity_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                pattern_type="algorithm_complexity",
                pattern_content=json.dumps(pattern_content),
                confidence=0.6,
                frequency=1
            )
            patterns.append(pattern)
        
        return patterns
    
    def _learn_structure_patterns(self, description: TextDescription, 
                                analysis: Dict[str, Any]) -> List[TemplatePattern]:
        """學習結構模式"""
        patterns = []
        structure_analysis = analysis.get("structure_analysis", {})
        
        for structure_type, matches in structure_analysis.items():
            if matches:
                pattern_content = {
                    "structure_type": structure_type,
                    "matches": matches,
                    "match_count": len(matches)
                }
                
                pattern = TemplatePattern(
                    pattern_id=f"structure_{structure_type}_{hashlib.md5(str(pattern_content).encode()).hexdigest()[:8]}",
                    pattern_type=f"structure_{structure_type}",
                    pattern_content=json.dumps(pattern_content),
                    confidence=0.7,
                    frequency=1
                )
                patterns.append(pattern)
        
        return patterns
    
    def _update_pattern_database(self, patterns: List[TemplatePattern]):
        """更新模式數據庫"""
        for pattern in patterns:
            if pattern.pattern_id in self.pattern_database:
                # 更新現有模式的頻率
                existing_pattern = self.pattern_database[pattern.pattern_id]
                existing_pattern.frequency += 1
                existing_pattern.confidence = min(existing_pattern.confidence + 0.1, 1.0)
            else:
                # 添加新模式
                self.pattern_database[pattern.pattern_id] = pattern
        
        logger.info(f"📊 模式數據庫已更新，當前包含 {len(self.pattern_database)} 個模式")

class TemplateEnrichmentEngine:
    """模板豐富引擎"""
    
    def __init__(self, text_analyzer: TextAnalysisEngine, learning_system: TemplateLearningSystem):
        self.text_analyzer = text_analyzer
        self.learning_system = learning_system
        self.enrichment_strategies = self._load_enrichment_strategies()
    
    def _load_enrichment_strategies(self) -> Dict[str, Callable]:
        """加載豐富化策略"""
        return {
            "variation_generation": self._generate_variations,
            "test_case_generation": self._generate_test_cases,
            "error_case_generation": self._generate_error_test_cases,
            "performance_scenarios": self._generate_performance_test_cases
        }
    
    def enrich_template(self, description: TextDescription) -> EnrichedTemplate:
        """豐富化模板"""
        logger.info(f"🔧 開始豐富化模板: {description.title}")
        
        # 分析文本描述
        analysis_result = self.text_analyzer.analyze_description(description)
        
        # 學習模式
        patterns = self.learning_system.learn_from_description(description, analysis_result)
        
        # 生成變體
        variations = self._generate_variations(description, analysis_result, patterns)
        
        # 生成測試用例
        test_cases = self._generate_test_cases(description, analysis_result, patterns)
        
        # 計算質量評分
        quality_score = self._calculate_quality_score(description, analysis_result, patterns)
        
        # 創建豐富化模板
        enriched_template = EnrichedTemplate(
            template_id=f"enriched_{hashlib.md5(description.content.encode()).hexdigest()[:8]}",
            original_description=description,
            extracted_patterns=patterns,
            generated_variations=variations,
            test_cases=test_cases,
            quality_score=quality_score,
            enrichment_metadata={
                "analysis_result": analysis_result,
                "enrichment_timestamp": datetime.now().isoformat(),
                "pattern_count": len(patterns),
                "variation_count": len(variations),
                "test_case_count": len(test_cases)
            }
        )
        
        logger.info(f"✅ 模板豐富化完成，質量評分: {quality_score:.2f}")
        return enriched_template
    
    def _generate_variations(self, description: TextDescription, 
                           analysis: Dict[str, Any], 
                           patterns: List[TemplatePattern]) -> List[Dict[str, Any]]:
        """生成模板變體"""
        variations = []
        
        # 基於輸入參數生成變體
        input_analysis = analysis.get("input_analysis", {})
        parameters = input_analysis.get("parameters", [])
        
        if parameters:
            # 參數數量變體
            variations.append({
                "type": "parameter_count_variation",
                "description": "減少參數數量的簡化版本",
                "changes": {"parameter_count": max(1, len(parameters) - 1)},
                "confidence": 0.7
            })
            
            variations.append({
                "type": "parameter_count_variation",
                "description": "增加參數數量的擴展版本",
                "changes": {"parameter_count": len(parameters) + 1},
                "confidence": 0.6
            })
        
        # 基於複雜度生成變體
        complexity_analysis = analysis.get("complexity_analysis", {})
        complexity_level = complexity_analysis.get("complexity_level", "中等")
        
        if complexity_level == "複雜":
            variations.append({
                "type": "complexity_reduction",
                "description": "簡化版本，降低複雜度",
                "changes": {"complexity_level": "簡單"},
                "confidence": 0.8
            })
        elif complexity_level == "簡單":
            variations.append({
                "type": "complexity_increase",
                "description": "增強版本，提高複雜度",
                "changes": {"complexity_level": "中等"},
                "confidence": 0.7
            })
        
        # 基於領域知識生成變體
        domain_analysis = analysis.get("domain_analysis", {})
        primary_domain = domain_analysis.get("primary_domain", "")
        
        if primary_domain:
            variations.append({
                "type": "domain_specific_variation",
                "description": f"針對{primary_domain}領域的專門化版本",
                "changes": {"domain_focus": primary_domain},
                "confidence": 0.8
            })
        
        return variations
    
    def _generate_test_cases(self, description: TextDescription, 
                           analysis: Dict[str, Any], 
                           patterns: List[TemplatePattern]) -> List[Dict[str, Any]]:
        """生成測試用例"""
        test_cases = []
        
        # 基本功能測試用例
        test_cases.append({
            "type": "basic_functionality",
            "title": "基本功能測試",
            "description": f"測試{description.title}的基本功能",
            "priority": "high",
            "test_data": self._generate_basic_test_data(description, analysis),
            "expected_result": "功能正常執行",
            "confidence": 0.9
        })
        
        # 邊界條件測試用例
        boundary_cases = self._generate_boundary_test_cases(description, analysis)
        test_cases.extend(boundary_cases)
        
        # 錯誤處理測試用例
        error_cases = self._generate_error_test_cases(description, analysis)
        test_cases.extend(error_cases)
        
        # 性能測試用例
        if description.category in [TemplateCategory.PERFORMANCE, TemplateCategory.API]:
            performance_cases = self._generate_performance_test_cases(description, analysis)
            test_cases.extend(performance_cases)
        
        # 安全測試用例
        if description.category == TemplateCategory.SECURITY:
            security_cases = self._generate_security_test_cases(description, analysis)
            test_cases.extend(security_cases)
        
        return test_cases
    
    def _generate_basic_test_data(self, description: TextDescription, 
                                analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成基本測試數據"""
        input_analysis = analysis.get("input_analysis", {})
        parameters = input_analysis.get("parameters", [])
        data_types = input_analysis.get("data_types", [])
        
        test_data = {}
        
        for i, param in enumerate(parameters):
            param_name = param.get("name", f"param_{i}")
            
            # 根據數據類型生成測試數據
            if "字符串" in data_types or "string" in data_types:
                test_data[param_name] = "test_string"
            elif "數字" in data_types or "number" in data_types:
                test_data[param_name] = 123
            elif "布爾" in data_types or "boolean" in data_types:
                test_data[param_name] = True
            else:
                test_data[param_name] = "test_value"
        
        return test_data
    
    def _generate_boundary_test_cases(self, description: TextDescription, 
                                    analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成邊界條件測試用例"""
        boundary_cases = []
        
        # 空值測試
        boundary_cases.append({
            "type": "boundary_null",
            "title": "空值邊界測試",
            "description": "測試空值輸入的處理",
            "priority": "medium",
            "test_data": {"input": None},
            "expected_result": "正確處理空值或拋出適當錯誤",
            "confidence": 0.8
        })
        
        # 最大值測試
        boundary_cases.append({
            "type": "boundary_max",
            "title": "最大值邊界測試",
            "description": "測試最大值輸入的處理",
            "priority": "medium",
            "test_data": {"input": "max_value"},
            "expected_result": "正確處理最大值",
            "confidence": 0.7
        })
        
        # 最小值測試
        boundary_cases.append({
            "type": "boundary_min",
            "title": "最小值邊界測試",
            "description": "測試最小值輸入的處理",
            "priority": "medium",
            "test_data": {"input": "min_value"},
            "expected_result": "正確處理最小值",
            "confidence": 0.7
        })
        
        return boundary_cases
    
    def _generate_error_test_cases(self, description: TextDescription, 
                                 analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成錯誤處理測試用例"""
        error_cases = []
        
        # 無效輸入測試
        error_cases.append({
            "type": "error_invalid_input",
            "title": "無效輸入測試",
            "description": "測試無效輸入的錯誤處理",
            "priority": "high",
            "test_data": {"input": "invalid_data"},
            "expected_result": "拋出適當的錯誤信息",
            "confidence": 0.8
        })
        
        # 類型錯誤測試
        error_cases.append({
            "type": "error_type_mismatch",
            "title": "類型錯誤測試",
            "description": "測試類型不匹配的錯誤處理",
            "priority": "medium",
            "test_data": {"input": "wrong_type"},
            "expected_result": "拋出類型錯誤",
            "confidence": 0.7
        })
        
        return error_cases
    
    def _generate_performance_test_cases(self, description: TextDescription, 
                                       analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成性能測試用例"""
        performance_cases = []
        
        # 響應時間測試
        performance_cases.append({
            "type": "performance_response_time",
            "title": "響應時間測試",
            "description": "測試功能的響應時間",
            "priority": "medium",
            "test_data": {"load": "normal"},
            "expected_result": "響應時間在可接受範圍內",
            "confidence": 0.7
        })
        
        # 負載測試
        performance_cases.append({
            "type": "performance_load",
            "title": "負載測試",
            "description": "測試高負載下的性能",
            "priority": "medium",
            "test_data": {"load": "high"},
            "expected_result": "在高負載下保持穩定性能",
            "confidence": 0.6
        })
        
        return performance_cases
    
    def _generate_security_test_cases(self, description: TextDescription, 
                                    analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成安全測試用例"""
        security_cases = []
        
        # SQL注入測試
        security_cases.append({
            "type": "security_sql_injection",
            "title": "SQL注入測試",
            "description": "測試SQL注入攻擊的防護",
            "priority": "high",
            "test_data": {"input": "'; DROP TABLE users; --"},
            "expected_result": "成功防止SQL注入攻擊",
            "confidence": 0.8
        })
        
        # XSS測試
        security_cases.append({
            "type": "security_xss",
            "title": "XSS攻擊測試",
            "description": "測試跨站腳本攻擊的防護",
            "priority": "high",
            "test_data": {"input": "<script>alert('xss')</script>"},
            "expected_result": "成功防止XSS攻擊",
            "confidence": 0.8
        })
        
        return security_cases
    
    def _calculate_quality_score(self, description: TextDescription, 
                               analysis: Dict[str, Any], 
                               patterns: List[TemplatePattern]) -> float:
        """計算質量評分"""
        score = 0.0
        
        # 基於描述完整性評分 (30%)
        completeness_score = 0.0
        if description.input_description:
            completeness_score += 0.3
        if description.output_description:
            completeness_score += 0.3
        if description.implementation_details:
            completeness_score += 0.2
        if description.examples:
            completeness_score += 0.1
        if description.constraints:
            completeness_score += 0.1
        
        score += completeness_score * 0.3
        
        # 基於分析深度評分 (25%)
        analysis_score = 0.0
        complexity_analysis = analysis.get("complexity_analysis", {})
        domain_analysis = analysis.get("domain_analysis", {})
        
        if complexity_analysis.get("overall_complexity", 0) > 0:
            analysis_score += 0.4
        if domain_analysis.get("domain_confidence", 0) > 0.5:
            analysis_score += 0.3
        if analysis.get("structure_analysis", {}):
            analysis_score += 0.3
        
        score += analysis_score * 0.25
        
        # 基於模式數量評分 (20%)
        pattern_score = min(len(patterns) / 10, 1.0)  # 最多10個模式得滿分
        score += pattern_score * 0.2
        
        # 基於模式質量評分 (25%)
        if patterns:
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            score += avg_confidence * 0.25
        
        return min(score, 1.0)

# 測試函數
def test_template_enrichment_system():
    """測試模板豐富系統"""
    print("🧪 測試黑白盒模板豐富系統")
    print("=" * 80)
    
    # 創建系統組件
    text_analyzer = TextAnalysisEngine()
    learning_system = TemplateLearningSystem()
    enrichment_engine = TemplateEnrichmentEngine(text_analyzer, learning_system)
    
    # 測試用例1: 黑盒描述
    black_box_description = TextDescription(
        description_id="test_black_001",
        box_type=BoxType.BLACK_BOX,
        category=TemplateCategory.API,
        title="用戶登錄API",
        content="這是一個用戶登錄的API接口，用於驗證用戶身份",
        input_description="輸入用戶名和密碼",
        output_description="返回登錄結果和用戶信息",
        examples=[
            {"input": {"username": "test", "password": "123456"}, "output": {"success": True, "user_id": 1}}
        ],
        constraints=["用戶名不能為空", "密碼長度至少6位"],
        tags=["authentication", "api", "security"]
    )
    
    # 測試用例2: 白盒描述
    white_box_description = TextDescription(
        description_id="test_white_001",
        box_type=BoxType.WHITE_BOX,
        category=TemplateCategory.FUNCTIONAL,
        title="排序算法實現",
        content="實現快速排序算法對數組進行排序",
        input_description="輸入一個整數數組",
        output_description="返回排序後的數組",
        implementation_details="""
        步驟1: 選擇基準元素
        步驟2: 分割數組為小於和大於基準的兩部分
        步驟3: 遞歸排序兩個子數組
        步驟4: 合併結果
        算法複雜度: O(n log n)
        """,
        examples=[
            {"input": [3, 1, 4, 1, 5], "output": [1, 1, 3, 4, 5]}
        ],
        constraints=["數組長度不超過10000", "元素為整數"],
        tags=["algorithm", "sorting", "recursion"]
    )
    
    # 測試黑盒模板豐富
    print("\n🔍 測試黑盒模板豐富")
    print("-" * 60)
    black_box_enriched = enrichment_engine.enrich_template(black_box_description)
    
    print(f"✅ 黑盒模板豐富完成")
    print(f"📊 質量評分: {black_box_enriched.quality_score:.2f}")
    print(f"🔧 提取模式數: {len(black_box_enriched.extracted_patterns)}")
    print(f"🔄 生成變體數: {len(black_box_enriched.generated_variations)}")
    print(f"🧪 測試用例數: {len(black_box_enriched.test_cases)}")
    
    # 測試白盒模板豐富
    print("\n🔍 測試白盒模板豐富")
    print("-" * 60)
    white_box_enriched = enrichment_engine.enrich_template(white_box_description)
    
    print(f"✅ 白盒模板豐富完成")
    print(f"📊 質量評分: {white_box_enriched.quality_score:.2f}")
    print(f"🔧 提取模式數: {len(white_box_enriched.extracted_patterns)}")
    print(f"🔄 生成變體數: {len(white_box_enriched.generated_variations)}")
    print(f"🧪 測試用例數: {len(white_box_enriched.test_cases)}")
    
    # 顯示學習到的模式
    print(f"\n📚 學習系統統計")
    print("-" * 60)
    print(f"模式數據庫大小: {len(learning_system.pattern_database)}")
    
    for pattern_id, pattern in list(learning_system.pattern_database.items())[:3]:
        print(f"  📋 模式: {pattern.pattern_type}")
        print(f"     信心度: {pattern.confidence:.2f}")
        print(f"     頻率: {pattern.frequency}")
    
    print("\n🎉 黑白盒模板豐富系統測試完成！")
    
    return {
        "black_box_result": black_box_enriched,
        "white_box_result": white_box_enriched,
        "learning_system": learning_system
    }

if __name__ == "__main__":
    test_template_enrichment_system()

