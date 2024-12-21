import pandas as pd
import numpy as np
from typing import Optional

class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_ma(
        data: pd.Series,
        window: int
    ) -> pd.Series:
        """计算移动平均线"""
        return data.rolling(window=window).mean()
        
    @staticmethod
    def calculate_ema(
        data: pd.Series,
        window: int
    ) -> pd.Series:
        """计算指数移动平均线"""
        return data.ewm(span=window, adjust=False).mean()
        
    @staticmethod
    def calculate_rsi(
        data: pd.Series,
        window: int = 14
    ) -> pd.Series:
        """计算RSI指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        window: int = 20,
        num_std: float = 2
    ) -> tuple:
        """计算布林带"""
        middle_band = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        upper_band = middle_band + num_std * std
        lower_band = middle_band - num_std * std
        return upper_band, middle_band, lower_band 