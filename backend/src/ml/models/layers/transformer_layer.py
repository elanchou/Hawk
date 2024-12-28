import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class TransformerLayer(BaseLayer):
    """Transformer层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.layer = nn.TransformerEncoderLayer(
            d_model=config['hidden_size'],
            nhead=config['num_heads'],
            dim_feedforward=config['hidden_size'] * 4,
            dropout=config.get('dropout', 0.1),
            batch_first=True
        )
    
    def forward(self, x):
        return self.layer(x) 