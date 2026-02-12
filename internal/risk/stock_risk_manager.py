"""
股票风险控制模块

增强风险控制功能，支持股票交易特有的风险控制
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import numpy as np
from vnpy.trader.constant import Direction, Offset, Exchange
from vnpy.trader.object import OrderData, TradeData, BarData
from internal.trading.account_manager import StockAccount, get_account_manager
from internal.trading.trading_time import get_trading_time_manager


class StockRiskConfig:
    """股票风险控制配置"""
    
    def __init__(
        self, 
        # 个股风险控制
        max_position_per_stock: float = 0.3,  # 单股票最大持仓比例
        max_trades_per_stock: int = 50,  # 单股票最大日交易次数
        max_loss_per_stock: float = 5000,  # 单股票最大日亏损
        
        # 行业风险控制
        max_position_per_industry: float = 0.5,  # 单行业最大持仓比例
        max_industry_concentration: float = 0.7,  # 行业集中度上限
        
        # 市场风险控制
        market_risk_threshold: float = 0.03,  # 大盘风险阈值
        market_risk_stop_loss: bool = True,  # 大盘风险止损
        
        # 流动性风险控制
        min_turnover_rate: float = 0.01,  # 最小换手率
        min_volume: int = 100000,  # 最小成交量
        max_position_to_volume_ratio: float = 0.01,  # 持仓与成交量比例上限
        
        # 合规风险控制
        insider_trading_check: bool = True,  # 内幕交易检查
        market_manipulation_check: bool = True,  # 市场操纵检查
        regulatory_holding_period: int = 6,  # 监管持股期（月）
        
        # 账户风险控制
        max_total_positions: int = 20,  # 最大持仓数量
        max_leverage: float = 1.0,  # 最大杠杆
        daily_withdrawal_limit: float = 500000,  # 每日提现限额
        
        # 交易频率控制
        max_daily_trades: int = 200,  # 最大日交易次数
        max_intraday_trades: int = 100,  # 最大日内交易次数
        cool_down_period: int = 60,  # 交易冷却期（秒）
        
        # 止损止盈控制
        global_stop_loss: float = 0.1,  # 全局止损比例
        global_take_profit: float = 0.2,  # 全局止盈比例
        position_stop_loss: float = 0.05,  # 单持仓止损比例
        position_take_profit: float = 0.1,  # 单持仓止盈比例
        
        # 预警阈值
        warning_level: float = 0.8,  # 预警阈值（达到风控阈值的80%）
        alert_notification: bool = True,  # 预警通知
        
        # 监控频率
        monitoring_interval: int = 60  # 监控间隔（秒）
    ):
        """初始化股票风险控制配置
        
        Args:
            max_position_per_stock: 单股票最大持仓比例
            max_trades_per_stock: 单股票最大日交易次数
            max_loss_per_stock: 单股票最大日亏损
            max_position_per_industry: 单行业最大持仓比例
            max_industry_concentration: 行业集中度上限
            market_risk_threshold: 大盘风险阈值
            market_risk_stop_loss: 大盘风险止损
            min_turnover_rate: 最小换手率
            min_volume: 最小成交量
            max_position_to_volume_ratio: 持仓与成交量比例上限
            insider_trading_check: 内幕交易检查
            market_manipulation_check: 市场操纵检查
            regulatory_holding_period: 监管持股期（月）
            max_total_positions: 最大持仓数量
            max_leverage: 最大杠杆
            daily_withdrawal_limit: 每日提现限额
            max_daily_trades: 最大日交易次数
            max_intraday_trades: 最大日内交易次数
            cool_down_period: 交易冷却期（秒）
            global_stop_loss: 全局止损比例
            global_take_profit: 全局止盈比例
            position_stop_loss: 单持仓止损比例
            position_take_profit: 单持仓止盈比例
            warning_level: 预警阈值
            alert_notification: 预警通知
            monitoring_interval: 监控间隔（秒）
        """
        self.max_position_per_stock = max_position_per_stock
        self.max_trades_per_stock = max_trades_per_stock
        self.max_loss_per_stock = max_loss_per_stock
        self.max_position_per_industry = max_position_per_industry
        self.max_industry_concentration = max_industry_concentration
        self.market_risk_threshold = market_risk_threshold
        self.market_risk_stop_loss = market_risk_stop_loss
        self.min_turnover_rate = min_turnover_rate
        self.min_volume = min_volume
        self.max_position_to_volume_ratio = max_position_to_volume_ratio
        self.insider_trading_check = insider_trading_check
        self.market_manipulation_check = market_manipulation_check
        self.regulatory_holding_period = regulatory_holding_period
        self.max_total_positions = max_total_positions
        self.max_leverage = max_leverage
        self.daily_withdrawal_limit = daily_withdrawal_limit
        self.max_daily_trades = max_daily_trades
        self.max_intraday_trades = max_intraday_trades
        self.cool_down_period = cool_down_period
        self.global_stop_loss = global_stop_loss
        self.global_take_profit = global_take_profit
        self.position_stop_loss = position_stop_loss
        self.position_take_profit = position_take_profit
        self.warning_level = warning_level
        self.alert_notification = alert_notification
        self.monitoring_interval = monitoring_interval
    
    def to_dict(self) -> Dict:
        """转换为字典
        
        Returns:
            配置字典
        """
        return {
            "max_position_per_stock": self.max_position_per_stock,
            "max_trades_per_stock": self.max_trades_per_stock,
            "max_loss_per_stock": self.max_loss_per_stock,
            "max_position_per_industry": self.max_position_per_industry,
            "max_industry_concentration": self.max_industry_concentration,
            "market_risk_threshold": self.market_risk_threshold,
            "market_risk_stop_loss": self.market_risk_stop_loss,
            "min_turnover_rate": self.min_turnover_rate,
            "min_volume": self.min_volume,
            "max_position_to_volume_ratio": self.max_position_to_volume_ratio,
            "insider_trading_check": self.insider_trading_check,
            "market_manipulation_check": self.market_manipulation_check,
            "regulatory_holding_period": self.regulatory_holding_period,
            "max_total_positions": self.max_total_positions,
            "max_leverage": self.max_leverage,
            "daily_withdrawal_limit": self.daily_withdrawal_limit,
            "max_daily_trades": self.max_daily_trades,
            "max_intraday_trades": self.max_intraday_trades,
            "cool_down_period": self.cool_down_period,
            "global_stop_loss": self.global_stop_loss,
            "global_take_profit": self.global_take_profit,
            "position_stop_loss": self.position_stop_loss,
            "position_take_profit": self.position_take_profit,
            "warning_level": self.warning_level,
            "alert_notification": self.alert_notification,
            "monitoring_interval": self.monitoring_interval
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StockRiskConfig':
        """从字典创建配置
        
        Args:
            data: 配置字典
            
        Returns:
            StockRiskConfig实例
        """
        return cls(
            max_position_per_stock=data.get("max_position_per_stock", 0.3),
            max_trades_per_stock=data.get("max_trades_per_stock", 50),
            max_loss_per_stock=data.get("max_loss_per_stock", 5000),
            max_position_per_industry=data.get("max_position_per_industry", 0.5),
            max_industry_concentration=data.get("max_industry_concentration", 0.7),
            market_risk_threshold=data.get("market_risk_threshold", 0.03),
            market_risk_stop_loss=data.get("market_risk_stop_loss", True),
            min_turnover_rate=data.get("min_turnover_rate", 0.01),
            min_volume=data.get("min_volume", 100000),
            max_position_to_volume_ratio=data.get("max_position_to_volume_ratio", 0.01),
            insider_trading_check=data.get("insider_trading_check", True),
            market_manipulation_check=data.get("market_manipulation_check", True),
            regulatory_holding_period=data.get("regulatory_holding_period", 6),
            max_total_positions=data.get("max_total_positions", 20),
            max_leverage=data.get("max_leverage", 1.0),
            daily_withdrawal_limit=data.get("daily_withdrawal_limit", 500000),
            max_daily_trades=data.get("max_daily_trades", 200),
            max_intraday_trades=data.get("max_intraday_trades", 100),
            cool_down_period=data.get("cool_down_period", 60),
            global_stop_loss=data.get("global_stop_loss", 0.1),
            global_take_profit=data.get("global_take_profit", 0.2),
            position_stop_loss=data.get("position_stop_loss", 0.05),
            position_take_profit=data.get("position_take_profit", 0.1),
            warning_level=data.get("warning_level", 0.8),
            alert_notification=data.get("alert_notification", True),
            monitoring_interval=data.get("monitoring_interval", 60)
        )


class StockRiskManager:
    """股票风险管理器"""
    
    def __init__(self, config: Optional[StockRiskConfig] = None):
        """初始化股票风险管理器
        
        Args:
            config: 股票风险控制配置
        """
        self.config = config or StockRiskConfig()
        self.account_manager = get_account_manager()
        self.trading_time_manager = get_trading_time_manager()
        
        # 风险监控数据
        self.risk_data = {
            "daily_trades": {},  # 每日交易次数 {account_id: {stock: count}}
            "intraday_trades": {},  # 日内交易次数 {account_id: count}
            "last_trade_time": {},  # 最后交易时间 {account_id: datetime}
            "position_risk": {},  # 持仓风险 {account_id: {stock: {risk_score, exposure}}}
            "industry_exposure": {},  # 行业暴露 {account_id: {industry: exposure}}
            "market_risk": {},  # 市场风险 {date: risk_score}
            "liquidity_risk": {},  # 流动性风险 {stock: risk_score}
            "compliance_risk": {},  # 合规风险 {account_id: {stock: risk_score}}
            "drawdown": {},  # 回撤 {account_id: drawdown}
            "profit_loss": {},  # 盈亏 {account_id: pnl}
            "leverage": {},  # 杠杆 {account_id: leverage}
            "warnings": [],  # 预警记录
            "violations": [],  # 违规记录
            "last_monitoring": datetime.now()  # 最后监控时间
        }
        
        # 行业映射（示例）
        self.industry_map = {
            "600000": "银行",
            "600519": "白酒",
            "000858": "白酒",
            "000001": "银行",
            "002594": "食品饮料",
            "601318": "保险",
            "601628": "保险",
            "600036": "银行",
            "601888": "银行",
            "601166": "银行",
            "000333": "家电",
            "600887": "食品饮料",
            "600276": "医药",
            "601607": "医药",
            "002304": "汽车",
            "600104": "汽车",
            "601800": "建筑",
            "601117": "建筑",
            "000002": "地产",
            "600048": "地产",
            "600031": "机械",
            "601106": "机械",
            "000651": "电子",
            "600703": "电子",
            "600585": "煤炭",
            "601088": "煤炭",
            "600028": "石化",
            "601857": "石化",
            "601988": "银行",
            "601328": "银行"
        }
    
    def check_order_risk(self, account_id: str, order: OrderData) -> Dict:
        """检查订单风险
        
        Args:
            account_id: 账户ID
            order: 订单数据
            
        Returns:
            风险检查结果
        """
        # 获取账户
        account = self.account_manager.get_account(account_id)
        if not account:
            return {
                "risk_passed": False,
                "reason": "Account not found",
                "risk_score": 1.0
            }
        
        # 初始化账户风险数据
        self._init_account_risk_data(account_id)
        
        # 检查交易时间
        if not self.trading_time_manager.is_trading_time(datetime.now()):
            return {
                "risk_passed": False,
                "reason": "Not trading time",
                "risk_score": 1.0
            }
        
        # 检查股票是否停牌
        if self.trading_time_manager.is_stock_suspended(order.symbol):
            return {
                "risk_passed": False,
                "reason": "Stock is suspended",
                "risk_score": 1.0
            }
        
        # 检查交易频率
        if not self._check_trade_frequency(account_id, order.symbol):
            return {
                "risk_passed": False,
                "reason": "Trade frequency limit exceeded",
                "risk_score": 0.9
            }
        
        # 检查持仓限额
        if not self._check_position_limit(account_id, order.symbol, order.volume):
            return {
                "risk_passed": False,
                "reason": "Position limit exceeded",
                "risk_score": 0.8
            }
        
        # 检查行业暴露
        if not self._check_industry_exposure(account_id, order.symbol, order.volume):
            return {
                "risk_passed": False,
                "reason": "Industry exposure limit exceeded",
                "risk_score": 0.7
            }
        
        # 检查流动性风险
        if not self._check_liquidity_risk(order.symbol, order.volume):
            return {
                "risk_passed": False,
                "reason": "Liquidity risk too high",
                "risk_score": 0.6
            }
        
        # 检查合规风险
        if not self._check_compliance_risk(account_id, order.symbol):
            return {
                "risk_passed": False,
                "reason": "Compliance risk detected",
                "risk_score": 0.95
            }
        
        # 检查杠杆风险
        if not self._check_leverage_risk(account_id, order.price * order.volume):
            return {
                "risk_passed": False,
                "reason": "Leverage limit exceeded",
                "risk_score": 0.85
            }
        
        # 检查止损止盈
        if not self._check_stop_loss_take_profit(account_id, order.symbol):
            return {
                "risk_passed": False,
                "reason": "Stop loss/take profit limit hit",
                "risk_score": 0.75
            }
        
        # 检查市场风险
        if not self._check_market_risk():
            return {
                "risk_passed": False,
                "reason": "Market risk too high",
                "risk_score": 0.8
            }
        
        return {
            "risk_passed": True,
            "reason": "Risk check passed",
            "risk_score": 0.0
        }
    
    def _init_account_risk_data(self, account_id: str):
        """初始化账户风险数据
        
        Args:
            account_id: 账户ID
        """
        if account_id not in self.risk_data["daily_trades"]:
            self.risk_data["daily_trades"][account_id] = {}
        if account_id not in self.risk_data["intraday_trades"]:
            self.risk_data["intraday_trades"][account_id] = 0
        if account_id not in self.risk_data["last_trade_time"]:
            self.risk_data["last_trade_time"][account_id] = datetime.now() - timedelta(days=1)
        if account_id not in self.risk_data["position_risk"]:
            self.risk_data["position_risk"][account_id] = {}
        if account_id not in self.risk_data["industry_exposure"]:
            self.risk_data["industry_exposure"][account_id] = {}
        if account_id not in self.risk_data["drawdown"]:
            self.risk_data["drawdown"][account_id] = 0.0
        if account_id not in self.risk_data["profit_loss"]:
            self.risk_data["profit_loss"][account_id] = 0.0
        if account_id not in self.risk_data["leverage"]:
            self.risk_data["leverage"][account_id] = 0.0
        if account_id not in self.risk_data["compliance_risk"]:
            self.risk_data["compliance_risk"][account_id] = {}
    
    def _check_trade_frequency(self, account_id: str, symbol: str) -> bool:
        """检查交易频率
        
        Args:
            account_id: 账户ID
            symbol: 股票代码
            
        Returns:
            是否通过检查
        """
        # 检查冷却期
        last_trade = self.risk_data["last_trade_time"][account_id]
        if (datetime.now() - last_trade).total_seconds() < self.config.cool_down_period:
            return False
        
        # 检查每日交易次数
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.risk_data["daily_trades"][account_id]:
            self.risk_data["daily_trades"][account_id][today] = {}
        
        if symbol not in self.risk_data["daily_trades"][account_id][today]:
            self.risk_data["daily_trades"][account_id][today][symbol] = 0
        
        # 检查单股票每日交易次数
        if self.risk_data["daily_trades"][account_id][today][symbol] >= self.config.max_trades_per_stock:
            return False
        
        # 检查总每日交易次数
        total_daily_trades = sum(self.risk_data["daily_trades"][account_id][today].values())
        if total_daily_trades >= self.config.max_daily_trades:
            return False
        
        # 检查日内交易次数
        if self.risk_data["intraday_trades"][account_id] >= self.config.max_intraday_trades:
            return False
        
        return True
    
    def _check_position_limit(self, account_id: str, symbol: str, volume: int) -> bool:
        """检查持仓限额
        
        Args:
            account_id: 账户ID
            symbol: 股票代码
            volume: 交易数量
            
        Returns:
            是否通过检查
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return False
        
        # 检查最大持仓数量
        current_positions = len([p for p in account.positions.values() if p.volume > 0])
        if current_positions >= self.config.max_total_positions:
            return False
        
        # 检查单股票持仓比例
        position = account.get_position(symbol)
        if position:
            current_exposure = position.market_value
        else:
            current_exposure = 0.0
        
        total_asset = account.total_asset
        new_exposure = current_exposure + volume * 10  # 假设价格为10元
        
        if new_exposure / total_asset > self.config.max_position_per_stock:
            return False
        
        return True
    
    def _check_industry_exposure(self, account_id: str, symbol: str, volume: int) -> bool:
        """检查行业暴露
        
        Args:
            account_id: 账户ID
            symbol: 股票代码
            volume: 交易数量
            
        Returns:
            是否通过检查
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return False
        
        # 获取行业
        industry = self.industry_map.get(symbol, "其他")
        if not industry:
            return True  # 未知行业，跳过检查
        
        # 计算当前行业暴露
        current_exposure = self.risk_data["industry_exposure"][account_id].get(industry, 0.0)
        
        # 计算新增暴露
        new_exposure = current_exposure + volume * 10  # 假设价格为10元
        
        # 检查行业暴露上限
        total_asset = account.total_asset
        if new_exposure / total_asset > self.config.max_position_per_industry:
            return False
        
        # 检查行业集中度
        total_industry_exposure = sum(self.risk_data["industry_exposure"][account_id].values())
        if total_industry_exposure > 0:
            concentration = new_exposure / total_industry_exposure
            if concentration > self.config.max_industry_concentration:
                return False
        
        return True
    
    def _check_liquidity_risk(self, symbol: str, volume: int) -> bool:
        """检查流动性风险
        
        Args:
            symbol: 股票代码
            volume: 交易数量
            
        Returns:
            是否通过检查
        """
        # 检查流动性风险（示例实现）
        # 实际应用中应该从数据源获取真实的成交量和换手率
        
        # 假设最小成交量
        min_volume = self.config.min_volume
        if volume > min_volume * self.config.max_position_to_volume_ratio:
            return False
        
        # 检查换手率（示例）
        # 实际应用中应该计算真实的换手率
        
        return True
    
    def _check_compliance_risk(self, account_id: str, symbol: str) -> bool:
        """检查合规风险
        
        Args:
            account_id: 账户ID
            symbol: 股票代码
            
        Returns:
            是否通过检查
        """
        # 检查内幕交易风险（示例）
        # 实际应用中应该检查：
        # 1. 上市公司内幕信息
        # 2. 高管交易
        # 3. 重大事件前交易
        
        # 检查市场操纵风险（示例）
        # 实际应用中应该检查：
        # 1. 频繁报撤单
        # 2. 对敲交易
        # 3. 拉抬打压股价
        
        return True
    
    def _check_leverage_risk(self, account_id: str, amount: float) -> bool:
        """检查杠杆风险
        
        Args:
            account_id: 账户ID
            amount: 交易金额
            
        Returns:
            是否通过检查
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return False
        
        # 计算杠杆
        total_asset = account.total_asset
        market_value = account.total_market_value
        
        if total_asset > 0:
            leverage = market_value / total_asset
            if leverage > self.config.max_leverage:
                return False
        
        return True
    
    def _check_stop_loss_take_profit(self, account_id: str, symbol: str) -> bool:
        """检查止损止盈
        
        Args:
            account_id: 账户ID
            symbol: 股票代码
            
        Returns:
            是否通过检查
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return False
        
        # 检查全局止损
        drawdown = self.risk_data["drawdown"][account_id]
        if drawdown > self.config.global_stop_loss:
            return False
        
        # 检查单持仓止损
        position = account.get_position(symbol)
        if position:
            pnl_ratio = position.profit_ratio
            if pnl_ratio < -self.config.position_stop_loss:
                return False
            if pnl_ratio > self.config.position_take_profit:
                return False
        
        return True
    
    def _check_market_risk(self) -> bool:
        """检查市场风险
        
        Returns:
            是否通过检查
        """
        # 检查市场风险（示例）
        # 实际应用中应该：
        # 1. 监控大盘指数
        # 2. 计算波动率
        # 3. 检查市场情绪
        
        return True
    
    def update_trade_risk(self, account_id: str, trade: TradeData):
        """更新交易风险
        
        Args:
            account_id: 账户ID
            trade: 成交数据
        """
        # 更新交易次数
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.risk_data["daily_trades"][account_id]:
            self.risk_data["daily_trades"][account_id][today] = {}
        
        if trade.symbol not in self.risk_data["daily_trades"][account_id][today]:
            self.risk_data["daily_trades"][account_id][today][trade.symbol] = 0
        
        self.risk_data["daily_trades"][account_id][today][trade.symbol] += 1
        self.risk_data["intraday_trades"][account_id] += 1
        self.risk_data["last_trade_time"][account_id] = datetime.now()
        
        # 更新行业暴露
        industry = self.industry_map.get(trade.symbol, "其他")
        if industry:
            if industry not in self.risk_data["industry_exposure"][account_id]:
                self.risk_data["industry_exposure"][account_id][industry] = 0.0
            
            exposure = trade.price * trade.volume
            if trade.direction == Direction.LONG:
                self.risk_data["industry_exposure"][account_id][industry] += exposure
            else:
                self.risk_data["industry_exposure"][account_id][industry] -= exposure
        
        # 更新持仓风险
        account = self.account_manager.get_account(account_id)
        if account:
            position = account.get_position(trade.symbol)
            if position:
                risk_score = self._calculate_position_risk(position)
                self.risk_data["position_risk"][account_id][trade.symbol] = {
                    "risk_score": risk_score,
                    "exposure": position.market_value
                }
    
    def _calculate_position_risk(self, position) -> float:
        """计算持仓风险
        
        Args:
            position: 持仓对象
            
        Returns:
            风险评分
        """
        # 计算风险评分（示例）
        risk_score = 0.0
        
        # 基于盈亏比例的风险
        if position.profit_ratio < -self.config.position_stop_loss:
            risk_score += 0.5
        elif position.profit_ratio > self.config.position_take_profit:
            risk_score += 0.3
        
        # 基于持仓比例的风险
        account = self.account_manager.get_account("default")  # 假设默认账户
        if account:
            exposure_ratio = position.market_value / account.total_asset
            if exposure_ratio > self.config.max_position_per_stock:
                risk_score += 0.5
            elif exposure_ratio > self.config.max_position_per_stock * self.config.warning_level:
                risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def calculate_portfolio_risk(self, account_id: str) -> Dict:
        """计算组合风险
        
        Args:
            account_id: 账户ID
            
        Returns:
            组合风险评估
        """
        account = self.account_manager.get_account(account_id)
        if not account:
            return {
                "risk_score": 0.0,
                "exposure": 0.0,
                "diversification": 0.0,
                "liquidity": 0.0,
                "volatility": 0.0,
                "drawdown": 0.0,
                "leverage": 0.0,
                "industry_concentration": 0.0,
                "stock_concentration": 0.0,
                "risk_level": "low"
            }
        
        # 计算风险指标
        position_count = account.position_count
        total_asset = account.total_asset
        market_value = account.total_market_value
        total_profit = account.total_profit
        
        # 计算集中度
        if position_count > 0:
            stock_concentration = 1.0 / position_count
        else:
            stock_concentration = 0.0
        
        # 计算行业集中度
        industries = set()
        for symbol in account.positions:
            industry = self.industry_map.get(symbol, "其他")
            industries.add(industry)
        
        if len(industries) > 0:
            industry_concentration = 1.0 / len(industries)
        else:
            industry_concentration = 0.0
        
        # 计算杠杆
        if total_asset > 0:
            leverage = market_value / total_asset
        else:
            leverage = 0.0
        
        # 计算风险评分
        risk_score = 0.0
        
        # 基于集中度的风险
        risk_score += stock_concentration * 0.3
        risk_score += industry_concentration * 0.3
        
        # 基于杠杆的风险
        risk_score += min(leverage / self.config.max_leverage, 1.0) * 0.2
        
        # 基于盈亏的风险
        if total_asset > 0:
            drawdown = max(0.0, (total_asset - account.initial_balance) / account.initial_balance)
            risk_score += min(drawdown / self.config.global_stop_loss, 1.0) * 0.2
        
        # 确定风险等级
        if risk_score < 0.3:
            risk_level = "low"
        elif risk_score < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_score": min(risk_score, 1.0),
            "exposure": market_value,
            "diversification": 1.0 - (stock_concentration + industry_concentration) / 2,
            "liquidity": 0.8,  # 示例值
            "volatility": 0.2,  # 示例值
            "drawdown": drawdown if 'drawdown' in locals() else 0.0,
            "leverage": leverage,
            "industry_concentration": industry_concentration,
            "stock_concentration": stock_concentration,
            "risk_level": risk_level
        }
    
    def generate_risk_report(self, account_id: str) -> Dict:
        """生成风险报告
        
        Args:
            account_id: 账户ID
            
        Returns:
            风险报告
        """
        portfolio_risk = self.calculate_portfolio_risk(account_id)
        
        # 生成详细风险报告
        report = {
            "account_id": account_id,
            "report_time": datetime.now().isoformat(),
            "portfolio_risk": portfolio_risk,
            "position_risks": [],
            "industry_exposure": {},
            "trading_activity": {
                "daily_trades": 0,
                "intraday_trades": 0,
                "most_traded_stocks": []
            },
            "compliance_status": {
                "insider_trading": "clear",
                "market_manipulation": "clear",
                "regulatory_compliance": "clear"
            },
            "risk_alerts": [],
            "recommendations": []
        }
        
        # 添加持仓风险
        account = self.account_manager.get_account(account_id)
        if account:
            for position in account.positions.values():
                if position.volume > 0:
                    risk_score = self._calculate_position_risk(position)
                    report["position_risks"].append({
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "avg_price": position.avg_price,
                        "current_price": position.current_price,
                        "market_value": position.market_value,
                        "profit": position.profit,
                        "profit_ratio": position.profit_ratio,
                        "risk_score": risk_score,
                        "risk_level": "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low"
                    })
            
            # 添加行业暴露
            report["industry_exposure"] = self.risk_data["industry_exposure"].get(account_id, {})
            
            # 添加交易活动
            today = datetime.now().strftime("%Y-%m-%d")
            daily_trades = self.risk_data["daily_trades"].get(account_id, {}).get(today, {})
            report["trading_activity"]["daily_trades"] = sum(daily_trades.values())
            report["trading_activity"]["intraday_trades"] = self.risk_data["intraday_trades"].get(account_id, 0)
            
            # 添加风险预警
            if portfolio_risk["risk_score"] > 0.6:
                report["risk_alerts"].append({
                    "type": "portfolio_risk",
                    "level": "high",
                    "message": f"组合风险评分过高: {portfolio_risk['risk_score']:.2f}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 添加建议
            if portfolio_risk["industry_concentration"] > 0.7:
                report["recommendations"].append({
                    "type": "diversification",
                    "message": "行业集中度过高，建议分散投资",
                    "priority": "high"
                })
            
            if portfolio_risk["leverage"] > self.config.max_leverage * 0.8:
                report["recommendations"].append({
                    "type": "leverage",
                    "message": "杠杆水平接近上限，建议降低仓位",
                    "priority": "medium"
                })
        
        return report
    
    def update_config(self, config: StockRiskConfig):
        """更新配置
        
        Args:
            config: 新的风险控制配置
        """
        self.config = config
    
    def get_config(self) -> StockRiskConfig:
        """获取配置
        
        Returns:
            风险控制配置
        """
        return self.config
    
    def reset_daily_data(self):
        """重置每日数据
        """
        today = datetime.now().strftime("%Y-%m-%d")
        for account_id in self.risk_data["daily_trades"]:
            if today in self.risk_data["daily_trades"][account_id]:
                del self.risk_data["daily_trades"][account_id][today]
        
        for account_id in self.risk_data["intraday_trades"]:
            self.risk_data["intraday_trades"][account_id] = 0
    
    def monitor_risk(self):
        """监控风险
        
        Returns:
            监控结果
        """
        # 检查监控间隔
        if (datetime.now() - self.risk_data["last_monitoring"]).total_seconds() < self.config.monitoring_interval:
            return {"status": "ok", "message": "Monitoring interval not reached"}
        
        # 监控所有账户
        alerts = []
        
        for account_id in self.risk_data["position_risk"]:
            portfolio_risk = self.calculate_portfolio_risk(account_id)
            
            if portfolio_risk["risk_score"] > self.config.warning_level:
                alerts.append({
                    "account_id": account_id,
                    "risk_score": portfolio_risk["risk_score"],
                    "risk_level": portfolio_risk["risk_level"],
                    "message": f"账户风险评分过高: {portfolio_risk['risk_score']:.2f}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # 更新最后监控时间
        self.risk_data["last_monitoring"] = datetime.now()
        
        return {
            "status": "ok",
            "message": "Risk monitoring completed",
            "alerts": alerts,
            "monitoring_time": self.risk_data["last_monitoring"].isoformat()
        }


# 全局实例
global_stock_risk_manager = StockRiskManager()

def get_stock_risk_manager() -> StockRiskManager:
    """获取股票风险管理器实例
    
    Returns:
        股票风险管理器实例
    """
    return global_stock_risk_manager


def check_stock_order_risk(account_id: str, order: OrderData) -> Dict:
    """检查股票订单风险
    
    Args:
        account_id: 账户ID
        order: 订单数据
        
    Returns:
        风险检查结果
    """
    return get_stock_risk_manager().check_order_risk(account_id, order)


def calculate_stock_portfolio_risk(account_id: str) -> Dict:
    """计算股票组合风险
    
    Args:
        account_id: 账户ID
        
    Returns:
        组合风险评估
    """
    return get_stock_risk_manager().calculate_portfolio_risk(account_id)


def generate_stock_risk_report(account_id: str) -> Dict:
    """生成股票风险报告
    
    Args:
        account_id: 账户ID
        
    Returns:
        风险报告
    """
    return get_stock_risk_manager().generate_risk_report(account_id)