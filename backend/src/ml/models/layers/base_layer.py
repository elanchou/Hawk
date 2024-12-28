from abc import ABC, abstractmethod
import torch.nn as nn
from typing import Dict, Any

class BaseLayer(nn.Module, ABC):
    """基础层接口"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
    
    @abstractmethod
    def forward(self, x):
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """获取层配置"""
        return self.config
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BaseLayer':
        """从配置创建层"""
        return cls(config) 