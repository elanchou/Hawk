from typing import Dict, Optional
import numpy as np

class PositionSizer:
    """仓位管理器"""
    
    def __init__(
        self,
        account_balance: float,
        risk_per_trade: float = 0.02,
        max_position_size: float = 0.1,
        position_sizing_method: str = 'risk_parity'
    ):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        self.position_sizing_method = position_sizing_method
        
    def calculate_position_size(
        self,
        price: float,
        volatility: float,
        stop_loss: Optional[float] = None
    ) -> float:
        """计算仓位大小"""
        if self.position_sizing_method == 'fixed_risk':
            return self._fixed_risk_position_size(price, stop_loss)
        elif self.position_sizing_method == 'risk_parity':
            return self._risk_parity_position_size(price, volatility)
        else:
            return self._fixed_fraction_position_size(price)
            
    def _fixed_risk_position_size(
        self,
        price: float,
        stop_loss: float
    ) -> float:
        """固定风险金额的仓位计算"""
        risk_amount = self.account_balance * self.risk_per_trade
        position_size = risk_amount / (price - stop_loss)
        return min(position_size, self.account_balance * self.max_position_size / price)
        
    def _risk_parity_position_size(
        self,
        price: float,
        volatility: float
    ) -> float:
        """风险平价仓位计算"""
        target_risk = self.account_balance * self.risk_per_trade
        position_size = target_risk / (price * volatility)
        return min(position_size, self.account_balance * self.max_position_size / price)
        
    def _fixed_fraction_position_size(
        self,
        price: float
    ) -> float:
        """固定比例仓位计算"""
        return self.account_balance * self.max_position_size / price 