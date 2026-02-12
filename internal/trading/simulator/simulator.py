"""
模拟盘交易核心功能
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SimulatedOrder:
    """模拟订单"""
    def __init__(self, order_id: str, symbol: str, direction: str, offset: str, price: float, volume: int, 
                 status: str = "pending", create_time: datetime = None):
        self.order_id = order_id
        self.symbol = symbol
        self.direction = direction  # 'buy' or 'sell'
        self.offset = offset        # 'open' or 'close'
        self.price = price
        self.volume = volume
        self.traded_volume = 0
        self.status = status        # 'pending', 'filled', 'canceled'
        self.create_time = create_time or datetime.now()
        self.update_time = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "offset": self.offset,
            "price": self.price,
            "volume": self.volume,
            "traded_volume": self.traded_volume,
            "status": self.status,
            "create_time": self.create_time.isoformat(),
            "update_time": self.update_time.isoformat()
        }


class SimulatedTrade:
    """模拟成交"""
    def __init__(self, trade_id: str, order_id: str, symbol: str, direction: str, offset: str, 
                 price: float, volume: int, trade_time: datetime = None):
        self.trade_id = trade_id
        self.order_id = order_id
        self.symbol = symbol
        self.direction = direction
        self.offset = offset
        self.price = price
        self.volume = volume
        self.trade_time = trade_time or datetime.now()

    def to_dict(self) -> Dict:
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "direction": self.direction,
            "offset": self.offset,
            "price": self.price,
            "volume": self.volume,
            "trade_time": self.trade_time.isoformat()
        }


class SimulatedPosition:
    """模拟持仓"""
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.volume = 0          # 持仓数量
        self.frozen = 0          # 冻结数量
        self.avg_price = 0.0     # 持仓均价

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "volume": self.volume,
            "frozen": self.frozen,
            "avg_price": self.avg_price
        }


class SimulatedAccount:
    """模拟账户"""
    def __init__(self, initial_balance: float = 100000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.available = initial_balance
        self.frozen = 0.0
        self.total = initial_balance
        self.pnl = 0.0

    def to_dict(self) -> Dict:
        return {
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "available": self.available,
            "frozen": self.frozen,
            "total": self.total,
            "pnl": self.pnl
        }


class TradingSimulator:
    """交易模拟器"""
    
    def __init__(self, initial_balance: float = 100000.0):
        self.account = SimulatedAccount(initial_balance)
        self.positions: Dict[str, SimulatedPosition] = {}
        self.orders: Dict[str, SimulatedOrder] = {}
        self.trades: List[SimulatedTrade] = []
        self.symbol_prices: Dict[str, float] = {}  # 当前模拟价格

    def set_symbol_price(self, symbol: str, price: float):
        """设置合约当前价格"""
        self.symbol_prices[symbol] = price

    def get_position(self, symbol: str) -> SimulatedPosition:
        """获取持仓"""
        if symbol not in self.positions:
            self.positions[symbol] = SimulatedPosition(symbol)
        return self.positions[symbol]

    def buy(self, symbol: str, price: float, volume: int) -> Tuple[str, Optional[str]]:
        """买入"""
        order_id = str(uuid.uuid4())
        order = SimulatedOrder(
            order_id=order_id,
            symbol=symbol,
            direction="buy",
            offset="open",
            price=price,
            volume=volume
        )
        
        # 检查资金是否足够
        cost = price * volume
        if cost > self.account.available:
            return order_id, f"资金不足：需要 {cost}，可用 {self.account.available}"
        
        # 冻结资金
        self.account.available -= cost
        self.account.frozen += cost
        
        # 模拟成交
        trade_id = str(uuid.uuid4())
        trade = SimulatedTrade(
            trade_id=trade_id,
            order_id=order_id,
            symbol=symbol,
            direction="buy",
            offset="open",
            price=price,
            volume=volume
        )
        
        # 更新持仓
        position = self.get_position(symbol)
        if position.volume == 0:
            position.avg_price = price
        else:
            total_cost = position.avg_price * position.volume + price * volume
            position.avg_price = total_cost / (position.volume + volume)
        position.volume += volume
        
        # 释放冻结资金
        self.account.frozen -= cost
        
        # 更新订单状态
        order.traded_volume = volume
        order.status = "filled"
        
        # 记录
        self.orders[order_id] = order
        self.trades.append(trade)
        
        return order_id, None

    def sell(self, symbol: str, price: float, volume: int) -> Tuple[str, Optional[str]]:
        """卖出"""
        order_id = str(uuid.uuid4())
        order = SimulatedOrder(
            order_id=order_id,
            symbol=symbol,
            direction="sell",
            offset="close",
            price=price,
            volume=volume
        )
        
        # 检查持仓是否足够
        position = self.get_position(symbol)
        if position.volume < volume:
            return order_id, f"持仓不足：需要 {volume}，可用 {position.volume}"
        
        # 模拟成交
        trade_id = str(uuid.uuid4())
        trade = SimulatedTrade(
            trade_id=trade_id,
            order_id=order_id,
            symbol=symbol,
            direction="sell",
            offset="close",
            price=price,
            volume=volume
        )
        
        # 计算盈亏
        pnl = (price - position.avg_price) * volume
        
        # 更新持仓
        position.volume -= volume
        if position.volume == 0:
            position.avg_price = 0.0
        
        # 更新资金
        self.account.available += price * volume
        self.account.balance += pnl
        self.account.total = self.account.balance
        self.account.pnl = self.account.balance - self.account.initial_balance
        
        # 更新订单状态
        order.traded_volume = volume
        order.status = "filled"
        
        # 记录
        self.orders[order_id] = order
        self.trades.append(trade)
        
        return order_id, None

    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status != "pending":
            return False
        
        # 释放冻结资金
        if order.direction == "buy":
            cost = order.price * order.volume
            self.account.frozen -= cost
            self.account.available += cost
        
        order.status = "canceled"
        return True

    def get_account_info(self) -> Dict:
        """获取账户信息"""
        return self.account.to_dict()

    def get_positions(self) -> List[Dict]:
        """获取持仓信息"""
        return [pos.to_dict() for pos in self.positions.values() if pos.volume > 0]

    def get_orders(self) -> List[Dict]:
        """获取订单信息"""
        return [order.to_dict() for order in self.orders.values()]

    def get_trades(self) -> List[Dict]:
        """获取成交信息"""
        return [trade.to_dict() for trade in self.trades]

    def reset(self, initial_balance: float = None):
        """重置模拟器"""
        if initial_balance is None:
            initial_balance = self.account.initial_balance
        
        self.account = SimulatedAccount(initial_balance)
        self.positions = {}
        self.orders = {}
        self.trades = []
