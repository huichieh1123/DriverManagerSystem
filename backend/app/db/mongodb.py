from typing import List, Dict, Any, Optional, Union
from bson import ObjectId
import time # Import time for generating unique IDs

from app.core.mongodb_config import users_collection, jobs_collection, invitations_collection, vehicles_collection
from app.api.v1.schemas.users import UserCreate, User, RoleType, DispatcherAssociationStatus, DriverAssociationStatus
from app.api.v1.schemas.jobs import JobCreate, JobStatus, JobType # Import JobType
from app.api.v1.schemas.invitations import InvitationCreate, InvitationStatus
from app.api.v1.schemas.vehicles import VehicleCreate, VehicleUpdate # Import Vehicle schemas
from pydantic import BaseModel # Import BaseModel for type checking

# Helper function to convert MongoDB document to Python dict
def user_helper(user) -> Dict[str, Any]:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "password": user["password"],
        "name": user.get("name"),
        "roles": user["roles"],
        "driver_profile": user.get("driver_profile"),
        "dispatcher_profile": user.get("dispatcher_profile"),
        "company_profile": user.get("company_profile"),
        "company_id": user.get("company_id"),
        "company_name": user.get("company_name"),
        "dispatcher_association_status": user.get("dispatcher_association_status"),
        "driver_association_status": user.get("driver_association_status"),
    }

def job_helper(job) -> Dict[str, Any]:
    job_id = job["_id"]
    if isinstance(job_id, ObjectId):
        job_id = str(job_id)
    return {
        "id": job_id,
        "company": job.get("company"),
        "transfer_type": job.get("transfer_type"),
        "pick_up_date": job.get("pick_up_date"),
        "pick_up_time": job.get("pick_up_time"),
        "flight_number": job.get("flight_number"),
        "passenger_name": job.get("passenger_name"),
        "phone_number": job.get("phone_number"),
        "vehicle_model": job.get("vehicle_model"),
        "num_of_passenger": job.get("num_of_passenger"),
        "from_location": job.get("from_location"),
        "to_location": job.get("to_location"),
        "additional_services": job.get("additional_services"),
        "special_requirements": job.get("special_requirements"),
        "other_contact_info": job.get("other_contact_info"),
        "order_number": job.get("order_number"),
        "total_price": job.get("total_price"),
        "email": job.get("email"),
        "driver_name": job.get("driver_name"),
        "driver_phone": job.get("driver_phone"),
        "vehicle_number": job.get("vehicle_number"),
        "vehicle_type": job.get("vehicle_type"),
        "is_public": job.get("is_public"),
        "status": job["status"],
        "assigned_driver_id": job.get("assigned_driver_id"),
        "assigned_vehicle_id": job.get("assigned_vehicle_id"),
        "created_by_dispatcher_id": job.get("created_by_dispatcher_id"),
        "company_id": job.get("company_id"),
        "company_name": job.get("company_name"),
        "original_job_id": job.get("original_job_id"), # New field
        "copied_job_id": job.get("copied_job_id"), # New field
        "job_type": job.get("job_type"), # New field
        "driver_response_status": job.get("driver_response_status"), # New field
    }

def invitation_helper(invitation) -> Dict[str, Any]:
    return {
        "id": str(invitation["_id"]),
        "company_id": invitation["company_id"],
        "company_name": invitation["company_name"],
        "invitee_id": invitation["invitee_id"],
        "invitee_username": invitation["invitee_username"],
        "invitee_role": invitation["invitee_role"],
        "status": invitation["status"],
    }

# --- User Operations ---
async def get_user_by_username_mongodb(username: str) -> Optional[Dict[str, Any]]:
    user = await users_collection.find_one({"username": username})
    if user:
        return user_helper(user)
    return None

