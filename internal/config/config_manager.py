import os
import tomllib
from typing import Dict, Any


class TomlConfig:
    """从toml文件读取配置的配置类"""
    
    @classmethod
    def _load_toml_config(cls) -> Dict[str, Any]:
        """从toml文件加载配置
        
        Returns:
            配置字典
        """
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cfg', 'unios.toml')
        if os.path.exists(config_path):
            with open(config_path, 'rb') as f:
                return tomllib.load(f)
        return {}
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        config = cls._load_toml_config()
        keys = key.split('.')
        value = config
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default
        return value
    
    # 基础配置
    @property
    def DEBUG(self):
        return self.get('basic.DEBUG', True)
    
    @property
    def SECRET_KEY(self):
        return self.get('basic.SECRET_KEY', 'your-secret-key-here')
    
    # 数据库配置
    @property
    def DATABASE_NAME(self):
        return self.get('database.DATABASE_NAME', 'vnpy')
    
    @property
    def DATABASE_HOST(self):
        return self.get('database.DATABASE_HOST', 'localhost')
    
    @property
    def DATABASE_PORT(self):
        return self.get('database.DATABASE_PORT', 3306)
    
    @property
    def DATABASE_USER(self):
        return self.get('database.DATABASE_USER', 'root')
    
    @property
    def DATABASE_PASSWORD(self):
        return self.get('database.DATABASE_PASSWORD', 'password')
    
    # 交易接口配置
    @property
    def GATEWAY_NAME(self):
        return self.get('gateway.GATEWAY_NAME', 'CTP')
    
    @property
    def GATEWAY_SETTING(self):
        return self.get('gateway.setting', {
            'userid': '',
            'password': '',
            'brokerid': '',
            'td_address': '',
            'md_address': '',
            'app_id': '',
            'auth_code': '',
        })
    
    # 日志配置
    @property
    def LOG_LEVEL(self):
        return self.get('logging.LOG_LEVEL', 'INFO')
    
    @property
    def LOG_FILE(self):
        return self.get('logging.LOG_FILE', 'logs/vnpy.log')
    
    @property
    def LOG_CONSOLE(self):
        return self.get('logging.LOG_CONSOLE', True)
    
    # 日志分割配置
    @property
    def LOG_ROTATION_TYPE(self):
        return self.get('logging.rotation.LOG_ROTATION_TYPE', 'size')
    
    @property
    def LOG_MAX_BYTES(self):
        return self.get('logging.rotation.LOG_MAX_BYTES', 10 * 1024 * 1024)
    
    @property
    def LOG_ROTATION_WHEN(self):
        return self.get('logging.rotation.LOG_ROTATION_WHEN', 'D')
    
    @property
    def LOG_ROTATION_INTERVAL(self):
        return self.get('logging.rotation.LOG_ROTATION_INTERVAL', 1)
    
    @property
    def LOG_BACKUP_COUNT(self):
        return self.get('logging.rotation.LOG_BACKUP_COUNT', 5)
    
    # 日志清理配置
    @property
    def LOG_CLEANUP_ENABLED(self):
        return self.get('logging.cleanup.LOG_CLEANUP_ENABLED', True)
    
    @property
    def LOG_DAYS_TO_KEEP(self):
        return self.get('logging.cleanup.LOG_DAYS_TO_KEEP', 7)
    
    # 策略配置
    @property
    def STRATEGY_NAME(self):
        return self.get('strategy.STRATEGY_NAME', 'my_strategy')
    
    @property
    def STRATEGY_SYMBOL(self):
        return self.get('strategy.STRATEGY_SYMBOL', 'IF2312.CFFEX')
    
    @property
    def STRATEGY_INTERVAL(self):
        return self.get('strategy.STRATEGY_INTERVAL', '1m')
    
    # 风控配置
    @property
    def MAX_POSITION_SIZE(self):
        return self.get('risk.MAX_POSITION_SIZE', 10)
    
    @property
    def MAX_DAILY_TRADES(self):
        return self.get('risk.MAX_DAILY_TRADES', 100)
    
    @property
    def MAX_DAILY_LOSS(self):
        return self.get('risk.MAX_DAILY_LOSS', 10000)
    
    @property
    def STOP_LOSS_RATIO(self):
        return self.get('risk.STOP_LOSS_RATIO', 0.02)
    
    @property
    def TAKE_PROFIT_RATIO(self):
        return self.get('risk.TAKE_PROFIT_RATIO', 0.03)
    
    # 回测配置
    @property
    def BACKTEST_START(self):
        return self.get('backtest.BACKTEST_START', '2023-01-01')
    
    @property
    def BACKTEST_END(self):
        return self.get('backtest.BACKTEST_END', '2023-12-31')
    
    @property
    def BACKTEST_CAPITAL(self):
        return self.get('backtest.BACKTEST_CAPITAL', 1000000)
    
    @property
    def BACKTEST_RATE(self):
        return self.get('backtest.BACKTEST_RATE', 0.0001)
    
    @property
    def BACKTEST_SLIPPAGE(self):
        return self.get('backtest.BACKTEST_SLIPPAGE', 0.0)
    
    @property
    def BACKTEST_SIZE(self):
        return self.get('backtest.BACKTEST_SIZE', 1)
    
    @property
    def BACKTEST_PRICETICK(self):
        return self.get('backtest.BACKTEST_PRICETICK', 0.01)
    
    # 股票交易配置
    @property
    def DIVIDEND_ADJUSTMENT_ENABLED(self):
        return self.get('stock.DIVIDEND_ADJUSTMENT_ENABLED', True)
    
    @property
    def DIVIDEND_DATA_PATH(self):
        return self.get('stock.DIVIDEND_DATA_PATH', 'data/dividends')
    
    @property
    def DIVIDEND_UPDATE_INTERVAL(self):
        return self.get('stock.DIVIDEND_UPDATE_INTERVAL', 30)
    
    # 交易成本配置
    @property
    def TRADING_COST_CONFIG(self):
        return self.get('trading_cost', {
            'commission_rate': 0.0003,
            'min_commission': 5.0,
            'stamp_tax_rate': 0.001,
            'transfer_fee_rate': 0.00002,
            'min_transfer_fee': 0.0,
            'jing_shou_fee_rate': 0.0000487,
            'supervision_fee_rate': 0.00002,
            'other_fees': 0.0
        })
    
    # 券商配置
    @property
    def BROKER_NAME(self):
        return self.get('broker.BROKER_NAME', '华泰证券')
    
    @property
    def BROKER_CONFIG(self):
        return self.get('broker.config', {
            'user_id': '',
            'password': '',
            'broker_id': '',
            'app_id': '',
            'auth_code': ''
        })
    
    # 股票账户配置
    @property
    def ACCOUNT_CONFIG(self):
        return self.get('account', {
            'initial_balance': 1000000,
            'max_position_per_stock': 0.3,
            'max_position_per_industry': 0.5,
            'total_positions_limit': 20
        })
    
    # 交易时间配置
    @property
    def TRADING_TIME_CONFIG(self):
        return self.get('trading_time', {
            'market': 'A_SHARE',
            'holiday_file': 'data/holidays.json',
            'special_trading_days': {}
        })
    
    # 停牌股票配置
    @property
    def SUSPENDED_STOCKS_FILE(self):
        return self.get('suspended_stocks.SUSPENDED_STOCKS_FILE', 'data/suspended_stocks.json')
    
    @property
    def SUSPENDED_STOCKS_UPDATE_INTERVAL(self):
        return self.get('suspended_stocks.SUSPENDED_STOCKS_UPDATE_INTERVAL', 60)
    
    # 数据源配置
    @property
    def DATA_SOURCE(self):
        return self.get('data_source.DATA_SOURCE', 'tushare')
    
    @property
    def DATA_TOKEN(self):
        return self.get('data_source.DATA_TOKEN', '')
    
    @property
    def TUSHARE_TOKEN(self):
        return self.get('data_source.TUSHARE_TOKEN', '')
    
    @property
    def AKSHARE_TOKEN(self):
        return self.get('data_source.AKSHARE_TOKEN', '')
    
    @property
    def BAOSTOCK_TOKEN(self):
        return self.get('data_source.BAOSTOCK_TOKEN', '')
    
    @property
    def DATA_CACHE_DIR(self):
        return self.get('data_source.DATA_CACHE_DIR', 'data/cache')
    
    @property
    def DATA_DOWNLOAD_DIR(self):
        return self.get('data_source.DATA_DOWNLOAD_DIR', 'data/download')
    
    @property
    def API_HOST(self):
        return self.get('api.API_HOST', '0.0.0.0')
    
    @property
    def API_PORT(self):
        return self.get('api.API_PORT', 5000)
    
    @property
    def API_PREFIX(self):
        return self.get('api.API_PREFIX', '/api')
    
    @property
    def TASK_TIMEOUT(self):
        return self.get('task.TASK_TIMEOUT', 3600)
    
    @property
    def TASK_MAX_RETRIES(self):
        return self.get('task.TASK_MAX_RETRIES', 3)
    
    @property
    def TASK_LOG_DIR(self):
        return self.get('task.TASK_LOG_DIR', 'logs/tasks')


