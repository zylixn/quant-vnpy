from flask import Flask
from flask_restx import Api
from internal.config import ConfigManager, get_config, TomlConfig
from app.api.resources.health import health_ns
from internal.utils import get_logger
from internal.database import init_vnpy_database
from internal.trading.api.routes import trading_ns
from internal.risk.routes import risk_ns
from internal.fetcher.api.routes import fetcher_ns
from internal.task.api.routes import tasks_ns
from internal.backtest.api.routes import backtest_ns

# 初始化日志
def initialize_logging():
    """初始化日志系统"""
    logger = get_logger('app')
    logger.info('Logging system initialized')

def initialize_vnpy():
    """初始化 vnpy 数据库"""
    try:
        init_vnpy_database()
    except Exception as e:
        logger = get_logger('app')
        logger.error(f"初始化 vnpy 失败: {e}")

def create_app(config_name=None):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(TomlConfig())  # 使用TomlConfig类
    
    # 初始化日志系统
    initialize_logging()
    
    # 初始化 vnpy 数据库
    initialize_vnpy()
    # 创建Flask-RESTX Api对象，用于生成Swagger文档
    api = Api(
        app,
        version='1.0',
        title='Quant-VNPY API',
        description='量化交易系统API文档',
        doc='/docs',  # Swagger文档的访问路径
        prefix=''  # 前缀设置为空字符串
    )
    
    # 注册健康检查命名空间
    api.add_namespace(health_ns, path='/api/health')
    
    # 注册交易命名空间
    api.add_namespace(trading_ns, path='/api/trading')
    
    # 注册风险评估命名空间
    api.add_namespace(risk_ns, path='/api/risk')
    
    # 注册股票数据获取命名空间
    api.add_namespace(fetcher_ns, path='/api/fetcher')
    
    # 注册任务管理命名空间
    api.add_namespace(tasks_ns, path='/api/tasks')
    
    # 注册回测命名空间
    api.add_namespace(backtest_ns, path='/api/backtest')
    
    return app

__all__ = [
    'ConfigManager',
    'get_config',
    'TomlConfig',
    'create_app',
]