import os
import yaml
from typing import Dict, Any
from pathlib import Path

class Config:
    """配置管理类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            self._create_default_config()
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            'api': {
                'binance': {
                    'api_key': '',
                    'api_secret': '',
                    'testnet': True
                }
            },
            'database': {
                'url': 'sqlite:///trading.db',
                'echo': False
            },
            'trading': {
                'symbols': ['BTCUSDT'],
                'intervals': ['1m', '5m', '15m'],
                'risk_per_trade': 0.02,
                'max_positions': 3
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'trading.log'
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False)
            
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default 