import asyncio
import uvicorn
from datetime import datetime, timedelta
from pathlib import Path
from src.api.main import app
from src.data.collectors.binance_collector import BinanceDataCollector
from backend.src.utils.logger import Logger
from src.config.config import Config
from src.models.database import DatabaseManager
from src.services.market_data_service import MarketDataService

logger = Logger(__name__)
config = Config()

async def init_data_collection():
    """初始化数据收集"""
    try:
        service = MarketDataService()
        symbols = config.get('api.binance.symbols', ['BTCUSDT'])
        intervals = config.get('api.binance.intervals', ['1m', '5m', '15m'])
        
        for symbol in symbols:
            for interval in intervals:
                logger.info(f"初始化 {symbol} {interval} 历史数据")
                await service.sync_market_data(symbol, interval)
                
    except Exception as e:
        logger.error(f"数据收集初始化失败: {e}")

def init_database():
    """初始化数据库"""
    try:
        db = DatabaseManager()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise e

def run():
    """运行应用"""
    # 确保配置文件存在
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        logger.error("配置文件不存在，请复制 config.example.yaml 并修改配置")
        return
    
    # 初始化数据库
    init_database()
    
    # 初始化数据收集
    asyncio.run(init_data_collection())
    
    # 启动API服务
    logger.info("启动API服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    run() 
 