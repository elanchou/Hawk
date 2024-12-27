from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
from ..models.database import DatabaseManager, Trade, Position
from ..utils.logger import Logger
from ..config.config import Config

app = FastAPI(title="量化交易系统API")
logger = Logger(__name__)
config = Config()
db = DatabaseManager()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT配置
SECRET_KEY = "your-secret-key"  # 实际应用中应该从环境变量获取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 用户认证相关接口
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 这里应该查询数据库验证用户
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token(
        data={"sub": form_data.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证信息")
        return username
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的认证信息")

# 交易相关接口
@app.get("/api/trades")
async def get_trades(
    current_user: str = Depends(get_current_user),
    limit: int = 100
) -> List[Trade]:
    """获取交易记录"""
    session = db.get_session()
    try:
        trades = session.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
        return trades
    finally:
        session.close()

@app.get("/api/positions")
async def get_positions(
    current_user: str = Depends(get_current_user)
) -> List[Position]:
    """获取当前持仓"""
    session = db.get_session()
    try:
        positions = session.query(Position).all()
        return positions
    finally:
        session.close()

@app.get("/api/equity-curve")
async def get_equity_curve(
    current_user: str = Depends(get_current_user),
    days: Optional[int] = 30
):
    """获取权益曲线数据"""
    session = db.get_session()
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        trades = session.query(Trade).filter(
            Trade.timestamp >= start_date
        ).order_by(Trade.timestamp).all()
        
        equity_curve = []
        current_equity = config.get('trading.initial_capital', 100000)
        
        for trade in trades:
            if trade.type == 'sell':
                current_equity += trade.pnl
            equity_curve.append({
                'timestamp': trade.timestamp,
                'equity': current_equity
            })
            
        return equity_curve
    finally:
        session.close()

@app.get("/api/statistics")
async def get_statistics(
    current_user: str = Depends(get_current_user)
):
    """获取交易统计数据"""
    session = db.get_session()
    try:
        trades = session.query(Trade).filter(Trade.type == 'sell').all()
        
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        total_pnl = sum(t.pnl for t in trades)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'average_pnl': total_pnl / total_trades if total_trades > 0 else 0
        }
    finally:
        session.close() 