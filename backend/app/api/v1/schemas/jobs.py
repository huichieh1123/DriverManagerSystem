from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

class JobStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLAIM_REQUESTED = "claim_requested"
    PENDING_ACCEPTANCE = "pending_acceptance" # New: Copied job sent to driver, awaiting response
    ACCEPTED = "accepted" # New: Copied job accepted by driver
    REJECTED = "rejected" # New: Copied job rejected by driver
    SUPERSEDED = "superseded" # New: Copied job superseded by another accepted copy
    APPLICATION_REQUESTED = "application_requested" # New: Driver applied for a public job

class JobType(str, Enum):
    ORIGINAL = "original"
    COPIED = "copied"
    APPLICATION = "application" # New: Job created as an application by a driver

class JobSummary(BaseModel):
    id: str
    company: Optional[str] = None
    transfer_type: Optional[str] = None
    pick_up_date: Optional[str] = None
    pick_up_time: Optional[str] = None
    flight_number: Optional[str] = None
    total_price: Optional[str] = None
    status: JobStatus
    job_type: JobType # Add job_type to summary

    class Config:
        orm_mode = True
        from_attributes = True

class JobBase(BaseModel):
    company: Optional[str] = None
    transfer_type: Optional[str] = None
    pick_up_date: Optional[str] = None
    pick_up_time: Optional[str] = None
    flight_number: Optional[str] = None
    passenger_name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    num_of_passenger: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    additional_services: Optional[str] = None
    special_requirements: Optional[str] = None
    other_contact_info: Optional[str] = None
    order_number: Optional[str] = None
    total_price: Optional[str] = None
    email: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    is_public: bool = False # 是否外包
    status: JobStatus = JobStatus.PENDING
    assigned_driver_id: Optional[str] = None
    proposed_driver_vehicle_id: Optional[str] = None # New: Vehicle ID proposed by driver for claim
    created_by_dispatcher_id: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    original_job_id: Optional[str] = None # ID of the original job if this is a copied job
    copied_job_id: Optional[str] = None # Unique ID for this specific copied job instance
    job_type: JobType = JobType.ORIGINAL # Type of job: original or copied
    driver_response_status: Optional[str] = None # Status of driver's response to a copied job (e.g., "accepted", "rejected")

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    company: Optional[str] = None
    transfer_type: Optional[str] = None
    pick_up_date: Optional[str] = None
    pick_up_time: Optional[str] = None
    flight_number: Optional[str] = None
    passenger_name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle_model: Optional[str] = None
    num_of_passenger: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    additional_services: Optional[str] = None
    special_requirements: Optional[str] = None
    other_contact_info: Optional[str] = None
    order_number: Optional[str] = None
    total_price: Optional[str] = None
    email: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    is_public: Optional[bool] = None
    status: Optional[JobStatus] = None
    assigned_driver_id: Optional[str] = None
    proposed_driver_vehicle_id: Optional[str] = None # New: Vehicle ID proposed by driver for claim
    original_job_id: Optional[str] = None # Allow updating original_job_id if needed
    copied_job_id: Optional[str] = None # Allow updating copied_job_id if needed
    job_type: Optional[JobType] = None # Allow updating job_type if needed
    driver_response_status: Optional[str] = None # Allow updating driver_response_status

class Job(JobBase):
    id: str # Changed from int to str
    status: JobStatus

    class Config:
        orm_mode = True
        from_attributes = True

class DispatcherClaimRequest(BaseModel):
    driver_id: str
    vehicle_id: str

class JobBatchDeleteRequest(BaseModel):
    job_ids: List[str]