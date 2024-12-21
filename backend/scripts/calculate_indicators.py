import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import click

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.technical_analysis_service import TechnicalAnalysisService
from backend.src.utils.logger import Logger
from src.config.config import Config

logger = Logger(__name__)
config = Config()

@click.command()
@click.option('--symbol', default='BTCUSDT', help='交易对')
@click.option('--interval', default='1m', help='时间间隔')
@click.option('--days', default=30, help='计算天数')
@click.option('--force', is_flag=True, help='强制更新')
async def calculate_indicators(symbol: str, interval: str, days: int, force: bool):
    """计算技术指标"""
    service = TechnicalAnalysisService()
    start_time = datetime.utcnow() - timedelta(days=days)
    
    logger.info(f"开始计算技术指标: {symbol} {interval} (过去 {days} 天)")
    await service.calculate_indicators(
        symbol=symbol,
        interval=interval,
        start_time=start_time,
        force_update=force
    )
    logger.info("计算完成")

if __name__ == "__main__":
    asyncio.run(calculate_indicators()) 