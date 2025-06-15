#!/usr/bin/env python3
"""
PowerAutomation API配置修復器

確保所有API密鑰正確載入和配置
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIConfigurationManager:
    """API配置管理器"""
    
    def __init__(self, project_dir: str = "/home/ubuntu/Powerauto.ai"):
        self.project_dir = Path(project_dir)
        self.env_file = self.project_dir / '.env'
        self.api_configs = {}
        
        # 載入配置
        self._load_environment_variables()
        self._validate_api_keys()
    
    def _load_environment_variables(self):
        """載入環境變數"""
        try:
            # 方法1: 使用python-dotenv
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_file)
                logger.info("✅ 使用python-dotenv載入環境變數")
            except ImportError:
                logger.warning("python-dotenv未安裝，使用手動解析")
                self._manual_load_env()
            
            # 方法2: 直接讀取.env文件並設置環境變數
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                            logger.debug(f"設置環境變數: {key}")
            
            logger.info("環境變數載入完成")
            
        except Exception as e:
            logger.error(f"載入環境變數失敗: {e}")
    
    def _manual_load_env(self):
        """手動載入.env文件"""
        if not self.env_file.exists():
            logger.warning(f".env文件不存在: {self.env_file}")
            return
        
        try:
            with open(self.env_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' not in line:
                        logger.warning(f".env文件第{line_num}行格式錯誤: {line}")
                        continue
                    
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引號
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    os.environ[key] = value
                    logger.debug(f"手動設置環境變數: {key}")
            
            logger.info("手動載入.env文件完成")
            
        except Exception as e:
            logger.error(f"手動載入.env文件失敗: {e}")
    
    def _validate_api_keys(self):
        """驗證API密鑰"""
        # 定義需要的API密鑰
        required_apis = {
            'CLAUDE_API_KEY': {
                'name': 'Claude',
                'prefix': 'sk-ant-',
                'min_length': 50
            },
            'GEMINI_API_KEY': {
                'name': 'Gemini',
                'prefix': 'AIzaSy',
                'min_length': 30
            },
            'OPENAI_API_KEY': {
                'name': 'OpenAI',
                'prefix': 'sk-',
                'min_length': 40
            }
        }
        
        for key, config in required_apis.items():
            value = os.getenv(key)
            
            if not value:
                logger.warning(f"❌ {config['name']} API密鑰未配置: {key}")
                self.api_configs[key] = {
                    'configured': False,
                    'valid': False,
                    'error': 'API密鑰未配置'
                }
                continue
            
            # 驗證格式
            is_valid = True
            error_msg = None
            
            if not value.startswith(config['prefix']):
                is_valid = False
                error_msg = f"API密鑰格式錯誤，應以 {config['prefix']} 開頭"
            elif len(value) < config['min_length']:
                is_valid = False
                error_msg = f"API密鑰長度不足，應至少 {config['min_length']} 字符"
            
            if is_valid:
                logger.info(f"✅ {config['name']} API密鑰配置正確")
                self.api_configs[key] = {
                    'configured': True,
                    'valid': True,
                    'masked_key': value[:10] + '...' + value[-4:] if len(value) > 14 else value[:6] + '...'
                }
            else:
                logger.error(f"❌ {config['name']} API密鑰無效: {error_msg}")
                self.api_configs[key] = {
                    'configured': True,
                    'valid': False,
                    'error': error_msg
                }
    
    def get_api_status(self) -> Dict[str, Any]:
        """獲取API配置狀態"""
        return {
            'total_apis': len(self.api_configs),
            'configured_apis': sum(1 for config in self.api_configs.values() if config['configured']),
            'valid_apis': sum(1 for config in self.api_configs.values() if config.get('valid', False)),
            'details': self.api_configs
        }
    
    def fix_api_configuration(self) -> Dict[str, Any]:
        """修復API配置"""
        fixes_applied = []
        
        try:
            # 1. 確保環境變數正確設置
            self._ensure_environment_variables()
            fixes_applied.append("重新載入環境變數")
            
            # 2. 修復適配器中的API密鑰載入
            self._fix_adapter_api_loading()
            fixes_applied.append("修復適配器API載入")
            
            # 3. 重新驗證
            self._validate_api_keys()
            fixes_applied.append("重新驗證API密鑰")
            
            return {
                "success": True,
                "fixes_applied": fixes_applied,
                "api_status": self.get_api_status()
            }
            
        except Exception as e:
            logger.error(f"修復API配置失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "fixes_applied": fixes_applied
            }
    
    def _ensure_environment_variables(self):
        """確保環境變數正確設置"""
        # 重新載入.env文件
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                content = f.read()
                logger.info(f".env文件內容長度: {len(content)} 字符")
                
                # 解析並設置每個變數
                for line in content.split('\\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        # 強制設置環境變數
                        os.environ[key] = value
                        logger.debug(f"強制設置: {key}")
        
        # 驗證關鍵API密鑰是否已設置
        claude_key = os.getenv('CLAUDE_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        logger.info(f"Claude API密鑰: {'已設置' if claude_key else '未設置'}")
        logger.info(f"Gemini API密鑰: {'已設置' if gemini_key else '未設置'}")
    
    def _fix_adapter_api_loading(self):
        """修復適配器中的API密鑰載入"""
        try:
            # 修復Gemini適配器
            self._fix_gemini_adapter()
            
            # 修復Claude適配器
            self._fix_claude_adapter()
            
        except Exception as e:
            logger.error(f"修復適配器API載入失敗: {e}")
    
    def _fix_gemini_adapter(self):
        """修復Gemini適配器"""
        try:
            gemini_adapter_path = self.project_dir / 'mcptool/adapters/simple_gemini_adapter.py'
            if gemini_adapter_path.exists():
                # 讀取文件內容
                with open(gemini_adapter_path, 'r') as f:
                    content = f.read()
                
                # 檢查是否需要修復
                if 'os.getenv' not in content or 'GEMINI_API_KEY' not in content:
                    logger.info("修復Gemini適配器API密鑰載入")
                    
                    # 在適當位置添加API密鑰載入代碼
                    fixed_content = self._add_api_loading_to_adapter(content, 'GEMINI_API_KEY')
                    
                    # 寫回文件
                    with open(gemini_adapter_path, 'w') as f:
                        f.write(fixed_content)
                    
                    logger.info("✅ Gemini適配器API載入已修復")
                
        except Exception as e:
            logger.error(f"修復Gemini適配器失敗: {e}")
    
    def _fix_claude_adapter(self):
        """修復Claude適配器"""
        try:
            claude_adapter_path = self.project_dir / 'mcptool/adapters/simple_claude_adapter.py'
            if claude_adapter_path.exists():
                # 讀取文件內容
                with open(claude_adapter_path, 'r') as f:
                    content = f.read()
                
                # 檢查是否需要修復
                if 'os.getenv' not in content or 'CLAUDE_API_KEY' not in content:
                    logger.info("修復Claude適配器API密鑰載入")
                    
                    # 在適當位置添加API密鑰載入代碼
                    fixed_content = self._add_api_loading_to_adapter(content, 'CLAUDE_API_KEY')
                    
                    # 寫回文件
                    with open(claude_adapter_path, 'w') as f:
                        f.write(fixed_content)
                    
                    logger.info("✅ Claude適配器API載入已修復")
                
        except Exception as e:
            logger.error(f"修復Claude適配器失敗: {e}")
    
    def _add_api_loading_to_adapter(self, content: str, api_key_name: str) -> str:
        """在適配器中添加API密鑰載入代碼"""
        # 在import語句後添加API密鑰載入
        import_section = "import os\\n"
        if "import os" not in content:
            content = import_section + content
        
        # 在__init__方法中添加API密鑰載入
        api_loading_code = f"""
        # 載入API密鑰
        self.api_key = os.getenv('{api_key_name}')
        if not self.api_key:
            logger.warning(f"API密鑰未配置: {api_key_name}")
