from typing import List, Dict, Any, Optional, Union
from bson import ObjectId

from app.core.mongodb_config import users_collection, jobs_collection, invitations_collection
from app.api.v1.schemas.users import UserCreate, User, RoleType, DispatcherAssociationStatus
from app.api.v1.schemas.jobs import JobCreate, JobStatus
from app.api.v1.schemas.invitations import InvitationCreate, InvitationStatus
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
    }

def job_helper(job) -> Dict[str, Any]:
    return {
        "id": str(job["_id"]),
        "title": job["title"],
        "description": job.get("description"),
        "status": job["status"],
        "assigned_driver_id": str(job["assigned_driver_id"]) if job.get("assigned_driver_id") is not None else None, # Ensure it's a string
        "created_by_dispatcher_id": job.get("created_by_dispatcher_id"),
        "is_public": job["is_public"],
        "company_id": job.get("company_id"),
        "company_name": job.get("company_name"),
    }

def invitation_helper(invitation) -> Dict[str, Any]:
    return {
        "id": str(invitation["_id"]),
        "company_id": invitation["company_id"],
        "company_name": invitation["company_name"],
        "dispatcher_id": invitation["dispatcher_id"],
        "dispatcher_username": invitation["dispatcher_username"],
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

# --- Task Operations ---
async def get_tasks_mongodb() -> List[Dict[str, Any]]:
    # Tasks are currently hardcoded in frontend, so this is a placeholder
    return []

async def create_task_mongodb(task_data: JobCreate) -> Dict[str, Any]:
    # Tasks are currently hardcoded in frontend, so this is a placeholder
    return {}

# --- Job Operations ---
async def get_jobs_mongodb(assigned_driver_id: Optional[str] = None, created_by_dispatcher_id: Optional[str] = None, is_public: Optional[bool] = None, status: Optional[str] = None, company_id: Optional[str] = None) -> List[Dict[str, Any]]: # Changed ID types to str
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

    jobs = []
    async for job in jobs_collection.find(query):
        jobs.append(job_helper(job))
    return jobs

async def create_job_mongodb(job_data: JobCreate, created_by_dispatcher_id: str, company_id: Optional[str] = None, company_name: Optional[str] = None) -> Dict[str, Any]:
    job_dict = job_data.dict()
    job_dict["status"] = job_data.status.value
    job_dict["created_by_dispatcher_id"] = created_by_dispatcher_id
    job_dict["company_id"] = company_id
    job_dict["company_name"] = company_name
    
    result = await jobs_collection.insert_one(job_dict)
    new_job = await jobs_collection.find_one({"_id": result.inserted_id})
    return job_helper(new_job)

async def get_job_by_id_mongodb(job_id: str) -> Optional[Dict[str, Any]]: # Changed job_id type to str
    job = await jobs_collection.find_one({"_id": ObjectId(job_id)}) # Query by ObjectId
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
        else:
            update_query["$set"][key] = value

    result = await jobs_collection.update_one({"_id": ObjectId(job_id)}, update_query)
    if result.modified_count > 0:
        updated_job = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        return job_helper(updated_job)
    return None

async def delete_job_mongodb(job_id: str) -> bool:
    result = await jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return result.deleted_count > 0

# --- Invitation Operations ---
async def get_invitation_by_id_mongodb(invitation_id: str) -> Optional[Dict[str, Any]]: # Changed invitation_id type to str
    invitation = await invitations_collection.find_one({"_id": ObjectId(invitation_id)}) # Query by ObjectId
    if invitation: 
        return invitation_helper(invitation)
    return None

async def create_invitation_mongodb(invitation_data: InvitationCreate, company_id: str, company_name: str) -> Dict[str, Any]: # Changed company_id type to str
    invitation_dict = invitation_data.dict()
    invitation_dict["company_id"] = company_id
    invitation_dict["company_name"] = company_name
    invitation_dict["status"] = InvitationStatus.PENDING.value
    invitation_dict["dispatcher_id"] = None # Will be filled by crud layer

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

async def get_invitations_for_dispatcher_mongodb(dispatcher_id: str) -> List[Dict[str, Any]]:
    invitations = []
    async for inv in invitations_collection.find({"dispatcher_id": dispatcher_id, "status": InvitationStatus.PENDING.value}):
        invitations.append(invitation_helper(inv))
    return invitations
