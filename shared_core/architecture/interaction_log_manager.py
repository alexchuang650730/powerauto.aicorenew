#!/usr/bin/env python3
"""
PowerAutomation 交互日誌管理系統

實現交互日誌的分類存儲、KiloCode RAG整合、交付件模板化和Readiness檢查
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

class InteractionType(Enum):
    """交互類型枚舉"""
    TECHNICAL_ANALYSIS = "technical_analysis"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PRESENTATION = "presentation"
    DATA_ANALYSIS = "data_analysis"
    SYSTEM_DESIGN = "system_design"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"

class DeliverableType(Enum):
    """交付件類型枚舉"""
    PYTHON_CODE = "python_code"
    MARKDOWN_DOC = "markdown_doc"
    JSON_DATA = "json_data"
    HTML_SLIDES = "html_slides"
    TEST_SUITE = "test_suite"
    CONFIG_FILE = "config_file"
    ANALYSIS_REPORT = "analysis_report"
    SYSTEM_ARCHITECTURE = "system_architecture"
    API_SPECIFICATION = "api_specification"
    DATABASE_SCHEMA = "database_schema"

@dataclass
class InteractionLog:
    """交互日誌數據結構"""
    session_id: str
    timestamp: str
    interaction_type: InteractionType
    user_request: str
    agent_response: str
    deliverables: List[Dict[str, Any]]
    context: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    tags: List[str]

@dataclass
class Deliverable:
    """交付件數據結構"""
    id: str
    type: DeliverableType
    name: str
    content: str
    file_path: str
    metadata: Dict[str, Any]
    template_potential: float  # 模板化潛力評分

class InteractionLogManager:
    """交互日誌管理器"""
    
    def __init__(self, base_dir: str = "/home/ubuntu/Powerauto.ai/interaction_logs"):
        self.base_dir = Path(base_dir)
        self.setup_logging()
        self.setup_directory_structure()
        self.current_session_id = self.generate_session_id()
        
    def setup_directory_structure(self):
        """設置目錄結構"""
        directories = [
            "logs/technical_analysis",
            "logs/code_generation", 
            "logs/testing",
            "logs/documentation",
            "logs/presentation",
            "logs/data_analysis",
            "logs/system_design",
            "logs/research",
            "logs/debugging",
            "logs/optimization",
            "deliverables/python_code",
            "deliverables/markdown_doc",
            "deliverables/json_data",
            "deliverables/html_slides",
            "deliverables/test_suite",
            "deliverables/config_file",
            "deliverables/analysis_report",
            "deliverables/system_architecture",
            "deliverables/api_specification",
            "deliverables/database_schema",
            "templates/kilocode",
            "rag/embeddings",
            "rag/index",
            "readiness/checks",
            "readiness/reports"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
            
        self.logger.info(f"✅ 目錄結構已設置: {self.base_dir}")
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_session_id(self) -> str:
        """生成會話ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_hash}"
    
    def classify_interaction(self, user_request: str, agent_response: str) -> InteractionType:
        """分類交互類型"""
        request_lower = user_request.lower()
        response_lower = agent_response.lower()
        
        # 基於關鍵詞的分類邏輯
        if any(keyword in request_lower for keyword in ['分析', 'analysis', '技術', 'technical']):
            return InteractionType.TECHNICAL_ANALYSIS
        elif any(keyword in request_lower for keyword in ['代碼', 'code', '編程', 'programming']):
            return InteractionType.CODE_GENERATION
        elif any(keyword in request_lower for keyword in ['測試', 'test', '驗證', 'validation']):
            return InteractionType.TESTING
        elif any(keyword in request_lower for keyword in ['文檔', 'document', '報告', 'report']):
            return InteractionType.DOCUMENTATION
        elif any(keyword in request_lower for keyword in ['演示', 'presentation', '幻燈片', 'slides']):
            return InteractionType.PRESENTATION
        elif any(keyword in request_lower for keyword in ['數據', 'data', '統計', 'statistics']):
            return InteractionType.DATA_ANALYSIS
        elif any(keyword in request_lower for keyword in ['設計', 'design', '架構', 'architecture']):
            return InteractionType.SYSTEM_DESIGN
        elif any(keyword in request_lower for keyword in ['研究', 'research', '調查', 'investigation']):
            return InteractionType.RESEARCH
        elif any(keyword in request_lower for keyword in ['調試', 'debug', '修復', 'fix']):
            return InteractionType.DEBUGGING
        elif any(keyword in request_lower for keyword in ['優化', 'optimize', '改進', 'improve']):
            return InteractionType.OPTIMIZATION
        else:
            return InteractionType.TECHNICAL_ANALYSIS  # 默認分類
    
    def classify_deliverable(self, file_path: str, content: str) -> DeliverableType:
        """分類交付件類型"""
        file_ext = Path(file_path).suffix.lower()
        content_sample = content[:500].lower()
        
        if file_ext == '.py' or 'python' in content_sample:
            return DeliverableType.PYTHON_CODE
        elif file_ext == '.md' or 'markdown' in content_sample:
            return DeliverableType.MARKDOWN_DOC
        elif file_ext == '.json' or content_sample.strip().startswith('{'):
            return DeliverableType.JSON_DATA
        elif file_ext == '.html' or 'slides' in content_sample:
            return DeliverableType.HTML_SLIDES
        elif 'test' in file_path.lower() or 'unittest' in content_sample:
            return DeliverableType.TEST_SUITE
        elif file_ext in ['.yaml', '.yml', '.conf', '.ini']:
            return DeliverableType.CONFIG_FILE
        elif 'analysis' in content_sample or 'report' in content_sample:
            return DeliverableType.ANALYSIS_REPORT
        elif 'architecture' in content_sample or 'design' in content_sample:
            return DeliverableType.SYSTEM_ARCHITECTURE
        elif 'api' in content_sample or 'endpoint' in content_sample:
            return DeliverableType.API_SPECIFICATION
        elif 'schema' in content_sample or 'database' in content_sample:
            return DeliverableType.DATABASE_SCHEMA
        else:
            return DeliverableType.MARKDOWN_DOC  # 默認類型
    
    def calculate_template_potential(self, deliverable: Dict[str, Any]) -> float:
        """計算交付件的模板化潛力"""
        content = deliverable.get('content', '')
        file_path = deliverable.get('file_path', '')
        
        score = 0.0
        
        # 代碼結構化程度
        if deliverable['type'] == DeliverableType.PYTHON_CODE:
            if 'class ' in content:
                score += 0.3
            if 'def ' in content:
                score += 0.2
            if 'import ' in content:
                score += 0.1
        
        # 文檔結構化程度
        elif deliverable['type'] == DeliverableType.MARKDOWN_DOC:
            if content.count('#') >= 3:  # 多級標題
                score += 0.3
            if '```' in content:  # 代碼塊
                score += 0.2
            if '|' in content:  # 表格
                score += 0.1
        
        # 配置文件結構
        elif deliverable['type'] == DeliverableType.JSON_DATA:
            try:
                data = json.loads(content)
                if isinstance(data, dict) and len(data) > 3:
                    score += 0.4
            except:
                pass
        
        # 通用評分因素
        if len(content) > 1000:  # 內容豐富度
            score += 0.2
        if len(content.split('\n')) > 20:  # 行數
            score += 0.1
        
        return min(score, 1.0)
    
    def log_interaction(self, user_request: str, agent_response: str, 
                       deliverables: List[str] = None, context: Dict = None) -> str:
        """記錄交互日誌"""
        
        # 分類交互類型
        interaction_type = self.classify_interaction(user_request, agent_response)
        
        # 處理交付件
        processed_deliverables = []
        if deliverables:
            for file_path in deliverables:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    deliverable_type = self.classify_deliverable(file_path, content)
                    template_potential = self.calculate_template_potential({
                        'type': deliverable_type,
                        'content': content,
                        'file_path': file_path
                    })
                    
                    deliverable = {
                        'id': hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()[:12],
                        'type': deliverable_type.value,
                        'name': Path(file_path).name,
                        'content': content,
                        'file_path': file_path,
                        'template_potential': template_potential,
                        'metadata': {
                            'size': len(content),
                            'lines': len(content.split('\n')),
                            'created_at': datetime.now().isoformat()
                        }
                    }
                    processed_deliverables.append(deliverable)
        
        # 創建交互日誌
        log_entry = InteractionLog(
            session_id=self.current_session_id,
            timestamp=datetime.now().isoformat(),
            interaction_type=interaction_type,
            user_request=user_request,
            agent_response=agent_response,
            deliverables=processed_deliverables,
            context=context or {},
            performance_metrics={
                'response_time': time.time(),
                'deliverable_count': len(processed_deliverables),
                'total_content_size': sum(len(d['content']) for d in processed_deliverables)
            },
            tags=self.generate_tags(user_request, agent_response, processed_deliverables)
        )
        
        # 保存日誌
        log_id = self.save_interaction_log(log_entry)
        
        # 保存交付件
        self.save_deliverables(processed_deliverables)
        
        # 生成模板
        self.generate_templates(processed_deliverables)
        
        self.logger.info(f"✅ 交互日誌已記錄: {log_id}")
        return log_id
    
    def generate_tags(self, user_request: str, agent_response: str, 
                     deliverables: List[Dict]) -> List[str]:
        """生成標籤"""
        tags = []
        
        # 基於請求內容的標籤
        request_words = user_request.lower().split()
        common_tags = ['gaia', 'test', 'analysis', 'code', 'mcp', 'ai', 'automation']
        tags.extend([tag for tag in common_tags if tag in ' '.join(request_words)])
        
        # 基於交付件類型的標籤
        for deliverable in deliverables:
            tags.append(deliverable['type'])
            if deliverable['template_potential'] > 0.7:
                tags.append('high_template_potential')
        
        return list(set(tags))
    
    def save_interaction_log(self, log_entry: InteractionLog) -> str:
        """保存交互日誌"""
        log_id = hashlib.md5(f"{log_entry.session_id}{log_entry.timestamp}".encode()).hexdigest()[:12]
        
        # 按類型分類保存
        log_dir = self.base_dir / "logs" / log_entry.interaction_type.value
        log_file = log_dir / f"{log_id}.json"
        
        # 轉換為可序列化的字典
        log_dict = asdict(log_entry)
        log_dict['interaction_type'] = log_entry.interaction_type.value
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_dict, f, indent=2, ensure_ascii=False)
        
        return log_id
    
    def save_deliverables(self, deliverables: List[Dict]):
        """保存交付件"""
        for deliverable in deliverables:
            # 按類型分類保存
            deliverable_dir = self.base_dir / "deliverables" / deliverable['type']
            deliverable_file = deliverable_dir / f"{deliverable['id']}_{deliverable['name']}"
            
            with open(deliverable_file, 'w', encoding='utf-8') as f:
                f.write(deliverable['content'])
            
            # 保存元數據
            metadata_file = deliverable_dir / f"{deliverable['id']}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'id': deliverable['id'],
                    'type': deliverable['type'],
                    'name': deliverable['name'],
                    'template_potential': deliverable['template_potential'],
                    'metadata': deliverable['metadata']
                }, f, indent=2, ensure_ascii=False)
    
    def generate_templates(self, deliverables: List[Dict]):
        """生成KiloCode模板"""
        for deliverable in deliverables:
            if deliverable['template_potential'] > 0.6:  # 高潛力交付件
                template = self.create_kilocode_template(deliverable)
                
                template_dir = self.base_dir / "templates" / "kilocode"
                template_file = template_dir / f"{deliverable['type']}_{deliverable['id']}.json"
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"✅ KiloCode模板已生成: {template_file}")
    
    def create_kilocode_template(self, deliverable: Dict) -> Dict:
        """創建KiloCode模板"""
        template = {
            'template_id': f"kilocode_{deliverable['id']}",
            'name': f"{deliverable['type']} Template",
            'description': f"Auto-generated template from {deliverable['name']}",
            'type': deliverable['type'],
            'template_potential': deliverable['template_potential'],
            'parameters': self.extract_parameters(deliverable['content']),
            'structure': self.analyze_structure(deliverable['content']),
            'content_template': self.create_content_template(deliverable['content']),
            'usage_examples': self.generate_usage_examples(deliverable),
            'metadata': {
                'source_deliverable_id': deliverable['id'],
                'created_at': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        return template
    
    def extract_parameters(self, content: str) -> List[Dict]:
        """提取可參數化的部分"""
        parameters = []
        
        # 提取Python變量
        if 'def ' in content:
            import re
            functions = re.findall(r'def\s+(\w+)\s*\((.*?)\):', content)
            for func_name, params in functions:
                parameters.append({
                    'name': f"{func_name}_params",
                    'type': 'function_parameters',
                    'value': params,
                    'description': f"Parameters for function {func_name}"
                })
        
        # 提取配置值
        if '=' in content:
            import re
            assignments = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
            for var_name, value in assignments:
                parameters.append({
                    'name': var_name,
                    'type': 'string_variable',
                    'value': value,
                    'description': f"Configurable variable {var_name}"
                })
        
        return parameters
    
    def analyze_structure(self, content: str) -> Dict:
        """分析內容結構"""
        structure = {
            'total_lines': len(content.split('\n')),
            'total_chars': len(content),
            'sections': [],
            'code_blocks': 0,
            'functions': 0,
            'classes': 0
        }
        
        lines = content.split('\n')
        
        # 分析Markdown結構
        for i, line in enumerate(lines):
            if line.startswith('#'):
                structure['sections'].append({
                    'level': len(line) - len(line.lstrip('#')),
                    'title': line.strip('#').strip(),
                    'line_number': i + 1
                })
            elif line.strip().startswith('```'):
                structure['code_blocks'] += 1
            elif line.strip().startswith('def '):
                structure['functions'] += 1
            elif line.strip().startswith('class '):
                structure['classes'] += 1
        
        return structure
    
    def create_content_template(self, content: str) -> str:
        """創建內容模板"""
        # 簡單的模板化：將具體值替換為佔位符
        template = content
        
        # 替換常見的可變部分
        import re
        
        # 替換日期
        template = re.sub(r'\d{4}-\d{2}-\d{2}', '{{DATE}}', template)
        
        # 替換時間戳
        template = re.sub(r'\d{10,}', '{{TIMESTAMP}}', template)
        
        # 替換文件路徑
        template = re.sub(r'/[a-zA-Z0-9_/.-]+\.(py|md|json|html)', '{{FILE_PATH}}', template)
        
        # 替換數字
        template = re.sub(r'\b\d+\.\d+\b', '{{FLOAT_VALUE}}', template)
        template = re.sub(r'\b\d+\b', '{{INTEGER_VALUE}}', template)
        
        return template
    
    def generate_usage_examples(self, deliverable: Dict) -> List[Dict]:
        """生成使用示例"""
        examples = []
        
        if deliverable['type'] == 'python_code':
            examples.append({
                'title': 'Basic Usage',
                'description': 'How to use this Python code template',
                'code': f"# Import and use the generated code\n# from {deliverable['name']} import *"
            })
        
        elif deliverable['type'] == 'markdown_doc':
            examples.append({
                'title': 'Documentation Template',
                'description': 'How to customize this documentation template',
                'code': f"# Customize the sections and content\n# Replace {{PLACEHOLDERS}} with actual values"
            })
        
        return examples

class KiloCodeRAGIntegration:
    """KiloCode RAG整合系統"""
    
    def __init__(self, log_manager: InteractionLogManager):
        self.log_manager = log_manager
        self.rag_dir = log_manager.base_dir / "rag"
        self.setup_rag_system()
    
    def setup_rag_system(self):
        """設置RAG系統"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔍 設置KiloCode RAG系統...")
    
    def index_interactions(self):
        """索引所有交互日誌"""
        # 實現RAG索引邏輯
        pass
    
    def search_similar_interactions(self, query: str) -> List[Dict]:
        """搜索相似交互"""
        # 實現相似性搜索
        pass

class ReadinessChecker:
    """系統準備狀態檢查器"""
    
    def __init__(self, log_manager: InteractionLogManager):
        self.log_manager = log_manager
        self.readiness_dir = log_manager.base_dir / "readiness"
    
    def check_system_readiness(self) -> Dict[str, Any]:
        """檢查系統準備狀態"""
        readiness_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'checking',
            'components': {},
            'recommendations': []
        }
        
        # 檢查目錄結構
        readiness_report['components']['directory_structure'] = self.check_directory_structure()
        
        # 檢查日誌數量
        readiness_report['components']['log_coverage'] = self.check_log_coverage()
        
        # 檢查模板質量
        readiness_report['components']['template_quality'] = self.check_template_quality()
        
        # 檢查RAG準備狀態
        readiness_report['components']['rag_readiness'] = self.check_rag_readiness()
        
        # 計算總體狀態
        readiness_report['overall_status'] = self.calculate_overall_status(readiness_report['components'])
        
        # 生成建議
        readiness_report['recommendations'] = self.generate_recommendations(readiness_report['components'])
        
        return readiness_report
    
    def check_directory_structure(self) -> Dict[str, Any]:
        """檢查目錄結構"""
        required_dirs = [
            "logs", "deliverables", "templates", "rag", "readiness"
        ]
        
        status = {
            'status': 'pass',
            'missing_dirs': [],
            'existing_dirs': []
        }
        
        for dir_name in required_dirs:
            dir_path = self.log_manager.base_dir / dir_name
            if dir_path.exists():
                status['existing_dirs'].append(dir_name)
            else:
                status['missing_dirs'].append(dir_name)
        
        if status['missing_dirs']:
            status['status'] = 'fail'
        
        return status
    
    def check_log_coverage(self) -> Dict[str, Any]:
        """檢查日誌覆蓋度"""
        log_types = [t.value for t in InteractionType]
        coverage = {}
        
        for log_type in log_types:
            log_dir = self.log_manager.base_dir / "logs" / log_type
            if log_dir.exists():
                log_count = len(list(log_dir.glob("*.json")))
                coverage[log_type] = log_count
            else:
                coverage[log_type] = 0
        
        total_logs = sum(coverage.values())
        covered_types = len([t for t, count in coverage.items() if count > 0])
        
        return {
            'status': 'pass' if covered_types >= len(log_types) * 0.7 else 'warning',
            'total_logs': total_logs,
            'covered_types': covered_types,
            'total_types': len(log_types),
            'coverage_percentage': (covered_types / len(log_types)) * 100,
            'details': coverage
        }
    
    def check_template_quality(self) -> Dict[str, Any]:
        """檢查模板質量"""
        template_dir = self.log_manager.base_dir / "templates" / "kilocode"
        
        if not template_dir.exists():
            return {'status': 'fail', 'reason': 'Template directory not found'}
        
        templates = list(template_dir.glob("*.json"))
        high_quality_templates = 0
        
        for template_file in templates:
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                
                if template.get('template_potential', 0) > 0.7:
                    high_quality_templates += 1
            except:
                continue
        
        quality_ratio = high_quality_templates / len(templates) if templates else 0
        
        return {
            'status': 'pass' if quality_ratio > 0.5 else 'warning',
            'total_templates': len(templates),
            'high_quality_templates': high_quality_templates,
            'quality_ratio': quality_ratio
        }
    
    def check_rag_readiness(self) -> Dict[str, Any]:
        """檢查RAG準備狀態"""
        rag_dir = self.log_manager.base_dir / "rag"
        
        return {
            'status': 'pass' if rag_dir.exists() else 'warning',
            'embeddings_ready': (rag_dir / "embeddings").exists(),
            'index_ready': (rag_dir / "index").exists()
        }
    
    def calculate_overall_status(self, components: Dict[str, Any]) -> str:
        """計算總體狀態"""
        statuses = [comp.get('status', 'unknown') for comp in components.values()]
        
        if all(status == 'pass' for status in statuses):
            return 'ready'
        elif any(status == 'fail' for status in statuses):
            return 'not_ready'
        else:
            return 'partially_ready'
    
    def generate_recommendations(self, components: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        
        if components['directory_structure']['status'] == 'fail':
            recommendations.append("創建缺失的目錄結構")
        
        if components['log_coverage']['coverage_percentage'] < 70:
            recommendations.append("增加更多類型的交互日誌")
        
        if components['template_quality']['quality_ratio'] < 0.5:
            recommendations.append("提高模板質量，增加高潛力交付件")
        
        if not components['rag_readiness']['embeddings_ready']:
            recommendations.append("設置RAG嵌入系統")
        
        return recommendations

def main():
    """主函數 - 演示系統使用"""
    
    # 初始化交互日誌管理器
    log_manager = InteractionLogManager()
    
    # 模擬記錄當前交互
    user_request = "設計交互日誌管理系統，包括分類存儲、KiloCode RAG整合、交付件模板化"
    agent_response = "已設計完整的交互日誌管理系統架構，包含分類存儲、模板化和RAG整合功能"
    
    # 記錄交互（假設有交付件）
    deliverables = [
        "/home/ubuntu/Powerauto.ai/interaction_log_manager.py"  # 當前文件
    ]
    
    log_id = log_manager.log_interaction(
        user_request=user_request,
        agent_response=agent_response,
        deliverables=deliverables,
        context={'task': 'system_design', 'priority': 'high'}
    )
    
    # 檢查系統準備狀態
    readiness_checker = ReadinessChecker(log_manager)
    readiness_report = readiness_checker.check_system_readiness()
    
    # 保存準備狀態報告
    report_file = log_manager.base_dir / "readiness" / "reports" / f"readiness_report_{int(time.time())}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(readiness_report, f, indent=2, ensure_ascii=False)
    
    print("🎯 交互日誌管理系統演示完成")
    print(f"📝 交互日誌ID: {log_id}")
    print(f"📊 系統狀態: {readiness_report['overall_status']}")
    print(f"📋 準備狀態報告: {report_file}")
    
    return log_manager, readiness_report

if __name__ == "__main__":
    main()

