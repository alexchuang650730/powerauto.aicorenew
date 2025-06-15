# SmartUI 智慧用户界面系统

## 🎯 系统概述

SmartUI是PowerAutomation生态系统中的智慧用户界面系统，采用前后端分离架构，提供完整的Web管理界面和API服务。系统集成了飞书SDK、MCP协调器、GitHub Webhook等核心功能，为用户提供直观、高效的智能自动化管理体验。

### 核心特色
- **🎨 现代化界面设计** - 响应式三栏布局，支持桌面和移动设备
- **🔗 完整前后端分离** - Flask后端API + HTML/JavaScript前端
- **🤖 智能交互体验** - AI聊天界面，实时状态监控
- **🔧 企业级集成** - 飞书、GitHub、MCP协调器无缝集成
- **📊 实时数据可视化** - 工作流状态、系统监控、性能指标

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    SmartUI 智慧界面系统                      │
├─────────────────────────────────────────────────────────────┤
│  前端层 (Frontend)                                          │
│  ├─ 智慧Dashboard (1615行)                                 │
│  ├─ AI聊天界面 (1205行)                                    │
│  ├─ Web管理界面 (1136行)                                   │
│  └─ Manus智能介入界面 (845行)                              │
├─────────────────────────────────────────────────────────────┤
│  后端层 (Backend - Flask)                                   │
│  ├─ API路由层                                               │
│  │  ├─ 用户管理API (/api)                                  │
│  │  ├─ 飞书集成API (/api/feishu)                          │
│  │  ├─ MCP协调器API (/api/mcp)                            │
│  │  └─ GitHub Webhook API (/api/github)                   │
│  ├─ 数据模型层                                              │
│  │  ├─ 用户模型                                            │
│  │  ├─ 工作流模型                                          │
│  │  └─ 系统配置模型                                        │
│  └─ 数据存储层                                              │
│     ├─ SQLite数据库                                        │
│     └─ 静态文件存储                                        │
├─────────────────────────────────────────────────────────────┤
│  集成层 (Integration)                                       │
│  ├─ 飞书SDK集成                                             │
│  ├─ GitHub API集成                                          │
│  ├─ MCP协调器集成                                           │
│  └─ PowerAutomation核心系统集成                            │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构详解

```
smartui/
├── 📁 src/                     # 后端源码 (Flask应用)
│   ├── main.py                 # Flask主程序 (47行)
│   ├── __init__.py             # 包初始化
│   ├── 📁 routes/              # API路由模块
│   │   ├── user.py             # 用户管理API (30行)
│   │   ├── feishu.py           # 飞书集成API (280行)
│   │   ├── mcp_coordinator.py  # MCP协调器API (300行)
│   │   └── github_webhook.py   # GitHub Webhook API (330行)
│   ├── 📁 models/              # 数据模型
│   │   ├── user.py             # 用户数据模型
│   │   ├── workflow.py         # 工作流数据模型
│   │   └── system_config.py    # 系统配置模型
│   ├── 📁 database/            # 数据库文件
│   │   └── app.db              # SQLite数据库
│   └── 📁 static/              # 静态资源
│       └── index.html          # 默认首页
├── 📁 frontend/                # 前端界面文件
│   ├── smart_ui_enhanced_dashboard.html      # 主Dashboard (1615行)
│   ├── ai_chat_interface_v2.html            # AI聊天界面 (1205行)
│   ├── client_webadmin_v2.html              # Web管理界面 (1136行)
│   ├── smart_ui_manus_app_intervention.html # Manus介入界面 (845行)
│   ├── remote_deploy.sh                     # 远程部署脚本
│   └── AI_CHAT_INTERFACE_SPEC_v0.2.md       # 接口规范文档
└── requirements.txt            # Python依赖包
```

## 🔧 核心组件详解

### 1. 后端服务 (Flask Backend)

#### 主程序 (main.py)
**功能**: SmartUI系统的核心服务器
- **Flask应用初始化**: 配置CORS、数据库、蓝图注册
- **环境变量管理**: 飞书、GitHub、MCP协调器配置
- **静态文件服务**: 前端界面文件托管
- **数据库集成**: SQLite数据库自动初始化

#### API路由系统

**用户管理API** (`/api`)
```python
# 基础用户功能
GET  /api/users          # 获取用户列表
POST /api/users          # 创建新用户
GET  /api/users/{id}     # 获取用户详情
PUT  /api/users/{id}     # 更新用户信息
```

