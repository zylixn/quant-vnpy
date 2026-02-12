"""
基于vnpy的风险评估核心功能
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any


class RiskMetrics:
    """风险指标计算"""
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """计算最大回撤"""
        if not equity_curve:
            return 0.0
        
        equity = np.array(equity_curve)
        peak = equity[0]
        max_drawdown = 0.0
        
        for value in equity[1:]:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """计算夏普比率"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        if len(returns_array) < 2:
            return 0.0
        
        avg_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
        
        sharpe = (avg_return - risk_free_rate) / std_return
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """计算索提诺比率"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        if len(returns_array) < 2:
            return 0.0
        
        avg_return = np.mean(returns_array)
        negative_returns = returns_array[returns_array < 0]
        
        if len(negative_returns) == 0:
            return 0.0
        
        downside_std = np.std(negative_returns)
        
        if downside_std == 0:
            return 0.0
        
        sortino = (avg_return - risk_free_rate) / downside_std
        return sortino
    
    @staticmethod
    def calculate_win_rate(trades: List[Dict]) -> float:
        """计算胜率"""
        if not trades:
            return 0.0
        
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        return len(winning_trades) / len(trades)
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """计算盈利因子"""
        if not trades:
            return 0.0
        
        gross_profit = sum(max(0, t.get('pnl', 0)) for t in trades)
        gross_loss = sum(abs(min(0, t.get('pnl', 0))) for t in trades)
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss


class AccountRiskAssessor:
    """账户风险评估"""
    
    def __init__(self, initial_balance: float = 100000.0):
        self.initial_balance = initial_balance
        self.equity_curve = [initial_balance]
        self.trades = []
        self.current_balance = initial_balance
        self.positions = {}
    
    def update_balance(self, balance: float):
        """更新账户余额"""
        self.current_balance = balance
        self.equity_curve.append(balance)
    
    def add_trade(self, trade: Dict):
        """添加交易记录"""
        self.trades.append(trade)
    
    def update_position(self, symbol: str, volume: int, avg_price: float):
        """更新持仓"""
        self.positions[symbol] = {
            'volume': volume,
            'avg_price': avg_price
        }
    
    def assess_account_risk(self) -> Dict[str, float]:
        """评估账户风险"""
        metrics = {
            'current_balance': self.current_balance,  # 当前账户余额
            'total_return': (self.current_balance - self.initial_balance) / self.initial_balance,  # 总收益率
            'max_drawdown': RiskMetrics.calculate_max_drawdown(self.equity_curve),  # 最大回撤
            'sharpe_ratio': self._calculate_sharpe_ratio(),  # 夏普比率
            'sortino_ratio': self._calculate_sortino_ratio(),  # 索提诺比率
            'win_rate': RiskMetrics.calculate_win_rate(self.trades),  # 胜率
            'profit_factor': RiskMetrics.calculate_profit_factor(self.trades),  # 盈利因子
            'total_trades': len(self.trades),  # 总交易次数
            'open_positions': len([p for p in self.positions.values() if p['volume'] > 0])  # 未平仓头寸数量
        }
        return metrics
    
    def _calculate_sharpe_ratio(self) -> float:
        """计算夏普比率"""
        if len(self.equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(self.equity_curve)):
            return_rate = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(return_rate)
        
        return RiskMetrics.calculate_sharpe_ratio(returns)
    
    def _calculate_sortino_ratio(self) -> float:
        """计算索提诺比率"""
        if len(self.equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(self.equity_curve)):
            return_rate = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(return_rate)
        
        return RiskMetrics.calculate_sortino_ratio(returns)


class StrategyRiskAssessor:
    """策略风险评估"""
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.trades = []
        self.params = {}
        self.indicators = {}
    
    def add_trade(self, trade: Dict):
        """添加交易记录"""
        self.trades.append(trade)
    
    def set_strategy_params(self, params: Dict):
        """设置策略参数"""
        self.params = params
    
    def set_indicators(self, indicators: Dict):
        """设置指标值"""
        self.indicators = indicators
    
    def assess_strategy_risk(self) -> Dict[str, Any]:
        """评估策略风险"""
        if not self.trades:
            return {
                'strategy_name': self.strategy_name,  # 策略名称
                'total_trades': 0,  # 总交易次数
                'win_rate': 0.0,  # 胜率
                'profit_factor': 0.0,  # 盈利因子
                'avg_trade_pnl': 0.0,  # 平均每笔交易盈亏
                'max_win': 0.0,  # 最大盈利
                'max_loss': 0.0  # 最大亏损
            }
        
        win_rate = RiskMetrics.calculate_win_rate(self.trades)
        profit_factor = RiskMetrics.calculate_profit_factor(self.trades)
        
        pnls = [t.get('pnl', 0) for t in self.trades]
        avg_trade_pnl = np.mean(pnls) if pnls else 0.0
        max_win = max(pnls) if pnls else 0.0
        max_loss = min(pnls) if pnls else 0.0
        
        metrics = {
            'strategy_name': self.strategy_name,  # 策略名称
            'total_trades': len(self.trades),  # 总交易次数
            'win_rate': win_rate,  # 胜率
            'profit_factor': profit_factor,  # 盈利因子
            'avg_trade_pnl': avg_trade_pnl,  # 平均每笔交易盈亏
            'max_win': max_win,  # 最大盈利
            'max_loss': max_loss,  # 最大亏损
            'strategy_params': self.params,  # 策略参数
            'current_indicators': self.indicators  # 当前指标值
        }
        return metrics


class MarketRiskAssessor:
    """市场风险评估"""
    
    @staticmethod
    def assess_market_volatility(prices: List[float]) -> Dict[str, float]:
        """评估市场波动率"""
        if len(prices) < 2:
            return {
                'volatility': 0.0,
                'avg_price': 0.0,
                'price_change': 0.0
            }
        
        prices_array = np.array(prices)
        returns = []
        
        for i in range(1, len(prices_array)):
            return_rate = (prices_array[i] - prices_array[i-1]) / prices_array[i-1]
            returns.append(return_rate)
        
        volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
        avg_price = np.mean(prices_array)
        price_change = (prices_array[-1] - prices_array[0]) / prices_array[0]
        
        return {
            'volatility': volatility,
            'avg_price': avg_price,
            'price_change': price_change,
            'price_volatility': np.std(prices_array)
        }
    
    @staticmethod
    def assess_trend_strength(prices: List[float]) -> Dict[str, float]:
        """评估趋势强度"""
        if len(prices) < 3:
            return {
                'trend_strength': 0.0,
                'trend_direction': 0.0
            }
        
        prices_array = np.array(prices)
        x = np.arange(len(prices_array))
        
        # 线性回归斜率
        slope = np.polyfit(x, prices_array, 1)[0]
        
        # 归一化趋势强度
        price_range = max(prices_array) - min(prices_array)
        if price_range == 0:
            return {
                'trend_strength': 0.0,
                'trend_direction': 0.0
            }
        
        trend_strength = abs(slope) / price_range * len(prices_array)
        trend_direction = 1.0 if slope > 0 else -1.0 if slope < 0 else 0.0
        
        return {
            'trend_strength': min(trend_strength, 1.0),
            'trend_direction': trend_direction
        }


class RiskManager:
    """风险管理"""
    
    def __init__(self, account_risk: AccountRiskAssessor):
        self.account_risk = account_risk
        self.risk_limits = {
            'max_position_size': 0.3,  # 最大持仓比例
            'max_drawdown': 0.2,       # 最大回撤限制
            'max_leverage': 3.0,        # 最大杠杆
            'single_trade_risk': 0.02   # 单笔交易风险
        }
    
    def set_risk_limits(self, limits: Dict[str, float]):
        """设置风险限制"""
        self.risk_limits.update(limits)
    
    def assess_risk_exposure(self, position_value: float, total_equity: float) -> Dict[str, bool]:
        """评估风险敞口"""
        exposure = position_value / total_equity
        drawdown = self.account_risk.assess_account_risk()['max_drawdown']
        
        warnings = {
            'position_limit_exceeded': exposure > self.risk_limits['max_position_size'],
            'drawdown_limit_exceeded': drawdown > self.risk_limits['max_drawdown'],
            'high_risk': exposure > self.risk_limits['max_position_size'] * 0.8 or 
                        drawdown > self.risk_limits['max_drawdown'] * 0.8
        }
        
        return warnings
    
    def calculate_position_size(self, account_balance: float, atr: float, risk_per_trade: float = None) -> int:
        """计算合理持仓大小"""
        if risk_per_trade is None:
            risk_per_trade = self.risk_limits['single_trade_risk']
        
        if atr <= 0:
            return 0
        
        risk_amount = account_balance * risk_per_trade
        position_size = risk_amount / atr
        
        return int(position_size)
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """生成风险报告"""
        account_metrics = self.account_risk.assess_account_risk()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'account_metrics': account_metrics,
            'risk_limits': self.risk_limits,
            'risk_assessment': self._assess_overall_risk(account_metrics)
        }
        
        return report
    
    def _assess_overall_risk(self, account_metrics: Dict[str, float]) -> str:
        """评估整体风险"""
        if account_metrics['max_drawdown'] > self.risk_limits['max_drawdown']:
            return '高风险 - 最大回撤超出限制'
        elif account_metrics['sharpe_ratio'] < 0.5:
            return '中风险 - 夏普比率较低'
        elif account_metrics['win_rate'] < 0.4:
            return '中风险 - 胜率较低'
        else:
            return '低风险 - 各项指标正常'
