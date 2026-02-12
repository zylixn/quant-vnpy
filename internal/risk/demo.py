"""
风险评估功能演示
"""

from internal.risk.risk_assessor import (
    AccountRiskAssessor,
    StrategyRiskAssessor,
    MarketRiskAssessor,
    RiskManager
)
from internal.risk.vnpy_integration import RiskMonitor, RiskControlStrategy
import numpy as np
from datetime import datetime


def demo_basic_risk_assessment():
    """基础风险评估演示"""
    print("=== 基础风险评估演示 ===")
    
    # 创建账户风险评估器
    account_assessor = AccountRiskAssessor(initial_balance=100000.0)
    
    # 模拟交易
    trades = [
        {'pnl': 1000},  # 盈利
        {'pnl': -500},  # 亏损
        {'pnl': 1500},  # 盈利
        {'pnl': 800},   # 盈利
        {'pnl': -300},  # 亏损
    ]
    
    # 添加交易
    for trade in trades:
        account_assessor.add_trade(trade)
    
    # 更新余额
    account_assessor.update_balance(102500.0)
    
    # 评估账户风险
    metrics = account_assessor.assess_account_risk()
    print(f"账户风险评估: {metrics}")
    print()


def demo_strategy_risk_assessment():
    """策略风险评估演示"""
    print("=== 策略风险评估演示 ===")
    
    # 创建策略风险评估器
    strategy_assessor = StrategyRiskAssessor("BullStrategy")
    
    # 设置策略参数
    params = {
        'fast_window': 10,
        'slow_window': 30,
        'fixed_size': 1
    }
    strategy_assessor.set_strategy_params(params)
    
    # 设置指标
    indicators = {
        'fast_ma': 50000,
        'slow_ma': 49000,
        'rsi': 65
    }
    strategy_assessor.set_indicators(indicators)
    
    # 模拟交易
    trades = [
        {'pnl': 2000},  # 盈利
        {'pnl': -800},  # 亏损
        {'pnl': 3000},  # 盈利
        {'pnl': -1200}, # 亏损
        {'pnl': 1500},  # 盈利
    ]
    
    # 添加交易
    for trade in trades:
        strategy_assessor.add_trade(trade)
    
    # 评估策略风险
    metrics = strategy_assessor.assess_strategy_risk()
    print(f"策略风险评估: {metrics}")
    print()


def demo_market_risk_assessment():
    """市场风险评估演示"""
    print("=== 市场风险评估演示 ===")
    
    # 生成模拟价格数据
    prices = np.cumsum(np.random.normal(0.1, 1, 100)) + 50000
    
    # 评估市场波动率
    volatility_metrics = MarketRiskAssessor.assess_market_volatility(prices.tolist())
    print(f"市场波动率评估: {volatility_metrics}")
    
    # 评估趋势强度
    trend_metrics = MarketRiskAssessor.assess_trend_strength(prices.tolist())
    print(f"市场趋势评估: {trend_metrics}")
    print()


def demo_risk_manager():
    """风险管理演示"""
    print("=== 风险管理演示 ===")
    
    # 创建账户风险评估器
    account_assessor = AccountRiskAssessor(initial_balance=100000.0)
    
    # 创建风险管理器
    risk_manager = RiskManager(account_assessor)
    
    # 设置风险限制
    risk_limits = {
        'max_position_size': 0.4,  # 最大持仓比例40%
        'max_drawdown': 0.15,       # 最大回撤15%
        'single_trade_risk': 0.02   # 单笔交易风险2%
    }
    risk_manager.set_risk_limits(risk_limits)
    
    # 模拟交易
    trades = [
        {'pnl': 1500},  # 盈利
        {'pnl': -800},  # 亏损
        {'pnl': 2500},  # 盈利
        {'pnl': -1200}, # 亏损
        {'pnl': 3000},  # 盈利
    ]
    
    # 添加交易
    for trade in trades:
        account_assessor.add_trade(trade)
    
    # 更新余额
    account_assessor.update_balance(105000.0)
    
    # 计算持仓大小
    position_size = risk_manager.calculate_position_size(105000.0, 500)
    print(f"推荐持仓大小: {position_size}")
    
    # 评估风险敞口
    warnings = risk_manager.assess_risk_exposure(40000, 105000)
    print(f"风险敞口评估: {warnings}")
    
    # 生成风险报告
    report = risk_manager.generate_risk_report()
    print(f"风险报告: {report}")
    print()


def demo_risk_monitor():
    """风险监控器演示"""
    print("=== 风险监控器演示 ===")
    
    # 创建风险监控器
    risk_monitor = RiskMonitor()
    
    # 注册策略
    risk_monitor.register_strategy("BullStrategy")
    risk_monitor.register_strategy("BearStrategy")
    
    # 更新账户余额
    risk_monitor.update_balance(100000.0)
    
    # 模拟交易数据
    class MockTrade:
        def __init__(self, symbol, direction, price, volume, pnl, commission=None, trade_time=None):
            self.symbol = symbol
            self.direction = direction
            self.price = price
            self.volume = volume
            self.pnl = pnl
            self.commission = commission or 0
            self.trade_time = trade_time or datetime.now()
    
    # 模拟成交
    trades = [
        MockTrade("BTC/USDT", "LONG", 50000, 1, 1000),
        MockTrade("BTC/USDT", "LONG", 51000, 1, 1000),
        MockTrade("ETH/USDT", "SHORT", 3000, 2, -200),
        MockTrade("BTC/USDT", "LONG", 52000, 1, 1000),
    ]
    
    # 更新交易
    for trade in trades:
        risk_monitor.update_trade(trade, "BullStrategy")
    
    # 更新余额
    risk_monitor.update_balance(102800.0)
    
    # 生成综合报告
    report = risk_monitor.generate_combined_report()
    print(f"综合风险报告: {report}")
    print()


if __name__ == "__main__":
    # 运行演示
    demo_basic_risk_assessment()
    demo_strategy_risk_assessment()
    demo_market_risk_assessment()
    demo_risk_manager()
    demo_risk_monitor()
    
    print("=== 演示完成 ===")
