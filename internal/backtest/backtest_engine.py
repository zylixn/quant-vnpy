"""
回测核心引擎
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Direction, Offset, Exchange, Interval

try:
    from vnpy.trader.database import database_manager
except ImportError:
    # 如果database_manager不存在，设置为None
    database_manager = None

try:
    from vnpy.strategy import StrategyTemplate
except ImportError:
    # 如果StrategyTemplate不存在，定义一个空类
    class StrategyTemplate:
        pass

from vnpy_ctastrategy.backtesting import BacktestingEngine as VnpyBacktestingEngine
from vnpy_ctastrategy.base import BacktestingMode


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self):
        """初始化回测引擎"""
        self.engine = VnpyBacktestingEngine()
        self.strategy_class = None
        self.strategy_settings = {}
        self.backtest_results = {}
    
    def set_parameters(self, 
                      vt_symbol: str,          # 合约代码
                      interval: Interval,      # 周期
                      start: datetime,         # 开始时间
                      end: datetime,           # 结束时间
                      rate: float = 0.0001,    # 手续费率
                      slippage: float = 0.0,   # 滑点
                      size: int = 1,           # 合约乘数
                      pricetick: float = 0.01,  # 最小价格变动
                      capital: int = 1000000,   # 初始资金
                      mode: BacktestingMode = BacktestingMode.BAR  # 回测模式
                      ):
        """设置回测参数"""
        self.engine.set_parameters(
            vt_symbol=vt_symbol,
            interval=interval,
            start=start,
            end=end,
            rate=rate,
            slippage=slippage,
            size=size,
            pricetick=pricetick,
            capital=capital,
            mode=mode
        )
    
    def add_strategy(self, 
                    strategy_class: type,  # 策略类
                    settings: Dict[str, Any] = {}  # 策略参数
                    ):
        """添加策略"""
        self.strategy_class = strategy_class
        self.strategy_settings = settings
        self.engine.add_strategy(strategy_class, settings)
    
    def load_data(self, 
                 data: Optional[List[BarData]] = None,  # 数据
                 filename: Optional[str] = None  # 文件名
                 ):
        """加载数据"""
        if data:
            self.engine.data_manager.set_data(data)
        elif filename:
            self.engine.load_data(filename=filename)
        else:
            # 从数据库加载数据
            self.engine.load_data()
    
    def run_backtesting(self) -> Dict[str, Any]:
        """运行回测"""
        self.engine.run_backtesting()
        self.backtest_results = self.engine.calculate_result()
        return self.backtest_results
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """计算统计指标"""
        if not self.backtest_results:
            self.run_backtesting()
        
        statistics = self.engine.calculate_statistics()
        return statistics
    
    def show_chart(self):
        """显示回测图表"""
        if not self.backtest_results:
            self.run_backtesting()
        
        self.engine.show_chart()
    
    def export_results(self, 
                      filename: str = "backtest_results.json"  # 文件名
                      ):
        """导出回测结果"""
        if not self.backtest_results:
            self.run_backtesting()
        
        statistics = self.calculate_statistics()
        
        results = {
            "backtest_results": self.backtest_results.to_dict(),
            "statistics": statistics,
            "strategy": {
                "class_name": self.strategy_class.__name__,
                "settings": self.strategy_settings
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def get_trades(self) -> List[TradeData]:
        """获取成交记录"""
        return self.engine.trades
    
    def get_orders(self) -> List[OrderData]:
        """获取订单记录"""
        return self.engine.orders
    
    def get_daily_results(self) -> Dict[datetime, float]:
        """获取每日结果"""
        if not self.backtest_results:
            self.run_backtesting()
        
        return self.backtest_results.to_dict()


class BacktestEngineAdapter:
    """回测引擎适配器，用于适配不同的数据源和策略"""
    
    @staticmethod
    def create_backtest_engine() -> BacktestEngine:
        """创建回测引擎"""
        return BacktestEngine()
    
    @staticmethod
    def convert_to_bar_data(data: List[Dict[str, Any]]) -> List[BarData]:
        """将字典数据转换为BarData"""
        bars = []
        for item in data:
            bar = BarData(
                symbol=item.get('symbol', ''),
                exchange=Exchange(item.get('exchange', 'SHFE')),
                datetime=datetime.fromisoformat(item['datetime']),
                interval=Interval(item.get('interval', '1m')),
                open_price=item.get('open', 0.0),
                high_price=item.get('high', 0.0),
                low_price=item.get('low', 0.0),
                close_price=item.get('close', 0.0),
                volume=item.get('volume', 0),
                open_interest=item.get('open_interest', 0),
                gateway_name="BACKTEST"
            )
            bars.append(bar)
        return bars
    
    @staticmethod
    def generate_test_data(symbol: str = "BTC/USDT", 
                          exchange: str = "BINANCE",
                          start: datetime = datetime(2023, 1, 1),
                          end: datetime = datetime(2023, 1, 31),
                          interval: str = "1h") -> List[BarData]:
        """生成测试数据"""
        import random
        
        bars = []
        current_price = 50000.0
        
        from vnpy.trader.utility import BarGenerator
        bg = BarGenerator(on_bar=None, interval=Interval(interval))
        
        for i in range((end - start).days * 24):
            dt = start + pd.Timedelta(hours=i)
            
            # 生成随机价格
            change = random.uniform(-1, 1) * 1000
            open_price = current_price
            high_price = max(current_price, current_price + change)
            low_price = min(current_price, current_price + change)
            close_price = current_price + change
            volume = random.randint(1000, 10000)
            
            bar = BarData(
                symbol=symbol,
                exchange=Exchange(exchange),
                datetime=dt,
                interval=Interval(interval),
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                volume=volume,
                open_interest=0,
                gateway_name="BACKTEST"
            )
            
            bars.append(bar)
            current_price = close_price
        
        return bars


# 导入必要的库
import pandas as pd
