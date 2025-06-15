#!/usr/bin/env python3
"""
PowerAutomation v0.575 - 視頻驅動測試用例優化系統

核心技術難點2解決方案：
如何利用產生的視頻和工作文本來協助修正及細化，產生更細更正確更多樣的test cases

技術架構：
1. 視頻分析引擎 - 解析執行過程視頻，提取關鍵幀和操作序列
2. 行為識別系統 - 識別用戶操作、系統響應、錯誤狀態等
3. 文本視頻關聯器 - 將工作文本與視頻片段進行時間軸關聯
4. 測試用例細化器 - 基於視頻分析結果優化和生成測試用例
5. 反饋學習機制 - 從視頻驗證結果中學習改進
"""

import os
import cv2
import json
import time
import base64
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import pickle
from collections import defaultdict, deque
import threading
import asyncio
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoEventType(Enum):
    """視頻事件類型"""
    CLICK = "click"                    # 點擊事件
    INPUT = "input"                    # 輸入事件
    SCROLL = "scroll"                  # 滾動事件
    NAVIGATION = "navigation"          # 導航事件
    WAIT = "wait"                      # 等待事件
    ERROR = "error"                    # 錯誤事件
    SUCCESS = "success"                # 成功事件
    VALIDATION = "validation"          # 驗證事件
    SCREENSHOT = "screenshot"          # 截圖事件

class TestCaseType(Enum):
    """測試用例類型"""
    FUNCTIONAL = "functional"          # 功能測試
    UI_INTERACTION = "ui_interaction"  # UI交互測試
    ERROR_HANDLING = "error_handling"  # 錯誤處理測試
    PERFORMANCE = "performance"        # 性能測試
    REGRESSION = "regression"          # 回歸測試
    EDGE_CASE = "edge_case"           # 邊界情況測試

class VideoQuality(Enum):
    """視頻質量等級"""
    HIGH = "high"      # 高質量：清晰、完整、無錯誤
    MEDIUM = "medium"  # 中等質量：基本清晰、大部分完整
    LOW = "low"        # 低質量：模糊、不完整、有錯誤

@dataclass
class VideoFrame:
    """視頻幀數據"""
    frame_id: str
    timestamp: float
    frame_data: np.ndarray
    frame_hash: str
    annotations: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []

@dataclass
class VideoEvent:
    """視頻事件"""
    event_id: str
    event_type: VideoEventType
    timestamp: float
    duration: float
    coordinates: Optional[Tuple[int, int]] = None
    text_content: Optional[str] = None
    element_info: Optional[Dict[str, Any]] = None
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WorkflowStep:
    """工作流步驟"""
    step_id: str
    step_number: int
    description: str
    expected_result: str
    actual_result: Optional[str] = None
    video_events: List[VideoEvent] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    status: str = "pending"  # pending, running, completed, failed
    
    def __post_init__(self):
        if self.video_events is None:
            self.video_events = []

@dataclass
class VideoAnalysisResult:
    """視頻分析結果"""
    video_id: str
    video_path: str
    analysis_timestamp: datetime
    total_duration: float
    frame_count: int
    fps: float
    resolution: Tuple[int, int]
    quality_score: float
    detected_events: List[VideoEvent]
    workflow_steps: List[WorkflowStep]
    error_segments: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    text_video_correlations: List[Dict[str, Any]]
    