"""
        
        # 查找__init__方法並添加代碼
        if "def __init__" in content:
            lines = content.split('\\n')
            new_lines = []
            in_init = False
            
            for line in lines:
                new_lines.append(line)
                if "def __init__" in line:
                    in_init = True
                elif in_init and line.strip() and not line.startswith(' ') and not line.startswith('\\t'):
                    # __init__方法結束
                    in_init = False
                elif in_init and "self.api_key" not in line and line.strip().endswith(':'):
                    # 在__init__方法中添加API密鑰載入代碼
                    new_lines.extend(api_loading_code.strip().split('\\n'))
                    in_init = False
            
            content = '\\n'.join(new_lines)
        
        return content
    
    def test_api_connections(self) -> Dict[str, Any]:
        """測試API連接"""
        test_results = {}
        
        # 測試Claude API
        if self.api_configs.get('CLAUDE_API_KEY', {}).get('valid'):
            test_results['claude'] = self._test_claude_api()
        else:
            test_results['claude'] = {"success": False, "error": "API密鑰未配置或無效"}
        
        # 測試Gemini API
        if self.api_configs.get('GEMINI_API_KEY', {}).get('valid'):
            test_results['gemini'] = self._test_gemini_api()
        else:
            test_results['gemini'] = {"success": False, "error": "API密鑰未配置或無效"}
        
        return test_results
    
    def _test_claude_api(self) -> Dict[str, Any]:
        """測試Claude API"""
        try:
            import requests
            
            api_key = os.getenv('CLAUDE_API_KEY')
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 10,
                'messages': [{'role': 'user', 'content': 'Hello'}]
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Claude API連接成功"}
            else:
                return {"success": False, "error": f"API返回錯誤: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Claude API測試失敗: {e}"}
    
    def _test_gemini_api(self) -> Dict[str, Any]:
        """測試Gemini API"""
        try:
            import requests
            
            api_key = os.getenv('GEMINI_API_KEY')
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            data = {
                'contents': [{
                    'parts': [{'text': 'Hello'}]
                }]
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": "Gemini API連接成功"}
            else:
                return {"success": False, "error": f"API返回錯誤: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Gemini API測試失敗: {e}"}

# 測試和修復腳本
if __name__ == "__main__":
    print("🔧 PowerAutomation API配置修復器")
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 創建配置管理器
    config_manager = APIConfigurationManager()
    
    # 顯示當前狀態
    print("\\n📊 當前API配置狀態:")
    status = config_manager.get_api_status()
    print(f"總API數量: {status['total_apis']}")
    print(f"已配置: {status['configured_apis']}")
    print(f"有效: {status['valid_apis']}")
    
    for key, config in status['details'].items():
        if config['configured']:
            if config['valid']:
                print(f"  ✅ {key}: {config.get('masked_key', '已配置')}")
            else:
                print(f"  ❌ {key}: {config.get('error', '無效')}")
        else:
            print(f"  ⚠️  {key}: 未配置")
    
    # 執行修復
    print("\\n🔧 執行API配置修復...")
    fix_result = config_manager.fix_api_configuration()
    
    if fix_result['success']:
        print("✅ API配置修復成功")
        print(f"應用的修復: {', '.join(fix_result['fixes_applied'])}")
        
        # 顯示修復後狀態
        new_status = fix_result['api_status']
        print(f"\\n修復後狀態: {new_status['valid_apis']}/{new_status['total_apis']} API有效")
        
    else:
        print(f"❌ API配置修復失敗: {fix_result['error']}")
    
    # 測試API連接
    print("\\n🧪 測試API連接...")
    test_results = config_manager.test_api_connections()
    
    for api_name, result in test_results.items():
        if result['success']:
            print(f"  ✅ {api_name}: {result['message']}")
        else:
            print(f"  ❌ {api_name}: {result['error']}")
    
    print("\\n🎯 API配置修復完成")

