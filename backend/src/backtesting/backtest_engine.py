import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from ..models.strategies.base_strategy import BaseStrategy

class BacktestEngine:
    """回测引擎"""
    
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.001
    ):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.reset()
        
    def reset(self):
        """重置回测状态"""
        self.position = 0
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = []
        self.current_trade = None
        
    def run(
        self,
        data: pd.DataFrame,
        risk_manager: Optional[object] = None
    ) -> Dict:
        """运行回测"""
        signals = self.strategy.generate_signals(data)
        
        for i in range(len(data)):
            current_bar = data.iloc[i]
            signal = signals.iloc[i]
            
            # 更新当前持仓的盈亏
            if self.current_trade is not None:
                self._update_trade_pnl(current_bar)
            
            # 执行交易
            if signal == 1 and self.position == 0:  # 买入
                self._execute_buy(current_bar, risk_manager)
                    
            elif signal == -1 and self.position > 0:  # 卖出
                self._execute_sell(current_bar)
                
            # 更新权益曲线
            self._update_equity_curve(current_bar)
            
        return self._calculate_metrics()
        
    def _execute_buy(self, bar: pd.Series, risk_manager: Optional[object] = None):
        """执行买入"""
        price = bar['close'] * (1 + self.slippage)
        
        if risk_manager:
            position_size = self.strategy.calculate_position_size(
                price,
                self.strategy.current_atr,
                self.capital
            )
        else:
            position_size = self.capital / price
            
        cost = position_size * price * (1 + self.commission)
        
        if cost <= self.capital:
            self.position = position_size
            self.capital -= cost
            
            self.current_trade = {
                'entry_time': bar.name,
                'entry_price': price,
                'position': position_size,
                'stop_loss': self.strategy.get_stop_loss(price),
                'take_profit': self.strategy.get_take_profit(price)
            }
            
            self.trades.append({
                'timestamp': bar.name,
                'type': 'buy',
                'price': price,
                'shares': position_size,
                'cost': cost
            })
            
    def _execute_sell(self, bar: pd.Series):
        """执行卖出"""
        price = bar['close'] * (1 - self.slippage)
        revenue = self.position * price * (1 - self.commission)
        
        self.trades.append({
            'timestamp': bar.name,
            'type': 'sell',
            'price': price,
            'shares': self.position,
            'revenue': revenue,
            'pnl': revenue - self.current_trade['entry_price'] * self.position
        })
        
        self.capital += revenue
        self.position = 0
        self.current_trade = None
        
    def _update_trade_pnl(self, bar: pd.Series):
        """更新当前交易的盈亏"""
        if self.current_trade:
            # 检查是否触发止损或止盈
            if bar['low'] <= self.current_trade['stop_loss']:
                self._execute_sell(pd.Series({
                    'name': bar.name,
                    'close': self.current_trade['stop_loss']
                }))
            elif bar['high'] >= self.current_trade['take_profit']:
                self._execute_sell(pd.Series({
                    'name': bar.name,
                    'close': self.current_trade['take_profit']
                }))
                
    def _update_equity_curve(self, bar: pd.Series):
        """更新权益曲线"""
        self.equity_curve.append({
            'timestamp': bar.name,
            'equity': self.capital + (self.position * bar['close']),
            'position': self.position
        })
        
    def _calculate_metrics(self) -> Dict:
        """计算回测指标"""
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df.set_index('timestamp', inplace=True)
        
        returns = equity_df['equity'].pct_change()
        
        # 计算交易统计
        trades_df = pd.DataFrame(self.trades)
        winning_trades = trades_df[trades_df['type'] == 'sell']['pnl'] > 0
        
        metrics = {
            'total_return': (equity_df['equity'].iloc[-1] - self.initial_capital) / self.initial_capital,
            'annual_return': self._calculate_annual_return(equity_df['equity']),
            'sharpe_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(equity_df['equity']),
            'win_rate': len(winning_trades) / len(trades_df[trades_df['type'] == 'sell']),
            'profit_factor': self._calculate_profit_factor(trades_df),
            'trade_count': len(trades_df[trades_df['type'] == 'sell']),
            'equity_curve': equity_df
        }
        
        return metrics
        
    def _calculate_annual_return(self, equity: pd.Series) -> float:
        """计算年化收益率"""
        days = (equity.index[-1] - equity.index[0]).days
        return ((equity.iloc[-1] / equity.iloc[0]) ** (365 / days)) - 1
        
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """计算夏普比率"""
        return np.sqrt(252) * returns.mean() / returns.std()
        
    def _calculate_max_drawdown(self, equity: pd.Series) -> float:
        """计算最大回撤"""
        peak = equity.expanding(min_periods=1).max()
        drawdown = (equity - peak) / peak
        return drawdown.min()
        
    def _calculate_profit_factor(self, trades: pd.DataFrame) -> float:
        """计算盈亏比"""
        sell_trades = trades[trades['type'] == 'sell']
        if len(sell_trades) == 0:
            return 0
            
        gross_profit = sell_trades[sell_trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(sell_trades[sell_trades['pnl'] < 0]['pnl'].sum())
        
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')