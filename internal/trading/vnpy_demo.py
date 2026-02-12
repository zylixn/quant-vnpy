"""
基于vnpy的模拟盘交易演示
"""

from internal.trading.simulator import VnpyTradingSimulator, SimulatedCtaEngine
from internal.strategies.bull_trend_strategy import BullStrategy
from vnpy.trader.constant import Direction, Offset, Exchange, OrderType
from vnpy.trader.object import TickData, BarData
from datetime import datetime
import time


def demo_vnpy_simulator():
    """vnpy模拟器演示"""
    print("=== vnpy模拟器演示 ===")
    
    # 创建vnpy模拟器
    simulator = VnpyTradingSimulator(initial_balance=100000.0)
    
    # 设置合约价格
    simulator.set_symbol_price("BTC/USDT", 50000.0)
    
    # 测试1: 买入开仓
    print("\n测试1: 买入开仓")
    order_id, error = simulator.submit_order(
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        direction=Direction.LONG,
        offset=Offset.OPEN,
        price=50000.0,
        volume=1.0
    )
    
    if error:
        print(f"买入失败: {error}")
    else:
        print(f"买入成功，订单ID: {order_id}")
    
    # 获取账户信息
    account_info = simulator.get_account_info()
    print(f"账户信息: {account_info}")
    
    # 获取持仓信息
    positions = simulator.get_positions()
    print(f"持仓信息: {positions}")
    
    # 测试2: 卖出平仓
    print("\n测试2: 卖出平仓")
    # 更新价格
    simulator.set_symbol_price("BTC/USDT", 51000.0)
    
    order_id, error = simulator.submit_order(
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        direction=Direction.SHORT,
        offset=Offset.CLOSE,
        price=51000.0,
        volume=1.0
    )
    
    if error:
        print(f"卖出失败: {error}")
    else:
        print(f"卖出成功，订单ID: {order_id}")
    
    # 获取账户信息
    account_info = simulator.get_account_info()
    print(f"账户信息: {account_info}")
    
    # 获取持仓信息
    positions = simulator.get_positions()
    print(f"持仓信息: {positions}")
    
    # 测试3: 做空开仓
    print("\n测试3: 做空开仓")
    order_id, error = simulator.submit_order(
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        direction=Direction.SHORT,
        offset=Offset.OPEN,
        price=51000.0,
        volume=1.0
    )
    
    if error:
        print(f"做空失败: {error}")
    else:
        print(f"做空成功，订单ID: {order_id}")
    
    # 获取持仓信息
    positions = simulator.get_positions()
    print(f"持仓信息: {positions}")
    
    # 测试4: 买入平仓（平空）
    print("\n测试4: 买入平仓（平空）")
    # 更新价格
    simulator.set_symbol_price("BTC/USDT", 50500.0)
    
    order_id, error = simulator.submit_order(
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        direction=Direction.LONG,
        offset=Offset.CLOSE,
        price=50500.0,
        volume=1.0
    )
    
    if error:
        print(f"平空失败: {error}")
    else:
        print(f"平空成功，订单ID: {order_id}")
    
    # 获取账户信息
    account_info = simulator.get_account_info()
    print(f"账户信息: {account_info}")
    
    # 获取持仓信息
    positions = simulator.get_positions()
    print(f"持仓信息: {positions}")
    
    # 获取订单信息
    orders = simulator.get_orders()
    print(f"\n订单数量: {len(orders)}")
    
    # 获取成交信息
    trades = simulator.get_trades()
    print(f"成交数量: {len(trades)}")
    
    print("\n=== vnpy模拟器演示完成 ===")


