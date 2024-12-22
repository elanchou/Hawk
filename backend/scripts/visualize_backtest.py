import sys
import os
from pathlib import Path
import click
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import Logger

logger = Logger(__name__)

@click.command()
@click.argument('result_path')
def visualize_backtest(result_path: str):
    """可视化回测结果"""
    try:
        # 加载回测结果
        base_path = Path(result_path).with_suffix('')
        metrics = pd.read_json(f"{result_path}")
        trades = pd.read_json(f"{base_path}_trades.json")
        equity = pd.read_json(f"{base_path}_equity.json")
        
        # 创建图表
        fig = make_subplots(
            rows=3, 
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('权益曲线', '持仓价值', '现金余额'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # 添加权益曲线
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(equity['timestamp']),
                y=equity['equity'],
                name='账户权益',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        # 添加持仓价值
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(equity['timestamp']),
                y=equity['positions_value'],
                name='持仓价值',
                line=dict(color='green')
            ),
            row=2, col=1
        )
        
        # 添加现金余额
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(equity['timestamp']),
                y=equity['cash'],
                name='现金余额',
                line=dict(color='orange')
            ),
            row=3, col=1
        )
        
        # 添加交易点
        buy_trades = trades[trades['type'] == 'buy']
        sell_trades = trades[trades['type'] == 'sell']
        
        # 买入点
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(buy_trades['timestamp']),
                y=buy_trades['cost'],
                mode='markers',
                name='买入',
                marker=dict(
                    symbol='triangle-up',
                    size=10,
                    color='green'
                )
            ),
            row=1, col=1
        )
        
        # 卖出点
        fig.add_trace(
            go.Scatter(
                x=pd.to_datetime(sell_trades['timestamp']),
                y=sell_trades['revenue'],
                mode='markers',
                name='卖出',
                marker=dict(
                    symbol='triangle-down',
                    size=10,
                    color='red'
                )
            ),
            row=1, col=1
        )
        
        # 更新布局
        fig.update_layout(
            title='回测结果可视化',
            height=1000,
            showlegend=True,
            xaxis3_title='时间',
            yaxis_title='账户权益',
            yaxis2_title='持仓价值',
            yaxis3_title='现金余额'
        )
        
        # 保存图表
        output_dir = project_root / 'outputs' / 'backtest_results' / 'plots'
        output_dir.mkdir(exist_ok=True)
        
        plot_path = output_dir / f"{Path(result_path).stem}_plot.html"
        fig.write_html(str(plot_path))
        
        # 打印回测指标
        logger.info("回测指标:")
        for metric, value in metrics.items():
            logger.info(f"{metric}: {value:.4f}")
        
        logger.info(f"可视化结果已���存到: {plot_path}")
        
    except Exception as e:
        logger.error(f"可视化失败: {e}")
        raise e

if __name__ == "__main__":
    visualize_backtest() 