from typing import Dict, List
import pandas as pd
import numpy as np
from ..database import Trade, Position

class RiskManager:
    """风险管理器"""
    
    def __init__(
        self,
        max_drawdown: float = 0.2,
        max_position_size: float = 0.1,
        max_correlation: float = 0.7,
        var_window: int = 20,
        var_confidence: float = 0.95
    ):
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        self.max_correlation = max_correlation
        self.var_window = var_window
        self.var_confidence = var_confidence
        
    def check_drawdown(self, equity_curve: pd.Series) -> bool:
        """检查回撤是否超过限制"""
        drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
        return drawdown.max() <= self.max_drawdown
        
    def calculate_var(self, returns: pd.Series) -> float:
        """计算VaR"""
        return np.percentile(returns.rolling(self.var_window).apply(
            lambda x: x.dropna()
        ), (1 - self.var_confidence) * 100)
        
    def check_position_correlation(
        self,
        positions: List[Position],
        price_data: Dict[str, pd.DataFrame]
    ) -> bool:
        """检查持仓相关性"""
        if len(positions) < 2:
            return True
            
        returns = pd.DataFrame()
        for pos in positions:
            if pos.symbol in price_data:
                returns[pos.symbol] = price_data[pos.symbol]['close'].pct_change()
                
        corr_matrix = returns.corr()
        return corr_matrix.max().max() <= self.max_correlation
        
    def check_risk_limits(
        self,
        new_position: Position,
        current_positions: List[Position],
        account_value: float
    ) -> bool:
        """检查是否满足风险限制"""
        # 检查单个持仓规模
        position_value = new_position.quantity * new_position.current_price
        if position_value / account_value > self.max_position_size:
            return False
            
        # 检查总持仓规模
        total_position_value = sum(
            pos.quantity * pos.current_price for pos in current_positions
        ) + position_value
        
        if total_position_value / account_value > self.max_position_size:
            return False
            
        return True 