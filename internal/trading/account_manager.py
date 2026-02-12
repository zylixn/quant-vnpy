"""
资金账户管理模块

管理股票交易的资金账户、持仓和资产组合
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from vnpy.trader.constant import Direction, Offset, Exchange
from vnpy.trader.object import OrderData, TradeData
from internal.trading.cost_calculator import StockTradingCostCalculator, get_cost_calculator


class StockPosition:
    """股票持仓"""
    
    def __init__(self, 
                 symbol: str, 
                 exchange: Exchange, 
                 volume: int = 0, 
                 avg_price: float = 0.0, 
                 current_price: float = 0.0):
        """初始化股票持仓
        
        Args:
            symbol: 股票代码
            exchange: 交易所
            volume: 持仓数量
            avg_price: 持仓均价
            current_price: 当前价格
        """
        self.symbol = symbol
        self.exchange = exchange
        self.volume = volume
        self.avg_price = avg_price
        self.current_price = current_price
        self.last_update_time = datetime.now()
        
    @property
    def market_value(self) -> float:
        """市值
        
        Returns:
            持仓市值
        """
        return self.current_price * self.volume
    
    @property
    def cost(self) -> float:
        """成本
        
        Returns:
            持仓成本
        """
        return self.avg_price * self.volume
    
    @property
    def profit(self) -> float:
        """盈亏
        
        Returns:
            持仓盈亏
        """
        return self.market_value - self.cost
    
    @property
    def profit_ratio(self) -> float:
        """盈亏比例
        
        Returns:
            盈亏比例
        """
        if self.cost > 0:
            return self.profit / self.cost
        return 0.0
    
    def update_trade(self, trade: TradeData):
        """根据成交更新持仓
        
        Args:
            trade: 成交数据
        """
        if trade.symbol != self.symbol or trade.exchange != self.exchange:
            return
        
        if trade.direction == Direction.LONG:
            # 买入
            if self.volume > 0:
                # 已有多头持仓，加仓
                total_cost = self.cost + trade.price * trade.volume
                total_volume = self.volume + trade.volume
                self.avg_price = total_cost / total_volume
                self.volume = total_volume
            else:
                # 空转多
                self.avg_price = trade.price
                self.volume = trade.volume
        else:
            # 卖出
            if self.volume > trade.volume:
                # 减仓
                self.volume -= trade.volume
            else:
                # 平仓
                self.volume = 0
                self.avg_price = 0.0
        
        self.current_price = trade.price
        self.last_update_time = datetime.now()
    
    def update_price(self, price: float):
        """更新价格
        
        Args:
            price: 当前价格
        """
        self.current_price = price
        self.last_update_time = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典
        
        Returns:
            持仓信息字典
        """
        return {
            "symbol": self.symbol,
            "exchange": self.exchange.value,
            "volume": self.volume,
            "avg_price": self.avg_price,
            "current_price": self.current_price,
            "market_value": self.market_value,
            "cost": self.cost,
            "profit": self.profit,
            "profit_ratio": self.profit_ratio,
            "last_update_time": self.last_update_time.isoformat()
        }


