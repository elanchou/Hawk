import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class LSTMLayer(BaseLayer):
    """LSTM层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.lstm = nn.LSTM(
            input_size=config['input_size'],
            hidden_size=config['hidden_size'],
            num_layers=config.get('num_layers', 1),
            dropout=config.get('dropout', 0.1),
            bidirectional=config.get('bidirectional', False),
            batch_first=True
        )
        self.dropout = nn.Dropout(config.get('dropout', 0.1))
    
    def forward(self, x):
        x, _ = self.lstm(x)
        return self.dropout(x) 