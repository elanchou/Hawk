from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import enum
from typing import Optional
from ..config.config import Config
from pathlib import Path

Base = declarative_base()

class OrderStatus(enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderType(enum.Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class Trade(Base):
    """交易记录表"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    order_id = Column(String(50), nullable=False, unique=True)
    type = Column(Enum(OrderType), nullable=False)
    side = Column(String(10), nullable=False)  # buy/sell
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    commission = Column(Float, nullable=False, default=0)
    commission_asset = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(Enum(OrderStatus), nullable=False)
    pnl = Column(Float)
    extra_data = Column(JSON)

class Position(Base):
    """持仓表"""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, unique=True)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    stop_loss = Column(Float)
    take_profit = Column(Float)

class EquityCurve(Base):
    """权益曲线表"""
    __tablename__ = 'equity_curve'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    equity = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    daily_pnl = Column(Float)
    daily_return = Column(Float)

class MarketData(Base):
    """市场数据表"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    interval = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, nullable=False)
    trades_count = Column(Integer)
    taker_buy_volume = Column(Float)
    taker_buy_quote_volume = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'interval', 'timestamp', name='unique_market_data'),
    )

class DataSyncStatus(Base):
    """数据同步状态表"""
    __tablename__ = 'data_sync_status'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    interval = Column(String(10), nullable=False)
    last_sync_time = Column(DateTime, nullable=False)
    next_sync_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # success/failed
    error_message = Column(String(500))
    
    __table_args__ = (
        UniqueConstraint('symbol', 'interval', name='unique_sync_status'),
    )

class TechnicalIndicators(Base):
    """技术指标表"""
    __tablename__ = 'technical_indicators'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    interval = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # 趋势指标
    ma_5 = Column(Float)
    ma_10 = Column(Float)
    ma_20 = Column(Float)
    ma_50 = Column(Float)
    ma_200 = Column(Float)
    ema_5 = Column(Float)
    ema_10 = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    ema_200 = Column(Float)
    
    # 动量指标
    rsi_6 = Column(Float)
    rsi_12 = Column(Float)
    rsi_24 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    
    # 波动指标
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    atr = Column(Float)
    
    # 成交量指标
    vwap = Column(Float)
    obv = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'interval', 'timestamp', name='unique_technical_indicators'),
    )

class DatabaseManager:
    """数据库管理器"""
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = Config()
            
            # 确保数据目录存在
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)
            
            # 获取数据库URL，如果是相对路径，则转换为绝对路径
            db_url = self.config.get('database.url')
            if db_url.startswith('sqlite:///'):
                db_path = db_url.replace('sqlite:///', '')
                if not db_path.startswith('/'):
                    db_path = str(data_dir / db_path)
                db_url = f'sqlite:///{db_path}'
            
            self.engine = create_engine(
                db_url,
                echo=self.config.get('database.echo', False)
            )
            Base.metadata.create_all(self.engine)
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            self.initialized = True
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def close_session(self):
        """关闭数据库会话"""
        self.Session.remove()