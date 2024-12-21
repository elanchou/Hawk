import sys
import os
from pathlib import Path
import shutil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import Logger

logger = Logger(__name__)

def init_project():
    """初始化项目目录结构"""
    try:
        # 创建必要的目录
        directories = [
            'data',
            'logs',
            'outputs/models',
            'outputs/logs',
            'src/api',
            'src/config',
            'src/data/collectors',
            'src/ml/features',
            'src/ml/models',
            'src/ml/training',
            'src/ml/utils',
            'src/models',
            'src/utils',
            'tests'
        ]
        
        for dir_path in directories:
            full_path = project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {full_path}")
        
        # 复制配置文件模板（如果不存在）
        config_example = project_root / 'src' / 'config' / 'config.example.yaml'
        config_file = project_root / 'src' / 'config' / 'config.yaml'
        
        if not config_file.exists() and config_example.exists():
            shutil.copy(config_example, config_file)
            logger.info(f"创建配置文件: {config_file}")
        
        # 创建必要的空文件
        files = [
            'src/api/__init__.py',
            'src/config/__init__.py',
            'src/data/__init__.py',
            'src/data/collectors/__init__.py',
            'src/ml/__init__.py',
            'src/ml/features/__init__.py',
            'src/ml/models/__init__.py',
            'src/ml/training/__init__.py',
            'src/ml/utils/__init__.py',
            'src/models/__init__.py',
            'src/utils/__init__.py',
            'tests/__init__.py'
        ]
        
        for file_path in files:
            full_path = project_root / file_path
            if not full_path.exists():
                full_path.touch()
                logger.info(f"创建文件: {full_path}")
        
        logger.info("项目初始化完成")
        
    except Exception as e:
        logger.error(f"项目初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_project() 