**飞书集成API** (`/api/feishu`)
```python
# 飞书企业协作集成
POST /api/feishu/webhook           # 飞书事件回调
GET  /api/feishu/groups           # 获取群组列表
POST /api/feishu/send_message     # 发送飞书消息
GET  /api/feishu/notifications    # 获取通知列表
```

**MCP协调器API** (`/api/mcp`)
```python
# MCP工具协调管理
GET  /api/mcp/status              # MCP系统状态
GET  /api/mcp/workflow/nodes      # 工作流节点状态
POST /api/mcp/intervention/trigger # 触发智能介入
GET  /api/mcp/tools               # 获取可用工具列表
```

**GitHub集成API** (`/api/github`)
```python
# GitHub代码仓库集成
POST /api/github/webhook          # GitHub事件回调
GET  /api/github/repos            # 获取仓库列表
GET  /api/github/sync/status      # 同步状态查询
POST /api/github/deploy           # 触发部署
```

### 2. 前端界面系统

#### 智慧Dashboard (smart_ui_enhanced_dashboard.html)
**功能**: 系统主控制台，三栏布局设计
- **左侧状态面板** (280px宽度):
  - MCP协调器状态监控
  - 飞书集成状态显示
  - GitHub同步状态追踪
  - 系统资源使用情况
- **中间AI对话区域** (flex-1):
  - 智能对话界面
  - 实时消息交互
  - AI建议卡片显示
  - 历史对话记录
- **右侧工作流Dashboard** (400px宽度):
  - 三节点工作流可视化
  - 实时进度监控
  - 快速操作按钮
  - 性能指标展示

#### AI聊天界面 (ai_chat_interface_v2.html)
**功能**: 专门的AI交互界面
- **消息输入区域**: 支持文本和文件输入
- **对话历史**: 完整的对话记录和搜索
- **智能建议**: 基于上下文的智能建议
- **多模态支持**: 文本、图片、文件等多种输入

#### Web管理界面 (client_webadmin_v2.html)
**功能**: 系统管理和配置界面
- **用户管理**: 用户账户创建、编辑、权限管理
- **系统配置**: 飞书、GitHub、MCP等集成配置
- **监控面板**: 系统性能和使用情况监控
- **日志查看**: 系统操作日志和错误日志

#### Manus智能介入界面 (smart_ui_manus_app_intervention.html)
**功能**: Manus应用智能介入专用界面
- **介入触发**: 手动和自动介入触发
- **状态监控**: Manus应用状态实时监控
- **建议展示**: 智能介入建议和操作指导
- **历史记录**: 介入历史和效果分析


## 🛠️ 技术栈详解

### 后端技术栈

#### 核心框架
- **Flask 2.3+**: 轻量级Web框架
  - 蓝图 (Blueprint) 模块化路由管理
  - CORS跨域支持
  - 静态文件服务
  - 环境变量配置管理

#### 数据存储
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级关系数据库
- **文件存储**: 静态资源和上传文件管理

#### 集成SDK
- **飞书SDK**: 企业协作平台集成
  - 事件回调处理
  - 消息发送和接收
  - 群组管理
  - 用户认证
- **GitHub API**: 代码仓库集成
  - Webhook事件处理
  - 仓库信息获取
  - 自动化部署触发
  - 同步状态管理

#### 网络通信
- **requests**: HTTP客户端库
- **hmac/hashlib**: 安全签名验证
- **json**: 数据序列化和反序列化

### 前端技术栈

#### 核心技术
- **HTML5**: 现代Web标准
  - 语义化标签
  - 响应式设计
  - 移动设备支持
- **CSS3**: 样式和布局
  - Flexbox布局
  - CSS Grid
  - 动画和过渡效果
  - 媒体查询
- **JavaScript ES6+**: 前端交互逻辑
  - 异步编程 (async/await)
  - 模块化开发
  - DOM操作
  - 事件处理

#### UI/UX设计
- **Font Awesome 6.4.0**: 图标库
- **响应式设计**: 支持桌面、平板、手机
- **三栏布局**: 状态面板 + 主内容区 + 工作流面板
- **现代化配色**: 白色背景 + 深色文字 + 蓝色强调

#### 数据交互
- **Fetch API**: 现代HTTP请求
- **WebSocket**: 实时数据通信 (规划中)
- **JSON**: 数据格式标准
- **RESTful API**: 标准化接口调用

