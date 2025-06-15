"""
智能介入引擎 - 核心智能介入系统
基于Playwright实现跨应用智能介入
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page

class InterventionEngine:
    """智能介入引擎"""
    
    def __init__(self):
        """初始化智能介入引擎"""
        self.logger = logging.getLogger("InterventionEngine")
        
        self.playwright = None
        self.browser = None
        self.pages = {}
        self.monitoring = False
        
        # 监听配置
        self.targets = {
            "vscode": {
                "url_pattern": "vscode://",
                "selectors": {
                    "input": "textarea, input[type='text']",
                    "file_input": "input[type='file']"
                }
            },
            "manus": {
                "url_pattern": "manus.im",
                "selectors": {
                    "input": "[placeholder*='发送消息'], textarea",
                    "file_input": "input[type='file']"
                }
            }
        }
        
        self.logger.info("智能介入引擎初始化完成")
    
    async def start(self):
        """启动智能介入"""
        try:
            self.logger.info("启动智能介入引擎")
            
            # 启动Playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # 可见模式，便于调试
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            # 开始监听
            self.monitoring = True
            asyncio.create_task(self._monitor_loop())
            
            self.logger.info("智能介入引擎启动成功")
            
        except Exception as e:
            self.logger.error(f"启动智能介入引擎失败: {e}")
            raise
    
    async def stop(self):
        """停止智能介入"""
        try:
            self.logger.info("停止智能介入引擎")
            
            self.monitoring = False
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            self.logger.info("智能介入引擎已停止")
            
        except Exception as e:
            self.logger.error(f"停止智能介入引擎失败: {e}")
    
    async def _monitor_loop(self):
        """监听循环"""
        while self.monitoring:
            try:
                # 检查现有页面
                await self._check_existing_pages()
                
                # 监听新页面
                await self._monitor_new_pages()
                
                await asyncio.sleep(1)  # 1秒检查一次
                
            except Exception as e:
                self.logger.error(f"监听循环错误: {e}")
                await asyncio.sleep(5)  # 错误时等待5秒
    
    async def _check_existing_pages(self):
        """检查现有页面"""
        if not self.browser:
            return
        
        try:
            contexts = self.browser.contexts
            for context in contexts:
                pages = context.pages
                for page in pages:
                    page_url = page.url
                    page_id = id(page)
                    
                    # 检查是否是目标页面
                    target_type = self._identify_target(page_url)
                    if target_type and page_id not in self.pages:
                        await self._setup_page_monitoring(page, target_type)
                        
        except Exception as e:
            self.logger.error(f"检查现有页面失败: {e}")
    
    async def _monitor_new_pages(self):
        """监听新页面"""
        # 这里可以添加监听新页面的逻辑
        pass
    
    def _identify_target(self, url: str) -> Optional[str]:
        """识别目标类型"""
        for target_type, config in self.targets.items():
            if config["url_pattern"] in url:
                return target_type
        return None
    
    async def _setup_page_monitoring(self, page: Page, target_type: str):
        """设置页面监听"""
        try:
            page_id = id(page)
            self.pages[page_id] = {
                "page": page,
                "type": target_type,
                "last_content": ""
            }
            
            self.logger.info(f"开始监听页面: {target_type} - {page.url}")
            
            # 监听输入事件
            await self._monitor_input_events(page, target_type)
            
            # 监听文件上传事件
            await self._monitor_file_events(page, target_type)
            
        except Exception as e:
            self.logger.error(f"设置页面监听失败: {e}")
    
    async def _monitor_input_events(self, page: Page, target_type: str):
        """监听输入事件"""
        try:
            selectors = self.targets[target_type]["selectors"]
            
            # 监听输入框变化
            await page.evaluate(f"""
                () => {{
                    const inputs = document.querySelectorAll('{selectors["input"]}');
                    inputs.forEach(input => {{
                        input.addEventListener('input', (e) => {{
                            window.powerAutoIntervention = window.powerAutoIntervention || {{}};
                            window.powerAutoIntervention.lastInput = {{
                                type: 'input',
                                content: e.target.value,
                                timestamp: Date.now(),
                                target: '{target_type}'
                            }};
                        }});
                    }});
                }}
            """)
            
            # 定期检查输入变化
            asyncio.create_task(self._check_input_changes(page, target_type))
            
        except Exception as e:
            self.logger.error(f"监听输入事件失败: {e}")
    
    async def _monitor_file_events(self, page: Page, target_type: str):
        """监听文件事件"""
        try:
            selectors = self.targets[target_type]["selectors"]
            
            # 监听文件上传
            await page.evaluate(f"""
                () => {{
                    const fileInputs = document.querySelectorAll('{selectors["file_input"]}');
                    fileInputs.forEach(input => {{
                        input.addEventListener('change', (e) => {{
                            window.powerAutoIntervention = window.powerAutoIntervention || {{}};
                            window.powerAutoIntervention.lastFile = {{
                                type: 'file',
                                files: Array.from(e.target.files).map(f => f.name),
                                timestamp: Date.now(),
                                target: '{target_type}'
                            }};
                        }});
                    }});
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"监听文件事件失败: {e}")
    
    async def _check_input_changes(self, page: Page, target_type: str):
        """检查输入变化"""
        while self.monitoring:
            try:
                # 获取最新输入
                intervention_data = await page.evaluate("""
                    () => window.powerAutoIntervention || {}
                """)
                
                if intervention_data.get("lastInput"):
                    input_data = intervention_data["lastInput"]
                    await self._process_input(input_data)
                
                if intervention_data.get("lastFile"):
                    file_data = intervention_data["lastFile"]
                    await self._process_file(file_data)
                
                await asyncio.sleep(0.5)  # 500ms检查一次
                
            except Exception as e:
                self.logger.error(f"检查输入变化失败: {e}")
                break
    
    async def _process_input(self, input_data: Dict[str, Any]):
        """处理输入数据"""
        try:
            content = input_data.get("content", "")
            target = input_data.get("target", "")
            
            if len(content) > 10:  # 只处理有意义的输入
                self.logger.info(f"检测到输入 [{target}]: {content[:50]}...")
                
                # 这里可以调用AI分析
                analysis = await self._analyze_content(content, target)
                
                if analysis.get("should_intervene"):
                    await self._perform_intervention(analysis, target)
                    
        except Exception as e:
            self.logger.error(f"处理输入数据失败: {e}")
    
    async def _process_file(self, file_data: Dict[str, Any]):
        """处理文件数据"""
        try:
            files = file_data.get("files", [])
            target = file_data.get("target", "")
            
            self.logger.info(f"检测到文件上传 [{target}]: {files}")
            
            # 这里可以分析文件类型和内容
            analysis = await self._analyze_files(files, target)
            
            if analysis.get("should_intervene"):
                await self._perform_intervention(analysis, target)
                
        except Exception as e:
            self.logger.error(f"处理文件数据失败: {e}")
    
    async def _analyze_content(self, content: str, target: str) -> Dict[str, Any]:
        """分析内容"""
        # 简单的分析逻辑
        should_intervene = False
        suggestions = []
        
        if "错误" in content or "error" in content.lower():
            should_intervene = True
            suggestions.append("检测到可能的错误，建议检查代码逻辑")
        
        if "帮助" in content or "help" in content.lower():
            should_intervene = True
            suggestions.append("检测到求助请求，可以提供相关建议")
        
        return {
            "should_intervene": should_intervene,
            "suggestions": suggestions,
            "content": content,
            "target": target
        }
    
    async def _analyze_files(self, files: List[str], target: str) -> Dict[str, Any]:
        """分析文件"""
        should_intervene = False
        suggestions = []
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                should_intervene = True
                suggestions.append(f"检测到代码文件 {file}，可以提供代码分析")
            elif file.endswith(('.jpg', '.png', '.gif')):
                should_intervene = True
                suggestions.append(f"检测到图片文件 {file}，可以提供图像分析")
        
        return {
            "should_intervene": should_intervene,
            "suggestions": suggestions,
            "files": files,
            "target": target
        }
    
    async def _perform_intervention(self, analysis: Dict[str, Any], target: str):
        """执行智能介入"""
        try:
            suggestions = analysis.get("suggestions", [])
            
            self.logger.info(f"执行智能介入 [{target}]: {suggestions}")
            
            # 这里可以实现具体的介入逻辑
            # 比如在页面中显示建议、自动填充内容等
            
        except Exception as e:
            self.logger.error(f"执行智能介入失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "monitoring": self.monitoring,
            "browser_active": self.browser is not None,
            "pages_count": len(self.pages),
            "targets": list(self.targets.keys())
        }

