#!/usr/bin/env python3
"""
Manus交互数据验证器

此模块实现了Manus交互数据的验证和强化功能，
用于确保收集的数据质量和有效性，为教师-学生模型训练提供高质量数据。
"""

import re
import json
import logging
import time
from datetime import datetime


class ManusDataValidator:
    """
    用于强化和验证Manus交互数据的组件
    """
    def __init__(self, config_path=None):
        self.logger = logging.getLogger("manus_validator")
        self.config = self._load_config(config_path)
        
        # 设置日志
        self._setup_logging()
    
    def _load_config(self, config_path):
        """加载配置文件"""
        if not config_path:
            return {
                "log_level": "INFO",
                "min_quality_score": 0.7,
                "min_thought_count": 1,
                "min_action_count": 1
            }
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}，使用默认配置")
            return {
                "log_level": "INFO",
                "min_quality_score": 0.7,
                "min_thought_count": 1,
                "min_action_count": 1
            }
    
    def _setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def validate_dataset(self, dataset_path):
        """验证数据集的完整性和质量"""
        try:
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
            
            valid_count = 0
            invalid_count = 0
            enhanced_dataset = []
            
            for interaction in dataset:
                # 验证必要字段
                if self._validate_interaction(interaction):
                    # 强化数据
                    enhanced = self._enhance_interaction(interaction)
                    enhanced_dataset.append(enhanced)
                    valid_count += 1
                else:
                    invalid_count += 1
                    self.logger.warning(f"无效交互数据: {interaction.get('timestamp', 'unknown')}")
            
            validation_result = {
                "total": len(dataset),
                "valid": valid_count,
                "invalid": invalid_count,
                "validity_rate": valid_count / len(dataset) if dataset else 0
            }
            
            # 导出强化后的数据集
            output_path = dataset_path.replace('.json', '_enhanced.json')
            with open(output_path, 'w') as f:
                json.dump(enhanced_dataset, f, indent=2)
            
            self.logger.info(f"数据验证完成: {validation_result}")
            return validation_result, output_path
            
        except Exception as e:
            self.logger.error(f"数据验证异常: {str(e)}")
            return None, None
    
    def _validate_interaction(self, interaction):
        """验证单个交互数据的有效性"""
        required_fields = ["timestamp", "type", "user_input", "manus_response"]
        
        # 检查必要字段
        for field in required_fields:
            if field not in interaction:
                return False
        
        # 验证响应内容
        if not interaction["manus_response"]:
            return False
        
        # 验证思考过程和行动
        thought_process = interaction.get("thought_process", [])
        actions = interaction.get("actions", [])
        
        if len(thought_process) < self.config.get("min_thought_count", 1):
            return False
        
        if len(actions) < self.config.get("min_action_count", 1):
            return False
        
        # 计算质量分数
        quality_score = self._calculate_quality_score(interaction)
        if quality_score < self.config.get("min_quality_score", 0.7):
            return False
        
        return True
    
    def _calculate_quality_score(self, interaction):
        """计算交互数据的质量分数"""
        # 基础分数
        score = 0.5
        
        # 思考过程加分
        thought_process = interaction.get("thought_process", [])
        if thought_process:
            score += min(0.2, len(thought_process) * 0.05)
        
        # 行动加分
        actions = interaction.get("actions", [])
        if actions:
            score += min(0.2, len(actions) * 0.05)
        
        # 响应长度加分
        response = interaction.get("manus_response", "")
        if isinstance(response, dict):
            response = json.dumps(response)
        elif not isinstance(response, str):
            response = str(response)
        
        response_length = len(response)
        if response_length > 1000:
            score += 0.1
        
        # 区域信息加分
        if "area" in interaction:
            score += 0.1
        
        return min(1.0, score)  # 最高分为1.0
    
    def _enhance_interaction(self, interaction):
        """强化交互数据，添加额外信息"""
        enhanced = interaction.copy()
        
        # 添加分类标签
        enhanced["category"] = self._categorize_interaction(interaction)
        
        # 提取关键步骤
        enhanced["key_steps"] = self._extract_key_steps(interaction)
        
        # 分析复杂度
        enhanced["complexity"] = self._analyze_complexity(interaction)
        
        # 区分工作任务区域和操作区域
        if "area" not in enhanced:
            enhanced["area"] = self._determine_area(interaction)
        
        # 添加时间戳信息
        if "datetime" not in enhanced:
            enhanced["datetime"] = datetime.fromtimestamp(
                interaction.get("timestamp", time.time())
            ).isoformat()
        
        # 添加质量分数
        enhanced["quality_score"] = self._calculate_quality_score(interaction)
        
        return enhanced
    
    def _categorize_interaction(self, interaction):
        """对交互进行分类"""
        # 实现交互分类逻辑
        user_input = interaction.get("user_input", "").lower()
        
        if "generate" in user_input or "create" in user_input or "新建" in user_input or "创建" in user_input:
            return "generation"
        elif "modify" in user_input or "change" in user_input or "修改" in user_input or "更改" in user_input:
            return "modification"
        elif "select" in user_input or "choose" in user_input or "选择" in user_input or "挑选" in user_input:
            return "selection"
        elif "analyze" in user_input or "分析" in user_input:
            return "analysis"
        elif "execute" in user_input or "run" in user_input or "执行" in user_input or "运行" in user_input:
            return "execution"
        else:
            return "other"
    
    def _extract_key_steps(self, interaction):
        """提取交互中的关键步骤"""
        # 实现关键步骤提取逻辑
        response = interaction.get("manus_response", "")
        thought_process = interaction.get("thought_process", [])
        
        key_steps = []
        
        # 从思考过程中提取步骤
        for thought in thought_process:
            step_pattern = r"Step (\d+):(.*?)(?=Step \d+:|$)"
            steps = re.findall(step_pattern, thought, re.DOTALL)
            for num, desc in steps:
                key_steps.append({
                    "step_number": int(num),
                    "description": desc.strip()
                })
        
        # 如果没有找到步骤，尝试其他格式
        if not key_steps:
            step_pattern = r"(\d+)\.(.*?)(?=\d+\.|$)"
            if isinstance(response, dict):
                response = json.dumps(response)
            elif not isinstance(response, str):
                response = str(response)
                
            steps = re.findall(step_pattern, response, re.DOTALL)
            for num, desc in steps:
                key_steps.append({
                    "step_number": int(num),
                    "description": desc.strip()
                })
        
        return key_steps
    
    def _analyze_complexity(self, interaction):
        """分析交互的复杂度"""
        # 实现复杂度分析逻辑
        user_input = interaction.get("user_input", "")
        response = interaction.get("manus_response", "")
        thought_process = interaction.get("thought_process", [])
        
        # 基于输入长度、响应长度和思考过程的复杂度评分
        input_score = len(user_input) / 100  # 每100字符1分
        
        if isinstance(response, dict):
            response = json.dumps(response)
        elif not isinstance(response, str):
            response = str(response)
            
        response_score = len(response) / 500  # 每500字符1分
        thought_score = len(thought_process) * 2  # 每个思考过程2分
        
        total_score = input_score + response_score + thought_score
        
        # 复杂度分级
        if total_score < 5:
            return "simple"
        elif total_score < 15:
            return "moderate"
        else:
            return "complex"
    
    def _determine_area(self, interaction):
        """确定交互属于工作任务区域还是操作区域"""
        # 实现区域判断逻辑
        user_input = interaction.get("user_input", "").lower()
        response = interaction.get("manus_response", "")
        
        if isinstance(response, dict):
            response = json.dumps(response)
        elif not isinstance(response, str):
            response = str(response)
        
        # 工作任务区域关键词
        task_keywords = ["task", "project", "任务", "项目", "工作", "计划", "进度", "状态"]
        
        # 操作区域关键词
        operation_keywords = ["execute", "run", "操作", "执行", "运行", "生成", "修改", "选择", "分析"]
        
        task_score = sum(1 for keyword in task_keywords if keyword in user_input or keyword in response.lower())
        operation_score = sum(1 for keyword in operation_keywords if keyword in user_input or keyword in response.lower())
        
        if task_score > operation_score:
            return "task_area"
        else:
            return "operation_area"
    
    def filter_dataset_by_area(self, dataset_path, area_type):
        """按区域类型过滤数据集"""
        try:
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
            
            filtered_dataset = []
            
            for interaction in dataset:
                # 确定区域类型
                if "area" not in interaction:
                    interaction["area"] = self._determine_area(interaction)
                
                # 过滤
                if interaction["area"] == area_type:
                    filtered_dataset.append(interaction)
            
            # 导出过滤后的数据集
            output_path = dataset_path.replace('.json', f'_{area_type}.json')
            with open(output_path, 'w') as f:
                json.dump(filtered_dataset, f, indent=2)
            
            self.logger.info(f"已过滤 {area_type} 数据: {len(filtered_dataset)}/{len(dataset)}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"过滤数据异常: {str(e)}")
            return None
    
    def merge_datasets(self, dataset_paths, output_path):
        """合并多个数据集"""
        try:
            merged_dataset = []
            
            for path in dataset_paths:
                with open(path, 'r') as f:
                    dataset = json.load(f)
                merged_dataset.extend(dataset)
            
            # 按时间戳排序
            merged_dataset.sort(key=lambda x: x.get("timestamp", 0))
            
            # 导出合并后的数据集
            with open(output_path, 'w') as f:
                json.dump(merged_dataset, f, indent=2)
            
            self.logger.info(f"已合并 {len(dataset_paths)} 个数据集，共 {len(merged_dataset)} 条记录")
            return output_path
            
        except Exception as e:
            self.logger.error(f"合并数据集异常: {str(e)}")
            return None


# 如果直接运行此脚本，执行简单的测试
if __name__ == "__main__":
    validator = ManusDataValidator()
    
    # 测试数据集路径
    test_dataset_path = "manus_test_interactions.json"
    
    # 验证数据集
    validation_result, enhanced_path = validator.validate_dataset(test_dataset_path)
    if validation_result:
        print(f"验证结果: {validation_result}")
        print(f"增强数据集路径: {enhanced_path}")
        
        # 按区域过滤
        task_area_path = validator.filter_dataset_by_area(enhanced_path, "task_area")
        operation_area_path = validator.filter_dataset_by_area(enhanced_path, "operation_area")
        
        if task_area_path and operation_area_path:
            # 合并数据集
            merged_path = "manus_merged_dataset.json"
            result_path = validator.merge_datasets([task_area_path, operation_area_path], merged_path)
            if result_path:
                print(f"合并数据集路径: {result_path}")
    else:
        print("数据验证失败")
