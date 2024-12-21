import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    """趋势跟踪策略"""
    
    def __init__(
        self,
        short_window: int = 20,
        long_window: int = 50,
        rsi_window: int = 14,
        rsi_overbought: float = 70,
        rsi_oversold: float = 30,
        volume_window: int = 20,
        atr_window: int = 14,
        risk_factor: float = 2.0
    ):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.volume_window = volume_window
        self.atr_window = atr_window
        self.risk_factor = risk_factor
        
    def calculate_position_size(
        self,
        price: float,
        atr: float,
        account_value: float
    ) -> float:
        """计算仓位大小"""
        risk_per_trade = account_value * 0.02  # 每次交易风险2%资金
        stop_loss_distance = self.risk_factor * atr
        position_size = risk_per_trade / stop_loss_distance
        return position_size
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成交易信号"""
        # 计算技术指标
        short_ma = self.indicators.calculate_ma(data['close'], self.short_window)
        long_ma = self.indicators.calculate_ma(data['close'], self.long_window)
        rsi = self.indicators.calculate_rsi(data['close'], self.rsi_window)
        volume_ma = self.indicators.calculate_ma(data['volume'], self.volume_window)
        bb_upper, bb_middle, bb_lower = self.indicators.calculate_bollinger_bands(
            data['close'], self.short_window
        )
        
        # 生成信号
        signals = pd.Series(0, index=data.index)
        
        # 趋势确认
        trend_up = short_ma > long_ma
        trend_down = short_ma < long_ma
        
        # 成交量确认
        volume_confirm = data['volume'] > volume_ma
        
        # 买入条件
        buy_condition = (
            trend_up &  # 上升趋势
            (short_ma.shift(1) <= long_ma.shift(1)) &  # 均线金叉
            (rsi < self.rsi_oversold) &  # RSI超卖
            volume_confirm &  # 放量确认
            (data['close'] > bb_lower)  # 价格在布林带支撑位之上
        )
        
        # 卖出条件
        sell_condition = (
            trend_down |  # 下降趋势
            (rsi > self.rsi_overbought) |  # RSI超买
            (data['close'] < bb_lower)  # 跌破布林带支撑
        )
        
        # 设置信号
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        # 计算ATR用于仓位管理
        self.current_atr = self.indicators.calculate_atr(
            data['high'], 
            data['low'], 
            data['close'], 
            self.atr_window
        ).iloc[-1]
        
        return signals
        
    def get_stop_loss(self, entry_price: float) -> float:
        """获取止损价格"""
        return entry_price - (self.risk_factor * self.current_atr)
        
    def get_take_profit(self, entry_price: float) -> float:
        """获取止盈价格"""
        return entry_price + (self.risk_factor * 2 * self.current_atr)