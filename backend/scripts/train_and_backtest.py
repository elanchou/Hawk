import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import torch
import torch.nn as nn
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import pandas as pd
import numpy as np

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.database import DatabaseManager
from src.services.market_data_service import MarketDataService
from src.services.technical_analysis_service import TechnicalAnalysisService
from src.ml.features.feature_generator import FeatureGenerator
from src.utils.logger import Logger

logger = Logger(__name__)

class QuickTrader(pl.LightningModule):
    def __init__(self, input_size: int):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 1),
            nn.Tanh()  # 输出范围[-1, 1]，用于生成交易信号
        )
        
    def forward(self, x):
        return self.model(x)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.MSELoss()(y_hat, y)
        self.log('train_loss', loss)
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.MSELoss()(y_hat, y)
        self.log('val_loss', loss)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.001)

async def quick_train_and_test():
    """快速训练和回测"""
    try:
        # 初始化服务
        market_service = MarketDataService()
        feature_generator = FeatureGenerator()
        
        # 获取最近3天的数据用于训练
        end_time = datetime.now()
        start_time = end_time - timedelta(days=3)
        
        print("获取训练数据...")
        market_data = await market_service.get_market_data(
            symbol='BTCUSDT',
            interval='1m',
            start_time=start_time,
            end_time=end_time
        )
        
        if market_data.empty:
            print("未获取到市场数据")
            return
            
        print(f"获取到 {len(market_data)} 条市场数据")
        print("数据列:", market_data.columns.tolist())
        
        # 检查必要的列是否存在
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in market_data.columns]
        if missing_columns:
            print(f"缺少必要的列: {missing_columns}")
            return
        
        # 生成特征
        print("生成特征...")
        features = feature_generator.generate_features(market_data)
        print(f"特征维度: {features.shape}")
        
        # 确保特征和标签对齐
        features = features.dropna()  # 删除包含NaN的行
        market_data = market_data.loc[features.index]  # 对齐市场数据
        
        # 生成标签
        print("生成标签...")
        returns = market_data['close'].pct_change()
        labels = np.where(returns > 0, 1.0, -1.0)
        labels = labels[1:]  # 去掉第一个NaN
        features = features[1:]  # 对应去掉第一行特征
        
        print(f"特征数量: {len(features)}")
        print(f"标签数量: {len(labels)}")
        
        # 转换为张量
        X = torch.FloatTensor(features.values)
        y = torch.FloatTensor(labels).reshape(-1, 1)
        
        assert len(X) == len(y), f"特征和标签长度不匹配: {len(X)} vs {len(y)}"
        
        # 划分训练集和验证集
        train_size = int(len(X) * 0.8)
        X_train, X_val = X[:train_size], X[train_size:]
        y_train, y_val = y[:train_size], y[train_size:]
        
        # 创建数据加载器
        train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
        val_dataset = torch.utils.data.TensorDataset(X_val, y_val)
        
        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=32, shuffle=True
        )
        val_loader = torch.utils.data.DataLoader(
            val_dataset, batch_size=32
        )
        
        # 创建模型
        model = QuickTrader(input_size=X.shape[1])
        
        # 训练模型
        trainer = pl.Trainer(
            max_epochs=10,
            accelerator='auto',
            enable_progress_bar=True,
            enable_model_summary=True,
            log_every_n_steps=10
        )
        
        print("\n开始训练...")
        trainer.fit(model, train_loader, val_loader)
        
        # 保存模型
        output_dir = project_root / 'outputs' / 'models'
        output_dir.mkdir(exist_ok=True)
        model_path = output_dir / f'quick_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pth'
        torch.save(model, model_path)
        print(f"\n模���已保存到: {model_path}")
        
        # 回测
        print("\n开始回测...")
        # 获取新的1天数据进行回测
        backtest_end = datetime.now()
        backtest_start = backtest_end - timedelta(days=1)
        
        backtest_data = await market_service.get_market_data(
            symbol='BTCUSDT',
            interval='1m',
            start_time=backtest_start,
            end_time=backtest_end
        )
        
        backtest_features = feature_generator.generate_features(backtest_data)
        backtest_features = backtest_features.dropna()  # 删除NaN行
        backtest_data = backtest_data.loc[backtest_features.index]  # 对齐数据
        
        # 生成预测
        model.eval()
        with torch.no_grad():
            predictions = model(torch.FloatTensor(backtest_features.values))
            predictions = predictions.numpy().flatten()
        
        # 生成交易信号（确保长度匹配）
        signals = pd.Series(0, index=backtest_features.index)  # 使用特征的索引
        signals[predictions > 0.2] = 1  # 买入信号
        signals[predictions < -0.2] = -1  # 卖出信号
        
        # 模拟交易
        capital = 100000
        position = 0
        trades = []
        
        for timestamp, row in backtest_data.iterrows():
            price = row['close']
            signal = signals[timestamp]
            
            if signal == 1 and position == 0:  # 买入
                position = (capital * 0.1) / price  # 使用10%资金
                capital -= position * price
                trades.append({
                    'timestamp': timestamp,
                    'type': 'buy',
                    'price': price,
                    'quantity': position
                })
            elif signal == -1 and position > 0:  # 卖出
                capital += position * price
                trades.append({
                    'timestamp': timestamp,
                    'type': 'sell',
                    'price': price,
                    'quantity': position,
                    'pnl': position * (price - trades[-1]['price'])
                })
                position = 0
        
        # 计算最终资金
        final_capital = capital + (position * backtest_data['close'].iloc[-1] if position > 0 else 0)
        
        # 打印回测结果
        print("\n回测结果:")
        print(f"初始资金: ${100000:,.2f}")
        print(f"最终资金: ${final_capital:,.2f}")
        print(f"收益率: {((final_capital/100000 - 1) * 100):.2f}%")
        print(f"总交易次数: {len(trades)}")
        
        if trades:
            trades_df = pd.DataFrame(trades)
            if 'pnl' in trades_df.columns:
                profitable_trades = trades_df[trades_df['pnl'] > 0]
                print(f"盈利交易: {len(profitable_trades)}")
                print(f"平均盈利: ${profitable_trades['pnl'].mean():,.2f}")
        
    except Exception as e:
        print(f"错误: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(quick_train_and_test()) 