"""
基于vnpy的模拟盘交易核心功能
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from vnpy.trader.object import OrderData, TradeData, TickData, BarData, AccountData, PositionData
from vnpy.trader.constant import Direction, Offset, Exchange, OrderType, Status


class VnpySimulatedOrder:
    """兼容vnpy的模拟订单"""
    def __init__(self, 
            order_id: str,           # 订单ID
            symbol: str,             # 合约代码
            exchange: Exchange,      # 交易所
            direction: Direction,    # 交易方向
            offset: Offset,          # 开平方向
            price: float,            # 委托价格
            volume: float,           # 委托数量
            order_type: OrderType = OrderType.LIMIT,  # 订单类型
            status: Status = Status.SUBMITTING,       # 订单状态
            create_time: datetime = None,            # 创建时间
            gateway_name: str = "SIMULATOR"          # 网关名称
        ):
        self.order_id = order_id
        self.symbol = symbol
        self.exchange = exchange
        self.direction = direction
        self.offset = offset
        self.price = price
        self.volume = volume
        self.traded_volume = 0
        self.status = status
        self.order_type = order_type
        self.create_time = create_time or datetime.now()
        self.update_time = datetime.now()
        self.gateway_name = gateway_name

    def to_order_data(self) -> OrderData:
        """转换为vnpy的OrderData"""
        return OrderData(
            symbol=self.symbol,
            exchange=self.exchange,
            order_id=self.order_id,
            direction=self.direction,
            offset=self.offset,
            price=self.price,
            volume=self.volume,
            traded_volume=self.traded_volume,
            status=self.status,
            order_type=self.order_type,
            create_time=self.create_time,
            update_time=self.update_time,
            gateway_name=self.gateway_name
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "exchange": self.exchange.value,
            "direction": self.direction.value,
            "offset": self.offset.value,
            "price": self.price,
            "volume": self.volume,
            "traded_volume": self.traded_volume,
            "status": self.status.value,
            "order_type": self.order_type.value,
            "create_time": self.create_time.isoformat(),
            "update_time": self.update_time.isoformat(),
            "gateway_name": self.gateway_name
        }


class VnpySimulatedTrade:
    """兼容vnpy的模拟成交"""
    def __init__(self, 
            trade_id: str,           # 成交ID
            symbol: str,             # 合约代码
            exchange: Exchange,      # 交易所
            order_id: str,           # 订单ID
            direction: Direction,    # 交易方向
            offset: Offset,          # 开平方向
            price: float,            # 成交价格
            volume: float,           # 成交数量
            trade_time: datetime = None,            # 成交时间
            gateway_name: str = "SIMULATOR",          # 网关名称
            commission: float = 0.0,                 # 佣金
            pnl: float = 0.0                        # 盈亏
        ):
        self.trade_id = trade_id
        self.symbol = symbol
        self.exchange = exchange
        self.order_id = order_id
        self.direction = direction
        self.offset = offset
        self.price = price
        self.volume = volume
        self.trade_time = trade_time or datetime.now()
        self.gateway_name = gateway_name
        self.commission = commission
        self.pnl = pnl

    def to_trade_data(self) -> TradeData:
        """转换为vnpy的TradeData"""
        return TradeData(
            symbol=self.symbol,
            exchange=self.exchange,
            trade_id=self.trade_id,
            order_id=self.order_id,
            direction=self.direction,
            offset=self.offset,
            price=self.price,
            volume=self.volume,
            trade_time=self.trade_time,
            gateway_name=self.gateway_name,
            commission=self.commission,
            pnl=self.pnl
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "exchange": self.exchange.value,
            "order_id": self.order_id,
            "direction": self.direction.value,
            "offset": self.offset.value,
            "price": self.price,
            "volume": self.volume,
            "trade_time": self.trade_time.isoformat(),
            "gateway_name": self.gateway_name,
            "commission": self.commission,
            "pnl": self.pnl
        }


class VnpySimulatedPosition:
    """兼容vnpy的模拟持仓"""
    def __init__(self, 
                 symbol: str,             # 合约代码
                 exchange: Exchange       # 交易所
                 ):
        self.symbol = symbol
        self.exchange = exchange
        self.volume = 0.0          # 持仓数量
        self.frozen = 0.0          # 冻结数量
        self.avg_price = 0.0       # 持仓均价
        self.pnl = 0.0             # 持仓盈亏
        self.position_id = f"{symbol}_{exchange}"

    def to_position_data(self) -> PositionData:
        """转换为vnpy的PositionData"""
        return PositionData(
            symbol=self.symbol,
            exchange=self.exchange,
            volume=self.volume,
            frozen=self.frozen,
            avg_price=self.avg_price,
            pnl=self.pnl,
            position_id=self.position_id,
            gateway_name="SIMULATOR"
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "exchange": self.exchange.value,
            "volume": self.volume,
            "frozen": self.frozen,
            "avg_price": self.avg_price,
            "pnl": self.pnl,
            "position_id": self.position_id
        }


class VnpySimulatedAccount:
    """兼容vnpy的模拟账户"""
    def __init__(self, 
                 initial_balance: float = 100000.0,  # 初始资金
                 account_id: str = "SIMULATOR"         # 账户ID
                 ):
        self.account_id = account_id
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.available = initial_balance
        self.frozen = 0.0
        self.total = initial_balance
        self.pnl = 0.0
        self.commission = 0.0

    def to_account_data(self) -> AccountData:
        """转换为vnpy的AccountData"""
        return AccountData(
            account_id=self.account_id,
            balance=self.balance,
            frozen=self.frozen,
            available=self.available,
            gateway_name="SIMULATOR"
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "account_id": self.account_id,
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "available": self.available,
            "frozen": self.frozen,
            "total": self.total,
            "pnl": self.pnl,
            "commission": self.commission
        }


class VnpyTradingSimulator:
    """基于vnpy的交易模拟器"""
    
    def __init__(self, 
                 initial_balance: float = 100000.0  # 初始资金
                 ):
        self.account = VnpySimulatedAccount(initial_balance)
        self.positions: Dict[str, VnpySimulatedPosition] = {}  # key: symbol_exchange
        self.orders: Dict[str, VnpySimulatedOrder] = {}  # key: order_id
        self.trades: List[VnpySimulatedTrade] = []
        self.symbol_prices: Dict[str, float] = {}  # 当前模拟价格，key: symbol
        self.symbol_info: Dict[str, Dict] = {}  # 合约信息

    def set_symbol_price(self, 
                        symbol: str,     # 合约代码
                        price: float     # 当前价格
                        ):
        """设置合约当前价格"""
        self.symbol_prices[symbol] = price

    def get_position(self, 
                    symbol: str,                         # 合约代码
                    exchange: Exchange = Exchange.SHFE    # 交易所
                    ) -> VnpySimulatedPosition:
        """获取持仓"""
        position_key = f"{symbol}_{exchange.value}"
        if position_key not in self.positions:
            self.positions[position_key] = VnpySimulatedPosition(symbol, exchange)
        return self.positions[position_key]

    def submit_order(self, 
                    symbol: str,         # 合约代码
                    exchange: Exchange,  # 交易所
                    direction: Direction,    # 交易方向
                    offset: Offset,          # 开平方向
                    price: float,            # 委托价格
                    volume: float,           # 委托数量
                    order_type: OrderType = OrderType.LIMIT  # 订单类型
                    ) -> Tuple[str, Optional[str]]:
        """提交订单"""
        order_id = str(uuid.uuid4())
        order = VnpySimulatedOrder(
            order_id=order_id,
            symbol=symbol,
            exchange=exchange,
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            order_type=order_type
        )
        
        # 检查资金是否足够（仅对买入/开仓）
        if direction == Direction.LONG and offset == Offset.OPEN:
            cost = price * volume
            if cost > self.account.available:
                return order_id, f"资金不足：需要 {cost}，可用 {self.account.available}"
            
            # 冻结资金
            self.account.available -= cost
            self.account.frozen += cost
        
        # 检查持仓是否足够（仅对卖出/平仓）
        elif direction == Direction.SHORT and offset == Offset.CLOSE:
            position = self.get_position(symbol, exchange)
            if position.volume < volume:
                return order_id, f"持仓不足：需要 {volume}，可用 {position.volume}"
        
        # 模拟成交
        trade_id = str(uuid.uuid4())
        
        # 计算佣金和盈亏
        commission = price * volume * 0.0001  # 假设佣金率为0.01%
        pnl = 0.0
        
        # 更新持仓和资金
        if direction == Direction.LONG:
            if offset == Offset.OPEN:
                # 买入开仓
                position = self.get_position(symbol, exchange)
                if position.volume == 0:
                    position.avg_price = price
                else:
                    total_cost = position.avg_price * position.volume + price * volume
                    position.volume += volume
                    position.avg_price = total_cost / position.volume
            else:
                # 买入平仓（做空平仓）
                position = self.get_position(symbol, exchange)
                if position.volume > 0:
                    pnl = (price - position.avg_price) * volume
                    position.volume -= volume
                    if position.volume == 0:
                        position.avg_price = 0.0
        
        elif direction == Direction.SHORT:
            if offset == Offset.OPEN:
                # 卖出开仓
                position = self.get_position(symbol, exchange)
                if position.volume == 0:
                    position.avg_price = price
                else:
                    total_cost = position.avg_price * position.volume + price * volume
                    position.volume += volume
                    position.avg_price = total_cost / position.volume
            else:
                # 卖出平仓（做多平仓）
                position = self.get_position(symbol, exchange)
                if position.volume > 0:
                    pnl = (position.avg_price - price) * volume
                    position.volume -= volume
                    if position.volume == 0:
                        position.avg_price = 0.0
        
        # 创建成交记录
        trade = VnpySimulatedTrade(
            trade_id=trade_id,
            symbol=symbol,
            exchange=exchange,
            order_id=order_id,
            direction=direction,
            offset=offset,
            price=price,
            volume=volume,
            commission=commission,
            pnl=pnl
        )
        
        # 更新资金
        if direction == Direction.LONG and offset == Offset.OPEN:
            # 释放冻结资金
            self.account.frozen -= price * volume
        elif direction == Direction.SHORT and offset == Offset.CLOSE:
            # 增加可用资金
            self.account.available += price * volume
        
        # 更新账户余额
        self.account.balance += pnl - commission
        self.account.available = self.account.balance - self.account.frozen
        self.account.total = self.account.balance
        self.account.pnl = self.account.balance - self.account.initial_balance
        self.account.commission += commission
        
        # 更新订单状态
        order.traded_volume = volume
        order.status = Status.ALLTRADED
        
        # 记录
        self.orders[order_id] = order
        self.trades.append(trade)
        
        return order_id, None

    def cancel_order(self, 
                    order_id: str  # 订单ID
                    ) -> bool:
        """撤单"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        if order.status != Status.SUBMITTING and order.status != Status.ACTIVE:
            return False
        
        # 释放冻结资金
        if order.direction == Direction.LONG and order.offset == Offset.OPEN:
            cost = order.price * order.volume
            self.account.frozen -= cost
            self.account.available += cost
        
        order.status = Status.CANCELLED
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

    def get_order_data(self, 
                      order_id: str  # 订单ID
                      ) -> Optional[OrderData]:
        """获取订单数据"""
        if order_id in self.orders:
            return self.orders[order_id].to_order_data()
        return None

    def get_trade_data(self, 
                      trade_id: str  # 成交ID
                      ) -> Optional[TradeData]:
        """获取成交数据"""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                return trade.to_trade_data()
        return None

    def get_position_data(self, 
                         symbol: str,                         # 合约代码
                         exchange: Exchange = Exchange.SHFE    # 交易所
                         ) -> PositionData:
        """获取持仓数据"""
        position = self.get_position(symbol, exchange)
        return position.to_position_data()

    def get_account_data(self) -> AccountData:
        """获取账户数据"""
        return self.account.to_account_data()

    def update_tick(self, 
                   tick: TickData  # 行情数据
                   ):
        """更新行情"""
        self.set_symbol_price(tick.symbol, tick.last_price)

    def update_bar(self, 
                  bar: BarData  # K线数据
                  ):
        """更新K线"""
        self.set_symbol_price(bar.symbol, bar.close_price)

    def reset(self, 
             initial_balance: float = None  # 初始资金
             ):
        """重置模拟器"""
        if initial_balance is None:
            initial_balance = self.account.initial_balance
        
        self.account = VnpySimulatedAccount(initial_balance)
        self.positions = {}
        self.orders = {}
        self.trades = []
        self.symbol_prices = {}

    def calculate_commission(self, 
                           symbol: str,         # 合约代码
                           price: float,        # 价格
                           volume: float,       # 数量
                           direction: Direction,    # 交易方向
                           offset: Offset          # 开平方向
                           ) -> float:
        """计算佣金"""
        # 这里可以根据不同合约设置不同的佣金率
        commission_rate = 0.0001  # 0.01%
        return price * volume * commission_rate

    def calculate_pnl(self, 
                     symbol: str,         # 合约代码
                     price: float,        # 价格
                     volume: float,       # 数量
                     direction: Direction,    # 交易方向
                     offset: Offset,          # 开平方向
                     exchange: Exchange = Exchange.SHFE    # 交易所
                     ) -> float:
        """计算盈亏"""
        if offset == Offset.OPEN:
            return 0.0
        
        position = self.get_position(symbol, exchange)
        if position.volume == 0:
            return 0.0
        
        if direction == Direction.LONG:
            # 买入平仓（做空平仓）
            return (price - position.avg_price) * volume
        else:
            # 卖出平仓（做多平仓）
            return (position.avg_price - price) * volume
