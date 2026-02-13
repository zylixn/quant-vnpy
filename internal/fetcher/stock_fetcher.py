"""
股票数据获取核心类
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval
from internal.fetcher.data_sources import LocalDataSource, APIDataSource, DatabaseDataSource
from internal.fetcher.data_processor import DataProcessor
from internal.config import get_config


class StockFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        """初始化股票数据获取器"""
        self.local_source = LocalDataSource()
        self.api_source = APIDataSource()
        self.db_source = DatabaseDataSource()
        self.processor = DataProcessor()
    
    def get_stock_data(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval = Interval.DAILY,  # 周期
        source: str = "api",  # 数据源
        exchange: Exchange = Exchange.SSE,  # 交易所
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """获取股票数据"""
        bars = []
        
        try:
            if source == "local":
                # 从本地文件获取
                filename = kwargs.get("filename")
                bars = self.local_source.get_data(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    exchange=exchange,
                    filename=filename
                )
            elif source == "api":
                # 从API获取
                api_name = kwargs.pop("api_name", "tushare")  # 从kwargs中移除api_name，避免重复传递
                bars = self.api_source.get_data(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    exchange=exchange,
                    api_name=api_name,
                    **kwargs
                )
            elif source == "database":
                # 从数据库获取
                bars = self.db_source.get_data(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                    exchange=exchange
                )
            else:
                raise ValueError(f"Unknown data source: {source}")
            
            # 数据处理
            if kwargs.get("clean", True):
                bars = self.processor.clean_data(bars)
            
            if kwargs.get("calculate_indicators", False):
                indicators = kwargs.get("indicators", ["ma", "macd", "rsi"])
                bars = self.processor.calculate_indicators(bars, indicators)
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
        return bars
    
    def get_stock_list(
        self,
        exchange: Exchange = Exchange.SSE,  # 交易所
        source: str = "api"  # 数据源
    ) -> List[Dict[str, Any]]:
        """获取股票列表"""
        stocks = []
        
        try:
            if source == "api":
                stocks = self.api_source.get_stock_list(exchange)
            elif source == "database":
                stocks = self.db_source.get_stock_list(exchange)
        except Exception as e:
            print(f"获取股票列表失败: {e}")
        
        return stocks
    
    def get_stock_info(
        self,
        symbol: str,  # 股票代码
        exchange: Exchange = Exchange.SSE,  # 交易所
        source: str = "api"  # 数据源
    ) -> Dict[str, Any]:
        """获取股票信息"""
        info = {}
        
        try:
            if source == "api":
                info = self.api_source.get_stock_info(symbol, exchange)
            elif source == "database":
                info = self.db_source.get_stock_info(symbol, exchange)
        except Exception as e:
            print(f"获取股票信息失败: {e}")
        
        return info
    
    def save_stock_data(
        self,
        bars: List[BarData],  # K线数据
        filename: str,  # 文件名
        format: str = "csv"  # 格式
    ):
        """保存股票数据"""
        try:
            if format == "csv":
                self.local_source.save_to_csv(bars, filename)
            elif format == "json":
                self.local_source.save_to_json(bars, filename)
        except Exception as e:
            print(f"保存股票数据失败: {e}")
    
    def download_and_save(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        filename: str,  # 文件名
        interval: Interval = Interval.DAILY,  # 周期
        exchange: Exchange = Exchange.SSE,  # 交易所
        api_name: str = "tushare"  # API名称
    ):
        """下载并保存股票数据"""
        # 获取数据
        bars = self.get_stock_data(
            symbol=symbol,
            start=start,
            end=end,
            interval=interval,
            source="api",
            exchange=exchange,
            api_name=api_name,
            token=get_config().get("TUSHARE_TOKEN")
        )
        
        # 保存数据
        if bars:
            self.save_stock_data(bars, filename)
            print(f"数据已保存到: {filename}")
        else:
            print("未获取到数据")
    
    def batch_download(
        self,
        symbols: List[str],  # 股票代码列表
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        output_dir: str,  # 输出目录
        interval: Interval = Interval.DAILY,  # 周期
        exchange: Exchange = Exchange.SSE,  # 交易所
        api_name: str = "tushare"  # API名称
    ):
        """批量下载股票数据"""
        import os
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        for symbol in symbols:
            print(f"下载 {symbol} ...")
            filename = os.path.join(output_dir, f"{symbol}.csv")
            
            try:
                self.download_and_save(
                    symbol=symbol,
                    start=start,
                    end=end,
                    filename=filename,
                    interval=interval,
                    exchange=exchange,
                    api_name=api_name
                )
            except Exception as e:
                print(f"下载 {symbol} 失败: {e}")
    
    def get_realtime_data(
        self,
        symbol: str,  # 股票代码
        exchange: Exchange = Exchange.SSE,  # 交易所
        api_name: str = "tushare"  # API名称
    ) -> Optional[TickData]:
        """获取实时数据"""
        try:
            return self.api_source.get_realtime_data(
                symbol=symbol,
                exchange=exchange,
                api_name=api_name
            )
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            return None
    
    def get_index_components(
        self,
        index_symbol: str,  # 指数代码
        date: datetime = None,  # 日期
        api_name: str = "tushare"  # API名称
    ) -> List[Dict[str, Any]]:
        """获取指数成分股"""
        try:
            return self.api_source.get_index_components(
                index_symbol=index_symbol,
                date=date or datetime.now(),
                api_name=api_name
            )
        except Exception as e:
            print(f"获取指数成分股失败: {e}")
            return []


class StockDataManager:
    """股票数据管理器"""
    
    def __init__(self, fetcher: Optional[StockFetcher] = None):
        """初始化股票数据管理器"""
        self.fetcher = fetcher or StockFetcher()
        self.data_cache: Dict[str, List[BarData]] = {}
    
    def get_data(
        self,
        symbol: str,  # 股票代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: Interval = Interval.DAILY,  # 周期
        source: str = "api",  # 数据源
        exchange: Exchange = Exchange.SSE,  # 交易所
        use_cache: bool = True,  # 使用缓存
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """获取股票数据（带缓存）"""
        # 生成缓存键
        cache_key = f"{symbol}_{exchange.value}_{interval.value}_{start}_{end}"
        
        # 检查缓存
        if use_cache and cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        # 获取数据
        bars = self.fetcher.get_stock_data(
            symbol=symbol,
            start=start,
            end=end,
            interval=interval,
            source=source,
            exchange=exchange,
            **kwargs
        )
        
        # 缓存数据
        if use_cache and bars:
            self.data_cache[cache_key] = bars
        
        return bars
    
    def clear_cache(self):
        """清空缓存"""
        self.data_cache.clear()
    
    def get_cache_size(self) -> int:
        """获取缓存大小"""
        return len(self.data_cache)
