#!/usr/bin/env python3
"""
通用智能体自动化设计工作流

此模块实现了通用智能体的自动化设计工作流，支持智能体的选择、生成和修改功能。
基于教师-学生模型，利用从Manus平台采集的交互数据训练Gemini的分析能力和Claude+Kilo Code的代码生成能力。
"""

import os
import json
import time
import logging
import uuid
from typing import Dict, List, Tuple, Optional, Any, Union

from ..interfaces.adapter_interface import AdapterInterface
from .enhanced_thought_action_recorder import EnhancedThoughtActionRecorder


class AgentDesignWorkflow:
    """
    通用智能体自动化设计工作流类
    
    实现了通用智能体的选择、生成和修改功能，基于教师-学生模型训练数据。
    """
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger("agent_design_workflow")
        
        # 设置日志
        self._setup_logging()
        
        # 初始化组件
        self.thought_action_recorder = None
        self.gemini_adapter = None
        self.claude_adapter = None
        self.kilocode_adapter = None
        
        # 初始化训练数据
        self.training_data = {
            "interaction": [],  # Manus交互数据，用于训练Gemini
            "code": []          # Manus代码生成数据，用于训练Claude和Kilo Code
        }
        
        # 初始化组件
        self._initialize_components()
    
    def _load_config(self, config_path):
        """加载配置文件"""
        default_config = {
            "log_level": "INFO",
            "recorder_config_path": None,
            "gemini_adapter_config": {
                "api_key": None,
                "model": "gemini-pro"
            },
            "claude_adapter_config": {
                "api_key": "${CLAUDE_API_KEY}",  # 使用环境变量，请在运行前设置
                "model": "claude-3-opus-20240229"
            },
            "kilocode_adapter_config": {
                "api_endpoint": "https://api.kilocode.ai/v1",
                "api_key": None
            },
            "training_data_path": "./training_data",
            "agent_templates_path": "./agent_templates",
            "output_path": "./generated_agents"
        }
        
        if not config_path:
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # 合并配置
            for key, value in user_config.items():
                if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
                    default_config[key].update(value)
                else:
                    default_config[key] = value
            
            return default_config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}，使用默认配置")
            return default_config
    
    def _setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            # 初始化ThoughtActionRecorder
            from .enhanced_thought_action_recorder import EnhancedThoughtActionRecorder
            self.thought_action_recorder = EnhancedThoughtActionRecorder(
                config_path=self.config.get("recorder_config_path")
            )
            self.logger.info("已初始化ThoughtActionRecorder")
            
            # 初始化Gemini适配器
            try:
                from ..kilocode.gemini_adapter import GeminiAdapter
                self.gemini_adapter = GeminiAdapter(
                    api_key=self.config.get("gemini_adapter_config", {}).get("api_key"),
                    model=self.config.get("gemini_adapter_config", {}).get("model", "gemini-pro")
                )
                self.logger.info("已初始化Gemini适配器")
            except Exception as e:
                self.logger.error(f"初始化Gemini适配器失败: {str(e)}")
            
            # 初始化Claude适配器
            try:
                from ..claude.claude_adapter import ClaudeAdapter
                self.claude_adapter = ClaudeAdapter(
                    api_key=self.config.get("claude_adapter_config", {}).get("api_key"),
                    model=self.config.get("claude_adapter_config", {}).get("model", "claude-3-opus-20240229")
                )
                self.logger.info("已初始化Claude适配器")
            except Exception as e:
                self.logger.error(f"初始化Claude适配器失败: {str(e)}")
            
            # 初始化Kilo Code适配器
            try:
                from ..kilocode.kilocode_adapter import KiloCodeAdapter
                self.kilocode_adapter = KiloCodeAdapter(
                    api_endpoint=self.config.get("kilocode_adapter_config", {}).get("api_endpoint"),
                    api_key=self.config.get("kilocode_adapter_config", {}).get("api_key")
                )
                self.logger.info("已初始化Kilo Code适配器")
            except Exception as e:
                self.logger.error(f"初始化Kilo Code适配器失败: {str(e)}")
            
            return True
        except Exception as e:
            self.logger.error(f"初始化组件失败: {str(e)}")
            return False
    
    def load_training_data(self, data_path=None):
        """加载训练数据"""
        if not data_path:
            data_path = self.config.get("training_data_path")
        
        if not os.path.exists(data_path):
            self.logger.warning(f"训练数据路径不存在: {data_path}")
            return False
        
        try:
            # 加载交互数据
            interaction_path = os.path.join(data_path, "interaction")
            if os.path.exists(interaction_path):
                for filename in os.listdir(interaction_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(interaction_path, filename)
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            self.training_data["interaction"].extend(data)
            
            # 加载代码数据
            code_path = os.path.join(data_path, "code")
            if os.path.exists(code_path):
                for filename in os.listdir(code_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(code_path, filename)
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            self.training_data["code"].extend(data)
            
            self.logger.info(f"已加载 {len(self.training_data['interaction'])} 条交互数据和 {len(self.training_data['code'])} 条代码数据")
            return True
        except Exception as e:
            self.logger.error(f"加载训练数据失败: {str(e)}")
            return False
    
    def collect_training_data(self, manus_url=None, duration=300, interval=2.0):
        """从Manus平台收集训练数据"""
        if not self.thought_action_recorder:
            self.logger.error("ThoughtActionRecorder未初始化，无法收集训练数据")
            return False
        
        try:
            # 连接到Manus平台
            if not self.thought_action_recorder.connect(url=manus_url):
                self.logger.error("连接Manus平台失败")
                return False
            
            # 开始记录
            self.logger.info(f"开始收集训练数据，持续时间: {duration}秒，间隔: {interval}秒")
            self.thought_action_recorder.start_recording(duration=duration, interval=interval)
            
            # 获取记录的数据
            captured_data = self.thought_action_recorder.captured_data
            
            # 处理数据，分离交互数据和代码数据
            for record in captured_data:
                # 提取交互数据
                interaction_data = {
                    "timestamp": record.get("timestamp"),
                    "datetime": record.get("datetime"),
                    "work_area": record.get("work_area"),
                    "operation_area": record.get("operation_area"),
                    "thoughts": record.get("thoughts"),
                    "actions": record.get("actions"),
                    "steps": record.get("steps")
                }
                self.training_data["interaction"].append(interaction_data)
                
                # 提取代码数据
                code_text = record.get("operation_area", {}).get("text", "")
                if "```" in code_text:
                    import re
                    code_blocks = re.findall(r"```(?:\w+)?\s*(.*?)\s*```", code_text, re.DOTALL)
                    for code in code_blocks:
                        code_data = {
                            "timestamp": record.get("timestamp"),
                            "datetime": record.get("datetime"),
                            "code": code,
                            "language": self._detect_language(code)
                        }
                        self.training_data["code"].append(code_data)
            
            # 保存训练数据
            self._save_training_data()
            
            self.logger.info(f"已收集 {len(self.training_data['interaction'])} 条交互数据和 {len(self.training_data['code'])} 条代码数据")
            return True
        except Exception as e:
            self.logger.error(f"收集训练数据失败: {str(e)}")
            return False
        finally:
            # 断开连接
            if self.thought_action_recorder:
                self.thought_action_recorder.disconnect()
    
    def _detect_language(self, code):
        """检测代码语言"""
        # 简单的语言检测逻辑
        if "def " in code and ":" in code:
            return "python"
        elif "function " in code and "{" in code:
            return "javascript"
        elif "public class " in code:
            return "java"
        elif "#include" in code:
            return "c++"
        else:
            return "unknown"
    
    def _save_training_data(self):
        """保存训练数据"""
        try:
            data_path = self.config.get("training_data_path")
            os.makedirs(data_path, exist_ok=True)
            
            # 保存交互数据
            interaction_path = os.path.join(data_path, "interaction")
            os.makedirs(interaction_path, exist_ok=True)
            interaction_file = os.path.join(interaction_path, f"interaction_data_{int(time.time())}.json")
            with open(interaction_file, 'w') as f:
                json.dump(self.training_data["interaction"], f, indent=2)
            
            # 保存代码数据
            code_path = os.path.join(data_path, "code")
            os.makedirs(code_path, exist_ok=True)
            code_file = os.path.join(code_path, f"code_data_{int(time.time())}.json")
            with open(code_file, 'w') as f:
                json.dump(self.training_data["code"], f, indent=2)
            
            self.logger.info(f"已保存训练数据到 {data_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存训练数据失败: {str(e)}")
            return False
    
    def train_models(self):
        """训练模型（教师-学生模型）"""
        if not self.training_data["interaction"] and not self.training_data["code"]:
            self.logger.error("没有训练数据，无法训练模型")
            return False
        
        try:
            # 训练Gemini（学习Manus的交互分析能力）
            if self.gemini_adapter and self.training_data["interaction"]:
                self.logger.info("开始训练Gemini模型")
                # 实际训练代码将根据Gemini API的具体实现而定
                # 这里仅作为示例
                success = self._train_gemini()
                if success:
                    self.logger.info("Gemini模型训练成功")
                else:
                    self.logger.error("Gemini模型训练失败")
            
            # 训练Claude（学习Manus的代码生成能力）
            if self.claude_adapter and self.training_data["code"]:
                self.logger.info("开始训练Claude模型")
                # 实际训练代码将根据Claude API的具体实现而定
                # 这里仅作为示例
                success = self._train_claude()
                if success:
                    self.logger.info("Claude模型训练成功")
                else:
                    self.logger.error("Claude模型训练失败")
            
            # 训练Kilo Code（学习Manus的代码生成能力）
            if self.kilocode_adapter and self.training_data["code"]:
                self.logger.info("开始训练Kilo Code模型")
                # 实际训练代码将根据Kilo Code API的具体实现而定
                # 这里仅作为示例
                success = self._train_kilocode()
                if success:
                    self.logger.info("Kilo Code模型训练成功")
                else:
                    self.logger.error("Kilo Code模型训练失败")
            
            return True
        except Exception as e:
            self.logger.error(f"训练模型失败: {str(e)}")
            return False
    
    def _train_gemini(self):
        """训练Gemini模型"""
        # 实际训练代码将根据Gemini API的具体实现而定
        # 这里仅作为示例
        try:
            # 准备训练数据
            training_examples = []
            for interaction in self.training_data["interaction"]:
                # 提取输入和输出
                input_text = interaction.get("work_area", {}).get("text", "")
                output_text = ""
                for thought in interaction.get("thoughts", []):
                    output_text += f"<thought>{thought}</thought>\n"
                for action in interaction.get("actions", []):
                    output_text += f"<action>{action}</action>\n"
                for step in interaction.get("steps", []):
                    step_num = step.get("step_number", 0)
                    step_desc = step.get("description", "")
                    output_text += f"Step {step_num}: {step_desc}\n"
                
                if input_text and output_text:
                    training_examples.append({
                        "input": input_text,
                        "output": output_text
                    })
            
            # 调用Gemini API进行训练
            # 注意：实际的Gemini API可能不支持直接训练，这里仅作为示例
            if self.gemini_adapter and hasattr(self.gemini_adapter, "train"):
                self.gemini_adapter.train(training_examples)
                return True
            else:
                self.logger.warning("Gemini适配器不支持训练，跳过")
                return False
        except Exception as e:
            self.logger.error(f"训练Gemini模型失败: {str(e)}")
            return False
    
    def _train_claude(self):
        """训练Claude模型"""
        # 实际训练代码将根据Claude API的具体实现而定
        # 这里仅作为示例
        try:
            # 准备训练数据
            training_examples = []
            for code_data in self.training_data["code"]:
                # 提取输入和输出
                # 假设每个代码示例前有一个注释描述了任务
                code = code_data.get("code", "")
                language = code_data.get("language", "unknown")
                
                # 尝试提取任务描述
                task_description = ""
                lines = code.split("\n")
                for line in lines[:5]:  # 只检查前5行
                    if line.startswith("#") or line.startswith("//") or line.startswith("/*"):
                        task_description += line + "\n"
                
                if task_description and code:
                    training_examples.append({
                        "input": task_description,
                        "output": code,
                        "language": language
                    })
            
            # 调用Claude API进行训练
            # 注意：实际的Claude API可能不支持直接训练，这里仅作为示例
            if self.claude_adapter and hasattr(self.claude_adapter, "train"):
                self.claude_adapter.train(training_examples)
                return True
            else:
                self.logger.warning("Claude适配器不支持训练，跳过")
                return False
        except Exception as e:
            self.logger.error(f"训练Claude模型失败: {str(e)}")
            return False
    
    def _train_kilocode(self):
        """训练Kilo Code模型"""
        # 实际训练代码将根据Kilo Code API的具体实现而定
        # 这里仅作为示例
        try:
            # 准备训练数据
            training_examples = []
            for code_data in self.training_data["code"]:
                # 提取输入和输出
                # 假设每个代码示例前有一个注释描述了任务
                code = code_data.get("code", "")
                language = code_data.get("language", "unknown")
                
                # 尝试提取任务描述
                task_description = ""
                lines = code.split("\n")
                for line in lines[:5]:  # 只检查前5行
                    if line.startswith("#") or line.startswith("//") or line.startswith("/*"):
                        task_description += line + "\n"
                
                if task_description and code:
                    training_examples.append({
                        "input": task_description,
                        "output": code,
                        "language": language
                    })
            
            # 调用Kilo Code API进行训练
            # 注意：实际的Kilo Code API可能不支持直接训练，这里仅作为示例
            if self.kilocode_adapter and hasattr(self.kilocode_adapter, "train"):
                self.kilocode_adapter.train(training_examples)
                return True
            else:
                self.logger.warning("Kilo Code适配器不支持训练，跳过")
                return False
        except Exception as e:
            self.logger.error(f"训练Kilo Code模型失败: {str(e)}")
            return False
    
    def select_agent(self, requirements):
        """选择智能体"""
        if not self.gemini_adapter:
            self.logger.error("Gemini适配器未初始化，无法选择智能体")
            return None
        
        try:
            # 使用Gemini分析需求
            analysis_prompt = f"""
            分析以下智能体需求，并选择最合适的智能体类型：

            需求：
            {requirements}

            可选的智能体类型：
            1. 代码生成智能体 - 擅长生成和优化代码
            2. 数据分析智能体 - 擅长处理和分析数据
            3. 文本处理智能体 - 擅长处理和生成文本内容
            4. 对话智能体 - 擅长进行自然语言对话
            5. 多模态智能体 - 能够处理文本、图像等多种模态

            请分析需求并选择最合适的智能体类型，给出选择理由。
            """
            
            analysis_result = self.gemini_adapter.generate_text(analysis_prompt)
            
            # 解析分析结果
            agent_type = self._parse_agent_type(analysis_result)
            
            self.logger.info(f"已选择智能体类型: {agent_type}")
            return {
                "agent_type": agent_type,
                "analysis": analysis_result
            }
        except Exception as e:
            self.logger.error(f"选择智能体失败: {str(e)}")
            return None
    
    def _parse_agent_type(self, analysis_result):
        """解析分析结果，提取智能体类型"""
        # 简单的解析逻辑
        if "代码生成智能体" in analysis_result or "代码生成" in analysis_result:
            return "code_generation"
        elif "数据分析智能体" in analysis_result or "数据分析" in analysis_result:
            return "data_analysis"
        elif "文本处理智能体" in analysis_result or "文本处理" in analysis_result:
            return "text_processing"
        elif "对话智能体" in analysis_result or "对话" in analysis_result:
            return "conversation"
        elif "多模态智能体" in analysis_result or "多模态" in analysis_result:
            return "multimodal"
        else:
            return "general"
    
    def generate_agent(self, requirements, agent_type=None):
        """生成智能体"""
        if not self.gemini_adapter or not self.claude_adapter:
            self.logger.error("Gemini或Claude适配器未初始化，无法生成智能体")
            return None
        
        try:
            # 如果未指定智能体类型，先选择一个
            if not agent_type:
                selection_result = self.select_agent(requirements)
                if selection_result:
                    agent_type = selection_result.get("agent_type")
                else:
                    agent_type = "general"
            
            # 使用Gemini分析需求，生成智能体设计
            design_prompt = f"""
            基于以下需求，设计一个{agent_type}智能体：

            需求：
            {requirements}

            请提供以下内容：
            1. 智能体名称
            2. 智能体描述
            3. 核心功能列表
            4. 输入输出格式
            5. 主要组件和工作流程
            6. 与其他系统的集成点
            """
            
            design_result = self.gemini_adapter.generate_text(design_prompt)
            
            # 使用Claude生成智能体代码
            code_prompt = f"""
            基于以下智能体设计，生成实现代码：

            智能体设计：
            {design_result}

            需求：
            {requirements}

            请生成完整的Python代码实现，包括：
            1. 类定义
            2. 初始化方法
            3. 核心功能实现
            4. 辅助方法
            5. 示例用法
            
            代码应当遵循PEP 8规范，包含详细的文档字符串和注释。
            """
            
            code_result = self.claude_adapter.generate_text(code_prompt)
            
            # 提取代码
            import re
            code_blocks = re.findall(r"```(?:python)?\s*(.*?)\s*```", code_result, re.DOTALL)
            code = "\n\n".join(code_blocks) if code_blocks else code_result
            
            # 解析智能体名称
            agent_name = self._parse_agent_name(design_result)
            
            # 保存智能体
            agent_id = str(uuid.uuid4())[:8]
            agent_data = {
                "id": agent_id,
                "name": agent_name,
                "type": agent_type,
                "requirements": requirements,
                "design": design_result,
                "code": code,
                "created_at": time.time()
            }
            
            self._save_agent(agent_data)
            
            self.logger.info(f"已生成智能体: {agent_name} (ID: {agent_id})")
            return agent_data
        except Exception as e:
            self.logger.error(f"生成智能体失败: {str(e)}")
            return None
    
    def _parse_agent_name(self, design_result):
        """解析设计结果，提取智能体名称"""
        # 简单的解析逻辑
        lines = design_result.split("\n")
        for line in lines[:10]:  # 只检查前10行
            if "名称" in line or "name" in line.lower():
                parts = line.split("：" if "：" in line else ":")
                if len(parts) > 1:
                    return parts[1].strip()
        
        # 如果没有找到名称，返回默认名称
        return f"Agent_{int(time.time())}"
    
    def _save_agent(self, agent_data):
        """保存智能体"""
        try:
            output_path = self.config.get("output_path")
            os.makedirs(output_path, exist_ok=True)
            
            # 保存智能体元数据
            agent_id = agent_data.get("id")
            agent_dir = os.path.join(output_path, f"agent_{agent_id}")
            os.makedirs(agent_dir, exist_ok=True)
            
            # 保存元数据
            metadata_file = os.path.join(agent_dir, "metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump({
                    "id": agent_data.get("id"),
                    "name": agent_data.get("name"),
                    "type": agent_data.get("type"),
                    "requirements": agent_data.get("requirements"),
                    "created_at": agent_data.get("created_at")
                }, f, indent=2)
            
            # 保存设计文档
            design_file = os.path.join(agent_dir, "design.md")
            with open(design_file, 'w') as f:
                f.write(f"# {agent_data.get('name')}\n\n")
                f.write(agent_data.get("design", ""))
            
            # 保存代码
            code_file = os.path.join(agent_dir, f"{agent_data.get('id')}.py")
            with open(code_file, 'w') as f:
                f.write(agent_data.get("code", ""))
            
            self.logger.info(f"已保存智能体到 {agent_dir}")
            return True
        except Exception as e:
            self.logger.error(f"保存智能体失败: {str(e)}")
            return False
    
    def modify_agent(self, agent_id, modifications):
        """修改智能体"""
        if not self.gemini_adapter or not self.claude_adapter:
            self.logger.error("Gemini或Claude适配器未初始化，无法修改智能体")
            return None
        
        try:
            # 加载智能体
            agent_data = self._load_agent(agent_id)
            if not agent_data:
                self.logger.error(f"未找到智能体: {agent_id}")
                return None
            
            # 使用Gemini分析修改需求
            analysis_prompt = f"""
            分析以下智能体修改需求：

            原始智能体设计：
            {agent_data.get('design', '')}

            原始代码：
            {agent_data.get('code', '')}

            修改需求：
            {modifications}

            请提供以下内容：
            1. 需要修改的部分
            2. 修改的理由
            3. 修改后的设计变化
            """
            
            analysis_result = self.gemini_adapter.generate_text(analysis_prompt)
            
            # 使用Claude修改智能体代码
            code_prompt = f"""
            基于以下分析，修改智能体代码：

            原始代码：
            ```python
            {agent_data.get('code', '')}
            ```

            修改分析：
            {analysis_result}

            修改需求：
            {modifications}

            请生成完整的修改后的Python代码，包括：
            1. 所有原始功能
            2. 根据修改需求新增或修改的功能
            3. 更新的文档字符串和注释
            
            代码应当遵循PEP 8规范，包含详细的文档字符串和注释。
            """
            
            code_result = self.claude_adapter.generate_text(code_prompt)
            
            # 提取代码
            import re
            code_blocks = re.findall(r"```(?:python)?\s*(.*?)\s*```", code_result, re.DOTALL)
            code = "\n\n".join(code_blocks) if code_blocks else code_result
            
            # 更新智能体设计
            design_prompt = f"""
            基于以下分析，更新智能体设计文档：

            原始设计：
            {agent_data.get('design', '')}

            修改分析：
            {analysis_result}

            修改需求：
            {modifications}

            请提供更新后的完整设计文档。
            """
            
            design_result = self.gemini_adapter.generate_text(design_prompt)
            
            # 保存修改后的智能体
            modified_agent_data = {
                "id": agent_data.get("id"),
                "name": agent_data.get("name"),
                "type": agent_data.get("type"),
                "requirements": agent_data.get("requirements"),
                "modifications": modifications,
                "design": design_result,
                "code": code,
                "created_at": agent_data.get("created_at"),
                "modified_at": time.time()
            }
            
            self._save_agent(modified_agent_data)
            
            self.logger.info(f"已修改智能体: {agent_data.get('name')} (ID: {agent_id})")
            return modified_agent_data
        except Exception as e:
            self.logger.error(f"修改智能体失败: {str(e)}")
            return None
    
    def _load_agent(self, agent_id):
        """加载智能体"""
        try:
            output_path = self.config.get("output_path")
            agent_dir = os.path.join(output_path, f"agent_{agent_id}")
            
            if not os.path.exists(agent_dir):
                self.logger.error(f"智能体目录不存在: {agent_dir}")
                return None
            
            # 加载元数据
            metadata_file = os.path.join(agent_dir, "metadata.json")
            if not os.path.exists(metadata_file):
                self.logger.error(f"智能体元数据文件不存在: {metadata_file}")
                return None
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # 加载设计文档
            design_file = os.path.join(agent_dir, "design.md")
            design = ""
            if os.path.exists(design_file):
                with open(design_file, 'r') as f:
                    design = f.read()
            
            # 加载代码
            code_file = os.path.join(agent_dir, f"{agent_id}.py")
            code = ""
            if os.path.exists(code_file):
                with open(code_file, 'r') as f:
                    code = f.read()
            
            agent_data = {
                "id": metadata.get("id"),
                "name": metadata.get("name"),
                "type": metadata.get("type"),
                "requirements": metadata.get("requirements"),
                "design": design,
                "code": code,
                "created_at": metadata.get("created_at")
            }
            
            return agent_data
        except Exception as e:
            self.logger.error(f"加载智能体失败: {str(e)}")
            return None
    
    def list_agents(self):
        """列出所有智能体"""
        try:
            output_path = self.config.get("output_path")
            if not os.path.exists(output_path):
                self.logger.warning(f"输出路径不存在: {output_path}")
                return []
            
            agents = []
            for dirname in os.listdir(output_path):
                if dirname.startswith("agent_"):
                    agent_id = dirname[6:]  # 去掉"agent_"前缀
                    agent_dir = os.path.join(output_path, dirname)
                    
                    # 加载元数据
                    metadata_file = os.path.join(agent_dir, "metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        agents.append({
                            "id": metadata.get("id"),
                            "name": metadata.get("name"),
                            "type": metadata.get("type"),
                            "created_at": metadata.get("created_at"),
                            "modified_at": metadata.get("modified_at", metadata.get("created_at"))
                        })
            
            return sorted(agents, key=lambda x: x.get("modified_at", 0), reverse=True)
        except Exception as e:
            self.logger.error(f"列出智能体失败: {str(e)}")
            return []
    
    def get_agent(self, agent_id):
        """获取智能体详情"""
        return self._load_agent(agent_id)
    
    def delete_agent(self, agent_id):
        """删除智能体"""
        try:
            output_path = self.config.get("output_path")
            agent_dir = os.path.join(output_path, f"agent_{agent_id}")
            
            if not os.path.exists(agent_dir):
                self.logger.error(f"智能体目录不存在: {agent_dir}")
                return False
            
            import shutil
            shutil.rmtree(agent_dir)
            
            self.logger.info(f"已删除智能体: {agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"删除智能体失败: {str(e)}")
            return False


# 如果直接运行此脚本，执行简单的测试
if __name__ == "__main__":
    workflow = AgentDesignWorkflow()
    
    # 加载训练数据
    workflow.load_training_data()
    
    # 生成一个简单的智能体
    agent = workflow.generate_agent("创建一个能够分析CSV文件并生成数据可视化的智能体")
    
    if agent:
        print(f"已生成智能体: {agent.get('name')} (ID: {agent.get('id')})")
        
        # 列出所有智能体
        agents = workflow.list_agents()
        print(f"智能体列表: {agents}")
