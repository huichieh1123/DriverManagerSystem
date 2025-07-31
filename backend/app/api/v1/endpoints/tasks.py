from fastapi import APIRouter, HTTPException
from typing import List
from app.api.v1.schemas.tasks import Task, TaskCreate
from app.crud import task

router = APIRouter()

@router.get("/tasks", response_model=List[Task])
def read_tasks():
    return task.get_all()

@router.post("/tasks", response_model=Task, status_code=201)
def create_task(task_in: TaskCreate):
    new_task = task.create(task_in)
    return new_task
