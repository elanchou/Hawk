from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, and_
import math
import pytz

from ..models.database import DatabaseManager, MarketData, DataSyncStatus
from ..data.collectors.binance_collector import BinanceDataCollector
from ..utils.logger import Logger
from ..config.config import Config

logger = Logger(__name__)

class MarketDataService:
    def __init__(self):
        self.db = DatabaseManager()
        self.config = Config()
        self.collector = BinanceDataCollector(
            api_key=self.config.get('api.binance.api_key'),
            api_secret=self.config.get('api.binance.api_secret')
        )
        
        # 每批次同步的天数（币安API限制）
        self.batch_days = 7
        
    async def sync_market_data(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        force_update: bool = False
    ):
        """同步市场数据"""
        try:
            # 使用UTC时间
            now = datetime.now(pytz.UTC)
            
            if not start_time:
                # 获取配置的历史天数
                history_days = self.config.get('data.history_days', 30)
                # 计算开始时间，确保是整天
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=history_days)
                logger.info(f"设置同步历史数据天数: {history_days}天")
            elif not start_time.tzinfo:
                start_time = pytz.UTC.localize(start_time)
            
            if not end_time:
                # 设置结束时间为当前整点
                end_time = now.replace(minute=0, second=0, microsecond=0)
            elif not end_time.tzinfo:
                end_time = pytz.UTC.localize(end_time)
            
            logger.info(f"计划同步时间范围: {start_time} 到 {end_time}")
            logger.info(f"总天数: {(end_time - start_time).days}天")
            
            # 检查数据库中最早的记录
            session = self.db.get_session()
            try:
                earliest_record = session.query(MarketData.timestamp)\
                    .filter(
                        MarketData.symbol == symbol,
                        MarketData.interval == interval
                    )\
                    .order_by(MarketData.timestamp.asc())\
                    .first()
                
                if earliest_record and not force_update:
                    earliest_time = earliest_record[0]
                    if earliest_time.tzinfo:
                        earliest_time = earliest_time.replace(tzinfo=pytz.UTC)
                    else:
                        earliest_time = pytz.UTC.localize(earliest_time)
                    
                    if earliest_time > start_time:
                        logger.info(f"发现历史数据缺口: {start_time} 到 {earliest_time}")
                        await self._sync_data_range(symbol, interval, start_time, earliest_time, force_update)
                    
                    # 同步最新数据
                    latest_record = session.query(MarketData.timestamp)\
                        .filter(
                            MarketData.symbol == symbol,
                            MarketData.interval == interval
                        )\
                        .order_by(MarketData.timestamp.desc())\
                        .first()
                    
                    if latest_record:
                        latest_time = latest_record[0]
                        if latest_time.tzinfo:
                            latest_time = latest_time.replace(tzinfo=pytz.UTC)
                        else:
                            latest_time = pytz.UTC.localize(latest_time)
                        
                        if latest_time < end_time:
                            logger.info(f"同步最新数据: {latest_time} 到 {end_time}")
                            await self._sync_data_range(symbol, interval, latest_time, end_time, force_update)
                else:
                    # 首次同步或强制更新
                    logger.info("开始全量数据同步")
                    await self._sync_data_range(symbol, interval, start_time, end_time, force_update)
                
            finally:
                session.close()
            
        except Exception as e:
            logger.error(f"同步数据失败: {symbol} {interval} - {e}")
            raise e
            
    async def _sync_data_range(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        force_update: bool
    ):
        """同步指定时间范围的数据"""
        total_days = (end_time - start_time).days
        batch_count = math.ceil(total_days / self.batch_days)
        
        logger.info(f"开始同步数据范围: {start_time} 到 {end_time}")
        logger.info(f"总天数: {total_days}天, 分{batch_count}批同步")
        
        current_start = start_time
        for batch in range(batch_count):
            batch_end = min(
                current_start + timedelta(days=self.batch_days),
                end_time
            )
            
            logger.info(f"同步第 {batch + 1}/{batch_count} 批数据")
            logger.info(f"批次时间范围: {current_start} 到 {batch_end}")
            
            await self._sync_batch(
                symbol,
                interval,
                current_start,
                batch_end,
                force_update
            )
            
            current_start = batch_end
    
    async def _sync_batch(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime,
        force_update: bool
    ):
        """同步一批数据"""
        try:
            session = self.db.get_session()
            
            # 获取数据
            data = await self.collector.fetch_historical_data(
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time
            )
            
            if data.empty:
                logger.warning(f"没有新的数据需要同步: {symbol} {interval}")
                return
            
            # 准备数据记录
            records = []
            for index, row in data.iterrows():
                record = {
                    'symbol': symbol,
                    'interval': interval,
                    'timestamp': index,
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row['volume']),
                    'quote_volume': float(row['quote_volume']),
                    'trades_count': int(row['trades']),
                    'taker_buy_volume': float(row['taker_buy_base']),
                    'taker_buy_quote_volume': float(row['taker_buy_quote'])
                }
                records.append(record)
            
            # 使用 upsert 插入数据
            stmt = insert(MarketData).values(records)
            
            if force_update:
                update_cols = {col.name: stmt.excluded[col.name] 
                             for col in MarketData.__table__.columns 
                             if col.name not in ['id', 'symbol', 'interval', 'timestamp']}
                
                stmt = stmt.on_conflict_do_update(
                    constraint='unique_market_data',
                    set_=update_cols
                )
            else:
                stmt = stmt.on_conflict_do_nothing()
            
            session.execute(stmt)
            
            # 更新同步状态
            await self._update_sync_status(
                session,
                symbol,
                interval,
                end_time,
                'success'
            )
            
            session.commit()
            logger.info(f"成功同步 {len(records)} 条数据")
            
        except Exception as e:
            logger.error(f"批次同步失败: {e}")
            if session:
                await self._update_sync_status(
                    session,
                    symbol,
                    interval,
                    start_time,
                    'failed',
                    str(e)
                )
                session.commit()
        finally:
            if session:
                session.close()
    
    async def get_market_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """获取市场数据"""
        session = self.db.get_session()
        try:
            query = select(MarketData).where(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.interval == interval,
                    MarketData.timestamp >= start_time,
                    MarketData.timestamp <= (end_time or datetime.utcnow())
                )
            ).order_by(MarketData.timestamp)
            
            result = session.execute(query)
            records = result.fetchall()
            
            if not records:
                return pd.DataFrame()
            
            df = pd.DataFrame([r._asdict() for r in records])
            df.set_index('timestamp', inplace=True)
            return df
            
        finally:
            session.close()
    
    async def _get_sync_status(
        self,
        session,
        symbol: str,
        interval: str
    ) -> Optional[DataSyncStatus]:
        """获取同步状态"""
        return session.query(DataSyncStatus).filter(
            DataSyncStatus.symbol == symbol,
            DataSyncStatus.interval == interval
        ).first()
    
    async def _update_sync_status(
        self,
        session,
        symbol: str,
        interval: str,
        sync_time: datetime,
        status: str,
        error_message: Optional[str] = None
    ):
        """更新同步状态"""
        next_sync_time = sync_time + self._get_sync_interval(interval)
        
        # 检查是否存在记录
        existing = session.query(DataSyncStatus).filter(
            DataSyncStatus.symbol == symbol,
            DataSyncStatus.interval == interval
        ).first()
        
        if existing:
            # 更新现有记录
            existing.last_sync_time = sync_time
            existing.next_sync_time = next_sync_time
            existing.status = status
            existing.error_message = error_message
        else:
            # 创建新记录
            new_status = DataSyncStatus(
                symbol=symbol,
                interval=interval,
                last_sync_time=sync_time,
                next_sync_time=next_sync_time,
                status=status,
                error_message=error_message
            )
            session.add(new_status)
    
    def _get_sync_interval(self, interval: str) -> timedelta:
        """获取同步间隔"""
        if interval == '1m':
            return timedelta(minutes=1)
        elif interval == '5m':
            return timedelta(minutes=5)
        elif interval == '15m':
            return timedelta(minutes=15)
        elif interval == '30m':
            return timedelta(minutes=30)
        elif interval == '1h':
            return timedelta(hours=1)
        elif interval == '4h':
            return timedelta(hours=4)
        elif interval == '1d':
            return timedelta(days=1)
        else:
            return timedelta(minutes=1)