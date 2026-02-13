"""
回测API路由
"""

from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta
from vnpy.trader.constant import Exchange, Interval
from internal.backtest import BacktestEngine, DataLoader, BacktestAnalyzer
from internal.backtest.strategies import DemoBacktestStrategy, MACDBacktestStrategy, RSIBacktestStrategy
from internal.utils import get_logger, set_req_id, clear_req_id

# 创建回测命名空间
backtest_ns = Namespace('backtest', description='回测相关操作')
logger = get_logger('backtest.api')
# 定义响应模型
trade_response = backtest_ns.model('TradeResponse', {
    'trade_id': fields.String(description='交易ID'),
    'symbol': fields.String(description='交易标的'),
    'direction': fields.String(description='交易方向'),
    'offset': fields.String(description='交易开平'),
    'price': fields.Float(description='交易价格'),
    'volume': fields.Float(description='交易量'),
    'trade_time': fields.String(description='交易时间'),
    'pnl': fields.Float(description='盈亏')
})

run_backtest_response = backtest_ns.model('RunBacktestResponse', {
    'status': fields.String(description='状态'),
    'statistics': fields.Raw(description='回测统计'),
    'trades': fields.List(fields.Nested(trade_response), description='交易列表')
})

strategy_parameter = backtest_ns.model('StrategyParameter', {
    'name': fields.String(description='参数名称'),
    'type': fields.String(description='参数类型'),
    'default': fields.Raw(description='默认值'),
    'description': fields.String(description='参数描述')
})

strategy_response = backtest_ns.model('StrategyResponse', {
    'name': fields.String(description='策略名称'),
    'display_name': fields.String(description='策略显示名称'),
    'description': fields.String(description='策略描述'),
    'parameters': fields.List(fields.Nested(strategy_parameter), description='策略参数')
})

analyze_response = backtest_ns.model('AnalyzeResponse', {
    'status': fields.String(description='状态'),
    'statistics': fields.Raw(description='统计指标'),
    'trade_analysis': fields.Raw(description='交易分析')
})

data_response = backtest_ns.model('DataResponse', {
    'datetime': fields.String(description='时间'),
    'open': fields.Float(description='开盘价'),
    'high': fields.Float(description='最高价'),
    'low': fields.Float(description='最低价'),
    'close': fields.Float(description='收盘价'),
    'volume': fields.Integer(description='成交量')
})

download_data_response = backtest_ns.model('DownloadDataResponse', {
    'status': fields.String(description='状态'),
    'data': fields.List(fields.Nested(data_response), description='数据列表'),
    'count': fields.Integer(description='数据条数')
})

parameters_response = backtest_ns.model('ParametersResponse', {
    'symbol': fields.String(description='交易标的或者股票代码'),
    'exchange': fields.String(description='交易所'),
    'interval': fields.String(description='时间周期'),
    'start': fields.String(description='开始时间'),
    'end': fields.String(description='结束时间'),
    'strategy': fields.String(description='策略名称'),
    'params': fields.Raw(description='策略参数')
})

response_error = backtest_ns.model('ResponseError', {
    'error': fields.String(description='错误消息')
})

# 定义请求模型
run_backtest_request = backtest_ns.model('RunBacktestRequest', {
    'symbol': fields.String(description='交易标的或者股票代码', default='601179'),
    'exchange': fields.String(description='交易所', default='SSE'),
    'interval': fields.String(description='时间周期', default='1m'),
    'start': fields.String(description='开始时间', default='2023-01-01T00:00:00'),
    'end': fields.String(description='结束时间', default='2023-01-31T23:59:59'),
    'strategy': fields.String(description='策略名称', default='demo'),
    'params': fields.Raw(description='策略参数', default={})
})

analyze_request = backtest_ns.model('AnalyzeRequest', {
    'results': fields.Raw(description='回测结果', required=True),
    'trades': fields.List(fields.Raw, description='交易列表', default=[])
})

download_data_request = backtest_ns.model('DownloadDataRequest', {
    'symbol': fields.String(description='交易标的', default='BTC/USDT'),
    'start': fields.String(description='开始时间', default='2023-01-01T00:00:00'),
    'end': fields.String(description='结束时间', default='2023-01-31T23:59:59'),
    'interval': fields.String(description='时间周期', default='1m'),
    'source': fields.String(description='数据源', default='binance')
})


