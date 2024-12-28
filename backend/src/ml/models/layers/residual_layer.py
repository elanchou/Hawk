import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class ResidualLayer(BaseLayer):
    """残差连接层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.layer = nn.Sequential(
            nn.Linear(config['input_size'], config['hidden_size']),
            nn.BatchNorm1d(config['hidden_size']),
            getattr(nn, config.get('activation', 'ReLU'))(),
            nn.Dropout(config.get('dropout', 0.1)),
            nn.Linear(config['hidden_size'], config['input_size'])
        )
        self.layer_norm = nn.LayerNorm(config['input_size'])
        
    def forward(self, x):
        residual = x
        x = self.layer(x)
        x = x + residual
        x = self.layer_norm(x)
        return x 