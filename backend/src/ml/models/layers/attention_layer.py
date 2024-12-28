import torch
import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class AttentionLayer(BaseLayer):
    """自注意力层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.attention = nn.MultiheadAttention(
            embed_dim=config['hidden_size'],
            num_heads=config['num_heads'],
            dropout=config.get('dropout', 0.1),
            batch_first=True
        )
        self.layer_norm = nn.LayerNorm(config['hidden_size'])
        self.dropout = nn.Dropout(config.get('dropout', 0.1))
    
    def forward(self, x):
        residual = x
        x, _ = self.attention(x, x, x)
        x = self.dropout(x)
        x = self.layer_norm(residual + x)
        return x 