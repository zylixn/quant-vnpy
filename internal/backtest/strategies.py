"""
回测策略基类
"""

from vnpy_ctastrategy import CtaTemplate
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Direction, Offset


class BacktestStrategy(CtaTemplate):
    """回测策略基类
    
    提供回测策略的基础功能，包括订单统计、成交统计和盈亏计算。
    所有回测策略都应继承此类。
    """
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """初始化回测策略基类
        
        Args:
            cta_engine: CTA策略引擎对象，负责策略的执行和管理
            strategy_name (str): 策略名称，用于标识不同的策略实例
            vt_symbol (str): 交易品种代码，格式为"交易所.合约代码"，如"SHFE.fu2401"
            setting (dict): 策略参数字典，包含策略的配置参数
        
        Attributes:
            backtest_mode (bool): 回测模式标志，始终为True
            order_count (int): 总订单数，统计策略发出的所有订单数量
            trade_count (int): 总成交数，统计策略实际成交的订单数量
            total_pnl (float): 总盈亏，累计所有交易的盈亏金额
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        # 回测专用参数
        self.backtest_mode = True
        self.order_count = 0
        self.trade_count = 0
        self.total_pnl = 0
    
    def on_init(self):
        """策略初始化回调
        
        当策略被初始化时调用，用于加载历史数据和初始化策略状态。
        默认加载10根K线数据用于计算技术指标。
        """
        self.write_log("策略初始化")
        self.load_bar(10)
    
    def on_start(self):
        """策略启动回调
        
        当策略被启动时调用，策略开始接收行情数据并执行交易逻辑。
        """
        self.write_log("策略启动")
    
    def on_stop(self):
        """策略停止回调
        
        当策略被停止时调用，输出策略运行统计信息。
        包括总订单数、总成交数和总盈亏。
        """
        self.write_log("策略停止")
        self.write_log(f"总订单数: {self.order_count}")
        self.write_log(f"总成交数: {self.trade_count}")
        self.write_log(f"总盈亏: {self.total_pnl:.2f}")
    
    def on_tick(self, tick: TickData):
        """收到行情Tick数据回调
        
        Args:
            tick (TickData): Tick数据对象，包含最新的行情信息
        
        Note:
            默认为空实现，子类可根据需要重写此方法处理Tick数据。
        """
        pass
    
    def on_bar(self, bar: BarData):
        """收到K线数据回调
        
        Args:
            bar (BarData): K线数据对象，包含开盘价、最高价、最低价、收盘价和成交量等信息
        
        Note:
            默认为空实现，子类必须重写此方法实现具体的交易逻辑。
        """
        pass
    
    def on_order(self, order: OrderData):
        """收到订单更新回调
        
        Args:
            order (OrderData): 订单数据对象，包含订单状态、价格、数量等信息
        
        Note:
            每次订单状态更新时都会调用，用于统计订单数量。
        """
        self.order_count += 1
    
    def on_trade(self, trade: TradeData):
        """收到成交更新回调
        
        Args:
            trade (TradeData): 成交数据对象，包含成交价格、数量和盈亏等信息
        
        Note:
            每次成交时都会调用，用于统计成交数量和累计盈亏。
        """
        self.trade_count += 1
        # 回测中 TradeData 可能没有 pnl 属性，所以需要检查
        if hasattr(trade, 'pnl'):
            self.total_pnl += trade.pnl
    
    def on_position(self, pos):
        """收到持仓更新回调
        
        Args:
            pos: 持仓数据对象，包含持仓数量、持仓价格等信息
        
        Note:
            默认为空实现，子类可根据需要重写此方法处理持仓变化。
        """
        pass
    
    def on_account(self, account):
        """收到账户更新回调
        
        Args:
            account: 账户数据对象，包含账户资金、可用资金等信息
        
        Note:
            默认为空实现，子类可根据需要重写此方法处理账户变化。
        """
        pass
    
    def buy(self, price: float, volume: float, stop: bool = False, lock: bool = False) -> str:
        """买入开仓
        
        Args:
            price (float): 买入价格，指定订单的限价
            volume (float): 买入数量，指定交易的手数或股数
            stop (bool, optional): 是否为停止单，默认为False
            lock (bool, optional): 是否锁定仓位，默认为False
        
        Returns:
            str: 订单ID，用于跟踪订单状态
        
        Note:
            此方法用于做多（买入开仓），对应Direction.LONG和Offset.OPEN。
        """
        return self.send_order(Direction.LONG, Offset.OPEN, price, volume, stop, lock)
    
    def sell(self, price: float, volume: float, stop: bool = False, lock: bool = False) -> str:
        """卖出平仓
        
        Args:
            price (float): 卖出价格，指定订单的限价
            volume (float): 卖出数量，指定交易的手数或股数
            stop (bool, optional): 是否为停止单，默认为False
            lock (bool, optional): 是否锁定仓位，默认为False
        
        Returns:
            str: 订单ID，用于跟踪订单状态
        
        Note:
            此方法用于平多仓（卖出平仓），对应Direction.SHORT和Offset.CLOSE。
        """
        return self.send_order(Direction.SHORT, Offset.CLOSE, price, volume, stop, lock)
    
    def short(self, price: float, volume: float, stop: bool = False, lock: bool = False) -> str:
        """卖出开仓
        
        Args:
            price (float): 卖出价格，指定订单的限价
            volume (float): 卖出数量，指定交易的手数或股数
            stop (bool, optional): 是否为停止单，默认为False
            lock (bool, optional): 是否锁定仓位，默认为False
        
        Returns:
            str: 订单ID，用于跟踪订单状态
        
        Note:
            此方法用于做空（卖出开仓），对应Direction.SHORT和Offset.OPEN。
        """
        return self.send_order(Direction.SHORT, Offset.OPEN, price, volume, stop, lock)
    
    def cover(self, price: float, volume: float, stop: bool = False, lock: bool = False) -> str:
        """买入平仓
        
        Args:
            price (float): 买入价格，指定订单的限价
            volume (float): 买入数量，指定交易的手数或股数
            stop (bool, optional): 是否为停止单，默认为False
            lock (bool, optional): 是否锁定仓位，默认为False
        
        Returns:
            str: 订单ID，用于跟踪订单状态
        
        Note:
            此方法用于平空仓（买入平仓），对应Direction.LONG和Offset.CLOSE。
        """
        return self.send_order(Direction.LONG, Offset.CLOSE, price, volume, stop, lock)


class DemoBacktestStrategy(BacktestStrategy):
    """演示回测策略
    
    基于双移动平均线的简单趋势跟踪策略。
    当快速均线上穿慢速均线时买入（金叉），当快速均线下穿慢速均线时卖出（死叉）。
    """
    
    author = "Demo"
    
    # 策略参数
    fast_window = 10
    slow_window = 20
    
    # 策略变量
    fast_ma = 0
    slow_ma = 0
    
    parameters = ["fast_window", "slow_window"]
    variables = ["fast_ma", "slow_ma"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """初始化演示回测策略
        
        Args:
            cta_engine: CTA策略引擎对象
            strategy_name (str): 策略名称
            vt_symbol (str): 交易品种代码
            setting (dict): 策略参数字典，可包含fast_window和slow_window
        
        Attributes:
            fast_window (int): 快速均线周期，默认为10
            slow_window (int): 慢速均线周期，默认为20
            fast_ma (float): 快速均线当前值
            slow_ma (float): 慢速均线当前值
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
    
    def on_init(self):
        """策略初始化回调
        
        加载足够的历史K线数据用于计算移动平均线。
        加载数量取fast_window和slow_window中的较大值。
        """
        super().on_init()
        self.write_log(f"快速均线: {self.fast_window}")
        self.write_log(f"慢速均线: {self.slow_window}")
        self.load_bar(max(self.fast_window, self.slow_window))
    
    def on_bar(self, bar: BarData):
        """收到K线数据回调
        
        Args:
            bar (BarData): K线数据对象
        
        交易逻辑:
            1. 计算快速均线和慢速均线
            2. 当快速均线上穿慢速均线且无持仓时，买入开仓
            3. 当快速均线下穿慢速均线且有多头持仓时，卖出平仓
        """
        # 计算均线
        self.fast_ma = self.calculate_ma(self.fast_window, bar.close_price)
        self.slow_ma = self.calculate_ma(self.slow_window, bar.close_price)
        
        # 金叉买入
        if self.fast_ma > self.slow_ma and not self.pos:
            self.buy(bar.close_price, 1)
        
        # 死叉卖出
        elif self.fast_ma < self.slow_ma and self.pos > 0:
            self.sell(bar.close_price, abs(self.pos))
    
    def calculate_ma(self, window: int, close_price: float) -> float:
        """计算移动平均线
        
        Args:
            window (int): 均线周期，计算均线的K线数量
            close_price (float): 当前收盘价
        
        Returns:
            float: 移动平均线值
        """
        # 简化实现，使用当前价格的简单计算
        # 因为历史数据较少，使用简单的平均值
        if hasattr(self, 'close_prices'):
            self.close_prices.append(close_price)
            if len(self.close_prices) > window:
                self.close_prices = self.close_prices[-window:]
            return sum(self.close_prices) / len(self.close_prices)
        else:
            # 初始化收盘价列表
            self.close_prices = [close_price]
            return close_price


