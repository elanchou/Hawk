from typing import Dict, Optional, List, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
from .base_collector import BaseDataCollector
import pytz
from ...utils.logger import Logger

logger = Logger(__name__)

class BinanceDataCollector(BaseDataCollector):
    """币安数据采集器"""
    
    INTERVALS = {
        '1m': Client.KLINE_INTERVAL_1MINUTE,
        '5m': Client.KLINE_INTERVAL_5MINUTE,
        '15m': Client.KLINE_INTERVAL_15MINUTE,
        '30m': Client.KLINE_INTERVAL_30MINUTE,
        '1h': Client.KLINE_INTERVAL_1HOUR,
        '4h': Client.KLINE_INTERVAL_4HOUR,
        '1d': Client.KLINE_INTERVAL_1DAY,
    }
    
    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.client = Client(api_key, api_secret)
        self.cache = {}  # 简单的数据缓存
        
        # 时间间隔映射到毫秒
        self.interval_ms = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
        }
        
        # 每个间隔的最大数据点数量
        self.max_limit = 1000
    
    def _format_kline_data(self, klines: List) -> pd.DataFrame:
        """格式化K线数据"""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 
            'volume', 'close_time', 'quote_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        # 转换数据类型
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 
                         'quote_volume', 'trades', 'taker_buy_base', 
                         'taker_buy_quote']
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df.set_index('timestamp')
        
    async def fetch_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime = None
    ) -> pd.DataFrame:
        """获取历史K线数据"""
        try:
            if not end_time:
                end_time = datetime.now(pytz.UTC)
            
            # 确保时间戳是UTC时间
            if not start_time.tzinfo:
                start_time = pytz.UTC.localize(start_time)
            if not end_time.tzinfo:
                end_time = pytz.UTC.localize(end_time)
            
            # 转换为毫秒时间戳
            start_ts = int(start_time.timestamp() * 1000)
            end_ts = int(end_time.timestamp() * 1000)
            
            # 计算需要获取的数据点数量
            interval_ms = self.interval_ms[interval]
            total_points = (end_ts - start_ts) // interval_ms
            
            logger.info(f"开始获取数据: {symbol} {interval}")
            logger.info(f"时间范围: {start_time} 到 {end_time}")
            logger.info(f"预计数据点数: {total_points}")
            
            all_klines = []
            current_start = start_ts
            
            while current_start < end_ts:
                # 计算当前批次的结束时间
                batch_end = min(
                    current_start + (self.max_limit * interval_ms),
                    end_ts
                )
                
                logger.debug(f"获取数据批次: {datetime.fromtimestamp(current_start/1000, pytz.UTC)} "
                           f"到 {datetime.fromtimestamp(batch_end/1000, pytz.UTC)}")
                
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=self.max_limit,
                    startTime=current_start,
                    endTime=batch_end
                )
                
                if not klines:
                    break
                    
                all_klines.extend(klines)
                current_start = int(klines[-1][0]) + interval_ms
                
                logger.debug(f"已获取 {len(all_klines)} 条数据")
            
            if not all_klines:
                logger.warning(f"未获取到数据: {symbol} {interval}")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = pd.DataFrame(all_klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close',
                'volume', 'close_time', 'quote_volume', 'trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # 转换时间戳
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            df.set_index('timestamp', inplace=True)
            
            # 转换数据类型
            numeric_columns = ['open', 'high', 'low', 'close', 'volume',
                             'quote_volume', 'trades', 'taker_buy_base',
                             'taker_buy_quote']
            df[numeric_columns] = df[numeric_columns].astype(float)
            
            # 删除不需要的列
            df.drop(['close_time', 'ignore'], axis=1, inplace=True)
            
            logger.info(f"成功获取 {len(df)} 条数据")
            return df
            
        except BinanceAPIException as e:
            logger.error(f"获取数据失败: {e}")
            raise e
        except Exception as e:
            logger.error(f"处理数据失败: {e}")
            raise e
            
    async def fetch_realtime_data(
        self,
        symbol: str,
        interval: str,
        limit: int = 1
    ) -> pd.DataFrame:
        """获取实时K线数据"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=self.INTERVALS[interval],
                limit=limit
            )
            return self._format_kline_data(klines)
            
        except BinanceAPIException as e:
            print(f"获取实时数据失败: {e}")
            return pd.DataFrame()
            
    async def fetch_orderbook(
        self,
        symbol: str,
        depth: int = 10
    ) -> Dict:
        """获取订单簿数据"""
        try:
            orderbook = self.client.get_order_book(
                symbol=symbol,
                limit=depth
            )
            
            result = {
                'bids': pd.DataFrame(orderbook['bids'], columns=['price', 'quantity']).astype(float),
                'asks': pd.DataFrame(orderbook['asks'], columns=['price', 'quantity']).astype(float),
                'timestamp': pd.Timestamp.now()
            }
            
            # 计算累计量
            result['bids']['cumulative'] = result['bids']['quantity'].cumsum()
            result['asks']['cumulative'] = result['asks']['quantity'].cumsum()
            
            return result
            
        except BinanceAPIException as e:
            print(f"获取订单簿失败: {e}")
            return {'bids': pd.DataFrame(), 'asks': pd.DataFrame()}
            
    async def fetch_ticker(self, symbol: str) -> Dict:
        """获取24小时价格变动统计"""
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                'price': float(ticker['lastPrice']),
                'volume': float(ticker['volume']),
                'high': float(ticker['highPrice']),
                'low': float(ticker['lowPrice']),
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent'])
            }
        except BinanceAPIException as e:
            print(f"获取Ticker失败: {e}")
            return {}
            
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()