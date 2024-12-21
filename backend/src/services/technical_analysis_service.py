from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, and_

from ..models.database import DatabaseManager, MarketData, TechnicalIndicators
from ..utils.logger import Logger

logger = Logger(__name__)

class TechnicalAnalysisService:
    def __init__(self):
        self.db = DatabaseManager()
    
    async def calculate_indicators(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        force_update: bool = False
    ):
        """计算技术指标"""
        try:
            session = self.db.get_session()
            
            # 获取市场数据
            query = select(MarketData).where(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.interval == interval,
                    MarketData.timestamp >= (start_time or datetime.min),
                    MarketData.timestamp <= (end_time or datetime.utcnow())
                )
            ).order_by(MarketData.timestamp)
            
            result = session.execute(query)
            records = result.fetchall()
            
            if not records:
                logger.warning(f"没有找到市场数据: {symbol} {interval}")
                return
            
            # 转换为DataFrame
            df = pd.DataFrame([r._asdict() for r in records])
            df.set_index('timestamp', inplace=True)
            
            # 计算技术指标
            indicators = self._calculate_all_indicators(df)
            
            # 准备数据记录
            records = []
            for timestamp, row in indicators.iterrows():
                record = {
                    'symbol': symbol,
                    'interval': interval,
                    'timestamp': timestamp,
                    **{col: row[col] for col in row.index if not pd.isna(row[col])}
                }
                records.append(record)
            
            # 使用 upsert 插入数据
            stmt = insert(TechnicalIndicators).values(records)
            
            # 如果强制更新或者有新数据，则更新已存在的记录
            if force_update:
                update_cols = {col.name: stmt.excluded[col.name] 
                             for col in TechnicalIndicators.__table__.columns 
                             if col.name not in ['id', 'symbol', 'interval', 'timestamp']}
                
                stmt = stmt.on_conflict_do_update(
                    constraint='unique_technical_indicators',
                    set_=update_cols
                )
            else:
                stmt = stmt.on_conflict_do_nothing()
            
            session.execute(stmt)
            session.commit()
            
            logger.info(f"成功计算并保存技术指标: {symbol} {interval} ({len(records)} 条记录)")
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {symbol} {interval} - {e}")
            if session:
                session.rollback()
        finally:
            if session:
                session.close()
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        result = pd.DataFrame(index=df.index)
        
        # 计算移动平均线
        for period in [5, 10, 20, 50, 200]:
            result[f'ma_{period}'] = df['close'].rolling(window=period).mean()
            result[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        # 计算RSI
        for period in [6, 12, 24]:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            result[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # 计算MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        result['macd'] = exp1 - exp2
        result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean()
        result['macd_hist'] = result['macd'] - result['macd_signal']
        
        # 计算布林带
        result['bb_middle'] = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        result['bb_upper'] = result['bb_middle'] + (std * 2)
        result['bb_lower'] = result['bb_middle'] - (std * 2)
        
        # 计算ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        result['atr'] = true_range.rolling(window=14).mean()
        
        # 计算VWAP
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        result['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        
        # 计算OBV
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        result['obv'] = obv
        
        return result

    async def get_indicators(
        self,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        indicators: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """获取技术指标数据"""
        session = self.db.get_session()
        try:
            query = select(TechnicalIndicators).where(
                and_(
                    TechnicalIndicators.symbol == symbol,
                    TechnicalIndicators.interval == interval,
                    TechnicalIndicators.timestamp >= start_time,
                    TechnicalIndicators.timestamp <= (end_time or datetime.utcnow())
                )
            ).order_by(TechnicalIndicators.timestamp)
            
            result = session.execute(query)
            records = result.fetchall()
            
            if not records:
                return pd.DataFrame()
            
            df = pd.DataFrame([r._asdict() for r in records])
            df.set_index('timestamp', inplace=True)
            
            if indicators:
                return df[indicators]
            return df
            
        finally:
            session.close() 