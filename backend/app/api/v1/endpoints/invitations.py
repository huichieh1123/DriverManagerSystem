from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.v1.schemas.invitations import Invitation, InvitationCreate, InvitationStatus
from app.api.v1.schemas.users import User, RoleType
from app.crud import invitation, user
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()

# Dependency to check if the current user is a company
def get_current_company(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.COMPANY.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only companies can perform this action")
    return current_user

# Dependency to check if the current user is a dispatcher
def get_current_dispatcher(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.DISPATCHER.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only dispatchers can perform this action")
    return current_user

@router.post("/invitations/send", response_model=Invitation, status_code=status.HTTP_201_CREATED)
def send_invitation(
    invitation_in: InvitationCreate,
    current_company: User = Depends(get_current_company)
):
    # Check if target dispatcher exists
    target_dispatcher = user.get_by_username(invitation_in.dispatcher_username)
    if not target_dispatcher or RoleType.DISPATCHER.value not in target_dispatcher["roles"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target dispatcher not found or not a dispatcher")

    # Check if target dispatcher is already part of a company
    if target_dispatcher.get("company_id") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Target dispatcher is already associated with a company")

    # Create invitation
    new_invitation = invitation.create(
        invitation_in,
        current_company.id,
        current_company.name or current_company.username # Use company name or username
    )
    # Update invitation with dispatcher_id
    invitation.update(new_invitation["id"], {"dispatcher_id": target_dispatcher["id"]})
    new_invitation["dispatcher_id"] = target_dispatcher["id"]

    return new_invitation

@router.get("/invitations/me", response_model=List[Invitation])
def get_my_invitations(
    current_dispatcher: User = Depends(get_current_dispatcher)
):
    return invitation.get_for_dispatcher(current_dispatcher.id)

@router.put("/invitations/{invitation_id}/accept", response_model=Invitation)
def accept_invitation(
    invitation_id: int,
    current_dispatcher: User = Depends(get_current_dispatcher)
):
    inv = invitation.get_by_id(invitation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if inv["dispatcher_id"] != current_dispatcher.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to accept this invitation")

    if inv["status"] != InvitationStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is not pending")

    # Update invitation status
    updated_inv = invitation.update(invitation_id, {"status": InvitationStatus.ACCEPTED.value})

    # Update dispatcher's company_id and company_name
    user.update(current_dispatcher.id, {
        "company_id": inv["company_id"],
        "company_name": inv["company_name"]
    })

    return updated_inv

@router.put("/invitations/{invitation_id}/decline", response_model=Invitation)
def decline_invitation(
    invitation_id: int,
    current_dispatcher: User = Depends(get_current_dispatcher)
):
    inv = invitation.get_by_id(invitation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if inv["dispatcher_id"] != current_dispatcher.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to decline this invitation")

    if inv["status"] != InvitationStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is not pending")

    # Update invitation status
    updated_inv = invitation.update(invitation_id, {"status": InvitationStatus.DECLINED.value})
    return updated_inv
