"""
智能介入系统主入口
"""

import asyncio
import logging
from smart_intervention.intervention_engine import InterventionEngine

async def main():
    """智能介入系统主函数"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("SmartIntervention")
    logger.info("启动智能介入系统")
    
    # 创建智能介入引擎
    engine = InterventionEngine()
    
    try:
        # 启动引擎
        await engine.start()
        
        # 保持运行
        logger.info("智能介入系统运行中... 按 Ctrl+C 退出")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到退出信号")
    except Exception as e:
        logger.error(f"系统错误: {e}")
    finally:
        # 停止引擎
        await engine.stop()
        logger.info("智能介入系统已退出")

if __name__ == "__main__":
    asyncio.run(main())

