"""
股票数据获取API路由
"""

from flask_restx import Namespace, Resource, fields
from datetime import datetime
from vnpy.trader.constant import Exchange, Interval
from internal.fetcher import StockFetcher
from internal.utils import get_logger, set_req_id, clear_req_id

# 获取日志器
logger = get_logger('fetcher.api')

# 创建股票数据获取命名空间
fetcher_ns = Namespace('fetcher', description='股票数据获取相关操作')

# 定义响应模型
stock_data_response = fetcher_ns.model('StockDataResponse', {
    'datetime': fields.String(description='时间'),
    'open': fields.Float(description='开盘价'),
    'high': fields.Float(description='最高价'),
    'low': fields.Float(description='最低价'),
    'close': fields.Float(description='收盘价'),
    'volume': fields.Float(description='成交量'),
    'open_interest': fields.Float(description='持仓量')
})

stock_data_list_response = fetcher_ns.model('StockDataListResponse', {
    'status': fields.String(description='状态'),
    'data': fields.List(fields.Nested(stock_data_response), description='股票数据'),
    'count': fields.Integer(description='数据条数')
})

stock_list_response = fetcher_ns.model('StockListResponse', {
    'status': fields.String(description='状态'),
    'data': fields.List(fields.String, description='股票列表'),
    'count': fields.Integer(description='股票数量')
})

stock_info_response = fetcher_ns.model('StockInfoResponse', {
    'status': fields.String(description='状态'),
    'data': fields.Raw(description='股票信息')
})

realtime_data_response = fetcher_ns.model('RealtimeDataResponse', {
    'status': fields.String(description='状态'),
    'data': fields.Raw(description='实时数据'),
    'message': fields.String(description='消息')
})

index_components_response = fetcher_ns.model('IndexComponentsResponse', {
    'status': fields.String(description='状态'),
    'data': fields.List(fields.String, description='成分股列表'),
    'count': fields.Integer(description='成分股数量')
})

download_response = fetcher_ns.model('DownloadResponse', {
    'status': fields.String(description='状态'),
    'message': fields.String(description='消息'),
    'count': fields.Integer(description='下载数量')
})

response_error = fetcher_ns.model('ResponseError', {
    'error': fields.String(description='错误消息')
})

# 定义请求模型
stock_data_request = fetcher_ns.model('StockDataRequest', {
    'symbol': fields.String(description='股票代码', default='600000'),
    'start': fields.String(description='开始时间', default='2023-01-01T00:00:00'),
    'end': fields.String(description='结束时间', default='2023-01-31T23:59:59'),
    'interval': fields.String(description='时间周期', default='1d'),
    'source': fields.String(description='数据源', default='api'),
    'exchange': fields.String(description='交易所', default='SSE'),
    'api_name': fields.String(description='API名称', default='tushare'),
    'params': fields.Raw(description='额外参数', default={})
})

download_request = fetcher_ns.model('DownloadRequest', {
    'symbol': fields.String(description='股票代码', default='600000'),
    'start': fields.String(description='开始时间', default='2023-01-01T00:00:00'),
    'end': fields.String(description='结束时间', default='2023-01-31T23:59:59'),
    'filename': fields.String(description='文件名', default='600000.csv'),
    'interval': fields.String(description='时间周期', default='1d'),
    'exchange': fields.String(description='交易所', default='SSE'),
    'api_name': fields.String(description='API名称', default='tushare'),
    'format': fields.String(description='格式(csv/json/database)', default='csv')
})

batch_download_request = fetcher_ns.model('BatchDownloadRequest', {
    'symbols': fields.List(fields.String, description='股票代码列表', default=['600000', '600036']),
    'start': fields.String(description='开始时间', default='2023-01-01T00:00:00'),
    'end': fields.String(description='结束时间', default='2023-01-31T23:59:59'),
    'output_dir': fields.String(description='输出目录', default='data'),
    'interval': fields.String(description='时间周期', default='1d'),
    'exchange': fields.String(description='交易所', default='SSE'),
    'api_name': fields.String(description='API名称', default='tushare'),
    'format': fields.String(description='格式(csv/json/database)', default='csv')
})


