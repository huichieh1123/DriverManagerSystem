from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from app.api.v1.schemas.jobs import Job, JobCreate, JobUpdate, JobStatus, JobSummary, JobType, DispatcherClaimRequest # Add DispatcherClaimRequest
from app.api.v1.schemas.users import User, RoleType
from app.crud.jobs import CRUDJob # Explicitly import CRUDJob
from app.crud import user
from app.crud.vehicle import vehicle
from app.db import mongodb
from app.api.v1.endpoints.users import get_current_user, get_current_dispatcher, get_current_driver

router = APIRouter()

# Create an instance of CRUDJob outside the functions
crud_job_instance = CRUDJob()

@router.get("/export", response_class=StreamingResponse)
async def export_jobs_to_excel(
    current_user: User = Depends(get_current_user),
    company_id: Optional[str] = None,
    created_by_dispatcher_id: Optional[str] = None,
    username: Optional[str] = None # Added to accept username query parameter
):
    query_params = {}
    if RoleType.COMPANY.value in current_user.roles:
        query_params["company_id"] = current_user.id
    elif RoleType.DISPATCHER.value in current_user.roles:
        query_params["created_by_dispatcher_id"] = current_user.id
    else: # Driver or other roles
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to export jobs.")


    jobs_data = await crud_job_instance.get_all(**query_params)
    if not jobs_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found to export.")

    df = pd.DataFrame(jobs_data)

    # Create an in-memory bytes buffer for the Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Jobs')
    
    output.seek(0);

    headers = {
        'Content-Disposition': 'attachment; filename="jobs_export.xlsx"',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }

    return StreamingResponse(output, headers=headers)

@router.get("/", response_model=List[Job])
async def read_jobs(
    assigned_driver_id: Optional[str] = None, # Changed from int to str
    created_by_dispatcher_id: Optional[str] = None, # Changed from int to str
    is_public: Optional[bool] = None,
    status: Optional[JobStatus] = None,
    company_id: Optional[str] = None, # Changed from int to str
    job_type: Optional[JobType] = None # Add job_type parameter
):
    print(f"Type of crud_job_instance object: {type(crud_job_instance)}") # Diagnostic print
    query_params = {
        "assigned_driver_id": assigned_driver_id,
        "created_by_dispatcher_id": created_by_dispatcher_id,
        "is_public": is_public,
        "status": status,
        "company_id": company_id,
    }
    if job_type is not None: # Conditionally pass job_type
        query_params["job_type"] = job_type
    
    return await crud_job_instance.get_all(**query_params)

@router.get("/{job_id}", response_model=Job)
async def read_job_by_id(job_id: str): # Changed from int to str
    job_item = await crud_job_instance.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job_item

