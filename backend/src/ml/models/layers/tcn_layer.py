import torch
import torch.nn as nn
from typing import Dict, Any
from .base_layer import BaseLayer

class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, dropout=0.2):
        super().__init__()
        self.conv1 = nn.Conv1d(
            n_inputs, n_outputs, kernel_size,
            stride=stride, padding=padding, dilation=dilation
        )
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)
        
        self.conv2 = nn.Conv1d(
            n_outputs, n_outputs, kernel_size,
            stride=stride, padding=padding, dilation=dilation
        )
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)
        
        self.net = nn.Sequential(
            self.conv1, self.relu1, self.dropout1,
            self.conv2, self.relu2, self.dropout2
        )
        
        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        self.relu = nn.ReLU()
        
    def forward(self, x):
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)

class TCNLayer(BaseLayer):
    """时间卷积网络层"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tcn = TemporalBlock(
            n_inputs=config['input_size'],
            n_outputs=config['hidden_size'],
            kernel_size=config.get('kernel_size', 3),
            stride=1,
            dilation=config.get('dilation', 1),
            padding=config.get('kernel_size', 3) // 2,
            dropout=config.get('dropout', 0.1)
        )
    
    def forward(self, x):
        # 调整维度顺序以适应TCN (batch, time, features) -> (batch, features, time)
        x = x.transpose(1, 2)
        x = self.tcn(x)
        # 恢复维度顺序 (batch, features, time) -> (batch, time, features)
        x = x.transpose(1, 2)
        return x 