## 📊 功能特性详解

### 🎨 用户界面特性

#### 响应式设计
- **桌面端**: 三栏布局，充分利用屏幕空间
- **平板端**: 自适应布局，优化触控体验
- **手机端**: 单栏布局，简化操作流程

#### 交互体验
- **实时更新**: 系统状态和数据实时刷新
- **智能提示**: 基于上下文的操作建议
- **快速操作**: 一键触发常用功能
- **视觉反馈**: 操作状态和结果即时显示

### 🔗 集成功能特性

#### 飞书企业协作
- **消息推送**: 系统事件自动推送到飞书群组
- **工作流通知**: 工作流状态变更实时通知
- **团队协作**: 支持多人协作和权限管理
- **移动办公**: 通过飞书移动端远程管理

#### GitHub代码管理
- **自动同步**: 代码仓库变更自动同步
- **部署触发**: 代码提交自动触发部署流程
- **状态监控**: 部署状态和结果实时监控
- **版本管理**: 支持多分支和版本控制

#### MCP工具协调
- **智能路由**: 自动选择最适合的MCP工具
- **状态监控**: MCP工具运行状态实时监控
- **性能分析**: 工具使用情况和性能分析
- **扩展支持**: 支持新MCP工具的动态加载

### 🚀 性能特性

#### 高性能架构
- **异步处理**: 非阻塞I/O操作
- **缓存机制**: 数据缓存减少重复请求
- **连接池**: 数据库连接复用
- **静态资源优化**: CSS/JS文件压缩和缓存

#### 可扩展性
- **模块化设计**: 组件独立，易于扩展
- **插件架构**: 支持第三方插件集成
- **API标准化**: RESTful API便于集成
- **配置灵活**: 环境变量配置，适应不同部署环境

## 🚀 安装和部署

### 环境要求
- **Python**: 3.11+
- **操作系统**: Windows 10+, macOS 12+, Ubuntu 20.04+
- **内存**: 最少2GB，推荐4GB+
- **存储**: 最少500MB可用空间
- **网络**: 需要访问飞书和GitHub API

### 快速安装

#### 1. 安装依赖
```bash
# 进入SmartUI目录
cd smartui/

# 安装Python依赖
pip install -r requirements.txt
```

#### 2. 配置环境变量
```bash
# 创建环境配置文件
cat > .env << EOF
# 飞书配置
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_VERIFICATION_TOKEN=your_verification_token
FEISHU_ENCRYPT_KEY=your_encrypt_key

# GitHub配置
GITHUB_WEBHOOK_SECRET=your_github_webhook_secret

# MCP协调器配置
MCP_COORDINATOR_URL=http://localhost:8001
EOF
```

#### 3. 初始化数据库
```bash
# 进入src目录
cd src/

# 初始化数据库
python -c "
from main import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"
```

#### 4. 启动服务
```bash
# 启动Flask后端服务
python main.py

# 服务启动在 http://localhost:5001
```

### 访问界面

#### Web界面访问地址
- **主Dashboard**: `http://localhost:5001/static/smart_ui_enhanced_dashboard.html`
- **AI聊天界面**: `http://localhost:5001/static/ai_chat_interface_v2.html`
- **Web管理界面**: `http://localhost:5001/static/client_webadmin_v2.html`
- **Manus介入界面**: `http://localhost:5001/static/smart_ui_manus_app_intervention.html`

#### API接口测试
```bash
# 测试系统状态
curl http://localhost:5001/api/mcp/status

# 测试用户API
curl http://localhost:5001/api/users

# 测试飞书集成
curl http://localhost:5001/api/feishu/groups
```

## 📖 使用指南

### 基本使用流程

#### 1. 系统初始化
1. 启动SmartUI后端服务
2. 访问主Dashboard界面
3. 检查系统状态指示器
4. 确认各集成服务连接正常

#### 2. 日常操作
1. **监控系统状态**: 通过左侧状态面板实时监控
2. **AI交互**: 在中间对话区域与AI助手交互
3. **工作流管理**: 通过右侧面板管理工作流程
4. **快速操作**: 使用快捷按钮执行常用操作

#### 3. 高级功能
1. **智能介入**: 配置和触发Manus智能介入
2. **自动化部署**: 通过GitHub集成自动部署
3. **团队协作**: 通过飞书集成进行团队协作
4. **系统管理**: 通过Web管理界面进行系统配置

