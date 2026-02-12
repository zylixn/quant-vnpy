"""
股票交易时间管理模块

管理股票交易时间、节假日、停牌等特殊情况
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Set
import json
import os


class TradingTimeConfig:
    """交易时间配置"""
    
    # A股交易时间
    A_SHARE_TRADING_HOURS = {
        "morning_open": time(9, 30),
        "morning_close": time(11, 30),
        "afternoon_open": time(13, 0),
        "afternoon_close": time(15, 0)
    }
    
    # 港股交易时间
    HK_SHARE_TRADING_HOURS = {
        "morning_open": time(9, 30),
        "morning_close": time(12, 0),
        "afternoon_open": time(13, 0),
        "afternoon_close": time(16, 0)
    }
    
    # 美股交易时间（夏令时）
    US_SHARE_TRADING_HOURS_DST = {
        "open": time(21, 30),  # 北京时间
        "close": time(4, 0)     # 次日北京时间
    }
    
    # 美股交易时间（冬令时）
    US_SHARE_TRADING_HOURS_WINTER = {
        "open": time(22, 30),  # 北京时间
        "close": time(5, 0)     # 次日北京时间
    }
    
    @classmethod
    def get_trading_hours(cls, market: str = "A_SHARE") -> Dict[str, time]:
        """获取交易时间
        
        Args:
            market: 市场类型
            
        Returns:
            交易时间配置
        """
        market_mapping = {
            "A_SHARE": cls.A_SHARE_TRADING_HOURS,
            "HK_SHARE": cls.HK_SHARE_TRADING_HOURS,
            "US_SHARE_DST": cls.US_SHARE_TRADING_HOURS_DST,
            "US_SHARE_WINTER": cls.US_SHARE_TRADING_HOURS_WINTER
        }
        return market_mapping.get(market, cls.A_SHARE_TRADING_HOURS)


class HolidayManager:
    """节假日管理器"""
    
    def __init__(self, holiday_file: Optional[str] = None):
        """初始化节假日管理器
        
        Args:
            holiday_file: 节假日文件路径
        """
        self.holidays: Set[str] = set()
        self.workdays: Set[str] = set()  # 补班日
        
        if holiday_file and os.path.exists(holiday_file):
            self.load_holidays(holiday_file)
        else:
            # 加载默认节假日
            self._load_default_holidays()
    
    def load_holidays(self, file_path: str):
        """从文件加载节假日
        
        Args:
            file_path: 节假日文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.holidays = set(data.get("holidays", []))
                self.workdays = set(data.get("workdays", []))
        except Exception as e:
            print(f"Load holidays error: {e}")
    
    def save_holidays(self, file_path: str):
        """保存节假日到文件
        
        Args:
            file_path: 节假日文件路径
        """
        data = {
            "holidays": list(self.holidays),
            "workdays": list(self.workdays)
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save holidays error: {e}")
    
    def add_holiday(self, date: str):
        """添加节假日
        
        Args:
            date: 节假日日期，格式：YYYY-MM-DD
        """
        self.holidays.add(date)
    
    def remove_holiday(self, date: str):
        """移除节假日
        
        Args:
            date: 节假日日期，格式：YYYY-MM-DD
        """
        if date in self.holidays:
            self.holidays.remove(date)
    
    def add_workday(self, date: str):
        """添加补班日
        
        Args:
            date: 补班日日期，格式：YYYY-MM-DD
        """
        self.workdays.add(date)
    
    def remove_workday(self, date: str):
        """移除补班日
        
        Args:
            date: 补班日日期，格式：YYYY-MM-DD
        """
        if date in self.workdays:
            self.workdays.remove(date)
    
    def is_holiday(self, date: datetime) -> bool:
        """判断是否为节假日
        
        Args:
            date: 日期
            
        Returns:
            是否为节假日
        """
        date_str = date.strftime("%Y-%m-%d")
        return date_str in self.holidays
    
    def is_workday(self, date: datetime) -> bool:
        """判断是否为工作日
        
        Args:
            date: 日期
            
        Returns:
            是否为工作日
        """
        # 检查是否为补班日
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self.workdays:
            return True
        
        # 检查是否为周末
        if date.weekday() >= 5:  # 周六、周日
            return False
        
        # 检查是否为节假日
        return not self.is_holiday(date)
    
    def _load_default_holidays(self):
        """加载默认节假日"""
        # 2024年节假日
        default_holidays = [
            "2024-01-01",  # 元旦
            "2024-02-10", "2024-02-11", "2024-02-12", "2024-02-13", "2024-02-14",  # 春节
            "2024-04-04", "2024-04-05",  # 清明节
            "2024-05-01", "2024-05-02", "2024-05-03",  # 劳动节
            "2024-06-10",  # 端午节
            "2024-09-17", "2024-09-18", "2024-09-19", "2024-09-20", "2024-09-21",  # 中秋节
            "2024-10-01", "2024-10-02", "2024-10-03", "2024-10-04", "2024-10-05", "2024-10-06", "2024-10-07"  # 国庆节
        ]
        
        # 2024年补班日
        default_workdays = [
            "2024-02-03", "2024-02-17",  # 春节补班
            "2024-04-06",  # 清明节补班
            "2024-05-11",  # 劳动节补班
            "2024-09-22",  # 中秋节补班
            "2024-10-12"   # 国庆节补班
        ]
        
        for holiday in default_holidays:
            self.add_holiday(holiday)
        
        for workday in default_workdays:
            self.add_workday(workday)


class TradingTimeManager:
    """交易时间管理器"""
    
    def __init__(self, holiday_manager: Optional[HolidayManager] = None):
        """初始化交易时间管理器
        
        Args:
            holiday_manager: 节假日管理器
        """
        self.holiday_manager = holiday_manager or HolidayManager()
        self.suspended_stocks: Set[str] = set()  # 停牌股票
        self.special_trading_days: Dict[str, Dict] = {}  # 特殊交易日
    
    def is_trading_day(self, date: datetime, market: str = "A_SHARE") -> bool:
        """判断是否为交易日
        
        Args:
            date: 日期
            market: 市场类型
            
        Returns:
            是否为交易日
        """
        # 检查特殊交易日
        date_str = date.strftime("%Y-%m-%d")
        if date_str in self.special_trading_days:
            return self.special_trading_days[date_str].get("is_trading", False)
        
        # 检查是否为工作日
        return self.holiday_manager.is_workday(date)
    
    def is_trading_time(self, dt: datetime, market: str = "A_SHARE") -> bool:
        """判断是否为交易时间
        
        Args:
            dt: 日期时间
            market: 市场类型
            
        Returns:
            是否为交易时间
        """
        # 首先判断是否为交易日
        if not self.is_trading_day(dt, market):
            return False
        
        # 获取交易时间配置
        trading_hours = TradingTimeConfig.get_trading_hours(market)
        
        # 检查是否在交易时间内
        current_time = dt.time()
        
        if market == "A_SHARE":
            # A股交易时间
            morning_open = trading_hours["morning_open"]
            morning_close = trading_hours["morning_close"]
            afternoon_open = trading_hours["afternoon_open"]
            afternoon_close = trading_hours["afternoon_close"]
            
            # 上午交易时间
            if morning_open <= current_time <= morning_close:
                return True
            
            # 下午交易时间
            if afternoon_open <= current_time <= afternoon_close:
                return True
                
        elif market == "HK_SHARE":
            # 港股交易时间
            morning_open = trading_hours["morning_open"]
            morning_close = trading_hours["morning_close"]
            afternoon_open = trading_hours["afternoon_open"]
            afternoon_close = trading_hours["afternoon_close"]
            
            # 上午交易时间
            if morning_open <= current_time <= morning_close:
                return True
            
            # 下午交易时间
            if afternoon_open <= current_time <= afternoon_close:
                return True
                
        elif market in ["US_SHARE_DST", "US_SHARE_WINTER"]:
            # 美股交易时间
            open_time = trading_hours["open"]
            close_time = trading_hours["close"]
            
            # 跨日交易
            if open_time > close_time:
                # 开盘时间在当日，收盘时间在次日
                if current_time >= open_time or current_time <= close_time:
                    return True
            else:
                # 开盘和收盘都在当日
                if open_time <= current_time <= close_time:
                    return True
        
        return False
    
    def is_pre_trading_time(self, dt: datetime, market: str = "A_SHARE") -> bool:
        """判断是否为集合竞价时间
        
        Args:
            dt: 日期时间
            market: 市场类型
            
        Returns:
            是否为集合竞价时间
        """
        if not self.is_trading_day(dt, market):
            return False
        
        current_time = dt.time()
        
        if market == "A_SHARE":
            # A股集合竞价时间
            # 上午集合竞价：9:15-9:25
            # 下午集合竞价：14:57-15:00
            if time(9, 15) <= current_time <= time(9, 25):
                return True
            if time(14, 57) <= current_time <= time(15, 0):
                return True
        
        return False
    
    def get_next_trading_day(self, date: datetime, market: str = "A_SHARE") -> datetime:
        """获取下一个交易日
        
        Args:
            date: 日期
            market: 市场类型
            
        Returns:
            下一个交易日
        """
        next_day = date + timedelta(days=1)
        
        while not self.is_trading_day(next_day, market):
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_previous_trading_day(self, date: datetime, market: str = "A_SHARE") -> datetime:
        """获取上一个交易日
        
        Args:
            date: 日期
            market: 市场类型
            
        Returns:
            上一个交易日
        """
        prev_day = date - timedelta(days=1)
        
        while not self.is_trading_day(prev_day, market):
            prev_day -= timedelta(days=1)
        
        return prev_day
    
    def get_trading_days_in_range(self, start_date: datetime, end_date: datetime, market: str = "A_SHARE") -> List[datetime]:
        """获取指定范围内的交易日
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            market: 市场类型
            
        Returns:
            交易日列表
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date, market):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def add_suspended_stock(self, symbol: str):
        """添加停牌股票
        
        Args:
            symbol: 股票代码
        """
        self.suspended_stocks.add(symbol)
    
    def remove_suspended_stock(self, symbol: str):
        """移除停牌股票
        
        Args:
            symbol: 股票代码
        """
        if symbol in self.suspended_stocks:
            self.suspended_stocks.remove(symbol)
    
    def is_stock_suspended(self, symbol: str) -> bool:
        """判断股票是否停牌
        
        Args:
            symbol: 股票代码
            
        Returns:
            是否停牌
        """
        return symbol in self.suspended_stocks
    
    def add_special_trading_day(self, date: str, config: Dict):
        """添加特殊交易日
        
        Args:
            date: 日期，格式：YYYY-MM-DD
            config: 特殊交易日配置
        """
        self.special_trading_days[date] = config
    
    def remove_special_trading_day(self, date: str):
        """移除特殊交易日
        
        Args:
            date: 日期，格式：YYYY-MM-DD
        """
        if date in self.special_trading_days:
            del self.special_trading_days[date]
    
    def get_trading_status(self, dt: datetime, symbol: Optional[str] = None, market: str = "A_SHARE") -> Dict:
        """获取交易状态
        
        Args:
            dt: 日期时间
            symbol: 股票代码
            market: 市场类型
            
        Returns:
            交易状态
        """
        status = {
            "is_trading_day": self.is_trading_day(dt, market),
            "is_trading_time": self.is_trading_time(dt, market),
            "is_pre_trading_time": self.is_pre_trading_time(dt, market),
            "market": market,
            "current_time": dt.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if symbol:
            status["is_stock_suspended"] = self.is_stock_suspended(symbol)
        
        return status
    
    def get_next_trading_time(self, dt: datetime, market: str = "A_SHARE") -> datetime:
        """获取下一个交易时间
        
        Args:
            dt: 日期时间
            market: 市场类型
            
        Returns:
            下一个交易时间
        """
        # 检查是否已经在交易时间内
        if self.is_trading_time(dt, market):
            return dt
        
        # 检查是否在交易日内但不在交易时间
        if self.is_trading_day(dt, market):
            trading_hours = TradingTimeConfig.get_trading_hours(market)
            current_time = dt.time()
            
            if market == "A_SHARE":
                # 上午交易时间
                morning_open = trading_hours["morning_open"]
                morning_close = trading_hours["morning_close"]
                afternoon_open = trading_hours["afternoon_open"]
                afternoon_close = trading_hours["afternoon_close"]
                
                if current_time < morning_open:
                    # 当日上午开盘前
                    return datetime.combine(dt.date(), morning_open)
                elif current_time < afternoon_open:
                    # 午间休市
                    return datetime.combine(dt.date(), afternoon_open)
            
        # 下一个交易日
        next_trading_day = self.get_next_trading_day(dt, market)
        trading_hours = TradingTimeConfig.get_trading_hours(market)
        
        if market in ["A_SHARE", "HK_SHARE"]:
            open_time = trading_hours["morning_open"]
        else:
            open_time = trading_hours["open"]
        
        return datetime.combine(next_trading_day.date(), open_time)
    
    def get_market_status(self, market: str = "A_SHARE") -> Dict:
        """获取市场状态
        
        Args:
            market: 市场类型
            
        Returns:
            市场状态
        """
        now = datetime.now()
        return {
            "market": market,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "is_trading_day": self.is_trading_day(now, market),
            "is_trading_time": self.is_trading_time(now, market),
            "is_pre_trading_time": self.is_pre_trading_time(now, market),
            "next_trading_time": self.get_next_trading_time(now, market).strftime("%Y-%m-%d %H:%M:%S"),
            "suspended_stock_count": len(self.suspended_stocks)
        }
    
    def save_suspended_stocks(self, file_path: str):
        """保存停牌股票
        
        Args:
            file_path: 文件路径
        """
        data = {
            "suspended_stocks": list(self.suspended_stocks),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save suspended stocks error: {e}")
    
    def load_suspended_stocks(self, file_path: str):
        """加载停牌股票
        
        Args:
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.suspended_stocks = set(data.get("suspended_stocks", []))
        except Exception as e:
            print(f"Load suspended stocks error: {e}")


class MarketCalendar:
    """市场日历"""
    
    def __init__(self, trading_time_manager: Optional[TradingTimeManager] = None):
        """初始化市场日历
        
        Args:
            trading_time_manager: 交易时间管理器
        """
        self.trading_time_manager = trading_time_manager or TradingTimeManager()
    
    def get_calendar(self, start_date: datetime, end_date: datetime, market: str = "A_SHARE") -> Dict:
        """获取日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            market: 市场类型
            
        Returns:
            日历数据
        """
        calendar = []
        current_date = start_date
        
        while current_date <= end_date:
            is_trading_day = self.trading_time_manager.is_trading_day(current_date, market)
            
            calendar.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "is_trading_day": is_trading_day,
                "weekday": current_date.strftime("%A")
            })
            
            current_date += timedelta(days=1)
        
        return {
            "market": market,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_days": len(calendar),
            "trading_days": sum(1 for day in calendar if day["is_trading_day"]),
            "calendar": calendar
        }
    
    def get_holidays(self, start_date: datetime, end_date: datetime) -> List[str]:
        """获取节假日
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            节假日列表
        """
        holidays = []
        current_date = start_date
        
        while current_date <= end_date:
            if not self.trading_time_manager.is_trading_day(current_date):
                holidays.append(current_date.strftime("%Y-%m-%d"))
            
            current_date += timedelta(days=1)
        
        return holidays
    
    def get_trading_days(self, start_date: datetime, end_date: datetime, market: str = "A_SHARE") -> List[str]:
        """获取交易日
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            market: 市场类型
            
        Returns:
            交易日列表
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.trading_time_manager.is_trading_day(current_date, market):
                trading_days.append(current_date.strftime("%Y-%m-%d"))
            
            current_date += timedelta(days=1)
        
        return trading_days


# 全局实例
global_trading_time_manager = TradingTimeManager()
global_market_calendar = MarketCalendar(global_trading_time_manager)

def get_trading_time_manager() -> TradingTimeManager:
    """获取交易时间管理器实例
    
    Returns:
        交易时间管理器实例
    """
    return global_trading_time_manager

def get_market_calendar() -> MarketCalendar:
    """获取市场日历实例
    
    Returns:
        市场日历实例
    """
    return global_market_calendar


def is_trading_time(dt: Optional[datetime] = None, market: str = "A_SHARE") -> bool:
    """判断是否为交易时间
    
    Args:
        dt: 日期时间，默认为当前时间
        market: 市场类型
        
    Returns:
        是否为交易时间
    """
    if dt is None:
        dt = datetime.now()
    return get_trading_time_manager().is_trading_time(dt, market)


def is_trading_day(date: Optional[datetime] = None, market: str = "A_SHARE") -> bool:
    """判断是否为交易日
    
    Args:
        date: 日期，默认为当前日期
        market: 市场类型
        
    Returns:
        是否为交易日
    """
    if date is None:
        date = datetime.now()
    return get_trading_time_manager().is_trading_day(date, market)