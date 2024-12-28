import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class LinearLayer(BaseLayer):
    """线性层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.linear = nn.Linear(
            config['input_size'],
            config['output_size']
        )
        self.activation = getattr(nn, config.get('activation', 'ReLU'))()
        self.dropout = nn.Dropout(config.get('dropout', 0.1))
    
    def forward(self, x):
        x = self.linear(x)
        x = self.activation(x)
        return self.dropout(x) 