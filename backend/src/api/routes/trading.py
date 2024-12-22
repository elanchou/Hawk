from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from ...services.market_data_service import MarketDataService
from ...services.technical_analysis_service import TechnicalAnalysisService
from ...models.database import DatabaseManager

router = APIRouter()

class TradeResponse(BaseModel):
    timestamp: datetime
    type: str
    price: float
    quantity: float
    pnl: Optional[float] = None

class PositionResponse(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float

class EquityResponse(BaseModel):
    timestamp: datetime
    equity: float
    cash: float
    positions_value: float

@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    symbol: str = "BTCUSDT",
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """获取交易记录"""
    db = DatabaseManager()
    session = db.get_session()
    try:
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=7)
        if not end_time:
            end_time = datetime.utcnow()
            
        trades = session.query(Trade).filter(
            Trade.symbol == symbol,
            Trade.timestamp.between(start_time, end_time)
        ).order_by(Trade.timestamp.desc()).all()
        
        return [TradeResponse(**trade.__dict__) for trade in trades]
    finally:
        session.close()

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions():
    """获取当前持仓"""
    db = DatabaseManager()
    session = db.get_session()
    try:
        positions = session.query(Position).all()
        return [PositionResponse(**pos.__dict__) for pos in positions]
    finally:
        session.close()

@router.get("/equity-curve", response_model=List[EquityResponse])
async def get_equity_curve(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """获取权益曲线"""
    db = DatabaseManager()
    session = db.get_session()
    try:
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=30)
        if not end_time:
            end_time = datetime.utcnow()
            
        equity_data = session.query(EquityCurve).filter(
            EquityCurve.timestamp.between(start_time, end_time)
        ).order_by(EquityCurve.timestamp.asc()).all()
        
        return [EquityResponse(**data.__dict__) for data in equity_data]
    finally:
        session.close()

@router.get("/market-data")
async def get_market_data(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    limit: int = 1000
):
    """获取市场数据"""
    service = MarketDataService()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=limit)
    
    data = await service.get_market_data(
        symbol=symbol,
        interval=interval,
        start_time=start_time,
        end_time=end_time
    )
    
    return data.to_dict(orient='records')

@router.get("/technical-indicators")
async def get_technical_indicators(
    symbol: str = "BTCUSDT",
    interval: str = "1m",
    limit: int = 1000
):
    """获取技术指标"""
    service = TechnicalAnalysisService()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=limit)
    
    indicators = await service.get_indicators(
        symbol=symbol,
        interval=interval,
        start_time=start_time,
        end_time=end_time
    )
    
    return indicators.to_dict(orient='records') 