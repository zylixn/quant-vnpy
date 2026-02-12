"""
任务管理器
"""

import uuid
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from internal.task.tasks import Task


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self.running_tasks: Dict[str, threading.Thread] = {}
    
    def create_task(self, task: Task) -> str:
        """创建任务"""
        with self.lock:
            task_id = task.task_id
            self.tasks[task_id] = task
            return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """列出任务"""
        if status:
            return [task for task in self.tasks.values() if task.status == status]
        return list(self.tasks.values())
    
    def start_task(self, task_id: str) -> bool:
        """启动任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status == "running":
            return False
        
        # 创建线程执行任务
        thread = threading.Thread(target=self._execute_task, args=(task_id,))
        thread.daemon = True
        
        with self.lock:
            task.status = "running"
            task.start_time = datetime.now()
            self.running_tasks[task_id] = thread
        
        thread.start()
        return True
    
    def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status != "running":
            return False
        
        # 这里只能标记任务为停止状态，实际停止需要在任务执行中检查
        task.stop_flag = True
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id in self.running_tasks:
            return False
        
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
        return False
    
    def _execute_task(self, task_id: str):
        """执行任务"""
        task = self.get_task(task_id)
        if not task:
            return
        
        try:
            task.execute()
            
            with self.lock:
                task.status = "completed"
                task.end_time = datetime.now()
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
        except Exception as e:
            with self.lock:
                task.status = "failed"
                task.error = str(e)
                task.end_time = datetime.now()
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task = self.get_task(task_id)
        if not task:
            return {"error": "Task not found"}
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status,
            "progress": task.progress,
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "end_time": task.end_time.isoformat() if task.end_time else None,
            "result": task.result,
            "error": task.error
        }
    
    def wait_for_task(self, task_id: str, timeout: Optional[int] = None) -> bool:
        """等待任务完成"""
        start_time = time.time()
        
        while True:
            task = self.get_task(task_id)
            if not task:
                return False
            
            if task.status in ["completed", "failed"]:
                return True
            
            if timeout and time.time() - start_time > timeout:
                return False
            
            time.sleep(0.1)
    
    def create_and_start_task(self, task: Task) -> str:
        """创建并启动任务"""
        task_id = self.create_task(task)
        self.start_task(task_id)
        return task_id
