"""
股票交易功能测试

测试股票交易相关模块的功能
"""

import unittest
from datetime import datetime, time
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from internal.data.dividend_adjustment import DividendEvent, DividendAdjuster, StockDataProcessor
from internal.trading.cost_calculator import StockTradingCostCalculator
from internal.trading.account_manager import StockPosition, StockAccount, PortfolioManager
from internal.trading.trading_time import TradingTimeConfig, HolidayManager, TradingTimeManager, MarketCalendar
from internal.risk.stock_risk_manager import StockRiskConfig, StockRiskManager
from internal.strategies.stock_strategies import StockStrategyFactory
from vnpy.trader.constant import Direction, Offset, Exchange


class TestDividendAdjustment(unittest.TestCase):
    """测试分红除权处理模块"""
    
    def test_dividend_event(self):
        """测试分红事件"""
        from datetime import datetime
        event = DividendEvent(
            date=datetime(2024, 7, 10),
            dividend=0.5,
            bonus_share=0.1,
            rights_share=0.05,
            rights_price=10.0,
            symbol="600519"
        )
        
        self.assertEqual(event.date.year, 2024)
        self.assertEqual(event.date.month, 7)
        self.assertEqual(event.date.day, 10)
        self.assertEqual(event.dividend, 0.5)
        self.assertEqual(event.bonus_share, 0.1)
        self.assertEqual(event.rights_share, 0.05)
        self.assertEqual(event.rights_price, 10.0)
        self.assertEqual(event.symbol, "600519")
        
        # 测试调整因子计算
        adjustment_factor = event.get_adjustment_factor()
        self.assertGreater(adjustment_factor, 0)
    
    def test_dividend_adjuster(self):
        """测试分红除权调整器"""
        adjuster = DividendAdjuster()
        
        # 测试调整器初始化
        self.assertIsNotNone(adjuster)
        
        # 测试添加事件
        from datetime import datetime
        event = DividendEvent(
            date=datetime(2024, 7, 10),
            dividend=0.5,
            bonus_share=0.1,
            rights_share=0.05,
            rights_price=10.0,
            symbol="600519"
        )
        adjuster.add_event(event)
        
        # 测试事件数量
        self.assertGreater(len(adjuster.dividend_events), 0)
    
    def test_stock_data_processor(self):
        """测试股票数据处理器"""
        processor = StockDataProcessor()
        
        # 测试处理器初始化
        self.assertIsNotNone(processor)
        
        # 测试添加事件
        from datetime import datetime
        event = DividendEvent(
            date=datetime(2024, 7, 10),
            dividend=0.5,
            bonus_share=0.1,
            rights_share=0.05,
            rights_price=10.0,
            symbol="600519"
        )
        processor.add_dividend_event(event)
        
        # 测试事件数量
        self.assertGreater(len(processor.dividend_adjuster.dividend_events), 0)


class TestTradingCostCalculator(unittest.TestCase):
    """测试交易成本计算模块"""
    
    def test_cost_calculator(self):
        """测试交易成本计算器"""
        calculator = StockTradingCostCalculator()
        
        # 测试买入成本
        buy_cost = calculator.calculate_cost(
            price=10.0,
            volume=1000,
            direction=Direction.LONG,
            offset=Offset.OPEN,
            exchange=Exchange.SSE
        )
        
        self.assertIn("total_cost", buy_cost)
        self.assertIn("commission", buy_cost)
        self.assertIn("stamp_tax", buy_cost)
        self.assertIn("transfer_fee", buy_cost)
        self.assertIn("jing_shou_fee", buy_cost)
        self.assertIn("supervision_fee", buy_cost)
        
        # 测试卖出成本
        sell_cost = calculator.calculate_cost(
            price=10.0,
            volume=1000,
            direction=Direction.SHORT,
            offset=Offset.CLOSE,
            exchange=Exchange.SSE
        )
        
        self.assertIn("total_cost", sell_cost)
        self.assertIn("commission", sell_cost)
        self.assertIn("stamp_tax", sell_cost)
        
        # 测试保本价格
        break_even = calculator.get_breakeven_price(
            buy_price=10.0,
            volume=1000,
            exchange=Exchange.SSE
        )
        
        self.assertGreater(break_even, 10.0)


class TestAccountManager(unittest.TestCase):
    """测试账户管理模块"""
    
    def test_stock_position(self):
        """测试股票持仓"""
        position = StockPosition(
            symbol="600519",
            exchange=Exchange.SSE,
            volume=100,
            avg_price=1800.0,
            current_price=1850.0
        )
        
        self.assertEqual(position.symbol, "600519")
        self.assertEqual(position.volume, 100)
        self.assertEqual(position.avg_price, 1800.0)
        self.assertEqual(position.current_price, 1850.0)
        self.assertEqual(position.market_value, 185000.0)
        self.assertEqual(position.cost, 180000.0)
        self.assertEqual(position.profit, 5000.0)
        self.assertEqual(position.profit_ratio, 5000.0 / 180000.0)
    
    def test_stock_account(self):
        """测试股票账户"""
        account = StockAccount("test_account", 1000000.0)
        
        self.assertEqual(account.account_id, "test_account")
        self.assertEqual(account.balance, 1000000.0)
        self.assertEqual(account.initial_balance, 1000000.0)
        self.assertEqual(account.available, 1000000.0)
        
        # 测试账户属性
        self.assertEqual(len(account.positions), 0)
        self.assertEqual(len(account.trades), 0)
        self.assertEqual(len(account.orders), 0)
        
        # 测试总资产计算
        total_asset = account.total_asset
        self.assertEqual(total_asset, 1000000.0)
        
        # 测试总市值计算
        total_market_value = account.total_market_value
        self.assertEqual(total_market_value, 0.0)
        
        # 测试总盈亏计算
        total_profit = account.total_profit
        self.assertEqual(total_profit, 0.0)
    
    def test_portfolio_manager(self):
        """测试资产组合管理器"""
        portfolio = PortfolioManager()
        
        # 创建账户
        account = StockAccount("test_account", 1000000.0)
        portfolio.add_account(account)
        
        self.assertEqual(len(portfolio.accounts), 1)
        self.assertIn("test_account", portfolio.accounts)
        
        # 测试获取账户
        retrieved_account = portfolio.get_account("test_account")
        self.assertEqual(retrieved_account.account_id, "test_account")


