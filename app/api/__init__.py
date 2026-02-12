"""
API模块初始化文件
注意：此文件已不再使用，API注册已移至app/__init__.py
"""

# 已移至app/__init__.py
# from flask import Blueprint
# from flask_restx import Api
# from app.api.resources import health
# from internal.trading.api.routes import trading_bp
# from internal.risk.routes import risk_bp
# from internal.fetcher.api.routes import fetcher_bp
# from internal.task.api.routes import tasks_bp
# 
# api_bp = Blueprint('api', __name__)
# 
# # 创建Flask-RESTX Api对象，用于生成Swagger文档
# api = Api(
#     api_bp,
#     version='1.0',
#     title='Quant-VNPY API',
#     description='量化交易系统API文档',
#     doc='/docs',  # Swagger文档的访问路径，去掉末尾的斜杠
#     prefix='/api'
# )
# 
# # 注册健康检查命名空间
# api.add_namespace(health.health_ns, path='/health')
# 
# # 注册其他Blueprint
# api_bp.register_blueprint(trading_bp, url_prefix='/trading')
# api_bp.register_blueprint(risk_bp, url_prefix='/risk')
# api_bp.register_blueprint(fetcher_bp, url_prefix='/fetcher')
# api_bp.register_blueprint(tasks_bp, url_prefix='/tasks')
