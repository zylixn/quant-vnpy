"""
vnpy 数据库初始化模块
"""

import os
from internal.config import get_config
from internal.utils import get_logger

logger = get_logger("vnpy_init")

def init_vnpy_database():
    """初始化 vnpy 数据库连接"""
    try:
        from vnpy.trader.database import SETTINGS, get_database
        
        # 从配置文件获取数据库配置
        config = get_config()
        config_instance = config()
        database_name = config_instance.DATABASE_NAME
        database_host = config_instance.DATABASE_HOST
        database_port = config_instance.DATABASE_PORT
        database_user = config_instance.DATABASE_USER
        database_password = config_instance.DATABASE_PASSWORD
        
        logger.info(f"初始化 vnpy 数据库: {database_user}@{database_host}:{database_port}/{database_name}")
        
        # 根据配置初始化数据库
        try:
            SETTINGS['database.name'] = 'mysql'
            SETTINGS['database.database'] = database_name
            SETTINGS['database.host'] = database_host
            SETTINGS['database.port'] = database_port
            SETTINGS['database.user'] = database_user
            SETTINGS['database.password'] = database_password
            
            from vnpy_mysql.mysql_database import MysqlDatabase
            
            db = get_database()
            logger.info("vnpy MySQL 数据库连接成功")
            
        except (ImportError, Exception) as e:
            logger.warning(f"vnpy_mysql 连接失败: {e}，使用 SQLite 数据库")
            
            SETTINGS['database.name'] = 'sqlite'
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'vnpy_trader.db')
            SETTINGS['database.database'] = db_path
            
            from vnpy_sqlite.sqlite_database import SqliteDatabase
            
            db = get_database()
            logger.info(f"vnpy SQLite 数据库连接成功: {db_path}")
            
    except ImportError as e:
        logger.error(f"无法导入 vnpy 数据库模块: {e}")
        logger.warning("vnpy 数据库功能将不可用")
    except Exception as e:
        logger.error(f"初始化 vnpy 数据库失败: {e}")
        logger.warning("vnpy 数据库功能将不可用")

def get_vnpy_database():
    """获取 vnpy 数据库管理器"""
    try:
        from vnpy.trader.database import get_database
        return get_database()
    except ImportError:
        logger.warning("vnpy 数据库管理器不可用")
        return None
