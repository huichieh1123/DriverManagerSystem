from typing import List, Dict, Any, Optional
from app.api.v1.schemas.jobs import JobCreate, Job, JobUpdate, JobStatus
from app.db import mongodb

class CRUDJob:
    async def get_all(self, assigned_driver_id: Optional[int] = None, created_by_dispatcher_id: Optional[int] = None, is_public: Optional[bool] = None, status: Optional[JobStatus] = None, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        # Convert JobStatus enum to string value for mongodb filter
        status_str = status.value if isinstance(status, JobStatus) else status
        return await mongodb.get_jobs_mongodb(assigned_driver_id, created_by_dispatcher_id, is_public, status_str, company_id)

    async def get_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_job_by_id_mongodb(job_id)

    async def create(self, job: JobCreate, created_by_dispatcher_id: int, company_id: Optional[int] = None, company_name: Optional[str] = None) -> Dict[str, Any]:
        return await mongodb.create_job_mongodb(job, created_by_dispatcher_id, company_id, company_name)

    async def update(self, job_id: str, job_in: JobUpdate) -> Optional[Dict[str, Any]]:
        return await mongodb.update_job_mongodb(job_id, job_in.dict(exclude_unset=True))

    async def delete(self, job_id: str) -> bool:
        return await mongodb.delete_job_mongodb(job_id)

job = CRUDJob()
