from pydantic import BaseModel

# Shared properties
class TaskBase(BaseModel):
    title: str
    completed: bool = False

# Properties to receive on item creation
class TaskCreate(TaskBase):
    pass

# Properties to return to client
class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True
