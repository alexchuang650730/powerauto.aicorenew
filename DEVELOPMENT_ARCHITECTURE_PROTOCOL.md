# PowerAutomation 开发架构协议
## 🚨 所有开发者必读 - 项目开始前强制确认

### 📋 架构纪律 - 零容忍政策

#### 🚫 严格禁止事项 (违反将导致代码被拒绝)

**1. 目录结构违规**
```
❌ 禁止: 创建新的顶级目录
❌ 禁止: 破坏现有目录结构  
❌ 禁止: 偏离 shared_core/ 标准架构

✅ 必须: 使用既定目录结构
shared_core/
├── api/           # API接口层
├── architecture/  # 架构设计层
├── config/        # 配置管理层
├── engines/       # 引擎层
├── mcptool/       # MCP工具层
├── server/        # 服务器层
└── utils/         # 工具函数层
```

**2. MCP通信违规**
```python
❌ 禁止: 直接MCP导入
from qwen3_8b_mcp import QwenModel

❌ 禁止: 直接MCP调用  
qwen_model.process(data)

❌ 禁止: 绕过中央协调器
direct_call_to_mcp()

✅ 必须: 通过中央协调器
qwen_model = coordinator.get_mcp('qwen3_8b_mcp')
result = coordinator.route_to_mcp('qwen3_8b_mcp', data)
```

**3. 工具注册违规**
```python
❌ 禁止: 使用未注册工具
self.unknown_tool.execute()

✅ 必须: 先注册到工具表
self.tools_registry['tool_name'] = {
    "name": "工具名称",
    "description": "工具描述", 
    "category": "工具分类",
    "handler": self._tool_handler
}
```

#### ✅ 强制要求事项

**1. 标准MCP架构**
- 所有MCP必须放在 `shared_core/mcptool/adapters/` 下
- 文件命名必须使用 `*_mcp.py` 后缀
- 每个MCP必须有独立的CLI接口
- 遵循PowerAutomation工具表注册模式

**2. 中央协调模式**
- 所有MCP通信必须通过MCPCoordinator
- 使用标准路由接口: `coordinator.route_to_mcp()`
- 禁止任何形式的直接MCP调用

**3. 开发智能介入系统**
- 实时架构合规检查已启用
- 违规行为将被自动检测
- 不合规代码将被阻止提交
- 自动修复建议将被提供

### 🛡️ 自动化执行机制

**Pre-commit Hook**
```bash
# 每次提交前自动执行
- 架构合规性扫描
- MCP通信规范检查  
- 工具注册验证
- 违规行为阻止
```

**实时监控**
```bash
# 开发过程中持续监控
- 5秒间隔代码扫描
- 即时违规提醒
- 自动修复建议
- IDE集成警告
```

**CI/CD门禁**
```bash
# 构建部署时强制验证
- 100%架构合规率要求
- 零违规容忍政策
- 自动化测试验证
- 部署前最终检查
```

### 📝 开发者确认清单

在开始编码前，每位开发者必须确认:

- [ ] 我已完全理解PowerAutomation架构协议
- [ ] 我承诺不会随意创建目录或文件
- [ ] 我承诺所有MCP通信通过中央协调器
- [ ] 我承诺遵循工具表注册机制
- [ ] 我理解违规代码将被自动拒绝
- [ ] 我同意接受实时架构监控

**签名确认**: _________________ 日期: _________

### 🚨 违规处理流程

**轻微违规 (LOW/MEDIUM)**
1. 自动检测并提醒
2. 提供修复建议
3. 允许开发者手动修复

**严重违规 (HIGH/CRITICAL)**  
1. 立即阻止代码提交
2. 自动应用修复 (如可能)
3. 要求开发者确认修复

**重复违规**
1. 代码审查强制介入
2. 架构培训要求
3. 项目权限限制

### 📞 支持联系

**架构问题**: PowerAutomation架构团队
**技术支持**: 开发智能介入系统
**紧急情况**: 立即联系项目负责人

---
**本协议自项目开始即生效，所有开发者必须严格遵循**
**违反架构协议将导致代码被拒绝，严重情况下将影响项目参与资格**

