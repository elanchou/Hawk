import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.cuda.amp import GradScaler, autocast
from transformers import get_linear_schedule_with_warmup
import numpy as np
from typing import Dict, Optional
from src.utils.logger import Logger

logger = Logger(__name__)

class ModelTrainer:
    """模型训练器"""
    
    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-4,
        device: str = 'cuda',
        fp16: bool = True,
        warmup_steps: int = 1000
    ):
        self.model = model
        self.device = device
        self.fp16 = fp16
        self.warmup_steps = warmup_steps
        
        # 优化器
        self.optimizer = AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=0.01
        )
        
        # 损失函数
        self.criterion = nn.MSELoss()
        
        # 混合精度训练
        self.scaler = GradScaler() if fp16 else None
    
    def train_epoch(self, train_loader, scheduler):
        """训练一个epoch"""
        self.model.train()
        total_loss = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data = data.to(self.device)
            target = target.to(self.device)
            
            self.optimizer.zero_grad()
            
            if self.fp16:
                with autocast():
                    output = self.model(data)
                    loss = self.criterion(output, target)
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                output = self.model(data)
                loss = self.criterion(output, target)
                loss.backward()
                self.optimizer.step()
            
            if scheduler is not None:
                scheduler.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader):
        """验证模型"""
        self.model.eval()
        total_loss = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = self.criterion(output, target)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def train(
        self,
        train_loader,
        val_loader,
        num_epochs: int,
        model_path: Optional[str] = None
    ):
        """训练模型"""
        # 创建学习率调度器
        total_steps = len(train_loader) * num_epochs
        scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=total_steps
        )
        
        best_val_loss = float('inf')
        
        for epoch in range(num_epochs):
            train_loss = self.train_epoch(train_loader, scheduler)
            val_loss = self.validate(val_loader)
            
            logger.info(f'Epoch: {epoch+1}/{num_epochs}')
            logger.info(f'Train Loss: {train_loss:.6f}')
            logger.info(f'Val Loss: {val_loss:.6f}')
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                if model_path:
                    self.save_checkpoint(model_path, epoch, val_loss)
    
    def save_checkpoint(self, path: str, epoch: int, val_loss: float):
        """保存模型检查点"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'val_loss': val_loss
        }
        if self.scaler is not None:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()
        torch.save(checkpoint, path)