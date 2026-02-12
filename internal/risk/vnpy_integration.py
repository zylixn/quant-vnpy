"""
与vnpy和现有交易系统的集成
"""

from typing import Optional, Dict, Any
from vnpy_ctastrategy import CtaTemplate
from vnpy.trader.object import TickData, BarData, OrderData, TradeData, StopOrder
from vnpy.trader.constant import Direction, Offset
from internal.risk.risk_assessor import AccountRiskAssessor, StrategyRiskAssessor, RiskManager


class RiskControlStrategy(CtaTemplate):
    """带风险控制的策略基类"""
    
    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        
        # 风险评估实例
        self.risk_manager = RiskManager(AccountRiskAssessor())
        self.strategy_assessor = StrategyRiskAssessor(strategy_name)
        
        # 风险控制参数
        self.max_position = 10  # 最大持仓
        self.max_drawdown = 0.2  # 最大回撤
        self.risk_per_trade = 0.01  # 单笔交易风险
        
        # 策略参数
        self.update_strategy_params(setting)
    
    def update_strategy_params(self, params: Dict[str, Any]):
        """更新策略参数"""
        self.strategy_assessor.set_strategy_params(params)
        
        # 风险控制参数
        if 'max_position' in params:
            self.max_position = params['max_position']
        if 'max_drawdown' in params:
            self.max_drawdown = params['max_drawdown']
        if 'risk_per_trade' in params:
            self.risk_per_trade = params['risk_per_trade']
    
    def on_tick(self, tick: TickData):
        """处理行情tick"""
        # 可以在这里添加实时风险监控
        pass
    
    def on_bar(self, bar: BarData):
        """处理K线"""
        # 可以在这里添加基于K线的风险监控
        pass
    
    def on_trade(self, trade: TradeData):
        """处理成交"""
        # 转换成交数据格式
        trade_dict = {
            'symbol': trade.symbol,
            'direction': 'buy' if trade.direction == Direction.LONG else 'sell',
            'price': trade.price,
            'volume': trade.volume,
            'pnl': trade.pnl,
            'commission': trade.commission,
            'trade_time': trade.trade_time.isoformat() if trade.trade_time else None
        }
        
        # 更新风险评估数据
        self.risk_manager.account_risk.add_trade(trade_dict)
        self.strategy_assessor.add_trade(trade_dict)
        
        # 检查风险
        self.check_risk()
    
    def on_order(self, order: OrderData):
        """处理订单"""
        pass
    
    def on_stop_order(self, stop_order: StopOrder):
        """处理停止单"""
        pass
    
    def buy(self, price: float, volume: int, stop: bool = False, lock: bool = False) -> Optional[str]:
        """买入"""
        # 风险控制检查
        if not self.check_risk_before_trade(volume):
            self.write_log(f"风险控制：买入被拒绝，当前持仓 {self.pos}")
            return None
        
        return super().buy(price, volume, stop, lock)
    
    def sell(self, price: float, volume: int, stop: bool = False, lock: bool = False) -> Optional[str]:
        """卖出"""
        return super().sell(price, volume, stop, lock)
    
    def short(self, price: float, volume: int, stop: bool = False, lock: bool = False) -> Optional[str]:
        """做空"""
        # 风险控制检查
        if not self.check_risk_before_trade(volume):
            self.write_log(f"风险控制：做空被拒绝，当前持仓 {self.pos}")
            return None
        
        return super().short(price, volume, stop, lock)
    
    def cover(self, price: float, volume: int, stop: bool = False, lock: bool = False) -> Optional[str]:
        """平空"""
        return super().cover(price, volume, stop, lock)
    
    def check_risk_before_trade(self, volume: int) -> bool:
        """交易前风险检查"""
        # 检查持仓限制
        if abs(self.pos + volume) > self.max_position:
            self.write_log(f"风险控制：持仓超过限制，当前 {self.pos}，计划增加 {volume}")
            return False
        
        # 检查账户风险
        account_metrics = self.risk_manager.account_risk.assess_account_risk()
        if account_metrics['max_drawdown'] > self.max_drawdown:
            self.write_log(f"风险控制：回撤超过限制，当前回撤 {account_metrics['max_drawdown']}")
            return False
        
        return True
    
    def check_risk(self):
        """检查风险"""
        # 生成风险报告
        report = self.risk_manager.generate_risk_report()
        
        # 检查风险指标
        account_metrics = report['account_metrics']
        risk_assessment = report['risk_assessment']
        
        # 记录风险状态
        self.write_log(f"风险评估：{risk_assessment}")
        self.write_log(f"最大回撤：{account_metrics['max_drawdown']:.2%}")
        self.write_log(f"夏普比率：{account_metrics['sharpe_ratio']:.2f}")
        self.write_log(f"胜率：{account_metrics['win_rate']:.2%}")
        
        # 风险过高时的处理
        if risk_assessment == '高风险 - 最大回撤超出限制':
            self.write_log("⚠️ 风险过高，建议减少仓位或暂停交易")
            # 可以在这里添加自动减仓或暂停交易的逻辑
    
    def calculate_position_size(self, atr: float) -> int:
        """计算合理持仓大小"""
        account_balance = self.cta_engine.capital if hasattr(self.cta_engine, 'capital') else 100000
        return self.risk_manager.calculate_position_size(account_balance, atr, self.risk_per_trade)
    
    def get_risk_report(self) -> Dict[str, Any]:
        """获取风险报告"""
        report = self.risk_manager.generate_risk_report()
        strategy_report = self.strategy_assessor.assess_strategy_risk()
        
        return {
            'account_report': report,
            'strategy_report': strategy_report
        }