@fetcher_ns.route('/stock/data')
class StockData(Resource):
    """获取股票数据操作"""
    
    @fetcher_ns.doc('get_stock_data')
    @fetcher_ns.expect(stock_data_request)
    # @fetcher_ns.marshal_with(stock_data_list_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def post(self):
        """获取股票数据"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            data = fetcher_ns.payload
            
            # 解析参数
            symbol = data.get('symbol', '600000')
            start = datetime.fromisoformat(data.get('start', '2023-01-01T00:00:00'))
            end = datetime.fromisoformat(data.get('end', '2023-01-31T23:59:59'))
            interval = data.get('interval', '1d')
            source = data.get('source', 'api')
            exchange = data.get('exchange', 'SSE')
            api_name = data.get('api_name', 'tushare')
            
            # 转换参数
            interval_map = {
                '1m': Interval.MINUTE,
                '5m': Interval.MINUTE,
                '15m': Interval.MINUTE,
                '30m': Interval.MINUTE,
                '1h': Interval.HOUR,
                '1d': Interval.DAILY,
                '1w': Interval.WEEKLY,
            }
            
            exchange_map = {
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            
            interval = interval_map.get(interval, Interval.DAILY)
            exchange = exchange_map.get(exchange, Exchange.SSE)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            
            # 获取数据
            bars = fetcher.get_stock_data(
                symbol=symbol,
                start=start,
                end=end,
                interval=interval,
                source=source,
                exchange=exchange,
                api_name=api_name,
                **data.get('params', {})
            )
            logger.info(f"获取股票数据成功, 股票代码: {symbol}, 开始时间: {start}, 结束时间: {end}, 时间周期: {interval}, 数据源: {source}, 交易所: {exchange}, API名称: {api_name}, 数据量: {len(bars)}")
            # 构建响应
            response = {
                'status': 'success',
                'data': [
                    {
                        'datetime': bar.datetime.isoformat(),
                        'open': bar.open_price,
                        'high': bar.high_price,
                        'low': bar.low_price,
                        'close': bar.close_price,
                        'volume': bar.volume,
                        'open_interest': bar.open_interest
                    }
                    for bar in bars
                ],
                'count': len(bars)
            }
            logger.info(f"返回股票数据成功, response: {response}")
            return response
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@fetcher_ns.route('/stock/list')
class StockList(Resource):
    """获取股票列表操作"""
    
    @fetcher_ns.doc('get_stock_list')
    @fetcher_ns.param('exchange', '交易所', default='SSE')
    @fetcher_ns.param('source', '数据源', default='api')
    # @fetcher_ns.marshal_with(stock_list_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def get(self):
        """获取股票列表"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            exchange = fetcher_ns.request.args.get('exchange', 'SSE')
            source = fetcher_ns.request.args.get('source', 'api')
            
            # 转换参数
            exchange_map = {
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            
            exchange = exchange_map.get(exchange, Exchange.SSE)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            
            # 获取股票列表
            stocks = fetcher.get_stock_list(
                exchange=exchange,
                source=source
            )
            
            # 构建响应
            response = {
                'status': 'success',
                'data': stocks,
                'count': len(stocks)
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@fetcher_ns.route('/stock/info')
class StockInfo(Resource):
    """获取股票信息操作"""
    
    @fetcher_ns.doc('get_stock_info')
    @fetcher_ns.param('symbol', '股票代码', default='600000')
    @fetcher_ns.param('exchange', '交易所', default='SSE')
    @fetcher_ns.param('source', '数据源', default='api')
    # @fetcher_ns.marshal_with(stock_info_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def get(self):
        """获取股票信息"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            symbol = fetcher_ns.request.args.get('symbol', '600000')
            exchange = fetcher_ns.request.args.get('exchange', 'SSE')
            source = fetcher_ns.request.args.get('source', 'api')
            
            # 转换参数
            exchange_map = {
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            
            exchange = exchange_map.get(exchange, Exchange.SSE)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            
            # 获取股票信息
            info = fetcher.get_stock_info(
                symbol=symbol,
                exchange=exchange,
                source=source
            )
            
            # 构建响应
            response = {
                'status': 'success',
                'data': info
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@fetcher_ns.route('/stock/realtime')
class RealtimeData(Resource):
    """获取实时数据操作"""
    
    @fetcher_ns.doc('get_realtime_data')
    @fetcher_ns.param('symbol', '股票代码', default='600000')
    @fetcher_ns.param('exchange', '交易所', default='SSE')
    @fetcher_ns.param('api_name', 'API名称', default='tushare')
    # @fetcher_ns.marshal_with(realtime_data_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def get(self):
        """获取实时数据"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            symbol = fetcher_ns.request.args.get('symbol', '600000')
            exchange = fetcher_ns.request.args.get('exchange', 'SSE')
            api_name = fetcher_ns.request.args.get('api_name', 'tushare')
            
            # 转换参数
            exchange_map = {
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            
            exchange = exchange_map.get(exchange, Exchange.SSE)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            
            # 获取实时数据
            tick = fetcher.get_realtime_data(
                symbol=symbol,
                exchange=exchange,
                api_name=api_name
            )
            
            # 构建响应
            if tick:
                response = {
                    'status': 'success',
                    'data': {
                        'datetime': tick.datetime.isoformat(),
                        'last_price': tick.last_price,
                        'volume': tick.volume,
                        'bid_price_1': tick.bid_price_1,
                        'bid_volume_1': tick.bid_volume_1,
                        'ask_price_1': tick.ask_price_1,
                        'ask_volume_1': tick.ask_volume_1
                    }
                }
            else:
                response = {
                    'status': 'success',
                    'data': None,
                    'message': '未获取到实时数据'
                }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@fetcher_ns.route('/stock/index/components')
class IndexComponents(Resource):
    """获取指数成分股操作"""
    
    @fetcher_ns.doc('get_index_components')
    @fetcher_ns.param('index_symbol', '指数代码', default='000001.SH')
    @fetcher_ns.param('date', '日期', default=datetime.now().isoformat())
    @fetcher_ns.param('api_name', 'API名称', default='tushare')
    # @fetcher_ns.marshal_with(index_components_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def get(self):
        """获取指数成分股"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            index_symbol = fetcher_ns.request.args.get('index_symbol', '000001.SH')
            date = fetcher_ns.request.args.get('date', datetime.now().isoformat())
            api_name = fetcher_ns.request.args.get('api_name', 'tushare')
            
            # 转换参数
            date = datetime.fromisoformat(date)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            
            # 获取指数成分股
            components = fetcher.get_index_components(
                index_symbol=index_symbol,
                date=date,
                api_name=api_name
            )
            
            # 构建响应
            response = {
                'status': 'success',
                'data': components,
                'count': len(components)
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@fetcher_ns.route('/stock/download')
class DownloadStockData(Resource):
    """下载股票数据操作"""
    
    @fetcher_ns.doc('download_stock_data')
    @fetcher_ns.expect(download_request)
    # @fetcher_ns.marshal_with(download_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def post(self):
        """下载股票数据"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            data = fetcher_ns.payload
            
            # 解析参数
            symbol = data.get('symbol', '600000')
            start = datetime.fromisoformat(data.get('start', '2023-01-01T00:00:00'))
            end = datetime.fromisoformat(data.get('end', '2023-01-31T23:59:59'))
            filename = data.get('filename', f'{symbol}.csv')
            interval = data.get('interval', '1d')
            exchange = data.get('exchange', 'SSE')
            api_name = data.get('api_name', 'tushare')
            format = data.get('format', 'csv')
            
            # 转换参数
            interval_map = {
                '1m': Interval.MINUTE,
                '5m': Interval.MINUTE,
                '15m': Interval.MINUTE,
                '30m': Interval.MINUTE,
                '1h': Interval.HOUR,
                '1d': Interval.DAILY,
                '1w': Interval.WEEKLY,
            }
            
            exchange_map = {
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            
            interval = interval_map.get(interval, Interval.DAILY)
            exchange = exchange_map.get(exchange, Exchange.SSE)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            
            # 下载并保存数据
            fetcher.download_and_save(
                symbol=symbol,
                start=start,
                end=end,
                filename=filename,
                interval=interval,
                exchange=exchange,
                api_name=api_name,
                format=format,
            )
            
            # 构建响应
            response = {
                'status': 'success',
                'message': '数据已保存',
                'format': format
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@fetcher_ns.route('/stock/batch/download')
class BatchDownloadStockData(Resource):
    """批量下载股票数据操作"""
    
    @fetcher_ns.doc('batch_download_stock_data')
    @fetcher_ns.expect(batch_download_request)
    # @fetcher_ns.marshal_with(download_response, code=200)
    # @fetcher_ns.marshal_with(response_error, code=500)
    def post(self):
        """批量下载股票数据"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            data = fetcher_ns.payload
            
            # 解析参数
            symbols = data.get('symbols', ['600000', '600036'])
            start = datetime.fromisoformat(data.get('start', '2023-01-01T00:00:00'))
            end = datetime.fromisoformat(data.get('end', '2023-01-31T23:59:59'))
            output_dir = data.get('output_dir', 'data')
            interval = data.get('interval', '1d')
            exchange = data.get('exchange', 'SSE')
            api_name = data.get('api_name', 'tushare')
            format = data.get('format', 'csv')
            # 打印参数
            logger.info(f"Received batch download request: symbols={symbols}, start={start}, end={end}, output_dir={output_dir}, interval={interval}, exchange={exchange}, api_name={api_name}, format={format}")
            # 转换参数
            interval_map = {
                '1m': Interval.MINUTE,
                '5m': Interval.MINUTE,
                '15m': Interval.MINUTE,
                '30m': Interval.MINUTE,
                '1h': Interval.HOUR,
                '1d': Interval.DAILY,
                '1w': Interval.WEEKLY,
            }
            
            exchange_map = {
                'SSE': Exchange.SSE,
                'SZSE': Exchange.SZSE
            }
            
            interval = interval_map.get(interval, Interval.DAILY)
            exchange = exchange_map.get(exchange, Exchange.SSE)
            
            # 创建股票数据获取器
            fetcher = StockFetcher()
            # 批量下载数据
            fetcher.batch_download(
                symbols=symbols,
                start=start,
                end=end,
                output_dir=output_dir,
                interval=interval,
                exchange=exchange,
                api_name=api_name,
                format=format,
            )
            
            # 构建响应
            response = {
                'status': 'success',
                'message': f'批量下载完成，数据已保存到: {output_dir}',
                'count': len(symbols)
            }
            
            return response
        except Exception as e:
            return {'error': str(e)}, 500
