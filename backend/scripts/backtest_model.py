import sys
import os
from pathlib import Path
import asyncio
import argparse
from datetime import datetime, timedelta
import torch
import pandas as pd
import numpy as np
import random
from typing import List, Dict

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.market_data_service import MarketDataService
from src.ml.features.feature_generator import FeatureGenerator
from src.utils.logger import Logger

logger = Logger(__name__)

async def run_backtest(
    model_path: str,
    symbol: str = 'BTCUSDT',
    interval: str = '1m',
    test_days: int = 7,
    initial_capital: float = 100000,
    position_size: float = 0.1,
    stop_loss: float = 0.02,
    take_profit: float = 0.04,
    num_tests: int = 5  # 回测次数
) -> List[Dict]:
    """运行多次回测"""
    try:
        # 加载模型
        model = torch.load(model_path)
        model.eval()
        
        # 初始化服务
        market_service = MarketDataService()
        feature_generator = FeatureGenerator()
        
        # 获取足够长的历史数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=test_days * 2)  # 获取2倍时间的数据，用于随机选择
        
        print(f"获取历史数据: {start_time} 到 {end_time}")
        market_data = await market_service.get_market_data(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time
        )
        
        if market_data.empty:
            print("未获取到市场数据")
            return []
        
        # 存储所有回测结果
        all_results = []
        
        # 运行多次回测
        for test_num in range(num_tests):
            print(f"\n{'='*50}")
            print(f"开始第 {test_num + 1}/{num_tests} 次回测")
            print(f"{'='*50}")
            
            # 随机选择回测时间段
            available_days = (market_data.index[-1] - market_data.index[0]).days - test_days
            random_start_days = random.randint(0, available_days)
            test_start = market_data.index[0] + timedelta(days=random_start_days)
            test_end = test_start + timedelta(days=test_days)
            
            # 获取回测数据段
            test_data = market_data[test_start:test_end]
            print(f"回测时间段: {test_start} 到 {test_end}")
            
            # 生成特征
            features = feature_generator.generate_features(test_data)
            features = features.dropna()
            test_data = test_data.loc[features.index]
            
            # 生成预测
            with torch.no_grad():
                predictions = model(torch.FloatTensor(features.values))
                predictions = predictions.numpy().flatten()
            
            # 生成交易信号
            signals = pd.Series(0, index=features.index)
            signals[predictions > 0.2] = 1
            signals[predictions < -0.2] = -1
            
            # 模拟交易
            capital = initial_capital
            position = 0
            trades = []
            equity_curve = []
            
            for timestamp, row in test_data.iterrows():
                price = row['close']
                signal = signals[timestamp]
                
                # 记录权益
                current_value = capital + (position * price if position > 0 else 0)
                equity_curve.append({
                    'timestamp': timestamp,
                    'equity': current_value
                })
                
                # 检查止损止盈
                if position > 0:
                    pnl_ratio = (price - entry_price) / entry_price
                    if pnl_ratio <= -stop_loss or pnl_ratio >= take_profit:
                        # 平仓
                        pnl = position * (price - entry_price)
                        capital += position * price
                        trades.append({
                            'timestamp': timestamp,
                            'type': 'sell',
                            'price': price,
                            'quantity': position,
                            'pnl': pnl,
                            'reason': 'stop_loss' if pnl_ratio <= -stop_loss else 'take_profit'
                        })
                        position = 0
                
                # 执行交易信号
                if signal == 1 and position == 0:  # 买入
                    position = (capital * position_size) / price
                    entry_price = price
                    capital -= position * price
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'buy',
                        'price': price,
                        'quantity': position
                    })
                elif signal == -1 and position > 0:  # 卖出
                    pnl = position * (price - entry_price)
                    capital += position * price
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'sell',
                        'price': price,
                        'quantity': position,
                        'pnl': pnl,
                        'reason': 'signal'
                    })
                    position = 0
            
            # 计算最终资金
            final_capital = capital + (position * test_data['close'].iloc[-1] if position > 0 else 0)
            
            # 计算回测指标
            trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
            equity_df = pd.DataFrame(equity_curve)
            
            # 计算收益率
            returns = equity_df['equity'].pct_change().dropna()
            total_return = (final_capital - initial_capital) / initial_capital
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if len(returns) > 1 else 0
            
            # 计算最大回撤
            peak = equity_df['equity'].expanding(min_periods=1).max()
            drawdown = (equity_df['equity'] - peak) / peak
            max_drawdown = drawdown.min()
            
            # 汇总结果
            result = {
                'test_number': test_num + 1,
                'start_time': test_start,
                'end_time': test_end,
                'initial_capital': initial_capital,
                'final_capital': final_capital,
                'total_return': total_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'total_trades': len(trades),
                'win_rate': len(trades_df[trades_df['pnl'] > 0]) / len(trades) if len(trades) > 0 else 0,
                'avg_profit': trades_df[trades_df['pnl'] > 0]['pnl'].mean() if len(trades_df) > 0 else 0,
                'avg_loss': trades_df[trades_df['pnl'] < 0]['pnl'].mean() if len(trades_df) > 0 else 0
            }
            
            all_results.append(result)
            
            # 打印回测结果
            print("\n回测结果:")
            print(f"初始资金: ${initial_capital:,.2f}")
            print(f"最终资金: ${final_capital:,.2f}")
            print(f"总收益率: {(total_return * 100):.2f}%")
            print(f"夏普比率: {sharpe_ratio:.2f}")
            print(f"最大回撤: {(max_drawdown * 100):.2f}%")
            print(f"总交易次数: {len(trades)}")
            if len(trades_df) > 0:
                print(f"胜率: {(result['win_rate'] * 100):.2f}%")
                if result['avg_profit']:
                    print(f"平均盈利: ${result['avg_profit']:,.2f}")
                if result['avg_loss']:
                    print(f"平均亏损: ${result['avg_loss']:,.2f}")
        
        # 打印汇总统计
        print(f"\n{'='*50}")
        print("回测汇总统计:")
        print(f"{'='*50}")
        returns = [r['total_return'] for r in all_results]
        print(f"平均收益率: {(np.mean(returns) * 100):.2f}%")
        print(f"收益率标准差: {(np.std(returns) * 100):.2f}%")
        print(f"最好收益率: {(max(returns) * 100):.2f}%")
        print(f"最差收益率: {(min(returns) * 100):.2f}%")
        
        return all_results
        
    except Exception as e:
        logger.error(f"回测失败: {e}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='运行回测')
    parser.add_argument('--model-path', required=True, help='模型文件路径')
    parser.add_argument('--symbol', default='BTCUSDT', help='交易对')
    parser.add_argument('--interval', default='1m', help='时间间隔')
    parser.add_argument('--test-days', type=int, default=7, help='每次回测天数')
    parser.add_argument('--num-tests', type=int, default=5, help='回测次数')
    parser.add_argument('--initial-capital', type=float, default=100000, help='初始资金')
    parser.add_argument('--position-size', type=float, default=0.1, help='仓位大小')
    parser.add_argument('--stop-loss', type=float, default=0.02, help='止损比例')
    parser.add_argument('--take-profit', type=float, default=0.04, help='止盈比例')
    
    args = parser.parse_args()
    
    asyncio.run(run_backtest(
        model_path=args.model_path,
        symbol=args.symbol,
        interval=args.interval,
        test_days=args.test_days,
        num_tests=args.num_tests,
        initial_capital=args.initial_capital,
        position_size=args.position_size,
        stop_loss=args.stop_loss,
        take_profit=args.take_profit
    ))