class ConfigManager:
    """配置管理器"""
    
    _configs = {
        'development': 'internal.config.config_dev.DevelopmentConfig',
        'production': 'internal.config.config_prod.ProductionConfig',
        'testing': 'internal.config.config_test.TestingConfig',
        'default': 'internal.config.config.Config'
    }
    
    @classmethod
    def get_config(cls, env: str = None) -> Any:
        """获取配置对象
        
        Args:
            env: 环境名称，默认从环境变量 FLASK_ENV 读取
            
        Returns:
            配置类实例
        """
        # 直接返回TomlConfig类，它会从cfg/unios.toml读取配置
        return TomlConfig
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, Any]:
        """获取所有配置
        
        Returns:
            所有配置的字典
        """
        configs = {}
        for env, config_path in cls._configs.items():
            module_path, class_name = config_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            config_class = getattr(module, class_name)
            configs[env] = config_class
        return configs
    
    @classmethod
    def get_env_config(cls) -> Dict[str, str]:
        """获取环境变量配置
        
        Returns:
            环境变量字典
        """
        return {
            'FLASK_ENV': os.getenv('FLASK_ENV', 'default'),
            'FLASK_DEBUG': os.getenv('FLASK_DEBUG', 'False'),
            'DATABASE_HOST': os.getenv('DATABASE_HOST', ''),
            'DATABASE_USER': os.getenv('DATABASE_USER', ''),
            'DATABASE_PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
            'DATA_TOKEN': os.getenv('DATA_TOKEN', ''),
        }


def get_config(env: str = None) -> Any:
    """获取配置对象的便捷函数
    
    Args:
        env: 环境名称
        
    Returns:
        配置类实例
    """
    return ConfigManager.get_config(env)
