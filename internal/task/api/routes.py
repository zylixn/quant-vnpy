"""
任务管理API路由
"""

from flask_restx import Namespace, Resource, fields
from typing import Dict, List, Optional
from datetime import datetime

from internal.task.task_manager import TaskManager
from internal.task.tasks import (
    DataFetchingTask, 
    StrategyExecutionTask, 
    RiskAssessmentTask, 
    TradingTask, 
    BacktestTask, 
    FullWorkflowTask,
    StockAnalysisTask
)
from internal.utils import get_logger, set_req_id, clear_req_id

# 创建任务管理命名空间
tasks_ns = Namespace('tasks', description='任务管理相关操作')

# 定义响应模型
task_response = tasks_ns.model('TaskResponse', {
    'task_id': fields.String(description='任务ID'),
    'name': fields.String(description='任务名称'),
    'status': fields.String(description='任务状态'),
    'created_at': fields.String(description='创建时间'),
    'started_at': fields.String(description='开始时间'),
    'completed_at': fields.String(description='完成时间'),
    'result': fields.Raw(description='任务结果'),
    'error': fields.String(description='错误信息')
})

task_list_response = tasks_ns.model('TaskListResponse', {
    'tasks': fields.List(fields.Nested(task_response), description='任务列表')
})

create_task_request = tasks_ns.model('CreateTaskRequest', {
    'task_type': fields.String(description='任务类型', required=True),
    'params': fields.Raw(description='任务参数', default={})
})

create_task_response = tasks_ns.model('CreateTaskResponse', {
    'task_id': fields.String(description='任务ID')
})

status_response = tasks_ns.model('StatusResponse', {
    'status': fields.String(description='任务状态'),
    'progress': fields.Float(description='任务进度'),
    'error': fields.String(description='错误信息')
})

success_response = tasks_ns.model('SuccessResponse', {
    'success': fields.Boolean(description='操作是否成功')
})

response_error = tasks_ns.model('ResponseError', {
    'error': fields.String(description='错误消息')
})

# 全局任务管理器实例
task_manager = TaskManager()


@tasks_ns.route('/create')
class CreateTask(Resource):
    """创建任务操作"""
    
    @tasks_ns.doc('create_task')
    @tasks_ns.expect(create_task_request)
    @tasks_ns.marshal_with(create_task_response, code=200)
    @tasks_ns.marshal_with(response_error, code=400)
    @tasks_ns.marshal_with(response_error, code=500)
    def post(self):
        """创建任务"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            data = tasks_ns.payload
            task_type = data.get('task_type')
            params = data.get('params', {})
            
            if not task_type:
                return {'error': 'Task type is required'}, 400
            
            if task_type == "data_fetching":
                task = DataFetchingTask(params)
            elif task_type == "strategy_execution":
                task = StrategyExecutionTask(params)
            elif task_type == "risk_assessment":
                task = RiskAssessmentTask(params)
            elif task_type == "trading":
                task = TradingTask(params)
            elif task_type == "backtest":
                task = BacktestTask(params)
            elif task_type == "full_workflow":
                task = FullWorkflowTask(params)
            elif task_type == "stock_analysis":
                task = StockAnalysisTask(params)
            else:
                return {'error': 'Invalid task type'}, 400
            
            task_id = task_manager.create_task(task)
            return {'task_id': task_id}
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@tasks_ns.route('/list')
class ListTasks(Resource):
    """列出任务操作"""
    
    @tasks_ns.doc('list_tasks')
    @tasks_ns.param('status', '任务状态')
    @tasks_ns.marshal_with(task_list_response, code=200)
    @tasks_ns.marshal_with(response_error, code=500)
    def get(self):
        """列出任务"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            status = tasks_ns.request.args.get('status')
            tasks = task_manager.list_tasks(status=status)
            return {'tasks': [task.to_dict() for task in tasks]}
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@tasks_ns.route('/get/<task_id>')
class GetTask(Resource):
    """获取任务操作"""
    
    @tasks_ns.doc('get_task')
    @tasks_ns.param('task_id', '任务ID')
    @tasks_ns.marshal_with(task_response, code=200)
    @tasks_ns.marshal_with(response_error, code=404)
    @tasks_ns.marshal_with(response_error, code=500)
    def get(self, task_id):
        """获取任务"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            task = task_manager.get_task(task_id)
            if not task:
                return {'error': 'Task not found'}, 404
            return task.to_dict()
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@tasks_ns.route('/start/<task_id>')
class StartTask(Resource):
    """启动任务操作"""
    
    @tasks_ns.doc('start_task')
    @tasks_ns.param('task_id', '任务ID')
    @tasks_ns.marshal_with(success_response, code=200)
    @tasks_ns.marshal_with(response_error, code=500)
    def post(self, task_id):
        """启动任务"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            result = task_manager.start_task(task_id)
            return {'success': result}
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@tasks_ns.route('/stop/<task_id>')
class StopTask(Resource):
    """停止任务操作"""
    
    @tasks_ns.doc('stop_task')
    @tasks_ns.param('task_id', '任务ID')
    @tasks_ns.marshal_with(success_response, code=200)
    @tasks_ns.marshal_with(response_error, code=500)
    def post(self, task_id):
        """停止任务"""
        req_id = None
        try:
            # 生成 reqId
            req_id = set_req_id()
            
            result = task_manager.stop_task(task_id)
            return {'success': result}
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            # 清除 reqId
            if req_id:
                clear_req_id()


