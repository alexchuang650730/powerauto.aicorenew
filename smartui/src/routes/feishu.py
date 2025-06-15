"""
飞书SDK集成路由
基于用户提供的飞书SDK方案实现
"""
import os
import json
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

feishu_bp = Blueprint('feishu', __name__)

class FeishuService:
    """飞书服务类 - 基于用户的SDK方案"""
    
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        
        # 飞书群组ID配置
        self.chat_ids = {
            "dev": "oc_powerauto_dev",           # 开发讨论群
            "architecture": "oc_powerauto_arch", # 架构决策群  
            "pr_review": "oc_powerauto_pr",      # 代码审查群
            "deployment": "oc_powerauto_deploy", # 部署监控群
            "smart_ui": "oc_powerauto_ui"        # 智慧UI通知群
        }
    
    def get_access_token(self):
        """获取访问令牌"""
        try:
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                return self.access_token
            else:
                print(f"获取飞书访问令牌失败: {result}")
                return None
                
        except Exception as e:
            print(f"飞书API调用异常: {e}")
            return None
    
    def send_text_message(self, chat_id, text):
        """发送文本消息"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.base_url}/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "receive_id": chat_id,
                "receive_id_type": "chat_id",
                "msg_type": "text",
                "content": json.dumps({"text": text})
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.json()
            
        except Exception as e:
            print(f"发送飞书消息失败: {e}")
            return {"error": str(e)}
    
    def send_card_message(self, chat_id, card_content):
        """发送卡片消息"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.base_url}/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "receive_id": chat_id,
                "receive_id_type": "chat_id",
                "msg_type": "interactive",
                "content": json.dumps({"card": card_content})
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.json()
            
        except Exception as e:
            print(f"发送飞书卡片消息失败: {e}")
            return {"error": str(e)}
    
    def create_progress_card(self, task_name, progress, status):
        """创建进度通知卡片"""
        progress_color = "#10b981" if progress >= 80 else "#f59e0b" if progress >= 50 else "#ef4444"
        
        card = {
            "header": {
                "title": {
                    "content": f"🚀 PowerAutomation 任务进度",
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**任务**: {task_name}\n**进度**: {progress}%\n**状态**: {status}\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "progress",
                    "percentage": progress,
                    "color": progress_color
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "查看详情",
                                "tag": "plain_text"
                            },
                            "url": "http://localhost:5000",
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
        
        return card

@feishu_bp.route('/test', methods=['POST'])
def test_feishu_integration():
    """测试飞书集成"""
    try:
        app_id = current_app.config.get('FEISHU_APP_ID')
        app_secret = current_app.config.get('FEISHU_APP_SECRET')
        
        if not app_id or not app_secret:
            return jsonify({
                'success': False,
                'message': '飞书配置未完成，请设置环境变量'
            }), 400
        
        feishu_service = FeishuService(app_id, app_secret)
        
        # 发送测试消息
        test_message = f"🎯 PowerAutomation 智慧UI测试通知\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n状态: 系统运行正常"
        
        # 这里使用开发群组ID进行测试
        result = feishu_service.send_text_message(
            feishu_service.chat_ids["smart_ui"], 
            test_message
        )
        
        return jsonify({
            'success': True,
            'message': '飞书测试通知发送成功',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'飞书测试失败: {str(e)}'
        }), 500

@feishu_bp.route('/notify/progress', methods=['POST'])
def notify_progress():
    """发送进度通知"""
    try:
        data = request.get_json()
        task_name = data.get('task_name', '未知任务')
        progress = data.get('progress', 0)
        status = data.get('status', '进行中')
        
        app_id = current_app.config.get('FEISHU_APP_ID')
        app_secret = current_app.config.get('FEISHU_APP_SECRET')
        
        if not app_id or not app_secret:
            return jsonify({
                'success': False,
                'message': '飞书配置未完成'
            }), 400
        
        feishu_service = FeishuService(app_id, app_secret)
        
        # 创建进度卡片
        card_content = feishu_service.create_progress_card(task_name, progress, status)
        
        # 发送到智慧UI通知群
        result = feishu_service.send_card_message(
            feishu_service.chat_ids["smart_ui"],
            card_content
        )
        
        return jsonify({
            'success': True,
            'message': '进度通知发送成功',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'进度通知发送失败: {str(e)}'
        }), 500

@feishu_bp.route('/notify/github', methods=['POST'])
def notify_github_event():
    """GitHub事件通知"""
    try:
        data = request.get_json()
        event_type = data.get('event_type', '')
        repository = data.get('repository', '')
        branch = data.get('branch', '')
        commit_message = data.get('commit_message', '')
        author = data.get('author', '')
        
        app_id = current_app.config.get('FEISHU_APP_ID')
        app_secret = current_app.config.get('FEISHU_APP_SECRET')
        
        if not app_id or not app_secret:
            return jsonify({
                'success': False,
                'message': '飞书配置未完成'
            }), 400
        
        feishu_service = FeishuService(app_id, app_secret)
        
        # 创建GitHub事件卡片
        card = {
            "header": {
                "title": {
                    "content": f"🔄 GitHub {event_type}",
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**仓库**: {repository}\n**分支**: {branch}\n**作者**: {author}\n**提交信息**: {commit_message}\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "查看仓库",
                                "tag": "plain_text"
                            },
                            "url": f"https://github.com/{repository}",
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
        
        # 发送到部署监控群
        result = feishu_service.send_card_message(
            feishu_service.chat_ids["deployment"],
            card
        )
        
        return jsonify({
            'success': True,
            'message': 'GitHub事件通知发送成功',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'GitHub事件通知发送失败: {str(e)}'
        }), 500

@feishu_bp.route('/status')
def feishu_status():
    """飞书集成状态"""
    try:
        app_id = current_app.config.get('FEISHU_APP_ID')
        app_secret = current_app.config.get('FEISHU_APP_SECRET')
        
        if not app_id or not app_secret:
            return jsonify({
                'status': 'not_configured',
                'message': '飞书配置未完成'
            })
        
        feishu_service = FeishuService(app_id, app_secret)
        token = feishu_service.get_access_token()
        
        if token:
            return jsonify({
                'status': 'connected',
                'message': '飞书集成正常',
                'app_id': app_id,
                'groups': list(feishu_service.chat_ids.keys())
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '飞书连接失败'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'飞书状态检查失败: {str(e)}'
        })

