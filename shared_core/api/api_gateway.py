"""
PowerAutomation v0.57 API Gateway
統一數據同步服務和API管理
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
import redis
import json
import uuid
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PowerAutomationAPIGateway:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'powerautomation-v057-secret-key'
        
        # 啟用CORS支持
        CORS(self.app, origins="*")
        
        # 初始化SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # 初始化Redis連接
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis連接成功")
        except:
            logger.warning("Redis連接失敗，使用內存存儲")
            self.redis_client = None
        
        # 內存存儲（Redis備用方案）
        self.memory_store = {}
        
        # 註冊路由
        self._register_routes()
        self._register_websocket_events()
    
    def _register_routes(self):
        """註冊API路由"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """健康檢查"""
            return jsonify({
                'status': 'healthy',
                'version': 'v0.57',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'api_gateway': True,
                    'redis': self.redis_client is not None,
                    'websocket': True
                }
            })
        
        @self.app.route('/api/auth/validate', methods=['POST'])
        def validate_token():
            """驗證用戶Token"""
            try:
                data = request.get_json()
                token = data.get('token')
                
                if not token:
                    return jsonify({'error': 'Token required'}), 400
                
                # 解碼JWT Token
                payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = payload.get('user_id')
                edition = payload.get('edition', 'personal_pro')
                
                return jsonify({
                    'valid': True,
                    'user_id': user_id,
                    'edition': edition,
                    'expires_at': payload.get('exp')
                })
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
            except Exception as e:
                logger.error(f"Token validation error: {e}")
                return jsonify({'error': 'Validation failed'}), 500
        
        @self.app.route('/api/credits/sync', methods=['POST'])
        def sync_credits():
            """同步積分數據"""
            try:
                data = request.get_json()
                user_id = data.get('user_id')
                credits = data.get('credits')
                transaction_type = data.get('transaction_type', 'sync')
                
                if not user_id or credits is None:
                    return jsonify({'error': 'user_id and credits required'}), 400
                
                # 更新積分緩存
                credits_data = {
                    'user_id': user_id,
                    'credits': credits,
                    'last_updated': datetime.now().isoformat(),
                    'transaction_type': transaction_type
                }
                
                self._store_data(f'credits:{user_id}', credits_data)
                
                # 實時推送到所有相關連接
                self.socketio.emit('credits_updated', credits_data, room=f'user_{user_id}')
                
                logger.info(f"Credits synced for user {user_id}: {credits}")
                
                return jsonify({
                    'success': True,
                    'user_id': user_id,
                    'credits': credits,
                    'synced_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Credits sync error: {e}")
                return jsonify({'error': 'Sync failed'}), 500
        
        @self.app.route('/api/credits/balance/<user_id>', methods=['GET'])
        def get_credits_balance(user_id):
            """獲取用戶積分餘額"""
            try:
                credits_data = self._get_data(f'credits:{user_id}')
                
                if not credits_data:
                    return jsonify({'error': 'User credits not found'}), 404
                
                return jsonify({
                    'user_id': user_id,
                    'credits': credits_data.get('credits', 0),
                    'last_updated': credits_data.get('last_updated'),
                    'transaction_type': credits_data.get('transaction_type')
                })
                
            except Exception as e:
                logger.error(f"Get credits balance error: {e}")
                return jsonify({'error': 'Failed to get balance'}), 500
        
        @self.app.route('/api/ui/config/<user_id>', methods=['GET'])
        def get_ui_config(user_id):
            """獲取用戶UI配置"""
            try:
                # 獲取用戶版本信息
                user_data = self._get_data(f'user:{user_id}')
                edition = user_data.get('edition', 'personal_pro') if user_data else 'personal_pro'
                
                # 根據版本返回不同的UI配置
                ui_config = self._get_ui_config_by_edition(edition)
                
                return jsonify({
                    'user_id': user_id,
                    'edition': edition,
                    'ui_config': ui_config,
                    'last_updated': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Get UI config error: {e}")
                return jsonify({'error': 'Failed to get UI config'}), 500
        
        @self.app.route('/api/ui/config/<user_id>', methods=['POST'])
        def update_ui_config(user_id):
            """更新用戶UI配置（Administrator功能）"""
            try:
                data = request.get_json()
                admin_token = data.get('admin_token')
                ui_config = data.get('ui_config')
                
                # 驗證管理員權限
                if not self._validate_admin_token(admin_token):
                    return jsonify({'error': 'Admin permission required'}), 403
                
                # 更新UI配置
                config_data = {
                    'user_id': user_id,
                    'ui_config': ui_config,
                    'updated_by': 'administrator',
                    'updated_at': datetime.now().isoformat()
                }
                
                self._store_data(f'ui_config:{user_id}', config_data)
                
                # 實時推送UI配置更新
                self.socketio.emit('ui_config_updated', config_data, room=f'user_{user_id}')
                
                logger.info(f"UI config updated for user {user_id} by administrator")
                
                return jsonify({
                    'success': True,
                    'user_id': user_id,
                    'updated_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Update UI config error: {e}")
                return jsonify({'error': 'Failed to update UI config'}), 500
    
    def _register_websocket_events(self):
        """註冊WebSocket事件"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客戶端連接"""
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'status': 'success', 'session_id': request.sid})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客戶端斷開連接"""
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_user_room')
        def handle_join_user_room(data):
            """加入用戶房間（用於接收個人數據更新）"""
            try:
                user_id = data.get('user_id')
                token = data.get('token')
                
                # 驗證用戶身份
                if self._validate_user_token(token, user_id):
                    room = f'user_{user_id}'
                    join_room(room)
                    emit('joined_room', {'room': room, 'user_id': user_id})
                    logger.info(f"User {user_id} joined room {room}")
                else:
                    emit('error', {'message': 'Invalid token or user_id'})
                    
            except Exception as e:
                logger.error(f"Join user room error: {e}")
                emit('error', {'message': 'Failed to join room'})
        
        @self.socketio.on('leave_user_room')
        def handle_leave_user_room(data):
            """離開用戶房間"""
            try:
                user_id = data.get('user_id')
                room = f'user_{user_id}'
                leave_room(room)
                emit('left_room', {'room': room, 'user_id': user_id})
                logger.info(f"User {user_id} left room {room}")
                
            except Exception as e:
                logger.error(f"Leave user room error: {e}")
                emit('error', {'message': 'Failed to leave room'})
        
        @self.socketio.on('ping')
        def handle_ping():
            """心跳檢測"""
            emit('pong', {'timestamp': datetime.now().isoformat()})
    
    def _store_data(self, key: str, data: Dict[str, Any]):
        """存儲數據（Redis或內存）"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, 3600, json.dumps(data))  # 1小時過期
            else:
                self.memory_store[key] = data
        except Exception as e:
            logger.error(f"Store data error: {e}")
    
    def _get_data(self, key: str) -> Optional[Dict[str, Any]]:
        """獲取數據（Redis或內存）"""
        try:
            if self.redis_client:
                data = self.redis_client.get(key)
                return json.loads(data) if data else None
            else:
                return self.memory_store.get(key)
        except Exception as e:
            logger.error(f"Get data error: {e}")
            return None
    
    def _get_ui_config_by_edition(self, edition: str) -> Dict[str, Any]:
        """根據版本獲取UI配置"""
        base_config = {
            'theme': 'modern',
            'layout': 'sidebar',
            'features': []
        }
        
        if edition == 'enterprise':
            base_config['features'] = [
                'requirement_analysis',
                'architecture_design', 
                'code_implementation',
                'test_verification',
                'deployment_release',
                'monitoring_operations'
            ]
            base_config['admin_features'] = [
                'user_management',
                'permission_control',
                'ui_customization',
                'audit_logs'
            ]
        elif edition == 'personal_pro':
            base_config['features'] = [
                'code_implementation',
                'test_verification',
                'deployment_release'
            ]
            base_config['admin_features'] = [
                'credits_management',
                'usage_statistics'
            ]
        else:  # opensource
            base_config['features'] = [
                'code_implementation'
            ]
            base_config['interface'] = 'cli'
        
        return base_config
    
    def _validate_user_token(self, token: str, user_id: str) -> bool:
        """驗證用戶Token"""
        try:
            payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload.get('user_id') == user_id
        except:
            return False
    
    def _validate_admin_token(self, token: str) -> bool:
        """驗證管理員Token"""
        try:
            payload = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload.get('role') == 'administrator'
        except:
            return False
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """啟動API Gateway"""
        logger.info(f"Starting PowerAutomation API Gateway v0.57 on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    # 創建並啟動API Gateway
    gateway = PowerAutomationAPIGateway()
    gateway.run(debug=True)

