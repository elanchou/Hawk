import torch
import torch.nn as nn
import pytorch_lightning as pl
from transformers import AutoConfig, AutoModel
from typing import Dict, Any
from src.utils.logger import Logger

logger = Logger(__name__)

class TimeSeriesModel(pl.LightningModule):
    """时间序列预测模型"""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        num_heads: int,
        dropout: float = 0.1,
        learning_rate: float = 1e-4,
        warmup_steps: int = 1000,
        max_seq_length: int = 512
    ):
        super().__init__()
        self.save_hyperparameters()
        
        # 创建Transformer配置
        self.config = AutoConfig.from_pretrained(
            'bert-base-uncased',
            hidden_size=hidden_size,
            num_hidden_layers=num_layers,
            num_attention_heads=num_heads,
            intermediate_size=hidden_size * 4,
            hidden_dropout_prob=dropout,
            attention_probs_dropout_prob=dropout,
            max_position_embeddings=max_seq_length,
            type_vocab_size=1,
            vocab_size=1
        )
        
        # 输入投影层
        self.input_proj = nn.Linear(input_size, hidden_size)
        
        # Transformer编码器
        self.transformer = AutoModel.from_config(self.config)
        
        # 输出头
        self.output_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 1)  # 预测下一个时间点
        )
        
        # 损失函数
        self.loss_fn = nn.MSELoss()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 输入投影
        x = self.input_proj(x)
        
        # 创建注意力掩码
        attention_mask = torch.ones(
            x.shape[0], x.shape[1],
            device=x.device,
            dtype=torch.long
        )
        
        # Transformer编码
        outputs = self.transformer(
            inputs_embeds=x,
            attention_mask=attention_mask,
            return_dict=True
        )
        
        # 使用最后一个隐藏状态
        pooled_output = outputs.last_hidden_state[:, -1, :]
        
        # 预测
        predictions = self.output_head(pooled_output)
        return predictions
    
    def training_step(self, batch: tuple, batch_idx: int) -> Dict[str, Any]:
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        
        self.log('train_loss', loss)
        return {'loss': loss}
    
    def validation_step(self, batch: tuple, batch_idx: int) -> Dict[str, Any]:
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        
        self.log('val_loss', loss)
        return {'val_loss': loss}
    
    def test_step(self, batch: tuple, batch_idx: int) -> Dict[str, Any]:
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        
        metrics = {
            'test_loss': loss,
            'predictions': y_hat,
            'targets': y
        }
        self.log('test_loss', loss)
        return metrics
    
    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.hparams.learning_rate,
            weight_decay=0.01
        )
        
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=self.hparams.learning_rate,
            total_steps=self.trainer.estimated_stepping_batches,
            pct_start=0.1
        )
        
        return {
            'optimizer': optimizer,
            'lr_scheduler': {
                'scheduler': scheduler,
                'interval': 'step'
            }
        } 