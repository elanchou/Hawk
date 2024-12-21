import torch
import numpy as np
from typing import Dict, List
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.utils.logger import Logger

logger = Logger(__name__)

class ModelEvaluator:
    """模型评估器"""
    
    def __init__(
        self,
        model: torch.nn.Module,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.model = model.to(device)
        self.device = device
    
    def evaluate(self, test_loader) -> Dict[str, float]:
        """评估模型"""
        self.model.eval()
        predictions = []
        targets = []
        
        with torch.no_grad():
            for data, target in test_loader:
                data = data.to(self.device)
                output = self.model(data)
                predictions.extend(output.cpu().numpy())
                targets.extend(target.cpu().numpy())
        
        predictions = np.array(predictions)
        targets = np.array(targets)
        
        metrics = {
            'mse': mean_squared_error(targets, predictions),
            'rmse': np.sqrt(mean_squared_error(targets, predictions)),
            'mae': mean_absolute_error(targets, predictions),
            'r2': r2_score(targets, predictions)
        }
        
        for name, value in metrics.items():
            logger.info(f'{name.upper()}: {value:.6f}')
        
        return metrics
    
    def predict(self, data_loader) -> np.ndarray:
        """使用模型进行预测"""
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for data, _ in data_loader:
                data = data.to(self.device)
                output = self.model(data)
                predictions.extend(output.cpu().numpy())
        
        return np.array(predictions) 