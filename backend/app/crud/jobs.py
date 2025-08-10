from typing import List, Dict, Any, Optional
from app.api.v1.schemas.jobs import JobCreate, Job, JobUpdate, JobStatus, JobType # Import JobType
from app.db import mongodb
from app.crud.users import user
from app.crud.vehicle import vehicle

class CRUDJob:
    async def get_all(self, assigned_driver_id: Optional[str] = None, created_by_dispatcher_id: Optional[str] = None, is_public: Optional[bool] = None, status: Optional[JobStatus] = None, company_id: Optional[str] = None, job_type: Optional[JobType] = None) -> List[Dict[str, Any]]:
        # Convert JobStatus enum to string value for mongodb filter
        status_str = status.value if isinstance(status, JobStatus) else status
        job_type_str = job_type.value if isinstance(job_type, JobType) else job_type
        return await mongodb.get_jobs_mongodb(assigned_driver_id, created_by_dispatcher_id, is_public, status_str, company_id, job_type_str)

    async def get_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_job_by_id_mongodb(job_id)

    async def get_by_copied_job_id(self, copied_job_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_job_by_copied_job_id_mongodb(copied_job_id)

    async def create(self, job: JobCreate, created_by_dispatcher_id: str, company_id: Optional[str] = None, company_name: Optional[str] = None) -> Dict[str, Any]:
        return await mongodb.create_job_mongodb(job, created_by_dispatcher_id, company_id, company_name)

    async def create_copied_job(self, original_job: Dict[str, Any], driver_id: str, vehicle_id: str, driver_name: str, driver_phone: str) -> Optional[Dict[str, Any]]:
        return await mongodb.create_copied_job_mongodb(original_job, driver_id, vehicle_id, driver_name, driver_phone)

    async def create_job_application(self, original_job: Dict[str, Any], driver_id: str, vehicle_id: str, driver_name: str, driver_phone: str) -> Optional[Dict[str, Any]]:
        return await mongodb.create_job_application_mongodb(original_job, driver_id, vehicle_id, driver_name, driver_phone)

    async def update(self, job_id: str, job_in: JobUpdate) -> Optional[Dict[str, Any]]:
        return await mongodb.update_job_mongodb(job_id, job_in.dict(exclude_unset=True))

    async def delete(self, job_id: str) -> bool:
        return await mongodb.delete_job_mongodb(job_id)

    async def accept_copied_job(self, copied_job_id: str, driver_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.accept_copied_job_mongodb(copied_job_id, driver_id)

    async def reject_copied_job(self, copied_job_id: str) -> bool:
        return await mongodb.reject_copied_job_mongodb(copied_job_id)

    async def delete_driver_application(self, copied_job_id: str, driver_id: str) -> bool:
        return await mongodb.delete_driver_application_mongodb(copied_job_id, driver_id)

job = CRUDJob()
