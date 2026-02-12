"""
策略适配器，用于连接现有策略和模拟盘交易系统
"""

from vnpy_ctastrategy import CtaTemplate
from vnpy.trader.object import TickData, BarData, OrderData, TradeData

try:
    from vnpy.trader.object import StopOrder
except ImportError:
    # 如果StopOrder不存在，定义一个空类
    class StopOrder:
        pass
from vnpy.trader.constant import Direction, Offset, Exchange, OrderType, Status
from internal.trading.simulator.simulator import TradingSimulator
from internal.trading.simulator.vnpy_simulator import VnpyTradingSimulator


class SimulatedStrategyAdapter:
    """策略适配器"""
    
    def __init__(self, strategy: CtaTemplate, simulator: TradingSimulator):
        self.strategy = strategy
        self.simulator = simulator
        self.use_vnpy = isinstance(simulator, VnpyTradingSimulator)
    
    def on_tick(self, tick: TickData):
        """处理行情tick"""
        # 设置当前价格
        self.simulator.set_symbol_price(tick.symbol, tick.last_price)
        # 调用策略的on_tick方法
        self.strategy.on_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线"""
        # 设置当前价格
        self.simulator.set_symbol_price(bar.symbol, bar.close_price)
        # 调用策略的on_bar方法
        self.strategy.on_bar(bar)
    
    def buy(self, symbol: str, price: float, volume: int, stop: bool = False):
        """买入"""
        if self.use_vnpy:
            order_id, error = self.simulator.submit_order(
                symbol=symbol,
                exchange=Exchange.SHFE,  # 默认交易所
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                order_type=OrderType.STOP if stop else OrderType.LIMIT
            )
        else:
            order_id, error = self.simulator.buy(symbol, price, volume)
        
        if error:
            print(f"买入失败: {error}")
        return order_id
    
    def sell(self, symbol: str, price: float, volume: int, stop: bool = False):
        """卖出"""
        if self.use_vnpy:
            order_id, error = self.simulator.submit_order(
                symbol=symbol,
                exchange=Exchange.SHFE,  # 默认交易所
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=price,
                volume=volume,
                order_type=OrderType.STOP if stop else OrderType.LIMIT
            )
        else:
            order_id, error = self.simulator.sell(symbol, price, volume)
        
        if error:
            print(f"卖出失败: {error}")
        return order_id
    
    def short(self, symbol: str, price: float, volume: int, stop: bool = False):
        """做空"""
        if self.use_vnpy:
            order_id, error = self.simulator.submit_order(
                symbol=symbol,
                exchange=Exchange.SHFE,  # 默认交易所
                direction=Direction.SHORT,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                order_type=OrderType.STOP if stop else OrderType.LIMIT
            )
            if error:
                print(f"做空失败: {error}")
            return order_id
        else:
            # 旧版本模拟盘不支持做空
            print("模拟盘暂不支持做空")
            return None
    
    def cover(self, symbol: str, price: float, volume: int, stop: bool = False):
        """平空"""
        if self.use_vnpy:
            order_id, error = self.simulator.submit_order(
                symbol=symbol,
                exchange=Exchange.SHFE,  # 默认交易所
                direction=Direction.LONG,
                offset=Offset.CLOSE,
                price=price,
                volume=volume,
                order_type=OrderType.STOP if stop else OrderType.LIMIT
            )
            if error:
                print(f"平空失败: {error}")
            return order_id
        else:
            # 旧版本模拟盘不支持平空
            print("模拟盘暂不支持平空")
            return None
    
    def cancel_order(self, order_id: str):
        """撤单"""
        return self.simulator.cancel_order(order_id)
    
    def get_account(self):
        """获取账户信息"""
        return self.simulator.get_account_info()
    
    def get_positions(self):
        """获取持仓信息"""
        return self.simulator.get_positions()


class SimulatedCtaEngine:
    """模拟CTA引擎"""
    
    def __init__(self, simulator: TradingSimulator):
        self.simulator = simulator
        self.strategies = {}
        self.use_vnpy = isinstance(simulator, VnpyTradingSimulator)
    
    def add_strategy(self, strategy: CtaTemplate):
        """添加策略"""
        self.strategies[strategy.strategy_name] = strategy
        print(f"策略 {strategy.strategy_name} 已添加")
    
    def start_strategy(self, strategy_name: str):
        """启动策略"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.on_start()
            print(f"策略 {strategy_name} 已启动")
    
    def stop_strategy(self, strategy_name: str):
        """停止策略"""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.on_stop()
            print(f"策略 {strategy_name} 已停止")
    
    def send_tick(self, tick: TickData):
        """发送tick"""
        for strategy in self.strategies.values():
            if strategy.vt_symbol == tick.symbol:
                adapter = SimulatedStrategyAdapter(strategy, self.simulator)
                adapter.on_tick(tick)
    
    def send_bar(self, bar: BarData):
        """发送bar"""
        for strategy in self.strategies.values():
            if strategy.vt_symbol == bar.symbol:
                adapter = SimulatedStrategyAdapter(strategy, self.simulator)
                adapter.on_bar(bar)
    
    @property
    def capital(self):
        """资金"""
        return self.simulator.account.balance
    
    @property
    def size(self):
        """合约乘数"""
        return 1  # 简化处理
    
    def get_account(self):
        """获取账户信息"""
        return self.simulator.get_account_info()
    
    def get_positions(self):
        """获取持仓信息"""
        return self.simulator.get_positions()
    
    def get_orders(self):
        """获取订单信息"""
        return self.simulator.get_orders()
    
    def get_trades(self):
        """获取成交信息"""
        return self.simulator.get_trades()
    
    def reset(self, initial_balance: float = None):
        """重置模拟器"""
        self.simulator.reset(initial_balance)
        print("模拟器已重置")
    
    def write_log(self, msg: str):
        """写入日志"""
        print(f"[LOG] {msg}")
