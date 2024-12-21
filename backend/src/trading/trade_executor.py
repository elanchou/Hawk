from typing import Dict, Optional, List
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

class TradeExecutor:
    """交易执行器"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)
        
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Dict:
        """下单"""
        try:
            if order_type == 'MARKET':
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
            else:
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
            return order
            
        except BinanceAPIException as e:
            print(f"下单失败: {e}")
            return {}
            
    async def get_account_info(self) -> Dict:
        """获取账户信息"""
        try:
            return self.client.get_account()
        except BinanceAPIException as e:
            print(f"获取账户信息失败: {e}")
            return {}
            
    async def get_open_orders(self, symbol: str) -> List:
        """获取未成交订单"""
        try:
            return self.client.get_open_orders(symbol=symbol)
        except BinanceAPIException as e:
            print(f"获取未成交订单失败: {e}")
            return [] 