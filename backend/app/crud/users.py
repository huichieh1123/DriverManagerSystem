from typing import List, Dict, Any, Optional
from app.api.v1.schemas.users import UserCreate, User, UserUpdate, RoleType, DispatcherAssociationStatus
from app.db import mongodb
from pydantic import BaseModel # Import BaseModel to check type

class CRUDUser:
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_user_by_username_mongodb(username)

    async def create(self, user: UserCreate) -> Dict[str, Any]:
        return await mongodb.create_user_mongodb(user)

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_user_by_id_mongodb(user_id)

    async def update(self, user_id: str, user_in: UserUpdate) -> Optional[Dict[str, Any]]:
        # Always convert the incoming Pydantic model to a dictionary
        # This ensures update_data is always a dictionary
        update_data = user_in.dict(exclude_unset=True)

        # Convert RoleType enums in roles list to their string values
        if "roles" in update_data and update_data["roles"] is not None:
            if all(isinstance(role, RoleType) for role in update_data["roles"]):
                update_data["roles"] = [role.value for role in update_data["roles"]]
        
        # Convert DispatcherAssociationStatus enum to string value
        if "dispatcher_association_status" in update_data and isinstance(update_data["dispatcher_association_status"], DispatcherAssociationStatus):
            update_data["dispatcher_association_status"] = update_data["dispatcher_association_status"].value

        # Explicitly convert nested profile Pydantic models to dicts
        # This is the crucial part to prevent the AttributeError in mongodb.py
        if "driver_profile" in update_data and update_data["driver_profile"] is not None and isinstance(update_data["driver_profile"], BaseModel):
            update_data["driver_profile"] = update_data["driver_profile"].dict(exclude_unset=True)
        if "dispatcher_profile" in update_data and update_data["dispatcher_profile"] is not None and isinstance(update_data["dispatcher_profile"], BaseModel):
            update_data["dispatcher_profile"] = update_data["dispatcher_profile"].dict(exclude_unset=True)
        if "company_profile" in update_data and update_data["company_profile"] is not None and isinstance(update_data["company_profile"], BaseModel):
            update_data["company_profile"] = update_data["company_profile"].dict(exclude_unset=True)

        return await mongodb.update_user_mongodb(user_id, update_data)

    async def get_dispatchers_by_company_id(self, company_id: int) -> List[Dict[str, Any]]:
        return await mongodb.get_dispatchers_by_company_id_mongodb(company_id)

user = CRUDUser()
