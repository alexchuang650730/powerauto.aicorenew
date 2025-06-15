"""
GitHub Webhook处理路由
基于用户的Amazon环境同步方案
"""
import os
import json
import hmac
import hashlib
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

github_bp = Blueprint('github', __name__)

class GitHubWebhookHandler:
    """GitHub Webhook处理器"""
    
    def __init__(self, webhook_secret):
        self.webhook_secret = webhook_secret
    
    def verify_signature(self, payload_body, signature_header):
        """验证GitHub webhook签名"""
        if not self.webhook_secret:
            return True  # 如果没有配置密钥，跳过验证
            
        try:
            signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload_body,
                hashlib.sha256
            ).hexdigest()
            
            expected_signature = f"sha256={signature}"
            return hmac.compare_digest(expected_signature, signature_header)
        except Exception as e:
            print(f"签名验证失败: {e}")
            return False
    
    def handle_push_event(self, payload):
        """处理推送事件"""
        try:
            ref = payload.get("ref", "")
            commits = payload.get("commits", [])
            repository = payload.get("repository", {})
            pusher = payload.get("pusher", {})
            
            # 只处理main和develop分支
            if ref not in ["refs/heads/main", "refs/heads/develop"]:
                return {"status": "ignored", "reason": "非主要分支"}
            
            branch = ref.split("/")[-1]
            repo_name = repository.get("full_name", "unknown")
            pusher_name = pusher.get("name", "unknown")
            
            event_data = {
                "event_type": "push",
                "repository": repo_name,
                "branch": branch,
                "pusher": pusher_name,
                "commit_count": len(commits),
                "commits": [
                    {
                        "id": commit.get("id", "")[:8],
                        "message": commit.get("message", "")[:100],
                        "author": commit.get("author", {}).get("name", ""),
                        "timestamp": commit.get("timestamp", "")
                    }
                    for commit in commits[:5]  # 只取前5个提交
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            return event_data
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def handle_pull_request_event(self, payload):
        """处理PR事件"""
        try:
            action = payload.get("action", "")
            pr = payload.get("pull_request", {})
            repository = payload.get("repository", {})
            
            if action not in ["opened", "synchronize", "closed"]:
                return {"status": "ignored", "reason": "非关注的PR动作"}
            
            event_data = {
                "event_type": f"pull_request_{action}",
                "repository": repository.get("full_name", "unknown"),
                "pr_number": pr.get("number", 0),
                "pr_title": pr.get("title", ""),
                "pr_author": pr.get("user", {}).get("login", ""),
                "source_branch": pr.get("head", {}).get("ref", ""),
                "target_branch": pr.get("base", {}).get("ref", ""),
                "pr_url": pr.get("html_url", ""),
                "merged": pr.get("merged", False),
                "timestamp": datetime.now().isoformat()
            }
            
            return event_data
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_feishu_notification(self, event_data):
        """创建飞书通知数据"""
        event_type = event_data.get("event_type", "")
        
        if event_type == "push":
            return {
                "event_type": "push",
                "repository": event_data.get("repository", ""),
                "branch": event_data.get("branch", ""),
                "commit_message": event_data.get("commits", [{}])[0].get("message", ""),
                "author": event_data.get("pusher", "")
            }
        elif "pull_request" in event_type:
            return {
                "event_type": event_type,
                "repository": event_data.get("repository", ""),
                "pr_title": event_data.get("pr_title", ""),
                "pr_author": event_data.get("pr_author", ""),
                "pr_url": event_data.get("pr_url", "")
            }
        
        return event_data

@github_bp.route('/webhook', methods=['POST'])
def github_webhook():
    """GitHub webhook端点"""
    try:
        # 获取请求数据
        signature = request.headers.get("X-Hub-Signature-256", "")
        payload_body = request.get_data()
        payload = request.get_json()
        event_type = request.headers.get("X-GitHub-Event", "")
        
        # 初始化处理器
        webhook_secret = current_app.config.get('GITHUB_WEBHOOK_SECRET', '')
        handler = GitHubWebhookHandler(webhook_secret)
        
        # 验证签名
        if not handler.verify_signature(payload_body, signature):
            return jsonify({"error": "Invalid signature"}), 401
        
        # 处理不同类型的事件
        event_data = None
        
        if event_type == "push":
            event_data = handler.handle_push_event(payload)
        elif event_type == "pull_request":
            event_data = handler.handle_pull_request_event(payload)
        else:
            return jsonify({
                "status": "ignored",
                "message": f"不支持的事件类型: {event_type}"
            })
        
        if event_data.get("status") == "error":
            return jsonify(event_data), 500
        
        if event_data.get("status") == "ignored":
            return jsonify(event_data)
        
        # 发送飞书通知
        feishu_data = handler.create_feishu_notification(event_data)
        try:
            # 调用飞书通知API
            feishu_response = requests.post(
                "http://localhost:5000/api/feishu/notify/github",
                json=feishu_data,
                timeout=10
            )
        except Exception as e:
            print(f"飞书通知发送失败: {e}")
        
        # 触发MCP协调器更新
        try:
            mcp_response = requests.post(
                "http://localhost:5000/api/mcp/intervention/trigger",
                json={
                    "type": "github_event",
                    "context": event_data
                },
                timeout=10
            )
        except Exception as e:
            print(f"MCP协调器通知失败: {e}")
        
        return jsonify({
            "status": "success",
            "message": "Webhook处理成功",
            "event_data": event_data
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Webhook处理失败: {str(e)}"
        }), 500

@github_bp.route('/sync/status')
def sync_status():
    """GitHub同步状态"""
    try:
        # 模拟GitHub同步状态
        sync_data = {
            "status": "syncing",
            "repository": "powerauto.ai_0.53",
            "branch": "v0.6",
            "last_sync": "2分钟前",
            "webhook_status": "listening",
            "auto_deploy": "enabled",
            "sync_frequency": "实时",
            "recent_events": [
                {
                    "type": "push",
                    "branch": "main",
                    "author": "developer",
                    "message": "feat: 添加智慧UI Dashboard",
                    "timestamp": "2分钟前"
                },
                {
                    "type": "pull_request_opened",
                    "pr_number": 42,
                    "title": "增强MCP协调器功能",
                    "author": "architect",
                    "timestamp": "15分钟前"
                },
                {
                    "type": "push",
                    "branch": "develop",
                    "author": "developer",
                    "message": "fix: 修复飞书集成问题",
                    "timestamp": "1小时前"
                }
            ],
            "statistics": {
                "total_webhooks_received": 156,
                "successful_syncs": 154,
                "failed_syncs": 2,
                "success_rate": 98.7,
                "average_sync_time": "3.2秒"
            }
        }
        
        return jsonify(sync_data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"同步状态获取失败: {str(e)}"
        }), 500

@github_bp.route('/sync/trigger', methods=['POST'])
def trigger_sync():
    """手动触发同步"""
    try:
        data = request.get_json()
        repository = data.get('repository', 'powerauto.ai_0.53')
        branch = data.get('branch', 'main')
        
        # 模拟同步过程
        sync_result = {
            "status": "success",
            "repository": repository,
            "branch": branch,
            "sync_id": f"SYNC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "steps": [
                "连接到GitHub仓库",
                "拉取最新代码",
                "检查代码质量",
                "触发自动化测试",
                "更新部署环境",
                "发送通知"
            ],
            "estimated_duration": "2-3分钟"
        }
        
        # 发送进度通知到飞书
        try:
            requests.post(
                "http://localhost:5000/api/feishu/notify/progress",
                json={
                    "task_name": f"GitHub同步 - {repository}",
                    "progress": 0,
                    "status": "开始同步"
                },
                timeout=10
            )
        except Exception as e:
            print(f"进度通知发送失败: {e}")
        
        return jsonify({
            "success": True,
            "message": "同步已触发",
            "result": sync_result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"同步触发失败: {str(e)}"
        }), 500

