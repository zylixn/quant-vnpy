"""
股票数据获取模块演示脚本
"""

from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from internal.fetcher import StockFetcher, DataProcessor


def demo_stock_fetcher():
    """股票数据获取器演示"""
    print("=== 股票数据获取器演示 ===")
    
    # 创建股票数据获取器
    fetcher = StockFetcher()
    
    # 测试获取单只股票数据
    print("\n1. 获取单只股票数据...")
    bars = fetcher.get_stock_data(
        symbol="600000",  # 浦发银行
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31),
        interval=Interval.DAILY,
        exchange=Exchange.SSE,
        source="api",
        api_name="tushare"
    )
    
    print(f"获取到 {len(bars)} 条数据")
    if bars:
        print(f"第一条数据: {bars[0].datetime} - 收盘价: {bars[0].close_price}")
        print(f"最后一条数据: {bars[-1].datetime} - 收盘价: {bars[-1].close_price}")
    
    # 测试下载并保存数据
    print("\n2. 下载并保存数据...")
    fetcher.download_and_save(
        symbol="600000",
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31),
        filename="600000.csv",
        interval=Interval.DAILY,
        exchange=Exchange.SSE,
        api_name="tushare"
    )
    
    # 测试批量下载
    print("\n3. 批量下载数据...")
    fetcher.batch_download(
        symbols=["600000", "600036"],  # 浦发银行和招商银行
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31),
        output_dir="stock_data",
        interval=Interval.DAILY,
        exchange=Exchange.SSE,
        api_name="tushare"
    )
    
    # 测试获取股票列表
    print("\n4. 获取股票列表...")
    stocks = fetcher.get_stock_list(exchange=Exchange.SSE)
    print(f"获取到 {len(stocks)} 只股票")
    if stocks:
        print("前5只股票:")
        for stock in stocks[:5]:
            print(f"{stock['symbol']} - {stock['name']} - {stock['industry']}")
    
    # 测试获取股票信息
    print("\n5. 获取股票信息...")
    info = fetcher.get_stock_info(symbol="600000", exchange=Exchange.SSE)
    print("浦发银行信息:")
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # 测试获取指数成分股
    print("\n6. 获取指数成分股...")
    components = fetcher.get_index_components(
        index_symbol="000001.SH",  # 上证指数
        date=datetime(2023, 1, 1)
    )
    print(f"获取到 {len(components)} 只成分股")
    if components:
        print("前5只成分股:")
        for component in components[:5]:
            print(f"{component['symbol']} - 权重: {component['weight']}")
    
    # 测试获取实时数据
    print("\n7. 获取实时数据...")
    tick = fetcher.get_realtime_data(symbol="600000", exchange=Exchange.SSE)
    if tick:
        print(f"实时价格: {tick.last_price}")
        print(f"成交量: {tick.volume}")
        print(f"买一: {tick.bid_price_1} x {tick.bid_volume_1}")
        print(f"卖一: {tick.ask_price_1} x {tick.ask_volume_1}")
    else:
        print("未获取到实时数据")
    
    print("\n=== 股票数据获取器演示完成 ===")


def demo_data_processor():
    """数据处理器演示"""
    print("\n=== 数据处理器演示 ===")
    
    # 创建股票数据获取器
    fetcher = StockFetcher()
    
    # 获取测试数据
    bars = fetcher.get_stock_data(
        symbol="600000",
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31),
        interval=Interval.DAILY,
        exchange=Exchange.SSE
    )
    
    if not bars:
        print("未获取到数据，无法演示数据处理器")
        return
    
    # 创建数据处理器
    processor = DataProcessor()
    
    # 测试数据清洗
    print("\n1. 测试数据清洗...")
    cleaned_bars = processor.clean_data(bars)
    print(f"清洗前: {len(bars)} 条数据")
    print(f"清洗后: {len(cleaned_bars)} 条数据")
    
    # 测试数据重采样
    print("\n2. 测试数据重采样...")
    resampled_bars = processor.resample_data(bars, Interval.WEEK)
    print(f"日线数据: {len(bars)} 条")
    print(f"周线数据: {len(resampled_bars)} 条")
    if resampled_bars:
        print(f"第一条周线: {resampled_bars[0].datetime} - 收盘价: {resampled_bars[0].close_price}")
    
    # 测试计算收益率
    print("\n3. 测试计算收益率...")
    returns_df = processor.calculate_returns(bars, periods=[1, 5, 10])
    print("收益率数据:")
    print(returns_df.tail())
    
    # 测试计算波动率
    print("\n4. 测试计算波动率...")
    volatility = processor.calculate_volatility(bars, period=20)
    print(f"20日年化波动率: {volatility:.2%}")
    
    # 测试异常值检测
    print("\n5. 测试异常值检测...")
    anomalies = processor.detect_anomalies(bars, threshold=0.05)
    print(f"检测到 {len(anomalies)} 个异常值")
    if anomalies:
        print("前3个异常值:")
        for anomaly in anomalies[:3]:
            print(f"{anomaly['datetime']} - {anomaly['type']} - 值: {anomaly['value']:.2%}")
    
    print("\n=== 数据处理器演示完成 ===")


def demo_local_data():
    """本地数据演示"""
    print("\n=== 本地数据演示 ===")
    
    # 创建股票数据获取器
    fetcher = StockFetcher()
    
    # 确保有本地数据文件
    if not os.path.exists("600000.csv"):
        print("生成测试数据文件...")
        fetcher.download_and_save(
            symbol="600000",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 1, 31),
            filename="600000.csv"
        )
    
    # 测试从本地文件读取
    print("\n从本地文件读取数据...")
    bars = fetcher.get_stock_data(
        symbol="600000",
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31),
        source="local",
        filename="600000.csv"
    )
    
    print(f"从本地文件获取到 {len(bars)} 条数据")
    if bars:
        print(f"第一条数据: {bars[0].datetime} - 收盘价: {bars[0].close_price}")
    
    print("\n=== 本地数据演示完成 ===")


def main():
    """主函数"""
    print("股票数据获取模块演示")
    print("=" * 50)
    
    try:
        # 运行各个演示
        demo_stock_fetcher()
        demo_data_processor()
        demo_local_data()
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
    
    print("\n" + "=" * 50)
    print("所有演示完成！")


if __name__ == "__main__":
    import os
    main()