async def create_user_mongodb(user_data: UserCreate) -> Dict[str, Any]:
    user_dict = user_data.dict()
    user_dict["roles"] = [role.value for role in user_data.roles]
    user_dict["dispatcher_association_status"] = DispatcherAssociationStatus.UNASSOCIATED.value if RoleType.DISPATCHER.value in user_data.roles else None
    user_dict["driver_association_status"] = DriverAssociationStatus.UNASSOCIATED.value if RoleType.DRIVER.value in user_data.roles else None

    # Initialize profiles as empty dicts if not provided
    user_dict["driver_profile"] = user_dict.get("driver_profile", {})
    user_dict["dispatcher_profile"] = user_dict.get("dispatcher_profile", {})
    user_dict["company_profile"] = user_dict.get("company_profile", {})

    result = await users_collection.insert_one(user_dict)
    new_user = await users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

async def get_user_by_id_mongodb(user_id: str) -> Optional[Dict[str, Any]]: # Changed user_id type to str
    user = await users_collection.find_one({"_id": ObjectId(user_id)}) # Query by ObjectId
    if user:
        return user_helper(user)
    return None

async def update_user_mongodb(user_id: str, updated_data: Union[Dict[str, Any], BaseModel]) -> Optional[Dict[str, Any]]:
    # 若 updated_data 是 Pydantic model，轉為 dict
    if isinstance(updated_data, BaseModel):
        updated_data = updated_data.dict(exclude_unset=True)

    update_query = {"$set": {}}
    for key, value in updated_data.items():
        if key == "roles":
            if isinstance(value, list) and all(isinstance(role, RoleType) for role in value):
                update_query["$set"]["roles"] = [role.value for role in value]
            else:
                update_query["$set"]["roles"] = value
        elif key == "dispatcher_association_status":
            update_query["$set"]["dispatcher_association_status"] = value.value if isinstance(value, DispatcherAssociationStatus) else value
        elif key == "driver_association_status":
            update_query["$set"]["driver_association_status"] = value.value if isinstance(value, DriverAssociationStatus) else value
        elif isinstance(value, BaseModel):
            update_query["$set"][key] = value.dict(exclude_unset=True)
        else:
            update_query["$set"][key] = value

    result = await users_collection.update_one({"_id": ObjectId(user_id)}, update_query)
    if result.modified_count > 0:
        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        return user_helper(updated_user)
    return None

async def get_dispatchers_by_company_id_mongodb(company_id: str) -> List[Dict[str, Any]]: # Changed company_id type to str
    dispatchers = []
    async for user in users_collection.find({"company_id": company_id, "roles": RoleType.DISPATCHER.value}):
        dispatchers.append(user_helper(user))
    return dispatchers

async def get_drivers_by_company_id_mongodb(company_id: str) -> List[Dict[str, Any]]:
    drivers = []
    query = {
        "company_id": company_id,
        "roles": RoleType.DRIVER.value,
        "driver_association_status": DriverAssociationStatus.ASSOCIATED.value
    }
    async for user in users_collection.find(query):
        drivers.append(user_helper(user))
    return drivers

# --- Task Operations ---
async def get_tasks_mongodb() -> List[Dict[str, Any]]:
    # Tasks are currently hardcoded in frontend, so this is a placeholder
    return []

async def create_task_mongodb(task_data: JobCreate) -> Dict[str, Any]:
    # Tasks are currently hardcoded in frontend, so this is a placeholder
    return {}

# --- Job Operations ---
async def get_jobs_mongodb(assigned_driver_id: Optional[str] = None, created_by_dispatcher_id: Optional[str] = None, is_public: Optional[bool] = None, status: Optional[str] = None, company_id: Optional[str] = None, job_type: Optional[str] = None) -> List[Dict[str, Any]]: # Added job_type
    query = {}
    if assigned_driver_id is not None:
        query["assigned_driver_id"] = assigned_driver_id
    if created_by_dispatcher_id is not None:
        query["created_by_dispatcher_id"] = created_by_dispatcher_id
    if is_public is not None:
        query["is_public"] = is_public
    if status is not None:
        query["status"] = status
    if company_id is not None:
        query["company_id"] = company_id
    if job_type is not None:
        query["job_type"] = job_type

    print(f"[get_jobs_mongodb] Final query: {query}")

    jobs = []
    async for job in jobs_collection.find(query):
        jobs.append(job_helper(job))
    print(f"[get_jobs_mongodb] Number of jobs found for query: {len(jobs)}")
    return jobs

