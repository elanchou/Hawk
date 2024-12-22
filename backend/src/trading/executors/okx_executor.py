from typing import Dict, Optional
from datetime import datetime
import asyncio
from okx import Trade, Account
from ...utils.logger import Logger

logger = Logger(__name__)

class OKXExecutor:
    """OKX交易执行器"""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        is_test: bool = True
    ):
        self.trade = Trade(
            api_key=api_key,
            api_secret_key=api_secret,
            passphrase=passphrase,
            flag='1' if is_test else '0'
        )
        
        self.account = Account(
            api_key=api_key,
            api_secret_key=api_secret,
            passphrase=passphrase,
            flag='1' if is_test else '0'
        )
    
    async def place_order(
        self,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        order_type: str,  # 'market' or 'limit'
        quantity: float,
        price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> Dict:
        """下单"""
        try:
            params = {
                'instId': symbol,
                'tdMode': 'cash',  # 现货交易
                'side': side,
                'ordType': 'market' if order_type == 'market' else 'limit',
                'sz': str(quantity)
            }
            
            if order_type == 'limit' and price:
                params['px'] = str(price)
            
            if client_order_id:
                params['clOrdId'] = client_order_id
            
            result = self.trade.place_order(**params)
            
            if result['code'] != '0':
                logger.error(f"下单失败: {result['msg']}")
                return {'success': False, 'error': result['msg']}
            
            return {
                'success': True,
                'order_id': result['data'][0]['ordId'],
                'client_order_id': result['data'][0].get('clOrdId')
            }
            
        except Exception as e:
            logger.error(f"下单异常: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cancel_order(
        self,
        symbol: str,
        order_id: str
    ) -> Dict:
        """撤单"""
        try:
            result = self.trade.cancel_order(
                instId=symbol,
                ordId=order_id
            )
            
            if result['code'] != '0':
                return {'success': False, 'error': result['msg']}
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"撤单异常: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_position(self, symbol: str) -> Dict:
        """获取持仓"""
        try:
            result = self.account.get_positions(instId=symbol)
            
            if result['code'] != '0':
                return {}
            
            if not result['data']:
                return {}
            
            position = result['data'][0]
            return {
                'symbol': symbol,
                'quantity': float(position['pos']),
                'entry_price': float(position['avgPx']),
                'unrealized_pnl': float(position['upl']),
                'leverage': float(position['lever'])
            }
            
        except Exception as e:
            logger.error(f"获取持仓异常: {e}")
            return {}
    
    async def get_account_balance(self) -> Dict:
        """获取账户余额"""
        try:
            result = self.account.get_account_balance()
            
            if result['code'] != '0':
                return {}
            
            balances = {}
            for currency in result['data'][0]['details']:
                balances[currency['ccy']] = {
                    'available': float(currency['availBal']),
                    'frozen': float(currency['frozenBal']),
                    'total': float(currency['cashBal'])
                }
            
            return balances
            
        except Exception as e:
            logger.error(f"获取账户余额异常: {e}")
            return {} 