"""
基于vn.py的均值回归策略示例
策略逻辑：
1. 计算过去N根K线的收盘价的均值与标准差
2. 当价格低于均值 - K倍标准差时开多仓
3. 当价格高于均值 + K倍标准差时开空仓
4. 当价格回归至均值时平仓
"""

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.constant import Interval


class MeanReversionStrategy(CtaTemplate):
    """均值回归策略"""

    author = "vn.py社区"

    # 策略参数
    window_size: int = 20          # 计算均值和标准差的窗口
    std_dev_multiplier: float = 2.0  # 标准差倍数
    fixed_size: int = 1              # 每次交易手数

    # 策略变量
    mean: float = 0.0
    std: float = 0.0
    upper_band: float = 0.0
    lower_band: float = 0.0

    parameters = ["window_size", "std_dev_multiplier", "fixed_size"]
    variables = ["mean", "std", "upper_band", "lower_band"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """构造函数"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar, 1, self.on_bar, Interval.MINUTE)
        self.am = ArrayManager(size=100)

    def on_init(self):
        """策略初始化回调"""
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """策略启动回调"""
        self.write_log("策略启动")

    def on_stop(self):
        """策略停止回调"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """收到Tick推送"""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """收到Bar推送"""
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # 计算均值、标准差和通道
        self.mean = self.am.close[-self.window_size:].mean()
        self.std = self.am.close[-self.window_size:].std()
        self.upper_band = self.mean + self.std_dev_multiplier * self.std
        self.lower_band = self.mean - self.std_dev_multiplier * self.std

        # 当前价格
        price = bar.close_price

        # 信号生成
        if not self.pos:
            # 无持仓，考虑开仓
            if price <= self.lower_band:
                # 价格低于下轨，做多
                self.buy(price, self.fixed_size)
            elif price >= self.upper_band:
                # 价格高于上轨，做空
                self.short(price, self.fixed_size)
        elif self.pos > 0:
            # 持有多头，考虑平仓
            if price >= self.mean:
                # 价格回归均值，平多
                self.sell(price, abs(self.pos))
        elif self.pos < 0:
            # 持有空头，考虑平仓
            if price <= self.mean:
                # 价格回归均值，平空
                self.cover(price, abs(self.pos))

        # 更新UI
        self.put_event()

    def on_order(self, order: OrderData):
        """收到委托回报"""
        pass

    def on_trade(self, trade: TradeData):
        """收到成交回报"""
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """收到停止单回报"""
        pass
