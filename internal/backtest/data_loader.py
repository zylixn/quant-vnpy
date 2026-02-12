"""
回测数据加载器
"""

import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import pandas as pd
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval


class DataLoader:
    """数据加载器"""
    
    @staticmethod
    def load_from_csv(
        filename: str,  # CSV文件路径
        symbol: str,    # 合约代码
        exchange: Exchange = Exchange.SHFE,  # 交易所
        interval: Interval = Interval.MINUTE  # 周期
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
                        gateway_name="CSV"
                    )
                    bars.append(bar)
        except Exception as e:
            print(f"加载CSV文件失败: {e}")
        
        return bars
    
    @staticmethod
    def load_from_json(
        filename: str,  # JSON文件路径
        symbol: str,    # 合约代码
        exchange: Exchange = Exchange.SHFE,  # 交易所
        interval: Interval = Interval.MINUTE  # 周期
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
                        gateway_name="JSON"
                    )
                    bars.append(bar)
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
        
        return bars
    
    @staticmethod
    def load_from_pandas(
        df: pd.DataFrame,  # pandas DataFrame
        symbol: str,       # 合约代码
        exchange: Exchange = Exchange.SHFE,  # 交易所
        interval: Interval = Interval.MINUTE  # 周期
    ) -> List[BarData]:
        """从pandas DataFrame加载数据"""
        bars = []
        
        try:
            for _, row in df.iterrows():
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=row['datetime'],
                    interval=interval,
                    open_price=float(row['open']),
                    high_price=float(row['high']),
                    low_price=float(row['low']),
                    close_price=float(row['close']),
                    volume=float(row['volume']),
                    open_interest=float(row.get('open_interest', 0)),
                    gateway_name="PANDAS"
                )
                bars.append(bar)
        except Exception as e:
            print(f"加载DataFrame失败: {e}")
        
        return bars
    
    @staticmethod
    def download_from_api(
        symbol: str,  # 合约代码
        start: datetime,  # 开始时间
        end: datetime,  # 结束时间
        interval: str = "1m",  # 周期
        source: str = "binance"  # 数据源
    ) -> List[BarData]:
        """从API下载数据"""
        bars = []
        
        try:
            if source == "binance":
                # 使用ccxt库从Binance下载数据
                import ccxt
                
                exchange = ccxt.binance()
                timeframe = interval
                limit = 1000
                
                all_ohlcv = []
                since = exchange.parse8601(start.isoformat())
                
                while since < exchange.parse8601(end.isoformat()):
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
                    if not ohlcv:
                        break
                    all_ohlcv.extend(ohlcv)
                    since = ohlcv[-1][0] + 1
                
                for ohlcv in all_ohlcv:
                    bar = BarData(
                        symbol=symbol,
                        exchange=Exchange.BINANCE,
                        datetime=datetime.fromtimestamp(ohlcv[0] / 1000),
                        interval=Interval(interval),
                        open_price=ohlcv[1],
                        high_price=ohlcv[2],
                        low_price=ohlcv[3],
                        close_price=ohlcv[4],
                        volume=ohlcv[5],
                        open_interest=0,
                        gateway_name="BINANCE"
                    )
                    bars.append(bar)
        except Exception as e:
            print(f"从API下载数据失败: {e}")
        
        return bars
    
    @staticmethod
    def resample_bars(
        bars: List[BarData],  # 原始K线数据
        interval: Interval  # 目标周期
    ) -> List[BarData]:
        """重采样K线数据"""
        if not bars:
            return []
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'open': bar.open_price,
                'high': bar.high_price,
                'low': bar.low_price,
                'close': bar.close_price,
                'volume': bar.volume,
                'open_interest': bar.open_interest
            })
        
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        
        # 重采样
        rule_map = {
            Interval.MINUTE: '1T',
            Interval.HOUR: '1H',
            Interval.DAILY: '1D',
            Interval.WEEKLY: '1W',
        }
        
        rule = rule_map.get(interval, '1T')
        
        resampled = df.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'open_interest': 'last'
        }).dropna()
        
        # 转换回BarData
        resampled_bars = []
        for idx, row in resampled.iterrows():
            bar = BarData(
                symbol=bars[0].symbol,
                exchange=bars[0].exchange,
                datetime=idx,
                interval=interval,
                open_price=row['open'],
                high_price=row['high'],
                low_price=row['low'],
                close_price=row['close'],
                volume=row['volume'],
                open_interest=row['open_interest'],
                gateway_name="RESAMPLED"
            )
            resampled_bars.append(bar)
        
        return resampled_bars
    
    @staticmethod
    def save_to_csv(
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
            print(f"保存CSV文件失败: {e}")
    
    @staticmethod
    def save_to_json(
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
            print(f"保存JSON文件失败: {e}")


class DataProcessor:
    """数据处理器"""
    
    @staticmethod
    def calculate_indicators(
        bars: List[BarData],  # K线数据
        indicators: List[str] = ['ma', 'macd', 'rsi']  # 指标列表
    ) -> List[Dict[str, Any]]:
        """计算技术指标"""
        result = []
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'open': bar.open_price,
                'high': bar.high_price,
                'low': bar.low_price,
                'close': bar.close_price,
                'volume': bar.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        
        # 计算指标
        if 'ma' in indicators:
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma50'] = df['close'].rolling(window=50).mean()
        
        if 'macd' in indicators:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['hist'] = df['macd'] - df['signal']
        
        if 'rsi' in indicators:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # 转换回字典列表
        for idx, row in df.iterrows():
            item = row.to_dict()
            item['datetime'] = idx
            result.append(item)
        
        return result
    
    @staticmethod
    def clean_data(
        bars: List[BarData],  # K线数据
        remove_duplicates: bool = True,  # 移除重复数据
        fill_missing: bool = True  # 填充缺失数据
    ) -> List[BarData]:
        """清洗数据"""
        if not bars:
            return []
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'open': bar.open_price,
                'high': bar.high_price,
                'low': bar.low_price,
                'close': bar.close_price,
                'volume': bar.volume,
                'open_interest': bar.open_interest
            })
        
        df = pd.DataFrame(data)
        
        # 移除重复数据
        if remove_duplicates:
            df.drop_duplicates(subset=['datetime'], keep='first', inplace=True)
        
        # 填充缺失数据
        if fill_missing:
            df = df.sort_values('datetime')
            df = df.set_index('datetime').asfreq('1T').reset_index()
            df.ffill(inplace=True)
        
        # 转换回BarData
        cleaned_bars = []
        for _, row in df.iterrows():
            bar = BarData(
                symbol=bars[0].symbol,
                exchange=bars[0].exchange,
                datetime=row['datetime'],
                interval=bars[0].interval,
                open_price=row['open'],
                high_price=row['high'],
                low_price=row['low'],
                close_price=row['close'],
                volume=row['volume'],
                open_interest=row['open_interest'],
                gateway_name="CLEANED"
            )
            cleaned_bars.append(bar)
        
        return cleaned_bars