@github_bp.route('/repositories')
def list_repositories():
    """获取仓库列表"""
    try:
        # 模拟仓库列表
        repositories = [
            {
                "name": "powerauto.ai_0.53",
                "full_name": "alexchuang650730/powerauto.ai_0.53",
                "description": "PowerAutomation 核心系统",
                "private": True,
                "default_branch": "main",
                "last_push": "2分钟前",
                "webhook_configured": True,
                "auto_deploy": True
            },
            {
                "name": "powerauto.aicore",
                "full_name": "alexchuang650730/powerauto.aicore",
                "description": "PowerAutomation 智能核心",
                "private": True,
                "default_branch": "main",
                "last_push": "1小时前",
                "webhook_configured": True,
                "auto_deploy": False
            }
        ]
        
        return jsonify({
            "repositories": repositories,
            "total_count": len(repositories)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"仓库列表获取失败: {str(e)}"
        }), 500

@github_bp.route('/webhook/test', methods=['POST'])
def test_webhook():
    """测试Webhook功能"""
    try:
        # 模拟GitHub事件
        test_payload = {
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "alexchuang650730/powerauto.ai_0.53"
            },
            "pusher": {
                "name": "test_user"
            },
            "commits": [
                {
                    "id": "abc123def456",
                    "message": "test: 测试Webhook功能",
                    "author": {
                        "name": "test_user"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # 处理测试事件
        handler = GitHubWebhookHandler("")
        event_data = handler.handle_push_event(test_payload)
        
        return jsonify({
            "success": True,
            "message": "Webhook测试成功",
            "test_event": event_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Webhook测试失败: {str(e)}"
        }), 500

