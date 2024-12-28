import torch
import torch.nn as nn
import pytorch_lightning as pl
from typing import List, Dict, Any
from .layers import BaseLayer

class TimeSeriesModel(pl.LightningModule):
    """可配置的时间序列模型"""
    
    def __init__(
        self,
        input_size: int,
        layers_config: List[Dict[str, Any]],
        learning_rate: float = 1e-4
    ):
        super().__init__()
        self.save_hyperparameters()
        
        # 动态创建层
        self.layers = nn.ModuleList()
        current_size = input_size
        
        for layer_config in layers_config:
            layer_type = layer_config.pop('type')
            layer_class = self._get_layer_class(layer_type)
            
            # 更新输入输出大小
            layer_config['input_size'] = current_size
            current_size = layer_config.get('output_size', current_size)
            
            # 创建层
            layer = layer_class(layer_config)
            self.layers.append(layer)
        
        # 输出层
        self.output_head = nn.Linear(current_size, 1)
    
    def _get_layer_class(self, layer_type: str) -> type:
        """获取层类"""
        from .layers import LinearLayer, TransformerLayer
        layer_map = {
            'linear': LinearLayer,
            'transformer': TransformerLayer,
        }
        return layer_map[layer_type]
    
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return self.output_head(x)
    
    def get_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return {
            'input_size': self.hparams.input_size,
            'layers': [layer.get_config() for layer in self.layers],
            'learning_rate': self.hparams.learning_rate
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'TimeSeriesModel':
        """从配置创建模型"""
        return cls(
            input_size=config['input_size'],
            layers_config=config['layers'],
            learning_rate=config['learning_rate']
        ) 