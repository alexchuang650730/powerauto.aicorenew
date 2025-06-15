from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit
import json
import os
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'powerautomation_unified_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 模擬用戶數據
users = {
    'admin': {'password': 'admin123', 'role': 'admin', 'credits': 5000},
    'user1': {'password': 'password1', 'role': 'user', 'credits': 2580},
    'manager': {'password': 'manager123', 'role': 'manager', 'credits': 10000}
}

# 平台配置
PLATFORM_CONFIGS = {
    'user': {
        'type': '使用者系統',
        'name': 'PowerAutomation',
        'theme_color': '#3b82f6',
        'features': ['代碼編輯', 'AI助手', '積分管理', '模型切換'],
        'default_model': 'qwen3-local'
    },
    'admin': {
        'type': '管理者系統', 
        'name': 'PowerAutomation Admin',
        'theme_color': '#1d4ed8',
        'features': ['用戶管理', '系統監控', '積分統計', '模型管理', '端雲協同'],
        'default_model': 'qwen8b-cloud'
    },
    'edge': {
        'type': '端側系統',
        'name': 'PowerAutomation Edge',
        'theme_color': '#2563eb',
        'features': ['本地推理', '端雲同步', '智能路由', '性能優化'],
        'default_model': 'qwen3-local'
    }
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    platform = request.args.get('platform', 'edge')
    return render_template('unified_blue_login.html', platform=platform)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    platform = data.get('platform', 'edge')
    
    if username in users and users[username]['password'] == password:
        session['user'] = username
        session['platform'] = platform
        session['login_time'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': '登錄成功',
            'redirect': '/editor',
            'user': {
                'username': username,
                'role': users[username]['role'],
                'credits': users[username]['credits'],
                'platform': platform
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': '用戶名或密碼錯誤'
        }), 401

@app.route('/editor')
def editor():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    platform = session.get('platform', 'edge')
    user_data = users[session['user']]
    
    return render_template('unified_blue_editor.html', 
                         platform=platform,
                         user=user_data,
                         config=PLATFORM_CONFIGS[platform])

@app.route('/api/platform-config')
def get_platform_config():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    platform = session.get('platform', 'edge')
    user_data = users[session['user']]
    
    return jsonify({
        'platform': platform,
        'config': PLATFORM_CONFIGS[platform],
        'user': {
            'username': session['user'],
            'role': user_data['role'],
            'credits': user_data['credits']
        }
    })

@app.route('/api/status')
def get_status():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    username = session['user']
    platform = session.get('platform', 'edge')
    user_data = users[username]
    
    # 模擬實時狀態數據
    import random
    
    status_data = {
        'model': {
            'current': 'Qwen3 本地' if platform == 'edge' else 'Qwen8B 雲端',
            'type': '本地推理' if platform == 'edge' else '雲端推理',
            'response_time': f"{random.uniform(1.0, 3.0):.1f}s"
        },
        'credits': {
            'amount': user_data['credits'],
            'last_sync': datetime.now().strftime('%H:%M')
        },
        'savings': {
            'local_processing': random.randint(60, 80),
            'cloud_processing': random.randint(20, 40),
            'today_savings': random.randint(1000, 2000),
            'savings_percentage': random.randint(35, 55)
        },
        'connection': {
            'status': 'connected',
            'latency': f"{random.randint(50, 200)}ms"
        }
    }
    
    # 確保本地+雲端處理比例為100%
    total = status_data['savings']['local_processing'] + status_data['savings']['cloud_processing']
    if total != 100:
        status_data['savings']['cloud_processing'] = 100 - status_data['savings']['local_processing']
    
    return jsonify(status_data)

@app.route('/api/model/switch', methods=['POST'])
def switch_model():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    model = data.get('model')
    
    # 模擬模型切換
    model_configs = {
        'qwen3-local': {
            'name': 'Qwen3 本地',
            'type': '本地推理',
            'response_time': '1.2s',
            'cost_per_token': 0
        },
        'qwen8b-cloud': {
            'name': 'Qwen8B 雲端',
            'type': '雲端推理', 
            'response_time': '2.8s',
            'cost_per_token': 0.001
        },
        'auto': {
            'name': '智能自動',
            'type': '混合推理',
            'response_time': '1.8s',
            'cost_per_token': 0.0005
        }
    }
    
    if model in model_configs:
        return jsonify({
            'success': True,
            'model': model_configs[model]
        })
    else:
        return jsonify({
            'success': False,
            'error': '不支持的模型'
        }), 400

@app.route('/api/credits/consume', methods=['POST'])
def consume_credits():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    amount = data.get('amount', 1)
    
    username = session['user']
    if users[username]['credits'] >= amount:
        users[username]['credits'] -= amount
        return jsonify({
            'success': True,
            'remaining_credits': users[username]['credits']
        })
    else:
        return jsonify({
            'success': False,
            'error': '積分不足'
        }), 400

@socketio.on('connect')
def handle_connect():
    if 'user' in session:
        emit('connected', {
            'message': '已連接到PowerAutomation服務器',
            'user': session['user'],
            'platform': session.get('platform', 'edge')
        })

@socketio.on('request_ai_suggestion')
def handle_ai_suggestion(data):
    if 'user' not in session:
        return
    
    code = data.get('code', '')
    cursor_position = data.get('cursor_position', 0)
    
    # 模擬AI建議生成
    suggestions = [
        {
            'type': 'optimization',
            'title': '性能優化建議',
            'content': '建議使用列表推導式來提高代碼性能',
            'confidence': 92,
            'code_snippet': '[x for x in items if condition(x)]'
        },
        {
            'type': 'completion',
            'title': '代碼補全',
            'content': '檢測到函數定義，建議添加文檔字符串',
            'confidence': 87,
            'code_snippet': '"""函數說明文檔"""'
        }
    ]
    
    emit('ai_suggestions', {
        'suggestions': suggestions,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 確保模板目錄存在
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 PowerAutomation 統一藍色系系統啟動中...")
    print("📱 支持三種平台模式:")
    print("   - 使用者系統: http://localhost:5001/login?platform=user")
    print("   - 管理者系統: http://localhost:5001/login?platform=admin") 
    print("   - 端側系統: http://localhost:5001/login?platform=edge")
    print("🔐 測試賬號:")
    print("   - admin / admin123 (管理員)")
    print("   - user1 / password1 (用戶)")
    print("   - manager / manager123 (經理)")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)

