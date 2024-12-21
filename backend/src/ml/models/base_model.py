from abc import ABC, abstractmethod
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

class BaseModel(nn.Module, ABC):
    """基础模型类"""
    
    def __init__(
        self,
        input_size: int,
        output_size: int,
        hidden_size: int,
        num_layers: int,
        dropout: float = 0.2
    ):
        super().__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        
        # 模型配置
        self.config = {
            'input_size': input_size,
            'output_size': output_size,
            'hidden_size': hidden_size,
            'num_layers': num_layers,
            'dropout': dropout
        }
    
    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """前向传播"""
        pass
    
    def predict(
        self,
        x: torch.Tensor,
        threshold: float = 0.5
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """预测"""
        self.eval()
        with torch.no_grad():
            outputs = self(x)
            probabilities = torch.sigmoid(outputs)
            predictions = (probabilities > threshold).float()
        return predictions, probabilities
    
    def save_model(self, path: str):
        """保存模型"""
        torch.save({
            'model_state_dict': self.state_dict(),
            'config': self.config
        }, path)
    
    @classmethod
    def load_model(cls, path: str):
        """加载模型"""
        checkpoint = torch.load(path)
        model = cls(**checkpoint['config'])
        model.load_state_dict(checkpoint['model_state_dict'])
        return model 