"""
初始化 MySQL 数据库
"""

import sys
import os

# 添加项目根目录到 Python 搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymysql
from internal.config import get_config

# 获取配置
config = get_config()()

# MySQL 连接配置
mysql_config = {
    'host': config.DATABASE_HOST,
    'port': config.DATABASE_PORT,
    'user': config.DATABASE_USER,
    'password': config.DATABASE_PASSWORD,
    'charset': 'utf8mb4'
}

def create_database():
    """创建数据库和表"""
    connection = None
    try:
        # 连接到 MySQL 服务器
        connection = pymysql.connect(**mysql_config)
        cursor = connection.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DATABASE_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {config.DATABASE_NAME} 创建成功")
        
        # 选择数据库
        cursor.execute(f"USE {config.DATABASE_NAME}")
        
        # 创建 K 线数据表
        create_bar_table = """
        CREATE TABLE IF NOT EXISTS dbbardata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(32) NOT NULL,
            exchange VARCHAR(32) NOT NULL,
            datetime DATETIME(3) NOT NULL,
            interval VARCHAR(32) NOT NULL,
            volume DOUBLE,
            turnover DOUBLE,
            open_interest DOUBLE,
            open_price DOUBLE,
            high_price DOUBLE,
            low_price DOUBLE,
            close_price DOUBLE,
            UNIQUE KEY idx_symbol_exchange_interval_datetime (symbol, exchange, interval, datetime)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_bar_table)
        print("K 线数据表 dbbardata 创建成功")
        
        # 创建 Tick 数据表
        create_tick_table = """
        CREATE TABLE IF NOT EXISTS dbtickdata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(32) NOT NULL,
            exchange VARCHAR(32) NOT NULL,
            datetime DATETIME(3) NOT NULL,
            name VARCHAR(32),
            volume DOUBLE,
            turnover DOUBLE,
            open_interest DOUBLE,
            last_price DOUBLE,
            last_volume DOUBLE,
            limit_up DOUBLE,
            limit_down DOUBLE,
            open_price DOUBLE,
            high_price DOUBLE,
            low_price DOUBLE,
            pre_close DOUBLE,
            bid_price_1 DOUBLE,
            bid_price_2 DOUBLE,
            bid_price_3 DOUBLE,
            bid_price_4 DOUBLE,
            bid_price_5 DOUBLE,
            ask_price_1 DOUBLE,
            ask_price_2 DOUBLE,
            ask_price_3 DOUBLE,
            ask_price_4 DOUBLE,
            ask_price_5 DOUBLE,
            bid_volume_1 DOUBLE,
            bid_volume_2 DOUBLE,
            bid_volume_3 DOUBLE,
            bid_volume_4 DOUBLE,
            bid_volume_5 DOUBLE,
            ask_volume_1 DOUBLE,
            ask_volume_2 DOUBLE,
            ask_volume_3 DOUBLE,
            ask_volume_4 DOUBLE,
            ask_volume_5 DOUBLE,
            localtime DATETIME(3),
            UNIQUE KEY idx_symbol_exchange_datetime (symbol, exchange, datetime)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_tick_table)
        print("Tick 数据表 dbtickdata 创建成功")
        
        # 创建 K 线汇总表
        create_bar_overview_table = """
        CREATE TABLE IF NOT EXISTS dbbaroverview (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(32) NOT NULL,
            exchange VARCHAR(32) NOT NULL,
            interval VARCHAR(32) NOT NULL,
            count INT,
            start DATETIME,
            end DATETIME,
            UNIQUE KEY idx_symbol_exchange_interval (symbol, exchange, interval)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_bar_overview_table)
        print("K 线汇总表 dbbaroverview 创建成功")
        
        # 创建 Tick 汇总表
        create_tick_overview_table = """
        CREATE TABLE IF NOT EXISTS dbtickoverview (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(32) NOT NULL,
            exchange VARCHAR(32) NOT NULL,
            count INT,
            start DATETIME,
            end DATETIME,
            UNIQUE KEY idx_symbol_exchange (symbol, exchange)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        cursor.execute(create_tick_overview_table)
        print("Tick 汇总表 dbtickoverview 创建成功")
        
        # 提交事务
        connection.commit()
        print("\n所有表创建成功！")
        
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    create_database()
