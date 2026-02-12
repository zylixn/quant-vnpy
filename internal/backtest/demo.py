"""
回测模块演示脚本
"""

from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from internal.backtest import BacktestEngine, DataLoader, BacktestAnalyzer
from internal.backtest.strategies import DemoBacktestStrategy, MACDBacktestStrategy, RSIBacktestStrategy


def demo_backtest_engine():
    """回测引擎演示"""
    print("=== 回测引擎演示 ===")
    
    # 创建回测引擎
    engine = BacktestEngine()
    
    # 设置回测参数
    engine.set_parameters(
        vt_symbol="BTC/USDT:BINANCE",
        interval=Interval.HOUR,
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31),
        rate=0.0001,
        slippage=0.0,
        size=1,
        pricetick=0.01,
        capital=100000
    )
    
    # 添加策略
    engine.add_strategy(DemoBacktestStrategy, {
        "fast_window": 10,
        "slow_window": 20
    })
    
    # 运行回测
    print("运行回测...")
    results = engine.run_backtesting()
    
    # 计算统计指标
    print("计算统计指标...")
    statistics = engine.calculate_statistics()
    
    # 打印统计结果
    print("\n回测结果:")
    print(f"总收益率: {statistics['total_return']:.2%}")
    print(f"年化收益率: {statistics['annual_return']:.2%}")
    print(f"最大回撤: {statistics['max_drawdown']:.2%}")
    print(f"夏普比率: {statistics['sharpe_ratio']:.2f}")
    print(f"总交易次数: {statistics['total_trades']}")
    
    # 获取成交记录
    trades = engine.get_trades()
    print(f"\n成交记录数: {len(trades)}")
    if trades:
        print("\n前5笔成交:")
        for i, trade in enumerate(trades[:5]):
            print(f"{i+1}. {trade.direction.value} {trade.offset.value} {trade.symbol} @ {trade.price} x {trade.volume} - P&L: {trade.pnl:.2f}")
    
    print("\n=== 回测引擎演示完成 ===")


def demo_data_loader():
    """数据加载器演示"""
    print("\n=== 数据加载器演示 ===")
    
    # 生成测试数据
    print("生成测试数据...")
    from internal.backtest.backtest_engine import BacktestEngineAdapter
    bars = BacktestEngineAdapter.generate_test_data(
        symbol="BTC/USDT",
        exchange="BINANCE",
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 7),
        interval="1h"
    )
    
    print(f"生成的数据条数: {len(bars)}")
    if bars:
        print(f"第一条数据: {bars[0].datetime} - {bars[0].close_price}")
        print(f"最后一条数据: {bars[-1].datetime} - {bars[-1].close_price}")
    
    # 保存数据到CSV
    print("保存数据到CSV...")
    DataLoader.save_to_csv(bars, "test_data.csv")
    print("数据已保存到 test_data.csv")
    
    # 从CSV加载数据
    print("从CSV加载数据...")
    loaded_bars = DataLoader.load_from_csv(
        "test_data.csv",
        symbol="BTC/USDT",
        exchange=Exchange.BINANCE,
        interval=Interval.HOUR
    )
    print(f"加载的数据条数: {len(loaded_bars)}")
    
    print("\n=== 数据加载器演示完成 ===")


def demo_backtest_analyzer():
    """回测分析器演示"""
    print("\n=== 回测分析器演示 ===")
    
    # 创建回测引擎
    engine = BacktestEngine()
    
    # 设置回测参数
    engine.set_parameters(
        vt_symbol="BTC/USDT:BINANCE",
        interval=Interval.HOUR,
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 31)
    )
    
    # 添加策略
    engine.add_strategy(MACDBacktestStrategy, {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
    })
    
    # 运行回测
    print("运行回测...")
    results = engine.run_backtesting()
    
    # 创建分析器
    analyzer = BacktestAnalyzer(results)
    analyzer.set_trades(engine.get_trades())
    
    # 计算统计指标
    print("计算统计指标...")
    statistics = analyzer.calculate_statistics()
    trade_analysis = analyzer.analyze_trades()
    
    # 打印分析结果
    print("\n统计指标:")
    for key, value in statistics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    print("\n交易分析:")
    for key, value in trade_analysis.items():
        print(f"{key}: {value}")
    
    # 导出报告
    print("\n导出回测报告...")
    analyzer.export_report("backtest_report.json")
    print("报告已导出到 backtest_report.json")
    
    print("\n=== 回测分析器演示完成 ===")


def demo_strategies():
    """策略演示"""
    print("\n=== 策略演示 ===")
    
    # 测试不同策略
    strategies = [
        ("演示策略", DemoBacktestStrategy, {"fast_window": 10, "slow_window": 20}),
        ("MACD策略", MACDBacktestStrategy, {"fast_period": 12, "slow_period": 26, "signal_period": 9}),
        ("RSI策略", RSIBacktestStrategy, {"rsi_period": 14, "overbought": 70, "oversold": 30})
    ]
    
    for strategy_name, strategy_class, params in strategies:
        print(f"\n测试{strategy_name}...")
        
        # 创建回测引擎
        engine = BacktestEngine()
        
        # 设置回测参数
        engine.set_parameters(
            vt_symbol="BTC/USDT:BINANCE",
            interval=Interval.HOUR,
            start=datetime(2023, 1, 1),
            end=datetime(2023, 1, 31)
        )
        
        # 添加策略
        engine.add_strategy(strategy_class, params)
        
        # 运行回测
        results = engine.run_backtesting()
        statistics = engine.calculate_statistics()
        
        # 打印结果
        print(f"总收益率: {statistics['total_return']:.2%}")
        print(f"年化收益率: {statistics['annual_return']:.2%}")
        print(f"最大回撤: {statistics['max_drawdown']:.2%}")
        print(f"夏普比率: {statistics['sharpe_ratio']:.2f}")
        print(f"总交易次数: {statistics['total_trades']}")
    
    print("\n=== 策略演示完成 ===")


def demo_data_loading():
    """数据加载演示"""
    print("\n=== 数据加载演示 ===")
    
    # 测试从API下载数据
    print("从Binance API下载数据...")
    try:
        bars = DataLoader.download_from_api(
            symbol="BTC/USDT",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 1, 3),
            interval="1h",
            source="binance"
        )
        print(f"下载的数据条数: {len(bars)}")
        if bars:
            print(f"第一条数据: {bars[0].datetime} - {bars[0].close_price}")
            print(f"最后一条数据: {bars[-1].datetime} - {bars[-1].close_price}")
    except Exception as e:
        print(f"下载数据失败: {e}")
        print("请确保已安装ccxt库")
    
    print("\n=== 数据加载演示完成 ===")


def main():
    """主函数"""
    print("回测模块演示")
    print("=" * 50)
    
    # 运行各个演示
    demo_backtest_engine()
    demo_data_loader()
    demo_backtest_analyzer()
    demo_strategies()
    demo_data_loading()
    
    print("\n" + "=" * 50)
    print("所有演示完成！")


if __name__ == "__main__":
    main()
