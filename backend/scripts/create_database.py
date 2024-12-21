import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.models.database import Base, DatabaseManager
from src.utils.logger import Logger

logger = Logger(__name__)

def create_database():
    """创建数据库表"""
    try:
        db = DatabaseManager()
        Base.metadata.create_all(db.engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database() 