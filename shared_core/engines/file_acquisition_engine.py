"""
PowerAutomation v0.57 - 文件獲取引擎
解決兜底自動化流程中的文件獲取技術挑戰

Author: PowerAutomation Team
Version: 0.57
Date: 2025-06-11
"""

import asyncio
import json
import time
import logging
import threading
import platform
import subprocess
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import uuid

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileEvent:
    """文件事件數據結構"""
    event_id: str
    timestamp: float
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    file_path: str
    wsl_path: Optional[str] = None
    file_size: int = 0
    file_content: Optional[str] = None
    source_plugin: Optional[str] = None

@dataclass
class WSLBridgeConfig:
    """WSL橋接配置"""
    windows_path: str
    wsl_path: str
    auto_sync: bool = True
    sync_interval: float = 1.0
    file_patterns: List[str] = None

class FileSystemEventHandler(FileSystemEventHandler):
    """文件系統事件處理器"""
    
    def __init__(self, callback: Callable[[FileEvent], None]):
        super().__init__()
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory:
            file_event = FileEvent(
                event_id=str(uuid.uuid4()),
                timestamp=time.time(),
                event_type='created',
                file_path=event.src_path,
                file_size=os.path.getsize(event.src_path) if os.path.exists(event.src_path) else 0
            )
            self.callback(file_event)
    
    def on_modified(self, event):
        if not event.is_directory:
            file_event = FileEvent(
                event_id=str(uuid.uuid4()),
                timestamp=time.time(),
                event_type='modified',
                file_path=event.src_path,
                file_size=os.path.getsize(event.src_path) if os.path.exists(event.src_path) else 0
            )
            self.callback(file_event)