class StockAccount:
    """股票账户"""
    
    def __init__(self, 
                 account_id: str, 
                 initial_balance: float = 0.0, 
                 cost_calculator: Optional[StockTradingCostCalculator] = None):
        """初始化股票账户
        
        Args:
            account_id: 账户ID
            initial_balance: 初始资金
            cost_calculator: 交易成本计算器
        """
        self.account_id = account_id
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.available = initial_balance
        self.frozen = 0.0
        self.positions: Dict[str, StockPosition] = {}  # key: symbol
        self.cost_calculator = cost_calculator or get_cost_calculator()
        self.trades: List[TradeData] = []
        self.orders: List[OrderData] = []
        self.history: List[Dict] = []  # 资金变动历史
        self.last_update_time = datetime.now()
    
    @property
    def total_asset(self) -> float:
        """总资产
        
        Returns:
            总资产
        """
        return self.balance + self.total_market_value
    
    @property
    def total_market_value(self) -> float:
        """总市值
        
        Returns:
            总市值
        """
        return sum(position.market_value for position in self.positions.values())
    
    @property
    def total_profit(self) -> float:
        """总盈亏
        
        Returns:
            总盈亏
        """
        return sum(position.profit for position in self.positions.values())
    
    @property
    def total_profit_ratio(self) -> float:
        """总盈亏比例
        
        Returns:
            总盈亏比例
        """
        total_cost = sum(position.cost for position in self.positions.values())
        if total_cost > 0:
            return self.total_profit / total_cost
        return 0.0
    
    @property
    def position_count(self) -> int:
        """持仓数量
        
        Returns:
            持仓数量
        """
        return len([p for p in self.positions.values() if p.volume > 0])
    
    def get_position(self, symbol: str) -> Optional[StockPosition]:
        """获取持仓
        
        Args:
            symbol: 股票代码
            
        Returns:
            持仓对象
        """
        return self.positions.get(symbol)
    
    def add_position(self, position: StockPosition):
        """添加持仓
        
        Args:
            position: 持仓对象
        """
        self.positions[position.symbol] = position
    
    def remove_position(self, symbol: str):
        """移除持仓
        
        Args:
            symbol: 股票代码
        """
        if symbol in self.positions:
            del self.positions[symbol]
    
    def update_trade(self, trade: TradeData):
        """根据成交更新账户
        
        Args:
            trade: 成交数据
        """
        # 计算交易成本
        cost_info = self.cost_calculator.calculate_cost(
            price=trade.price,
            volume=trade.volume,
            direction=trade.direction,
            offset=trade.offset,
            exchange=trade.exchange
        )
        
        # 更新资金
        if trade.direction == Direction.LONG:
            # 买入，减少可用资金
            self.available -= cost_info["amount"] + cost_info["total_cost"]
            self.balance -= cost_info["amount"] + cost_info["total_cost"]
        else:
            # 卖出，增加可用资金
            self.available += cost_info["amount"] - cost_info["total_cost"]
            self.balance += cost_info["amount"] - cost_info["total_cost"]
        
        # 更新持仓
        symbol = trade.symbol
        if symbol not in self.positions:
            self.positions[symbol] = StockPosition(
                symbol=symbol,
                exchange=trade.exchange
            )
        
        self.positions[symbol].update_trade(trade)
        
        # 记录成交
        self.trades.append(trade)
        
        # 记录资金变动
        self.history.append({
            "time": datetime.now(),
            "type": "trade",
            "symbol": symbol,
            "direction": trade.direction.value,
            "volume": trade.volume,
            "price": trade.price,
            "amount": cost_info["amount"],
            "cost": cost_info["total_cost"],
            "balance": self.balance,
            "available": self.available
        })
        
        self.last_update_time = datetime.now()
    
    def update_order(self, order: OrderData):
        """根据订单更新账户
        
        Args:
            order: 订单数据
        """
        # 记录订单
        self.orders.append(order)
        
        # 如果是新订单且是买入，冻结资金
        if order.status == OrderData.Status.SUBMITTED and order.direction == Direction.LONG:
            estimated_cost = order.price * order.volume * 1.01  # 预估1%的成本
            self.frozen += estimated_cost
            self.available -= estimated_cost
        
        # 如果订单取消或失败，解冻资金
        elif order.status in [OrderData.Status.CANCELLED, OrderData.Status.REJECTED]:
            if order.direction == Direction.LONG:
                estimated_cost = order.price * order.volume * 1.01
                self.frozen -= estimated_cost
                self.available += estimated_cost
        
        self.last_update_time = datetime.now()
    
    def update_price(self, symbol: str, price: float):
        """更新股票价格
        
        Args:
            symbol: 股票代码
            price: 当前价格
        """
        if symbol in self.positions:
            self.positions[symbol].update_price(price)
        
        self.last_update_time = datetime.now()
    
    def deposit(self, amount: float):
        """存入资金
        
        Args:
            amount: 存入金额
        """
        if amount > 0:
            self.balance += amount
            self.available += amount
            
            # 记录资金变动
            self.history.append({
                "time": datetime.now(),
                "type": "deposit",
                "amount": amount,
                "balance": self.balance,
                "available": self.available
            })
            
            self.last_update_time = datetime.now()
    
    def withdraw(self, amount: float):
        """取出资金
        
        Args:
            amount: 取出金额
        """
        if amount > 0 and amount <= self.available:
            self.balance -= amount
            self.available -= amount
            
            # 记录资金变动
            self.history.append({
                "time": datetime.now(),
                "type": "withdraw",
                "amount": amount,
                "balance": self.balance,
                "available": self.available
            })
            
            self.last_update_time = datetime.now()
    
    def handle_dividend(self, symbol: str, amount: float):
        """处理分红
        
        Args:
            symbol: 股票代码
            amount: 分红金额
        """
        if amount > 0:
            self.balance += amount
            self.available += amount
            
            # 记录资金变动
            self.history.append({
                "time": datetime.now(),
                "type": "dividend",
                "symbol": symbol,
                "amount": amount,
                "balance": self.balance,
                "available": self.available
            })
            
            self.last_update_time = datetime.now()
    
    def handle_bonus(self, symbol: str, bonus_shares: int):
        """处理送股
        
        Args:
            symbol: 股票代码
            bonus_shares: 送股数量
        """
        if symbol in self.positions and bonus_shares > 0:
            position = self.positions[symbol]
            old_volume = position.volume
            new_volume = old_volume + bonus_shares
            
            # 调整持仓
            position.volume = new_volume
            position.avg_price = position.cost / new_volume
            
            # 记录变动
            self.history.append({
                "time": datetime.now(),
                "type": "bonus",
                "symbol": symbol,
                "old_volume": old_volume,
                "new_volume": new_volume,
                "bonus_shares": bonus_shares
            })
            
            self.last_update_time = datetime.now()
    
    def get_portfolio_summary(self) -> Dict:
        """获取资产组合摘要
        
        Returns:
            资产组合摘要
        """
        positions = []
        for position in self.positions.values():
            if position.volume > 0:
                positions.append(position.to_dict())
        
        return {
            "account_id": self.account_id,
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "available": self.available,
            "frozen": self.frozen,
            "total_asset": self.total_asset,
            "total_market_value": self.total_market_value,
            "total_profit": self.total_profit,
            "total_profit_ratio": self.total_profit_ratio,
            "position_count": self.position_count,
            "positions": positions,
            "trade_count": len(self.trades),
            "last_update_time": self.last_update_time
        }
    
    def get_position_summary(self, symbol: str) -> Optional[Dict]:
        """获取单个持仓摘要
        
        Args:
            symbol: 股票代码
            
        Returns:
            持仓摘要
        """
        position = self.get_position(symbol)
        if position:
            return position.to_dict()
        return None
    
    def get_trade_history(self, limit: int = 100) -> List[TradeData]:
        """获取成交历史
        
        Args:
            limit: 限制数量
            
        Returns:
            成交历史
        """
        return self.trades[-limit:]
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取资金变动历史
        
        Args:
            limit: 限制数量
            
        Returns:
            资金变动历史
        """
        return self.history[-limit:]


class PortfolioManager:
    """资产组合管理器"""
    
    def __init__(self):
        """初始化资产组合管理器"""
        self.accounts: Dict[str, StockAccount] = {}  # key: account_id
        self.strategies: Dict[str, Dict] = {}  # key: strategy_name
    
    def add_account(self, account: StockAccount):
        """添加账户
        
        Args:
            account: 股票账户
        """
        self.accounts[account.account_id] = account
    
    def get_account(self, account_id: str) -> Optional[StockAccount]:
        """获取账户
        
        Args:
            account_id: 账户ID
            
        Returns:
            股票账户
        """
        return self.accounts.get(account_id)
    
    def remove_account(self, account_id: str):
        """移除账户
        
        Args:
            account_id: 账户ID
        """
        if account_id in self.accounts:
            del self.accounts[account_id]
    
    def get_total_asset(self) -> float:
        """获取总资产
        
        Returns:
            总资产
        """
        return sum(account.total_asset for account in self.accounts.values())
    
    def get_total_profit(self) -> float:
        """获取总盈亏
        
        Returns:
            总盈亏
        """
        return sum(account.total_profit for account in self.accounts.values())
    
    def get_all_positions(self) -> Dict[str, List[StockPosition]]:
        """获取所有持仓
        
        Returns:
            所有持仓，按账户分组
        """
        positions = {}
        for account_id, account in self.accounts.items():
            positions[account_id] = list(account.positions.values())
        return positions
    
    def get_portfolio_summary(self) -> Dict:
        """获取资产组合摘要
        
        Returns:
            资产组合摘要
        """
        account_summaries = []
        total_asset = 0.0
        total_profit = 0.0
        
        for account in self.accounts.values():
            summary = account.get_portfolio_summary()
            account_summaries.append(summary)
            total_asset += summary["total_asset"]
            total_profit += summary["total_profit"]
        
        return {
            "total_accounts": len(self.accounts),
            "total_asset": total_asset,
            "total_profit": total_profit,
            "accounts": account_summaries
        }
    
    def add_strategy(self, strategy_name: str, config: Dict):
        """添加策略
        
        Args:
            strategy_name: 策略名称
            config: 策略配置
        """
        self.strategies[strategy_name] = {
            "config": config,
            "created_at": datetime.now(),
            "last_updated_at": datetime.now()
        }
    
    def get_strategy(self, strategy_name: str) -> Optional[Dict]:
        """获取策略
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            策略配置
        """
        return self.strategies.get(strategy_name)
    
    def update_strategy(self, strategy_name: str, config: Dict):
        """更新策略
        
        Args:
            strategy_name: 策略名称
            config: 策略配置
        """
        if strategy_name in self.strategies:
            self.strategies[strategy_name]["config"] = config
            self.strategies[strategy_name]["last_updated_at"] = datetime.now()
    
    def remove_strategy(self, strategy_name: str):
        """移除策略
        
        Args:
            strategy_name: 策略名称
        """
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]


# 全局实例
global_account_manager = PortfolioManager()

def get_account_manager() -> PortfolioManager:
    """获取账户管理器实例
    
    Returns:
        账户管理器实例
    """
    return global_account_manager


def create_stock_account(account_id: str, initial_balance: float = 0.0) -> StockAccount:
    """创建股票账户
    
    Args:
        account_id: 账户ID
        initial_balance: 初始资金
        
    Returns:
        股票账户实例
    """
    account = StockAccount(account_id, initial_balance)
    get_account_manager().add_account(account)
    return account


def get_stock_account(account_id: str) -> Optional[StockAccount]:
    """获取股票账户
    
    Args:
        account_id: 账户ID
        
    Returns:
        股票账户实例
    """
    return get_account_manager().get_account(account_id)


def get_portfolio_summary() -> Dict:
    """获取资产组合摘要
    
    Returns:
        资产组合摘要
    """
    return get_account_manager().get_portfolio_summary()