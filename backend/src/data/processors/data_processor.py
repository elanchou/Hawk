import pandas as pd
import numpy as np
from typing import Optional, List

class DataProcessor:
    """数据处理类"""
    
    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        method: str = 'ffill'
    ) -> pd.DataFrame:
        """处理缺失值"""
        if method == 'ffill':
            return df.fillna(method='ffill')
        elif method == 'mean':
            return df.fillna(df.mean())
        return df
        
    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
        column: str,
        n_std: float = 3
    ) -> pd.DataFrame:
        """异常值检测"""
        mean = df[column].mean()
        std = df[column].std()
        df[f'{column}_is_outlier'] = (
            (df[column] < mean - n_std * std) |
            (df[column] > mean + n_std * std)
        )
        return df
        
    @staticmethod
    def normalize_data(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """数据归一化"""
        if columns is None:
            columns = df.columns
            
        df_normalized = df.copy()
        for column in columns:
            df_normalized[column] = (
                (df[column] - df[column].min()) /
                (df[column].max() - df[column].min())
            )
        return df_normalized 