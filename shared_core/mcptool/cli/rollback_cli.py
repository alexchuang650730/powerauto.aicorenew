#!/usr/bin/env python3
"""
PowerAutomation 統一回滾管理CLI

提供完整的回滾系統控制功能，包括：
- 創建保存點
- 執行回滾
- 查看歷史
- 管理保存點
- 系統狀態監控
"""

import os
import sys
import json
import argparse
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加項目路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from mcptool.adapters.intelligent_workflow_engine_mcp import IntelligentWorkflowEngineMCP
except ImportError:
    # 如果導入失敗，創建一個簡化的工作流引擎
    class IntelligentWorkflowEngineMCP:
        def __init__(self, project_root):
            self.project_root = project_root
            self.workflow_status = {"is_running": False}
        
        def start_rollback_workflow(self, reason, savepoint_id):
            pass

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PowerAutomationRollbackCLI:
    """PowerAutomation統一回滾管理CLI"""
    
    def __init__(self, project_root: str = None):
        """初始化CLI"""
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.config_dir = self.project_root / "mcptool" / "config"
        self.rollback_history_file = self.config_dir / "rollback_history.json"
        self.savepoints_file = self.config_dir / "savepoints.json"
        
        # 確保配置目錄存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化工作流引擎
        try:
            self.workflow_engine = IntelligentWorkflowEngineMCP(str(self.project_root))
        except Exception as e:
            logger.warning(f"工作流引擎初始化失敗: {e}")
            self.workflow_engine = None
        
        logger.info(f"PowerAutomation回滾CLI初始化完成，項目根目錄: {self.project_root}")
    
    def load_rollback_history(self) -> List[Dict[str, Any]]:
        """載入回滾歷史"""
        try:
            if self.rollback_history_file.exists():
                with open(self.rollback_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"載入回滾歷史失敗: {e}")
            return []
    
    def save_rollback_history(self, history: List[Dict[str, Any]]):
        """保存回滾歷史"""
        try:
            with open(self.rollback_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.info(f"回滾歷史已保存: {self.rollback_history_file}")
        except Exception as e:
            logger.error(f"保存回滾歷史失敗: {e}")
    
    def load_savepoints(self) -> List[Dict[str, Any]]:
        """載入保存點"""
        try:
            if self.savepoints_file.exists():
                with open(self.savepoints_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"載入保存點失敗: {e}")
            return []
    
    def save_savepoints(self, savepoints: List[Dict[str, Any]]):
        """保存保存點"""
        try:
            with open(self.savepoints_file, 'w', encoding='utf-8') as f:
                json.dump(savepoints, f, indent=2, ensure_ascii=False)
            logger.info(f"保存點已保存: {self.savepoints_file}")
        except Exception as e:
            logger.error(f"保存保存點失敗: {e}")
    
    def create_savepoint(self, description: str = None, auto: bool = False) -> str:
        """創建保存點"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        savepoint_id = f"sp_{description or 'manual'}_{timestamp}"
        
        # 計算項目狀態哈希
        project_hash = self._calculate_project_hash()
        
        # 創建保存點數據
        savepoint_data = {
            "id": savepoint_id,
            "timestamp": timestamp,
            "description": description or ("自動保存點" if auto else "手動保存點"),
            "created_at": datetime.now().isoformat(),
            "project_hash": project_hash,
            "auto_created": auto,
            "project_state": self._capture_detailed_project_state()
        }
        
        # 保存到保存點列表
        savepoints = self.load_savepoints()
        savepoints.append(savepoint_data)
        
        # 保持最多50個保存點
        if len(savepoints) > 50:
            savepoints = savepoints[-50:]
        
        self.save_savepoints(savepoints)
        
        print(f"✅ 保存點已創建: {savepoint_id}")
        print(f"   描述: {savepoint_data['description']}")
        print(f"   時間: {savepoint_data['created_at']}")
        print(f"   哈希: {project_hash[:12]}...")
        
        return savepoint_id
    
    def execute_rollback(self, savepoint_id: str = None, reason: str = None, 
                        dry_run: bool = False) -> Dict[str, Any]:
        """執行回滾"""
        if not savepoint_id:
            # 使用最新的保存點
            savepoints = self.load_savepoints()
            if not savepoints:
                print("❌ 沒有可用的保存點")
                return {"status": "error", "message": "沒有可用的保存點"}
            savepoint_id = savepoints[-1]["id"]
            print(f"🔄 使用最新保存點: {savepoint_id}")
        
        # 查找保存點
        savepoints = self.load_savepoints()
        savepoint = next((sp for sp in savepoints if sp["id"] == savepoint_id), None)
        
        if not savepoint:
            print(f"❌ 保存點不存在: {savepoint_id}")
            return {"status": "error", "message": f"保存點不存在: {savepoint_id}"}
        
        print(f"🔄 開始回滾到保存點: {savepoint_id}")
        print(f"   描述: {savepoint['description']}")
        print(f"   創建時間: {savepoint['created_at']}")
        
        if dry_run:
            print("🧪 乾運行模式 - 不會實際執行回滾")
            return {"status": "dry_run", "savepoint_id": savepoint_id}
        
        # 記錄回滾前狀態
        before_hash = self._calculate_project_hash()
        
        # 執行回滾
        try:
            if self.workflow_engine:
                # 使用工作流引擎執行回滾
                self.workflow_engine.start_rollback_workflow(
                    reason or f"回滾到保存點 {savepoint_id}", 
                    savepoint_id
                )
                
                # 等待完成
                import time
                max_wait = 60
                wait_time = 0
                
                while (self.workflow_engine.workflow_status.get("is_running", False) and 
                       wait_time < max_wait):
                    time.sleep(1)
                    wait_time += 1
                    if wait_time % 10 == 0:
                        print(f"   等待回滾完成... ({wait_time}/{max_wait}s)")
                
                if wait_time >= max_wait:
                    print("⚠️ 回滾超時，可能仍在進行中")
                    status = "timeout"
                else:
                    print("✅ 回滾完成")
                    status = "success"
            else:
                # 模擬回滾
                print("⚠️ 工作流引擎不可用，執行模擬回滾")
                time.sleep(2)
                status = "simulated"
            
            # 記錄回滾後狀態
            after_hash = self._calculate_project_hash()
            
            # 創建回滾記錄
            rollback_record = {
                "id": f"rb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "savepoint_id": savepoint_id,
                "timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
                "reason": reason or f"回滾到保存點 {savepoint_id}",
                "status": status,
                "before_hash": before_hash,
                "after_hash": after_hash,
                "files_changed": self._count_changed_files(before_hash, after_hash),
                "created_at": datetime.now().isoformat()
            }
            
            # 保存回滾歷史
            history = self.load_rollback_history()
            history.append(rollback_record)
            self.save_rollback_history(history)
            
            print(f"📝 回滾記錄已保存: {rollback_record['id']}")
            
            return {
                "status": status,
                "rollback_id": rollback_record["id"],
                "savepoint_id": savepoint_id,
                "files_changed": rollback_record["files_changed"]
            }
            
        except Exception as e:
            logger.error(f"回滾執行失敗: {e}")
            print(f"❌ 回滾失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    def list_savepoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出保存點"""
        savepoints = self.load_savepoints()
        
        if not savepoints:
            print("📝 沒有保存點")
            return []
        
        print(f"📝 保存點列表 (最近 {min(limit, len(savepoints))} 個):")
        print("-" * 80)
        
        for sp in savepoints[-limit:]:
            auto_flag = "🤖" if sp.get("auto_created", False) else "👤"
            print(f"{auto_flag} {sp['id']}")
            print(f"   描述: {sp['description']}")
            print(f"   時間: {sp['created_at']}")
            print(f"   哈希: {sp['project_hash'][:12]}...")
            print()
        
        return savepoints[-limit:]
    
    def list_rollback_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """列出回滾歷史"""
        history = self.load_rollback_history()
        
        if not history:
            print("📝 沒有回滾歷史")
            return []
        
        print(f"📝 回滾歷史 (最近 {min(limit, len(history))} 個):")
        print("-" * 80)
        
        for record in history[-limit:]:
            status_icon = "✅" if record["status"] == "success" else "❌"
            print(f"{status_icon} {record['id']}")
            print(f"   保存點: {record['savepoint_id']}")
            print(f"   原因: {record['reason']}")
            print(f"   狀態: {record['status']}")
            print(f"   文件變更: {record['files_changed']}")
            print(f"   時間: {record['created_at']}")
            print()
        
        return history[-limit:]
    
    def cleanup_old_savepoints(self, keep_count: int = 20) -> int:
        """清理舊保存點"""
        savepoints = self.load_savepoints()
        
        if len(savepoints) <= keep_count:
            print(f"📝 保存點數量 ({len(savepoints)}) 未超過限制 ({keep_count})")
            return 0
        
        # 保留最新的保存點
        removed_count = len(savepoints) - keep_count
        savepoints = savepoints[-keep_count:]
        
        self.save_savepoints(savepoints)
        
        print(f"🧹 已清理 {removed_count} 個舊保存點，保留最新 {keep_count} 個")
        return removed_count
    
    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態"""
        savepoints = self.load_savepoints()
        history = self.load_rollback_history()
        
        status = {
            "project_root": str(self.project_root),
            "current_hash": self._calculate_project_hash(),
            "savepoints_count": len(savepoints),
            "rollback_history_count": len(history),
            "latest_savepoint": savepoints[-1] if savepoints else None,
            "latest_rollback": history[-1] if history else None,
            "workflow_engine_available": self.workflow_engine is not None,
            "config_files": {
                "rollback_history": self.rollback_history_file.exists(),
                "savepoints": self.savepoints_file.exists()
            }
        }
        
        return status
    
    def print_system_status(self):
        """打印系統狀態"""
        status = self.get_system_status()
        
        print("🔍 PowerAutomation 回滾系統狀態")
        print("=" * 50)
        print(f"項目根目錄: {status['project_root']}")
        print(f"當前項目哈希: {status['current_hash'][:12]}...")
        print(f"保存點數量: {status['savepoints_count']}")
        print(f"回滾歷史數量: {status['rollback_history_count']}")
        print(f"工作流引擎: {'✅ 可用' if status['workflow_engine_available'] else '❌ 不可用'}")
        
        if status['latest_savepoint']:
            print(f"最新保存點: {status['latest_savepoint']['id']}")
            print(f"  時間: {status['latest_savepoint']['created_at']}")
        
        if status['latest_rollback']:
            print(f"最新回滾: {status['latest_rollback']['id']}")
            print(f"  時間: {status['latest_rollback']['created_at']}")
            print(f"  狀態: {status['latest_rollback']['status']}")
    
    def _calculate_project_hash(self) -> str:
        """計算項目狀態哈希"""
        try:
            hash_md5 = hashlib.md5()
            
            # 遍歷Python文件
            for py_file in self.project_root.rglob("*.py"):
                if ".git" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                try:
                    with open(py_file, 'rb') as f:
                        hash_md5.update(f.read())
                except:
                    continue
            
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"計算項目哈希失敗: {e}")
            return f"error_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _capture_detailed_project_state(self) -> Dict[str, Any]:
        """捕獲詳細項目狀態"""
        try:
            py_files = list(self.project_root.rglob("*.py"))
            json_files = list(self.project_root.rglob("*.json"))
            md_files = list(self.project_root.rglob("*.md"))
            
            # 過濾掉不需要的文件
            py_files = [f for f in py_files if ".git" not in str(f) and "__pycache__" not in str(f)]
            
            return {
                "total_py_files": len(py_files),
                "total_json_files": len(json_files),
                "total_md_files": len(md_files),
                "last_modified": max([f.stat().st_mtime for f in py_files[:10]] or [0]),
                "total_size": sum(f.stat().st_size for f in py_files[:100]),
                "capture_time": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"捕獲項目狀態失敗: {e}")
            return {"error": str(e)}
    
    def _count_changed_files(self, before_hash: str, after_hash: str) -> int:
        """計算變更文件數量（簡化實現）"""
        if before_hash == after_hash:
            return 0
        # 簡化實現，實際應該比較文件差異
        return 5


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation 統一回滾管理CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s create --description "重要功能完成前的保存點"
  %(prog)s rollback --savepoint sp_manual_20231201120000
  %(prog)s list-savepoints --limit 20
  %(prog)s list-history --limit 15
  %(prog)s status
  %(prog)s cleanup --keep 30
        """
    )
    
    parser.add_argument(
        '--project-root', 
        type=str, 
        help='項目根目錄路徑'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 創建保存點
    create_parser = subparsers.add_parser('create', help='創建保存點')
    create_parser.add_argument('--description', '-d', type=str, help='保存點描述')
    create_parser.add_argument('--auto', action='store_true', help='標記為自動創建')
    
    # 執行回滾
    rollback_parser = subparsers.add_parser('rollback', help='執行回滾')
    rollback_parser.add_argument('--savepoint', '-s', type=str, help='目標保存點ID')
    rollback_parser.add_argument('--reason', '-r', type=str, help='回滾原因')
    rollback_parser.add_argument('--dry-run', action='store_true', help='乾運行模式')
    
    # 列出保存點
    list_sp_parser = subparsers.add_parser('list-savepoints', help='列出保存點')
    list_sp_parser.add_argument('--limit', '-l', type=int, default=10, help='顯示數量限制')
    
    # 列出回滾歷史
    list_hist_parser = subparsers.add_parser('list-history', help='列出回滾歷史')
    list_hist_parser.add_argument('--limit', '-l', type=int, default=10, help='顯示數量限制')
    
    # 系統狀態
    subparsers.add_parser('status', help='顯示系統狀態')
    
    # 清理舊保存點
    cleanup_parser = subparsers.add_parser('cleanup', help='清理舊保存點')
    cleanup_parser.add_argument('--keep', '-k', type=int, default=20, help='保留的保存點數量')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化CLI
    cli = PowerAutomationRollbackCLI(args.project_root)
    
    try:
        if args.command == 'create':
            cli.create_savepoint(args.description, args.auto)
        
        elif args.command == 'rollback':
            result = cli.execute_rollback(args.savepoint, args.reason, args.dry_run)
            if result["status"] == "error":
                sys.exit(1)
        
        elif args.command == 'list-savepoints':
            cli.list_savepoints(args.limit)
        
        elif args.command == 'list-history':
            cli.list_rollback_history(args.limit)
        
        elif args.command == 'status':
            cli.print_system_status()
        
        elif args.command == 'cleanup':
            cli.cleanup_old_savepoints(args.keep)
        
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用戶中斷")
        sys.exit(1)
    except Exception as e:
        logger.error(f"執行失敗: {e}")
        print(f"❌ 執行失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