### API使用示例

#### 获取系统状态
```javascript
// 获取MCP协调器状态
const response = await fetch('/api/mcp/status');
const status = await response.json();
console.log('MCP状态:', status);
```

#### 发送飞书消息
```javascript
// 发送消息到飞书群组
const response = await fetch('/api/feishu/send_message', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        group_id: 'group_123',
        message: '系统部署完成',
        message_type: 'text'
    })
});
```

#### 触发智能介入
```javascript
// 触发Manus智能介入
const response = await fetch('/api/mcp/intervention/trigger', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        type: 'performance_issue',
        context: '检测到性能问题',
        auto_fix: true
    })
});
```

### 界面操作指南

#### 主Dashboard操作
1. **状态监控**: 左侧面板显示各系统状态
   - 绿色: 正常运行
   - 黄色: 警告状态
   - 红色: 错误状态
2. **AI对话**: 中间区域进行AI交互
   - 输入框: 输入问题或指令
   - 发送按钮: 发送消息
   - 历史记录: 查看对话历史
3. **工作流控制**: 右侧面板管理工作流
   - 节点状态: 查看各节点运行状态
   - 进度条: 显示任务完成进度
   - 操作按钮: 启动、暂停、重启工作流

#### AI聊天界面操作
1. **消息输入**: 支持文本、文件、图片输入
2. **智能建议**: 系统自动提供相关建议
3. **历史搜索**: 搜索历史对话内容
4. **导出功能**: 导出对话记录

#### Web管理界面操作
1. **用户管理**: 创建、编辑、删除用户账户
2. **权限设置**: 配置用户权限和角色
3. **系统配置**: 修改系统参数和集成设置
4. **日志查看**: 查看系统运行日志和错误日志


## 🔧 开发指南

### 开发环境搭建

#### 1. 开发工具推荐
- **IDE**: Visual Studio Code, PyCharm
- **Python**: 3.11+ (推荐使用虚拟环境)
- **浏览器**: Chrome/Firefox (用于前端调试)
- **API测试**: Postman, curl

#### 2. 开发环境配置
```bash
# 创建虚拟环境
python -m venv smartui_dev
source smartui_dev/bin/activate  # Linux/Mac
# 或
smartui_dev\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install flask-debugtoolbar  # 调试工具
pip install pytest              # 测试框架
```

#### 3. 开发模式启动
```bash
# 设置开发环境变量
export FLASK_ENV=development
export FLASK_DEBUG=1

# 启动开发服务器
cd src/
python main.py
```

### 后端开发

#### 添加新的API路由
```python
# 1. 在 src/routes/ 目录下创建新的路由文件
# 例如: src/routes/new_feature.py

from flask import Blueprint, request, jsonify

new_feature_bp = Blueprint('new_feature', __name__)

@new_feature_bp.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'status': 'success',
        'message': '新功能测试接口'
    })

# 2. 在 main.py 中注册新的蓝图
from src.routes.new_feature import new_feature_bp
app.register_blueprint(new_feature_bp, url_prefix='/api/new_feature')
```

#### 数据模型开发
```python
# 在 src/models/ 目录下创建新的数据模型
# 例如: src/models/workflow.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Workflow(db.Model):
    __tablename__ = 'workflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
```

### 前端开发

#### 界面开发规范
```html
<!-- 标准HTML结构 -->
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartUI - 功能名称</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <!-- 页面内容 -->
</body>
</html>
```

#### CSS样式规范
```css
/* 使用统一的设计系统 */
:root {
    --primary-color: #3b82f6;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --background-color: #ffffff;
    --text-color: #1f2937;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .desktop-only {
        display: none;
    }
}
```

