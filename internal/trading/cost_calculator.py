"""
交易成本计算模块

计算股票交易的各种成本，包括印花税、佣金、过户费等
"""

from typing import Dict, Optional, Tuple
from vnpy.trader.constant import Direction, Offset, Exchange


class TradingCostConfig:
    """交易成本配置"""
    
    def __init__(self, 
                 commission_rate: float = 0.0003,  # 佣金率
                 min_commission: float = 5.0,  # 最低佣金
                 stamp_tax_rate: float = 0.001,  # 印花税率
                 transfer_fee_rate: float = 0.00002,  # 过户费率
                 min_transfer_fee: float = 0.0,  # 最低过户费
                 jing_shou_fee_rate: float = 0.0000487,  # 经手费率
                 supervision_fee_rate: float = 0.00002,  # 证管费率
                 other_fees: float = 0.0):  # 其他费用
        """初始化交易成本配置
        
        Args:
            commission_rate: 佣金率
            min_commission: 最低佣金
            stamp_tax_rate: 印花税率（卖出时收取）
            transfer_fee_rate: 过户费率（上海股票收取）
            min_transfer_fee: 最低过户费
            jing_shou_fee_rate: 经手费率
            supervision_fee_rate: 证管费率
            other_fees: 其他固定费用
        """
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.stamp_tax_rate = stamp_tax_rate
        self.transfer_fee_rate = transfer_fee_rate
        self.min_transfer_fee = min_transfer_fee
        self.jing_shou_fee_rate = jing_shou_fee_rate
        self.supervision_fee_rate = supervision_fee_rate
        self.other_fees = other_fees
    
    def to_dict(self) -> Dict:
        """转换为字典
        
        Returns:
            配置字典
        """
        return {
            "commission_rate": self.commission_rate,
            "min_commission": self.min_commission,
            "stamp_tax_rate": self.stamp_tax_rate,
            "transfer_fee_rate": self.transfer_fee_rate,
            "min_transfer_fee": self.min_transfer_fee,
            "jing_shou_fee_rate": self.jing_shou_fee_rate,
            "supervision_fee_rate": self.supervision_fee_rate,
            "other_fees": self.other_fees
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TradingCostConfig':
        """从字典创建配置
        
        Args:
            data: 配置字典
            
        Returns:
            TradingCostConfig实例
        """
        return cls(
            commission_rate=data.get("commission_rate", 0.0003),
            min_commission=data.get("min_commission", 5.0),
            stamp_tax_rate=data.get("stamp_tax_rate", 0.001),
            transfer_fee_rate=data.get("transfer_fee_rate", 0.00002),
            min_transfer_fee=data.get("min_transfer_fee", 0.0),
            jing_shou_fee_rate=data.get("jing_shou_fee_rate", 0.0000487),
            supervision_fee_rate=data.get("supervision_fee_rate", 0.00002),
            other_fees=data.get("other_fees", 0.0)
        )


class StockTradingCostCalculator:
    """股票交易成本计算器"""
    
    def __init__(self, config: Optional[TradingCostConfig] = None):
        """初始化交易成本计算器
        
        Args:
            config: 交易成本配置
        """
        self.config = config or TradingCostConfig()
    
    def calculate_cost(self, 
                      price: float, 
                      volume: int, 
                      direction: Direction, 
                      offset: Offset, 
                      exchange: Exchange) -> Dict:
        """计算交易成本
        
        Args:
            price: 交易价格
            volume: 交易数量
            direction: 交易方向
            offset: 开平方向
            exchange: 交易所
            
        Returns:
            包含各项成本的字典
        """
        # 计算交易金额
        amount = price * volume
        
        # 计算佣金
        commission = self._calculate_commission(amount)
        
        # 计算印花税（卖出时收取）
        stamp_tax = self._calculate_stamp_tax(amount, direction)
        
        # 计算过户费（上海股票收取）
        transfer_fee = self._calculate_transfer_fee(amount, exchange)
        
        # 计算经手费
        jing_shou_fee = self._calculate_jing_shou_fee(amount)
        
        # 计算证管费
        supervision_fee = self._calculate_supervision_fee(amount)
        
        # 其他费用
        other_fees = self.config.other_fees
        
        # 计算总成本
        total_cost = commission + stamp_tax + transfer_fee + jing_shou_fee + supervision_fee + other_fees
        
        return {
            "amount": amount,
            "commission": commission,
            "stamp_tax": stamp_tax,
            "transfer_fee": transfer_fee,
            "jing_shou_fee": jing_shou_fee,
            "supervision_fee": supervision_fee,
            "other_fees": other_fees,
            "total_cost": total_cost,
            "cost_rate": total_cost / amount if amount > 0 else 0.0
        }
    
    def _calculate_commission(self, amount: float) -> float:
        """计算佣金
        
        Args:
            amount: 交易金额
            
        Returns:
            佣金金额
        """
        commission = amount * self.config.commission_rate
        return max(commission, self.config.min_commission)
    
    def _calculate_stamp_tax(self, amount: float, direction: Direction) -> float:
        """计算印花税
        
        Args:
            amount: 交易金额
            direction: 交易方向
            
        Returns:
            印花税金额
        """
        # 只有卖出时收取印花税
        if direction == Direction.SHORT:
            return amount * self.config.stamp_tax_rate
        return 0.0
    
    def _calculate_transfer_fee(self, amount: float, exchange: Exchange) -> float:
        """计算过户费
        
        Args:
            amount: 交易金额
            exchange: 交易所
            
        Returns:
            过户费金额
        """
        # 只有上海股票收取过户费
        if exchange in [Exchange.SSE, Exchange.SHFE, Exchange.INE]:
            transfer_fee = amount * self.config.transfer_fee_rate
            return max(transfer_fee, self.config.min_transfer_fee)
        return 0.0
    
    def _calculate_jing_shou_fee(self, amount: float) -> float:
        """计算经手费
        
        Args:
            amount: 交易金额
            
        Returns:
            经手费金额
        """
        return amount * self.config.jing_shou_fee_rate
    
    def _calculate_supervision_fee(self, amount: float) -> float:
        """计算证管费
        
        Args:
            amount: 交易金额
            
        Returns:
            证管费金额
        """
        return amount * self.config.supervision_fee_rate
    
    def calculate_round_trip_cost(self, 
                                price: float, 
                                volume: int, 
                                exchange: Exchange) -> Dict:
        """计算往返交易成本（买入+卖出）
        
        Args:
            price: 交易价格
            volume: 交易数量
            exchange: 交易所
            
        Returns:
            包含各项成本的字典
        """
        # 计算买入成本
        buy_cost = self.calculate_cost(price, volume, Direction.LONG, Offset.OPEN, exchange)
        
        # 计算卖出成本
        sell_cost = self.calculate_cost(price, volume, Direction.SHORT, Offset.CLOSE, exchange)
        
        # 计算总成本
        total_cost = buy_cost["total_cost"] + sell_cost["total_cost"]
        total_amount = buy_cost["amount"]
        
        return {
            "buy_cost": buy_cost,
            "sell_cost": sell_cost,
            "total_cost": total_cost,
            "total_amount": total_amount,
            "round_trip_cost_rate": total_cost / total_amount if total_amount > 0 else 0.0
        }
    
    def get_breakeven_price(self, 
                           buy_price: float, 
                           volume: int, 
                           exchange: Exchange) -> float:
        """计算保本价格
        
        Args:
            buy_price: 买入价格
            volume: 交易数量
            exchange: 交易所
            
        Returns:
            保本价格
        """
        # 计算买入成本
        buy_cost = self.calculate_cost(buy_price, volume, Direction.LONG, Offset.OPEN, exchange)
        
        # 计算保本价格
        # 买入成本 + 卖出成本 = (sell_price - buy_price) * volume
        # 简化计算：假设卖出价格为 x，则：
        # buy_cost + x * volume * 成本率 = (x - buy_price) * volume
        
        # 精确计算
        def calculate_sell_cost(sell_price):
            return self.calculate_cost(sell_price, volume, Direction.SHORT, Offset.CLOSE, exchange)["total_cost"]
        
        # 使用二分法计算保本价格
        low = buy_price
        high = buy_price * 1.1  # 初始上限为买入价格的110%
        
        for _ in range(100):
            mid = (low + high) / 2
            total_cost = buy_cost["total_cost"] + calculate_sell_cost(mid)
            profit = (mid - buy_price) * volume
            
            if abs(profit - total_cost) < 0.01:
                return mid
            elif profit < total_cost:
                low = mid
            else:
                high = mid
        
        return high
    
    def update_config(self, config: TradingCostConfig):
        """更新配置
        
        Args:
            config: 新的交易成本配置
        """
        self.config = config
    
    def get_config(self) -> TradingCostConfig:
        """获取配置
        
        Returns:
            交易成本配置
        """
        return self.config


class BrokerCostConfig:
    """券商成本配置"""
    
    # 主流券商的默认配置
    BROKER_CONFIGS = {
        "华泰证券": TradingCostConfig(
            commission_rate=0.00025,
            min_commission=5.0,
            stamp_tax_rate=0.001,
            transfer_fee_rate=0.00002,
            min_transfer_fee=0.0,
            jing_shou_fee_rate=0.0000487,
            supervision_fee_rate=0.00002,
            other_fees=0.0
        ),
        "国泰君安": TradingCostConfig(
            commission_rate=0.00025,
            min_commission=5.0,
            stamp_tax_rate=0.001,
            transfer_fee_rate=0.00002,
            min_transfer_fee=0.0,
            jing_shou_fee_rate=0.0000487,
            supervision_fee_rate=0.00002,
            other_fees=0.0
        ),
        "中信证券": TradingCostConfig(
            commission_rate=0.0003,
            min_commission=5.0,
            stamp_tax_rate=0.001,
            transfer_fee_rate=0.00002,
            min_transfer_fee=0.0,
            jing_shou_fee_rate=0.0000487,
            supervision_fee_rate=0.00002,
            other_fees=0.0
        ),
        "海通证券": TradingCostConfig(
            commission_rate=0.00025,
            min_commission=5.0,
            stamp_tax_rate=0.001,
            transfer_fee_rate=0.00002,
            min_transfer_fee=0.0,
            jing_shou_fee_rate=0.0000487,
            supervision_fee_rate=0.00002,
            other_fees=0.0
        ),
        "招商证券": TradingCostConfig(
            commission_rate=0.00025,
            min_commission=5.0,
            stamp_tax_rate=0.001,
            transfer_fee_rate=0.00002,
            min_transfer_fee=0.0,
            jing_shou_fee_rate=0.0000487,
            supervision_fee_rate=0.00002,
            other_fees=0.0
        )
    }
    
    @classmethod
    def get_broker_config(cls, broker_name: str) -> TradingCostConfig:
        """获取券商配置
        
        Args:
            broker_name: 券商名称
            
        Returns:
            交易成本配置
        """
        return cls.BROKER_CONFIGS.get(broker_name, TradingCostConfig())


# 全局实例
global_cost_calculator = StockTradingCostCalculator()

def get_cost_calculator() -> StockTradingCostCalculator:
    """获取交易成本计算器实例
    
    Returns:
        交易成本计算器实例
    """
    return global_cost_calculator


def get_stock_trading_cost_calculator() -> StockTradingCostCalculator:
    """获取股票交易成本计算器实例
    
    Returns:
        交易成本计算器实例
    """
    return global_cost_calculator


def create_broker_cost_calculator(broker_name: str) -> StockTradingCostCalculator:
    """创建券商专用的成本计算器
    
    Args:
        broker_name: 券商名称
        
    Returns:
        交易成本计算器实例
    """
    config = BrokerCostConfig.get_broker_config(broker_name)
    return StockTradingCostCalculator(config)