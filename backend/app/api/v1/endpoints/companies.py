from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.invitations import Invitation, InvitationCreate, InvitationStatus
from app.api.v1.schemas.users import User, RoleType, DispatcherAssociationStatus, DriverAssociationStatus
from app.crud import invitation, user
from app.api.v1.endpoints.users import get_current_user # Keep this for now, will refactor users.py later

router = APIRouter()

# Dependency to check if the current user is a company
async def get_current_company(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.COMPANY.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only companies can perform this action")
    return current_user

@router.post("/invitations", response_model=Invitation, status_code=status.HTTP_201_CREATED)
async def send_invitation(
    invitation_in: InvitationCreate,
    current_company: User = Depends(get_current_company)
):
    try:
        invitee_user = await user.get_by_username(invitation_in.invitee_username)
        if not invitee_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitee user not found.")

        new_invitation = await invitation.create(
            invitee_username=invitation_in.invitee_username,
            invitee_role=invitation_in.invitee_role,
            invitee_id=invitee_user["id"],
            company_id=current_company.id,
            company_name=current_company.name or current_company.username # Use company name or username
        )
        alert_message = f"Invitation sent to {new_invitation['invitee_username']} ({new_invitation['invitee_role']})!"
        return new_invitation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send invitation: {e}")

@router.get("/users/company_dispatchers", response_model=List[User])
async def get_company_dispatchers(
    current_company: User = Depends(get_current_company)
):
    company_id_to_filter = current_company.id
    dispatchers = await user.get_dispatchers_by_company_id(company_id_to_filter)
    return [User(**d) for d in dispatchers]

@router.get("/users/company_drivers", response_model=List[User])
async def get_company_drivers(
    current_company: User = Depends(get_current_company)
):
    company_id_to_filter = current_company.id
    drivers = await user.get_drivers_by_company_id(company_id_to_filter)
    return [User(**d) for d in drivers]

@router.put("/users/{dispatcher_id}/remove_company", response_model=User)
async def remove_dispatcher_from_company(
    dispatcher_id: str,
    current_company: User = Depends(get_current_company)
):
    target_dispatcher = await user.get_by_id(dispatcher_id)
    if not target_dispatcher or RoleType.DISPATCHER.value not in target_dispatcher.get("roles", []):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatcher not found.")

    if target_dispatcher.get("company_id") != current_company.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This dispatcher is not associated with your company.")

    update_data = {"dispatcher_association_status": DispatcherAssociationStatus.UNASSOCIATED}

    # If the user is NOT also an associated driver, then fully remove them from the company
    if target_dispatcher.get("driver_association_status") != DriverAssociationStatus.ASSOCIATED.value:
        update_data["company_id"] = None
        update_data["company_name"] = None

    updated_dispatcher = await user.update(dispatcher_id, update_data)
    if not updated_dispatcher:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove dispatcher from company.")
    
    return updated_dispatcher

@router.put("/users/{driver_id}/remove_driver_company", response_model=User)
async def remove_driver_from_company(
    driver_id: str,
    current_company: User = Depends(get_current_company)
):
    target_driver = await user.get_by_id(driver_id)
    if not target_driver or RoleType.DRIVER.value not in target_driver.get("roles", []):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    if target_driver.get("company_id") != current_company.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This driver is not associated with your company.")

    update_data = {"driver_association_status": DriverAssociationStatus.UNASSOCIATED}

    # If the user is NOT also an associated dispatcher, then fully remove them from the company
    if target_driver.get("dispatcher_association_status") != DispatcherAssociationStatus.ASSOCIATED.value:
        update_data["company_id"] = None
        update_data["company_name"] = None

    updated_driver = await user.update(driver_id, update_data)
    if not updated_driver:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove driver from company.")
    
    return updated_driver
