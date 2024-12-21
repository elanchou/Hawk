import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.market_data_service import MarketDataService
from src.utils.logger import Logger
from src.config.config import Config

logger = Logger(__name__)
config = Config()

async def sync_all_market_data():
    """同步所有市场数据"""
    service = MarketDataService()
    symbols = config.get('api.binance.symbols', ['BTCUSDT'])
    intervals = config.get('api.binance.intervals', ['1m', '5m', '15m'])
    
    for symbol in symbols:
        for interval in intervals:
            logger.info(f"开始同步数据: {symbol} {interval}")
            await service.sync_market_data(symbol, interval)
            logger.info(f"完成同步数据: {symbol} {interval}")

if __name__ == "__main__":
    asyncio.run(sync_all_market_data()) 