from vnpy.trader.constant import Direction, Offset, Exchange, Interval, Status
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
# 牛市、熊市交易策略示例（基于 vn.py CtaTemplate）

class BullStrategy(CtaTemplate):
    """牛市策略：趋势跟随，逢低做多"""
    author = "AI"

    # 策略参数
    fast_window = 10
    slow_window = 30
    fixed_size = 1

    # 策略变量
    fast_ma0 = 0.0
    fast_ma1 = 0.0
    slow_ma0 = 0.0
    slow_ma1 = 0.0

    parameters = ["fast_window", "slow_window", "fixed_size"]
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        当策略被初始化时调用。
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        当策略被启动时调用。
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        当策略被停止时调用。
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        通过行情推送生成 K 线。
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        收到新 K 线时回调。
        """
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        # 金叉做多
        if self.fast_ma0 > self.slow_ma0 and self.fast_ma1 <= self.slow_ma1:
            if self.pos == 0:
                self.buy(bar.close_price, self.fixed_size)
            elif self.pos < 0:
                self.cover(bar.close_price, abs(self.pos))
                self.buy(bar.close_price, self.fixed_size)

        # 跌破短期均线减仓/止盈
        elif bar.close_price < self.fast_ma0 and self.pos > 0:
            self.sell(bar.close_price, abs(self.pos))

        self.put_event()

    def on_order(self, order: OrderData):
        """
        订单更新回调。
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        成交更新回调。
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        本地停止单更新回调。
        """
        pass


class BearStrategy(CtaTemplate):
    """熊市策略：趋势反转，反弹做空"""
    author = "AI"

    # 策略参数
    fast_window = 10
    slow_window = 30
    rsi_window = 14
    rsi_overbought = 70
    fixed_size = 1

    # 策略变量
    fast_ma0 = 0.0
    fast_ma1 = 0.0
    slow_ma0 = 0.0
    slow_ma1 = 0.0
    rsi_value = 0.0

    parameters = ["fast_window", "slow_window", "rsi_window", "rsi_overbought", "fixed_size"]
    variables = ["fast_ma0", "fast_ma1", "slow_ma0", "slow_ma1", "rsi_value"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager()

    def on_init(self):
        """
        当策略被初始化时调用。
        """
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self):
        """
        当策略被启动时调用。
        """
        self.write_log("策略启动")

    def on_stop(self):
        """
        当策略被停止时调用。
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData):
        """
        通过行情推送生成 K 线。
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData):
        """
        收到新 K 线时回调。
        """
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        self.rsi_value = am.rsi(self.rsi_window)

        # 死叉做空
        if self.fast_ma0 < self.slow_ma0 and self.fast_ma1 >= self.slow_ma1:
            if self.pos == 0:
                self.short(bar.close_price, self.fixed_size)
            elif self.pos > 0:
                self.sell(bar.close_price, abs(self.pos))
                self.short(bar.close_price, self.fixed_size)

        # 反弹至短期均线附近且 RSI 超买时加仓空单
        elif bar.close_price > self.fast_ma0 and self.rsi_value > self.rsi_overbought and self.pos < 0:
            self.short(bar.close_price, self.fixed_size)

        # 跌破前低（这里用 slow_ma * 0.95 近似）后择机止盈
        elif bar.close_price < self.slow_ma0 * 0.95 and self.pos < 0:
            self.cover(bar.close_price, abs(self.pos))

        self.put_event()

    def on_order(self, order: OrderData):
        """
        订单更新回调。
        """
        pass

    def on_trade(self, trade: TradeData):
        """
        成交更新回调。
        """
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder):
        """
        本地停止单更新回调。
        """
        pass
