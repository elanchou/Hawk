from typing import Tuple, List, Optional
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler

class TimeSeriesDataset(Dataset):
    """时间序列数据集"""
    
    def __init__(
        self,
        data: np.ndarray,
        sequence_length: int,
        target_columns: List[int]
    ):
        self.data = torch.FloatTensor(data)
        self.sequence_length = sequence_length
        self.target_columns = target_columns
    
    def __len__(self) -> int:
        return len(self.data) - self.sequence_length
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self.data[idx:idx + self.sequence_length]
        y = self.data[idx + self.sequence_length, self.target_columns]
        return x, y

class MarketDataLoader:
    """市场数据加载器"""
    
    def __init__(
        self,
        db_manager,
        sequence_length: int = 60,
        batch_size: int = 32,
        train_split: float = 0.8,
        val_split: float = 0.1
    ):
        self.db_manager = db_manager
        self.sequence_length = sequence_length
        self.batch_size = batch_size
        self.train_split = train_split
        self.val_split = val_split
        self.scaler = StandardScaler()
    
    def load_data(
        self,
        symbol: str,
        interval: str,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        feature_generator = None
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """加载数据"""
        # 从数据库加载数据
        session = self.db_manager.get_session()
        try:
            query = f"""
                SELECT * FROM market_data 
                WHERE symbol = '{symbol}' 
                AND interval = '{interval}'
                AND timestamp BETWEEN '{start_time}' AND '{end_time}'
                ORDER BY timestamp ASC
            """
            df = pd.read_sql(query, session.bind)
        finally:
            session.close()
        
        # 生成特征
        if feature_generator:
            df = feature_generator.generate_features(df)
        
        # 准备数据
        data = df.select_dtypes(include=[np.number]).values
        data = self.scaler.fit_transform(data)
        
        # 划分数据集
        train_size = int(len(data) * self.train_split)
        val_size = int(len(data) * self.val_split)
        
        train_data = data[:train_size]
        val_data = data[train_size:train_size + val_size]
        test_data = data[train_size + val_size:]
        
        # 创建数据加载器
        target_columns = [df.columns.get_loc('close')]  # 使用收盘价作为目标
        
        train_dataset = TimeSeriesDataset(train_data, self.sequence_length, target_columns)
        val_dataset = TimeSeriesDataset(val_data, self.sequence_length, target_columns)
        test_dataset = TimeSeriesDataset(test_data, self.sequence_length, target_columns)
        
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size)
        
        return train_loader, val_loader, test_loader 