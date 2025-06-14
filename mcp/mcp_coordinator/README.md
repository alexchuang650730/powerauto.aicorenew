# MCP Coordinator - 阶段性交付文档

## 概述

`mcp_coordinator.py` 是 PowerAutomation 智能介入系统的核心协调器，实现了"答案自己打"的核心理念。

## 核心特性

### 1. 智能介入流程
- **输入处理**：处理来自前端的输入和环境反馈
- **AI分析**：并行调用多个AI MCPs进行内容分析
- **策略决策**：基于RL/SRT学习系统的智能决策
- **工具选择**：动态选择最适合的执行工具
- **介入执行**：协调各种MCP执行具体任务

### 2. "答案自己打"测试系统
- **自生成测试用例**：基于AI分析和决策自动生成测试脚本
- **视频录制执行**：使用Playwright MCP执行并录制操作视频
- **视频智能分析**：分析执行视频，提取关键信息
- **补充用例生成**：基于视频分析结果生成额外测试用例
- **学习反馈闭环**：将所有结果反馈给RL/SRT系统进行学习

### 3. 模块化架构
- **MCPInterface**：统一的MCP接口基类
- **SafeMCPRegistry**：安全的MCP注册表
- **核心模块**：InputFeedbackProcessor, ContextManager, AIAnalysisOrchestrator, PolicyDecider, ToolSelector, TestCaseManager, InterventionExecutor

## 使用方法

### 基本命令

```bash
# 检查状态
python mcp_coordinator.py get_status

# 处理输入（完整智能介入流程）
python mcp_coordinator.py process_input --data '{"type": "user_message", "content": "hello world", "session_id": "test_session"}'

# 直接运行测试用例流程
python mcp_coordinator.py run_test_case_flow --data '{"context": {"test": true}, "ai_analysis": {}, "decision": {"should_generate_test_case": true}}'
```

### 数据格式示例

#### process_input 数据格式
```json
{
  "type": "user_message",
  "content": "用户输入的内容",
  "session_id": "会话ID",
  "ui_changes": ["UI变化列表"],
  "dialog_behavior": {"对话行为": "数据"}
}
```

## 占位符MCPs

当前版本包含以下占位符MCPs，用于测试和验证：
- PlaceholderGeminiMCP
- PlaceholderClaudeMCP  
- PlaceholderSuperMemoryMCP
- PlaceholderRLSRTMCP
- PlaceholderSearchMCP
- PlaceholderKiloCodeMCP
- PlaceholderPlaywrightMCP
- PlaceholderTestCaseGeneratorMCP
- PlaceholderVideoAnalysisMCP

## 集成指南

### 替换占位符MCPs
1. 将您现有的真实MCPs注册到 `SafeMCPRegistry`
2. 确保真实MCPs实现了相应的接口方法
3. 移除或替换占位符MCPs

### 扩展功能
1. 继承 `MCPInterface` 创建新的MCP
2. 在 `MCPCoordinator.initialize()` 中添加新模块
3. 在相应的流程中调用新模块

## 技术特点

### 扩展性
- 模块化设计，易于添加新的MCP和功能
- 统一的接口规范，支持热插拔
- 灵活的注册表机制

### 约束力
- 严格的错误处理和日志记录
- 明确的接口契约和数据格式
- 完整的异常处理机制

### 自进化能力
- 基于RL/SRT的学习反馈机制
- 自生成测试用例的质量提升
- 环境反馈驱动的策略优化

## 下一步计划

1. **真实MCP集成**：将占位符替换为您的真实MCPs
2. **打包部署**：将代码打包为 .exe/.dmg 可执行文件
3. **实际测试**：在Mac/Windows环境中进行真实测试
4. **反馈优化**：基于测试结果优化算法和流程

## 文件结构

```
powerauto.aicorenew/
└── mcp/
    └── mcp_coordinator/
        ├── mcp_coordinator.py  # 主要实现文件
        └── README.md          # 本文档
```

---

**这是 PowerAutomation 智能介入系统的第一个阶段性交付，准备上传到 powerauto.aicorenew 仓库。**

