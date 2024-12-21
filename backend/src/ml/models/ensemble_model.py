import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Optional
from .base_model import BaseModel
from src.utils.logger import Logger

logger = Logger(__name__)

class EnsembleModel(BaseModel):
    """集成模型"""
    
    def __init__(
        self,
        models: List[BaseModel],
        weights: Optional[List[float]] = None,
        aggregation_method: str = 'weighted_average'
    ):
        super().__init__(
            input_size=models[0].input_size,
            output_size=models[0].output_size,
            hidden_size=models[0].hidden_size,
            num_layers=models[0].num_layers
        )
        self.models = nn.ModuleList(models)
        self.weights = weights if weights else [1.0/len(models)] * len(models)
        self.aggregation_method = aggregation_method
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        predictions = []
        for model in self.models:
            pred = model(x)
            predictions.append(pred)
        
        if self.aggregation_method == 'weighted_average':
            # 加权平均
            ensemble_pred = torch.zeros_like(predictions[0])
            for pred, weight in zip(predictions, self.weights):
                ensemble_pred += weight * pred
        elif self.aggregation_method == 'median':
            # 中位数
            stacked_preds = torch.stack(predictions, dim=0)
            ensemble_pred = torch.median(stacked_preds, dim=0)[0]
        else:
            # 简单平均
            stacked_preds = torch.stack(predictions, dim=0)
            ensemble_pred = torch.mean(stacked_preds, dim=0)
        
        return ensemble_pred
    
    def optimize_weights(
        self,
        val_loader,
        criterion: nn.Module = nn.MSELoss(),
        num_iterations: int = 1000,
        learning_rate: float = 0.01
    ):
        """优化集成权重"""
        device = next(self.parameters()).device
        weights = torch.tensor(self.weights, device=device, requires_grad=True)
        optimizer = torch.optim.Adam([weights], lr=learning_rate)
        
        best_loss = float('inf')
        best_weights = weights.clone()
        
        for i in range(num_iterations):
            total_loss = 0
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                
                # 获取每个模型的预测
                predictions = []
                for model in self.models:
                    pred = model(data)
                    predictions.append(pred)
                
                # 计算加权平均
                ensemble_pred = torch.zeros_like(predictions[0])
                for pred, weight in zip(predictions, torch.softmax(weights, dim=0)):
                    ensemble_pred += weight * pred
                
                loss = criterion(ensemble_pred, target)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(val_loader)
            if avg_loss < best_loss:
                best_loss = avg_loss
                best_weights = weights.clone()
            
            if i % 100 == 0:
                logger.info(f'Iteration {i}, Loss: {avg_loss:.6f}')
        
        # 更新权重
        self.weights = torch.softmax(best_weights, dim=0).detach().cpu().numpy()
        logger.info(f'Optimized weights: {self.weights}') 