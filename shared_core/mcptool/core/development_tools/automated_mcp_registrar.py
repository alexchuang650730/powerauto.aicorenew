#!/usr/bin/env python3
"""
自動化MCP註冊器

與Release Manager集成，實現MCP的自動化註冊和管理
"""

import os
import sys
import json
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class AutomatedMCPRegistrar:
    """自動化MCP註冊器"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.adapters_dir = self.project_dir / "mcptool" / "adapters"
        self.registry_file = self.adapters_dir / "core" / "safe_mcp_registry.py"
        
        # 註冊狀態
        self.registration_log = []
        self.discovered_mcps = []
        self.registered_mcps = []
        self.failed_registrations = []
        
        # MCP識別模式
        self.mcp_patterns = [
            "_mcp.py",
            "_adapter.py", 
            "_engine.py",
            "mcp_",
            "adapter_"
        ]
        
        # 排除模式
        self.exclude_patterns = [
            "__pycache__",
            ".pyc",
            "test_",
            "_test.py",
            "example_",
            "demo_"
        ]
        
        logger.info(f"AutomatedMCPRegistrar初始化完成，項目目錄: {project_dir}")
    
    def discover_mcps(self) -> List[Dict[str, Any]]:
        """發現所有MCP文件"""
        discovered = []
        
        # 遞歸掃描adapters目錄
        for root, dirs, files in os.walk(self.adapters_dir):
            # 跳過排除的目錄
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in self.exclude_patterns)]
            
            for file in files:
                if self._is_mcp_file(file):
                    file_path = Path(root) / file
                    mcp_info = self._analyze_mcp_file(file_path)
                    if mcp_info:
                        discovered.append(mcp_info)
        
        self.discovered_mcps = discovered
        logger.info(f"發現 {len(discovered)} 個MCP文件")
        return discovered
    
    def _is_mcp_file(self, filename: str) -> bool:
        """判斷是否為MCP文件"""
        if not filename.endswith('.py'):
            return False
        
        # 檢查排除模式
        if any(pattern in filename for pattern in self.exclude_patterns):
            return False
        
        # 檢查MCP模式
        return any(pattern in filename for pattern in self.mcp_patterns)
    
    def _analyze_mcp_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """分析MCP文件"""
        try:
            # 讀取文件內容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本信息
            relative_path = file_path.relative_to(self.project_dir)
            module_path = str(relative_path).replace('/', '.').replace('.py', '')
            
            mcp_info = {
                'file_path': str(file_path),
                'relative_path': str(relative_path),
                'module_path': module_path,
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'classes': [],
                'functions': [],
                'imports': [],
                'capabilities': [],
                'is_valid_mcp': False,
                'registration_name': self._generate_registration_name(file_path.name),
                'category': self._categorize_mcp(file_path, content)
            }
            
            # 分析代碼結構
            self._analyze_code_structure(content, mcp_info)
            
            # 驗證是否為有效MCP
            mcp_info['is_valid_mcp'] = self._validate_mcp(mcp_info)
            
            return mcp_info
            
        except Exception as e:
            logger.error(f"分析MCP文件失敗 {file_path}: {e}")
            return None
    
    def _generate_registration_name(self, filename: str) -> str:
        """生成註冊名稱"""
        # 移除文件擴展名
        name = filename.replace('.py', '')
        
        # 移除常見後綴
        suffixes = ['_mcp', '_adapter', '_engine', 'mcp_']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
            elif name.startswith(suffix):
                name = name[len(suffix):]
        
        # 轉換為小寫並替換下劃線
        name = name.lower().replace('_', '_')
        
        return name
    
    def _categorize_mcp(self, file_path: Path, content: str) -> str:
        """分類MCP"""
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        # 基於路徑分類
        if 'ai_model' in path_str or 'gemini' in path_str or 'claude' in path_str or 'qwen' in path_str:
            return 'ai_model'
        elif 'tool' in path_str or 'engine' in path_str:
            return 'tool_engine'
        elif 'memory' in path_str or 'rag' in path_str:
            return 'memory_system'
        elif 'web' in path_str or 'search' in path_str:
            return 'web_agent'
        elif 'workflow' in path_str or 'automation' in path_str:
            return 'workflow'
        elif 'data' in path_str or 'processing' in path_str:
            return 'data_processing'
        elif 'rl' in path_str or 'reinforcement' in path_str:
            return 'reinforcement_learning'
        elif 'cli' in path_str or 'interface' in path_str:
            return 'user_interface'
        elif 'core' in path_str or 'base' in path_str:
            return 'core_infrastructure'
        else:
            return 'general'
    
    def _analyze_code_structure(self, content: str, mcp_info: Dict[str, Any]):
        """分析代碼結構"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 分析導入
            if line.startswith('import ') or line.startswith('from '):
                mcp_info['imports'].append(line)
            
            # 分析類定義
            elif line.startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                mcp_info['classes'].append(class_name)
            
            # 分析函數定義
            elif line.startswith('def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                mcp_info['functions'].append(func_name)
            
            # 分析能力聲明
            elif 'capabilities' in line.lower() or 'get_capabilities' in line:
                # 嘗試提取能力信息
                if '[' in line and ']' in line:
                    try:
                        capabilities_str = line[line.find('['):line.find(']')+1]
                        capabilities = eval(capabilities_str)
                        if isinstance(capabilities, list):
                            mcp_info['capabilities'].extend(capabilities)
                    except:
                        pass
    
    def _validate_mcp(self, mcp_info: Dict[str, Any]) -> bool:
        """驗證是否為有效MCP"""
        # 檢查是否有MCP相關的類
        mcp_classes = [cls for cls in mcp_info['classes'] 
                      if 'mcp' in cls.lower() or 'adapter' in cls.lower() or 'engine' in cls.lower()]
        
        if not mcp_classes:
            return False
        
        # 檢查是否有process方法
        has_process = 'process' in mcp_info['functions']
        
        # 檢查是否有必要的導入
        has_base_import = any('base' in imp.lower() or 'mcp' in imp.lower() 
                             for imp in mcp_info['imports'])
        
        return len(mcp_classes) > 0 and (has_process or has_base_import)
    
    def validate_mcp_deployment(self, mcp_info: Dict[str, Any]) -> Dict[str, Any]:
        """驗證MCP部署狀態"""
        validation_result = {
            'mcp_name': mcp_info['registration_name'],
            'file_path': mcp_info['file_path'],
            'validation_time': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'unknown',
            'errors': [],
            'warnings': []
        }
        
        try:
            # 檢查1: 文件存在性
            file_exists = Path(mcp_info['file_path']).exists()
            validation_result['checks']['file_exists'] = file_exists
            if not file_exists:
                validation_result['errors'].append("MCP文件不存在")
            
            # 檢查2: 語法正確性
            try:
                with open(mcp_info['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, mcp_info['file_path'], 'exec')
                validation_result['checks']['syntax_valid'] = True
            except SyntaxError as e:
                validation_result['checks']['syntax_valid'] = False
                validation_result['errors'].append(f"語法錯誤: {e}")
            
            # 檢查3: 導入測試
            try:
                spec = importlib.util.spec_from_file_location(
                    mcp_info['registration_name'], 
                    mcp_info['file_path']
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                validation_result['checks']['import_successful'] = True
                
                # 檢查4: MCP類存在性
                mcp_classes = [getattr(module, cls) for cls in mcp_info['classes'] 
                              if hasattr(module, cls)]
                validation_result['checks']['mcp_class_found'] = len(mcp_classes) > 0
                
                if mcp_classes:
                    # 檢查5: 實例化測試
                    try:
                        mcp_instance = mcp_classes[0]()
                        validation_result['checks']['instantiation_successful'] = True
                        
                        # 檢查6: 基本方法存在性
                        has_process = hasattr(mcp_instance, 'process')
                        has_capabilities = hasattr(mcp_instance, 'get_capabilities')
                        validation_result['checks']['required_methods'] = {
                            'process': has_process,
                            'get_capabilities': has_capabilities
                        }
                        
                        if not has_process:
                            validation_result['warnings'].append("缺少process方法")
                        
                    except Exception as e:
                        validation_result['checks']['instantiation_successful'] = False
                        validation_result['errors'].append(f"實例化失敗: {e}")
                else:
                    validation_result['checks']['mcp_class_found'] = False
                    validation_result['errors'].append("未找到MCP類")
                    
            except Exception as e:
                validation_result['checks']['import_successful'] = False
                validation_result['errors'].append(f"導入失敗: {e}")
            
            # 確定整體狀態
            if validation_result['errors']:
                validation_result['overall_status'] = 'failed'
            elif validation_result['warnings']:
                validation_result['overall_status'] = 'warning'
            else:
                validation_result['overall_status'] = 'passed'
                
        except Exception as e:
            validation_result['overall_status'] = 'error'
            validation_result['errors'].append(f"驗證過程出錯: {e}")
        
        return validation_result
    
    def register_mcp(self, mcp_info: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """註冊單個MCP"""
        registration_result = {
            'mcp_name': mcp_info['registration_name'],
            'registration_time': datetime.now().isoformat(),
            'status': 'unknown',
            'steps': [],
            'errors': []
        }
        
        try:
            # 步驟1: 驗證部署
            if not force:
                validation = self.validate_mcp_deployment(mcp_info)
                registration_result['steps'].append({
                    'step': 'validation',
                    'status': validation['overall_status'],
                    'details': validation
                })
                
                if validation['overall_status'] == 'failed':
                    registration_result['status'] = 'failed'
                    registration_result['errors'].extend(validation['errors'])
                    return registration_result
            
            # 步驟2: 讀取當前註冊表
            registry_content = self._read_registry_file()
            registration_result['steps'].append({
                'step': 'read_registry',
                'status': 'success'
            })
            
            # 步驟3: 生成註冊代碼
            registration_code = self._generate_registration_code(mcp_info)
            registration_result['steps'].append({
                'step': 'generate_code',
                'status': 'success',
                'code': registration_code
            })
            
            # 步驟4: 更新註冊表
            updated_content = self._update_registry_content(registry_content, registration_code)
            registration_result['steps'].append({
                'step': 'update_registry',
                'status': 'success'
            })
            
            # 步驟5: 寫入註冊表
            self._write_registry_file(updated_content)
            registration_result['steps'].append({
                'step': 'write_registry',
                'status': 'success'
            })
            
            # 步驟6: 驗證註冊
            if self._verify_registration(mcp_info['registration_name']):
                registration_result['status'] = 'success'
                self.registered_mcps.append(mcp_info)
                registration_result['steps'].append({
                    'step': 'verify_registration',
                    'status': 'success'
                })
            else:
                registration_result['status'] = 'failed'
                registration_result['errors'].append("註冊驗證失敗")
                registration_result['steps'].append({
                    'step': 'verify_registration',
                    'status': 'failed'
                })
            
        except Exception as e:
            registration_result['status'] = 'error'
            registration_result['errors'].append(f"註冊過程出錯: {e}")
            self.failed_registrations.append({
                'mcp_info': mcp_info,
                'error': str(e),
                'time': datetime.now().isoformat()
            })
        
        # 記錄註冊日誌
        self.registration_log.append(registration_result)
        
        return registration_result
    
    def _read_registry_file(self) -> str:
        """讀取註冊表文件"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"註冊表文件不存在: {self.registry_file}")
            return self._create_default_registry_content()
    
    def _create_default_registry_content(self) -> str:
        """創建默認註冊表內容"""
        return '''#!/usr/bin/env python3
"""
安全的MCP註冊表
自動生成，請勿手動編輯
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 核心適配器註冊表
core_adapters = {
    # 自動註冊的MCP適配器將在此處添加
}

def get_core_adapters() -> Dict[str, Any]:
    """獲取核心適配器"""
    return core_adapters.copy()

def register_adapter(name: str, adapter_class: Any) -> bool:
    """註冊適配器"""
    try:
        core_adapters[name] = adapter_class
        logger.info(f"適配器註冊成功: {name}")
        return True
    except Exception as e:
        logger.error(f"適配器註冊失敗 {name}: {e}")
        return False
'''
    
    def _generate_registration_code(self, mcp_info: Dict[str, Any]) -> Dict[str, str]:
        """生成註冊代碼"""
        # 生成導入語句
        import_statement = f"from {mcp_info['module_path']} import {mcp_info['classes'][0]}"
        
        # 生成註冊條目
        registration_entry = f'    "{mcp_info["registration_name"]}": {mcp_info["classes"][0]},'
        
        return {
            'import': import_statement,
            'registration': registration_entry,
            'class_name': mcp_info['classes'][0],
            'registration_name': mcp_info['registration_name']
        }
    
    def _update_registry_content(self, content: str, registration_code: Dict[str, str]) -> str:
        """更新註冊表內容"""
        lines = content.split('\n')
        updated_lines = []
        
        import_added = False
        registration_added = False
        
        for line in lines:
            # 添加導入語句
            if not import_added and line.strip().startswith('logger = '):
                updated_lines.append(line)
                updated_lines.append('')
                updated_lines.append(f'# 自動添加的導入')
                updated_lines.append(registration_code['import'])
                import_added = True
            # 添加註冊條目
            elif not registration_added and 'core_adapters = {' in line:
                updated_lines.append(line)
                updated_lines.append(f'    # 自動註冊: {registration_code["registration_name"]}')
                updated_lines.append(registration_code['registration'])
                registration_added = True
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def _write_registry_file(self, content: str):
        """寫入註冊表文件"""
        # 備份原文件
        if self.registry_file.exists():
            backup_file = self.registry_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(self._read_registry_file())
        
        # 寫入新內容
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _verify_registration(self, registration_name: str) -> bool:
        """驗證註冊是否成功"""
        try:
            # 重新讀取註冊表並檢查
            content = self._read_registry_file()
            return f'"{registration_name}"' in content
        except Exception as e:
            logger.error(f"驗證註冊失敗: {e}")
            return False
    
    def batch_register_mcps(self, mcp_list: List[Dict[str, Any]] = None, 
                           force: bool = False) -> Dict[str, Any]:
        """批量註冊MCP"""
        if mcp_list is None:
            mcp_list = self.discovered_mcps
        
        batch_result = {
            'total_mcps': len(mcp_list),
            'successful_registrations': 0,
            'failed_registrations': 0,
            'skipped_registrations': 0,
            'registration_details': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None
        }
        
        start_time = datetime.now()
        
        for mcp_info in mcp_list:
            if not mcp_info['is_valid_mcp'] and not force:
                batch_result['skipped_registrations'] += 1
                batch_result['registration_details'].append({
                    'mcp_name': mcp_info['registration_name'],
                    'status': 'skipped',
                    'reason': 'Invalid MCP'
                })
                continue
            
            registration_result = self.register_mcp(mcp_info, force)
            batch_result['registration_details'].append(registration_result)
            
            if registration_result['status'] == 'success':
                batch_result['successful_registrations'] += 1
            else:
                batch_result['failed_registrations'] += 1
        
        end_time = datetime.now()
        batch_result['end_time'] = end_time.isoformat()
        batch_result['duration'] = str(end_time - start_time)
        
        logger.info(f"批量註冊完成: {batch_result['successful_registrations']}/{batch_result['total_mcps']} 成功")
        
        return batch_result
    
    def get_registration_summary(self) -> Dict[str, Any]:
        """獲取註冊摘要"""
        return {
            'discovered_mcps': len(self.discovered_mcps),
            'registered_mcps': len(self.registered_mcps),
            'failed_registrations': len(self.failed_registrations),
            'registration_rate': len(self.registered_mcps) / max(len(self.discovered_mcps), 1) * 100,
            'categories': self._get_category_summary(),
            'last_registration': self.registration_log[-1] if self.registration_log else None
        }
    
    def _get_category_summary(self) -> Dict[str, int]:
        """獲取分類摘要"""
        categories = {}
        for mcp in self.discovered_mcps:
            category = mcp['category']
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def integrate_with_release_manager(self, release_manager) -> Dict[str, Any]:
        """與Release Manager集成"""
        integration_result = {
            'integration_time': datetime.now().isoformat(),
            'status': 'success',
            'hooks_registered': [],
            'errors': []
        }
        
        try:
            # 註冊部署後鉤子
            def post_deployment_hook(release_info):
                """部署後自動註冊MCP"""
                logger.info(f"觸發MCP自動註冊，發布版本: {release_info.get('version', 'unknown')}")
                
                # 重新發現MCP
                self.discover_mcps()
                
                # 批量註冊新發現的MCP
                new_mcps = [mcp for mcp in self.discovered_mcps 
                           if mcp['registration_name'] not in [r['mcp_name'] for r in self.registered_mcps]]
                
                if new_mcps:
                    batch_result = self.batch_register_mcps(new_mcps)
                    logger.info(f"自動註冊完成: {batch_result['successful_registrations']} 個MCP")
                    return batch_result
                else:
                    logger.info("沒有發現新的MCP需要註冊")
                    return {'message': 'No new MCPs to register'}
            
            # 將鉤子添加到Release Manager
            if hasattr(release_manager, 'add_post_deployment_hook'):
                release_manager.add_post_deployment_hook(post_deployment_hook)
                integration_result['hooks_registered'].append('post_deployment_hook')
            
            logger.info("與Release Manager集成成功")
            
        except Exception as e:
            integration_result['status'] = 'failed'
            integration_result['errors'].append(str(e))
            logger.error(f"與Release Manager集成失敗: {e}")
        
        return integration_result

# 測試代碼
if __name__ == "__main__":
    # 創建自動化註冊器
    registrar = AutomatedMCPRegistrar("/home/ubuntu/Powerauto.ai")
    
    # 發現MCP
    print("=== 發現MCP ===")
    discovered = registrar.discover_mcps()
    print(f"發現 {len(discovered)} 個MCP文件")
    
    # 顯示發現的MCP
    for mcp in discovered[:5]:  # 只顯示前5個
        print(f"- {mcp['registration_name']} ({mcp['category']}) - 有效: {mcp['is_valid_mcp']}")
    
    # 獲取註冊摘要
    print(f"\n=== 註冊摘要 ===")
    summary = registrar.get_registration_summary()
    print(f"發現的MCP: {summary['discovered_mcps']}")
    print(f"已註冊MCP: {summary['registered_mcps']}")
    print(f"註冊率: {summary['registration_rate']:.1f}%")
    print(f"分類分佈: {summary['categories']}")

