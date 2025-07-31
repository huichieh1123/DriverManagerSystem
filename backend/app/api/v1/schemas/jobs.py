from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

class JobStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    assigned_driver_id: Optional[str] = None # Changed from int to str
    created_by_dispatcher_id: Optional[str] = None # Changed from int to str
    company_id: Optional[str] = None # Changed from int to str
    company_name: Optional[str] = None # New: Name of the company this job belongs to
    is_public: bool = False # New field: whether the job is public for drivers to claim

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    assigned_driver_id: Optional[str] = None # Changed from int to str
    is_public: Optional[bool] = None # New field for updating public status

class Job(JobBase):
    id: str # Changed from int to str

    class Config:
        orm_mode = True