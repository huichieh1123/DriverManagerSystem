from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.invitations import Invitation, InvitationCreate, InvitationStatus
from app.api.v1.schemas.users import User, RoleType, DispatcherAssociationStatus
from app.crud import invitation, user
from app.api.v1.endpoints.users import get_current_user # Keep this for now, will refactor users.py later

router = APIRouter()

# Dependency to check if the current user is a company
async def get_current_company(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.COMPANY.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only companies can perform this action")
    return current_user

@router.post("/invitations/send", response_model=Invitation, status_code=status.HTTP_201_CREATED)
async def send_invitation(
    invitation_in: InvitationCreate,
    current_company: User = Depends(get_current_company)
):
    # Check if target dispatcher exists
    target_dispatcher = await user.get_by_username(invitation_in.dispatcher_username)
    if not target_dispatcher or RoleType.DISPATCHER.value not in target_dispatcher["roles"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target dispatcher not found or not a dispatcher")

    # Check if target dispatcher is already part of a company
    if target_dispatcher.get("company_id") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target dispatcher is already associated with a company")

    # Create invitation
    new_invitation = await invitation.create(
        invitation_in,
        current_company.id,
        current_company.name or current_company.username # Use company name or username
    )
    # Update invitation with dispatcher_id
    await invitation.update(new_invitation["id"], {"dispatcher_id": target_dispatcher["id"]})
    new_invitation["dispatcher_id"] = target_dispatcher["id"]

    return new_invitation

@router.get("/users/company_dispatchers", response_model=List[User])
async def get_company_dispatchers(
    current_company: User = Depends(get_current_company)
):
    company_id_to_filter = current_company.id
    dispatchers = await user.get_dispatchers_by_company_id(company_id_to_filter)
    return [User(**d) for d in dispatchers]

@router.put("/users/{dispatcher_id}/remove_company", response_model=User)
async def remove_dispatcher_from_company(
    dispatcher_id: str, # Changed from int to str
    current_company: User = Depends(get_current_company)
):
    target_dispatcher = await user.get_by_id(dispatcher_id)
    if not target_dispatcher or RoleType.DISPATCHER.value not in target_dispatcher.get("roles", []):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatcher not found.")

    if target_dispatcher.get("company_id") != current_company.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This dispatcher is not associated with your company.")

    updated_dispatcher = await user.update(dispatcher_id, {"company_id": None, "company_name": None, "dispatcher_association_status": DispatcherAssociationStatus.UNASSOCIATED})
    if not updated_dispatcher:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove dispatcher from company.")
    
    return updated_dispatcher