import sys
import os
from pathlib import Path
import asyncio
import argparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import torch

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.database import DatabaseManager
from src.services.market_data_service import MarketDataService
from src.services.technical_analysis_service import TechnicalAnalysisService
from src.utils.logger import Logger
from src.ml.features.feature_generator import FeatureGenerator

logger = Logger(__name__)

async def run_backtest(
    symbol: str,
    interval: str,
    model_path: str,
    initial_capital: float = 100000,
    position_size: float = 0.1,
    stop_loss: float = 0.02,
    take_profit: float = 0.04
):
    """运行回测"""
    try:
        # 加载模型
        model = torch.load(model_path)
        model.eval()
        
        # 初始化服务
        market_data_service = MarketDataService()
        technical_service = TechnicalAnalysisService()
        feature_generator = FeatureGenerator()
        
        # 设置回测时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)  # 先测试7天的数据
        
        print(f"\n{'='*80}")
        print(f"开始回测")
        print(f"交易对: {symbol}")
        print(f"时间间隔: {interval}")
        print(f"开始时间: {start_time}")
        print(f"结束时间: {end_time}")
        print(f"{'='*80}")
        
        # 获取市场数据
        market_data = await market_data_service.get_market_data(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time
        )
        
        if market_data.empty:
            print("未获取到市场数据")
            return
            
        print(f"获取到 {len(market_data)} 条市场数据")
        
        # 生成特征
        features = feature_generator.generate_features(market_data)
        print(f"生成特征完成，特征数量: {len(features.columns)}")
        
        # 准备模型输入数据
        feature_tensor = torch.FloatTensor(features.values)
        
        # 使用模型预测
        with torch.no_grad():
            predictions = model(feature_tensor)
            predictions = predictions.numpy()
        
        print(f"模型预测完成，生成 {len(predictions)} 个预测信号")
        
        # 生成交易信号
        signals = pd.Series(0, index=market_data.index)
        signals[predictions > 0] = 1  # 买入信号
        signals[predictions < 0] = -1  # 卖出信号
        
        # 回测变量
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = []
        entry_price = 0
        
        # 执行回测
        for timestamp, row in market_data.iterrows():
            price = row['close']
            signal = signals[timestamp]
            
            # 更新持仓盈亏
            if position != 0:
                unrealized_pnl = position * (price - entry_price)
                
                # 检查止损止盈
                pnl_ratio = (price - entry_price) / entry_price
                if pnl_ratio <= -stop_loss or pnl_ratio >= take_profit:
                    # 平仓
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'sell',
                        'price': price,
                        'quantity': abs(position),
                        'pnl': unrealized_pnl,
                        'reason': 'stop_loss' if pnl_ratio <= -stop_loss else 'take_profit'
                    })
                    capital += position * price
                    position = 0
            
            # 执行交易信号
            if signal != 0 and position == 0:  # 仅在无持仓时开新仓
                quantity = (capital * position_size) / price
                if signal == 1:  # 买入
                    position = quantity
                    entry_price = price
                    capital -= quantity * price
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'buy',
                        'price': price,
                        'quantity': quantity
                    })
            
            # 记录权益
            equity = capital + (position * price if position != 0 else 0)
            equity_curve.append({
                'timestamp': timestamp,
                'equity': equity,
                'position': position
            })
        
        # 转换为DataFrame
        trades_df = pd.DataFrame(trades)
        equity_df = pd.DataFrame(equity_curve)
        
        # 打印交易统计
        print("\n交易统计:")
        print(f"初始资金: {initial_capital:,.2f}")
        print(f"最终资金: {equity_df['equity'].iloc[-1]:,.2f}")
        
        if not trades_df.empty:
            print(f"\n总交易次数: {len(trades_df)}")
            buy_trades = trades_df[trades_df['type'] == 'buy']
            sell_trades = trades_df[trades_df['type'] == 'sell']
            print(f"买入交易: {len(buy_trades)}")
            print(f"卖出交易: {len(sell_trades)}")
            
            if 'pnl' in trades_df.columns:
                profitable_trades = trades_df[trades_df['pnl'] > 0]
                loss_trades = trades_df[trades_df['pnl'] < 0]
                print(f"盈利交易: {len(profitable_trades)}")
                print(f"亏损交易: {len(loss_trades)}")
                
                if len(profitable_trades) > 0:
                    print(f"平均盈利: {profitable_trades['pnl'].mean():,.2f}")
                    print(f"最大盈利: {profitable_trades['pnl'].max():,.2f}")
                if len(loss_trades) > 0:
                    print(f"平均亏损: {loss_trades['pnl'].mean():,.2f}")
                    print(f"最大亏损: {loss_trades['pnl'].min():,.2f}")
        
        # 保存回测结果
        output_dir = project_root / 'outputs' / 'backtest_results'
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        trades_df.to_csv(output_dir / f'trades_{symbol}_{interval}_{timestamp}.csv')
        equity_df.to_csv(output_dir / f'equity_{symbol}_{interval}_{timestamp}.csv')
        
        print(f"\n回测结果已保存到: {output_dir}")
        
    except Exception as e:
        logger.error(f"回测失败: {e}")
        print(f"错误详情: {str(e)}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='运行回测')
    parser.add_argument('--symbol', default='BTCUSDT', help='交易对')
    parser.add_argument('--interval', default='1m', help='时间间隔')
    parser.add_argument('--model-path', required=True, help='模型文件路径')
    parser.add_argument('--initial-capital', type=float, default=100000, help='初始资金')
    parser.add_argument('--position-size', type=float, default=0.1, help='仓位大小')
    parser.add_argument('--stop-loss', type=float, default=0.02, help='止损比例')
    parser.add_argument('--take-profit', type=float, default=0.04, help='止盈比例')
    
    args = parser.parse_args()
    
    asyncio.run(run_backtest(
        symbol=args.symbol,
        interval=args.interval,
        model_path=args.model_path,
        initial_capital=args.initial_capital,
        position_size=args.position_size,
        stop_loss=args.stop_loss,
        take_profit=args.take_profit
    ))