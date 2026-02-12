"""
风险评估API接口
"""

from flask_restx import Namespace, Resource, fields
from internal.risk.risk_assessor import (
    AccountRiskAssessor,
    StrategyRiskAssessor,
    MarketRiskAssessor,
    RiskManager
)

# 创建全局风险评估实例
account_assessor = AccountRiskAssessor()
risk_manager = RiskManager(account_assessor)
strategy_assessors = {}

# 创建风险评估命名空间
risk_ns = Namespace('risk', description='风险评估相关操作')

# 定义响应模型
account_risk_response = risk_ns.model('AccountRiskResponse', {
    'total_trades': fields.Integer(description='总交易次数'),
    'win_rate': fields.Float(description='胜率'),
    'average_win': fields.Float(description='平均盈利'),
    'average_loss': fields.Float(description='平均亏损'),
    'profit_factor': fields.Float(description='盈利因子'),
    'sharpe_ratio': fields.Float(description='夏普比率'),
    'max_drawdown': fields.Float(description='最大回撤'),
    'current_balance': fields.Float(description='当前余额'),
    'total_pnl': fields.Float(description='总盈亏')
})

strategy_risk_response = risk_ns.model('StrategyRiskResponse', {
    'strategy_name': fields.String(description='策略名称'),
    'total_trades': fields.Integer(description='总交易次数'),
    'win_rate': fields.Float(description='胜率'),
    'average_win': fields.Float(description='平均盈利'),
    'average_loss': fields.Float(description='平均亏损'),
    'profit_factor': fields.Float(description='盈利因子'),
    'sharpe_ratio': fields.Float(description='夏普比率'),
    'max_drawdown': fields.Float(description='最大回撤'),
    'total_pnl': fields.Float(description='总盈亏')
})

market_volatility_response = risk_ns.model('MarketVolatilityResponse', {
    'volatility': fields.Float(description='波动率'),
    'std_dev': fields.Float(description='标准差'),
    'max_drawdown': fields.Float(description='最大回撤'),
    'drawdown_duration': fields.Integer(description='回撤持续时间'),
    'risk_metrics': fields.Raw(description='风险指标')
})

market_trend_response = risk_ns.model('MarketTrendResponse', {
    'trend_strength': fields.Float(description='趋势强度'),
    'trend_direction': fields.String(description='趋势方向'),
    'adx': fields.Float(description='ADX指标'),
    'trend_indicators': fields.Raw(description='趋势指标')
})

risk_limits_response = risk_ns.model('RiskLimitsResponse', {
    'max_position_percentage': fields.Float(description='单品种最大持仓比例'),
    'max_volatility': fields.Float(description='最大波动率'),
    'max_drawdown': fields.Float(description='最大回撤'),
    'max_leverage': fields.Float(description='最大杠杆'),
    'max_trades_per_day': fields.Integer(description='每日最大交易次数'),
    'max_loss_per_day': fields.Float(description='每日最大亏损'),
    'max_loss_per_week': fields.Float(description='每周最大亏损'),
    'max_loss_per_month': fields.Float(description='每月最大亏损')
})

risk_report_response = risk_ns.model('RiskReportResponse', {
    'account_metrics': fields.Nested(account_risk_response, description='账户指标'),
    'risk_limits': fields.Nested(risk_limits_response, description='风险限制'),
    'position_exposure': fields.Float(description='持仓敞口'),
    'market_conditions': fields.Raw(description='市场条件'),
    'recommendations': fields.List(fields.String, description='建议')
})

position_size_response = risk_ns.model('PositionSizeResponse', {
    'position_size': fields.Float(description='持仓大小')
})

risk_exposure_response = risk_ns.model('RiskExposureResponse', {
    'exposure_ratio': fields.Float(description='敞口比例'),
    'warnings': fields.List(fields.String, description='警告信息')
})

response_message = risk_ns.model('ResponseMessage', {
    'message': fields.String(description='响应消息')
})

response_error = risk_ns.model('ResponseError', {
    'error': fields.String(description='错误消息')
})

# 定义请求模型
prices_request = risk_ns.model('PricesRequest', {
    'prices': fields.List(fields.Float, description='价格列表', required=True)
})

risk_limits_request = risk_ns.model('RiskLimitsRequest', {
    'max_position_percentage': fields.Float(description='单品种最大持仓比例'),
    'max_volatility': fields.Float(description='最大波动率'),
    'max_drawdown': fields.Float(description='最大回撤'),
    'max_leverage': fields.Float(description='最大杠杆'),
    'max_trades_per_day': fields.Integer(description='每日最大交易次数'),
    'max_loss_per_day': fields.Float(description='每日最大亏损'),
    'max_loss_per_week': fields.Float(description='每周最大亏损'),
    'max_loss_per_month': fields.Float(description='每月最大亏损')
})