async def create_job_mongodb(job_data: JobCreate, created_by_dispatcher_id: str, company_id: Optional[str] = None, company_name: Optional[str] = None) -> Dict[str, Any]:
    job_dict = job_data.dict()
    job_dict["status"] = job_data.status.value
    job_dict["created_by_dispatcher_id"] = created_by_dispatcher_id
    job_dict["company_id"] = company_id
    job_dict["company_name"] = company_name

    # Set job_type if not already set (e.g., for original jobs)
    if "job_type" not in job_dict or job_dict["job_type"] is None:
        job_dict["job_type"] = JobType.ORIGINAL.value

    # If _id is already provided in job_dict (e.g., for claim applications or copied jobs), use it.
    # Otherwise, MongoDB will generate one.
    if "id" in job_dict:
        job_dict["_id"] = job_dict.pop("id") # Use the provided 'id' as '_id'

    result = await jobs_collection.insert_one(job_dict)
    new_job = await jobs_collection.find_one({"_id": result.inserted_id})
    return job_helper(new_job)

async def create_job_application_mongodb(original_job: Dict[str, Any], driver_id: str, vehicle_id: str, driver_name: str, driver_phone: str) -> Optional[Dict[str, Any]]:
    # Generate a unique copied_job_id based on original_job_id and a timestamp
    timestamp = int(time.time() * 1000) # Milliseconds since epoch
    application_id = f"{original_job['id']}-APP-{driver_id}-{timestamp}"

    # Fetch vehicle details
    selected_vehicle = await get_vehicle_by_id_mongodb(vehicle_id)
    if not selected_vehicle:
        print(f"[create_job_application_mongodb] Vehicle with ID {vehicle_id} not found.")
        return None # Or raise an error

    # Create a new JobCreate object for the application
    application_data = original_job.copy()
    application_data.pop('id', None) # Remove original _id to let MongoDB generate a new one
    application_data.pop('_id', None) # Ensure _id is not carried over

    application_data.update({
        "original_job_id": original_job["id"],
        "copied_job_id": application_id, # Using copied_job_id for application ID
        "job_type": JobType.APPLICATION.value,
        "status": JobStatus.APPLICATION_REQUESTED.value, # New status for applications
        "assigned_driver_id": driver_id, # Assign to the driver who applied
        "assigned_vehicle_id": vehicle_id, # Assign vehicle from application
        "driver_name": driver_name,
        "driver_phone": driver_phone,
        "driver_response_status": None, # No response yet
        "vehicle_model": selected_vehicle.get("make"), # Make/廠牌
        "vehicle_type": selected_vehicle.get("model"), # Model/車型
        "vehicle_number": selected_vehicle.get("license_plate"),
    })

    # Ensure all fields match JobCreate schema
    job_create_schema = JobCreate(**application_data)

    return await create_job_mongodb(job_create_schema,
                                     created_by_dispatcher_id=original_job.get("created_by_dispatcher_id"),
                                     company_id=original_job.get("company_id"),
                                     company_name=original_job.get("company_name"))