@tasks_ns.route('/delete/<task_id>')
class DeleteTask(Resource):
    """删除任务操作"""
    
    @tasks_ns.doc('delete_task')
    @tasks_ns.param('task_id', '任务ID')
    @tasks_ns.marshal_with(success_response, code=200)
    @tasks_ns.marshal_with(response_error, code=500)
    def delete(self, task_id):
        """删除任务"""
        try:
            result = task_manager.delete_task(task_id)
            return {'success': result}
        except Exception as e:
            return {'error': str(e)}, 500


@tasks_ns.route('/status/<task_id>')
class GetTaskStatus(Resource):
    """获取任务状态操作"""
    
    @tasks_ns.doc('get_task_status')
    @tasks_ns.param('task_id', '任务ID')
    @tasks_ns.marshal_with(status_response, code=200)
    @tasks_ns.marshal_with(response_error, code=404)
    @tasks_ns.marshal_with(response_error, code=500)
    def get(self, task_id):
        """获取任务状态"""
        try:
            status = task_manager.get_task_status(task_id)
            if "error" in status:
                return {'error': status["error"]}, 404
            return status
        except Exception as e:
            return {'error': str(e)}, 500


@tasks_ns.route('/create_and_start')
class CreateAndStartTask(Resource):
    """创建并启动任务操作"""
    
    @tasks_ns.doc('create_and_start_task')
    @tasks_ns.expect(create_task_request)
    @tasks_ns.marshal_with(create_task_response, code=200)
    @tasks_ns.marshal_with(response_error, code=400)
    @tasks_ns.marshal_with(response_error, code=500)
    def post(self):
        """创建并启动任务"""
        try:
            data = tasks_ns.payload
            task_type = data.get('task_type')
            params = data.get('params', {})
            
            if not task_type:
                return {'error': 'Task type is required'}, 400
            
            if task_type == "data_fetching":
                task = DataFetchingTask(params)
            elif task_type == "strategy_execution":
                task = StrategyExecutionTask(params)
            elif task_type == "risk_assessment":
                task = RiskAssessmentTask(params)
            elif task_type == "trading":
                task = TradingTask(params)
            elif task_type == "backtest":
                task = BacktestTask(params)
            elif task_type == "full_workflow":
                task = FullWorkflowTask(params)
            elif task_type == "stock_analysis":
                task = StockAnalysisTask(params)
            else:
                return {'error': 'Invalid task type'}, 400
            
            task_id = task_manager.create_and_start_task(task)
            return {'task_id': task_id}
        except Exception as e:
            return {'error': str(e)}, 500
