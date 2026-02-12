"""
股票分析任务演示

演示如何使用StockAnalysisTask任务类来分析股票并找出适合买入的股票
"""

import time
from datetime import datetime, timedelta
from vnpy.trader.constant import Exchange, Interval
from internal.task.task_manager import TaskManager
from internal.task.tasks import StockAnalysisTask


def demo_stock_analysis():
    """演示股票分析任务"""
    print("=== 股票分析任务演示 ===")
    print(f"当前时间: {datetime.now().isoformat()}")
    
    # 初始化任务管理器
    task_manager = TaskManager()
    
    # 创建股票分析任务
    # 分析的股票列表（可以根据需要修改）
    symbols = ["600000", "600519", "000001", "000858", "601318", "600036", "601166", "600276", "000333", "002594"]
    
    # 任务参数
    task_params = {
        "symbols": symbols,  # 要分析的股票列表
        "lookback_days": 60,  # 回溯天数
        "interval": Interval.DAILY,  # K线周期
        "exchange": Exchange.SSE,  # 交易所
        "strategies": ["value", "growth", "technical", "momentum", "mean_reversion"],  # 使用的策略
        "top_n": 5  # 推荐的股票数量
    }
    
    # 创建任务
    stock_analysis_task = StockAnalysisTask(params=task_params)
    
    # 添加并启动任务
    task_id = task_manager.create_and_start_task(stock_analysis_task)
    print(f"\n创建股票分析任务，任务ID: {task_id}")
    
    # 等待任务完成
    print("\n任务执行中，请稍候...")
    
    # 检查任务状态
    while True:
        task_status = task_manager.get_task_status(task_id)
        status = task_status.get("status")
        progress = task_status.get("progress", 0)
        
        print(f"\r任务状态: {status}, 进度: {progress:.1f}%", end="")
        
        if status in ["completed", "failed"]:
            break
        
        time.sleep(1)
    
    print()
    
    # 获取任务结果
    task = task_manager.get_task(task_id)
    if task and task.status == "completed":
        result = task.result
        print("\n=== 股票分析结果 ===")
        print(f"分析时间: {result['date']}")
        print(f"分析股票数量: {result['total_stocks_analyzed']}")
        print(f"推荐股票数量: {result['top_n']}")
        print(f"回溯天数: {result['lookback_days']}")
        
        print("\n=== 推荐买入的股票 ===")
        for i, stock in enumerate(result['top_stocks'], 1):
            print(f"\n{i}. 股票代码: {stock['symbol']}")
            print(f"   综合得分: {stock['score']:.2f}")
            print(f"   当前价格: {stock['price']:.2f}")
            print(f"   各策略得分:")
            for strategy, score in stock['strategies'].items():
                print(f"     - {strategy}: {score:.2f}")
            if 'return_1d' in stock:
                print(f"   1日收益率: {stock['return_1d']:.2%}")
            if 'return_7d' in stock:
                print(f"   7日收益率: {stock['return_7d']:.2%}")
            if 'return_30d' in stock:
                print(f"   30日收益率: {stock['return_30d']:.2%}")
        
        print("\n=== 分析报告 ===")
        report = result['report']
        print(f"\n摘要:")
        print(f"  分析股票总数: {report['summary']['total_stocks_analyzed']}")
        print(f"  平均得分: {report['summary']['average_score']:.2f}")
        print(f"  推荐股票数量: {report['summary']['top_stock_count']}")
        
        print(f"\n策略表现:")
        for strategy, score in report['strategy_performance'].items():
            print(f"  - {strategy}: {score:.2f}")
        
        print(f"\n推荐建议:")
        print(report['recommendation'])
    else:
        print("\n任务执行失败:")
        print(task.error if task else "未知错误")
    
    print("\n=== 演示完成 ===")


def demo_periodic_stock_analysis():
    """演示定期执行股票分析任务"""
    print("\n=== 定期股票分析任务演示 ===")
    print("此功能可以设置为定期执行，例如每天收盘后自动分析股票")
    
    # 这里只是演示如何设置定期任务
    # 实际应用中，可以使用crontab（Linux）或任务计划程序（Windows）来定期执行
    
    print("\n定期执行建议:")
    print("1. 每天收盘后（15:30左右）执行一次")
    print("2. 每周执行一次全面分析")
    print("3. 根据市场情况调整分析参数")


if __name__ == "__main__":
    # 执行股票分析任务演示
    demo_stock_analysis()
    
    # 演示定期执行功能
    demo_periodic_stock_analysis()
