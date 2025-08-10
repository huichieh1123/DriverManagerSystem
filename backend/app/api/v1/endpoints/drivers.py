from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.users import User, RoleType, DriverAssociationStatus
from app.api.v1.schemas.invitations import Invitation, InvitationCreate, InvitationStatus
from app.crud import invitation, user
from app.api.v1.endpoints.users import get_current_user # Keep this for now, will refactor users.py later

router = APIRouter()

# Dependency to check if the current user is a driver
async def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.DRIVER.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers can perform this action")
    return current_user

@router.get("/invitations", response_model=List[Invitation])
async def get_my_invitations(
    current_driver: User = Depends(get_current_driver)
):
    return await invitation.get_for_invitee(current_driver.id, RoleType.DRIVER)

@router.put("/invitations/{invitation_id}/accept", response_model=User)
async def accept_invitation(
    invitation_id: str,
    current_driver: User = Depends(get_current_driver)
):
    inv = await invitation.get_by_id(invitation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if inv["invitee_id"] != current_driver.id or inv["invitee_role"] != RoleType.DRIVER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to accept this invitation or invitation is not for a driver")

    if inv["status"] != InvitationStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is not pending")

    # Update invitation status
    await invitation.update(invitation_id, {"status": InvitationStatus.ACCEPTED.value})

    # Update driver's company_id, company_name, and association status
    updated_user = await user.update(current_driver.id, {
        "company_id": inv["company_id"],
        "company_name": inv["company_name"],
        "driver_association_status": DriverAssociationStatus.ASSOCIATED
    })

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile after accepting invitation."
        )

    return updated_user

@router.put("/invitations/{invitation_id}/decline", response_model=Invitation)
async def decline_invitation(
    invitation_id: str,
    current_driver: User = Depends(get_current_driver)
):
    inv = await invitation.get_by_id(invitation_id)
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if inv["invitee_id"] != current_driver.id or inv["invitee_role"] != RoleType.DRIVER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to decline this invitation or invitation is not for a driver")

    if inv["status"] != InvitationStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is not pending")

    # Update invitation status
    updated_inv = await invitation.update(invitation_id, {"status": InvitationStatus.DECLINED.value})

    # Update driver's association status to UNASSOCIATED if it was PENDING
    if current_driver.driver_association_status == DriverAssociationStatus.PENDING.value:
        await user.update(current_driver.id, {"driver_association_status": DriverAssociationStatus.UNASSOCIATED})

    return updated_inv