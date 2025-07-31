from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.jobs import Job, JobCreate, JobUpdate, JobStatus
from app.api.v1.schemas.users import User, RoleType
from app.crud import job, user
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()

@router.get("/jobs/", response_model=List[Job])
async def read_jobs(
    assigned_driver_id: Optional[str] = None, # Changed from int to str
    created_by_dispatcher_id: Optional[str] = None, # Changed from int to str
    is_public: Optional[bool] = None,
    status: Optional[JobStatus] = None,
    company_id: Optional[str] = None # Changed from int to str
):
    return await job.get_all(assigned_driver_id=assigned_driver_id, created_by_dispatcher_id=created_by_dispatcher_id, is_public=is_public, status=status, company_id=company_id)

@router.get("/jobs/{job_id}", response_model=Job)
async def read_job_by_id(job_id: str): # Changed from int to str
    job_item = await job.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job_item

@router.put("/jobs/{job_id}", response_model=Job)
async def update_job(
    job_id: str, # Changed from int to str
    job_in: JobUpdate,
    current_user: User = Depends(get_current_user) # Any logged in user can update for now
):
    existing_job = await job.get_by_id(job_id)
    if not existing_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    # Basic authorization: only dispatcher who created it or admin can update
    # For simplicity, allowing any logged-in user to update for now.
    # In a real app, you'd add more granular checks.

    updated_job = await job.update(job_id, job_in)
    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update job")
    return updated_job

@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    job_item = await job.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    # Authorization: Only the dispatcher who created the job or a company admin can delete it.
    is_creator = job_item.get("created_by_dispatcher_id") == current_user.id
    is_company_admin = RoleType.COMPANY.value in current_user.roles and job_item.get("company_id") == current_user.id

    if not (is_creator or is_company_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this job.")

    deleted = await job.delete(job_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete job.")
    return

@router.put("/jobs/{job_id}/assign", response_model=Job)
async def assign_job(
    job_id: str,
    driver_id: str, # Driver ID to assign the job to
    current_user: User = Depends(get_current_user) # Changed from get_current_dispatcher
):
    if RoleType.DISPATCHER.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only dispatchers can assign jobs.")

    job_item = await job.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    if job_item["status"] != JobStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not in pending status and cannot be assigned.")

    target_driver = await user.get_by_id(driver_id)
    if not target_driver or RoleType.DRIVER.value not in target_driver.get("roles", []):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target driver not found or not a driver.")

    # Optional: Check if dispatcher is authorized to assign this job (e.g., created it or belongs to same company)
    # For simplicity, we assume any dispatcher can assign any pending job for now.

    job_update_data = JobUpdate(
        status=JobStatus.ASSIGNED,
        assigned_driver_id=driver_id
    )
    updated_job = await job.update(job_id, job_update_data)

    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign job.")

    return updated_job

@router.put("/jobs/{job_id}/cancel", response_model=Job)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    job_item = await job.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    # Authorization: Only the dispatcher who created the job or a company admin can cancel it.
    is_creator = job_item.get("created_by_dispatcher_id") == current_user.id
    is_company_admin = RoleType.COMPANY.value in current_user.roles and job_item.get("company_id") == current_user.id

    if not (is_creator or is_company_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this job.")

    if job_item["status"] == JobStatus.COMPLETED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is already completed.")

    if job_item["status"] == JobStatus.CANCELLED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has been cancelled.")

    # Update job status to cancelled
    job_update_data = JobUpdate(
        status=JobStatus.CANCELLED
    )
    updated_job = await job.update(job_id, job_update_data)

    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel job.")

    return updated_job