@router.post("/{job_id}/send_to_driver", response_model=Job)
async def send_job_to_driver(
    job_id: str,
    driver_id: str,
    vehicle_id: str,
    current_dispatcher: User = Depends(get_current_dispatcher)
):
    original_job = await crud_job_instance.get_by_id(job_id)
    if not original_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original job not found.")

    # Authorization: Ensure the dispatcher is the creator of the job or from the same company
    if original_job.get("created_by_dispatcher_id") != current_dispatcher.id and \
       (original_job.get("company_id") and original_job.get("company_id") != current_dispatcher.company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to send this job.")

    # Check if the driver exists and belongs to the same company (if applicable)
    target_driver = await user.get_by_id(driver_id)
    if not target_driver or RoleType.DRIVER.value not in target_driver.roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found or not a driver.")
    
    if original_job.get("company_id") and target_driver.company_id != original_job.get("company_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Driver does not belong to the same company as the job.")

    # Check if the vehicle belongs to the target driver
    driver_vehicles = await vehicle.get_all(owner_id=driver_id)
    if not any(v["id"] == vehicle_id for v in driver_vehicles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proposed vehicle does not belong to the target driver.")

    copied_job = await crud_job_instance.create_copied_job(
        original_job,
        driver_id,
        vehicle_id,
        target_driver.name or target_driver.username, # driver_name
        target_driver.driver_profile.phone_number if target_driver.driver_profile else None # driver_phone
    )
    if not copied_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create copied job.")
    return copied_job

@router.post("/{job_id}/apply", response_model=Job)
async def apply_for_job(
    job_id: str,
    vehicle_id: str,
    current_driver: User = Depends(get_current_driver) # Ensure user is a driver
):
    original_job = await crud_job_instance.get_by_id(job_id)
    if not original_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    if original_job.get("is_public") != True or original_job.get("status") != JobStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not a public pending job and cannot be applied for.")

    # Check if the proposed vehicle belongs to the current driver
    driver_vehicles = await vehicle.get_all(owner_id=current_driver.id)
    if not any(v["id"] == vehicle_id for v in driver_vehicles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proposed vehicle does not belong to you.")

    # Create a job application (a special type of copied job)
    job_application = await crud_job_instance.create_job_application(
        original_job,
        current_driver.id,
        vehicle_id,
        current_driver.name or current_driver.username, # driver_name
        current_driver.driver_profile.phone_number if current_driver.driver_profile else None # driver_phone
    )

    if not job_application:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create job application.")

    return job_application

@router.post("/{job_id}/dispatcher_claim", response_model=Job)
async def dispatcher_claim_public_job(
    job_id: str,
    claim_request: DispatcherClaimRequest,
    current_dispatcher: User = Depends(get_current_dispatcher)
):
    """
    Allows a dispatcher to claim a public job and assign it to a driver
    from their own company.
    """
    # 1. Get the original job and verify it's a public pending job
    original_job = await crud_job_instance.get_by_id(job_id)
    if not original_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if not original_job.get("is_public") or original_job.get("status") != JobStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not a public pending job.")

    # 2. Verify the dispatcher belongs to a company
    if not current_dispatcher.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dispatcher is not associated with a company.")

    # 3. Get the selected driver and verify they belong to the same company
    target_driver = await user.get_by_id(claim_request.driver_id)
    if not target_driver or RoleType.DRIVER.value not in target_driver['roles']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected user is not a valid driver.")
    if target_driver.get('company_id') != current_dispatcher.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Selected driver does not belong to your company.")

    # 4. Verify the selected vehicle belongs to the driver OR the dispatcher
    vehicle_to_check = await vehicle.get_by_id(claim_request.vehicle_id)
    if not vehicle_to_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected vehicle not found.")
    
    is_driver_vehicle = vehicle_to_check.get("owner_id") == claim_request.driver_id
    is_dispatcher_vehicle = vehicle_to_check.get("owner_id") == current_dispatcher.id
    
    if not (is_driver_vehicle or is_dispatcher_vehicle):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Selected vehicle does not belong to the selected driver or to you.")

    # 5. Create a copied job assigned to the driver
    driver_profile = target_driver.get('driver_profile') or {}
    copied_job = await crud_job_instance.create_copied_job(
        original_job=original_job,
        driver_id=claim_request.driver_id,
        vehicle_id=claim_request.vehicle_id,
        driver_name=target_driver.get('name') or target_driver.get('username'),
        driver_phone=driver_profile.get("phone_number")
    )

    if not copied_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create copied job for driver.")

    return copied_job

@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: str, # Changed from int to str
    job_in: JobUpdate,
    current_user: User = Depends(get_current_user) # Any logged in user can update for now
):
    existing_job = await crud_job_instance.get_by_id(job_id)
    if not existing_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    
    # Basic authorization: only dispatcher who created it or admin can update
    # For simplicity, allowing any logged-in user to update for now.
    # In a real app, you'd add more granular checks.

    updated_job = await crud_job_instance.update(job_id, job_in);
    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update job")
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    job_item = await crud_job_instance.get_by_id(job_id)
    if not job_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    # Authorization: Only the dispatcher who created the job or a company admin can delete it.
    is_creator = job_item.get("created_by_dispatcher_id") == current_user.id
    is_company_admin = RoleType.COMPANY.value in current_user.roles and job_item.get("company_id") == current_user.id

    if not (is_creator or is_company_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this job.")

    deleted = await crud_job_instance.delete(job_id);
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete job.")
    return

@router.put("/{copied_job_id}/accept", response_model=Job)
async def accept_copied_job(
    copied_job_id: str,
    current_dispatcher: User = Depends(get_current_dispatcher) # Only dispatcher can accept applications/copied jobs
):
    print(f"[accept_copied_job] Accepting copied job with ID: {copied_job_id}")
    
    # Ensure the copied job exists and is for this dispatcher's company
    copied_job_item = await crud_job_instance.get_by_copied_job_id(copied_job_id)
    if not copied_job_item or copied_job_item.get("job_type") not in [JobType.COPIED.value, JobType.APPLICATION.value]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or invalid type.")
    
    # Authorization: Ensure the dispatcher is the creator of the original job or from the same company
    original_job_id = copied_job_item.get("original_job_id")
    if original_job_id:
        original_job = await crud_job_instance.get_by_id(original_job_id)
        if not original_job or (original_job.get("created_by_dispatcher_id") != current_dispatcher.id and \
           (original_job.get("company_id") and original_job.get("company_id") != current_dispatcher.company_id)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to accept this job.")
    else: # If it's a copied job without original_job_id (shouldn't happen for COPIED/APPLICATION types)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid job: missing original job ID.")

    if copied_job_item.get("status") not in [JobStatus.PENDING_ACCEPTANCE.value, JobStatus.APPLICATION_REQUESTED.value]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not in pending acceptance or application requested status.")

    updated_original_job = await crud_job_instance.accept_copied_job(copied_job_id, copied_job_item.get("assigned_driver_id"));

    if not updated_original_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to accept job. It might have been accepted by another driver or already assigned.")

    return updated_original_job

@router.put("/{copied_job_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_copied_job(
    copied_job_id: str,
    current_dispatcher: User = Depends(get_current_dispatcher) # Only dispatcher can reject applications/copied jobs
):
    print(f"[reject_copied_job] Rejecting copied job with ID: {copied_job_id}")

    # We need to fetch the item first to perform authorization checks
    copied_job_item = await crud_job_instance.get_by_copied_job_id(copied_job_id)
    if not copied_job_item or copied_job_item.get("job_type") not in [JobType.COPIED.value, JobType.APPLICATION.value]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or invalid type.")
    
    # Authorization
    original_job_id = copied_job_item.get("original_job_id")
    if not original_job_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid job: missing original job ID.")

    original_job = await crud_job_instance.get_by_id(original_job_id)
    if not original_job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Original job not found.")

    is_creator = original_job.get("created_by_dispatcher_id") == current_dispatcher.id
    is_same_company = original_job.get("company_id") and original_job.get("company_id") == current_dispatcher.company_id

    if not (is_creator or is_same_company):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reject this job.")

    # Now, attempt to delete the job application
    deleted = await crud_job_instance.reject_copied_job(copied_job_id)

    if not deleted:
        # This could happen if the job was already accepted/rejected by another dispatcher in a race condition
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to reject job. It may have already been processed."
        )

    return

@router.delete("/application/{copied_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver_application(
    copied_job_id: str,
    current_driver: User = Depends(get_current_driver) # Ensures only a driver can call this
):
    """
    Allows a driver to delete their own job application if it's in a superseded or rejected state.
    """
    deleted = await crud_job_instance.delete_driver_application(copied_job_id, current_driver.id)

    if not deleted:
        # This can happen if the application doesn't exist, doesn't belong to the driver,
        # or is not in a deletable state (e.g., still pending).
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deletable job application not found."
        )
    
    return

@router.put("/{job_id}/cancel", response_model=Job)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    job_item = await crud_job_instance.get_by_id(job_id)
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
    updated_job = await crud_job_instance.update(job_id, job_update_data);

    if not updated_job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel job.")

    return updated_job