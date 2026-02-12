"""
股票特有策略模块

实现股票特有策略，包括价值投资、成长投资、技术分析等
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
import numpy as np
import pandas as pd
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
from internal.data.dividend_adjustment import get_dividend_adjuster
from internal.trading.cost_calculator import get_stock_trading_cost_calculator
from internal.trading.account_manager import get_account_manager
from internal.trading.trading_time import get_trading_time_manager
from internal.risk.stock_risk_manager import get_stock_risk_manager


class ValueInvestingStrategy(CtaTemplate):
    """价值投资策略"""
    
    author = "Value Investing"
    
    # 策略参数
    pe_threshold = 15.0  # 市盈率阈值
    pb_threshold = 1.5  # 市净率阈值
    roe_threshold = 0.1  # 净资产收益率阈值
    market_cap_min = 10000000000  # 最小市值（100亿）
    cash_dividend_ratio = 0.03  # 现金分红率阈值
    holding_period = 30  # 持有期（天）
    
    # 风险控制参数
    max_position_per_stock = 0.2  # 单股票最大持仓比例
    max_industry_exposure = 0.4  # 单行业最大暴露
    stop_loss_ratio = 0.1  # 止损比例
    take_profit_ratio = 0.3  # 止盈比例
    
    # 变量
    stocks_held = set()  # 持有股票
    stock_fundamentals = {}  # 股票基本面数据
    stock_industry = {}  # 股票行业
    industry_exposure = {}  # 行业暴露
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 1, self.on_1min_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(size=100)
        self.dividend_adjuster = get_dividend_adjuster()
        self.cost_calculator = get_stock_trading_cost_calculator()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        self.risk_manager = get_stock_risk_manager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        """处理行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线推送"""
        self.bg.update_bar(bar)
    
    def on_1min_bar(self, bar: BarData):
        """处理1分钟K线"""
        # 检查是否为交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return
        
        # 更新数组管理器
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 获取股票代码
        symbol = bar.vt_symbol.split('.')[0]
        
        # 更新基本面数据
        self._update_fundamentals(symbol)
        
        # 检查买入条件
        if symbol not in self.stocks_held and self._check_buy_conditions(symbol, bar):
            self._buy(symbol, bar)
        
        # 检查卖出条件
        elif symbol in self.stocks_held and self._check_sell_conditions(symbol, bar):
            self._sell(symbol, bar)
        
        self.put_event()
    
    def _update_fundamentals(self, symbol: str):
        """更新基本面数据
        
        Args:
            symbol: 股票代码
        """
        # 模拟基本面数据
        # 实际应用中应该从数据源获取真实的基本面数据
        if symbol not in self.stock_fundamentals:
            self.stock_fundamentals[symbol] = {
                "pe": np.random.uniform(5, 30),
                "pb": np.random.uniform(0.5, 5),
                "roe": np.random.uniform(0.05, 0.2),
                "market_cap": np.random.uniform(10000000000, 1000000000000),
                "cash_dividend_ratio": np.random.uniform(0.01, 0.08),
                "industry": np.random.choice(["银行", "医药", "科技", "消费", "能源", "地产"])
            }
            self.stock_industry[symbol] = self.stock_fundamentals[symbol]["industry"]
    
    def _check_buy_conditions(self, symbol: str, bar: BarData) -> bool:
        """检查买入条件
        
        Args:
            symbol: 股票代码
            bar: K线数据
            
        Returns:
            是否满足买入条件
        """
        # 获取基本面数据
        if symbol not in self.stock_fundamentals:
            return False
        
        fundamentals = self.stock_fundamentals[symbol]
        
        # 价值投资核心指标
        if fundamentals["pe"] > self.pe_threshold:
            return False
        
        if fundamentals["pb"] > self.pb_threshold:
            return False
        
        if fundamentals["roe"] < self.roe_threshold:
            return False
        
        if fundamentals["market_cap"] < self.market_cap_min:
            return False
        
        if fundamentals["cash_dividend_ratio"] < self.cash_dividend_ratio:
            return False
        
        # 行业暴露检查
        industry = self.stock_industry[symbol]
        if industry in self.industry_exposure:
            if self.industry_exposure[industry] > self.max_industry_exposure:
                return False
        
        # 账户风险检查
        account = self.account_manager.get_account("default")
        if account:
            # 检查单股票持仓比例
            if symbol in account.positions:
                position = account.get_position(symbol)
                if position.market_value / account.total_asset > self.max_position_per_stock:
                    return False
            
            # 检查总持仓数量
            if len(self.stocks_held) >= 10:  # 最多持有10只股票
                return False
        
        return True
    
    def _check_sell_conditions(self, symbol: str, bar: BarData) -> bool:
        """检查卖出条件
        
        Args:
            symbol: 股票代码
            bar: K线数据
            
        Returns:
            是否满足卖出条件
        """
        # 检查止损
        position = self.get_position(symbol)
        if position:
            if position.profit_ratio < -self.stop_loss_ratio:
                return True
            
            # 检查止盈
            if position.profit_ratio > self.take_profit_ratio:
                return True
        
        # 检查基本面恶化
        if symbol in self.stock_fundamentals:
            fundamentals = self.stock_fundamentals[symbol]
            if fundamentals["pe"] > self.pe_threshold * 1.5:
                return True
            
            if fundamentals["pb"] > self.pb_threshold * 1.5:
                return True
            
            if fundamentals["roe"] < self.roe_threshold * 0.8:
                return True
        
        # 检查持有期
        # 实际应用中应该记录买入时间
        
        return False
    
    def _buy(self, symbol: str, bar: BarData):
        """买入股票
        
        Args:
            symbol: 股票代码
            bar: K线数据
        """
        account = self.account_manager.get_account("default")
        if not account:
            return
        
        # 计算买入数量
        cash_available = account.cash * self.max_position_per_stock
        price = bar.close_price
        volume = int(cash_available / price / 100) * 100  # 100股为单位
        
        if volume >= 100:
            # 检查风险
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=f"{symbol}.{(Exchange.SSE if symbol.startswith('6') else Exchange.SZSE).value}",
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.buy(price, volume)
                self.stocks_held.add(symbol)
                
                # 更新行业暴露
                industry = self.stock_industry[symbol]
                if industry not in self.industry_exposure:
                    self.industry_exposure[industry] = 0
                self.industry_exposure[industry] += volume * price
                
                self.write_log(f"买入 {symbol}，价格: {price}，数量: {volume}")
    
    def _sell(self, symbol: str, bar: BarData):
        """卖出股票
        
        Args:
            symbol: 股票代码
            bar: K线数据
        """
        position = self.get_position(symbol)
        if position and position.volume > 0:
            # 检查风险
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=bar.close_price,
                volume=position.volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=f"{symbol}.{(Exchange.SSE if symbol.startswith('6') else Exchange.SZSE).value}",
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.sell(bar.close_price, position.volume)
                self.stocks_held.remove(symbol)
                
                # 更新行业暴露
                industry = self.stock_industry[symbol]
                if industry in self.industry_exposure:
                    self.industry_exposure[industry] -= position.volume * bar.close_price
                    if self.industry_exposure[industry] <= 0:
                        del self.industry_exposure[industry]
                
                self.write_log(f"卖出 {symbol}，价格: {bar.close_price}，数量: {position.volume}")
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass


class GrowthInvestingStrategy(CtaTemplate):
    """成长投资策略"""
    
    author = "Growth Investing"
    
    # 策略参数
    revenue_growth_threshold = 0.2  # 营收增长率阈值
    earnings_growth_threshold = 0.25  # 净利润增长率阈值
    eps_growth_threshold = 0.2  # 每股收益增长率阈值
    sales_growth_threshold = 0.15  # 销售额增长率阈值
    profit_margin_threshold = 0.15  # 利润率阈值
    
    # 技术分析参数
    ma_short = 20  # 短期均线
    ma_long = 60  # 长期均线
    rsi_period = 14  # RSI周期
    rsi_overbought = 70  # RSI超买
    rsi_oversold = 30  # RSI超卖
    
    # 风险控制参数
    max_position_per_stock = 0.15  # 单股票最大持仓比例
    stop_loss_ratio = 0.15  # 止损比例
    take_profit_ratio = 0.4  # 止盈比例
    
    # 变量
    stocks_held = set()  # 持有股票
    stock_growth_metrics = {}  # 成长指标
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 1, self.on_1min_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(size=200)
        self.dividend_adjuster = get_dividend_adjuster()
        self.cost_calculator = get_stock_trading_cost_calculator()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        self.risk_manager = get_stock_risk_manager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(20)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        """处理行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线推送"""
        self.bg.update_bar(bar)
    
    def on_1min_bar(self, bar: BarData):
        """处理1分钟K线"""
        # 检查是否为交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return
        
        # 更新数组管理器
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 获取股票代码
        symbol = bar.vt_symbol.split('.')[0]
        
        # 更新成长指标
        self._update_growth_metrics(symbol)
        
        # 检查买入条件
        if symbol not in self.stocks_held and self._check_buy_conditions(symbol, bar):
            self._buy(symbol, bar)
        
        # 检查卖出条件
        elif symbol in self.stocks_held and self._check_sell_conditions(symbol, bar):
            self._sell(symbol, bar)
        
        self.put_event()
    
    def _update_growth_metrics(self, symbol: str):
        """更新成长指标
        
        Args:
            symbol: 股票代码
        """
        # 模拟成长指标
        # 实际应用中应该从数据源获取真实的成长指标
        if symbol not in self.stock_growth_metrics:
            self.stock_growth_metrics[symbol] = {
                "revenue_growth": np.random.uniform(0.1, 0.5),
                "earnings_growth": np.random.uniform(0.15, 0.6),
                "eps_growth": np.random.uniform(0.1, 0.4),
                "sales_growth": np.random.uniform(0.1, 0.4),
                "profit_margin": np.random.uniform(0.1, 0.3)
            }
    
    def _check_buy_conditions(self, symbol: str, bar: BarData) -> bool:
        """检查买入条件
        
        Args:
            symbol: 股票代码
            bar: K线数据
            
        Returns:
            是否满足买入条件
        """
        # 获取成长指标
        if symbol not in self.stock_growth_metrics:
            return False
        
        metrics = self.stock_growth_metrics[symbol]
        
        # 成长投资核心指标
        if metrics["revenue_growth"] < self.revenue_growth_threshold:
            return False
        
        if metrics["earnings_growth"] < self.earnings_growth_threshold:
            return False
        
        if metrics["eps_growth"] < self.eps_growth_threshold:
            return False
        
        if metrics["sales_growth"] < self.sales_growth_threshold:
            return False
        
        if metrics["profit_margin"] < self.profit_margin_threshold:
            return False
        
        # 技术分析指标
        if not self._check_technical_indicators(bar):
            return False
        
        # 账户风险检查
        account = self.account_manager.get_account("default")
        if not account:
            return False
        
        # 检查单股票持仓比例
        if symbol in account.positions:
            position = account.get_position(symbol)
            if position.market_value / account.total_asset > self.max_position_per_stock:
                return False
        
        return True
    
    def _check_technical_indicators(self, bar: BarData) -> bool:
        """检查技术指标
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足技术指标条件
        """
        # 计算均线
        ma_short = self.am.sma(self.ma_short, array=False)
        ma_long = self.am.sma(self.ma_long, array=False)
        
        # 计算RSI
        rsi = self.am.rsi(self.rsi_period, array=False)
        
        # 检查均线金叉
        if ma_short is None or ma_long is None:
            return False
        
        if ma_short <= ma_long:
            return False
        
        # 检查RSI
        if rsi is None:
            return False
        
        if rsi > self.rsi_overbought:
            return False
        
        return True
    
    def _check_sell_conditions(self, symbol: str, bar: BarData) -> bool:
        """检查卖出条件
        
        Args:
            symbol: 股票代码
            bar: K线数据
            
        Returns:
            是否满足卖出条件
        """
        # 检查止损
        position = self.get_position(symbol)
        if position:
            if position.profit_ratio < -self.stop_loss_ratio:
                return True
            
            # 检查止盈
            if position.profit_ratio > self.take_profit_ratio:
                return True
        
        # 检查成长指标恶化
        if symbol in self.stock_growth_metrics:
            metrics = self.stock_growth_metrics[symbol]
            if metrics["revenue_growth"] < self.revenue_growth_threshold * 0.8:
                return True
            
            if metrics["earnings_growth"] < self.earnings_growth_threshold * 0.8:
                return True
        
        # 检查技术指标
        ma_short = self.am.sma(self.ma_short, array=False)
        ma_long = self.am.sma(self.ma_long, array=False)
        
        if ma_short is not None and ma_long is not None:
            if ma_short <= ma_long:
                return True
        
        return False
    
    def _buy(self, symbol: str, bar: BarData):
        """买入股票
        
        Args:
            symbol: 股票代码
            bar: K线数据
        """
        account = self.account_manager.get_account("default")
        if not account:
            return
        
        # 计算买入数量
        cash_available = account.cash * self.max_position_per_stock
        price = bar.close_price
        volume = int(cash_available / price / 100) * 100  # 100股为单位
        
        if volume >= 100:
            # 检查风险
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=f"{symbol}.{(Exchange.SSE if symbol.startswith('6') else Exchange.SZSE).value}",
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.buy(price, volume)
                self.stocks_held.add(symbol)
                self.write_log(f"买入 {symbol}，价格: {price}，数量: {volume}")
    
    def _sell(self, symbol: str, bar: BarData):
        """卖出股票
        
        Args:
            symbol: 股票代码
            bar: K线数据
        """
        position = self.get_position(symbol)
        if position and position.volume > 0:
            # 检查风险
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=bar.close_price,
                volume=position.volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=f"{symbol}.{(Exchange.SSE if symbol.startswith('6') else Exchange.SZSE).value}",
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.sell(bar.close_price, position.volume)
                self.stocks_held.remove(symbol)
                self.write_log(f"卖出 {symbol}，价格: {bar.close_price}，数量: {position.volume}")
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass


class TechnicalAnalysisStrategy(CtaTemplate):
    """技术分析策略"""
    
    author = "Technical Analysis"
    
    # 策略参数
    # 均线参数
    ma_fast = 10  # 快速均线
    ma_medium = 20  # 中速均线
    ma_slow = 60  # 慢速均线
    
    # MACD参数
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    
    # KDJ参数
    kdj_period = 9
    kdj_slow = 3
    
    # RSI参数
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30
    
    # 布林带参数
    boll_period = 20
    boll_dev = 2
    
    # 成交量参数
    volume_ma = 20
    
    # 风险控制参数
    max_position_per_stock = 0.1  # 单股票最大持仓比例
    stop_loss_ratio = 0.08  # 止损比例
    take_profit_ratio = 0.2  # 止盈比例
    
    # 变量
    position = 0
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 1, self.on_1min_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(size=200)
        self.dividend_adjuster = get_dividend_adjuster()
        self.cost_calculator = get_stock_trading_cost_calculator()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        self.risk_manager = get_stock_risk_manager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(60)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        """处理行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线推送"""
        self.bg.update_bar(bar)
    
    def on_1min_bar(self, bar: BarData):
        """处理1分钟K线"""
        # 检查是否为交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return
        
        # 更新数组管理器
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 计算指标
        self._calculate_indicators()
        
        # 检查买入条件
        if self.position == 0 and self._check_buy_conditions(bar):
            self._buy(bar)
        
        # 检查卖出条件
        elif self.position > 0 and self._check_sell_conditions(bar):
            self._sell(bar)
        
        self.put_event()
    
    def _calculate_indicators(self):
        """计算技术指标"""
        # 均线
        self.ma_fast = self.am.sma(self.ma_fast, array=False)
        self.ma_medium = self.am.sma(self.ma_medium, array=False)
        self.ma_slow = self.am.sma(self.ma_slow, array=False)
        
        # MACD
        self.macd, self.macd_signal, self.macd_hist = self.am.macd(
            self.macd_fast, self.macd_slow, self.macd_signal
        )
        
        # KDJ
        self.k, self.d = self.am.kdj(self.kdj_period, self.kdj_slow)
        self.j = 3 * self.k - 2 * self.d if self.k and self.d else None
        
        # RSI
        self.rsi = self.am.rsi(self.rsi_period, array=False)
        
        # 布林带
        self.boll_mid = self.am.sma(self.boll_period, array=False)
        self.boll_std = self.am.std(self.boll_period, array=False)
        self.boll_up = self.boll_mid + self.boll_dev * self.boll_std if self.boll_mid and self.boll_std else None
        self.boll_down = self.boll_mid - self.boll_dev * self.boll_std if self.boll_mid and self.boll_std else None
        
        # 成交量
        self.volume_ma = self.am.sma(self.volume_ma, array=False, price='volume')
    
    def _check_buy_conditions(self, bar: BarData) -> bool:
        """检查买入条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足买入条件
        """
        # 均线多头排列
        if not (self.ma_fast and self.ma_medium and self.ma_slow):
            return False
        
        if not (self.ma_fast > self.ma_medium > self.ma_slow):
            return False
        
        # MACD金叉
        if not (self.macd and self.macd_signal):
            return False
        
        if not (self.macd > self.macd_signal > 0):
            return False
        
        # KDJ金叉
        if not (self.k and self.d and self.j):
            return False
        
        if not (self.j > self.k > self.d):
            return False
        
        # RSI
        if not self.rsi:
            return False
        
        if self.rsi < self.rsi_oversold:
            return False
        
        if self.rsi > self.rsi_overbought:
            return False
        
        # 布林带
        if not (self.boll_mid and self.boll_up and self.boll_down):
            return False
        
        if bar.close_price < self.boll_down:
            return False
        
        # 成交量
        if not self.volume_ma:
            return False
        
        if bar.volume < self.volume_ma:
            return False
        
        return True
    
    def _check_sell_conditions(self, bar: BarData) -> bool:
        """检查卖出条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足卖出条件
        """
        # 均线空头排列
        if self.ma_fast and self.ma_medium and self.ma_slow:
            if self.ma_fast < self.ma_medium < self.ma_slow:
                return True
        
        # MACD死叉
        if self.macd and self.macd_signal:
            if self.macd < self.macd_signal < 0:
                return True
        
        # KDJ死叉
        if self.k and self.d and self.j:
            if self.j < self.k < self.d:
                return True
        
        # RSI超买
        if self.rsi and self.rsi > self.rsi_overbought:
            return True
        
        # 布林带上轨
        if self.boll_up and bar.close_price > self.boll_up:
            return True
        
        # 止损止盈
        position = self.get_position()
        if position:
            if position.profit_ratio < -self.stop_loss_ratio:
                return True
            if position.profit_ratio > self.take_profit_ratio:
                return True
        
        return False
    
    def _buy(self, bar: BarData):
        """买入股票
        
        Args:
            bar: K线数据
        """
        account = self.account_manager.get_account("default")
        if not account:
            return
        
        # 计算买入数量
        cash_available = account.cash * self.max_position_per_stock
        price = bar.close_price
        volume = int(cash_available / price / 100) * 100  # 100股为单位
        
        if volume >= 100:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.buy(price, volume)
                self.position = volume
                self.write_log(f"买入 {bar.vt_symbol}，价格: {price}，数量: {volume}")
    
    def _sell(self, bar: BarData):
        """卖出股票
        
        Args:
            bar: K线数据
        """
        position = self.get_position()
        if position and position.volume > 0:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=bar.close_price,
                volume=position.volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.sell(bar.close_price, position.volume)
                self.position = 0
                self.write_log(f"卖出 {bar.vt_symbol}，价格: {bar.close_price}，数量: {position.volume}")
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass


class MomentumStrategy(CtaTemplate):
    """动量策略"""
    
    author = "Momentum Strategy"
    
    # 策略参数
    lookback_period = 20  # 回溯期
    holding_period = 5  # 持有期
    threshold = 0.05  # 动量阈值
    
    # 风险控制参数
    max_position_per_stock = 0.1  # 单股票最大持仓比例
    stop_loss_ratio = 0.08  # 止损比例
    
    # 变量
    position = 0
    entry_time = None
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 1, self.on_1min_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(size=100)
        self.dividend_adjuster = get_dividend_adjuster()
        self.cost_calculator = get_stock_trading_cost_calculator()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        self.risk_manager = get_stock_risk_manager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(self.lookback_period)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        """处理行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线推送"""
        self.bg.update_bar(bar)
    
    def on_1min_bar(self, bar: BarData):
        """处理1分钟K线"""
        # 检查是否为交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return
        
        # 更新数组管理器
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 检查买入条件
        if self.position == 0 and self._check_buy_conditions(bar):
            self._buy(bar)
        
        # 检查卖出条件
        elif self.position > 0 and self._check_sell_conditions(bar):
            self._sell(bar)
        
        self.put_event()
    
    def _check_buy_conditions(self, bar: BarData) -> bool:
        """检查买入条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足买入条件
        """
        # 计算动量
        close_prices = self.am.close[:-1]  # 排除当前K线
        if len(close_prices) < self.lookback_period:
            return False
        
        # 计算收益率
        returns = np.diff(close_prices) / close_prices[:-1]
        momentum = np.mean(returns[-self.lookback_period:])
        
        # 检查动量
        if momentum < self.threshold:
            return False
        
        return True
    
    def _check_sell_conditions(self, bar: BarData) -> bool:
        """检查卖出条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足卖出条件
        """
        # 检查持有期
        if self.entry_time:
            holding_days = (datetime.now() - self.entry_time).days
            if holding_days >= self.holding_period:
                return True
        
        # 检查止损
        position = self.get_position()
        if position:
            if position.profit_ratio < -self.stop_loss_ratio:
                return True
        
        # 检查动量反转
        close_prices = self.am.close[:-1]  # 排除当前K线
        if len(close_prices) >= self.lookback_period:
            returns = np.diff(close_prices) / close_prices[:-1]
            momentum = np.mean(returns[-self.lookback_period:])
            if momentum < -self.threshold:
                return True
        
        return False
    
    def _buy(self, bar: BarData):
        """买入股票
        
        Args:
            bar: K线数据
        """
        account = self.account_manager.get_account("default")
        if not account:
            return
        
        # 计算买入数量
        cash_available = account.cash * self.max_position_per_stock
        price = bar.close_price
        volume = int(cash_available / price / 100) * 100  # 100股为单位
        
        if volume >= 100:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.buy(price, volume)
                self.position = volume
                self.entry_time = datetime.now()
                self.write_log(f"买入 {bar.vt_symbol}，价格: {price}，数量: {volume}")
    
    def _sell(self, bar: BarData):
        """卖出股票
        
        Args:
            bar: K线数据
        """
        position = self.get_position()
        if position and position.volume > 0:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=bar.close_price,
                volume=position.volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.sell(bar.close_price, position.volume)
                self.position = 0
                self.entry_time = None
                self.write_log(f"卖出 {bar.vt_symbol}，价格: {bar.close_price}，数量: {position.volume}")
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass


class MeanReversionStrategy(CtaTemplate):
    """均值回归策略"""
    
    author = "Mean Reversion Strategy"
    
    # 策略参数
    lookback_period = 20  # 回溯期
    z_score_threshold = 2.0  # Z-score阈值
    
    # 风险控制参数
    max_position_per_stock = 0.1  # 单股票最大持仓比例
    stop_loss_ratio = 0.08  # 止损比例
    take_profit_ratio = 0.1  # 止盈比例
    
    # 变量
    position = 0
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 1, self.on_1min_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(size=100)
        self.dividend_adjuster = get_dividend_adjuster()
        self.cost_calculator = get_stock_trading_cost_calculator()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        self.risk_manager = get_stock_risk_manager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(self.lookback_period)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        """处理行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线推送"""
        self.bg.update_bar(bar)
    
    def on_1min_bar(self, bar: BarData):
        """处理1分钟K线"""
        # 检查是否为交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return
        
        # 更新数组管理器
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 计算Z-score
        z_score = self._calculate_z_score()
        
        # 检查买入条件
        if self.position == 0 and z_score < -self.z_score_threshold:
            self._buy(bar)
        
        # 检查卖出条件
        elif self.position > 0 and (z_score > self.z_score_threshold or self._check_sell_conditions(bar)):
            self._sell(bar)
        
        self.put_event()
    
    def _calculate_z_score(self) -> float:
        """计算Z-score
        
        Returns:
            Z-score值
        """
        close_prices = self.am.close[:-1]  # 排除当前K线
        if len(close_prices) < self.lookback_period:
            return 0.0
        
        # 计算均值和标准差
        mean = np.mean(close_prices[-self.lookback_period:])
        std = np.std(close_prices[-self.lookback_period:])
        
        if std == 0:
            return 0.0
        
        # 计算Z-score
        current_price = close_prices[-1]
        z_score = (current_price - mean) / std
        
        return z_score
    
    def _check_sell_conditions(self, bar: BarData) -> bool:
        """检查卖出条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足卖出条件
        """
        # 检查止损
        position = self.get_position()
        if position:
            if position.profit_ratio < -self.stop_loss_ratio:
                return True
            
            # 检查止盈
            if position.profit_ratio > self.take_profit_ratio:
                return True
        
        return False
    
    def _buy(self, bar: BarData):
        """买入股票
        
        Args:
            bar: K线数据
        """
        account = self.account_manager.get_account("default")
        if not account:
            return
        
        # 计算买入数量
        cash_available = account.cash * self.max_position_per_stock
        price = bar.close_price
        volume = int(cash_available / price / 100) * 100  # 100股为单位
        
        if volume >= 100:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.buy(price, volume)
                self.position = volume
                self.write_log(f"买入 {bar.vt_symbol}，价格: {price}，数量: {volume}")
    
    def _sell(self, bar: BarData):
        """卖出股票
        
        Args:
            bar: K线数据
        """
        position = self.get_position()
        if position and position.volume > 0:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=bar.close_price,
                volume=position.volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.sell(bar.close_price, position.volume)
                self.position = 0
                self.write_log(f"卖出 {bar.vt_symbol}，价格: {bar.close_price}，数量: {position.volume}")
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass


class SwingTradingStrategy(CtaTemplate):
    """波段交易策略"""
    
    author = "Swing Trading Strategy"
    
    # 策略参数
    trend_period = 60  # 趋势周期
    swing_period = 20  # 波段周期
    
    # 风险控制参数
    max_position_per_stock = 0.15  # 单股票最大持仓比例
    stop_loss_ratio = 0.08  # 止损比例
    take_profit_ratio = 0.2  # 止盈比例
    
    # 变量
    position = 0
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, 1, self.on_1min_bar, interval=Interval.MINUTE)
        self.am = ArrayManager(size=200)
        self.dividend_adjuster = get_dividend_adjuster()
        self.cost_calculator = get_stock_trading_cost_calculator()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        self.risk_manager = get_stock_risk_manager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(self.trend_period)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
        self.put_event()
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
        self.put_event()
    
    def on_tick(self, tick: TickData):
        """处理行情推送"""
        self.bg.update_tick(tick)
    
    def on_bar(self, bar: BarData):
        """处理K线推送"""
        self.bg.update_bar(bar)
    
    def on_1min_bar(self, bar: BarData):
        """处理1分钟K线"""
        # 检查是否为交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return
        
        # 更新数组管理器
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        
        # 检查买入条件
        if self.position == 0 and self._check_buy_conditions(bar):
            self._buy(bar)
        
        # 检查卖出条件
        elif self.position > 0 and self._check_sell_conditions(bar):
            self._sell(bar)
        
        self.put_event()
    
    def _check_buy_conditions(self, bar: BarData) -> bool:
        """检查买入条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足买入条件
        """
        # 检查趋势
        trend_ma = self.am.sma(self.trend_period, array=False)
        swing_ma = self.am.sma(self.swing_period, array=False)
        
        if not (trend_ma and swing_ma):
            return False
        
        # 检查趋势向上
        if swing_ma <= trend_ma:
            return False
        
        # 检查价格突破
        high_prices = self.am.high[:-1]
        if len(high_prices) < self.swing_period:
            return False
        
        if bar.close_price <= max(high_prices[-self.swing_period:]):
            return False
        
        # 检查成交量
        volume_ma = self.am.sma(self.swing_period, array=False, price='volume')
        if not volume_ma:
            return False
        
        if bar.volume < volume_ma:
            return False
        
        return True
    
    def _check_sell_conditions(self, bar: BarData) -> bool:
        """检查卖出条件
        
        Args:
            bar: K线数据
            
        Returns:
            是否满足卖出条件
        """
        # 检查趋势
        trend_ma = self.am.sma(self.trend_period, array=False)
        swing_ma = self.am.sma(self.swing_period, array=False)
        
        if trend_ma and swing_ma:
            if swing_ma <= trend_ma:
                return True
        
        # 检查价格跌破
        low_prices = self.am.low[:-1]
        if len(low_prices) >= self.swing_period:
            if bar.close_price <= min(low_prices[-self.swing_period:]):
                return True
        
        # 检查止损止盈
        position = self.get_position()
        if position:
            if position.profit_ratio < -self.stop_loss_ratio:
                return True
            if position.profit_ratio > self.take_profit_ratio:
                return True
        
        return False
    
    def _buy(self, bar: BarData):
        """买入股票
        
        Args:
            bar: K线数据
        """
        account = self.account_manager.get_account("default")
        if not account:
            return
        
        # 计算买入数量
        cash_available = account.cash * self.max_position_per_stock
        price = bar.close_price
        volume = int(cash_available / price / 100) * 100  # 100股为单位
        
        if volume >= 100:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.LONG,
                offset=Offset.OPEN,
                price=price,
                volume=volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.buy(price, volume)
                self.position = volume
                self.write_log(f"买入 {bar.vt_symbol}，价格: {price}，数量: {volume}")
    
    def _sell(self, bar: BarData):
        """卖出股票
        
        Args:
            bar: K线数据
        """
        position = self.get_position()
        if position and position.volume > 0:
            # 检查风险
            symbol = bar.vt_symbol.split('.')[0]
            order = OrderData(
                symbol=symbol,
                exchange=Exchange.SSE if symbol.startswith('6') else Exchange.SZSE,
                direction=Direction.SHORT,
                offset=Offset.CLOSE,
                price=bar.close_price,
                volume=position.volume,
                vt_orderid=f"{symbol}_{datetime.now().timestamp()}",
                vt_symbol=bar.vt_symbol,
                datetime=datetime.now(),
                status=Status.SUBMITTING
            )
            
            risk_check = self.risk_manager.check_order_risk("default", order)
            if risk_check["risk_passed"]:
                # 下单
                self.sell(bar.close_price, position.volume)
                self.position = 0
                self.write_log(f"卖出 {bar.vt_symbol}，价格: {bar.close_price}，数量: {position.volume}")
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        self.put_event()
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass


# 策略工厂
class StockStrategyFactory:
    """股票策略工厂"""
    
    @staticmethod
    def create_strategy(strategy_name: str, cta_engine, vt_symbol, setting) -> CtaTemplate:
        """创建股票策略
        
        Args:
            strategy_name: 策略名称
            cta_engine: CTA引擎
            vt_symbol: 合约代码
            setting: 策略设置
            
        Returns:
            策略实例
        """
        strategy_map = {
            "value_investing": ValueInvestingStrategy,
            "growth_investing": GrowthInvestingStrategy,
            "technical_analysis": TechnicalAnalysisStrategy,
            "momentum": MomentumStrategy,
            "mean_reversion": MeanReversionStrategy,
            "swing_trading": SwingTradingStrategy
        }
        
        if strategy_name not in strategy_map:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        return strategy_map[strategy_name](cta_engine, strategy_name, vt_symbol, setting)
    
    @staticmethod
    def get_available_strategies() -> List[str]:
        """获取可用策略列表
        
        Returns:
            可用策略列表
        """
        return [
            "value_investing",
            "growth_investing",
            "technical_analysis",
            "momentum",
            "mean_reversion",
            "swing_trading"
        ]
    
    @staticmethod
    def get_strategy_description(strategy_name: str) -> str:
        """获取策略描述
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            策略描述
        """
        descriptions = {
            "value_investing": "价值投资策略，基于市盈率、市净率、ROE等基本面指标",
            "growth_investing": "成长投资策略，基于营收增长率、净利润增长率等成长指标",
            "technical_analysis": "技术分析策略，基于均线、MACD、KDJ等技术指标",
            "momentum": "动量策略，基于价格趋势的延续性",
            "mean_reversion": "均值回归策略，基于价格对均值的回归",
            "swing_trading": "波段交易策略，基于趋势和价格波动"
        }
        
        return descriptions.get(strategy_name, "未知策略")