class VideoAnalysisEngine:
    """視頻分析引擎"""
    
    def __init__(self):
        self.frame_cache = {}
        self.event_patterns = self._load_event_patterns()
        self.ui_element_detector = UIElementDetector()
        self.text_extractor = VideoTextExtractor()
        
    def _load_event_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加載事件識別模式"""
        return {
            "click_pattern": {
                "color_change_threshold": 30,
                "duration_range": (0.1, 2.0),
                "cursor_movement_threshold": 10
            },
            "input_pattern": {
                "text_change_detection": True,
                "cursor_blink_detection": True,
                "keyboard_activity_threshold": 0.5
            },
            "scroll_pattern": {
                "content_shift_threshold": 20,
                "scroll_bar_detection": True,
                "duration_range": (0.2, 5.0)
            },
            "error_pattern": {
                "error_color_signatures": [(255, 0, 0), (255, 165, 0)],  # 紅色、橙色
                "error_text_keywords": ["error", "錯誤", "失敗", "exception", "failed"],
                "popup_detection": True
            }
        }
    
    def analyze_video(self, video_path: str, workflow_text: str = "") -> VideoAnalysisResult:
        """分析視頻並提取事件"""
        logger.info(f"🎬 開始分析視頻: {video_path}")
        
        # 打開視頻文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"無法打開視頻文件: {video_path}")
        
        # 獲取視頻基本信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_duration = frame_count / fps if fps > 0 else 0
        
        logger.info(f"📊 視頻信息: {width}x{height}, {fps:.2f}fps, {total_duration:.2f}s, {frame_count}幀")
        
        # 分析視頻幀
        frames = self._extract_frames(cap, fps)
        detected_events = self._detect_events(frames, fps)
        workflow_steps = self._correlate_with_workflow(detected_events, workflow_text)
        error_segments = self._detect_error_segments(frames, detected_events)
        performance_metrics = self._calculate_performance_metrics(detected_events, total_duration)
        text_correlations = self._correlate_text_video(workflow_text, detected_events)
        quality_score = self._calculate_video_quality(frames, detected_events)
        
        cap.release()
        
        # 創建分析結果
        result = VideoAnalysisResult(
            video_id=hashlib.md5(video_path.encode()).hexdigest()[:12],
            video_path=video_path,
            analysis_timestamp=datetime.now(),
            total_duration=total_duration,
            frame_count=frame_count,
            fps=fps,
            resolution=(width, height),
            quality_score=quality_score,
            detected_events=detected_events,
            workflow_steps=workflow_steps,
            error_segments=error_segments,
            performance_metrics=performance_metrics,
            text_video_correlations=text_correlations
        )
        
        logger.info(f"✅ 視頻分析完成，檢測到 {len(detected_events)} 個事件")
        return result
    
    def _extract_frames(self, cap: cv2.VideoCapture, fps: float) -> List[VideoFrame]:
        """提取關鍵幀"""
        frames = []
        frame_id = 0
        
        # 每秒提取2-4幀，根據fps調整
        sample_rate = max(1, int(fps / 3))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_id % sample_rate == 0:
                timestamp = frame_id / fps
                frame_hash = hashlib.md5(frame.tobytes()).hexdigest()[:16]
                
                video_frame = VideoFrame(
                    frame_id=f"frame_{frame_id:06d}",
                    timestamp=timestamp,
                    frame_data=frame.copy(),
                    frame_hash=frame_hash
                )
                frames.append(video_frame)
            
            frame_id += 1
        
        logger.info(f"📸 提取了 {len(frames)} 個關鍵幀")
        return frames
    
    def _detect_events(self, frames: List[VideoFrame], fps: float) -> List[VideoEvent]:
        """檢測視頻事件"""
        events = []
        
        for i in range(1, len(frames)):
            prev_frame = frames[i-1]
            curr_frame = frames[i]
            
            # 檢測點擊事件
            click_events = self._detect_click_events(prev_frame, curr_frame)
            events.extend(click_events)
            
            # 檢測輸入事件
            input_events = self._detect_input_events(prev_frame, curr_frame)
            events.extend(input_events)
            
            # 檢測滾動事件
            scroll_events = self._detect_scroll_events(prev_frame, curr_frame)
            events.extend(scroll_events)
            
            # 檢測錯誤事件
            error_events = self._detect_error_events(prev_frame, curr_frame)
            events.extend(error_events)
            
            # 檢測導航事件
            nav_events = self._detect_navigation_events(prev_frame, curr_frame)
            events.extend(nav_events)
        
        # 按時間排序事件
        events.sort(key=lambda e: e.timestamp)
        
        logger.info(f"🔍 檢測到 {len(events)} 個事件")
        return events
    
    def _detect_click_events(self, prev_frame: VideoFrame, curr_frame: VideoFrame) -> List[VideoEvent]:
        """檢測點擊事件"""
        events = []
        
        # 計算幀差異
        diff = cv2.absdiff(prev_frame.frame_data, curr_frame.frame_data)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # 查找顯著變化區域
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 5000:  # 點擊區域大小範圍
                # 獲取邊界框
                x, y, w, h = cv2.boundingRect(contour)
                center_x, center_y = x + w//2, y + h//2
                
                # 檢查是否為點擊模式
                if self._is_click_pattern(prev_frame.frame_data, curr_frame.frame_data, (center_x, center_y)):
                    event = VideoEvent(
                        event_id=f"click_{curr_frame.frame_id}_{center_x}_{center_y}",
                        event_type=VideoEventType.CLICK,
                        timestamp=curr_frame.timestamp,
                        duration=curr_frame.timestamp - prev_frame.timestamp,
                        coordinates=(center_x, center_y),
                        confidence=0.7,
                        metadata={"area": area, "contour_points": len(contour)}
                    )
                    events.append(event)
        
        return events
    
    def _detect_input_events(self, prev_frame: VideoFrame, curr_frame: VideoFrame) -> List[VideoEvent]:
        """檢測輸入事件"""
        events = []
        
        # 提取文本區域
        prev_text = self.text_extractor.extract_text(prev_frame.frame_data)
        curr_text = self.text_extractor.extract_text(curr_frame.frame_data)
        
        # 比較文本變化
        if prev_text != curr_text:
            # 找出變化的文本區域
            text_changes = self._find_text_changes(prev_text, curr_text)
            
            for change in text_changes:
                event = VideoEvent(
                    event_id=f"input_{curr_frame.frame_id}_{change['position']}",
                    event_type=VideoEventType.INPUT,
                    timestamp=curr_frame.timestamp,
                    duration=curr_frame.timestamp - prev_frame.timestamp,
                    text_content=change['new_text'],
                    coordinates=change.get('coordinates'),
                    confidence=0.8,
                    metadata={"change_type": change['type'], "old_text": change['old_text']}
                )
                events.append(event)
        
        return events
    
    def _detect_scroll_events(self, prev_frame: VideoFrame, curr_frame: VideoFrame) -> List[VideoEvent]:
        """檢測滾動事件"""
        events = []
        
        # 檢測垂直內容移動
        prev_gray = cv2.cvtColor(prev_frame.frame_data, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame.frame_data, cv2.COLOR_BGR2GRAY)
        
        # 使用光流檢測運動
        flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
        
        if flow is not None:
            # 分析運動向量
            vertical_movement = self._analyze_vertical_movement(flow)
            
            if abs(vertical_movement) > 20:  # 滾動閾值
                direction = "down" if vertical_movement > 0 else "up"
                
                event = VideoEvent(
                    event_id=f"scroll_{curr_frame.frame_id}_{direction}",
                    event_type=VideoEventType.SCROLL,
                    timestamp=curr_frame.timestamp,
                    duration=curr_frame.timestamp - prev_frame.timestamp,
                    confidence=0.6,
                    metadata={"direction": direction, "distance": abs(vertical_movement)}
                )
                events.append(event)
        
        return events
    
    def _detect_error_events(self, prev_frame: VideoFrame, curr_frame: VideoFrame) -> List[VideoEvent]:
        """檢測錯誤事件"""
        events = []
        
        # 檢測錯誤顏色特徵
        error_regions = self._detect_error_colors(curr_frame.frame_data)
        
        # 檢測錯誤文本
        frame_text = self.text_extractor.extract_text(curr_frame.frame_data)
        error_texts = self._detect_error_text(frame_text)
        
        # 檢測彈窗
        popup_detected = self._detect_popup(prev_frame.frame_data, curr_frame.frame_data)
        
        if error_regions or error_texts or popup_detected:
            event = VideoEvent(
                event_id=f"error_{curr_frame.frame_id}",
                event_type=VideoEventType.ERROR,
                timestamp=curr_frame.timestamp,
                duration=curr_frame.timestamp - prev_frame.timestamp,
                text_content="; ".join(error_texts) if error_texts else None,
                confidence=0.8,
                metadata={
                    "error_regions": len(error_regions),
                    "error_texts": error_texts,
                    "popup_detected": popup_detected
                }
            )
            events.append(event)
        
        return events
    
    def _detect_navigation_events(self, prev_frame: VideoFrame, curr_frame: VideoFrame) -> List[VideoEvent]:
        """檢測導航事件"""
        events = []
        
        # 檢測URL變化（如果有地址欄）
        prev_text = self.text_extractor.extract_text(prev_frame.frame_data)
        curr_text = self.text_extractor.extract_text(curr_frame.frame_data)
        
        # 簡單的URL檢測
        prev_urls = self._extract_urls(prev_text)
        curr_urls = self._extract_urls(curr_text)
        
        if prev_urls != curr_urls:
            event = VideoEvent(
                event_id=f"nav_{curr_frame.frame_id}",
                event_type=VideoEventType.NAVIGATION,
                timestamp=curr_frame.timestamp,
                duration=curr_frame.timestamp - prev_frame.timestamp,
                confidence=0.7,
                metadata={"prev_urls": prev_urls, "curr_urls": curr_urls}
            )
            events.append(event)
        
        return events
    
    def _is_click_pattern(self, prev_frame: np.ndarray, curr_frame: np.ndarray, 
                         coordinates: Tuple[int, int]) -> bool:
        """判斷是否為點擊模式"""
        x, y = coordinates
        
        # 檢查點擊區域的顏色變化
        region_size = 20
        x1, y1 = max(0, x-region_size), max(0, y-region_size)
        x2, y2 = min(prev_frame.shape[1], x+region_size), min(prev_frame.shape[0], y+region_size)
        
        prev_region = prev_frame[y1:y2, x1:x2]
        curr_region = curr_frame[y1:y2, x1:x2]
        
        if prev_region.size == 0 or curr_region.size == 0:
            return False
        
        # 計算顏色差異
        color_diff = np.mean(cv2.absdiff(prev_region, curr_region))
        
        return color_diff > 30  # 顏色變化閾值
    
    def _find_text_changes(self, prev_text: str, curr_text: str) -> List[Dict[str, Any]]:
        """找出文本變化"""
        changes = []
        
        # 簡單的文本差異檢測
        if len(curr_text) > len(prev_text):
            # 文本增加
            new_text = curr_text[len(prev_text):]
            changes.append({
                "type": "addition",
                "old_text": prev_text,
                "new_text": new_text,
                "position": len(prev_text)
            })
        elif len(curr_text) < len(prev_text):
            # 文本刪除
            changes.append({
                "type": "deletion",
                "old_text": prev_text[len(curr_text):],
                "new_text": "",
                "position": len(curr_text)
            })
        elif prev_text != curr_text:
            # 文本修改
            changes.append({
                "type": "modification",
                "old_text": prev_text,
                "new_text": curr_text,
                "position": 0
            })
        
        return changes
    
    def _analyze_vertical_movement(self, flow) -> float:
        """分析垂直運動"""
        # 這裡需要實際的光流分析實現
        # 簡化版本：返回隨機值模擬
        return np.random.uniform(-50, 50)
    
    def _detect_error_colors(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """檢測錯誤顏色"""
        error_regions = []
        
        # 檢測紅色區域
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 紅色範圍
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # 最小錯誤區域大小
                x, y, w, h = cv2.boundingRect(contour)
                error_regions.append({
                    "color": "red",
                    "area": area,
                    "bbox": (x, y, w, h)
                })
        
        return error_regions
    
    def _detect_error_text(self, text: str) -> List[str]:
        """檢測錯誤文本"""
        error_keywords = [
            "error", "錯誤", "失敗", "exception", "failed", "invalid", 
            "無效", "不正確", "timeout", "超時", "denied", "拒絕"
        ]
        
        found_errors = []
        text_lower = text.lower()
        
        for keyword in error_keywords:
            if keyword in text_lower:
                found_errors.append(keyword)
        
        return found_errors
    
    def _detect_popup(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> bool:
        """檢測彈窗"""
        # 簡單的彈窗檢測：檢查是否有新的矩形區域出現
        diff = cv2.absdiff(prev_frame, curr_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        _, thresh = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # 彈窗最小大小
                # 檢查是否為矩形
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                if len(approx) == 4:  # 矩形
                    return True
        
        return False
    
    def _extract_urls(self, text: str) -> List[str]:
        """提取URL"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def _correlate_with_workflow(self, events: List[VideoEvent], workflow_text: str) -> List[WorkflowStep]:
        """與工作流文本關聯"""
        steps = []
        
        # 解析工作流文本
        workflow_lines = workflow_text.split('\n')
        step_descriptions = [line.strip() for line in workflow_lines if line.strip()]
        
        # 將事件分組到步驟中
        events_per_step = len(events) // max(len(step_descriptions), 1) if step_descriptions else len(events)
        
        for i, description in enumerate(step_descriptions):
            start_idx = i * events_per_step
            end_idx = min((i + 1) * events_per_step, len(events))
            step_events = events[start_idx:end_idx]
            
            step = WorkflowStep(
                step_id=f"step_{i+1:03d}",
                step_number=i + 1,
                description=description,
                expected_result="步驟成功完成",
                video_events=step_events,
                start_time=step_events[0].timestamp if step_events else None,
                end_time=step_events[-1].timestamp if step_events else None,
                status="completed" if step_events else "pending"
            )
            steps.append(step)
        
        return steps
    
    def _detect_error_segments(self, frames: List[VideoFrame], events: List[VideoEvent]) -> List[Dict[str, Any]]:
        """檢測錯誤片段"""
        error_segments = []
        
        error_events = [e for e in events if e.event_type == VideoEventType.ERROR]
        
        for error_event in error_events:
            segment = {
                "start_time": error_event.timestamp,
                "end_time": error_event.timestamp + error_event.duration,
                "error_type": "unknown",
                "description": error_event.text_content or "檢測到錯誤",
                "confidence": error_event.confidence
            }
            error_segments.append(segment)
        
        return error_segments
    
    def _calculate_performance_metrics(self, events: List[VideoEvent], total_duration: float) -> Dict[str, float]:
        """計算性能指標"""
        metrics = {
            "total_events": len(events),
            "events_per_second": len(events) / total_duration if total_duration > 0 else 0,
            "click_events": len([e for e in events if e.event_type == VideoEventType.CLICK]),
            "input_events": len([e for e in events if e.event_type == VideoEventType.INPUT]),
            "error_events": len([e for e in events if e.event_type == VideoEventType.ERROR]),
            "average_event_duration": np.mean([e.duration for e in events]) if events else 0,
            "error_rate": len([e for e in events if e.event_type == VideoEventType.ERROR]) / len(events) if events else 0
        }
        
        return metrics
    
    def _correlate_text_video(self, workflow_text: str, events: List[VideoEvent]) -> List[Dict[str, Any]]:
        """關聯文本和視頻"""
        correlations = []
        
        # 簡單的關聯：基於關鍵詞匹配
        text_keywords = workflow_text.lower().split()
        
        for event in events:
            if event.text_content:
                event_keywords = event.text_content.lower().split()
                common_keywords = set(text_keywords) & set(event_keywords)
                
                if common_keywords:
                    correlation = {
                        "event_id": event.event_id,
                        "timestamp": event.timestamp,
                        "common_keywords": list(common_keywords),
                        "correlation_score": len(common_keywords) / max(len(text_keywords), len(event_keywords))
                    }
                    correlations.append(correlation)
        
        return correlations
    
    def _calculate_video_quality(self, frames: List[VideoFrame], events: List[VideoEvent]) -> float:
        """計算視頻質量評分"""
        quality_score = 0.0
        
        # 基於幀數量評分 (30%)
        frame_score = min(len(frames) / 100, 1.0)  # 100幀為滿分
        quality_score += frame_score * 0.3
        
        # 基於事件檢測評分 (40%)
        event_score = min(len(events) / 20, 1.0)  # 20個事件為滿分
        quality_score += event_score * 0.4
        
        # 基於錯誤率評分 (30%)
        error_events = [e for e in events if e.event_type == VideoEventType.ERROR]
        error_rate = len(error_events) / len(events) if events else 0
        error_score = max(0, 1.0 - error_rate * 2)  # 錯誤率越低分數越高
        quality_score += error_score * 0.3
        
        return min(quality_score, 1.0)

