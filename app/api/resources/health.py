from flask_restx import Namespace, Resource, fields

# 创建健康检查命名空间
health_ns = Namespace('health', description='健康检查相关操作')

# 定义响应模型
health_response = health_ns.model('HealthResponse', {
    'status': fields.String(description='服务状态'),
    'message': fields.String(description='服务消息')
})


@health_ns.route('/check')
class HealthCheck(Resource):
    """健康检查端点"""
    
    @health_ns.doc('health_check')
    @health_ns.marshal_with(health_response)
    def get(self):
        """检查服务健康状态"""
        return {
            'status': 'ok',
            'message': 'Service is running'
        }
