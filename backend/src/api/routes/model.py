from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ...ml.models import TimeSeriesModel

router = APIRouter()

@router.get("/model/config")
async def get_model_config():
    """获取当前模型配置"""
    model = TimeSeriesModel.load_from_checkpoint("path/to/model.ckpt")
    return model.get_config()

@router.post("/model/update")
async def update_model_config(config: Dict[str, Any]):
    """更新模型配置"""
    try:
        # 创建新模型
        model = TimeSeriesModel.from_config(config)
        # 保存模型
        model.save_checkpoint("path/to/model.ckpt")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/model/layer_types")
async def get_layer_types():
    """获取可用的层类型"""
    return {
        "linear": {
            "params": {
                "output_size": "int",
                "activation": ["ReLU", "Tanh", "GELU"],
                "dropout": "float"
            }
        },
        "transformer": {
            "params": {
                "hidden_size": "int",
                "num_heads": "int",
                "dropout": "float"
            }
        }
    } 