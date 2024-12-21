import pandas as pd
import numpy as np
from typing import Tuple, Union

class AdvancedIndicators:
    """高级技术指标"""
    
    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD指标"""
        # 计算快速和慢速EMA
        fast_ema = data.ewm(span=fast_period, adjust=False).mean()
        slow_ema = data.ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线
        macd_line = fast_ema - slow_ema
        
        # 计算信号线
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # 计算MACD柱状图
        macd_histogram = macd_line - signal_line
        
        return macd_line, signal_line, macd_histogram
        
    @staticmethod
    def calculate_kdj(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        n: int = 9,
        m1: int = 3,
        m2: int = 3
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算KDJ指标"""
        # 计算RSV
        low_min = low.rolling(window=n).min()
        high_max = high.rolling(window=n).max()
        rsv = 100 * (close - low_min) / (high_max - low_min)
        
        # 计算K值
        k = pd.Series(0.0, index=close.index)
        k[0] = 50.0
        for i in range(1, len(close)):
            k[i] = (m1 * rsv[i] + (n - m1) * k[i-1]) / n
            
        # 计算D值
        d = pd.Series(0.0, index=close.index)
        d[0] = 50.0
        for i in range(1, len(close)):
            d[i] = (m2 * k[i] + (n - m2) * d[i-1]) / n
            
        # 计算J值
        j = 3 * k - 2 * d
        
        return k, d, j
        
    @staticmethod
    def calculate_ichimoku(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        conversion_line_period: int = 9,
        base_line_period: int = 26,
        leading_span_b_period: int = 52,
        displacement: int = 26
    ) -> dict:
        """计算一目均衡表指标"""
        # 转换线 (Conversion Line)
        high_conversion = high.rolling(window=conversion_line_period).max()
        low_conversion = low.rolling(window=conversion_line_period).min()
        conversion_line = (high_conversion + low_conversion) / 2
        
        # 基准线 (Base Line)
        high_base = high.rolling(window=base_line_period).max()
        low_base = low.rolling(window=base_line_period).min()
        base_line = (high_base + low_base) / 2
        
        # 先行带A (Leading Span A)
        leading_span_a = ((conversion_line + base_line) / 2).shift(displacement)
        
        # 先行带B (Leading Span B)
        high_leading = high.rolling(window=leading_span_b_period).max()
        low_leading = low.rolling(window=leading_span_b_period).min()
        leading_span_b = ((high_leading + low_leading) / 2).shift(displacement)
        
        # 延迟线 (Lagging Span)
        lagging_span = close.shift(-displacement)
        
        return {
            'conversion_line': conversion_line,
            'base_line': base_line,
            'leading_span_a': leading_span_a,
            'leading_span_b': leading_span_b,
            'lagging_span': lagging_span
        }
        
    @staticmethod
    def calculate_vwap(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        window: int = None
    ) -> pd.Series:
        """计算成交量加权平均价格(VWAP)"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        
        if window:
            vwap = (typical_price * volume).rolling(window=window).sum() / \
                   volume.rolling(window=window).sum()
            
        return vwap 