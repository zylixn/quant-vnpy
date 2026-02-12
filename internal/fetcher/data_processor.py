"""
数据处理器模块
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Any
from vnpy.trader.object import BarData
from vnpy.trader.constant import Interval


class DataProcessor:
    """数据处理器"""
    
    def clean_data(
        self,
        bars: List[BarData],  # K线数据
        remove_duplicates: bool = True,  # 移除重复数据
        fill_missing: bool = True,  # 填充缺失数据
        check_validity: bool = True  # 检查数据有效性
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
                'open_interest': bar.open_interest,
                'symbol': bar.symbol,
                'exchange': bar.exchange,
                'interval': bar.interval,
                'gateway_name': bar.gateway_name
            })
        
        df = pd.DataFrame(data)
        
        # 移除重复数据
        if remove_duplicates:
            df.drop_duplicates(subset=['datetime'], keep='first', inplace=True)
        
        # 检查数据有效性
        if check_validity:
            # 移除价格为0的记录
            df = df[df['close'] > 0]
            # 确保最高价>=最低价
            df = df[df['high'] >= df['low']]
        
        # 填充缺失数据
        if fill_missing:
            df = df.sort_values('datetime')
            # 计算时间间隔
            if not df.empty:
                interval = df['interval'].iloc[0]
                if interval == Interval.MINUTE:
                    freq = '1T'
                elif interval == Interval.HOUR:
                    freq = '1H'
                elif interval == Interval.DAILY:
                    freq = '1D'
                elif interval == Interval.WEEKLY:
                    freq = '1W'
                else:
                    freq = '1D'
                
                # 重新索引并填充
                df = df.set_index('datetime').asfreq(freq)
                df.ffill(inplace=True)
                df.reset_index(inplace=True)
        
        # 转换回BarData
        cleaned_bars = []
        for _, row in df.iterrows():
            bar = BarData(
                symbol=row['symbol'],
                exchange=row['exchange'],
                datetime=row['datetime'],
                interval=row['interval'],
                open_price=row['open'],
                high_price=row['high'],
                low_price=row['low'],
                close_price=row['close'],
                volume=row['volume'],
                open_interest=row['open_interest'],
                gateway_name=row['gateway_name']
            )
            cleaned_bars.append(bar)
        
        return cleaned_bars
    
    def calculate_indicators(
        self,
        bars: List[BarData],  # K线数据
        indicators: List[str] = ['ma', 'macd', 'rsi'],  # 指标列表
        **kwargs  # 额外参数
    ) -> List[BarData]:
        """计算技术指标"""
        if not bars:
            return []
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'close': bar.close_price,
                'open': bar.open_price,
                'high': bar.high_price,
                'low': bar.low_price,
                'volume': bar.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        
        # 计算指标
        if 'ma' in indicators:
            # 计算移动平均线
            ma_periods = kwargs.get('ma_periods', [5, 10, 20, 50, 100, 200])
            for period in ma_periods:
                df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        
        if 'ema' in indicators:
            # 计算指数移动平均线
            ema_periods = kwargs.get('ema_periods', [12, 26])
            for period in ema_periods:
                df[f'ema{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        
        if 'macd' in indicators:
            # 计算MACD
            fast_period = kwargs.get('macd_fast', 12)
            slow_period = kwargs.get('macd_slow', 26)
            signal_period = kwargs.get('macd_signal', 9)
            
            exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
            exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        
        if 'rsi' in indicators:
            # 计算RSI
            rsi_period = kwargs.get('rsi_period', 14)
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        if 'kdj' in indicators:
            # 计算KDJ
            kdj_period = kwargs.get('kdj_period', 9)
            
            df['lowest'] = df['low'].rolling(window=kdj_period).min()
            df['highest'] = df['high'].rolling(window=kdj_period).max()
            df['rsv'] = (df['close'] - df['lowest']) / (df['highest'] - df['lowest']) * 100
            df['k'] = df['rsv'].ewm(com=2).mean()
            df['d'] = df['k'].ewm(com=2).mean()
            df['j'] = 3 * df['k'] - 2 * df['d']
        
        if 'boll' in indicators:
            # 计算布林带
            boll_period = kwargs.get('boll_period', 20)
            boll_std = kwargs.get('boll_std', 2)
            
            df['boll_mid'] = df['close'].rolling(window=boll_period).mean()
            df['boll_std'] = df['close'].rolling(window=boll_period).std()
            df['boll_upper'] = df['boll_mid'] + boll_std * df['boll_std']
            df['boll_lower'] = df['boll_mid'] - boll_std * df['boll_std']
        
        if 'ma' in indicators or 'volume_ma' in indicators:
            # 计算成交量移动平均线
            volume_ma_periods = kwargs.get('volume_ma_periods', [5, 20])
            for period in volume_ma_periods:
                df[f'volume_ma{period}'] = df['volume'].rolling(window=period).mean()
        
        # 转换回BarData（这里需要注意，BarData本身不支持指标，所以需要扩展或使用其他方式）
        # 这里我们返回原始的bars，实际应用中可能需要使用扩展的BarData类
        return bars
    
    def resample_data(
        self,
        bars: List[BarData],  # K线数据
        target_interval: Interval  # 目标周期
    ) -> List[BarData]:
        """重采样数据"""
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
                'open_interest': bar.open_interest,
                'symbol': bar.symbol,
                'exchange': bar.exchange,
                'gateway_name': bar.gateway_name
            })
        
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        
        # 重采样
        if target_interval == Interval.MINUTE:
            freq = '1T'
        elif target_interval == Interval.HOUR:
            freq = '1H'
        elif target_interval == Interval.DAILY:
            freq = '1D'
        elif target_interval == Interval.WEEKLY:
            freq = '1W'
        else:
            freq = '1D'
        
        resampled = df.resample(freq).agg({
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
                interval=target_interval,
                open_price=row['open'],
                high_price=row['high'],
                low_price=row['low'],
                close_price=row['close'],
                volume=row['volume'],
                open_interest=row['open_interest'],
                gateway_name=bars[0].gateway_name
            )
            resampled_bars.append(bar)
        
        return resampled_bars
    
    def calculate_returns(
        self,
        bars: List[BarData],  # K线数据
        periods: List[int] = [1, 5, 10, 20]  # 收益率周期
    ) -> pd.DataFrame:
        """计算收益率"""
        if not bars:
            return pd.DataFrame()
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'close': bar.close_price
            })
        
        df = pd.DataFrame(data)
        df.set_index('datetime', inplace=True)
        
        # 计算收益率
        for period in periods:
            # 计算指定周期的收益率
            # 例如：period=1 表示当日收益率，period=5 表示5日累计收益率
            df[f'return_{period}'] = df['close'].pct_change(periods=period)
        
        return df
    
    def calculate_beta(
        self,
        stock_bars: List[BarData],  # 股票数据
        index_bars: List[BarData],  # 指数数据
        period: int = 20  # 计算周期
    ) -> float:
        """
        计算贝塔系数
        β = 股票收益率协方差 / 指数收益率方差
        β > 1：进攻型（比大盘猛）
        大盘涨 1%，它涨 2%；大盘跌 1%，它跌 2%。
        ✅ 典型：有色金属、券商、科技股
        β ≈ 1：随大流
        β < 1：防守型（比大盘稳）
        大盘跌，它少跌甚至涨。
        ✅ 典型：黄金、白银、消费、公用事业
        """
        if not stock_bars or not index_bars:
            return 0.0
        
        # 计算收益率
        stock_returns = self.calculate_returns(stock_bars, periods=[1])['return_1']
        index_returns = self.calculate_returns(index_bars, periods=[1])['return_1']
        
        # 合并数据
        merged = pd.concat([stock_returns, index_returns], axis=1, join='inner')
        merged.columns = ['stock', 'index']
        
        # 计算协方差和方差
        if len(merged) >= period:
            cov = merged['stock'].cov(merged['index'])
            var = merged['index'].var()
            if var > 0:
                return cov / var
        
        return 0.0
    
    def calculate_volatility(
        self,
        bars: List[BarData],  # K线数据
        period: int = 20  # 计算周期
    ) -> float:
        """计算波动率"""
        if not bars:
            return 0.0
        
        # 计算收益率
        returns = self.calculate_returns(bars, periods=[1])['return_1']
        
        if len(returns) >= period:
            return returns.std() * np.sqrt(252)  # 年化波动率
        
        return 0.0
    
    def detect_anomalies(
        self,
        bars: List[BarData],  # K线数据
        threshold: float = 3.0  # 异常值阈值
    ) -> List[Dict[str, Any]]:
        """检测异常值"""
        anomalies = []
        
        if not bars:
            return anomalies
        
        # 转换为DataFrame
        data = []
        for bar in bars:
            data.append({
                'datetime': bar.datetime,
                'close': bar.close_price,
                'volume': bar.volume
            })
        
        df = pd.DataFrame(data)
        
        # 计算价格变化率
        df['price_change'] = df['close'].pct_change()
        # 计算成交量变化率
        df['volume_change'] = df['volume'].pct_change()
        
        # 检测异常值
        for idx, row in df.iterrows():
            if pd.notna(row['price_change']) and abs(row['price_change']) > threshold:
                anomalies.append({
                    'datetime': row['datetime'],
                    'type': 'price_anomaly',
                    'value': row['price_change'],
                    'threshold': threshold
                })
            
            if pd.notna(row['volume_change']) and abs(row['volume_change']) > threshold:
                anomalies.append({
                    'datetime': row['datetime'],
                    'type': 'volume_anomaly',
                    'value': row['volume_change'],
                    'threshold': threshold
                })
        
        return anomalies
