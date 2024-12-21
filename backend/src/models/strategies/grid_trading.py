import pandas as pd
import numpy as np
from typing import List, Dict
from .base_strategy import BaseStrategy

class GridTradingStrategy(BaseStrategy):
    """网格交易策略"""
    
    def __init__(
        self,
        upper_price: float,
        lower_price: float,
        grid_num: int = 10,
        position_size: float = 0.1
    ):
        super().__init__()
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.grid_num = grid_num
        self.position_size = position_size
        self.grid_lines = self._calculate_grid_lines()
        
    def _calculate_grid_lines(self) -> List[float]:
        """计算网格线"""
        return np.linspace(self.lower_price, self.upper_price, self.grid_num + 1)
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        signals = pd.Series(0, index=data.index)
        current_price = data['close']
        
        for i in range(len(self.grid_lines) - 1):
            lower = self.grid_lines[i]
            upper = self.grid_lines[i + 1]
            
            # 价格突破网格线，生成信号
            buy_condition = (current_price > lower) & (current_price.shift(1) <= lower)
            sell_condition = (current_price < upper) & (current_price.shift(1) >= upper)
            
            signals[buy_condition] = 1
            signals[sell_condition] = -1
            
        return signals
        
    def calculate_position_size(self, price: float) -> float:
        """计算每个网格的仓位大小"""
        return self.position_size 