class UIElementDetector:
    """UI元素檢測器"""
    
    def __init__(self):
        self.element_templates = self._load_element_templates()
    
    def _load_element_templates(self) -> Dict[str, Any]:
        """加載UI元素模板"""
        return {
            "button": {"min_area": 500, "aspect_ratio_range": (0.2, 5.0)},
            "input_field": {"min_area": 1000, "aspect_ratio_range": (2.0, 20.0)},
            "dropdown": {"min_area": 800, "aspect_ratio_range": (1.0, 10.0)},
            "checkbox": {"min_area": 100, "aspect_ratio_range": (0.8, 1.2)},
            "link": {"color_signature": (0, 0, 255), "underline_detection": True}
        }
    
    def detect_elements(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """檢測UI元素"""
        elements = []
        
        # 這裡應該實現實際的UI元素檢測算法
        # 簡化版本：返回模擬數據
        elements.append({
            "type": "button",
            "bbox": (100, 200, 80, 30),
            "confidence": 0.8,
            "text": "Submit"
        })
        
        return elements

class VideoTextExtractor:
    """視頻文本提取器"""
    
    def __init__(self):
        # 這裡可以初始化OCR引擎，如pytesseract
        pass
    
    def extract_text(self, frame: np.ndarray) -> str:
        """從幀中提取文本"""
        # 簡化版本：返回模擬文本
        # 實際實現應該使用OCR技術
        return f"Frame text at {time.time()}"

class TestCaseRefinementEngine:
    """測試用例細化引擎"""
    
    def __init__(self):
        self.refinement_strategies = self._load_refinement_strategies()
        self.pattern_analyzer = TestPatternAnalyzer()
    
    def _load_refinement_strategies(self) -> Dict[str, Any]:
        """加載細化策略"""
        return {
            "event_based_refinement": self._refine_by_events,
            "error_based_refinement": self._refine_by_errors,
            "performance_based_refinement": self._refine_by_performance,
            "workflow_based_refinement": self._refine_by_workflow
        }
    
    def refine_test_cases(self, video_analysis: VideoAnalysisResult, 
                         original_test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基於視頻分析結果細化測試用例"""
        logger.info(f"🔧 開始細化測試用例，原始用例數: {len(original_test_cases)}")
        
        refined_cases = []
        
        # 基於檢測到的事件細化
        event_refined_cases = self._refine_by_events(video_analysis, original_test_cases)
        refined_cases.extend(event_refined_cases)
        
        # 基於錯誤片段細化
        error_refined_cases = self._refine_by_errors(video_analysis, original_test_cases)
        refined_cases.extend(error_refined_cases)
        
        # 基於性能指標細化
        performance_refined_cases = self._refine_by_performance(video_analysis, original_test_cases)
        refined_cases.extend(performance_refined_cases)
        
        # 基於工作流步驟細化
        workflow_refined_cases = self._refine_by_workflow(video_analysis, original_test_cases)
        refined_cases.extend(workflow_refined_cases)
        
        # 去重和質量評估
        unique_cases = self._deduplicate_test_cases(refined_cases)
        quality_scored_cases = self._score_test_cases(unique_cases, video_analysis)
        
        logger.info(f"✅ 測試用例細化完成，生成 {len(quality_scored_cases)} 個優化用例")
        return quality_scored_cases
    
    def _refine_by_events(self, video_analysis: VideoAnalysisResult, 
                         original_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基於事件細化測試用例"""
        refined_cases = []
        
        for event in video_analysis.detected_events:
            if event.event_type == VideoEventType.CLICK:
                # 為每個點擊事件生成測試用例
                test_case = {
                    "id": f"click_test_{event.event_id}",
                    "type": TestCaseType.UI_INTERACTION.value,
                    "title": f"點擊測試 - 座標({event.coordinates[0]}, {event.coordinates[1]})",
                    "description": f"測試在座標({event.coordinates[0]}, {event.coordinates[1]})的點擊操作",
                    "steps": [
                        f"1. 導航到目標頁面",
                        f"2. 點擊座標({event.coordinates[0]}, {event.coordinates[1]})",
                        f"3. 驗證點擊響應"
                    ],
                    "expected_result": "點擊操作成功執行，系統正確響應",
                    "video_timestamp": event.timestamp,
                    "confidence": event.confidence,
                    "source": "video_event_analysis",
                    "metadata": {
                        "event_type": event.event_type.value,
                        "coordinates": event.coordinates,
                        "duration": event.duration
                    }
                }
                refined_cases.append(test_case)
            
            elif event.event_type == VideoEventType.INPUT:
                # 為輸入事件生成測試用例
                test_case = {
                    "id": f"input_test_{event.event_id}",
                    "type": TestCaseType.FUNCTIONAL.value,
                    "title": f"輸入測試 - {event.text_content[:20]}...",
                    "description": f"測試輸入內容: {event.text_content}",
                    "steps": [
                        f"1. 定位輸入字段",
                        f"2. 輸入內容: {event.text_content}",
                        f"3. 驗證輸入結果"
                    ],
                    "expected_result": "輸入內容正確顯示和處理",
                    "video_timestamp": event.timestamp,
                    "confidence": event.confidence,
                    "source": "video_event_analysis",
                    "test_data": {"input_text": event.text_content},
                    "metadata": {
                        "event_type": event.event_type.value,
                        "text_content": event.text_content
                    }
                }
                refined_cases.append(test_case)
        
        return refined_cases
    
    def _refine_by_errors(self, video_analysis: VideoAnalysisResult, 
                         original_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基於錯誤細化測試用例"""
        refined_cases = []
        
        for error_segment in video_analysis.error_segments:
            test_case = {
                "id": f"error_test_{hash(error_segment['description'])}",
                "type": TestCaseType.ERROR_HANDLING.value,
                "title": f"錯誤處理測試 - {error_segment['description']}",
                "description": f"測試錯誤情況的處理: {error_segment['description']}",
                "steps": [
                    "1. 重現導致錯誤的操作序列",
                    "2. 觀察錯誤的顯示和處理",
                    "3. 驗證錯誤恢復機制"
                ],
                "expected_result": "系統正確顯示錯誤信息並提供恢復選項",
                "video_timestamp": error_segment['start_time'],
                "confidence": error_segment['confidence'],
                "source": "video_error_analysis",
                "priority": "high",
                "metadata": {
                    "error_type": error_segment['error_type'],
                    "error_duration": error_segment['end_time'] - error_segment['start_time']
                }
            }
            refined_cases.append(test_case)
        
        return refined_cases
    
    def _refine_by_performance(self, video_analysis: VideoAnalysisResult, 
                              original_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基於性能指標細化測試用例"""
        refined_cases = []
        
        metrics = video_analysis.performance_metrics
        
        # 如果事件密度過高，生成性能測試用例
        if metrics.get('events_per_second', 0) > 2:
            test_case = {
                "id": "performance_high_activity",
                "type": TestCaseType.PERFORMANCE.value,
                "title": "高活動密度性能測試",
                "description": f"測試高活動密度下的系統性能 ({metrics['events_per_second']:.2f} 事件/秒)",
                "steps": [
                    "1. 執行高頻率操作序列",
                    "2. 監控系統響應時間",
                    "3. 驗證系統穩定性"
                ],
                "expected_result": "系統在高活動密度下保持穩定性能",
                "confidence": 0.7,
                "source": "video_performance_analysis",
                "metadata": {
                    "events_per_second": metrics['events_per_second'],
                    "total_events": metrics['total_events']
                }
            }
            refined_cases.append(test_case)
        
        # 如果平均事件持續時間過長，生成響應時間測試
        if metrics.get('average_event_duration', 0) > 2:
            test_case = {
                "id": "performance_response_time",
                "type": TestCaseType.PERFORMANCE.value,
                "title": "響應時間測試",
                "description": f"測試系統響應時間 (平均: {metrics['average_event_duration']:.2f}秒)",
                "steps": [
                    "1. 執行標準操作序列",
                    "2. 測量每個操作的響應時間",
                    "3. 驗證響應時間在可接受範圍內"
                ],
                "expected_result": "所有操作響應時間在2秒內",
                "confidence": 0.8,
                "source": "video_performance_analysis",
                "metadata": {
                    "average_duration": metrics['average_event_duration']
                }
            }
            refined_cases.append(test_case)
        
        return refined_cases
    
    def _refine_by_workflow(self, video_analysis: VideoAnalysisResult, 
                           original_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """基於工作流步驟細化測試用例"""
        refined_cases = []
        
        for step in video_analysis.workflow_steps:
            if step.video_events:
                test_case = {
                    "id": f"workflow_step_{step.step_id}",
                    "type": TestCaseType.FUNCTIONAL.value,
                    "title": f"工作流步驟測試 - {step.description[:30]}...",
                    "description": f"測試工作流步驟: {step.description}",
                    "steps": [
                        f"1. 準備步驟前置條件",
                        f"2. 執行步驟: {step.description}",
                        f"3. 驗證步驟結果: {step.expected_result}"
                    ],
                    "expected_result": step.expected_result,
                    "video_timestamp": step.start_time,
                    "confidence": 0.8,
                    "source": "video_workflow_analysis",
                    "metadata": {
                        "step_number": step.step_number,
                        "step_duration": (step.end_time - step.start_time) if step.end_time and step.start_time else 0,
                        "event_count": len(step.video_events)
                    }
                }
                refined_cases.append(test_case)
        
        return refined_cases
    
    def _deduplicate_test_cases(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重測試用例"""
        unique_cases = []
        seen_descriptions = set()
        
        for case in test_cases:
            description_hash = hashlib.md5(case['description'].encode()).hexdigest()
            if description_hash not in seen_descriptions:
                seen_descriptions.add(description_hash)
                unique_cases.append(case)
        
        logger.info(f"🔄 去重後保留 {len(unique_cases)} 個唯一測試用例")
        return unique_cases
    
    def _score_test_cases(self, test_cases: List[Dict[str, Any]], 
                         video_analysis: VideoAnalysisResult) -> List[Dict[str, Any]]:
        """為測試用例評分"""
        for case in test_cases:
            score = 0.0
            
            # 基於信心度評分 (40%)
            confidence = case.get('confidence', 0.5)
            score += confidence * 0.4
            
            # 基於視頻質量評分 (30%)
            score += video_analysis.quality_score * 0.3
            
            # 基於測試類型重要性評分 (30%)
            type_weights = {
                TestCaseType.ERROR_HANDLING.value: 1.0,
                TestCaseType.FUNCTIONAL.value: 0.8,
                TestCaseType.UI_INTERACTION.value: 0.7,
                TestCaseType.PERFORMANCE.value: 0.6,
                TestCaseType.REGRESSION.value: 0.5
            }
            type_weight = type_weights.get(case.get('type', ''), 0.5)
            score += type_weight * 0.3
            
            case['quality_score'] = min(score, 1.0)
        
        # 按質量評分排序
        test_cases.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return test_cases

class TestPatternAnalyzer:
    """測試模式分析器"""
    
    def __init__(self):
        self.learned_patterns = {}
    
    def analyze_patterns(self, video_analysis: VideoAnalysisResult) -> Dict[str, Any]:
        """分析測試模式"""
        patterns = {
            "interaction_patterns": self._analyze_interaction_patterns(video_analysis.detected_events),
            "error_patterns": self._analyze_error_patterns(video_analysis.error_segments),
            "timing_patterns": self._analyze_timing_patterns(video_analysis.detected_events),
            "workflow_patterns": self._analyze_workflow_patterns(video_analysis.workflow_steps)
        }
        
        return patterns
    
    def _analyze_interaction_patterns(self, events: List[VideoEvent]) -> Dict[str, Any]:
        """分析交互模式"""
        click_events = [e for e in events if e.event_type == VideoEventType.CLICK]
        input_events = [e for e in events if e.event_type == VideoEventType.INPUT]
        
        return {
            "click_frequency": len(click_events),
            "input_frequency": len(input_events),
            "click_input_ratio": len(click_events) / max(len(input_events), 1),
            "common_coordinates": self._find_common_coordinates(click_events)
        }
    
    def _analyze_error_patterns(self, error_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析錯誤模式"""
        return {
            "error_frequency": len(error_segments),
            "average_error_duration": np.mean([seg['end_time'] - seg['start_time'] for seg in error_segments]) if error_segments else 0,
            "error_types": [seg['error_type'] for seg in error_segments]
        }
    
    def _analyze_timing_patterns(self, events: List[VideoEvent]) -> Dict[str, Any]:
        """分析時間模式"""
        if not events:
            return {}
        
        intervals = []
        for i in range(1, len(events)):
            interval = events[i].timestamp - events[i-1].timestamp
            intervals.append(interval)
        
        return {
            "average_interval": np.mean(intervals) if intervals else 0,
            "min_interval": np.min(intervals) if intervals else 0,
            "max_interval": np.max(intervals) if intervals else 0,
            "interval_variance": np.var(intervals) if intervals else 0
        }
    
    def _analyze_workflow_patterns(self, workflow_steps: List[WorkflowStep]) -> Dict[str, Any]:
        """分析工作流模式"""
        return {
            "total_steps": len(workflow_steps),
            "completed_steps": len([s for s in workflow_steps if s.status == "completed"]),
            "average_step_duration": np.mean([
                (s.end_time - s.start_time) for s in workflow_steps 
                if s.start_time and s.end_time
            ]) if workflow_steps else 0
        }
    
    def _find_common_coordinates(self, click_events: List[VideoEvent]) -> List[Tuple[int, int]]:
        """找出常見的點擊座標"""
        coordinates = [e.coordinates for e in click_events if e.coordinates]
        
        # 簡單的聚類：找出距離較近的座標
        common_coords = []
        threshold = 50  # 像素距離閾值
        
        for coord in coordinates:
            is_common = False
            for common_coord in common_coords:
                distance = np.sqrt((coord[0] - common_coord[0])**2 + (coord[1] - common_coord[1])**2)
                if distance < threshold:
                    is_common = True
                    break
            
            if not is_common:
                common_coords.append(coord)
        
        return common_coords

# 測試函數
def test_video_driven_optimization():
    """測試視頻驅動測試用例優化系統"""
    print("🎬 測試視頻驅動測試用例優化系統")
    print("=" * 80)
    
    # 創建模擬視頻分析結果
    mock_events = [
        VideoEvent(
            event_id="click_001",
            event_type=VideoEventType.CLICK,
            timestamp=1.5,
            duration=0.2,
            coordinates=(300, 200),
            confidence=0.8
        ),
        VideoEvent(
            event_id="input_001",
            event_type=VideoEventType.INPUT,
            timestamp=3.0,
            duration=2.0,
            text_content="test@example.com",
            confidence=0.9
        ),
        VideoEvent(
            event_id="error_001",
            event_type=VideoEventType.ERROR,
            timestamp=6.0,
            duration=1.0,
            text_content="Invalid password",
            confidence=0.85
        )
    ]
    
    mock_workflow_steps = [
        WorkflowStep(
            step_id="step_001",
            step_number=1,
            description="輸入用戶名",
            expected_result="用戶名正確輸入",
            video_events=[mock_events[1]],
            start_time=2.5,
            end_time=5.0,
            status="completed"
        )
    ]
    
    mock_analysis = VideoAnalysisResult(
        video_id="test_video_001",
        video_path="/path/to/test_video.mp4",
        analysis_timestamp=datetime.now(),
        total_duration=10.0,
        frame_count=300,
        fps=30.0,
        resolution=(1920, 1080),
        quality_score=0.75,
        detected_events=mock_events,
        workflow_steps=mock_workflow_steps,
        error_segments=[{
            "start_time": 6.0,
            "end_time": 7.0,
            "error_type": "authentication_error",
            "description": "Invalid password",
            "confidence": 0.85
        }],
        performance_metrics={
            "total_events": 3,
            "events_per_second": 0.3,
            "average_event_duration": 1.07,
            "error_rate": 0.33
        },
        text_video_correlations=[]
    )
    
    # 創建原始測試用例
    original_test_cases = [
        {
            "id": "original_001",
            "type": "functional",
            "title": "用戶登錄測試",
            "description": "測試用戶登錄功能",
            "steps": ["1. 輸入用戶名", "2. 輸入密碼", "3. 點擊登錄"],
            "expected_result": "成功登錄"
        }
    ]
    
    # 測試細化引擎
    refinement_engine = TestCaseRefinementEngine()
    
    print("\n🔧 開始測試用例細化")
    print("-" * 60)
    
    refined_cases = refinement_engine.refine_test_cases(mock_analysis, original_test_cases)
    
    print(f"✅ 測試用例細化完成")
    print(f"📊 原始測試用例數: {len(original_test_cases)}")
    print(f"🔧 細化後測試用例數: {len(refined_cases)}")
    
    # 顯示細化結果
    print(f"\n📋 細化後的測試用例:")
    print("-" * 60)
    
    for i, case in enumerate(refined_cases[:5]):  # 只顯示前5個
        print(f"{i+1}. {case['title']}")
        print(f"   類型: {case['type']}")
        print(f"   質量評分: {case.get('quality_score', 0):.2f}")
        print(f"   來源: {case.get('source', 'unknown')}")
        if 'video_timestamp' in case:
            print(f"   視頻時間戳: {case['video_timestamp']:.2f}s")
        print()
    
    # 測試模式分析
    pattern_analyzer = TestPatternAnalyzer()
    patterns = pattern_analyzer.analyze_patterns(mock_analysis)
    
    print(f"📊 模式分析結果:")
    print("-" * 60)
    print(f"交互模式: {patterns['interaction_patterns']}")
    print(f"錯誤模式: {patterns['error_patterns']}")
    print(f"時間模式: {patterns['timing_patterns']}")
    
    print("\n🎉 視頻驅動測試用例優化系統測試完成！")
    
    return {
        "original_cases": original_test_cases,
        "refined_cases": refined_cases,
        "analysis_result": mock_analysis,
        "patterns": patterns
    }

if __name__ == "__main__":
    test_video_driven_optimization()