async def create_copied_job_mongodb(original_job: Dict[str, Any], driver_id: str, vehicle_id: str, driver_name: str, driver_phone: str) -> Optional[Dict[str, Any]]:
    # Generate a unique copied_job_id based on original_job_id and a timestamp
    timestamp = int(time.time() * 1000) # Milliseconds since epoch
    copied_job_id = f"{original_job['id']}-COPY-{timestamp}"

    # Fetch vehicle details to get license plate and model
    selected_vehicle = await get_vehicle_by_id_mongodb(vehicle_id)
    if not selected_vehicle:
        print(f"[create_copied_job_mongodb] Vehicle with ID {vehicle_id} not found.")
        return None # Or raise an error

    # Create a new JobCreate object for the copied job
    copied_job_data = original_job.copy()
    copied_job_data.pop('id', None) # Remove original _id to let MongoDB generate a new one
    copied_job_data.pop('_id', None) # Ensure _id is not carried over

    copied_job_data.update({
        "original_job_id": original_job["id"],
        "copied_job_id": copied_job_id,
        "job_type": JobType.COPIED.value,
        "status": JobStatus.PENDING_ACCEPTANCE.value, # New status for copied jobs
        "assigned_driver_id": driver_id, # Assign to the driver it's sent to
        "assigned_vehicle_id": vehicle_id, # Assign vehicle if provided
        "driver_name": driver_name,
        "driver_phone": driver_phone,
        "driver_response_status": None, # No response yet
        # Add vehicle details
        "vehicle_model": selected_vehicle.get("make"), # Make/廠牌
        "vehicle_type": selected_vehicle.get("model"), # Model/車型
        "vehicle_number": selected_vehicle.get("license_plate"),
    })

    # Ensure all fields match JobCreate schema
    job_create_schema = JobCreate(**copied_job_data)

    return await create_job_mongodb(job_create_schema,
                                     created_by_dispatcher_id=original_job.get("created_by_dispatcher_id"),
                                     company_id=original_job.get("company_id"),
                                     company_name=original_job.get("company_name"))

async def accept_copied_job_mongodb(copied_job_id: str, driver_id: str) -> Optional[Dict[str, Any]]:
    # 1. Find the copied job and its original job ID
    copied_job = await jobs_collection.find_one({"copied_job_id": copied_job_id, "job_type": {"$in": [JobType.COPIED.value, JobType.APPLICATION.value]}})
    if not copied_job:
        print(f"[accept_copied_job_mongodb] Copied job with ID {copied_job_id} not found or invalid type.")
        return None

    original_job_id = copied_job.get("original_job_id")
    if not original_job_id:
        print(f"[accept_copied_job_mongodb] Copied job {copied_job_id} has no original_job_id.")
        return None

    # 2. Atomically update the original job (simulate lock and check status)
    # Only update if the original job is still PENDING and not assigned
    updated_original_job = await jobs_collection.find_one_and_update(
        filter={
            "_id": ObjectId(original_job_id),
            "job_type": JobType.ORIGINAL.value,
            "status": JobStatus.PENDING.value, # Ensure it's still pending
            "assigned_driver_id": None # Ensure it's not assigned yet
        },
        update={
            "$set": {
                "status": JobStatus.ASSIGNED.value,
                "is_public": False, # Set is_public to False
                "assigned_driver_id": driver_id,
                "assigned_vehicle_id": copied_job.get("assigned_vehicle_id"), # Assign vehicle from copied job
                "driver_name": copied_job.get("driver_name"), # Update driver details
                "driver_phone": copied_job.get("driver_phone"),
                "vehicle_model": copied_job.get("vehicle_model"), # Copy vehicle make
                "vehicle_number": copied_job.get("vehicle_number"),
                "vehicle_type": copied_job.get("vehicle_type"),
            }
        },
        return_document=True # Return the updated document
    )

    if not updated_original_job:
        print(f"[accept_copied_job_mongodb] Original job {original_job_id} could not be assigned (already assigned or not pending).")
        return None # Original job was already assigned or not found

    # 3. Update the accepted copied job's status
    await jobs_collection.update_one(
        {"_id": copied_job["_id"]},
        {"$set": {"status": JobStatus.ACCEPTED.value, "driver_response_status": "accepted"}}
    )

    # 4. Supersede all other copied jobs related to this original_job_id
    # This includes other COPIED jobs and APPLICATION jobs
    await jobs_collection.update_many(
        filter={
            "original_job_id": original_job_id,
            "job_type": {"$in": [JobType.COPIED.value, JobType.APPLICATION.value]},
            "_id": {"$ne": copied_job["_id"]} # Exclude the currently accepted copied job
        },
        update={"$set": {"status": JobStatus.SUPERSEDED.value, "driver_response_status": "superseded"}}
    )

    return job_helper(updated_original_job)