@backtest_ns.route('/run')
class RunBacktest(Resource):
    """运行回测操作"""
    
    @backtest_ns.doc('run_backtest')
    @backtest_ns.expect(run_backtest_request)
    # @backtest_ns.marshal_with(run_backtest_response, code=200)
    # @backtest_ns.marshal_with(response_error, code=400)
    # @backtest_ns.marshal_with(response_error, code=500)
    def post(self):
        """运行回测"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            data = backtest_ns.payload
            # 解析参数
            symbol = data.get('symbol', 'BTC/USDT')
            exchange = data.get('exchange', 'BINANCE')
            interval_str = data.get('interval', '1m')
            # 默认起始时间为前一个月，终止时间为当前时间
            default_end = datetime.now()
            default_start = default_end - timedelta(days=30)
            start = datetime.fromisoformat(data.get('start', default_start.isoformat()))
            end = datetime.fromisoformat(data.get('end', default_end.isoformat()))
            strategy_name = data.get('strategy', 'demo')
            strategy_params = data.get('params', {})
            # 记录参数值
            logger.info(f"Parameters: strategy_name={strategy_name}, symbol={symbol}, exchange={exchange}, interval={interval_str}, start={start}, end={end}")
            # 转换 interval 字符串到 Interval 枚举
            interval_map = {
                '1m': Interval.MINUTE,
                '5m': Interval.MINUTE,
                '15m': Interval.MINUTE,
                '30m': Interval.MINUTE,
                '1h': Interval.HOUR,
                'd': Interval.DAILY,
                '1d': Interval.DAILY,
                'w': Interval.WEEKLY,
                '1w': Interval.WEEKLY
            }
            interval = interval_map.get(interval_str, Interval.MINUTE)
            
            # 转换 exchange 字符串到 Exchange 枚举
            exchange_map = {
                'BINANCE': Exchange.LOCAL,
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            exchange = exchange_map.get(exchange, Exchange.LOCAL)
            
            # 创建回测引擎
            engine = BacktestEngine()
            
            # 设置回测参数
            try:
                # 使用 "." 作为分隔符，而不是 ":"，因为底层代码使用 split(".")
                engine.set_parameters(
                    vt_symbol=f"{symbol}.{exchange.value}",
                    interval=interval,
                    start=start,
                    end=end
                )
            except Exception as e:
                logger.error(f"Error in set_parameters(): {str(e)}")
                raise
            # 添加策略
            if strategy_name == 'demo':
                engine.add_strategy(DemoBacktestStrategy, strategy_params)
            elif strategy_name == 'macd':
                engine.add_strategy(MACDBacktestStrategy, strategy_params)
            elif strategy_name == 'rsi':
                engine.add_strategy(RSIBacktestStrategy, strategy_params)
            else:
                return {'error': 'Unknown strategy'}, 400
            # 运行回测
            try:
                engine.load_data()
                results = engine.run_backtesting()
            except Exception as e:
                logger.error(f"Error in run_backtesting(): {str(e)}")
                raise
            
            try:
                statistics = engine.calculate_statistics()
            except Exception as e:
                logger.error(f"Error in calculate_statistics(): {str(e)}")
                raise
            
            # 构建响应
            try:
                trades = engine.get_trades()
                logger.info(f"get_trades() returned type: {type(trades)}, length: {len(trades) if hasattr(trades, '__len__') else 'N/A'}")
                if trades and len(trades) > 0:
                    logger.info(f"First trade type: {type(trades[0])}, content: {trades[0]}")
            except Exception as e:
                logger.error(f"Error in get_trades(): {str(e)}")
                raise
            
            try:
                trades_list = []
                for t in trades:
                    trades_list.append({
                        'trade_id': t.tradeid,
                        'symbol': t.symbol,
                        'direction': t.direction.value,
                        'offset': t.offset.value,
                        'price': t.price,
                        'volume': t.volume,
                        'trade_time': t.datetime.isoformat()
                    })
                
                response = {
                    'status': 'success',
                    'statistics': statistics,
                    'trades': trades_list
                }
            except Exception as e:
                logger.error(f"Error building response: {str(e)}")
                raise
            
            return response
        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@backtest_ns.route('/strategies')
class GetStrategies(Resource):
    """获取可用策略列表操作"""
    
    @backtest_ns.doc('get_strategies')
    @backtest_ns.marshal_with(strategy_response, code=200)
    @backtest_ns.marshal_with(response_error, code=500)
    def get(self):
        """获取可用策略列表"""
        try:
            strategies = [
                {
                    'name': 'demo',
                    'display_name': '演示策略',
                    'description': '基于均线交叉的简单策略',
                    'parameters': [
                        {'name': 'fast_window', 'type': 'int', 'default': 10, 'description': '快速均线周期'},
                        {'name': 'slow_window', 'type': 'int', 'default': 20, 'description': '慢速均线周期'}
                    ]
                },
                {
                    'name': 'macd',
                    'display_name': 'MACD策略',
                    'description': '基于MACD指标的趋势策略',
                    'parameters': [
                        {'name': 'fast_period', 'type': 'int', 'default': 12, 'description': '快速周期'},
                        {'name': 'slow_period', 'type': 'int', 'default': 26, 'description': '慢速周期'},
                        {'name': 'signal_period', 'type': 'int', 'default': 9, 'description': '信号周期'}
                    ]
                },
                {
                    'name': 'rsi',
                    'display_name': 'RSI策略',
                    'description': '基于RSI指标的震荡策略',
                    'parameters': [
                        {'name': 'rsi_period', 'type': 'int', 'default': 14, 'description': 'RSI周期'},
                        {'name': 'overbought', 'type': 'int', 'default': 70, 'description': '超买阈值'},
                        {'name': 'oversold', 'type': 'int', 'default': 30, 'description': '超卖阈值'}
                    ]
                }
            ]
            
            return strategies
        except Exception as e:
            return {'error': str(e)}, 500


@backtest_ns.route('/analyze')
class AnalyzeResults(Resource):
    """分析回测结果操作"""
    
    @backtest_ns.doc('analyze_results')
    @backtest_ns.expect(analyze_request)
    @backtest_ns.marshal_with(analyze_response, code=200)
    @backtest_ns.marshal_with(response_error, code=500)
    def post(self):
        """分析回测结果"""
        try:
            data = backtest_ns.payload
            backtest_results = data.get('results')
            trades = data.get('trades', [])
            
            # 创建分析器
            analyzer = BacktestAnalyzer(backtest_results)
            analyzer.set_trades(trades)
            
            # 计算统计指标
            statistics = analyzer.calculate_statistics()
            trade_analysis = analyzer.analyze_trades()
            
            # 构建响应
            response = {
                'status': 'success',
                'statistics': statistics,
                'trade_analysis': trade_analysis
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500


@backtest_ns.route('/data/download')
class DownloadData(Resource):
    """下载回测数据操作"""
    
    @backtest_ns.doc('download_data')
    @backtest_ns.expect(download_data_request)
    @backtest_ns.marshal_with(download_data_response, code=200)
    @backtest_ns.marshal_with(response_error, code=500)
    def post(self):
        """下载回测数据"""
        try:
            data = backtest_ns.payload
            symbol = data.get('symbol', 'BTC/USDT')
            start = datetime.fromisoformat(data.get('start', '2023-01-01T00:00:00'))
            end = datetime.fromisoformat(data.get('end', '2023-01-31T23:59:59'))
            interval = data.get('interval', '1m')
            source = data.get('source', 'binance')
            
            # 下载数据
            bars = DataLoader.download_from_api(
                symbol=symbol,
                start=start,
                end=end,
                interval=interval,
                source=source
            )
            
            # 构建响应
            response = {
                'status': 'success',
                'data': [
                    {
                        'datetime': b.datetime.isoformat(),
                        'open': b.open_price,
                        'high': b.high_price,
                        'low': b.low_price,
                        'close': b.close_price,
                        'volume': b.volume
                    }
                    for b in bars
                ],
                'count': len(bars)
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500


@backtest_ns.route('/parameters')
class GetParameters(Resource):
    """获取回测参数模板操作"""
    
    @backtest_ns.doc('get_parameters')
    @backtest_ns.marshal_with(parameters_response, code=200)
    @backtest_ns.marshal_with(response_error, code=500)
    def get(self):
        """获取回测参数模板"""
        try:
            parameters = {
                'symbol': 'BTC/USDT',
                'exchange': 'BINANCE',
                'interval': '1m',
                'start': '2023-01-01T00:00:00',
                'end': '2023-01-31T23:59:59',
                'strategy': 'demo',
                'params': {
                    'fast_window': 10,
                    'slow_window': 20
                }
            }
            
            return parameters
        except Exception as e:
            return {'error': str(e)}, 500
