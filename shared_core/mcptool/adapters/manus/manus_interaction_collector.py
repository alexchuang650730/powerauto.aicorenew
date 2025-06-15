#!/usr/bin/env python3
"""
Manus交互数据收集器

此模块实现了基于Manus的ThoughtActionRecorder的交互数据收集功能，
用于抓取Manus的交互分析数据，作为教师-学生模型训练的数据来源。
"""

import re
import time
import json
import logging
import requests
from datetime import datetime


class ManusInteractionCollector:
    """
    用于收集Manus交互数据的组件，参考ThoughtActionRecorder实现
    """
    def __init__(self, manus_endpoint="https://manus.im/app/nptXUzLrh5iY8da4BoBnt9", config_path=None):
        self.manus_endpoint = manus_endpoint
        self.session = requests.Session()
        self.interaction_data = []
        self.logger = logging.getLogger("manus_collector")
        self.config = self._load_config(config_path)
        
        # 设置日志
        self._setup_logging()
    
    def _load_config(self, config_path):
        """加载配置文件"""
        if not config_path:
            return {
                "log_level": "INFO",
                "max_retries": 3,
                "timeout": 30,
                "batch_size": 10
            }
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}，使用默认配置")
            return {
                "log_level": "INFO",
                "max_retries": 3,
                "timeout": 30,
                "batch_size": 10
            }
    
    def _setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def connect(self):
        """建立与Manus的连接"""
        try:
            response = self.session.get(
                f"{self.manus_endpoint}/status",
                timeout=self.config.get("timeout", 30)
            )
            if response.status_code == 200:
                self.logger.info("成功连接到Manus服务")
                return True
            else:
                self.logger.error(f"连接Manus失败: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"连接异常: {str(e)}")
            return False
    
    def record_interaction(self, interaction_type, user_input, manus_response):
        """记录交互数据"""
        interaction = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "type": interaction_type,
            "user_input": user_input,
            "manus_response": manus_response,
            "thought_process": self._extract_thought_process(manus_response),
            "actions": self._extract_actions(manus_response)
        }
        self.interaction_data.append(interaction)
        
        # 如果达到批处理大小，自动保存
        if len(self.interaction_data) >= self.config.get("batch_size", 10):
            self._auto_save()
            
        return interaction
    
    def _extract_thought_process(self, response):
        """从Manus响应中提取思考过程"""
        # 参考ThoughtActionRecorder的实现
        if isinstance(response, dict):
            response = json.dumps(response)
        elif not isinstance(response, str):
            response = str(response)
            
        thought_pattern = r"<thought>(.*?)</thought>"
        thoughts = re.findall(thought_pattern, response, re.DOTALL)
        return thoughts if thoughts else []
    
    def _extract_actions(self, response):
        """从Manus响应中提取行动"""
        if isinstance(response, dict):
            response = json.dumps(response)
        elif not isinstance(response, str):
            response = str(response)
            
        action_pattern = r"<action>(.*?)</action>"
        actions = re.findall(action_pattern, response, re.DOTALL)
        return actions if actions else []
    
    def _auto_save(self):
        """自动保存收集的数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"manus_interactions_{timestamp}.json"
        self.export_data(filename)
        self.interaction_data = []  # 清空已保存的数据
    
    def send_command_to_manus(self, command):
        """发送指令给Manus的agentProblemSolver"""
        max_retries = self.config.get("max_retries", 3)
        timeout = self.config.get("timeout", 30)
        
        for attempt in range(max_retries):
            try:
                payload = {"command": command}
                response = self.session.post(
                    f"{self.manus_endpoint}/api/agent/problem-solver",
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # 记录交互
                    self.record_interaction("command", command, result)
                    return result
                else:
                    self.logger.warning(f"发送指令失败 (尝试 {attempt+1}/{max_retries}): {response.status_code}")
                    if attempt == max_retries - 1:
                        self.logger.error(f"发送指令最终失败: {response.status_code}")
                        return None
            except Exception as e:
                self.logger.warning(f"发送指令异常 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    self.logger.error(f"发送指令最终异常: {str(e)}")
                    return None
            
            # 重试前等待
            time.sleep(1)
    
    def export_data(self, output_file):
        """导出收集的交互数据"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.interaction_data, f, indent=2)
            self.logger.info(f"交互数据已导出到 {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"导出数据异常: {str(e)}")
            return False
    
    def import_data(self, input_file):
        """导入交互数据"""
        try:
            with open(input_file, 'r') as f:
                imported_data = json.load(f)
            
            # 合并数据
            self.interaction_data.extend(imported_data)
            self.logger.info(f"已从 {input_file} 导入 {len(imported_data)} 条交互数据")
            return True
        except Exception as e:
            self.logger.error(f"导入数据异常: {str(e)}")
            return False
    
    def get_statistics(self):
        """获取交互数据统计信息"""
        if not self.interaction_data:
            return {"total": 0}
        
        stats = {
            "total": len(self.interaction_data),
            "by_type": {},
            "avg_response_length": 0,
            "avg_thought_count": 0,
            "avg_action_count": 0
        }
        
        total_response_length = 0
        total_thought_count = 0
        total_action_count = 0
        
        for interaction in self.interaction_data:
            # 按类型统计
            interaction_type = interaction.get("type", "unknown")
            if interaction_type not in stats["by_type"]:
                stats["by_type"][interaction_type] = 0
            stats["by_type"][interaction_type] += 1
            
            # 计算响应长度
            response = interaction.get("manus_response", "")
            if isinstance(response, dict):
                response = json.dumps(response)
            elif not isinstance(response, str):
                response = str(response)
            total_response_length += len(response)
            
            # 计算思考过程数量
            thoughts = interaction.get("thought_process", [])
            total_thought_count += len(thoughts)
            
            # 计算行动数量
            actions = interaction.get("actions", [])
            total_action_count += len(actions)
        
        # 计算平均值
        stats["avg_response_length"] = total_response_length / stats["total"]
        stats["avg_thought_count"] = total_thought_count / stats["total"]
        stats["avg_action_count"] = total_action_count / stats["total"]
        
        return stats


# 如果直接运行此脚本，执行简单的测试
if __name__ == "__main__":
    collector = ManusInteractionCollector()
    
    # 测试连接
    if collector.connect():
        print("成功连接到Manus服务")
        
        # 测试发送指令
        response = collector.send_command_to_manus("Generate a simple Python function to calculate factorial")
        if response:
            print("成功发送指令并获取响应")
            
            # 导出数据
            collector.export_data("manus_test_interactions.json")
            
            # 获取统计信息
            stats = collector.get_statistics()
            print(f"统计信息: {stats}")
        else:
            print("发送指令失败")
    else:
        print("连接Manus服务失败")
