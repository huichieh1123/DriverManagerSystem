from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.jobs import Job, JobCreate, JobUpdate, JobStatus
from app.api.v1.schemas.users import User, RoleType
from app.crud import job
from app.api.v1.endpoints.users import get_current_user # Keep this for now, will refactor users.py later

router = APIRouter()

# Dependency to check if the current user is a driver
async def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.DRIVER.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can perform this action")
    return current_user

@router.post("/jobs/{job_id}/claim", response_model=Job)
async def claim_job(
    job_id: str, # Changed from int to str
    current_driver: User = Depends(get_current_driver)
):
    job_item = await job.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job_item["status"] != JobStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not in pending status and cannot be claimed.")

    if not job_item["is_public"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This job is not public and cannot be claimed.")

    if job_item["assigned_driver_id"] is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is already assigned to a driver.")

    # Update job status and assigned driver
    job_update_data = JobUpdate(
        status=JobStatus.ASSIGNED,
        assigned_driver_id=current_driver.id
    )
    updated_job = await job.update(job_id, job_update_data)

    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to claim job")

    return updated_job

@router.put("/jobs/{job_id}/complete", response_model=Job)
async def complete_job(
    job_id: str, # Changed from int to str
    current_driver: User = Depends(get_current_driver)
):
    job_item = await job.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job_item["assigned_driver_id"] != current_driver.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not assigned to this job.")

    if job_item["status"] == JobStatus.COMPLETED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is already completed.")

    if job_item["status"] == JobStatus.CANCELLED.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_BAD_REQUEST, detail="Job has been cancelled.")

    # Update job status to completed
    job_update_data = JobUpdate(
        status=JobStatus.COMPLETED
    )
    updated_job = await job.update(job_id, job_update_data)

    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to complete job")

    return updated_job
