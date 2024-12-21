from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

class BaseDataCollector(ABC):
    """数据采集器基类"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        
    @abstractmethod
    async def fetch_historical_data(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """获取历史数据"""
        pass
        
    @abstractmethod
    async def fetch_realtime_data(
        self,
        symbol: str,
        interval: str
    ) -> pd.DataFrame:
        """获取实时数据"""
        pass
        
    @abstractmethod
    async def fetch_orderbook(
        self,
        symbol: str,
        depth: int = 10
    ) -> Dict:
        """获取订单簿数据"""
        pass 