from typing import Dict
import pandas as pd

class RiskManager:
    """风险管理器"""
    
    def __init__(
        self,
        max_position_size: float = 0.1,  # 最大持仓比例
        max_drawdown: float = 0.2,       # 最大回撤限制
        stop_loss_pct: float = 0.05      # 止损比例
    ):
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.stop_loss_pct = stop_loss_pct
        
    def check_position_size(
        self,
        account_balance: float,
        position_value: float
    ) -> bool:
        """检查持仓规模"""
        return position_value <= account_balance * self.max_position_size
        
    def check_drawdown(
        self,
        equity_curve: pd.Series
    ) -> bool:
        """检查回撤"""
        drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
        return drawdown.max() <= self.max_drawdown
        
    def calculate_stop_loss(
        self,
        entry_price: float
    ) -> float:
        """计算止损价格"""
        return entry_price * (1 - self.stop_loss_pct) 