async def reject_copied_job_mongodb(copied_job_id: str) -> bool:
    # Find the job to be rejected and delete it
    result = await jobs_collection.delete_one(
        {
            "copied_job_id": copied_job_id,
            "job_type": {"$in": [JobType.COPIED.value, JobType.APPLICATION.value]},
            "status": {"$in": [JobStatus.PENDING_ACCEPTANCE.value, JobStatus.APPLICATION_REQUESTED.value]}
        }
    )
    return result.deleted_count > 0

async def delete_driver_application_mongodb(copied_job_id: str, driver_id: str) -> bool:
    """
    Deletes a driver's own job application if it is in a terminal state (superseded, rejected, or accepted).
    """
    result = await jobs_collection.delete_one(
        {
            "copied_job_id": copied_job_id,
            "assigned_driver_id": driver_id, # Security: ensures drivers can only delete their own jobs
            "status": {"$in": [JobStatus.SUPERSEDED.value, JobStatus.REJECTED.value, JobStatus.ACCEPTED.value]}
        }
    )
    return result.deleted_count > 0

async def get_job_by_id_mongodb(job_id: str) -> Optional[Dict[str, Any]]: # Changed job_id type to str
    # Try to query by ObjectId first, then by string if not found
    job = await jobs_collection.find_one({"_id": job_id})
    if not job and ObjectId.is_valid(job_id):
        job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
    if job:
        return job_helper(job)
    return None

async def get_job_by_copied_job_id_mongodb(copied_job_id: str) -> Optional[Dict[str, Any]]:
    job = await jobs_collection.find_one({"copied_job_id": copied_job_id})
    if job:
        return job_helper(job)
    return None

async def update_job_mongodb(job_id: str, updated_data: Union[Dict[str, Any], BaseModel]) -> Optional[Dict[str, Any]]: # Changed job_id type to str
    if isinstance(updated_data, BaseModel):
        updated_data = updated_data.dict(exclude_unset=True)

    update_query = {"$set": {}}
    for key, value in updated_data.items():
        if key == "status":
            update_query["$set"]["status"] = value.value if isinstance(value, JobStatus) else value
        elif key == "job_type": # Handle JobType enum
            update_query["$set"]["job_type"] = value.value if isinstance(value, JobType) else value
        else:
            update_query["$set"][key] = value

    # Try to update by ObjectId first, then by string if not found
    result = await jobs_collection.update_one({"_id": job_id}, update_query)
    if result.matched_count == 0 and ObjectId.is_valid(job_id):
        result = await jobs_collection.update_one({"_id": ObjectId(job_id)}, update_query)

    if result.modified_count > 0:
        updated_job = await jobs_collection.find_one({"_id": job_id})
        if not updated_job and ObjectId.is_valid(job_id):
            updated_job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        return job_helper(updated_job)
    return None

async def delete_job_mongodb(job_id: str) -> bool:
    result = await jobs_collection.delete_one({"_id": job_id})
    if result.deleted_count == 0 and ObjectId.is_valid(job_id):
        result = await jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return result.deleted_count > 0

async def replace_job_mongodb(job_id: str, replacement_data: dict) -> Optional[Dict[str, Any]]:
    # The replacement document cannot contain the _id field. Let's be safe.
    replacement_data.pop('_id', None)
    result = await jobs_collection.replace_one({"_id": job_id}, replacement_data)
    if result.matched_count == 0 and ObjectId.is_valid(job_id):
        result = await jobs_collection.replace_one({"_id": ObjectId(job_id)}, replacement_data)

    if result.matched_count > 0:
        # If we found a document, the replacement was successful.
        replaced_job = await jobs_collection.find_one({"_id": job_id})
        if not replaced_job and ObjectId.is_valid(job_id):
            replaced_job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        return job_helper(replaced_job)
    # If no document was matched, it means the original_job_id was not found.
    return None


# --- Invitation Operations ---
async def get_invitation_by_id_mongodb(invitation_id: str) -> Optional[Dict[str, Any]]: # Changed invitation_id type to str
    invitation = await invitations_collection.find_one({"_id": ObjectId(invitation_id)}) # Query by ObjectId
    if invitation:
        return invitation_helper(invitation)
    return None

