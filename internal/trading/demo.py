"""
模拟盘交易演示
"""

from internal.trading.simulator.simulator import TradingSimulator
from internal.trading.simulator.strategy_adapter import SimulatedCtaEngine
from internal.strategies.bull_trend_strategy import BullStrategy


def demo_basic_trading():
    """基础交易演示"""
    print("=== 基础交易演示 ===")
    
    # 创建模拟器
    simulator = TradingSimulator(initial_balance=100000.0)
    
    # 设置价格
    simulator.set_symbol_price("BTC/USDT", 50000.0)
    
    # 买入
    order_id, error = simulator.buy("BTC/USDT", 50000.0, 1)
    if error:
        print(f"买入失败: {error}")
    else:
        print(f"买入成功，订单ID: {order_id}")
    
    # 获取账户信息
    account = simulator.get_account_info()
    print(f"账户信息: {account}")
    
    # 获取持仓
    positions = simulator.get_positions()
    print(f"持仓信息: {positions}")
    
    # 卖出
    simulator.set_symbol_price("BTC/USDT", 55000.0)
    order_id, error = simulator.sell("BTC/USDT", 55000.0, 1)
    if error:
        print(f"卖出失败: {error}")
    else:
        print(f"卖出成功，订单ID: {order_id}")
    
    # 获取最终账户信息
    account = simulator.get_account_info()
    print(f"最终账户信息: {account}")
    print()


def demo_strategy_trading():
    """策略交易演示"""
    print("=== 策略交易演示 ===")
    
    # 创建模拟器
    simulator = TradingSimulator(initial_balance=100000.0)
    
    # 创建模拟CTA引擎
    cta_engine = SimulatedCtaEngine(simulator)
    
    # 创建策略
    strategy = BullStrategy(
        cta_engine=cta_engine,
        strategy_name="BullStrategy",
        vt_symbol="BTC/USDT",
        setting={}
    )
    
    # 添加策略到引擎
    cta_engine.add_strategy(strategy)
    
    # 启动策略
    cta_engine.start_strategy("BullStrategy")
    
    # 模拟K线数据
    from vnpy.trader.object import BarData
    from vnpy.trader.constant import Interval
    
    # 创建一些K线数据模拟上涨趋势
    bars = []
    for i in range(30):
        bar = BarData(
            symbol="BTC/USDT",
            exchange="BINANCE",
            datetime=BarData.generate_datetime(i),
            interval=Interval.MINUTE,
            volume=1000,
            open_price=50000 + i * 100,
            high_price=50000 + i * 100 + 50,
            low_price=50000 + i * 100 - 50,
            close_price=50000 + i * 100,
            gateway_name="BINANCE"
        )
        bars.append(bar)
    
    # 推送K线数据
    for i, bar in enumerate(bars):
        print(f"处理第{i+1}根K线，收盘价: {bar.close_price}")
        cta_engine.send_bar(bar)
    
    # 获取最终状态
    account = simulator.get_account_info()
    positions = simulator.get_positions()
    
    print(f"\n最终账户信息: {account}")
    print(f"最终持仓信息: {positions}")
    print()


if __name__ == "__main__":
    # 运行基础交易演示
    demo_basic_trading()
    
    # 运行策略交易演示
    demo_strategy_trading()
    
    print("=== 演示完成 ===")
