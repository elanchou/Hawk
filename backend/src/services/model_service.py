from typing import Dict, Any, List, Optional
import torch
import json
from pathlib import Path
from datetime import datetime
from ..ml.models.layers import (
    LinearLayer, LSTMLayer, GRULayer, 
    CNNLayer, AttentionLayer, TCNLayer,
    ResidualLayer
)
from ..utils.logger import Logger

logger = Logger(__name__)

class ModelService:
    """模型服务"""
    
    LAYER_TYPES = {
        'linear': LinearLayer,
        'lstm': LSTMLayer,
        'gru': GRULayer,
        'cnn': CNNLayer,
        'attention': AttentionLayer,
        'tcn': TCNLayer,
        'residual': ResidualLayer
    }
    
    def __init__(self, model_dir: str = 'outputs/models'):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def create_model(self, config: Dict[str, Any]) -> torch.nn.Module:
        """从配置创建模型"""
        layers = []
        current_size = config['input_size']
        
        for layer_config in config['layers']:
            layer_type = layer_config['type']
            if layer_type not in self.LAYER_TYPES:
                raise ValueError(f"���知的层类型: {layer_type}")
            
            # 更新输入输出大小
            layer_config['input_size'] = current_size
            current_size = layer_config.get('hidden_size', current_size)
            
            # 创建层
            layer_class = self.LAYER_TYPES[layer_type]
            layer = layer_class(layer_config)
            layers.append(layer)
        
        # 创建模型
        model = torch.nn.Sequential(*layers)
        return model
    
    def save_model(
        self,
        model: torch.nn.Module,
        config: Dict[str, Any],
        name: Optional[str] = None
    ) -> str:
        """保存模型"""
        if name is None:
            name = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存模型文件
        model_path = self.model_dir / f"{name}.pth"
        torch.save({
            'state_dict': model.state_dict(),
            'config': config
        }, model_path)
        
        # 保存配置文件
        config_path = self.model_dir / f"{name}_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return str(model_path)
    
    def load_model(self, name: str) -> tuple[torch.nn.Module, Dict[str, Any]]:
        """加载模型"""
        model_path = self.model_dir / f"{name}.pth"
        if not model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        checkpoint = torch.load(model_path)
        model = self.create_model(checkpoint['config'])
        model.load_state_dict(checkpoint['state_dict'])
        
        return model, checkpoint['config']
    
    def list_models(self) -> List[Dict[str, Any]]:
        """获取所有可用模型"""
        models = []
        for model_path in self.model_dir.glob('*_config.json'):
            name = model_path.stem.replace('_config', '')
            with open(model_path) as f:
                config = json.load(f)
            
            models.append({
                'name': name,
                'config': config,
                'created_at': datetime.fromtimestamp(model_path.stat().st_ctime)
            })
        
        return models
    
    def delete_model(self, name: str):
        """删除模型"""
        model_path = self.model_dir / f"{name}.pth"
        config_path = self.model_dir / f"{name}_config.json"
        
        if model_path.exists():
            model_path.unlink()
        if config_path.exists():
            config_path.unlink() 