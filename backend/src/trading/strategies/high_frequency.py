import asyncio
from datetime import datetime
from typing import Dict, Optional
import numpy as np
import pandas as pd
from ...utils.logger import Logger
from ...data.collectors.okx_collector import OKXDataCollector
from ...trading.executors.okx_executor import OKXExecutor

logger = Logger(__name__)

class HighFrequencyStrategy:
    """高频交易策略"""
    
    def __init__(
        self,
        symbol: str,
        collector: OKXDataCollector,
        executor: OKXExecutor,
        tick_interval: float = 0.1,  # 100ms
        position_limit: float = 0.1,  # 最大仓位比例
        min_spread: float = 0.0002,  # 最小价差
        min_profit: float = 0.0001   # 最小利润
    ):
        self.symbol = symbol
        self.collector = collector
        self.executor = executor
        self.tick_interval = tick_interval
        self.position_limit = position_limit
        self.min_spread = min_spread
        self.min_profit = min_profit
        
        self.running = False
        self.position = 0
        self.orders = {}
    
    async def start(self):
        """启动策略"""
        self.running = True
        logger.info(f"启动高频交易策略: {self.symbol}")
        
        while self.running:
            try:
                # 获取订单簿数据
                orderbook = await self.collector.fetch_orderbook(self.symbol)
                if not orderbook['bids'].empty and not orderbook['asks'].empty:
                    await self.process_orderbook(orderbook)
                
                # 等待下一个tick
                await asyncio.sleep(self.tick_interval)
                
            except Exception as e:
                logger.error(f"策略执行异常: {e}")
                await asyncio.sleep(1)
    
    async def process_orderbook(self, orderbook: Dict):
        """处理订单簿数据"""
        best_bid = float(orderbook['bids'].iloc[0]['price'])
        best_ask = float(orderbook['asks'].iloc[0]['price'])
        spread = (best_ask - best_bid) / best_bid
        
        # 检查价差是否足够大
        if spread < self.min_spread:
            return
        
        # 获取当前持仓
        position = await self.executor.get_position(self.symbol)
        current_pos = float(position.get('quantity', 0))
        
        # 获取账户余额
        balances = await self.executor.get_account_balance()
        usdt_balance = balances.get('USDT', {}).get('available', 0)
        
        # 计算可交易数量
        max_trade_amount = min(
            usdt_balance * self.position_limit / best_ask,  # 基于USDT余额
            abs(current_pos)  # 基于当前持仓
        )
        
        if max_trade_amount < 0.0001:  # 最小交易数量
            return
        
        # 交易逻辑
        if current_pos == 0:
            # 无持仓时，尝试在买卖盘价差中套利
            if spread > self.min_profit:
                # 同时下买卖单
                buy_order = await self.executor.place_order(
                    symbol=self.symbol,
                    side='buy',
                    order_type='limit',
                    quantity=max_trade_amount,
                    price=best_bid
                )
                
                sell_order = await self.executor.place_order(
                    symbol=self.symbol,
                    side='sell',
                    order_type='limit',
                    quantity=max_trade_amount,
                    price=best_ask
                )
                
                if buy_order['success']:
                    self.orders[buy_order['order_id']] = 'buy'
                if sell_order['success']:
                    self.orders[sell_order['order_id']] = 'sell'
        
        elif current_pos > 0:
            # 持有多仓时，寻找合适的卖出价格
            if best_ask > position['entry_price'] * (1 + self.min_profit):
                await self.executor.place_order(
                    symbol=self.symbol,
                    side='sell',
                    order_type='limit',
                    quantity=current_pos,
                    price=best_ask
                )
        
        elif current_pos < 0:
            # 持有空仓时，寻找合适的买入价格
            if best_bid < position['entry_price'] * (1 - self.min_profit):
                await self.executor.place_order(
                    symbol=self.symbol,
                    side='buy',
                    order_type='limit',
                    quantity=abs(current_pos),
                    price=best_bid
                )
    
    def stop(self):
        """停止策略"""
        self.running = False
        logger.info(f"停止高频交易策略: {self.symbol}") 