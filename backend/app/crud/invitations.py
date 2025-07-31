from typing import List, Dict, Any, Optional
from app.api.v1.schemas.invitations import InvitationCreate, Invitation, InvitationStatus
from app.db import mongodb

class CRUDInvitation:
    async def get_by_id(self, invitation_id: int) -> Optional[Dict[str, Any]]:
        return await mongodb.get_invitation_by_id_mongodb(invitation_id)

    async def create(self, invitation: InvitationCreate, company_id: int, company_name: str) -> Dict[str, Any]:
        return await mongodb.create_invitation_mongodb(invitation, company_id, company_name)

    async def update(self, invitation_id: int, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await mongodb.update_invitation_mongodb(invitation_id, updated_data)

    async def get_for_dispatcher(self, dispatcher_id: int) -> List[Dict[str, Any]]:
        return await mongodb.get_invitations_for_dispatcher_mongodb(dispatcher_id)

invitation = CRUDInvitation()