position_size_request = risk_ns.model('PositionSizeRequest', {
    'account_balance': fields.Float(description='账户余额', required=True),
    'atr': fields.Float(description='ATR值', required=True),
    'risk_per_trade': fields.Float(description='每笔交易风险')
})

risk_exposure_request = risk_ns.model('RiskExposureRequest', {
    'position_value': fields.Float(description='持仓价值', required=True),
    'total_equity': fields.Float(description='总权益', required=True)
})

balance_request = risk_ns.model('BalanceRequest', {
    'balance': fields.Float(description='账户余额', required=True)
})

trade_request = risk_ns.model('TradeRequest', {
    'trade': fields.Raw(description='交易记录', required=True),
    'strategy_name': fields.String(description='策略名称')
})

position_request = risk_ns.model('PositionRequest', {
    'symbol': fields.String(description='合约代码', required=True),
    'volume': fields.Integer(description='持仓量'),
    'avg_price': fields.Float(description='均价')
})

strategy_params_request = risk_ns.model('StrategyParamsRequest', {
    'strategy_name': fields.String(description='策略名称', required=True),
    'params': fields.Raw(description='策略参数', required=True)
})

strategy_indicators_request = risk_ns.model('StrategyIndicatorsRequest', {
    'strategy_name': fields.String(description='策略名称', required=True),
    'indicators': fields.Raw(description='策略指标', required=True)
})


@risk_ns.route('/account')
class AccountRisk(Resource):
    """账户风险评估操作"""
    
    @risk_ns.doc('get_account_risk')
    @risk_ns.marshal_with(account_risk_response)
    def get(self):
        """获取账户风险评估"""
        metrics = account_assessor.assess_account_risk()
        return metrics


@risk_ns.route('/strategy/<strategy_name>')
class StrategyRisk(Resource):
    """策略风险评估操作"""
    
    @risk_ns.doc('get_strategy_risk')
    @risk_ns.marshal_with(strategy_risk_response)
    def get(self, strategy_name):
        """获取策略风险评估"""
        if strategy_name not in strategy_assessors:
            strategy_assessors[strategy_name] = StrategyRiskAssessor(strategy_name)
        
        assessor = strategy_assessors[strategy_name]
        metrics = assessor.assess_strategy_risk()
        return metrics


