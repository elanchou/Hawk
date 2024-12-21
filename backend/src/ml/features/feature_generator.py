from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator

class FeatureGenerator:
    """特征生成器"""
    
    def __init__(self, timeframes: List[str] = None):
        self.timeframes = timeframes or ['1m', '5m', '15m']
        
    def generate_features(
        self,
        df: pd.DataFrame,
        feature_groups: List[str] = None
    ) -> pd.DataFrame:
        """生成特征"""
        if feature_groups is None:
            feature_groups = ['trend', 'momentum', 'volatility', 'volume']
        
        features = df.copy()
        
        if 'trend' in feature_groups:
            features = self._add_trend_indicators(features)
        if 'momentum' in feature_groups:
            features = self._add_momentum_indicators(features)
        if 'volatility' in feature_groups:
            features = self._add_volatility_indicators(features)
        if 'volume' in feature_groups:
            features = self._add_volume_indicators(features)
        
        # 删除包含NaN的行
        features = features.dropna()
        
        return features
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加趋势指标"""
        # SMA
        for period in [5, 10, 20, 50, 200]:
            df[f'sma_{period}'] = SMAIndicator(
                close=df['close'], window=period
            ).sma_indicator()
        
        # EMA
        for period in [5, 10, 20, 50, 200]:
            df[f'ema_{period}'] = EMAIndicator(
                close=df['close'], window=period
            ).ema_indicator()
        
        # MACD
        macd = MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加动量指标"""
        # RSI
        for period in [6, 12, 24]:
            df[f'rsi_{period}'] = RSIIndicator(
                close=df['close'], window=period
            ).rsi()
        
        # Stochastic
        stoch = StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close']
        )
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加波动率指标"""
        # Bollinger Bands
        bb = BollingerBands(close=df['close'])
        df['bb_high'] = bb.bollinger_hband()
        df['bb_mid'] = bb.bollinger_mavg()
        df['bb_low'] = bb.bollinger_lband()
        
        # ATR
        df['atr'] = AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close']
        ).average_true_range()
        
        return df
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加成交量指标"""
        # VWAP
        df['vwap'] = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        ).volume_weighted_average_price()
        
        # OBV
        df['obv'] = OnBalanceVolumeIndicator(
            close=df['close'],
            volume=df['volume']
        ).on_balance_volume()
        
        return df 