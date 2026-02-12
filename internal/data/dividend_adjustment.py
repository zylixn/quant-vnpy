"""
分红除权处理模块

处理股票分红、送股、配股等事件，提供复权计算功能
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval


class DividendEvent:
    """分红除权事件"""
    
    def __init__(self, 
                 date: datetime, 
                 dividend: float = 0.0,  # 每股分红金额
                 bonus_share: float = 0.0,  # 每股送股数量
                 rights_share: float = 0.0,  # 每股配股数量
                 rights_price: float = 0.0,  # 配股价
                 symbol: str = ""):
        """初始化分红除权事件
        
        Args:
            date: 除权除息日
            dividend: 每股分红金额
            bonus_share: 每股送股数量
            rights_share: 每股配股数量
            rights_price: 配股价
            symbol: 股票代码
        """
        self.date = date
        self.dividend = dividend
        self.bonus_share = bonus_share
        self.rights_share = rights_share
        self.rights_price = rights_price
        self.symbol = symbol
        
    def get_adjustment_factor(self) -> float:
        """计算除权除息调整因子
        
        Returns:
            调整因子，用于价格复权
        """
        # 计算除权除息前的总股本
        old_share = 1.0
        
        # 计算除权除息后的总股本
        new_share = old_share + self.bonus_share + self.rights_share
        
        # 计算除权除息前的总市值
        old_value = old_share * 100  # 假设除权前价格为100
        
        # 计算除权除息后的总市值
        new_value = old_value - self.dividend + self.rights_share * self.rights_price
        
        # 计算调整因子
        if new_share > 0 and new_value > 0:
            return (new_value / new_share) / (old_value / old_share)
        return 1.0
    
    def to_dict(self) -> Dict:
        """转换为字典
        
        Returns:
            包含事件信息的字典
        """
        return {
            "date": self.date.isoformat(),
            "dividend": self.dividend,
            "bonus_share": self.bonus_share,
            "rights_share": self.rights_share,
            "rights_price": self.rights_price,
            "symbol": self.symbol
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DividendEvent':
        """从字典创建事件
        
        Args:
            data: 包含事件信息的字典
            
        Returns:
            DividendEvent实例
        """
        return cls(
            date=datetime.fromisoformat(data["date"]),
            dividend=data.get("dividend", 0.0),
            bonus_share=data.get("bonus_share", 0.0),
            rights_share=data.get("rights_share", 0.0),
            rights_price=data.get("rights_price", 0.0),
            symbol=data.get("symbol", "")
        )


class DividendAdjuster:
    """分红除权调整器"""
    
    def __init__(self):
        """初始化分红除权调整器"""
        self.dividend_events = []
    
    def add_event(self, event: DividendEvent):
        """添加分红除权事件
        
        Args:
            event: 分红除权事件
        """
        self.dividend_events.append(event)
        # 按日期排序
        self.dividend_events.sort(key=lambda x: x.date)
    
    def add_events(self, events: List[DividendEvent]):
        """批量添加分红除权事件
        
        Args:
            events: 分红除权事件列表
        """
        for event in events:
            self.add_event(event)
    
    def get_events(self, symbol: str = "") -> List[DividendEvent]:
        """获取分红除权事件
        
        Args:
            symbol: 股票代码，空字符串表示所有股票
            
        Returns:
            分红除权事件列表
        """
        if symbol:
            return [event for event in self.dividend_events if event.symbol == symbol]
        return self.dividend_events
    
    def adjust_prices(self, 
                      bars: List[BarData], 
                      adjust_type: str = "forward",  # forward: 前复权, backward: 后复权, none: 不复权
                      symbol: str = "") -> List[BarData]:
        """对价格进行复权处理
        
        Args:
            bars: K线数据列表
            adjust_type: 复权类型
            symbol: 股票代码
            
        Returns:
            复权后的K线数据列表
        """
        if not bars:
            return []
        
        # 按日期排序
        sorted_bars = sorted(bars, key=lambda x: x.datetime)
        
        # 获取相关的分红除权事件
        relevant_events = self.get_events(symbol)
        if not relevant_events:
            return sorted_bars
        
        # 转换为DataFrame以便处理
        bar_data = []
        for bar in sorted_bars:
            bar_data.append({
                "datetime": bar.datetime,
                "open": bar.open_price,
                "high": bar.high_price,
                "low": bar.low_price,
                "close": bar.close_price,
                "volume": bar.volume,
                "open_interest": bar.open_interest,
                "symbol": bar.symbol,
                "exchange": bar.exchange,
                "interval": bar.interval,
                "gateway_name": bar.gateway_name
            })
        
        df = pd.DataFrame(bar_data)
        
        # 计算复权因子
        if adjust_type == "forward":
            df = self._calculate_forward_adjustment(df, relevant_events)
        elif adjust_type == "backward":
            df = self._calculate_backward_adjustment(df, relevant_events)
        # none类型不需要调整
        
        # 转换回BarData
        adjusted_bars = []
        for _, row in df.iterrows():
            bar = BarData(
                symbol=row["symbol"],
                exchange=row["exchange"],
                datetime=row["datetime"],
                interval=row["interval"],
                open_price=row["open"],
                high_price=row["high"],
                low_price=row["low"],
                close_price=row["close"],
                volume=row["volume"],
                open_interest=row["open_interest"],
                gateway_name=row["gateway_name"]
            )
            adjusted_bars.append(bar)
        
        return adjusted_bars
    
    def _calculate_forward_adjustment(self, df: pd.DataFrame, events: List[DividendEvent]) -> pd.DataFrame:
        """计算前复权
        
        Args:
            df: K线数据DataFrame
            events: 分红除权事件列表
            
        Returns:
            前复权后的DataFrame
        """
        # 按日期排序事件
        sorted_events = sorted(events, key=lambda x: x.date, reverse=True)
        
        # 计算累计调整因子
        cum_factor = 1.0
        
        # 从最近的事件开始向前调整
        for event in sorted_events:
            # 找到事件日期之前的数据
            mask = df["datetime"] < event.date
            if mask.any():
                # 计算该事件的调整因子
                factor = event.get_adjustment_factor()
                cum_factor *= factor
                
                # 调整价格
                price_columns = ["open", "high", "low", "close"]
                for col in price_columns:
                    df.loc[mask, col] *= cum_factor
        
        return df
    
    def _calculate_backward_adjustment(self, df: pd.DataFrame, events: List[DividendEvent]) -> pd.DataFrame:
        """计算后复权
        
        Args:
            df: K线数据DataFrame
            events: 分红除权事件列表
            
        Returns:
            后复权后的DataFrame
        """
        # 按日期排序事件
        sorted_events = sorted(events, key=lambda x: x.date)
        
        # 计算累计调整因子
        cum_factor = 1.0
        
        # 从最早的事件开始向后调整
        for event in sorted_events:
            # 找到事件日期之后的数据
            mask = df["datetime"] >= event.date
            if mask.any():
                # 计算该事件的调整因子
                factor = event.get_adjustment_factor()
                cum_factor /= factor  # 后复权需要除以调整因子
                
                # 调整价格
                price_columns = ["open", "high", "low", "close"]
                for col in price_columns:
                    df.loc[mask, col] *= cum_factor
        
        return df
    
    def get_adjusted_price(self, 
                          price: float, 
                          date: datetime, 
                          adjust_type: str = "forward",
                          symbol: str = "") -> float:
        """获取指定日期的复权价格
        
        Args:
            price: 原始价格
            date: 日期
            adjust_type: 复权类型
            symbol: 股票代码
            
        Returns:
            复权后的价格
        """
        # 获取相关的分红除权事件
        relevant_events = self.get_events(symbol)
        if not relevant_events:
            return price
        
        adjusted_price = price
        
        if adjust_type == "forward":
            # 前复权：应用日期之后的所有调整因子
            future_events = [event for event in relevant_events if event.date > date]
            for event in sorted(future_events, key=lambda x: x.date):
                factor = event.get_adjustment_factor()
                adjusted_price *= factor
        
        elif adjust_type == "backward":
            # 后复权：应用日期之前的所有调整因子
            past_events = [event for event in relevant_events if event.date <= date]
            for event in sorted(past_events, key=lambda x: x.date):
                factor = event.get_adjustment_factor()
                adjusted_price /= factor
        
        return adjusted_price


class StockDataProcessor:
    """股票数据处理器"""
    
    def __init__(self):
        """初始化股票数据处理器"""
        self.dividend_adjuster = DividendAdjuster()
    
    def process_stock_data(self, 
                          bars: List[BarData], 
                          adjust_type: str = "forward",
                          symbol: str = "",
                          clean_data: bool = True) -> List[BarData]:
        """处理股票数据
        
        Args:
            bars: K线数据列表
            adjust_type: 复权类型
            symbol: 股票代码
            clean_data: 是否清洗数据
            
        Returns:
            处理后的K线数据列表
        """
        if not bars:
            return []
        
        # 清洗数据
        if clean_data:
            bars = self._clean_data(bars)
        
        # 复权处理
        if adjust_type in ["forward", "backward"]:
            bars = self.dividend_adjuster.adjust_prices(bars, adjust_type, symbol)
        
        return bars
    
    def _clean_data(self, bars: List[BarData]) -> List[BarData]:
        """清洗数据
        
        Args:
            bars: K线数据列表
            
        Returns:
            清洗后的K线数据列表
        """
        if not bars:
            return []
        
        # 按日期排序
        sorted_bars = sorted(bars, key=lambda x: x.datetime)
        
        # 移除重复数据
        unique_bars = []
        seen_dates = set()
        for bar in sorted_bars:
            date_key = bar.datetime.strftime("%Y-%m-%d %H:%M:%S")
            if date_key not in seen_dates:
                seen_dates.add(date_key)
                unique_bars.append(bar)
        
        return unique_bars
    
    def add_dividend_event(self, event: DividendEvent):
        """添加分红除权事件
        
        Args:
            event: 分红除权事件
        """
        self.dividend_adjuster.add_event(event)
    
    def load_dividend_events(self, events: List[Dict]):
        """加载分红除权事件
        
        Args:
            events: 分红除权事件字典列表
        """
        for event_data in events:
            event = DividendEvent.from_dict(event_data)
            self.add_dividend_event(event)


# 全局实例
global_dividend_adjuster = DividendAdjuster()
global_stock_processor = StockDataProcessor()

def get_dividend_adjuster() -> DividendAdjuster:
    """获取分红除权调整器实例
    
    Returns:
        分红除权调整器实例
    """
    return global_dividend_adjuster

def get_stock_processor() -> StockDataProcessor:
    """获取股票数据处理器实例
    
    Returns:
        股票数据处理器实例
    """
    return global_stock_processor