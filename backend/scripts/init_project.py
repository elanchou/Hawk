import sys
import os
from pathlib import Path
import shutil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.src.utils.logger import Logger
from src.config.config import Config

logger = Logger(__name__)

def init_project():
    """初始化项目目录和配置"""
    try:
        # 创建必要的目录
        data_dir = project_root / 'data'
        logs_dir = project_root / 'logs'
        config_dir = project_root / 'src' / 'config'
        
        data_dir.mkdir(exist_ok=True)
        logs_dir.mkdir(exist_ok=True)
        
        # 复制配置文件模板（如果不存在）
        config_example = config_dir / 'config.example.yaml'
        config_file = config_dir / 'config.yaml'
        
        if not config_file.exists() and config_example.exists():
            shutil.copy(config_example, config_file)
            logger.info(f"已创建配置文件: {config_file}")
        
        logger.info("项目初始化完成")
        logger.info(f"数据目录: {data_dir}")
        logger.info(f"日志目目录: {logs_dir}")
        logger.info(f"配置文件: {config_file}")
        
    except Exception as e:
        logger.error(f"项目初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_project() 