#### JavaScript开发规范
```javascript
// 使用现代JavaScript语法
class SmartUIComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.apiBaseUrl = '/api';
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.bindEvents();
    }
    
    async loadData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/data`);
            const data = await response.json();
            this.renderData(data);
        } catch (error) {
            console.error('数据加载失败:', error);
        }
    }
    
    bindEvents() {
        // 事件绑定逻辑
    }
    
    renderData(data) {
        // 数据渲染逻辑
    }
}
```

### 测试开发

#### 后端API测试
```python
# tests/test_api.py
import pytest
from src.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_mcp_status(client):
    """测试MCP状态API"""
    response = client.get('/api/mcp/status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data

def test_user_creation(client):
    """测试用户创建API"""
    response = client.post('/api/users', json={
        'username': 'test_user',
        'email': 'test@example.com'
    })
    assert response.status_code == 201
```

#### 前端功能测试
```javascript
// 使用浏览器开发者工具进行测试
// 或集成自动化测试框架

// 测试API调用
async function testAPICall() {
    try {
        const response = await fetch('/api/mcp/status');
        const data = await response.json();
        console.log('API测试成功:', data);
    } catch (error) {
        console.error('API测试失败:', error);
    }
}

// 测试界面交互
function testUIInteraction() {
    const button = document.getElementById('test-button');
    button.click();
    // 验证预期结果
}
```

## 🛡️ 安全和性能

### 安全特性

#### 数据安全
- **输入验证**: 所有用户输入进行严格验证
- **SQL注入防护**: 使用ORM防止SQL注入
- **XSS防护**: 输出数据进行HTML转义
- **CSRF防护**: 使用CSRF令牌保护表单

#### 认证和授权
- **会话管理**: 安全的会话管理机制
- **权限控制**: 基于角色的访问控制
- **API安全**: API密钥和签名验证
- **数据加密**: 敏感数据加密存储

#### 网络安全
- **HTTPS支持**: 生产环境强制HTTPS
- **CORS配置**: 合理的跨域资源共享配置
- **请求限制**: API请求频率限制
- **日志审计**: 完整的安全日志记录

### 性能优化

#### 后端性能
- **数据库优化**: 索引优化、查询优化
- **缓存策略**: Redis缓存、内存缓存
- **异步处理**: 长时间任务异步执行
- **连接池**: 数据库连接池管理

#### 前端性能
- **资源压缩**: CSS/JS文件压缩
- **图片优化**: 图片格式和大小优化
- **懒加载**: 按需加载内容
- **CDN加速**: 静态资源CDN分发

#### 监控和调优
- **性能监控**: 实时性能指标监控
- **错误追踪**: 错误日志和异常追踪
- **资源监控**: CPU、内存、磁盘使用监控
- **用户体验**: 页面加载时间、响应时间监控

## 🚀 部署和运维

### 生产环境部署

#### 1. 服务器配置
```bash
# 系统要求
- CPU: 2核心以上
- 内存: 4GB以上
- 存储: 20GB以上
- 网络: 稳定的互联网连接

# 软件要求
- Python 3.11+
- Nginx (反向代理)
- Supervisor (进程管理)
- SQLite/PostgreSQL (数据库)
```

#### 2. 部署脚本
```bash
#!/bin/bash
# deploy.sh - SmartUI部署脚本

# 1. 更新代码
git pull origin main

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库迁移
python -c "
from src.main import app, db
with app.app_context():
    db.create_all()
"

# 4. 重启服务
supervisorctl restart smartui

# 5. 重载Nginx配置
nginx -s reload

echo "SmartUI部署完成"
```

#### 3. Nginx配置
```nginx
# /etc/nginx/sites-available/smartui
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static/ {
        alias /path/to/smartui/src/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 4. Supervisor配置
```ini
# /etc/supervisor/conf.d/smartui.conf
[program:smartui]
command=/path/to/venv/bin/python /path/to/smartui/src/main.py
directory=/path/to/smartui/src
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/smartui.log
```

### 运维管理

#### 日志管理
```bash
# 查看应用日志
tail -f /var/log/smartui.log

# 查看Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 查看系统日志
journalctl -u smartui -f
```

#### 备份策略
```bash
#!/bin/bash
# backup.sh - 数据备份脚本

# 备份数据库
cp /path/to/smartui/src/database/app.db /backup/smartui_$(date +%Y%m%d_%H%M%S).db

# 备份配置文件
tar -czf /backup/smartui_config_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/smartui/src/

# 清理旧备份 (保留30天)
find /backup -name "smartui_*" -mtime +30 -delete
```

#### 监控告警
```bash
# 健康检查脚本
#!/bin/bash
# health_check.sh

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/mcp/status)

if [ $response -eq 200 ]; then
    echo "SmartUI服务正常"
else
    echo "SmartUI服务异常，状态码: $response"
    # 发送告警通知
    curl -X POST "https://api.feishu.cn/webhook/xxx" \
         -H "Content-Type: application/json" \
         -d '{"msg_type":"text","content":{"text":"SmartUI服务异常"}}'
fi
```

## 📞 支持和维护

### 常见问题解决

#### 1. 服务启动失败
```bash
# 检查端口占用
netstat -tlnp | grep :5001

# 检查Python环境
python --version
pip list | grep flask

# 查看错误日志
tail -f /var/log/smartui.log
```

#### 2. 数据库连接问题
```bash
# 检查数据库文件权限
ls -la src/database/app.db

# 重新初始化数据库
python -c "
from src.main import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
"
```

#### 3. 前端界面无法访问
```bash
# 检查静态文件路径
ls -la src/static/

# 检查Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

### 技术支持

#### 联系方式
- **GitHub Issues**: 提交Bug报告和功能请求
- **技术文档**: 查看详细的API文档和开发指南
- **社区讨论**: 参与开发者社区讨论

#### 贡献指南
1. Fork项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request
5. 代码审查和合并

### 版本更新

#### 更新流程
1. **备份数据**: 更新前备份重要数据
2. **停止服务**: 停止SmartUI服务
3. **更新代码**: 拉取最新代码
4. **安装依赖**: 更新Python依赖包
5. **数据库迁移**: 执行数据库结构更新
6. **重启服务**: 重新启动SmartUI服务
7. **验证功能**: 验证更新后功能正常

#### 版本兼容性
- **向后兼容**: 新版本保持API向后兼容
- **数据迁移**: 提供数据库迁移脚本
- **配置更新**: 自动更新配置文件格式
- **功能废弃**: 提前通知功能废弃计划

---

## 📄 附录

### API接口完整列表

#### 用户管理API
```
GET    /api/users              # 获取用户列表
POST   /api/users              # 创建新用户
GET    /api/users/{id}         # 获取用户详情
PUT    /api/users/{id}         # 更新用户信息
DELETE /api/users/{id}         # 删除用户
```

#### 飞书集成API
```
POST   /api/feishu/webhook           # 飞书事件回调
GET    /api/feishu/groups           # 获取群组列表
POST   /api/feishu/send_message     # 发送飞书消息
GET    /api/feishu/notifications    # 获取通知列表
POST   /api/feishu/upload_file      # 上传文件到飞书
```

#### MCP协调器API
```
GET    /api/mcp/status              # MCP系统状态
GET    /api/mcp/workflow/nodes      # 工作流节点状态
POST   /api/mcp/intervention/trigger # 触发智能介入
GET    /api/mcp/tools               # 获取可用工具列表
POST   /api/mcp/tools/execute       # 执行MCP工具
```

#### GitHub集成API
```
POST   /api/github/webhook          # GitHub事件回调
GET    /api/github/repos            # 获取仓库列表
GET    /api/github/sync/status      # 同步状态查询
POST   /api/github/deploy           # 触发部署
GET    /api/github/branches         # 获取分支列表
```

### 配置参数说明

#### 环境变量配置
```bash
# 飞书配置
FEISHU_APP_ID=cli_powerautomation          # 飞书应用ID
FEISHU_APP_SECRET=your_app_secret          # 飞书应用密钥
FEISHU_VERIFICATION_TOKEN=your_token       # 飞书验证令牌
FEISHU_ENCRYPT_KEY=your_encrypt_key        # 飞书加密密钥

# GitHub配置
GITHUB_WEBHOOK_SECRET=your_webhook_secret  # GitHub Webhook密钥

# MCP协调器配置
MCP_COORDINATOR_URL=http://localhost:8001  # MCP协调器地址

# 数据库配置
DATABASE_URL=sqlite:///app.db              # 数据库连接字符串

# 服务配置
FLASK_ENV=production                       # Flask运行环境
FLASK_DEBUG=0                             # 调试模式开关
SECRET_KEY=your_secret_key                # Flask密钥
```

### 错误代码说明

#### HTTP状态码
- **200**: 请求成功
- **201**: 创建成功
- **400**: 请求参数错误
- **401**: 未授权访问
- **403**: 权限不足
- **404**: 资源不存在
- **500**: 服务器内部错误

#### 业务错误码
- **1001**: 用户不存在
- **1002**: 密码错误
- **2001**: 飞书集成配置错误
- **2002**: GitHub集成配置错误
- **3001**: MCP协调器连接失败
- **3002**: 工具执行失败

---

**SmartUI智慧用户界面系统 - 让智能管理触手可及** 🚀

*文档版本: v1.0*  
*最后更新: 2025年6月15日*  
*维护团队: PowerAutomation开发团队*

