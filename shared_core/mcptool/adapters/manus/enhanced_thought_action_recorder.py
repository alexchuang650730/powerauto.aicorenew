#!/usr/bin/env python3
"""
增强版ThoughtActionRecorder视觉采集模块

此模块优化并强化了原有ThoughtActionRecorder的视觉采集功能，
增加了多标签页处理、浏览器前台激活、窗口大小自适应和窗口最小化检测与恢复等功能，
用于通过视觉方式获取Manus界面的工作区和操作区数据。
"""

import re
import os
import time
import json
import logging
import base64
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EnhancedThoughtActionRecorder:
    """
    优化和强化的ThoughtActionRecorder视觉采集模块，
    增加了多标签页处理、浏览器前台激活、窗口大小自适应和窗口最小化检测与恢复等功能
    """
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger("enhanced_thought_action_recorder")
        
        # 设置日志
        self._setup_logging()
        
        # 初始化Selenium WebDriver
        self.driver = None
        self.is_connected = False
        
        # 存储捕获的数据
        self.captured_data = []
        
        # 区域坐标（将在连接时初始化）
        self.work_area_coords = None
        self.operation_area_coords = None
        self.input_box_coords = None
        
        # OCR引擎设置
        self._setup_ocr()
    
    def _load_config(self, config_path):
        """加载配置文件"""
        default_config = {
            "log_level": "INFO",
            "screenshot_interval": 2.0,  # 截图间隔（秒）
            "manus_url": "https://manus.im/app/nptXUzLrh5iY8da4BoBnt9",
            "browser_type": "chrome",
            "headless": False,  # 默认非无头模式，便于调试
            "ocr_engine": "tesseract",
            "tesseract_path": "/usr/bin/tesseract",
            "tesseract_lang": "chi_sim+eng",  # 支持中文简体和英文
            "output_dir": "./captured_data",
            "auto_save": True,
            "auto_save_interval": 60,  # 自动保存间隔（秒）
            "min_window_width": 1024,  # 最小窗口宽度
            "min_window_height": 768,  # 最小窗口高度
            "area_detection": {
                "work_area": {
                    "method": "template",
                    "template_path": "./templates/work_area.png",
                    "confidence": 0.7
                },
                "operation_area": {
                    "method": "template",
                    "template_path": "./templates/operation_area.png",
                    "confidence": 0.7
                },
                "input_box": {
                    "method": "template",
                    "template_path": "./templates/input_box.png",
                    "confidence": 0.7
                }
            },
            "pattern_detection": {
                "thought_pattern": r"<thought>(.*?)</thought>",
                "action_pattern": r"<action>(.*?)</action>",
                "step_pattern": r"Step (\d+):(.*?)(?=Step \d+:|$)"
            }
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
    
    def _setup_ocr(self):
        """设置OCR引擎"""
        ocr_engine = self.config.get("ocr_engine", "tesseract")
        
        if ocr_engine == "tesseract":
            tesseract_path = self.config.get("tesseract_path", "/usr/bin/tesseract")
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                self.logger.info(f"已设置Tesseract OCR路径: {tesseract_path}")
            else:
                self.logger.warning(f"Tesseract路径不存在: {tesseract_path}，将使用系统默认路径")
    
    def connect(self, url=None, credentials=None):
        """连接到Manus平台"""
        if self.is_connected:
            self.logger.info("已经连接到Manus平台")
            return True
        
        try:
            # 初始化WebDriver
            browser_type = self.config.get("browser_type", "chrome")
            headless = self.config.get("headless", False)
            
            if browser_type.lower() == "chrome":
                options = Options()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                
                self.driver = webdriver.Chrome(options=options)
            else:
                self.logger.error(f"不支持的浏览器类型: {browser_type}")
                return False
            
            # 打开Manus平台
            target_url = url or self.config.get("manus_url")
            self.driver.get(target_url)
            self.logger.info(f"已打开Manus平台: {target_url}")
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 验证页面
            if not self._verify_manus_page():
                self.logger.error("未能验证Manus平台页面")
                if self.driver:
                    self.driver.quit()
                    self.driver = None
                return False
            
            # 如果需要登录
            if credentials:
                self._login(credentials)
            
            # 确保浏览器在前台
            self._ensure_browser_foreground()
            
            # 确保窗口大小适合数据采集
            self._ensure_proper_window_size()
            
            # 检测区域坐标
            self._detect_areas()
            
            self.is_connected = True
            self.logger.info("成功连接到Manus平台")
            return True
            
        except Exception as e:
            self.logger.error(f"连接Manus平台失败: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None
            return False
    
    def _verify_manus_page(self):
        """验证当前页面是否为Manus平台页面"""
        try:
            if self.driver:
                # 检查URL
                current_url = self.driver.current_url
                if "manus.im/app" not in current_url:
                    self.logger.warning(f"当前URL不是Manus平台: {current_url}")
                    return False
                
                # 检查页面特征元素
                try:
                    # 等待特征元素出现
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".manus-app-container"))
                    )
                    return True
                except:
                    self.logger.warning("未找到Manus平台特征元素")
                    return False
            return False
        except Exception as e:
            self.logger.error(f"验证Manus页面失败: {str(e)}")
            return False
    
    def _find_manus_tab(self):
        """在多个标签页中查找Manus平台页面"""
        if not self.driver:
            return False
            
        current_handle = self.driver.current_window_handle
        found_manus = False
        manus_handle = None
        
        try:
            # 遍历所有标签页
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if "manus.im/app" in self.driver.current_url:
                    found_manus = True
                    manus_handle = handle
                    break
            
            # 如果找到Manus页面，切换到该页面
            if found_manus:
                if current_handle != manus_handle:
                    self.driver.switch_to.window(manus_handle)
                return True
            else:
                # 如果没找到，切回原页面
                self.driver.switch_to.window(current_handle)
                return False
                
        except Exception as e:
            self.logger.error(f"查找Manus标签页失败: {str(e)}")
            try:
                self.driver.switch_to.window(current_handle)
            except:
                pass
            return False
    
    def _check_and_restore_minimized_window(self):
        """检测并恢复最小化的窗口"""
        if not self.driver:
            return False
            
        try:
            # 尝试获取窗口状态
            window_state = self.driver.execute_script(
                "return document.visibilityState === 'visible' ? 'normal' : 'minimized';"
            )
            
            if window_state == 'minimized':
                self.logger.warning("检测到窗口已最小化，尝试恢复")
                
                # 在Windows上恢复窗口
                if os.name == 'nt':
                    try:
                        import win32gui
                        import win32con
                        
                        # 查找并恢复窗口
                        window_title = self.driver.title
                        hwnd = win32gui.FindWindow(None, window_title)
                        if hwnd:
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            win32gui.SetForegroundWindow(hwnd)
                            return True
                    except Exception as e:
                        self.logger.warning(f"使用win32gui恢复窗口失败: {str(e)}")
                
                # 在Linux上恢复窗口
                elif os.name == 'posix':
                    try:
                        window_title = self.driver.title
                        os.system(f"xdotool search --name '{window_title}' windowactivate")
                        return True
                    except Exception as e:
                        self.logger.warning(f"使用xdotool恢复窗口失败: {str(e)}")
                
                # 通用方法：尝试使用Selenium命令
                try:
                    self.driver.maximize_window()
                    time.sleep(0.5)
                    return True
                except Exception as e:
                    self.logger.warning(f"使用Selenium恢复窗口失败: {str(e)}")
                    
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"检查窗口状态失败: {str(e)}")
            return False
    
    def _ensure_browser_foreground(self):
        """确保浏览器在前台"""
        if not self.driver:
            return False
            
        try:
            # 首先检查并恢复最小化的窗口
            if not self._check_and_restore_minimized_window():
                self.logger.warning("无法恢复最小化的窗口，尝试其他方法")
            
            # 尝试使浏览器窗口获得焦点
            if hasattr(self.driver, "execute_script"):
                self.driver.execute_script("window.focus();")
                
            # 在Windows系统上，可以使用win32gui
            if os.name == 'nt':
                try:
                    import win32gui
                    import win32con
                    
                    # 获取浏览器窗口句柄
                    hwnd = None
                    if hasattr(self.driver, "current_window_handle"):
                        window_info = self.driver.execute_script(
                            "return { width: window.outerWidth, height: window.outerHeight, left: window.screenX, top: window.screenY };"
                        )
                        
                        def callback(hwnd, extra):
                            rect = win32gui.GetWindowRect(hwnd)
                            if (rect[2] - rect[0] == window_info["width"] and 
                                rect[3] - rect[1] == window_info["height"]):
                                extra.append(hwnd)
                        
                        hwnds = []
                        win32gui.EnumWindows(callback, hwnds)
                        
                        if hwnds:
                            hwnd = hwnds[0]
                    
                    # 如果找到窗口句柄，将其置于前台
                    if hwnd:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                        return True
                except ImportError:
                    self.logger.warning("未安装win32gui模块，无法将浏览器置于前台")
                except Exception as e:
                    self.logger.warning(f"将浏览器置于前台失败: {str(e)}")
            
            # 在Linux系统上，可以使用xdotool
            elif os.name == 'posix':
                try:
                    window_title = self.driver.title
                    os.system(f"xdotool search --name '{window_title}' windowactivate")
                    return True
                except Exception as e:
                    self.logger.warning(f"将浏览器置于前台失败: {str(e)}")
                    
            # 通用方法：最大化窗口
            self.driver.maximize_window()
            time.sleep(0.5)  # 给窗口切换一些时间
            
            return True
        except Exception as e:
            self.logger.error(f"确保浏览器在前台失败: {str(e)}")
            return False
    
    def _ensure_proper_window_size(self):
        """确保窗口大小适合数据采集"""
        if not self.driver:
            return False
            
        try:
            # 获取当前窗口大小
            current_size = self.driver.get_window_size()
            min_width = self.config.get("min_window_width", 1024)
            min_height = self.config.get("min_window_height", 768)
            
            # 检查窗口是否足够大
            if current_size['width'] < min_width or current_size['height'] < min_height:
                self.logger.warning(f"窗口过小 ({current_size['width']}x{current_size['height']}), 调整大小")
                
                # 调整窗口大小
                self.driver.set_window_size(
                    max(current_size['width'], min_width),
                    max(current_size['height'], min_height)
                )
                
                # 给浏览器一些时间来调整布局
                time.sleep(0.5)
                
            return True
        except Exception as e:
            self.logger.error(f"调整窗口大小失败: {str(e)}")
            return False
    
    def _login(self, credentials):
        """登录Manus平台"""
        try:
            # 等待登录表单加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # 输入用户名和密码
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "login-button")
            
            username_input.send_keys(credentials.get("username", ""))
            password_input.send_keys(credentials.get("password", ""))
            login_button.click()
            
            # 等待登录完成
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("app")
            )
            
            self.logger.info("成功登录Manus平台")
            return True
            
        except Exception as e:
            self.logger.error(f"登录Manus平台失败: {str(e)}")
            return False
    
    def _detect_areas(self):
        """检测工作区、操作区和输入框的坐标"""
        try:
            # 验证页面
            if not self._verify_manus_page():
                self.logger.error("当前不是Manus平台页面，无法检测区域")
                return False
            
            # 等待页面完全加载
            time.sleep(2)
            
            # 检查窗口大小是否足够
            window_size = self.driver.get_window_size() if self.driver else None
            if window_size:
                min_width = self.config.get("min_window_width", 1024)
                min_height = self.config.get("min_window_height", 768)
                
                if window_size['width'] < min_width or window_size['height'] < min_height:
                    self.logger.warning(f"窗口过小 ({window_size['width']}x{window_size['height']}), 可能影响区域检测")
            
            # 获取页面截图
            screenshot = self._take_screenshot()
            if screenshot is None:
                self.logger.error("获取页面截图失败，无法检测区域")
                return False
            
            # 转换为OpenCV格式
            screenshot_np = np.array(screenshot)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 计算回退坐标时考虑窗口大小
            width, height = screenshot_cv.shape[1], screenshot_cv.shape[0]
            
            # 检测工作区
            self.work_area_coords = self._detect_area(
                screenshot_cv, 
                "work_area", 
                fallback=(0, 0, width // 3, height)
            )
            
            # 检测操作区
            self.operation_area_coords = self._detect_area(
                screenshot_cv, 
                "operation_area", 
                fallback=(width // 3, 0, width, height)
            )
            
            # 检测输入框
            self.input_box_coords = self._detect_area(
                screenshot_cv, 
                "input_box", 
                fallback=(width // 3, height - 100, width, height)
            )
            
            self.logger.info(f"区域检测结果 - 工作区: {self.work_area_coords}, 操作区: {self.operation_area_coords}, 输入框: {self.input_box_coords}")
            return True
            
        except Exception as e:
            self.logger.error(f"检测区域失败: {str(e)}")
            return False
    
    def _detect_area(self, screenshot, area_type, fallback=None):
        """检测特定区域的坐标"""
        area_config = self.config.get("area_detection", {}).get(area_type, {})
        method = area_config.get("method", "template")
        
        if method == "template":
            template_path = area_config.get("template_path")
            confidence = area_config.get("confidence", 0.7)
            
            if template_path and os.path.exists(template_path):
                template = cv2.imread(template_path)
                if template is not None:
                    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= confidence:
                        h, w = template.shape[:2]
                        return (max_loc[0], max_loc[1], max_loc[0] + w, max_loc[1] + h)
        
        # 如果检测失败，使用回退值
        self.logger.warning(f"使用回退值检测 {area_type} 区域")
        return fallback
    
    def _take_screenshot(self):
        """获取页面截图"""
        try:
            if self.driver:
                # 使用Selenium获取截图
                screenshot_base64 = self.driver.get_screenshot_as_base64()
                screenshot_data = base64.b64decode(screenshot_base64)
                screenshot = Image.open(tempfile.BytesIO(screenshot_data))
                return screenshot
            else:
                # 使用PIL获取屏幕截图
                screenshot = ImageGrab.grab()
                return screenshot
        except Exception as e:
            self.logger.error(f"获取截图失败: {str(e)}")
            return None
    
    def start_recording(self, duration=None, interval=None):
        """开始记录交互数据"""
        if not self.is_connected:
            self.logger.error("未连接到Manus平台，无法开始记录")
            return False
        
        interval = interval or self.config.get("screenshot_interval", 2.0)
        end_time = time.time() + duration if duration else None
        
        try:
            self.logger.info(f"开始记录交互数据，间隔: {interval}秒" + (f", 持续时间: {duration}秒" if duration else ""))
            
            last_auto_save = time.time()
            auto_save_interval = self.config.get("auto_save_interval", 60)
            
            while True:
                # 检查是否达到记录时间
                if end_time and time.time() >= end_time:
                    break
                
                # 确保在正确的Manus标签页
                if not self._find_manus_tab():
                    self.logger.warning("未找到Manus标签页，尝试重新连接")
                    if not self.connect():
                        self.logger.error("重新连接失败，停止记录")
                        break
                
                # 检查并恢复最小化的窗口
                if not self._check_and_restore_minimized_window():
                    self.logger.warning("无法恢复最小化的窗口，尝试重新连接")
                    if not self.connect():
                        self.logger.error("重新连接失败，停止记录")
                        break
                
                # 确保浏览器在前台
                self._ensure_browser_foreground()
                
                # 确保窗口大小适合数据采集
                self._ensure_proper_window_size()
                
                # 获取页面截图
                screenshot = self._take_screenshot()
                if screenshot is None:
                    self.logger.warning("获取截图失败，跳过本次记录")
                    time.sleep(interval)
                    continue
                
                # 处理截图
                self._process_screenshot(screenshot)
                
                # 自动保存
                if self.config.get("auto_save", True) and time.time() - last_auto_save >= auto_save_interval:
                    self._auto_save()
                    last_auto_save = time.time()
                
                # 等待下一次截图
                time.sleep(interval)
            
            self.logger.info("记录完成")
            
            # 最终保存
            if self.config.get("auto_save", True):
                self._auto_save()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("用户中断记录")
            
            # 保存已记录的数据
            if self.config.get("auto_save", True):
                self._auto_save()
            
            return True
            
        except Exception as e:
            self.logger.error(f"记录过程中发生错误: {str(e)}")
            return False
    
    def _process_screenshot(self, screenshot):
        """处理截图，提取工作区和操作区的数据"""
        timestamp = time.time()
        datetime_str = datetime.now().isoformat()
        
        try:
            # 保存原始截图
            screenshot_path = None
            if self.config.get("save_screenshots", False):
                output_dir = self.config.get("output_dir", "./captured_data")
                os.makedirs(output_dir, exist_ok=True)
                screenshot_filename = f"screenshot_{int(timestamp)}.png"
                screenshot_path = os.path.join(output_dir, screenshot_filename)
                screenshot.save(screenshot_path)
            
            # 提取工作区数据
            work_area_data = self._extract_area_data(screenshot, "work_area")
            
            # 提取操作区数据
            operation_area_data = self._extract_area_data(screenshot, "operation_area")
            
            # 提取输入框数据
            input_box_data = self._extract_area_data(screenshot, "input_box")
            
            # 构建记录
            record = {
                "timestamp": timestamp,
                "datetime": datetime_str,
                "screenshot_path": screenshot_path,
                "work_area": work_area_data,
                "operation_area": operation_area_data,
                "input_box": input_box_data,
                "thoughts": self._extract_thoughts(operation_area_data.get("text", "")),
                "actions": self._extract_actions(operation_area_data.get("text", "")),
                "steps": self._extract_steps(operation_area_data.get("text", ""))
            }
            
            self.captured_data.append(record)
            self.logger.debug(f"已处理截图，时间戳: {timestamp}")
            
            return record
            
        except Exception as e:
            self.logger.error(f"处理截图失败: {str(e)}")
            return None
    
    def _extract_area_data(self, screenshot, area_type):
        """提取特定区域的数据"""
        coords = None
        
        if area_type == "work_area" and self.work_area_coords:
            coords = self.work_area_coords
        elif area_type == "operation_area" and self.operation_area_coords:
            coords = self.operation_area_coords
        elif area_type == "input_box" and self.input_box_coords:
            coords = self.input_box_coords
        
        if not coords:
            self.logger.warning(f"未找到 {area_type} 区域坐标")
            return {"text": "", "confidence": 0}
        
        try:
            # 裁剪区域
            area_image = screenshot.crop(coords)
            
            # OCR识别
            text = pytesseract.image_to_string(
                area_image, 
                lang=self.config.get("tesseract_lang", "chi_sim+eng")
            )
            
            # 计算置信度（简单实现，实际应用中可能需要更复杂的算法）
            confidence = 1.0 if text.strip() else 0.0
            
            return {
                "text": text,
                "confidence": confidence
            }
            
        except Exception as e:
            self.logger.error(f"提取 {area_type} 区域数据失败: {str(e)}")
            return {"text": "", "confidence": 0}
    
    def _extract_thoughts(self, text):
        """从文本中提取思考过程"""
        thought_pattern = self.config.get("pattern_detection", {}).get("thought_pattern", r"<thought>(.*?)</thought>")
        thoughts = re.findall(thought_pattern, text, re.DOTALL)
        return thoughts if thoughts else []
    
    def _extract_actions(self, text):
        """从文本中提取行动"""
        action_pattern = self.config.get("pattern_detection", {}).get("action_pattern", r"<action>(.*?)</action>")
        actions = re.findall(action_pattern, text, re.DOTALL)
        return actions if actions else []
    
    def _extract_steps(self, text):
        """从文本中提取步骤"""
        step_pattern = self.config.get("pattern_detection", {}).get("step_pattern", r"Step (\d+):(.*?)(?=Step \d+:|$)")
        steps = re.findall(step_pattern, text, re.DOTALL)
        
        result = []
        for num, desc in steps:
            result.append({
                "step_number": int(num),
                "description": desc.strip()
            })
        
        return result
    
    def _auto_save(self):
        """自动保存记录的数据"""
        if not self.captured_data:
            self.logger.warning("没有数据需要保存")
            return False
        
        try:
            output_dir = self.config.get("output_dir", "./captured_data")
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = int(time.time())
            filename = f"thought_action_data_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(self.captured_data, f, indent=2)
            
            self.logger.info(f"已保存 {len(self.captured_data)} 条记录到 {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            return False
    
    def save_data(self, filepath=None):
        """保存记录的数据到指定文件"""
        if not self.captured_data:
            self.logger.warning("没有数据需要保存")
            return False
        
        try:
            if not filepath:
                output_dir = self.config.get("output_dir", "./captured_data")
                os.makedirs(output_dir, exist_ok=True)
                
                timestamp = int(time.time())
                filename = f"thought_action_data_{timestamp}.json"
                filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(self.captured_data, f, indent=2)
            
            self.logger.info(f"已保存 {len(self.captured_data)} 条记录到 {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {str(e)}")
            return False
    
    def load_data(self, filepath):
        """从文件加载数据"""
        try:
            with open(filepath, 'r') as f:
                loaded_data = json.load(f)
            
            self.captured_data.extend(loaded_data)
            self.logger.info(f"已从 {filepath} 加载 {len(loaded_data)} 条记录")
            return True
            
        except Exception as e:
            self.logger.error(f"加载数据失败: {str(e)}")
            return False
    
    def get_statistics(self):
        """获取记录数据的统计信息"""
        if not self.captured_data:
            return {"total": 0}
        
        stats = {
            "total": len(self.captured_data),
            "time_range": {
                "start": self.captured_data[0].get("datetime", ""),
                "end": self.captured_data[-1].get("datetime", "")
            },
            "thought_count": sum(len(record.get("thoughts", [])) for record in self.captured_data),
            "action_count": sum(len(record.get("actions", [])) for record in self.captured_data),
            "step_count": sum(len(record.get("steps", [])) for record in self.captured_data)
        }
        
        return stats
    
    def clear_data(self):
        """清除记录的数据"""
        self.captured_data = []
        self.logger.info("已清除所有记录的数据")
    
    def disconnect(self):
        """断开与Manus平台的连接"""
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        self.is_connected = False
        self.logger.info("已断开与Manus平台的连接")
    
    def __del__(self):
        """析构函数，确保资源释放"""
        self.disconnect()


# 如果直接运行此脚本，执行简单的测试
if __name__ == "__main__":
    recorder = EnhancedThoughtActionRecorder()
    
    # 连接到Manus平台
    if recorder.connect():
        print("成功连接到Manus平台")
        
        # 开始记录（持续10秒）
        recorder.start_recording(duration=10)
        
        # 获取统计信息
        stats = recorder.get_statistics()
        print(f"统计信息: {stats}")
        
        # 保存数据
        recorder.save_data("thought_action_test_data.json")
        
        # 断开连接
        recorder.disconnect()
    else:
        print("连接Manus平台失败")
