"""
配置管理模块
"""

from internal.config.config_manager import ConfigManager, get_config, TomlConfig

__all__ = [
    'ConfigManager',
    'get_config',
    'TomlConfig',
]