class FileAcquisitionEngine:
    """文件獲取引擎 - 解決兜底自動化流程的文件獲取挑戰"""
    
    def __init__(self):
        self.observers = {}
        self.wsl_bridges = {}
        self.file_cache = {}
        self.event_callbacks = []
        self.is_running = False
        self.platform_info = self._detect_platform()
        
        # 初始化文件監聽目錄
        self.watch_directories = {
            'manus_uploads': '/tmp/manus_uploads',
            'trae_uploads': '/tmp/trae_uploads',
            'general_uploads': '/tmp/powerauto_uploads'
        }
        
        logger.info(f"文件獲取引擎初始化完成 - 平台: {self.platform_info}")
    
    def _detect_platform(self) -> Dict[str, Any]:
        """檢測運行平台"""
        system = platform.system().lower()
        
        platform_info = {
            'system': system,
            'is_windows': system == 'windows',
            'is_linux': system == 'linux',
            'is_macos': system == 'darwin',
            'has_wsl': False,
            'wsl_version': None
        }
        
        # 檢測WSL環境
        if platform_info['is_windows']:
            try:
                result = subprocess.run(['wsl', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    platform_info['has_wsl'] = True
                    platform_info['wsl_version'] = 'WSL2' if 'WSL 2' in result.stdout else 'WSL1'
            except Exception as e:
                logger.warning(f"WSL檢測失敗: {e}")
        
        return platform_info
    
    async def start_monitoring(self) -> bool:
        """啟動文件監聽"""
        try:
            self.is_running = True
            
            # 創建監聽目錄
            for name, path in self.watch_directories.items():
                os.makedirs(path, exist_ok=True)
                
                # 設置文件監聽
                observer = Observer()
                event_handler = FileSystemEventHandler(self._handle_file_event)
                observer.schedule(event_handler, path, recursive=True)
                observer.start()
                
                self.observers[name] = observer
                logger.info(f"開始監聽目錄: {name} -> {path}")
            
            # 如果是Windows環境且有WSL，設置WSL橋接
            if self.platform_info['is_windows'] and self.platform_info['has_wsl']:
                await self._setup_wsl_bridges()
            
            logger.info("文件監聽服務啟動成功")
            return True
            
        except Exception as e:
            logger.error(f"文件監聽啟動失敗: {e}")
            return False
    
    async def stop_monitoring(self):
        """停止文件監聽"""
        self.is_running = False
        
        for name, observer in self.observers.items():
            observer.stop()
            observer.join()
            logger.info(f"停止監聽: {name}")
        
        self.observers.clear()
        logger.info("文件監聽服務已停止")
    
    def _handle_file_event(self, file_event: FileEvent):
        """處理文件事件"""
        try:
            # 讀取文件內容
            if os.path.exists(file_event.file_path):
                try:
                    with open(file_event.file_path, 'r', encoding='utf-8') as f:
                        file_event.file_content = f.read()
                except UnicodeDecodeError:
                    # 如果是二進制文件，記錄文件類型
                    file_event.file_content = f"[Binary file: {os.path.splitext(file_event.file_path)[1]}]"
            
            # 如果有WSL橋接，轉換路徑
            if self.platform_info['has_wsl']:
                file_event.wsl_path = self._convert_to_wsl_path(file_event.file_path)
            
            # 檢測來源插件
            file_event.source_plugin = self._detect_source_plugin(file_event.file_path)
            
            # 緩存文件事件
            self.file_cache[file_event.event_id] = file_event
            
            # 觸發回調
            for callback in self.event_callbacks:
                try:
                    callback(file_event)
                except Exception as e:
                    logger.error(f"文件事件回調失敗: {e}")
            
            logger.info(f"文件事件處理完成: {file_event.event_type} - {file_event.file_path}")
            
        except Exception as e:
            logger.error(f"文件事件處理失敗: {e}")
    
    def _convert_to_wsl_path(self, windows_path: str) -> str:
        """將Windows路徑轉換為WSL路徑"""
        try:
            # 標準化路徑
            windows_path = os.path.normpath(windows_path)
            
            # 轉換驅動器字母
            if len(windows_path) >= 2 and windows_path[1] == ':':
                drive = windows_path[0].lower()
                path_part = windows_path[2:].replace('\\', '/')
                wsl_path = f"/mnt/{drive}{path_part}"
                return wsl_path
            
            return windows_path
            
        except Exception as e:
            logger.error(f"WSL路徑轉換失敗: {e}")
            return windows_path
    
    def _detect_source_plugin(self, file_path: str) -> Optional[str]:
        """檢測文件來源插件"""
        path_lower = file_path.lower()
        
        if 'manus' in path_lower:
            return 'manus'
        elif 'trae' in path_lower:
            return 'trae'
        elif 'cursor' in path_lower:
            return 'cursor'
        elif 'windsurf' in path_lower:
            return 'windsurf'
        elif 'vscode' in path_lower:
            return 'vscode'
        
        return 'unknown'
    
    async def _setup_wsl_bridges(self):
        """設置WSL文件橋接"""
        try:
            for name, windows_path in self.watch_directories.items():
                wsl_path = self._convert_to_wsl_path(windows_path)
                
                bridge_config = WSLBridgeConfig(
                    windows_path=windows_path,
                    wsl_path=wsl_path,
                    auto_sync=True,
                    sync_interval=1.0,
                    file_patterns=['*.py', '*.js', '*.ts', '*.json', '*.md', '*.txt']
                )
                
                self.wsl_bridges[name] = bridge_config
                
                # 創建WSL目錄
                await self._create_wsl_directory(wsl_path)
                
                logger.info(f"WSL橋接設置完成: {name} -> {windows_path} <-> {wsl_path}")
        
        except Exception as e:
            logger.error(f"WSL橋接設置失敗: {e}")
    
    async def _create_wsl_directory(self, wsl_path: str):
        """在WSL中創建目錄"""
        try:
            cmd = ['wsl', 'mkdir', '-p', wsl_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"WSL目錄創建成功: {wsl_path}")
            else:
                logger.warning(f"WSL目錄創建失敗: {result.stderr}")
                
        except Exception as e:
            logger.error(f"WSL目錄創建異常: {e}")
    
    async def sync_file_to_wsl(self, windows_path: str, wsl_path: str) -> bool:
        """同步文件到WSL"""
        try:
            # 使用WSL命令複製文件
            cmd = ['wsl', 'cp', windows_path, wsl_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"文件同步成功: {windows_path} -> {wsl_path}")
                return True
            else:
                logger.error(f"文件同步失敗: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"文件同步異常: {e}")
            return False
    
    def add_event_callback(self, callback: Callable[[FileEvent], None]):
        """添加文件事件回調"""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[FileEvent], None]):
        """移除文件事件回調"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def get_file_events(self, limit: int = 100) -> List[FileEvent]:
        """獲取最近的文件事件"""
        events = list(self.file_cache.values())
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
    
    def get_platform_info(self) -> Dict[str, Any]:
        """獲取平台信息"""
        return self.platform_info.copy()
    
    async def test_wsl_connectivity(self) -> Dict[str, Any]:
        """測試WSL連接性"""
        test_result = {
            'wsl_available': False,
            'wsl_version': None,
            'test_command_success': False,
            'file_access_success': False,
            'error_message': None
        }
        
        try:
            if not self.platform_info['has_wsl']:
                test_result['error_message'] = 'WSL未安裝或不可用'
                return test_result
            
            # 測試基本命令
            result = subprocess.run(['wsl', 'echo', 'test'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                test_result['wsl_available'] = True
                test_result['wsl_version'] = self.platform_info['wsl_version']
                test_result['test_command_success'] = True
                
                # 測試文件訪問
                test_file = '/tmp/powerauto_wsl_test.txt'
                result = subprocess.run(['wsl', 'touch', test_file], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    test_result['file_access_success'] = True
                    # 清理測試文件
                    subprocess.run(['wsl', 'rm', test_file], 
                                 capture_output=True, text=True, timeout=5)
            
        except Exception as e:
            test_result['error_message'] = str(e)
        
        return test_result

# 全局文件獲取引擎實例
file_acquisition_engine = FileAcquisitionEngine()

async def main():
    """測試文件獲取引擎"""
    print("🚀 PowerAutomation 文件獲取引擎測試")
    
    # 測試平台檢測
    platform_info = file_acquisition_engine.get_platform_info()
    print(f"平台信息: {json.dumps(platform_info, indent=2, ensure_ascii=False)}")
    
    # 測試WSL連接性
    if platform_info['has_wsl']:
        wsl_test = await file_acquisition_engine.test_wsl_connectivity()
        print(f"WSL測試結果: {json.dumps(wsl_test, indent=2, ensure_ascii=False)}")
    
    # 啟動文件監聽
    success = await file_acquisition_engine.start_monitoring()
    print(f"文件監聽啟動: {'成功' if success else '失敗'}")
    
    if success:
        print("文件監聽服務運行中，按Ctrl+C停止...")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止文件監聽服務...")
            await file_acquisition_engine.stop_monitoring()
            print("文件獲取引擎測試完成")

if __name__ == "__main__":
    asyncio.run(main())

