import torch
import torch.nn as nn

class QuantileLoss(nn.Module):
    """分位数损失"""
    
    def __init__(self, quantiles=[0.1, 0.5, 0.9]):
        super().__init__()
        self.quantiles = quantiles
        
    def forward(self, preds, target):
        losses = []
        for i, q in enumerate(self.quantiles):
            errors = target - preds[..., i]
            losses.append(
                torch.max(
                    (q - 1) * errors,
                    q * errors
                )
            )
        return torch.mean(torch.sum(torch.stack(losses), dim=0))

class FocalLoss(nn.Module):
    """焦点损失"""
    
    def __init__(self, alpha=1, gamma=2):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        
    def forward(self, inputs, targets):
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1-pt)**self.gamma * ce_loss
        return torch.mean(focal_loss) 