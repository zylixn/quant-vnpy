"""
回测API路由
"""

from flask_restx import Namespace, Resource, fields
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from internal.backtest import BacktestEngine, DataLoader, BacktestAnalyzer
from internal.backtest.strategies import DemoBacktestStrategy, MACDBacktestStrategy, RSIBacktestStrategy

# 创建回测命名空间
backtest_ns = Namespace('backtest', description='回测相关操作')

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
    'symbol': fields.String(description='交易标的'),
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
    'symbol': fields.String(description='交易标的', default='BTC/USDT'),
    'exchange': fields.String(description='交易所', default='BINANCE'),
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
    @backtest_ns.marshal_with(run_backtest_response, code=200)
    @backtest_ns.marshal_with(response_error, code=400)
    @backtest_ns.marshal_with(response_error, code=500)
    def post(self):
        """运行回测"""
        try:
            data = backtest_ns.payload
            
            # 解析参数
            symbol = data.get('symbol', 'BTC/USDT')
            exchange = data.get('exchange', 'BINANCE')
            interval = data.get('interval', '1m')
            start = datetime.fromisoformat(data.get('start', '2023-01-01T00:00:00'))
            end = datetime.fromisoformat(data.get('end', '2023-01-31T23:59:59'))
            strategy_name = data.get('strategy', 'demo')
            strategy_params = data.get('params', {})
            
            # 创建回测引擎
            engine = BacktestEngine()
            
            # 设置回测参数
            engine.set_parameters(
                vt_symbol=f"{symbol}:{exchange}",
                interval=Interval(interval),
                start=start,
                end=end
            )
            
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
            results = engine.run_backtesting()
            statistics = engine.calculate_statistics()
            
            # 构建响应
            response = {
                'status': 'success',
                'statistics': statistics,
                'trades': [
                    {
                        'trade_id': t.trade_id,
                        'symbol': t.symbol,
                        'direction': t.direction.value,
                        'offset': t.offset.value,
                        'price': t.price,
                        'volume': t.volume,
                        'trade_time': t.trade_time.isoformat(),
                        'pnl': t.pnl
                    }
                    for t in engine.get_trades()
                ]
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500


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