def demo_strategy_integration():
    """策略集成演示"""
    print("\n=== 策略集成演示 ===")
    
    # 创建vnpy模拟器
    simulator = VnpyTradingSimulator(initial_balance=100000.0)
    
    # 创建模拟CTA引擎
    cta_engine = SimulatedCtaEngine(simulator)
    
    # 创建策略实例
    strategy = BullStrategy(cta_engine, "BullStrategy", "BTC/USDT", {})
    
    # 添加策略
    cta_engine.add_strategy(strategy)
    
    # 启动策略
    cta_engine.start_strategy("BullStrategy")
    
    # 模拟行情数据
    print("\n模拟行情数据...")
    
    # 创建tick数据
    tick = TickData(
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        datetime=datetime.now(),
        last_price=50000.0,
        volume=1000,
        bid_price_1=49999.0,
        bid_volume_1=10,
        ask_price_1=50001.0,
        ask_volume_1=10,
        gateway_name="SIMULATOR"
    )
    
    # 发送tick数据
    cta_engine.send_tick(tick)
    
    # 创建bar数据
    bar = BarData(
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        datetime=datetime.now(),
        interval="1m",
        open_price=49900.0,
        high_price=50100.0,
        low_price=49800.0,
        close_price=50000.0,
        volume=10000,
        gateway_name="SIMULATOR"
    )
    
    # 发送bar数据
    cta_engine.send_bar(bar)
    
    # 模拟价格上涨
    print("\n模拟价格上涨...")
    for i in range(5):
        time.sleep(0.5)
        price = 50000.0 + i * 100
        tick.last_price = price
        tick.datetime = datetime.now()
        cta_engine.send_tick(tick)
        
        bar.close_price = price
        bar.high_price = max(bar.high_price, price)
        bar.datetime = datetime.now()
        cta_engine.send_bar(bar)
    
    # 模拟价格下跌
    print("\n模拟价格下跌...")
    for i in range(5):
        time.sleep(0.5)
        price = 50400.0 - i * 100
        tick.last_price = price
        tick.datetime = datetime.now()
        cta_engine.send_tick(tick)
        
        bar.close_price = price
        bar.low_price = min(bar.low_price, price)
        bar.datetime = datetime.now()
        cta_engine.send_bar(bar)
    
    # 停止策略
    cta_engine.stop_strategy("BullStrategy")
    
    # 获取交易结果
    print("\n交易结果:")
    account_info = cta_engine.get_account()
    print(f"账户信息: {account_info}")
    
    positions = cta_engine.get_positions()
    print(f"持仓信息: {positions}")
    
    trades = cta_engine.get_trades()
    print(f"成交数量: {len(trades)}")
    
    print("\n=== 策略集成演示完成 ===")


def demo_risk_control_integration():
    """风险控制集成演示"""
    print("\n=== 风险控制集成演示 ===")
    
    try:
        # 导入风险控制相关模块
        from internal.risk.vnpy_integration import RiskControlStrategy
        
        # 创建vnpy模拟器
        simulator = VnpyTradingSimulator(initial_balance=100000.0)
        
        # 创建模拟CTA引擎
        cta_engine = SimulatedCtaEngine(simulator)
        
        # 创建带风险控制的策略
        class RiskControlledBullStrategy(RiskControlStrategy):
            """带风险控制的牛市策略"""
            def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
                super().__init__(cta_engine, strategy_name, vt_symbol, setting)
            
            def on_bar(self, bar: BarData):
                # 先检查风险
                if not self.check_risk_before_trade(1.0):
                    self.write_log("风险检查失败，跳过交易")
                    return
                
                # 原有的策略逻辑
                super().on_bar(bar)
        
        # 创建策略实例
        strategy = RiskControlledBullStrategy(cta_engine, "RiskControlledBull", "BTC/USDT", {})
        
        # 添加策略
        cta_engine.add_strategy(strategy)
        
        # 启动策略
        cta_engine.start_strategy("RiskControlledBull")
        
        # 模拟行情数据
        print("\n模拟行情数据...")
        
        # 创建bar数据
        bar = BarData(
            symbol="BTC/USDT",
            exchange=Exchange.BINANCE,
            datetime=datetime.now(),
            interval="1m",
            open_price=50000.0,
            high_price=50100.0,
            low_price=49900.0,
            close_price=50000.0,
            volume=10000,
            gateway_name="SIMULATOR"
        )
        
        # 发送bar数据
        cta_engine.send_bar(bar)
        
        # 模拟价格上涨
        print("\n模拟价格上涨...")
        for i in range(3):
            time.sleep(0.5)
            price = 50000.0 + i * 200
            bar.close_price = price
            bar.high_price = max(bar.high_price, price)
            bar.datetime = datetime.now()
            cta_engine.send_bar(bar)
        
        # 停止策略
        cta_engine.stop_strategy("RiskControlledBull")
        
        print("\n=== 风险控制集成演示完成 ===")
        
    except ImportError as e:
        print(f"\n风险控制模块导入失败: {e}")
        print("请先安装vnpy依赖")


if __name__ == "__main__":
    # 运行演示
    demo_vnpy_simulator()
    
    # 运行策略集成演示
    demo_strategy_integration()
    
    # 运行风险控制集成演示
    demo_risk_control_integration()
    
    print("\n=== 所有演示完成 ===")