@risk_ns.route('/market/volatility')
class MarketVolatility(Resource):
    """市场波动率评估操作"""
    
    @risk_ns.doc('assess_market_volatility')
    @risk_ns.expect(prices_request)
    @risk_ns.marshal_with(market_volatility_response, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """评估市场波动率"""
        data = risk_ns.payload
        prices = data.get('prices', [])
        
        if not isinstance(prices, list) or not all(isinstance(p, (int, float)) for p in prices):
            return {'error': 'Invalid prices format'}, 400
        
        metrics = MarketRiskAssessor.assess_market_volatility(prices)
        return metrics


@risk_ns.route('/market/trend')
class MarketTrend(Resource):
    """市场趋势评估操作"""
    
    @risk_ns.doc('assess_market_trend')
    @risk_ns.expect(prices_request)
    @risk_ns.marshal_with(market_trend_response, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """评估市场趋势强度"""
        data = risk_ns.payload
        prices = data.get('prices', [])
        
        if not isinstance(prices, list) or not all(isinstance(p, (int, float)) for p in prices):
            return {'error': 'Invalid prices format'}, 400
        
        metrics = MarketRiskAssessor.assess_trend_strength(prices)
        return metrics


@risk_ns.route('/limits')
class RiskLimits(Resource):
    """风险限制操作"""
    
    @risk_ns.doc('get_risk_limits')
    @risk_ns.marshal_with(risk_limits_response)
    def get(self):
        """获取风险限制"""
        limits = risk_manager.risk_limits
        return limits
    
    @risk_ns.doc('set_risk_limits')
    @risk_ns.expect(risk_limits_request)
    @risk_ns.marshal_with(response_message, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """设置风险限制"""
        data = risk_ns.payload
        if not isinstance(data, dict):
            return {'error': 'Invalid data format'}, 400
        
        risk_manager.set_risk_limits(data)
        return {'message': 'Risk limits updated successfully'}


@risk_ns.route('/report')
class RiskReport(Resource):
    """风险报告操作"""
    
    @risk_ns.doc('get_risk_report')
    @risk_ns.marshal_with(risk_report_response)
    def get(self):
        """获取风险报告"""
        report = risk_manager.generate_risk_report()
        return report


@risk_ns.route('/position/size')
class PositionSize(Resource):
    """持仓大小计算操作"""
    
    @risk_ns.doc('calculate_position_size')
    @risk_ns.expect(position_size_request)
    @risk_ns.marshal_with(position_size_response, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """计算合理持仓大小"""
        data = risk_ns.payload
        account_balance = data.get('account_balance', 0)
        atr = data.get('atr', 0)
        risk_per_trade = data.get('risk_per_trade')
        
        if account_balance <= 0 or atr <= 0:
            return {'error': 'Invalid parameters'}, 400
        
        position_size = risk_manager.calculate_position_size(
            account_balance, atr, risk_per_trade
        )
        
        return {'position_size': position_size}


@risk_ns.route('/exposure')
class RiskExposure(Resource):
    """风险敞口评估操作"""
    
    @risk_ns.doc('assess_risk_exposure')
    @risk_ns.expect(risk_exposure_request)
    @risk_ns.marshal_with(risk_exposure_response, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """评估风险敞口"""
        data = risk_ns.payload
        position_value = data.get('position_value', 0)
        total_equity = data.get('total_equity', 0)
        
        if total_equity <= 0:
            return {'error': 'Invalid parameters'}, 400
        
        warnings = risk_manager.assess_risk_exposure(position_value, total_equity)
        exposure_ratio = position_value / total_equity if total_equity > 0 else 0
        return {'exposure_ratio': exposure_ratio, 'warnings': warnings}


@risk_ns.route('/update/balance')
class UpdateBalance(Resource):
    """更新账户余额操作"""
    
    @risk_ns.doc('update_balance')
    @risk_ns.expect(balance_request)
    @risk_ns.marshal_with(response_message, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """更新账户余额"""
        data = risk_ns.payload
        balance = data.get('balance', 0)
        
        if balance < 0:
            return {'error': 'Invalid balance'}, 400
        
        account_assessor.update_balance(balance)
        return {'message': 'Balance updated successfully'}


@risk_ns.route('/update/trade')
class AddTrade(Resource):
    """添加交易记录操作"""
    
    @risk_ns.doc('add_trade')
    @risk_ns.expect(trade_request)
    @risk_ns.marshal_with(response_message, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """添加交易记录"""
        data = risk_ns.payload
        trade = data.get('trade', {})
        
        if not isinstance(trade, dict):
            return {'error': 'Invalid trade format'}, 400
        
        account_assessor.add_trade(trade)
        
        # 如果指定了策略名称，也添加到策略评估器
        strategy_name = data.get('strategy_name')
        if strategy_name:
            if strategy_name not in strategy_assessors:
                strategy_assessors[strategy_name] = StrategyRiskAssessor(strategy_name)
            strategy_assessors[strategy_name].add_trade(trade)
        
        return {'message': 'Trade added successfully'}


@risk_ns.route('/update/position')
class UpdatePosition(Resource):
    """更新持仓操作"""
    
    @risk_ns.doc('update_position')
    @risk_ns.expect(position_request)
    @risk_ns.marshal_with(response_message, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """更新持仓"""
        data = risk_ns.payload
        symbol = data.get('symbol')
        volume = data.get('volume', 0)
        avg_price = data.get('avg_price', 0)
        
        if not symbol:
            return {'error': 'Symbol is required'}, 400
        
        account_assessor.update_position(symbol, volume, avg_price)
        return {'message': 'Position updated successfully'}


@risk_ns.route('/update/strategy/params')
class UpdateStrategyParams(Resource):
    """更新策略参数操作"""
    
    @risk_ns.doc('update_strategy_params')
    @risk_ns.expect(strategy_params_request)
    @risk_ns.marshal_with(response_message, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """更新策略参数"""
        data = risk_ns.payload
        strategy_name = data.get('strategy_name')
        params = data.get('params', {})
        
        if not strategy_name:
            return {'error': 'Strategy name is required'}, 400
        
        if strategy_name not in strategy_assessors:
            strategy_assessors[strategy_name] = StrategyRiskAssessor(strategy_name)
        
        assessor = strategy_assessors[strategy_name]
        assessor.set_strategy_params(params)
        
        return {'message': 'Strategy parameters updated successfully'}


@risk_ns.route('/update/strategy/indicators')
class UpdateStrategyIndicators(Resource):
    """更新策略指标操作"""
    
    @risk_ns.doc('update_strategy_indicators')
    @risk_ns.expect(strategy_indicators_request)
    @risk_ns.marshal_with(response_message, code=200)
    @risk_ns.marshal_with(response_error, code=400)
    def post(self):
        """更新策略指标"""
        data = risk_ns.payload
        strategy_name = data.get('strategy_name')
        indicators = data.get('indicators', {})
        
        if not strategy_name:
            return {'error': 'Strategy name is required'}, 400
        
        if strategy_name not in strategy_assessors:
            strategy_assessors[strategy_name] = StrategyRiskAssessor(strategy_name)
        
        assessor = strategy_assessors[strategy_name]
        assessor.set_indicators(indicators)
        
        return {'message': 'Strategy indicators updated successfully'}
