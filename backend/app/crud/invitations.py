from typing import List, Dict, Any, Optional
from app.api.v1.schemas.invitations import InvitationCreate, Invitation, InvitationStatus
from app.db import mongodb
from app.api.v1.schemas.users import RoleType, DispatcherAssociationStatus, DriverAssociationStatus # Import new enums
from app.crud.users import user # Import user CRUD

class CRUDInvitation:
    async def get_by_id(self, invitation_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_invitation_by_id_mongodb(invitation_id)

    async def create(self, invitation_in: InvitationCreate, company_id: str, company_name: str) -> Dict[str, Any]:
        # 1. Find the invitee user
        target_user = await user.get_by_username(invitation_in.invitee_username)
        if not target_user:
            raise ValueError("Invitee user not found.") # Or raise HTTPException

        # 2. Check if user has the correct role
        if invitation_in.invitee_role.value not in target_user["roles"]:
            raise ValueError(f"Invitee is not a {invitation_in.invitee_role.value}.")

        # 3. Check current association status
        if invitation_in.invitee_role == RoleType.DISPATCHER:
            if target_user.get("dispatcher_association_status") == DispatcherAssociationStatus.ASSOCIATED.value:
                raise ValueError("Dispatcher is already associated with a company.")
        elif invitation_in.invitee_role == RoleType.DRIVER:
            if target_user.get("driver_association_status") == DriverAssociationStatus.ASSOCIATED.value:
                raise ValueError("Driver is already associated with a company.")

        # 4. Create the invitation in MongoDB
        new_invitation = await mongodb.create_invitation_mongodb(
            invitee_id=target_user["id"],
            invitee_username=invitation_in.invitee_username,
            invitee_role=invitation_in.invitee_role,
            company_id=company_id,
            company_name=company_name
        )

        # 5. Update the invitee's association status to PENDING
        update_data = {}
        if invitation_in.invitee_role == RoleType.DISPATCHER:
            update_data["dispatcher_association_status"] = DispatcherAssociationStatus.PENDING
        elif invitation_in.invitee_role == RoleType.DRIVER:
            update_data["driver_association_status"] = DriverAssociationStatus.PENDING
        
        await user.update(target_user["id"], update_data)

        return new_invitation

    async def update(self, invitation_id: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await mongodb.update_invitation_mongodb(invitation_id, updated_data)

    async def get_for_invitee(self, invitee_id: str, invitee_role: RoleType) -> List[Dict[str, Any]]:
        return await mongodb.get_invitations_for_invitee_mongodb(invitee_id, invitee_role)

invitation = CRUDInvitation()
