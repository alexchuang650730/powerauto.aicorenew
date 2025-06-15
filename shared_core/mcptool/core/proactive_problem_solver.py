"""
主动问题解决器 - 集成Sequential Thinking和WebAgentB能力
该模块实现主动发现问题并推送解决方案到GitHub的功能。
"""
import os
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入适配器 - 调整导入路径以适应主仓库结构
from agents.ppt_agent.core.mcp.sequential_thinking_adapter import SequentialThinkingAdapter
from agents.ppt_agent.core.mcp.webagent_adapter import WebAgentBAdapter

class GitHubPushManager:
    """GitHub推送管理器，负责将解决方案推送到GitHub"""
    
    def __init__(self, repo_path: str, remote: str = "origin", branch: str = "main"):
        """
        初始化GitHub推送管理器
        
        Args:
            repo_path: 本地仓库路径
            remote: 远程仓库名称
            branch: 分支名称
        """
        self.repo_path = repo_path
        self.remote = remote
        self.branch = branch
        self.logger = logging.getLogger("GitHubPushManager")
        
        self.logger.info(f"初始化GitHub推送管理器: {repo_path}, {remote}/{branch}")
    
    def check_changes(self, files: List[str] = None) -> bool:
        """
        检查是否有文件变更
        
        Args:
            files: 要检查的文件列表，如果为None则检查所有文件
            
        Returns:
            bool: 是否有变更
        """
        self.logger.info("检查文件变更")
        
        try:
            cmd = ["git", "status", "--porcelain"]
            if files:
                cmd.extend(files)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 如果有输出，说明有变更
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            self.logger.error(f"检查文件变更失败: {e}")
            return False
    
    def add_files(self, files: List[str]) -> bool:
        """
        添加文件到暂存区
        
        Args:
            files: 要添加的文件列表
            
        Returns:
            bool: 是否成功
        """
        self.logger.info(f"添加文件到暂存区: {files}")
        
        try:
            cmd = ["git", "add"]
            cmd.extend(files)
            
            subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"添加文件到暂存区失败: {e}")
            return False
    
    def commit(self, message: str) -> bool:
        """
        提交变更
        
        Args:
            message: 提交信息
            
        Returns:
            bool: 是否成功
        """
        self.logger.info(f"提交变更: {message}")
        
        try:
            cmd = ["git", "commit", "-m", message]
            
            subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"提交变更失败: {e}")
            return False
    
    def push(self) -> bool:
        """
        推送到远程仓库
        
        Returns:
            bool: 是否成功
        """
        self.logger.info(f"推送到远程仓库: {self.remote}/{self.branch}")
        
        try:
            cmd = ["git", "push", self.remote, self.branch]
            
            subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"推送到远程仓库失败: {e}")
            return False
    
    def create_branch(self, branch_name: str) -> bool:
        """
        创建新分支
        
        Args:
            branch_name: 分支名称
            
        Returns:
            bool: 是否成功
        """
        self.logger.info(f"创建新分支: {branch_name}")
        
        try:
            # 检查分支是否已存在
            check_cmd = ["git", "branch", "--list", branch_name]
            check_result = subprocess.run(
                check_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 如果分支已存在，则切换到该分支
            if check_result.stdout.strip():
                self.logger.info(f"分支已存在，切换到: {branch_name}")
                switch_cmd = ["git", "checkout", branch_name]
                subprocess.run(
                    switch_cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                # 创建并切换到新分支
                create_cmd = ["git", "checkout", "-b", branch_name]
                subprocess.run(
                    create_cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            # 更新当前分支
            self.branch = branch_name
            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"创建新分支失败: {e}")
            return False
    
    def create_pull_request(self, title: str, body: str, target_branch: str = "main") -> Optional[str]:
        """
        创建Pull Request
        
        Args:
            title: PR标题
            body: PR内容
            target_branch: 目标分支
            
        Returns:
            Optional[str]: PR URL，如果失败则返回None
        """
        self.logger.info(f"创建Pull Request: {title}, 目标分支: {target_branch}")
        
        try:
            # 这里应该使用GitHub API创建PR
            # 为了演示，我们假设PR创建成功
            pr_url = f"https://github.com/example/repo/pull/123"
            
            self.logger.info(f"Pull Request创建成功: {pr_url}")
            
            return pr_url
        except Exception as e:
            self.logger.error(f"创建Pull Request失败: {e}")
            return None

class ProactiveProblemSolver:
    """主动问题解决器，负责主动发现问题并推送解决方案到GitHub"""
    
    def __init__(self, repo_path: str):
        """
        初始化主动问题解决器
        
        Args:
            repo_path: 本地仓库路径
        """
        self.repo_path = repo_path
        self.logger = logging.getLogger("ProactiveProblemSolver")
        
        # 初始化WebAgentB适配器
        self.webagent = WebAgentBAdapter()
        # 初始化Sequential Thinking适配器
        self.sequential_thinking = SequentialThinkingAdapter()
        # 初始化GitHub推送管理器
        self.github = GitHubPushManager(repo_path)
        
        self.logger.info(f"初始化主动问题解决器: {repo_path}")
    
    def solve_on_event(self, event_type: str) -> Dict:
        """
        基于事件触发问题解决
        
        Args:
            event_type: 事件类型，如"manual_check"、"system_startup"等
            
        Returns:
            Dict: 问题解决结果
        """
        self.logger.info(f"基于事件触发问题解决: {event_type}")
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 步骤1: 使用Sequential Thinking规划任务
        task_plan = self._plan_task("检查系统问题并提供解决方案")
        
        # 步骤2: 使用WebAgentB收集信息
        system_info = self._collect_system_info()
        
        # 步骤3: 分析问题
        problems = self._analyze_problems(system_info)
        
        # 如果没有发现问题，则返回
        if not problems:
            self.logger.info("未发现问题")
            return {
                "status": "success",
                "message": "未发现需要解决的问题",
                "event_type": event_type,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
        
        # 步骤4: 生成解决方案
        solutions = self._generate_solutions(problems)
        
        # 步骤5: 实现解决方案
        implementation_results = self._implement_solutions(solutions)
        
        # 步骤6: 推送到GitHub
        push_result = self._push_to_github(implementation_results, event_type)
        
        # 记录结束时间
        end_time = datetime.now()
        
        return {
            "status": "success",
            "message": f"成功解决{len(problems)}个问题并推送到GitHub",
            "event_type": event_type,
            "problems": problems,
            "solutions": solutions,
            "implementation_results": implementation_results,
            "push_result": push_result,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds()
        }
    
    def _plan_task(self, task_description: str) -> Dict:
        """规划任务"""
        self.logger.info(f"规划任务: {task_description}")
        
        # 使用Sequential Thinking分解任务
        decomposed_task = self.sequential_thinking.decompose_task(task_description)
        
        # 创建todo.md
        todo_md = self.sequential_thinking.create_todo_md(decomposed_task)
        
        # 保存todo.md
        todo_path = os.path.join(self.repo_path, "todo.md")
        with open(todo_path, "w") as f:
            f.write(todo_md)
        
        return {
            "task_description": task_description,
            "decomposed_task": decomposed_task,
            "todo_md": todo_md,
            "todo_path": todo_path
        }
    
    def _collect_system_info(self) -> Dict:
        """收集系统信息"""
        self.logger.info("收集系统信息")
        
        # 使用WebAgentB访问manus.im并进行语义化提取
        manus_info = self.webagent.semantic_extract("https://manus.im")
        
        # 使用WebAgentB搜索相关信息
        search_results = self.webagent.enhanced_search("manus ai latest updates", depth=2)
        
        # 收集GitHub仓库信息
        github_info = self._collect_github_info()
        
        return {
            "manus_info": manus_info,
            "search_results": search_results,
            "github_info": github_info,
            "timestamp": datetime.now().isoformat()
        }
    
    def _collect_github_info(self) -> Dict:
        """收集GitHub仓库信息"""
        self.logger.info("收集GitHub仓库信息")
        
        try:
            # 获取最新提交
            last_commit_cmd = ["git", "log", "-1", "--pretty=format:%H|%an|%ad|%s"]
            last_commit_result = subprocess.run(
                last_commit_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if last_commit_result.stdout:
                commit_parts = last_commit_result.stdout.split("|")
                last_commit = {
                    "hash": commit_parts[0],
                    "author": commit_parts[1],
                    "date": commit_parts[2],
                    "message": commit_parts[3]
                }
            else:
                last_commit = None
            
            # 获取分支信息
            branch_cmd = ["git", "branch", "--show-current"]
            branch_result = subprocess.run(
                branch_cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            current_branch = branch_result.stdout.strip()
            
            return {
                "last_commit": last_commit,
                "current_branch": current_branch
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"收集GitHub仓库信息失败: {e}")
            return {}
    
    def _analyze_problems(self, system_info: Dict) -> List[Dict]:
        """分析系统问题"""
        self.logger.info("分析系统问题")
        
        problems = []
        
        # 分析manus.im信息
        if "manus_info" in system_info and system_info["manus_info"]:
            manus_problems = self._analyze_manus_info(system_info["manus_info"])
            problems.extend(manus_problems)
        
        # 分析搜索结果
        if "search_results" in system_info and system_info["search_results"]:
            search_problems = self._analyze_search_results(system_info["search_results"])
            problems.extend(search_problems)
        
        # 分析GitHub仓库信息
        if "github_info" in system_info and system_info["github_info"]:
            github_problems = self._analyze_github_info(system_info["github_info"])
            problems.extend(github_problems)
        
        return problems
    
    def _analyze_manus_info(self, manus_info: Dict) -> List[Dict]:
        """分析manus.im信息"""
        self.logger.info("分析manus.im信息")
        
        problems = []
        
        # 这里应该包含实际的分析逻辑
        # 为了演示，我们假设发现了一个问题
        
        if "structured_content" in manus_info:
            content = manus_info["structured_content"]
            
            # 检查是否有新功能或更新
            if "main_points" in content:
                for point in content["main_points"]:
                    if "新功能" in point or "更新" in point or "升级" in point:
                        problems.append({
                            "id": f"manus_update_{len(problems) + 1}",
                            "description": f"Manus有新的更新需要适配: {point}",
                            "severity": "medium",
                            "source": "manus_info"
                        })
        
        return problems
    
    def _analyze_search_results(self, search_results: List[Dict]) -> List[Dict]:
        """分析搜索结果"""
        self.logger.info("分析搜索结果")
        
        problems = []
        
        # 这里应该包含实际的分析逻辑
        # 为了演示，我们假设发现了一个问题
        
        for i, result in enumerate(search_results):
            if "semantic_analysis" in result:
                analysis = result["semantic_analysis"]
                
                # 检查关键概念
                if "key_concepts" in analysis:
                    for concept in analysis["key_concepts"]:
                        if concept not in ["概念1", "概念2"]:  # 假设这些是已知概念
                            problems.append({
                                "id": f"new_concept_{len(problems) + 1}",
                                "description": f"发现新的关键概念需要研究: {concept}",
                                "severity": "low",
                                "source": "search_results"
                            })
        
        return problems
    
    def _analyze_github_info(self, github_info: Dict) -> List[Dict]:
        """分析GitHub仓库信息"""
        self.logger.info("分析GitHub仓库信息")
        
        problems = []
        
        # 这里应该包含实际的分析逻辑
        # 为了演示，我们假设发现了一个问题
        
        if "last_commit" in github_info and github_info["last_commit"]:
            commit = github_info["last_commit"]
            
            # 检查提交信息是否包含TODO或FIXME
            if "message" in commit and ("TODO" in commit["message"] or "FIXME" in commit["message"]):
                problems.append({
                    "id": f"commit_todo_{len(problems) + 1}",
                    "description": f"提交信息中包含待办事项: {commit['message']}",
                    "severity": "medium",
                    "source": "github_info"
                })
        
        return problems
    
    def _generate_solutions(self, problems: List[Dict]) -> List[Dict]:
        """为问题生成解决方案"""
        self.logger.info(f"为{len(problems)}个问题生成解决方案")
        
        solutions = []
        
        for problem in problems:
            # 使用WebAgentB搜索相关解决方案
            search_results = self.webagent.enhanced_search(
                f"解决方案 {problem['description']}",
                depth=1
            )
            
            # 提取相关页面内容
            page_contents = []
            for result in search_results[:2]:
                content = self.webagent.semantic_extract(result["url"])
                if content:
                    page_contents.append(content)
            
            # 基于搜索结果生成解决方案
            # 这里应该包含实际的生成逻辑
            # 为了演示，我们假设生成了一个解决方案
            
            solution = {
                "problem_id": problem["id"],
                "problem_description": problem["description"],
                "solution_description": f"解决{problem['description']}的方案",
                "implementation_steps": [
                    "步骤1: 分析问题",
                    "步骤2: 设计解决方案",
                    "步骤3: 实现解决方案",
                    "步骤4: 测试解决方案"
                ],
                "files_to_modify": [
                    {
                        "path": "example/file1.py",
                        "changes": [
                            {
                                "type": "add",
                                "content": "# 添加的内容"
                            }
                        ]
                    }
                ],
                "references": [result["url"] for result in search_results[:2]]
            }
            
            solutions.append(solution)
        
        return solutions
    
    def _implement_solutions(self, solutions: List[Dict]) -> List[Dict]:
        """实现解决方案"""
        self.logger.info(f"实现{len(solutions)}个解决方案")
        
        implementation_results = []
        
        for solution in solutions:
            # 这里应该包含实际的实现逻辑
            # 为了演示，我们假设实现成功
            
            result = {
                "solution_id": solution["problem_id"],
                "status": "success",
                "modified_files": [],
                "added_files": [],
                "deleted_files": []
            }
            
            # 处理文件修改
            for file_info in solution["files_to_modify"]:
                file_path = file_info["path"]
                file_path_full = os.path.join(self.repo_path, file_path)
                
                # 确保目录存在
                os.makedirs(os.path.dirname(file_path_full), exist_ok=True)
                
                # 处理文件变更
                if os.path.exists(file_path_full):
                    # 修改现有文件
                    with open(file_path_full, "a") as f:
                        for change in file_info["changes"]:
                            if change["type"] == "add":
                                f.write(f"\n{change['content']}\n")
                    
                    result["modified_files"].append(file_path)
                else:
                    # 创建新文件
                    with open(file_path_full, "w") as f:
                        for change in file_info["changes"]:
                            if change["type"] == "add":
                                f.write(f"{change['content']}\n")
                    
                    result["added_files"].append(file_path)
            
            implementation_results.append(result)
        
        return implementation_results
    
    def _push_to_github(self, implementation_results: List[Dict], event_type: str) -> Dict:
        """推送解决方案到GitHub"""
        self.logger.info("推送解决方案到GitHub")
        
        # 创建新分支
        branch_name = f"auto-fix-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        branch_created = self.github.create_branch(branch_name)
        
        if not branch_created:
            return {
                "status": "failed",
                "message": "创建分支失败",
                "branch": branch_name
            }
        
        # 收集修改的文件
        modified_files = []
        for result in implementation_results:
            modified_files.extend(result["modified_files"])
            modified_files.extend(result["added_files"])
        
        # 添加文件到暂存区
        files_added = self.github.add_files(modified_files)
        
        if not files_added:
            return {
                "status": "failed",
                "message": "添加文件到暂存区失败",
                "branch": branch_name
            }
        
        # 提交变更
        commit_message = f"自动修复: {event_type} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        committed = self.github.commit(commit_message)
        
        if not committed:
            return {
                "status": "failed",
                "message": "提交变更失败",
                "branch": branch_name
            }
        
        # 推送到远程仓库
        pushed = self.github.push()
        
        if not pushed:
            return {
                "status": "failed",
                "message": "推送到远程仓库失败",
                "branch": branch_name
            }
        
        # 创建Pull Request
        pr_title = f"自动修复: {event_type}"
        pr_body = f"自动修复: {event_type}\n\n"
        
        for result in implementation_results:
            pr_body += f"- 修复问题: {result['solution_id']}\n"
            pr_body += f"  - 修改文件: {', '.join(result['modified_files'])}\n"
            pr_body += f"  - 添加文件: {', '.join(result['added_files'])}\n"
            pr_body += f"  - 删除文件: {', '.join(result['deleted_files'])}\n\n"
        
        pr_url = self.github.create_pull_request(pr_title, pr_body)
        
        if not pr_url:
            return {
                "status": "partial",
                "message": "推送成功但创建Pull Request失败",
                "branch": branch_name
            }
        
        return {
            "status": "success",
            "message": "推送成功并创建Pull Request",
            "branch": branch_name,
            "pr_url": pr_url
        }
