import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class CNNLayer(BaseLayer):
    """卷积神经网络层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.conv = nn.Conv1d(
            in_channels=config['input_size'],
            out_channels=config['hidden_size'],
            kernel_size=config.get('kernel_size', 3),
            stride=config.get('stride', 1),
            padding=config.get('kernel_size', 3) // 2
        )
        self.batch_norm = nn.BatchNorm1d(config['hidden_size'])
        self.activation = getattr(nn, config.get('activation', 'ReLU'))()
        self.dropout = nn.Dropout(config.get('dropout', 0.1))
        
    def forward(self, x):
        # 调整维度顺序 (batch, time, features) -> (batch, features, time)
        x = x.transpose(1, 2)
        x = self.conv(x)
        x = self.batch_norm(x)
        x = self.activation(x)
        x = self.dropout(x)
        # 恢复维度顺序 (batch, features, time) -> (batch, time, features)
        x = x.transpose(1, 2)
        return x 