async def create_invitation_mongodb(
    invitee_id: str,
    invitee_username: str,
    invitee_role: RoleType,
    company_id: str,
    company_name: str
) -> Dict[str, Any]:
    invitation_dict = {
        "company_id": company_id,
        "company_name": company_name,
        "invitee_id": invitee_id,
        "invitee_username": invitee_username,
        "invitee_role": invitee_role.value if isinstance(invitee_role, RoleType) else invitee_role, # Store enum value
        "status": InvitationStatus.PENDING.value,
    }

    result = await invitations_collection.insert_one(invitation_dict)
    new_invitation = await invitations_collection.find_one({"_id": result.inserted_id})
    return invitation_helper(new_invitation)

async def update_invitation_mongodb(invitation_id: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]: # Changed invitation_id type to str
    update_query = {"$set": {}}
    for key, value in updated_data.items():
        if key == "status":
            update_query["$set"]["status"] = value.value if isinstance(value, InvitationStatus) else value
        else:
            update_query["$set"][key] = value

    result = await invitations_collection.update_one({"_id": ObjectId(invitation_id)}, update_query)
    if result.modified_count > 0:
        updated_invitation = await invitations_collection.find_one({"_id": ObjectId(invitation_id)})
        return invitation_helper(updated_invitation)
    return None

async def get_invitations_for_invitee_mongodb(invitee_id: str, invitee_role: RoleType) -> List[Dict[str, Any]]:
    invitations = []
    async for inv in invitations_collection.find({
        "invitee_id": invitee_id,
        "invitee_role": invitee_role.value,
        "status": InvitationStatus.PENDING.value
    }):
        invitations.append(invitation_helper(inv))
    return invitations


# --- Vehicle Operations ---
def vehicle_helper(vehicle) -> Dict[str, Any]:
    return {
        "id": str(vehicle["_id"]),
        "license_plate": vehicle["license_plate"],
        "make": vehicle.get("make"),
        "model": vehicle.get("model"),
        "capacity": vehicle.get("capacity"),
        "color": vehicle.get("color"),
        "manufacture_year": vehicle.get("manufacture_year"),
        "insurance_valid_date": vehicle.get("insurance_valid_date"),
        "passenger_insurance_amount": vehicle.get("passenger_insurance_amount"),
        "owner_id": vehicle.get("owner_id"),
    }

async def get_vehicles_mongodb(owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
    query = {}
    if owner_id:
        query["owner_id"] = owner_id


    vehicles = []
    async for vehicle in vehicles_collection.find(query):
        vehicles.append(vehicle_helper(vehicle))
    return vehicles

async def get_vehicle_by_id_mongodb(vehicle_id: str) -> Optional[Dict[str, Any]]:
    vehicle = await vehicles_collection.find_one({"_id": ObjectId(vehicle_id)})
    if vehicle:
        return vehicle_helper(vehicle)
    return None

async def create_vehicle_mongodb(vehicle_data: VehicleCreate) -> Dict[str, Any]:
    vehicle_dict = vehicle_data.dict()
    result = await vehicles_collection.insert_one(vehicle_dict)
    new_vehicle = await vehicles_collection.find_one({"_id": result.inserted_id})
    return vehicle_helper(new_vehicle)

async def update_vehicle_mongodb(vehicle_id: str, updated_data: Union[Dict[str, Any], BaseModel]) -> Optional[Dict[str, Any]]:
    if isinstance(updated_data, BaseModel):
        updated_data = updated_data.dict(exclude_unset=True)

    update_query = {"$set": updated_data}
    result = await vehicles_collection.update_one({"_id": ObjectId(vehicle_id)}, update_query)
    if result.modified_count > 0:
        updated_vehicle = await vehicles_collection.find_one({"_id": ObjectId(vehicle_id)})
        return vehicle_helper(updated_vehicle)
    return None

async def delete_vehicle_mongodb(vehicle_id: str) -> bool:
    result = await vehicles_collection.delete_one({"_id": ObjectId(vehicle_id)})
    return result.deleted_count > 0