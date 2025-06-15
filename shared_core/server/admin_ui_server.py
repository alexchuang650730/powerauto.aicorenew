#!/usr/bin/env python3
"""
PowerAutomation v0.56 - 端側Admin UI服務器
整合Kilo Code引擎和一鍵錄製工作流功能

Author: PowerAutomation Team
Version: 0.56
Date: 2025-06-10
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import asyncio
import json
import threading
import time
from pathlib import Path
import os
import sys

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

from engines.kilo_code_engine import KiloCodeEngine, InterventionEvent
from engines.real_token_saving_system import RealTokenSavingSystem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'powerautomation_v056_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局變量
kilo_code_engine = None
token_saving_system = None
admin_metrics = {
    'total_interventions': 0,
    'successful_workflows': 0,
    'token_saved': 0,
    'cost_saved': 0.0,
    'active_recordings': 0
}

class AdminUIServer:
    """端側Admin UI服務器"""
    
    def __init__(self):
        self.kilo_code_engine = KiloCodeEngine()
        self.token_saving_system = RealTokenSavingSystem()
        self.is_running = False
        
    async def start_services(self):
        """啟動所有服務"""
        try:
            # 啟動Kilo Code引擎
            await self.kilo_code_engine.start_engine(host="localhost", port=8765)
            
            # 啟動Token節省系統
            self.token_saving_system.start_monitoring()
            
            self.is_running = True
            print("✅ 所有服務已啟動")
            
        except Exception as e:
            print(f"❌ 服務啟動失敗: {e}")
            
    async def stop_services(self):
        """停止所有服務"""
        try:
            await self.kilo_code_engine.stop_engine()
            self.token_saving_system.stop_monitoring()
            self.is_running = False
            print("✅ 所有服務已停止")
        except Exception as e:
            print(f"❌ 服務停止失敗: {e}")

# 創建服務器實例
admin_server = AdminUIServer()

@app.route('/')
def index():
    """主頁面"""
    return render_template('admin_dashboard.html')

@app.route('/workflow-recorder')
def workflow_recorder():
    """工作流錄製頁面"""
    return render_template('workflow_recorder.html')

@app.route('/api/metrics')
def get_metrics():
    """獲取系統指標"""
    return jsonify(admin_metrics)

@app.route('/api/intervention/analyze', methods=['POST'])
def analyze_conversation():
    """分析對話並判斷是否需要介入"""
    try:
        data = request.get_json()
        conversation = data.get('conversation', '')
        
        # 使用Kilo Code引擎分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'conversation_analysis',
            'conversation': conversation
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        # 更新指標
        if result.get('intervention_needed'):
            admin_metrics['total_interventions'] += 1
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflow/start', methods=['POST'])
def start_workflow_recording():
    """開始工作流錄製"""
    try:
        data = request.get_json()
        workflow_name = data.get('workflow_name', f'工作流_{int(time.time())}')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'workflow_recording',
            'action': 'start',
            'workflow_name': workflow_name
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        if result.get('status') == 'success':
            admin_metrics['active_recordings'] += 1
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflow/record', methods=['POST'])
def record_workflow_action():
    """錄製工作流動作"""
    try:
        data = request.get_json()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'workflow_recording',
            'action': 'record',
            'action_type': data.get('action_type'),
            'target': data.get('target'),
            'value': data.get('value', '')
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflow/stop', methods=['POST'])
def stop_workflow_recording():
    """停止工作流錄製"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'workflow_recording',
            'action': 'stop'
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        if result.get('status') == 'success':
            admin_metrics['active_recordings'] = max(0, admin_metrics['active_recordings'] - 1)
            admin_metrics['successful_workflows'] += 1
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/workflow/execute', methods=['POST'])
def execute_workflow():
    """執行工作流"""
    try:
        data = request.get_json()
        workflow_definition = data.get('workflow')
        variables = data.get('variables', {})
        
        # 模擬工作流執行
        execution_result = {
            'status': 'success',
            'execution_id': f'exec_{int(time.time())}',
            'steps_completed': len(workflow_definition.get('steps', [])),
            'execution_time': 2.5,
            'variables_used': variables
        }
        
        return jsonify(execution_result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/token-saving/status')
def get_token_saving_status():
    """獲取Token節省狀態"""
    try:
        # 獲取Token節省系統狀態
        status = admin_server.token_saving_system.get_current_status()
        
        # 更新全局指標
        admin_metrics['token_saved'] = status.get('total_tokens_saved', 0)
        admin_metrics['cost_saved'] = status.get('total_cost_saved', 0.0)
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# WebSocket事件處理
@socketio.on('connect')
def handle_connect():
    """處理WebSocket連接"""
    print('客戶端已連接')
    emit('status', {'message': '已連接到PowerAutomation v0.56 Admin'})

@socketio.on('disconnect')
def handle_disconnect():
    """處理WebSocket斷開"""
    print('客戶端已斷開')

@socketio.on('start_recording')
def handle_start_recording(data):
    """處理開始錄製事件"""
    workflow_name = data.get('workflow_name', f'工作流_{int(time.time())}')
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'workflow_recording',
            'action': 'start',
            'workflow_name': workflow_name
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        emit('recording_started', result)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('record_action')
def handle_record_action(data):
    """處理錄製動作事件"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'workflow_recording',
            'action': 'record',
            'action_type': data.get('action_type'),
            'target': data.get('target'),
            'value': data.get('value', '')
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        emit('action_recorded', result)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_recording')
def handle_stop_recording():
    """處理停止錄製事件"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        request_data = {
            'type': 'workflow_recording',
            'action': 'stop'
        }
        
        result = loop.run_until_complete(
            admin_server.kilo_code_engine.intervention_coordinator.process_intervention_request(request_data)
        )
        
        emit('recording_stopped', result)
        
    except Exception as e:
        emit('error', {'message': str(e)})

def start_background_services():
    """在後台線程中啟動服務"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(admin_server.start_services())

if __name__ == '__main__':
    print("🚀 PowerAutomation v0.56 - 端側Admin UI服務器")
    print("=" * 60)
    
    # 在後台線程中啟動服務
    service_thread = threading.Thread(target=start_background_services)
    service_thread.daemon = True
    service_thread.start()
    
    # 等待服務啟動
    time.sleep(2)
    
    # 啟動Flask應用
    print("🌐 Admin UI服務器啟動中...")
    print("📱 訪問地址: http://localhost:5000")
    print("🔧 工作流錄製: http://localhost:5000/workflow-recorder")
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n⏹️ 正在停止服務...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(admin_server.stop_services())

