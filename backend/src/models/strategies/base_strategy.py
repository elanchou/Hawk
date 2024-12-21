from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd
from ..indicators.technical_indicators import TechnicalIndicators

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.position = 0
        self.positions = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        pass
        
    def update_position(self, signal: int):
        """更新持仓"""
        self.position = signal
        self.positions.append(signal) 