class TestTradingTime(unittest.TestCase):
    """测试交易时间管理模块"""
    
    def test_trading_time_config(self):
        """测试交易时间配置"""
        # 测试A股交易时间
        a_share_hours = TradingTimeConfig.get_trading_hours("A_SHARE")
        self.assertIn("morning_open", a_share_hours)
        self.assertIn("morning_close", a_share_hours)
        self.assertIn("afternoon_open", a_share_hours)
        self.assertIn("afternoon_close", a_share_hours)
        
        # 测试港股交易时间
        hk_share_hours = TradingTimeConfig.get_trading_hours("HK_SHARE")
        self.assertIn("morning_open", hk_share_hours)
    
    def test_holiday_manager(self):
        """测试节假日管理器"""
        manager = HolidayManager()
        
        # 测试是否为节假日
        # 2024年1月1日是元旦
        holiday_date = datetime(2024, 1, 1)
        self.assertTrue(manager.is_holiday(holiday_date))
        
        # 2024年1月2日是工作日
        workday_date = datetime(2024, 1, 2)
        self.assertTrue(manager.is_workday(workday_date))
    
    def test_trading_time_manager(self):
        """测试交易时间管理器"""
        manager = TradingTimeManager()
        
        # 测试是否为交易日
        # 2024年1月1日是节假日
        holiday_date = datetime(2024, 1, 1, 10, 0, 0)
        self.assertFalse(manager.is_trading_day(holiday_date))
        
        # 测试是否为交易时间
        # 2024年1月2日10:00是交易时间
        trading_time = datetime(2024, 1, 2, 10, 0, 0)
        self.assertTrue(manager.is_trading_time(trading_time))
        
        # 测试是否为集合竞价时间
        pre_trading_time = datetime(2024, 1, 2, 9, 20, 0)
        self.assertTrue(manager.is_pre_trading_time(pre_trading_time))
    
    def test_market_calendar(self):
        """测试市场日历"""
        calendar = MarketCalendar()
        
        # 测试获取日历
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 7)
        calendar_data = calendar.get_calendar(start_date, end_date)
        
        self.assertIn("market", calendar_data)
        self.assertIn("start_date", calendar_data)
        self.assertIn("end_date", calendar_data)
        self.assertIn("total_days", calendar_data)
        self.assertIn("trading_days", calendar_data)
        self.assertIn("calendar", calendar_data)


class TestStockRiskManager(unittest.TestCase):
    """测试股票风险管理模块"""
    
    def test_stock_risk_config(self):
        """测试股票风险配置"""
        config = StockRiskConfig(
            max_position_per_stock=0.3,
            max_trades_per_stock=50,
            max_loss_per_stock=5000
        )
        
        self.assertEqual(config.max_position_per_stock, 0.3)
        self.assertEqual(config.max_trades_per_stock, 50)
        self.assertEqual(config.max_loss_per_stock, 5000)
        
        # 测试转换为字典
        config_dict = config.to_dict()
        self.assertIn("max_position_per_stock", config_dict)
        
        # 测试从字典创建
        new_config = StockRiskConfig.from_dict(config_dict)
        self.assertEqual(new_config.max_position_per_stock, 0.3)
    
    def test_stock_risk_manager(self):
        """测试股票风险管理器"""
        manager = StockRiskManager()
        
        # 测试风险管理器初始化
        self.assertIsNotNone(manager)
        
        # 测试计算组合风险
        portfolio_risk = manager.calculate_portfolio_risk("default")
        self.assertIn("risk_score", portfolio_risk)
        self.assertIn("exposure", portfolio_risk)
        self.assertIn("diversification", portfolio_risk)
        self.assertIn("risk_level", portfolio_risk)
        
        # 测试生成风险报告
        risk_report = manager.generate_risk_report("default")
        self.assertIn("account_id", risk_report)
        self.assertIn("portfolio_risk", risk_report)
        self.assertIn("position_risks", risk_report)
        self.assertIn("industry_exposure", risk_report)
        self.assertIn("trading_activity", risk_report)
        self.assertIn("compliance_status", risk_report)


class TestStockStrategies(unittest.TestCase):
    """测试股票策略模块"""
    
    def test_strategy_factory(self):
        """测试策略工厂"""
        # 测试获取可用策略
        strategies = StockStrategyFactory.get_available_strategies()
        self.assertGreater(len(strategies), 0)
        
        # 测试获取策略描述
        for strategy in strategies:
            description = StockStrategyFactory.get_strategy_description(strategy)
            self.assertGreater(len(description), 0)


if __name__ == '__main__':
    unittest.main()