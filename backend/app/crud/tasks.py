from typing import List, Dict, Any, Optional
from app.api.v1.schemas.tasks import TaskCreate, Task
from app.db import mongodb

class CRUDTask:
    async def get_all(self) -> List[Dict[str, Any]]:
        return await mongodb.get_tasks_mongodb()

    async def create(self, task: TaskCreate) -> Dict[str, Any]:
        return await mongodb.create_task_mongodb(task)

task = CRUDTask()