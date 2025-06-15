"""
PowerAuto AI Core - 主入口
基于三层架构哲学的智能AI核心系统
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from core.search_engine import SearchEngine
from core.mcp_manager import MCPManager
from core.kilocode_fallback import KiloCodeFallback
from smart_intervention.intervention_engine import InterventionEngine

class PowerAutoAICore:
    """PowerAuto AI Core 主类"""
    
    def __init__(self):
        """初始化AI Core"""
        self.logger = logging.getLogger("PowerAutoAICore")
        
        # 三层架构组件
        self.search_engine = SearchEngine()
        self.mcp_manager = MCPManager()
        self.kilocode_fallback = KiloCodeFallback()
        
        # 智能介入引擎
        self.intervention_engine = InterventionEngine()
        
        self.logger.info("PowerAuto AI Core 初始化完成")
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户请求 - 三层架构核心逻辑
        
        Args:
            request: 用户请求
            context: 上下文信息
            
        Returns:
            处理结果
        """
        self.logger.info(f"处理请求: {request[:100]}...")
        
        try:
            # 第一层：搜索
            search_result = await self.search_engine.search(request, context)
            if search_result.get("success"):
                self.logger.info("搜索层成功处理请求")
                return {
                    "success": True,
                    "result": search_result["result"],
                    "layer": "search",
                    "tool": search_result.get("tool")
                }
            
            # 第二层：MCP
            mcp_result = await self.mcp_manager.process(request, context)
            if mcp_result.get("success"):
                self.logger.info("MCP层成功处理请求")
                return {
                    "success": True,
                    "result": mcp_result["result"],
                    "layer": "mcp",
                    "tool": mcp_result.get("tool")
                }
            
            # 第三层：Kilo Code兜底
            fallback_result = await self.kilocode_fallback.handle(request, context)
            self.logger.info("Kilo Code兜底层处理请求")
            return {
                "success": True,
                "result": fallback_result["result"],
                "layer": "kilocode",
                "tool": "kilocode_fallback"
            }
            
        except Exception as e:
            self.logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer": "error"
            }
    
    async def start_smart_intervention(self):
        """启动智能介入功能"""
        self.logger.info("启动智能介入系统")
        await self.intervention_engine.start()
    
    async def stop_smart_intervention(self):
        """停止智能介入功能"""
        self.logger.info("停止智能介入系统")
        await self.intervention_engine.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "search_engine": self.search_engine.get_status(),
            "mcp_manager": self.mcp_manager.get_status(),
            "kilocode_fallback": self.kilocode_fallback.get_status(),
            "intervention_engine": self.intervention_engine.get_status()
        }

async def main():
    """主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建AI Core实例
    aicore = PowerAutoAICore()
    
    # 启动智能介入
    await aicore.start_smart_intervention()
    
    # 示例请求
    test_requests = [
        "帮我搜索Python异步编程的最佳实践",
        "生成一个用户登录的API接口",
        "分析这段代码的性能问题",
        "创建一个React组件"
    ]
    
    for request in test_requests:
        print(f"\n处理请求: {request}")
        result = await aicore.process_request(request)
        print(f"结果: {result}")
    
    # 保持运行
    print("\nAI Core 运行中... 按 Ctrl+C 退出")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭...")
        await aicore.stop_smart_intervention()

if __name__ == "__main__":
    asyncio.run(main())

