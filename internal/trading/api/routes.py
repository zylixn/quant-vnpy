"""
模拟盘交易API接口
"""

from flask_restx import Namespace, Resource, fields
from internal.trading.simulator.simulator import TradingSimulator

# 创建交易模拟器实例
simulator = TradingSimulator()

# 创建交易命名空间
trading_ns = Namespace('trading', description='交易相关操作')

# 定义响应模型
account_response = trading_ns.model('AccountResponse', {
    'balance': fields.Float(description='账户余额'),
    'available': fields.Float(description='可用资金'),
    'total_value': fields.Float(description='总市值'),
    'pnl': fields.Float(description='盈亏'),
    'pnl_ratio': fields.Float(description='盈亏比例')
})

position_response = trading_ns.model('PositionResponse', {
    'symbol': fields.String(description='合约代码'),
    'volume': fields.Integer(description='持仓量'),
    'avg_price': fields.Float(description='均价'),
    'current_price': fields.Float(description='当前价格'),
    'pnl': fields.Float(description='盈亏'),
    'pnl_ratio': fields.Float(description='盈亏比例')
})

order_response = trading_ns.model('OrderResponse', {
    'order_id': fields.String(description='订单ID'),
    'symbol': fields.String(description='合约代码'),
    'direction': fields.String(description='方向'),
    'offset': fields.String(description='开平'),
    'price': fields.Float(description='价格'),
    'volume': fields.Integer(description='数量'),
    'traded_volume': fields.Integer(description='成交数量'),
    'status': fields.String(description='状态'),
    'timestamp': fields.String(description='时间戳')
})

trade_response = trading_ns.model('TradeResponse', {
    'trade_id': fields.String(description='成交ID'),
    'order_id': fields.String(description='订单ID'),
    'symbol': fields.String(description='合约代码'),
    'direction': fields.String(description='方向'),
    'offset': fields.String(description='开平'),
    'price': fields.Float(description='价格'),
    'volume': fields.Integer(description='数量'),
    'timestamp': fields.String(description='时间戳')
})

order_request = trading_ns.model('OrderRequest', {
    'symbol': fields.String(description='合约代码', required=True),
    'price': fields.Float(description='价格', required=True),
    'volume': fields.Integer(description='数量', required=True)
})

reset_request = trading_ns.model('ResetRequest', {
    'initial_balance': fields.Float(description='初始资金')
})

price_request = trading_ns.model('PriceRequest', {
    'symbol': fields.String(description='合约代码', required=True),
    'price': fields.Float(description='价格', required=True)
})

response_message = trading_ns.model('ResponseMessage', {
    'message': fields.String(description='响应消息')
})

response_error = trading_ns.model('ResponseError', {
    'error': fields.String(description='错误消息')
})

order_response_message = trading_ns.model('OrderResponseMessage', {
    'order_id': fields.String(description='订单ID'),
    'message': fields.String(description='响应消息')
})

order_error_response = trading_ns.model('OrderErrorResponse', {
    'order_id': fields.String(description='订单ID'),
    'error': fields.String(description='错误消息')
})


@trading_ns.route('/account')
class Account(Resource):
    """账户相关操作"""
    
    @trading_ns.doc('get_account')
    @trading_ns.marshal_with(account_response)
    def get(self):
        """获取账户信息"""
        account_info = simulator.get_account_info()
        return account_info


@trading_ns.route('/positions')
class Positions(Resource):
    """持仓相关操作"""
    
    @trading_ns.doc('get_positions')
    @trading_ns.marshal_with(position_response, as_list=True)
    def get(self):
        """获取持仓信息"""
        positions = simulator.get_positions()
        return positions


@trading_ns.route('/orders')
class Orders(Resource):
    """订单相关操作"""
    
    @trading_ns.doc('get_orders')
    @trading_ns.marshal_with(order_response, as_list=True)
    def get(self):
        """获取订单信息"""
        orders = simulator.get_orders()
        return orders


@trading_ns.route('/trades')
class Trades(Resource):
    """成交相关操作"""
    
    @trading_ns.doc('get_trades')
    @trading_ns.marshal_with(trade_response, as_list=True)
    def get(self):
        """获取成交信息"""
        trades = simulator.get_trades()
        return trades


@trading_ns.route('/order/buy')
class BuyOrder(Resource):
    """买入操作"""
    
    @trading_ns.doc('buy_order')
    @trading_ns.expect(order_request)
    @trading_ns.marshal_with(order_response_message, code=200)
    @trading_ns.marshal_with(order_error_response, code=400)
    def post(self):
        """买入"""
        data = trading_ns.payload
        symbol = data.get('symbol')
        price = data.get('price')
        volume = data.get('volume')
        
        if not all([symbol, price, volume]):
            return {'error': '缺少必要参数', 'order_id': ''}, 400
        
        order_id, error = simulator.buy(symbol, price, volume)
        
        if error:
            return {'error': error, 'order_id': order_id}, 400
        
        return {'order_id': order_id, 'message': '下单成功'}


@trading_ns.route('/order/sell')
class SellOrder(Resource):
    """卖出操作"""
    
    @trading_ns.doc('sell_order')
    @trading_ns.expect(order_request)
    @trading_ns.marshal_with(order_response_message, code=200)
    @trading_ns.marshal_with(order_error_response, code=400)
    def post(self):
        """卖出"""
        data = trading_ns.payload
        symbol = data.get('symbol')
        price = data.get('price')
        volume = data.get('volume')
        
        if not all([symbol, price, volume]):
            return {'error': '缺少必要参数', 'order_id': ''}, 400
        
        order_id, error = simulator.sell(symbol, price, volume)
        
        if error:
            return {'error': error, 'order_id': order_id}, 400
        
        return {'order_id': order_id, 'message': '下单成功'}


@trading_ns.route('/order/cancel/<order_id>')
class CancelOrder(Resource):
    """撤单操作"""
    
    @trading_ns.doc('cancel_order')
    @trading_ns.marshal_with(response_message, code=200)
    @trading_ns.marshal_with(response_error, code=400)
    def post(self, order_id):
        """撤单"""
        success = simulator.cancel_order(order_id)
        if success:
            return {'message': '撤单成功'}
        else:
            return {'error': '撤单失败'}, 400


@trading_ns.route('/reset')
class ResetSimulator(Resource):
    """重置模拟器操作"""
    
    @trading_ns.doc('reset_simulator')
    @trading_ns.expect(reset_request)
    @trading_ns.marshal_with(response_message)
    def post(self):
        """重置模拟器"""
        data = trading_ns.payload
        initial_balance = data.get('initial_balance')
        
        simulator.reset(initial_balance)
        return {'message': '重置成功'}


@trading_ns.route('/price')
class SetPrice(Resource):
    """设置价格操作"""
    
    @trading_ns.doc('set_price')
    @trading_ns.expect(price_request)
    @trading_ns.marshal_with(response_message, code=200)
    @trading_ns.marshal_with(response_error, code=400)
    def post(self):
        """设置合约价格"""
        data = trading_ns.payload
        symbol = data.get('symbol')
        price = data.get('price')
        
        if not all([symbol, price]):
            return {'error': '缺少必要参数'}, 400
        
        simulator.set_symbol_price(symbol, price)
        return {'message': '设置成功'}