class RiskMonitor:
    """风险监控器"""
    
    def __init__(self):
        self.risk_manager = RiskManager(AccountRiskAssessor())
        self.strategy_assessors = {}
    
    def register_strategy(self, strategy_name: str):
        """注册策略"""
        if strategy_name not in self.strategy_assessors:
            self.strategy_assessors[strategy_name] = StrategyRiskAssessor(strategy_name)
        return self.strategy_assessors[strategy_name]
    
    def update_trade(self, trade: TradeData, strategy_name: str = None):
        """更新交易数据"""
        trade_dict = {
            'symbol': trade.symbol,
            'direction': 'buy' if trade.direction == Direction.LONG else 'sell',
            'price': trade.price,
            'volume': trade.volume,
            'pnl': trade.pnl,
            'commission': trade.commission,
            'trade_time': trade.trade_time.isoformat() if trade.trade_time else None
        }
        
        # 更新账户风险评估
        self.risk_manager.account_risk.add_trade(trade_dict)
        
        # 更新策略风险评估
        if strategy_name and strategy_name in self.strategy_assessors:
            self.strategy_assessors[strategy_name].add_trade(trade_dict)
    
    def update_balance(self, balance: float):
        """更新账户余额"""
        self.risk_manager.account_risk.update_balance(balance)
    
    def update_position(self, symbol: str, volume: int, avg_price: float):
        """更新持仓"""
        self.risk_manager.account_risk.update_position(symbol, volume, avg_price)
    
    def generate_combined_report(self) -> Dict[str, Any]:
        """生成综合风险报告"""
        account_report = self.risk_manager.generate_risk_report()
        
        strategy_reports = {}
        for strategy_name, assessor in self.strategy_assessors.items():
            strategy_reports[strategy_name] = assessor.assess_strategy_risk()
        
        return {
            'timestamp': account_report['timestamp'],
            'account_report': account_report,
            'strategy_reports': strategy_reports,
            'overall_risk': self._assess_overall_risk(account_report, strategy_reports)
        }
    
    def _assess_overall_risk(self, account_report: Dict[str, Any], strategy_reports: Dict[str, Dict[str, Any]]) -> str:
        """评估整体风险"""
        account_risk = account_report['risk_assessment']
        
        if '高风险' in account_risk:
            return '整体高风险'
        
        # 检查策略风险
        high_risk_strategies = []
        for strategy_name, report in strategy_reports.items():
            if report.get('profit_factor', 0) < 1:
                high_risk_strategies.append(strategy_name)
        
        if high_risk_strategies:
            return f'部分策略高风险: {high_risk_strategies}'
        
        return '整体风险适中'


# 全局风险监控器实例
global_risk_monitor = RiskMonitor()


def get_risk_monitor() -> RiskMonitor:
    """获取全局风险监控器"""
    return global_risk_monitor
