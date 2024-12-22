import sys
import os
from pathlib import Path
import click
from datetime import datetime
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_lightning.loggers import TensorBoardLogger

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.ml.models.time_series_model import TimeSeriesModel
from src.ml.utils.data_loader import MarketDataLoader
from src.ml.features.feature_generator import FeatureGenerator
from src.models.database import DatabaseManager
from src.utils.logger import Logger

custom_logger = Logger(__name__)

@click.command()
@click.option('--symbol', default='BTCUSDT', help='交易对')
@click.option('--interval', default='1m', help='时间间隔')
@click.option('--sequence-length', default=128, help='序列长度')
@click.option('--hidden-size', default=512, help='隐藏层大小')
@click.option('--num-layers', default=8, help='Transformer层数')
@click.option('--num-heads', default=8, help='注意力头数')
@click.option('--batch-size', default=128, help='批次大小')
@click.option('--epochs', default=100, help='训练轮数')
@click.option('--dropout', default=0.1, help='Dropout率')
@click.option('--learning-rate', default=1e-4, help='学习率')
@click.option('--warmup-steps', default=1000, help='预热步数')
@click.option('--precision', default=16, help='训练精度')
@click.option('--accelerator', default='gpu', help='加速器类型')
@click.option('--devices', default=-1, help='设备数量')
def train_model(**kwargs):
    """训练时间序列预测模型"""
    try:
        # 创建输出目录
        output_dir = project_root / 'outputs'
        models_dir = output_dir / 'models'
        logs_dir = output_dir / 'logs'
        for dir in [output_dir, models_dir, logs_dir]:
            dir.mkdir(exist_ok=True)
        
        # 准备数据
        db_manager = DatabaseManager()
        data_loader = MarketDataLoader(
            db_manager=db_manager,
            sequence_length=kwargs['sequence_length'],
            batch_size=kwargs['batch_size']
        )
        
        feature_generator = FeatureGenerator()
        
        train_loader, val_loader, test_loader = data_loader.load_data(
            symbol=kwargs['symbol'],
            interval=kwargs['interval'],
            start_time=datetime(2024, 12, 20),
            end_time=datetime.now(),
            feature_generator=feature_generator
        )
        
        # 获取输入维度
        input_size = next(iter(train_loader))[0].shape[-1]
        
        # 创建模型
        model = TimeSeriesModel(
            input_size=input_size,
            hidden_size=kwargs['hidden_size'],
            num_layers=kwargs['num_layers'],
            num_heads=kwargs['num_heads'],
            dropout=kwargs['dropout'],
            learning_rate=kwargs['learning_rate'],
            warmup_steps=kwargs['warmup_steps']
        )
        
        # 设置回调
        callbacks = [
            ModelCheckpoint(
                dirpath=str(models_dir),
                filename=f"{kwargs['symbol']}_{kwargs['interval']}_{{epoch}}_{{val_loss:.4f}}",
                monitor='val_loss',
                mode='min',
                save_top_k=3
            ),
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                mode='min'
            )
        ]
        
        # 设置TensorBoard日志记录器
        tb_logger = TensorBoardLogger(
            save_dir=str(logs_dir),
            name=f"{kwargs['symbol']}_{kwargs['interval']}"
        )
        
        # 创建训练器
        trainer = pl.Trainer(
            max_epochs=kwargs['epochs'],
            accelerator=kwargs['accelerator'],
            devices=kwargs['devices'],
            precision=kwargs['precision'],
            callbacks=callbacks,
            logger=tb_logger,
            gradient_clip_val=1.0,
            accumulate_grad_batches=1,
            log_every_n_steps=10
        )
        
        # 训练模型
        trainer.fit(
            model=model,
            train_dataloaders=train_loader,
            val_dataloaders=val_loader
        )
        
        # 测试模型
        trainer.test(
            model=model,
            dataloaders=test_loader
        )
        
        custom_logger.info("训练完成")
        
    except Exception as e:
        custom_logger.error(f"训练失败: {e}")
        raise e

if __name__ == "__main__":
    train_model() 