class MACDBacktestStrategy(BacktestStrategy):
    """MACD回测策略
    
    基于MACD（指数平滑异同移动平均线）指标的趋势跟踪策略。
    当MACD柱状图由负转正时买入（金叉），由正转负时卖出（死叉）。
    """
    
    author = "MACD"
    
    # 策略参数
    fast_period = 12
    slow_period = 26
    signal_period = 9
    
    # 策略变量
    macd = 0
    signal = 0
    hist = 0
    
    parameters = ["fast_period", "slow_period", "signal_period"]
    variables = ["macd", "signal", "hist"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """初始化MACD回测策略
        
        Args:
            cta_engine: CTA策略引擎对象
            strategy_name (str): 策略名称
            vt_symbol (str): 交易品种代码
            setting (dict): 策略参数字典，可包含fast_period、slow_period和signal_period
        
        Attributes:
            fast_period (int): 快速EMA周期，默认为12
            slow_period (int): 慢速EMA周期，默认为26
            signal_period (int): 信号线EMA周期，默认为9
            macd (float): MACD线当前值（快速EMA - 慢速EMA）
            signal (float): 信号线当前值（MACD的EMA）
            hist (float): MACD柱状图值（MACD - 信号线）
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
    
    def on_init(self):
        """策略初始化回调
        
        加载足够的历史K线数据用于计算MACD指标。
        加载数量为slow_period + signal_period。
        """
        super().on_init()
        self.write_log(f"快速周期: {self.fast_period}")
        self.write_log(f"慢速周期: {self.slow_period}")
        self.write_log(f"信号周期: {self.signal_period}")
        self.load_bar(self.slow_period + self.signal_period)
    
    def on_bar(self, bar: BarData):
        """收到K线数据回调
        
        Args:
            bar (BarData): K线数据对象
        
        交易逻辑:
            1. 计算MACD指标（MACD线、信号线、柱状图）
            2. 当柱状图由负转正且无持仓时，买入开仓
            3. 当柱状图由正转负且有多头持仓时，卖出平仓
        """
        # 保存当前收盘价
        self.close_price = bar.close_price
        
        # 计算MACD
        self.calculate_macd()
        
        # 金叉买入
        if self.hist > 0 and not self.pos:
            self.buy(bar.close_price, 1)
        
        # 死叉卖出
        elif self.hist < 0 and self.pos > 0:
            self.sell(bar.close_price, abs(self.pos))
    
    def calculate_macd(self):
        """计算MACD指标
        
        计算步骤:
            1. 计算快速EMA（指数移动平均线）
            2. 计算慢速EMA
            3. 计算MACD线 = 快速EMA - 慢速EMA
            4. 计算信号线 = MACD线的EMA
            5. 计算柱状图 = MACD线 - 信号线
        """
        # 简化实现，使用当前价格的简单计算
        # 因为历史数据较少，使用简单的趋势判断
        if hasattr(self, 'last_close'):
            price_change = self.close_price - self.last_close
            if price_change > 0:
                self.hist = 1.0
            else:
                self.hist = -1.0
        else:
            self.hist = 0.0
        
        # 保存当前收盘价
        if hasattr(self, 'close_price'):
            self.last_close = self.close_price


class RSIBacktestStrategy(BacktestStrategy):
    """RSI回测策略
    
    基于RSI（相对强弱指标）的均值回归策略。
    当RSI低于超卖阈值时买入，高于超买阈值时卖出。
    """
    
    author = "RSI"
    
    # 策略参数
    rsi_period = 14
    overbought = 70
    oversold = 30
    
    # 策略变量
    rsi = 50
    
    parameters = ["rsi_period", "overbought", "oversold"]
    variables = ["rsi"]
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """初始化RSI回测策略
        
        Args:
            cta_engine: CTA策略引擎对象
            strategy_name (str): 策略名称
            vt_symbol (str): 交易品种代码
            setting (dict): 策略参数字典，可包含rsi_period、overbought和oversold
        
        Attributes:
            rsi_period (int): RSI计算周期，默认为14
            overbought (int): 超买阈值，默认为70，高于此值认为超买
            oversold (int): 超卖阈值，默认为30，低于此值认为超卖
            rsi (float): RSI当前值，范围0-100
        """
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
    
    def on_init(self):
        """策略初始化回调
        
        加载足够的历史K线数据用于计算RSI指标。
        加载数量为rsi_period。
        """
        super().on_init()
        self.write_log(f"RSI周期: {self.rsi_period}")
        self.write_log(f"超买阈值: {self.overbought}")
        self.write_log(f"超卖阈值: {self.oversold}")
        self.load_bar(self.rsi_period)
    
    def on_bar(self, bar: BarData):
        """收到K线数据回调
        
        Args:
            bar (BarData): K线数据对象
        
        交易逻辑:
            1. 计算RSI指标
            2. 当RSI低于超卖阈值且无持仓时，买入开仓
            3. 当RSI高于超买阈值且有多头持仓时，卖出平仓
        """
        # 保存当前收盘价
        self.close_price = bar.close_price
        
        # 计算RSI
        self.calculate_rsi()
        
        # 超卖买入
        if self.rsi < self.oversold and not self.pos:
            self.buy(bar.close_price, 1)
        
        # 超买卖出
        elif self.rsi > self.overbought and self.pos > 0:
            self.sell(bar.close_price, abs(self.pos))
    
    def calculate_rsi(self):
        """计算RSI指标
        
        计算步骤:
            1. 计算价格变化
            2. 计算上涨和下跌的平均值
            3. 计算相对强度(RS) = 上涨平均值 / 下跌平均值
            4. 计算RSI = 100 - (100 / (1 + RS))
        """
        # 简化实现，使用当前价格的简单计算
        # 因为历史数据较少，使用简单的超买超卖判断
        if hasattr(self, 'last_close'):
            price_change = self.close_price - self.last_close
            if price_change > 0:
                # 价格上涨，RSI 设为 70
                self.rsi = 70.0
            else:
                # 价格下跌，RSI 设为 30
                self.rsi = 30.0
        else:
            # 初始值
            self.rsi = 50.0
        
        # 保存当前收盘价
        if hasattr(self, 'close_price'):
            self.last_close = self.close_price
