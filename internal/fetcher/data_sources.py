"""
数据源模块
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import pandas as pd
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval
from internal.utils import get_logger
from internal.config import get_config

logger = get_logger("fetcher")

def get_database():
    """获取 vnpy 数据库实例"""
    try:
        from vnpy.trader.database import get_database as vnpy_get_database
        return vnpy_get_database()
    except ImportError:
        return None

def get_db_tz():
    """获取数据库时区"""
    try:
        from vnpy.trader.database import DB_TZ
        return DB_TZ
    except ImportError:
        from zoneinfo import ZoneInfo
        return ZoneInfo("Asia/Shanghai")

def convert_tz(dt: datetime) -> datetime:
    """转换时区"""
    try:
        from vnpy.trader.database import convert_tz as vnpy_convert_tz
        return vnpy_convert_tz(dt)
    except ImportError:
        db_tz = get_db_tz()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=db_tz)
        dt = dt.astimezone(db_tz)
        return dt.replace(tzinfo=None)
        
class LocalDataSource:
    """本地数据源"""
    
    def get_data(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval = Interval.DAILY,  # 周期
        exchange: Exchange = Exchange.SSE,  # 交易所
        filename: Optional[str] = None,  # 文件名
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """从本地文件获取数据"""
        bars = []
        
        if not filename:
            filename = f"{symbol}.csv"
        
        try:
            if filename.endswith('.csv'):
                bars = self._load_from_csv(
                    filename=filename,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval
                )
            elif filename.endswith('.json'):
                bars = self._load_from_json(
                    filename=filename,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval
                )
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            # 过滤时间范围
            bars = [b for b in bars if start <= b.datetime <= end]
            
        except Exception as e:
            print(f"从本地文件获取数据失败: {e}")
        
        return bars
    
    def _load_from_csv(
        self,
        filename: str,  # 文件名
        symbol: str,  # 股票代码
        exchange: Exchange,  # 交易所
        interval: Interval  # 周期
    ) -> List[BarData]:
        """从CSV文件加载数据"""
        bars = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    bar = BarData(
                        symbol=symbol,
                        exchange=exchange,
                        datetime=datetime.fromisoformat(row['datetime']),
                        interval=interval,
                        open_price=float(row['open']),
                        high_price=float(row['high']),
                        low_price=float(row['low']),
                        close_price=float(row['close']),
                        volume=float(row['volume']),
                        open_interest=float(row.get('open_interest', 0)),
                        gateway_name="LOCAL"
                    )
                    bars.append(bar)
        except Exception as e:
            print(f"从CSV文件加载数据失败: {e}")
        
        return bars
    
    def _load_from_json(
        self,
        filename: str,  # 文件名
        symbol: str,  # 股票代码
        exchange: Exchange,  # 交易所
        interval: Interval  # 周期
    ) -> List[BarData]:
        """从JSON文件加载数据"""
        bars = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    bar = BarData(
                        symbol=symbol,
                        exchange=exchange,
                        datetime=datetime.fromisoformat(item['datetime']),
                        interval=interval,
                        open_price=float(item['open']),
                        high_price=float(item['high']),
                        low_price=float(item['low']),
                        close_price=float(item['close']),
                        volume=float(item['volume']),
                        open_interest=float(item.get('open_interest', 0)),
                        gateway_name="LOCAL"
                    )
                    bars.append(bar)
        except Exception as e:
            print(f"从JSON文件加载数据失败: {e}")
        
        return bars
    
    def save_to_csv(
        self,
        bars: List[BarData],  # K线数据
        filename: str  # 文件名
    ):
        """保存数据到CSV文件"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'open_interest']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for bar in bars:
                    writer.writerow({
                        'datetime': bar.datetime.isoformat(),
                        'open': bar.open_price,
                        'high': bar.high_price,
                        'low': bar.low_price,
                        'close': bar.close_price,
                        'volume': bar.volume,
                        'open_interest': bar.open_interest
                    })
        except Exception as e:
            print(f"保存数据到CSV文件失败: {e}")
    
    def save_to_json(
        self,
        bars: List[BarData],  # K线数据
        filename: str  # 文件名
    ):
        """保存数据到JSON文件"""
        try:
            data = []
            for bar in bars:
                data.append({
                    'datetime': bar.datetime.isoformat(),
                    'open': bar.open_price,
                    'high': bar.high_price,
                    'low': bar.low_price,
                    'close': bar.close_price,
                    'volume': bar.volume,
                    'open_interest': bar.open_interest
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据到JSON文件失败: {e}")


class APIDataSource:
    """API数据源"""
    
    def get_data(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval = Interval.DAILY,  # 周期
        exchange: Exchange = Exchange.SSE,  # 交易所
        api_name: str = "tushare",  # API名称
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """从API获取数据"""
        bars = []
        try:
            if api_name == "tushare":
                bars = self._get_from_tushare(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    exchange=exchange,
                    **kwargs
                )
            elif api_name == "baostock":
                bars = self._get_from_baostock(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    exchange=exchange,
                    **kwargs
                )
            elif api_name == "akshare":
                bars = self._get_from_akshare(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    exchange=exchange,
                    **kwargs
                )
            else:
                raise ValueError(f"Unknown API: {api_name}")
        except Exception as e:
            print(f"从API获取数据失败: {e}")
        
        return bars
    
    def _get_from_tushare(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval,  # 周期
        exchange: Exchange,  # 交易所
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """从Tushare获取数据"""
        bars = []
        
        try:
            import tushare as ts
            
            # 设置token
            token = kwargs.get("token") or get_config().get("data_source.TUSHARE_TOKEN")
            if token:
                ts.set_token(token)
            else:
                raise ValueError("Tushare token is required")
            pro = ts.pro_api()
            
            # 转换股票代码
            if exchange == Exchange.SSE:
                ts_symbol = symbol + ".SH"
            elif exchange == Exchange.SZSE:
                ts_symbol = symbol + ".SZ"
            else:
                ts_symbol = symbol
            
            # 转换时间格式
            start_date = start.strftime("%Y%m%d")
            end_date = end.strftime("%Y%m%d")
            
            # 转换周期
            if interval == Interval.DAILY:
                freq = "D"
            elif interval == Interval.MINUTE:
                freq = "1min"
            elif interval == Interval.HOUR:
                freq = "60min"
            else:
                freq = "D"
            
            # 获取数据
            if freq == "D":
                df = pro.daily(
                    ts_code=ts_symbol,
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                df = ts.pro_bar(
                    ts_code=ts_symbol,
                    adj='qfq',
                    start_date=start_date,
                    end_date=end_date,
                    freq=freq
                )
            
            # 转换为BarData
            for _, row in df.iterrows():
                bar_datetime = datetime.strptime(row['trade_date'], "%Y%m%d")
                bar_datetime = convert_tz(bar_datetime)
                
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=bar_datetime,
                    interval=interval,
                    open_price=row['open'],
                    high_price=row['high'],
                    low_price=row['low'],
                    close_price=row['close'],
                    volume=row['vol'],
                    open_interest=0,
                    gateway_name="TUSHARE"
                )
                bars.append(bar)
            
            # 按时间排序
            bars.sort(key=lambda x: x.datetime)
            
        except ImportError:
            print("请安装tushare库: pip install tushare")
        except Exception as e:
            print(f"从Tushare获取数据失败: {e}")
        
        return bars
    
    def _get_from_baostock(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval,  # 周期
        exchange: Exchange,  # 交易所
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """从Baostock获取数据"""
        bars = []
        
        try:
            import baostock as bs
            
            # 登录
            lg = bs.login()
            if lg.error_code != '0':
                print(f"Baostock登录失败: {lg.error_msg}")
                return bars
            
            # 转换股票代码
            if exchange == Exchange.SSE:
                bs_symbol = "sh." + symbol
            elif exchange == Exchange.SZSE:
                bs_symbol = "sz." + symbol
            else:
                bs_symbol = symbol
            
            # 转换时间格式
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")
            
            # 转换周期
            if interval == Interval.DAILY:
                freq = "d"
            elif interval == Interval.MINUTE:
                freq = "5"
            elif interval == Interval.HOUR:
                freq = "60"
            else:
                freq = "d"
            
            # 获取数据
            rs = bs.query_history_k_data_plus(
                bs_symbol,
                "date,open,high,low,close,volume",
                start_date=start_date,
                end_date=end_date,
                frequency=freq,
                adjustflag="3"
            )
            logger.info(f"Baostock查询数据返回状态码: {rs.error_code}")
            logger.info(f"Baostock查询数据返回消息: {rs.error_msg}")
            # 转换为BarData
            while (rs.error_code == '0') & rs.next():
                row = rs.get_row_data()
                # logger.info(f"Baostock查询数据返回行数据: {row}")
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=datetime.strptime(row[0], "%Y-%m-%d"),
                    interval=interval,
                    open_price=float(row[1]),
                    high_price=float(row[2]),
                    low_price=float(row[3]),
                    close_price=float(row[4]),
                    volume=float(row[5]),
                    open_interest=0,
                    gateway_name="BAOSTOCK"
                )
                bars.append(bar)
            
            # 登出
            bs.logout()
            
        except ImportError:
            print("请安装baostock库: pip install baostock")
        except Exception as e:
            print(f"从Baostock获取数据失败: {e}")
        
        return bars
    
    def _get_from_akshare(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval,  # 周期
        exchange: Exchange,  # 交易所
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """从Akshare获取数据"""
        bars = []
        
        try:
            import akshare as ak
            
            # 转换股票代码
            if exchange == Exchange.SSE:
                ak_symbol = symbol + "_SH"
            elif exchange == Exchange.SZSE:
                ak_symbol = symbol + "_SZ"
            else:
                ak_symbol = symbol
            
            # 转换时间格式
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")
            
            # 转换周期
            if interval == Interval.DAILY:
                freq = "daily"
            elif interval == Interval.MINUTE:
                freq = "1min"
            elif interval == Interval.HOUR:
                freq = "60min"
            else:
                freq = "daily"
            
            # 获取数据
            if freq == "daily":
                df = ak.stock_zh_a_hist(
                    symbol=ak_symbol.split("_")[0],
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            else:
                df = ak.stock_zh_a_minute(
                    symbol=ak_symbol,
                    period=freq,
                    adjust="qfq"
                )
            
            # 转换为BarData
            for _, row in df.iterrows():
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=pd.to_datetime(row['日期']),
                    interval=interval,
                    open_price=row['开盘'],
                    high_price=row['最高'],
                    low_price=row['最低'],
                    close_price=row['收盘'],
                    volume=row['成交量'],
                    open_interest=0,
                    gateway_name="AKSHARE"
                )
                bars.append(bar)
            
        except ImportError:
            print("请安装akshare库: pip install akshare")
        except Exception as e:
            print(f"从Akshare获取数据失败: {e}")
        
        return bars
    
    def get_stock_list(
        self,
        exchange: Exchange = Exchange.SSE,  # 交易所
        **kwargs  # 额外参数
    ) -> List[Dict[str, Any]]:
        """获取股票列表"""
        stocks = []
        
        try:
            import tushare as ts
            
            # 设置token
            token = kwargs.get("token") or get_config().get("TUSHARE_TOKEN")
            if token:
                ts.set_token(token)
            
            pro = ts.pro_api()
            
            # 获取股票列表
            if exchange == Exchange.SSE:
                df = pro.stock_basic(exchange="SSE")
            elif exchange == Exchange.SZSE:
                df = pro.stock_basic(exchange="SZSE")
            else:
                df = pro.stock_basic()
            
            # 转换为字典列表
            for _, row in df.iterrows():
                stocks.append({
                    "symbol": row['ts_code'].split(".")[0],
                    "name": row['name'],
                    "industry": row['industry'],
                    "area": row['area'],
                    "list_date": row['list_date']
                })
        except Exception as e:
            print(f"获取股票列表失败: {e}")
        
        return stocks
    
    def get_stock_info(
        self,
        symbol: str,  # 股票代码
        exchange: Exchange = Exchange.SSE,  # 交易所
        **kwargs  # 额外参数
    ) -> Dict[str, Any]:
        """获取股票信息"""
        info = {}
        
        try:
            import tushare as ts
            
            # 设置token
            token = kwargs.get("token") or get_config().get("TUSHARE_TOKEN")
            if token:
                ts.set_token(token)
            
            pro = ts.pro_api()
            
            # 转换股票代码
            if exchange == Exchange.SSE:
                ts_symbol = symbol + ".SH"
            elif exchange == Exchange.SZSE:
                ts_symbol = symbol + ".SZ"
            else:
                ts_symbol = symbol
            
            # 获取股票信息
            df = pro.stock_basic(ts_code=ts_symbol)
            if not df.empty:
                row = df.iloc[0]
                info = {
                    "symbol": row['ts_code'],
                    "name": row['name'],
                    "industry": row['industry'],
                    "area": row['area'],
                    "list_date": row['list_date'],
                    "market": row['market']
                }
        except Exception as e:
            print(f"获取股票信息失败: {e}")
        
        return info
    
    def get_realtime_data(
        self,
        symbol: str,  # 股票代码
        exchange: Exchange = Exchange.SSE,  # 交易所
        api_name: str = "tushare",  # API名称
        **kwargs  # 额外参数
    ) -> Optional[TickData]:
        """获取实时数据"""
        tick = None
        
        try:
            if api_name == "tushare":
                import tushare as ts
                
                # 设置token
                token = kwargs.get("token") or get_config().get("TUSHARE_TOKEN")
                if token:
                    ts.set_token(token)
                
                # 转换股票代码
                if exchange == Exchange.SSE:
                    ts_symbol = symbol + ".SH"
                elif exchange == Exchange.SZSE:
                    ts_symbol = symbol + ".SZ"
                else:
                    ts_symbol = symbol
                
                # 获取实时数据
                df = ts.get_realtime_quotes([ts_symbol])
                if not df.empty:
                    row = df.iloc[0]
                    tick = TickData(
                        symbol=symbol,
                        exchange=exchange,
                        datetime=datetime.now(),
                        last_price=float(row['price']),
                        volume=float(row['volume']),
                        bid_price_1=float(row['bid']),
                        bid_volume_1=float(row['b1_v']),
                        ask_price_1=float(row['ask']),
                        ask_volume_1=float(row['a1_v']),
                        gateway_name="TUSHARE"
                    )
        except Exception as e:
            print(f"获取实时数据失败: {e}")
        
        return tick
    
    def get_index_components(
        self,
        index_symbol: str,  # 指数代码
        date: datetime,  # 日期
        api_name: str = "tushare",  # API名称
        **kwargs  # 额外参数
    ) -> List[Dict[str, Any]]:
        """获取指数成分股"""
        components = []
        
        try:
            if api_name == "tushare":
                import tushare as ts
                
                # 设置token
                token = kwargs.get("token") or get_config().get("TUSHARE_TOKEN")
                if token:
                    ts.set_token(token)
                
                pro = ts.pro_api()
                
                # 获取指数成分股
                df = pro.index_weight(
                    index_code=index_symbol,
                    trade_date=date.strftime("%Y%m%d")
                )
                
                # 转换为字典列表
                for _, row in df.iterrows():
                    components.append({
                        "symbol": row['con_code'].split(".")[0],
                        "weight": row['weight']
                    })
        except Exception as e:
            print(f"获取指数成分股失败: {e}")
        
        return components


class DatabaseDataSource:
    """数据库数据源"""
    
    def get_data(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval = Interval.DAILY,  # 周期
        exchange: Exchange = Exchange.SSE,  # 交易所
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """从数据库获取数据"""
        bars = []
        
        try:
            db = get_database()
            if db is None:
                print("数据库未初始化")
                return bars
            
            # 从数据库获取数据
            bars = db.load_bar_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start=start,
                end=end
            )
        except Exception as e:
            print(f"从数据库获取数据失败: {e}")
        
        return bars
    
    def save_data(
        self,
        bars: List[BarData]  # K线数据
    ):
        """保存数据到数据库"""
        try:
            db = get_database()
            if db is None:
                print("数据库未初始化")
                return
            
            # 确保 datetime 字段是正确的类型
            import pandas as pd
            db_tz = get_db_tz()
            for bar in bars:
                # 如果是 pandas.Timestamp，转换为 datetime
                if isinstance(bar.datetime, pd.Timestamp):
                    # 如果没有时区，先加上时区
                    if bar.datetime.tzinfo is None:
                        bar.datetime = bar.datetime.tz_localize(db_tz)
                    # 转换为 datetime
                    bar.datetime = bar.datetime.to_pydatetime()
            
            db.save_bar_data(bars)
        except Exception as e:
            print(f"保存数据到数据库失败: {e}")
    
    def get_stock_list(
        self,
        exchange: Exchange = Exchange.SSE,  # 交易所
        **kwargs  # 额外参数
    ) -> List[Dict[str, Any]]:
        """获取股票列表"""
        stocks = []
        
        try:
            db = get_database()
            if db is None:
                print("数据库未初始化")
                return stocks
            
            # 从数据库获取股票列表
            # 这里需要根据实际的数据库结构实现
            pass
        except Exception as e:
            print(f"从数据库获取股票列表失败: {e}")
        
        return stocks
    
    def get_stock_info(
        self,
        symbol: str,  # 股票代码
        exchange: Exchange = Exchange.SSE,  # 交易所
        **kwargs  # 额外参数
    ) -> Dict[str, Any]:
        """获取股票信息"""
        info = {}
        
        try:
            db = get_database()
            if db is None:
                print("数据库未初始化")
                return info
            
            # 从数据库获取股票信息
            # 这里需要根据实际的数据库结构实现
            pass
        except Exception as e:
            print(f"从数据库获取股票信息失败: {e}")
        
        return info
