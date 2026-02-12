"""
基于 vn.py 实现海龟交易策略（简化版）
仅包含核心策略逻辑，需配合 vn.py 框架运行
"""

from vnpy_ctastrategy import CtaTemplate
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Interval, Direction, Offset, OrderType
from vnpy.trader.utility import ArrayManager


class TurtleStrategy(CtaTemplate):
    """海龟交易策略"""

    # 策略参数
    entry_window = 20          # 突破入场窗口
    exit_window = 10           # 突破出场窗口
    atr_window = 20            # ATR 计算窗口
    risk_ratio = 0.01          # 每单位风险占资金比例
    max_add = 4                # 最大加仓次数
    add_gap = 0.5              # 加仓间隔（ATR 倍数）

    # 策略变量
    day_high = 0               # 入场窗口最高价
    day_low = 0                # 出场窗口最低价
    atr_value = 0              # 当前 ATR
    unit_size = 0              # 每单位交易手数
    last_entry_price = 0       # 最后一次入场价
    add_count = 0              # 已加仓次数
    intra_trade_high = 0       # 持仓期间最高价
    intra_trade_low = 0        # 持仓期间最低价

    parameters = ["entry_window", "exit_window", "atr_window",
                  "risk_ratio", "max_add", "add_gap"]
    variables = ["day_high", "day_low", "atr_value", "unit_size",
                 "last_entry_price", "add_count",
                 "intra_trade_high", "intra_trade_low"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """构造函数"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.am = ArrayManager(size=100)  # 缓存 K 线

    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(30, Interval.DAILY)  # 加载 30 天日线数据

    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")

    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")

    def on_bar(self, bar: BarData):
        """K 线推送"""
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # 计算指标
        self.day_high = am.high_array[-self.entry_window:].max()
        self.day_low = am.low_array[-self.exit_window:].min()
        self.atr_value = am.atr(self.atr_window)

        # 计算单位手数
        if self.atr_value > 0:
            risk_capital = self.risk_ratio * self.cta_engine.capital
            self.unit_size = int(risk_capital / (self.atr_value * self.cta_engine.size))

        # 无持仓
        if not self.pos:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            # 突破入场
            if bar.close_price > self.day_high:
                self.buy(self.day_high, self.unit_size, stop=True)

        # 持多头
        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

            # 加仓
            add_price = self.last_entry_price + self.add_gap * self.atr_value
            if bar.close_price >= add_price and self.add_count < self.max_add:
                self.buy(add_price, self.unit_size, stop=True)

            # 止损/出场
            exit_price = self.intra_trade_high - 2 * self.atr_value
            if bar.close_price <= exit_price:
                self.sell(bar.close_price, abs(self.pos))

            # 反向突破出场
            if bar.close_price < self.day_low:
                self.sell(bar.close_price, abs(self.pos))

        self.put_event()

    def on_order(self, order: OrderData):
        """委托推送"""
        pass

    def on_trade(self, trade: TradeData):
        """成交推送"""
        if trade.direction == Direction.LONG:
            self.last_entry_price = trade.price
            self.add_count += 1
        else:
            self.last_entry_price = 0
            self.add_count = 0

        self.put_event()

    def on_stop_order(self, stop_order):
        """停止单推送"""
        pass
