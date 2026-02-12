"""
日志工具模块
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime, timedelta
from internal.config import get_config

# 确保日志目录存在
os.makedirs('logs', exist_ok=True)
os.makedirs('logs/tasks', exist_ok=True)

# 获取配置
config = get_config()()  # 创建TomlConfig实例

# 创建日志器
logger = logging.getLogger('quant-vnpy')
logger.setLevel(getattr(logging, config.LOG_LEVEL))

# 创建日志格式化器
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

# 确定使用哪种处理器
log_handler = None
if config.LOG_ROTATION_TYPE == 'size':
    # 按大小分割
    log_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT
    )
elif config.LOG_ROTATION_TYPE == 'time':
    # 按时间分割
    log_handler = TimedRotatingFileHandler(
        config.LOG_FILE,
        when=config.LOG_ROTATION_WHEN,
        interval=config.LOG_ROTATION_INTERVAL,
        backupCount=config.LOG_BACKUP_COUNT
    )
else:
    # 默认按大小分割
    log_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )

# 设置处理器
log_handler.setLevel(getattr(logging, config.LOG_LEVEL))
log_handler.setFormatter(formatter)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
console_handler.setFormatter(formatter)

# 添加处理器到日志器
logger.addHandler(log_handler)
if config.LOG_CONSOLE:
    logger.addHandler(console_handler)

# 清理过期日志文件
def cleanup_old_logs(log_dir='logs', days_to_keep=7):
    """
    清理过期的日志文件
    
    Args:
        log_dir (str): 日志目录
        days_to_keep (int): 保留日志的天数
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                if file.endswith('.log') or file.endswith('.log.1'):
                    file_path = os.path.join(root, file)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time < cutoff_date:
                        os.remove(file_path)
                        print(f"Removed old log file: {file_path}")
    except Exception as e:
        print(f"Error cleaning up old logs: {str(e)}")

# 定期清理过期日志
if config.LOG_CLEANUP_ENABLED:
    cleanup_old_logs(
        log_dir=os.path.dirname(config.LOG_FILE),
        days_to_keep=config.LOG_DAYS_TO_KEEP
    )

# 导出日志器
def get_logger(name=None):
    """
    获取指定名称的日志器
    
    Args:
        name (str): 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    if name:
        return logging.getLogger(f'quant-vnpy.{name}')
    return logger

# 示例用法
if __name__ == '__main__':
    # 获取日志器
    app_logger = get_logger('app')
    
    # 记录不同级别的日志
    app_logger.debug('调试信息')
    app_logger.info('信息')
    app_logger.warning('警告')
    app_logger.error('错误')
    app_logger.critical('严重错误')
