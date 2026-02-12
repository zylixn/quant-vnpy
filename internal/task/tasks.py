"""
任务类型定义
"""

import abc
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData
from vnpy_ctastrategy.backtesting import BacktestingMode

from internal.utils import get_logger
from internal.fetcher.stock_fetcher import StockFetcher, StockDataManager
from internal.strategies.bull_trend_strategy import BullStrategy
from internal.strategies.stock_strategies import ValueInvestingStrategy, GrowthInvestingStrategy, TechnicalAnalysisStrategy, MomentumStrategy, MeanReversionStrategy
from internal.risk.risk_assessor import RiskManager, AccountRiskAssessor
from internal.trading.simulator.simulator import TradingSimulator
from internal.backtest.backtest_engine import BacktestEngine
import numpy as np
import pandas as pd

# 获取日志器
logger = get_logger('task')


class Task(abc.ABC):
    """任务基类"""
    
    def __init__(self, task_type: str, params: Dict[str, Any]):
        """初始化任务"""
        self.task_id = str(uuid.uuid4())
        self.task_type = task_type
        self.params = params
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0.0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.stop_flag = False
    
    @abc.abstractmethod
    def execute(self):
        """执行任务"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "params": self.params,
            "status": self.status,
            "progress": self.progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "result": self.result,
            "error": self.error
        }


class DataFetchingTask(Task):
    """数据获取任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化数据获取任务"""
        super().__init__("data_fetching", params)
        self.fetcher = StockFetcher()
        self.logger = get_logger('task.data_fetching')
    
    def execute(self):
        """执行数据获取任务"""
        try:
            symbol = self.params.get("symbol")
            start = self.params.get("start")
            end = self.params.get("end")
            interval = self.params.get("interval", Interval.DAILY)
            source = self.params.get("source", "api")
            exchange = self.params.get("exchange", Exchange.SSE)
            
            self.logger.info(f"开始执行数据获取任务: symbol={symbol}, start={start}, end={end}, interval={interval}")
            self.progress = 20.0
            
            # 获取数据
            bars = self.fetcher.get_stock_data(
                symbol=symbol,
                start=start,
                end=end,
                interval=interval,
                source=source,
                exchange=exchange
            )
            
            self.logger.info(f"获取到 {len(bars)} 条数据")
            self.progress = 80.0
            
            # 处理数据
            if self.params.get("calculate_indicators", False):
                from ..fetcher.data_processor import DataProcessor
                processor = DataProcessor()
                indicators = self.params.get("indicators", ["ma", "macd", "rsi"])
                bars = processor.calculate_indicators(bars, indicators)
                self.logger.info(f"计算指标: {indicators}")
            
            self.progress = 100.0
            self.result = {
                "symbol": symbol,
                "data_count": len(bars),
                "data": [bar.__dict__ for bar in bars] if bars else []
            }
            self.logger.info("数据获取任务执行完成")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"数据获取任务执行失败: {str(e)}")
            raise


class StrategyExecutionTask(Task):
    """策略执行任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化策略执行任务"""
        super().__init__("strategy_execution", params)
        self.logger = get_logger('task.strategy_execution')
    
    def execute(self):
        """执行策略执行任务"""
        try:
            strategy_name = self.params.get("strategy_name", "bull")
            symbol = self.params.get("symbol")
            bars = self.params.get("bars", [])
            
            self.logger.info(f"开始执行策略执行任务: strategy_name={strategy_name}, symbol={symbol}, bars_count={len(bars)}")
            self.progress = 20.0
            
            # 根据策略名称选择策略
            if strategy_name == "bull":
                strategy_class = BullStrategy
            else:
                # 可以添加其他策略
                strategy_class = BullStrategy
            
            self.logger.info(f"选择策略: {strategy_class.__name__}")
            self.progress = 50.0
            
            # 这里简化处理，实际应该在回测或实盘环境中执行
            # 这里只是模拟策略执行
            signals = []
            for i, bar in enumerate(bars):
                if i > 0:
                    # 简单的买入信号：价格上涨
                    if bar.close_price > bars[i-1].close_price:
                        signals.append({
                            "datetime": bar.datetime,
                            "signal": "buy",
                            "price": bar.close_price
                        })
            
            self.progress = 100.0
            self.result = {
                "strategy_name": strategy_name,
                "symbol": symbol,
                "signal_count": len(signals),
                "signals": signals
            }
            self.logger.info(f"策略执行任务执行完成，生成了 {len(signals)} 个信号")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"策略执行任务执行失败: {str(e)}")
            raise


class RiskAssessmentTask(Task):
    """风险评估任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化风险评估任务"""
        super().__init__("risk_assessment", params)
        self.logger = get_logger('task.risk_assessment')
    
    def execute(self):
        """执行风险评估任务"""
        try:
            trades = self.params.get("trades", [])
            equity_curve = self.params.get("equity_curve", [100000.0])
            account_balance = self.params.get("account_balance", 100000.0)
            
            self.logger.info(f"开始执行风险评估任务: trades_count={len(trades)}, equity_curve_length={len(equity_curve)}")
            self.progress = 30.0
            
            # 创建账户风险评估器
            account_risk = AccountRiskAssessor(initial_balance=equity_curve[0])
            
            # 更新账户余额
            for balance in equity_curve[1:]:
                account_risk.update_balance(balance)
            
            # 添加交易记录
            for trade in trades:
                account_risk.add_trade(trade)
            
            self.progress = 60.0
            
            # 创建风险管理器
            risk_manager = RiskManager(account_risk)
            
            # 评估账户风险
            account_metrics = account_risk.assess_account_risk()
            
            # 生成风险报告
            risk_report = risk_manager.generate_risk_report()
            
            self.progress = 100.0
            self.result = {
                "account_metrics": account_metrics,
                "risk_report": risk_report
            }
            self.logger.info("风险评估任务执行完成")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"风险评估任务执行失败: {str(e)}")
            raise


class TradingTask(Task):
    """交易任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化交易任务"""
        super().__init__("trading", params)
        initial_balance = params.get("initial_balance", 100000.0)
        self.simulator = TradingSimulator(initial_balance=initial_balance)
        self.logger = get_logger('task.trading')
    
    def execute(self):
        """执行交易任务"""
        try:
            symbol = self.params.get("symbol")
            price = self.params.get("price")
            volume = self.params.get("volume")
            action = self.params.get("action", "buy")
            
            self.logger.info(f"开始执行交易任务: action={action}, symbol={symbol}, price={price}, volume={volume}")
            self.progress = 30.0
            
            # 设置价格
            self.simulator.set_symbol_price(symbol, price)
            
            self.progress = 60.0
            
            # 执行交易
            if action == "buy":
                order_id, error = self.simulator.buy(symbol, price, volume)
            else:
                order_id, error = self.simulator.sell(symbol, price, volume)
            
            self.logger.info(f"交易执行结果: order_id={order_id}, error={error}")
            self.progress = 80.0
            
            # 获取结果
            account_info = self.simulator.get_account_info()
            positions = self.simulator.get_positions()
            trades = self.simulator.get_trades()
            
            self.progress = 100.0
            self.result = {
                "order_id": order_id,
                "error": error,
                "account_info": account_info,
                "positions": positions,
                "trades": trades
            }
            self.logger.info("交易任务执行完成")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"交易任务执行失败: {str(e)}")
            raise


class BacktestTask(Task):
    """回测任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化回测任务"""
        super().__init__("backtest", params)
        self.logger = get_logger('task.backtest')
    
    def execute(self):
        """执行回测任务"""
        try:
            symbol = self.params.get("symbol")
            start = self.params.get("start")
            end = self.params.get("end")
            interval = self.params.get("interval", Interval.DAILY)
            strategy_class = self.params.get("strategy_class", BullStrategy)
            strategy_params = self.params.get("strategy_params", {})
            capital = self.params.get("capital", 1000000)
            
            self.logger.info(f"开始执行回测任务: symbol={symbol}, start={start}, end={end}, strategy={strategy_class.__name__}")
            self.progress = 20.0
            
            # 创建回测引擎
            engine = BacktestEngine()
            
            # 设置回测参数
            engine.set_parameters(
                vt_symbol=f"{symbol}.{Exchange.SSE.value}",
                interval=interval,
                start=start,
                end=end,
                capital=capital
            )
            
            self.progress = 40.0
            
            # 添加策略
            engine.add_strategy(strategy_class, strategy_params)
            self.logger.info(f"添加策略: {strategy_class.__name__}")
            
            self.progress = 60.0
            
            # 获取数据
            fetcher = StockFetcher()
            bars = fetcher.get_stock_data(
                symbol=symbol,
                start=start,
                end=end,
                interval=interval
            )
            self.logger.info(f"获取到 {len(bars)} 条回测数据")
            
            # 加载数据
            engine.load_data(data=bars)
            
            self.progress = 80.0
            
            # 运行回测
            results = engine.run_backtesting()
            self.logger.info("回测运行完成")
            
            # 计算统计指标
            statistics = engine.calculate_statistics()
            self.logger.info("计算统计指标完成")
            
            self.progress = 100.0
            self.result = {
                "symbol": symbol,
                "strategy": strategy_class.__name__,
                "results": results.to_dict() if results is not None else {},
                "statistics": statistics
            }
            self.logger.info("回测任务执行完成")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"回测任务执行失败: {str(e)}")
            raise


class FullWorkflowTask(Task):
    """完整工作流任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化完整工作流任务"""
        super().__init__("full_workflow", params)
        self.logger = get_logger('task.full_workflow')
    
    def execute(self):
        """执行完整工作流任务"""
        try:
            symbol = self.params.get("symbol")
            start = self.params.get("start", datetime.now() - pd.Timedelta(days=365))
            end = self.params.get("end", datetime.now())
            interval = self.params.get("interval", Interval.DAILY)
            strategy_name = self.params.get("strategy_name", "bull")
            initial_balance = self.params.get("initial_balance", 100000.0)
            
            self.logger.info(f"开始执行完整工作流任务: symbol={symbol}, start={start}, end={end}, strategy={strategy_name}")
            workflow_result = {}
            
            # 1. 数据获取
            self.progress = 10.0
            fetcher = StockFetcher()
            bars = fetcher.get_stock_data(
                symbol=symbol,
                start=start,
                end=end,
                interval=interval
            )
            workflow_result["data_fetching"] = {
                "symbol": symbol,
                "data_count": len(bars)
            }
            self.logger.info(f"数据获取完成，获取到 {len(bars)} 条数据")
            
            # 2. 策略执行
            self.progress = 30.0
            signals = []
            for i, bar in enumerate(bars):
                if i > 0:
                    if bar.close_price > bars[i-1].close_price:
                        signals.append({
                            "datetime": bar.datetime,
                            "signal": "buy",
                            "price": bar.close_price
                        })
            workflow_result["strategy_execution"] = {
                "strategy_name": strategy_name,
                "signal_count": len(signals)
            }
            self.logger.info(f"策略执行完成，生成了 {len(signals)} 个信号")
            
            # 3. 回测
            self.progress = 50.0
            engine = BacktestEngine()
            engine.set_parameters(
                vt_symbol=f"{symbol}.{Exchange.SSE.value}",
                interval=interval,
                start=start,
                end=end,
                capital=initial_balance
            )
            engine.add_strategy(BullStrategy, {})
            engine.load_data(data=bars)
            results = engine.run_backtesting()
            statistics = engine.calculate_statistics()
            workflow_result["backtest"] = {
                "statistics": statistics
            }
            self.logger.info("回测完成")
            
            # 4. 风险评估
            self.progress = 70.0
            equity_curve = [initial_balance]
            current_balance = initial_balance
            trades = []
            
            for i, bar in enumerate(bars):
                if i > 0:
                    # 简单模拟交易
                    if bar.close_price > bars[i-1].close_price:
                        # 买入
                        volume = 100
                        cost = bar.close_price * volume
                        if current_balance > cost:
                            current_balance -= cost
                            trades.append({
                                "datetime": bar.datetime,
                                "symbol": symbol,
                                "direction": "buy",
                                "price": bar.close_price,
                                "volume": volume,
                                "pnl": 0
                            })
                    elif bar.close_price < bars[i-1].close_price and trades:
                        # 卖出
                        last_trade = trades[-1]
                        if last_trade["direction"] == "buy":
                            pnl = (bar.close_price - last_trade["price"]) * last_trade["volume"]
                            current_balance += bar.close_price * last_trade["volume"]
                            last_trade["pnl"] = pnl
                equity_curve.append(current_balance)
            
            account_risk = AccountRiskAssessor(initial_balance=initial_balance)
            for balance in equity_curve[1:]:
                account_risk.update_balance(balance)
            for trade in trades:
                account_risk.add_trade(trade)
            
            risk_manager = RiskManager(account_risk)
            risk_report = risk_manager.generate_risk_report()
            workflow_result["risk_assessment"] = {
                "risk_report": risk_report
            }
            self.logger.info("风险评估完成")
            
            # 5. 交易模拟
            self.progress = 90.0
            simulator = TradingSimulator(initial_balance=initial_balance)
            for signal in signals[:5]:  # 只模拟前5个信号
                simulator.set_symbol_price(symbol, signal["price"])
                simulator.buy(symbol, signal["price"], 100)
            
            account_info = simulator.get_account_info()
            positions = simulator.get_positions()
            workflow_result["trading"] = {
                "account_info": account_info,
                "positions": positions
            }
            self.logger.info("交易模拟完成")
            
            self.progress = 100.0
            self.result = workflow_result
            self.logger.info("完整工作流任务执行完成")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"完整工作流任务执行失败: {str(e)}")
            raise


class StockAnalysisTask(Task):
    """股票分析任务"""
    
    def __init__(self, params: Dict[str, Any]):
        """初始化股票分析任务"""
        super().__init__("stock_analysis", params)
        self.fetcher = StockFetcher()
        self.logger = get_logger('task.stock_analysis')
    
    def execute(self):
        """执行股票分析任务"""
        try:
            # 获取参数
            symbols = self.params.get("symbols", ["600000", "600519", "000001", "000858", "601318"])
            lookback_days = self.params.get("lookback_days", 60)
            interval = self.params.get("interval", Interval.DAILY)
            exchange = self.params.get("exchange", Exchange.SSE)
            strategies = self.params.get("strategies", ["value", "growth", "technical", "momentum", "mean_reversion"])
            top_n = self.params.get("top_n", 5)
            
            self.logger.info(f"开始执行股票分析任务: symbols_count={len(symbols)}, lookback_days={lookback_days}, strategies={strategies}")
            self.progress = 5.0
            
            # 计算时间范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            self.progress = 10.0
            
            # 分析结果
            analysis_results = []
            
            # 遍历股票
            total_stocks = len(symbols)
            for i, symbol in enumerate(symbols):
                self.progress = 10.0 + (i / total_stocks) * 70.0
                
                # 获取股票数据
                bars = self.fetcher.get_stock_data(
                    symbol=symbol,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    exchange=exchange
                )
                
                if not bars:
                    self.logger.warning(f"未获取到股票 {symbol} 的数据")
                    continue
                
                # 分析股票
                stock_result = self._analyze_stock(symbol, bars, strategies)
                if stock_result:
                    analysis_results.append(stock_result)
                    self.logger.info(f"分析完成股票 {symbol}，得分: {stock_result['score']:.4f}")
            
            self.progress = 80.0
            
            # 排序并选择前N只股票
            analysis_results.sort(key=lambda x: x["score"], reverse=True)
            top_stocks = analysis_results[:top_n]
            
            # 生成分析报告
            report = self._generate_report(top_stocks, analysis_results)
            
            self.progress = 100.0
            self.result = {
                "top_stocks": top_stocks,
                "analysis_results": analysis_results,
                "report": report,
                "total_stocks_analyzed": len(analysis_results),
                "top_n": top_n,
                "lookback_days": lookback_days,
                "date": end_date.isoformat()
            }
            self.logger.info(f"股票分析任务执行完成，分析了 {len(analysis_results)} 只股票，选出了 {len(top_stocks)} 只 top 股票")
        except Exception as e:
            self.error = str(e)
            self.logger.error(f"股票分析任务执行失败: {str(e)}")
            raise
    
    def _analyze_stock(self, symbol: str, bars: List[BarData], strategies: List[str]) -> Dict[str, Any]:
        """分析单个股票
        
        Args:
            symbol: 股票代码
            bars: K线数据
            strategies: 策略列表
            
        Returns:
            分析结果
        """
        result = {
            "symbol": symbol,
            "score": 0.0,
            "strategies": {},
            "price": bars[-1].close_price if bars else 0.0,
            "volume": bars[-1].volume if bars else 0,
            "date": bars[-1].datetime.isoformat() if bars else None
        }
        
        # 计算基本指标
        if len(bars) >= 20:
            close_prices = [bar.close_price for bar in bars]
            volumes = [bar.volume for bar in bars]
            
            # 计算收益率
            returns = np.diff(close_prices) / close_prices[:-1]
            result["return_1d"] = returns[-1] if returns.size > 0 else 0.0
            result["return_7d"] = np.mean(returns[-7:]) if returns.size >= 7 else 0.0
            result["return_30d"] = np.mean(returns[-30:]) if returns.size >= 30 else 0.0
            
            # 计算波动率
            result["volatility"] = np.std(returns) if returns.size > 0 else 0.0
            
            # 计算成交量
            result["avg_volume_30d"] = np.mean(volumes[-30:]) if len(volumes) >= 30 else 0.0
        
        # 应用策略
        if "value" in strategies:
            value_score = self._apply_value_strategy(bars)
            result["strategies"]["value"] = value_score
            result["score"] += value_score
        
        if "growth" in strategies:
            growth_score = self._apply_growth_strategy(bars)
            result["strategies"]["growth"] = growth_score
            result["score"] += growth_score
        
        if "technical" in strategies:
            technical_score = self._apply_technical_strategy(bars)
            result["strategies"]["technical"] = technical_score
            result["score"] += technical_score
        
        if "momentum" in strategies:
            momentum_score = self._apply_momentum_strategy(bars)
            result["strategies"]["momentum"] = momentum_score
            result["score"] += momentum_score
        
        if "mean_reversion" in strategies:
            mean_reversion_score = self._apply_mean_reversion_strategy(bars)
            result["strategies"]["mean_reversion"] = mean_reversion_score
            result["score"] += mean_reversion_score
        
        return result
    
    def _apply_value_strategy(self, bars: List[BarData]) -> float:
        """应用价值投资策略
        
        Args:
            bars: K线数据
            
        Returns:
            策略得分
        """
        # 简单的价值投资指标：市盈率（模拟）、市净率（模拟）
        # 实际应用中应该从数据源获取真实的基本面数据
        if len(bars) < 20:
            return 0.0
        
        # 模拟基本面数据
        pe = np.random.uniform(5, 30)
        pb = np.random.uniform(0.5, 5)
        roe = np.random.uniform(0.05, 0.2)
        
        # 计算价值得分
        score = 0.0
        if pe < 15:
            score += 2.0
        elif pe < 20:
            score += 1.0
        
        if pb < 1.5:
            score += 2.0
        elif pb < 2.0:
            score += 1.0
        
        if roe > 0.1:
            score += 2.0
        elif roe > 0.08:
            score += 1.0
        
        return score
    
    def _apply_growth_strategy(self, bars: List[BarData]) -> float:
        """应用成长投资策略
        
        Args:
            bars: K线数据
            
        Returns:
            策略得分
        """
        if len(bars) < 30:
            return 0.0
        
        # 计算增长率
        close_prices = [bar.close_price for bar in bars]
        returns = np.diff(close_prices) / close_prices[:-1]
        
        # 计算30天和60天增长率
        growth_30d = np.mean(returns[-30:]) if returns.size >= 30 else 0.0
        growth_60d = np.mean(returns[-60:]) if returns.size >= 60 else 0.0
        
        # 计算成长得分
        score = 0.0
        if growth_30d > 0.02:
            score += 2.0
        elif growth_30d > 0.01:
            score += 1.0
        
        if growth_60d > 0.04:
            score += 2.0
        elif growth_60d > 0.02:
            score += 1.0
        
        return score
    
    def _apply_technical_strategy(self, bars: List[BarData]) -> float:
        """应用技术分析策略
        
        Args:
            bars: K线数据
            
        Returns:
            策略得分
        """
        if len(bars) < 60:
            return 0.0
        
        # 计算技术指标
        close_prices = [bar.close_price for bar in bars]
        volumes = [bar.volume for bar in bars]
        
        # 计算均线
        ma20 = np.mean(close_prices[-20:])
        ma60 = np.mean(close_prices[-60:])
        
        # 计算MACD
        exp1 = self._ema(close_prices, 12)
        exp2 = self._ema(close_prices, 26)
        macd = exp1 - exp2
        signal = self._ema(macd, 9)
        macd_hist = macd - signal
        
        # 计算RSI
        rsi = self._calculate_rsi(close_prices, 14)
        
        # 计算技术得分
        score = 0.0
        
        # 均线多头排列
        if ma20 > ma60:
            score += 2.0
        
        # MACD金叉
        if macd_hist[-1] > 0 and macd_hist[-2] <= 0:
            score += 2.0
        elif macd_hist[-1] > 0:
            score += 1.0
        
        # RSI正常范围
        if 30 < rsi < 70:
            score += 1.0
        elif rsi < 30:
            score += 2.0  # 超卖
        
        return score
    
    def _apply_momentum_strategy(self, bars: List[BarData]) -> float:
        """应用动量策略
        
        Args:
            bars: K线数据
            
        Returns:
            策略得分
        """
        if len(bars) < 20:
            return 0.0
        
        # 计算动量
        close_prices = [bar.close_price for bar in bars]
        returns = np.diff(close_prices) / close_prices[:-1]
        
        # 计算20天动量
        momentum = np.mean(returns[-20:]) if returns.size >= 20 else 0.0
        
        # 计算动量得分
        score = 0.0
        if momentum > 0.01:
            score += 2.0
        elif momentum > 0.005:
            score += 1.0
        
        return score
    
    def _apply_mean_reversion_strategy(self, bars: List[BarData]) -> float:
        """应用均值回归策略
        
        Args:
            bars: K线数据
            
        Returns:
            策略得分
        """
        if len(bars) < 20:
            return 0.0
        
        # 计算Z-score
        close_prices = [bar.close_price for bar in bars]
        mean = np.mean(close_prices[-20:])
        std = np.std(close_prices[-20:])
        
        if std == 0:
            return 0.0
        
        z_score = (close_prices[-1] - mean) / std
        
        # 计算均值回归得分
        score = 0.0
        if z_score < -2.0:
            score += 2.0  # 严重低估
        elif z_score < -1.0:
            score += 1.0  # 低估
        
        return score
    
    def _ema(self, prices: List[float], period: int) -> List[float]:
        """计算指数移动平均线
        
        Args:
            prices: 价格列表
            period: 周期
            
        Returns:
            EMA列表
        """
        ema = []
        multiplier = 2 / (period + 1)
        
        # 初始EMA为第一个价格
        ema_value = prices[0]
        ema.append(ema_value)
        
        # 计算后续EMA
        for price in prices[1:]:
            ema_value = (price - ema_value) * multiplier + ema_value
            ema.append(ema_value)
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """计算RSI
        
        Args:
            prices: 价格列表
            period: 周期
            
        Returns:
            RSI值
        """
        if len(prices) < period + 1:
            return 50.0
        
        # 计算价格变化
        changes = np.diff(prices)
        
        # 分离涨跌
        gains = []
        losses = []
        
        for change in changes:
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # 计算平均涨跌
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        # 计算RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _generate_report(self, top_stocks: List[Dict[str, Any]], analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成分析报告
        
        Args:
            top_stocks: 前N只股票
            analysis_results: 所有分析结果
            
        Returns:
            分析报告
        """
        # 计算统计信息
        total_score = sum([result["score"] for result in analysis_results])
        avg_score = total_score / len(analysis_results) if analysis_results else 0.0
        
        # 计算各策略平均得分
        strategy_scores = {}
        for strategy in ["value", "growth", "technical", "momentum", "mean_reversion"]:
            scores = [result["strategies"].get(strategy, 0.0) for result in analysis_results]
            avg_strategy_score = sum(scores) / len(scores) if scores else 0.0
            strategy_scores[strategy] = avg_strategy_score
        
        # 生成报告
        report = {
            "summary": {
                "total_stocks_analyzed": len(analysis_results),
                "average_score": avg_score,
                "top_stock_count": len(top_stocks)
            },
            "strategy_performance": strategy_scores,
            "top_stocks_details": [
                {
                    "symbol": stock["symbol"],
                    "score": stock["score"],
                    "price": stock["price"],
                    "strategies": stock["strategies"],
                    "return_1d": stock.get("return_1d", 0.0),
                    "return_7d": stock.get("return_7d", 0.0),
                    "return_30d": stock.get("return_30d", 0.0)
                }
                for stock in top_stocks
            ],
            "recommendation": "\n".join([
                f"1. {stock['symbol']}: 综合得分 {stock['score']:.2f}, 当前价格 {stock['price']:.2f}"
                for stock in top_stocks
            ])
        }
        
        return report

