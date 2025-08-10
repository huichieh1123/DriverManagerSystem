from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.vehicles import Vehicle, VehicleCreate, VehicleUpdate
from app.api.v1.schemas.users import User, RoleType
from app.crud.vehicle import vehicle
from app.api.v1.endpoints.users import get_current_user

router = APIRouter()

# Dependency to check if the current user is a driver or company
async def get_current_driver_or_company(current_user: User = Depends(get_current_user)) -> User:
    if RoleType.DRIVER.value not in current_user.roles and RoleType.COMPANY.value not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only drivers or companies can manage vehicles.")
    return current_user

@router.post("/", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    current_user: User = Depends(get_current_driver_or_company)
):
    # Assign owner_id based on the current user
    vehicle_in.owner_id = current_user.id
    new_vehicle = await vehicle.create(vehicle_in)
    return new_vehicle

@router.get("/", response_model=List[Vehicle])
async def read_vehicles(
    username: Optional[str] = None, # Accept username query parameter
    current_user: User = Depends(get_current_driver_or_company)
):
    print(f"[read_vehicles] current_user.id: {current_user.id}")
    print(f"[read_vehicles] current_user.roles: {current_user.roles}")
    # Only return vehicles owned by the current user
    vehicles = await vehicle.get_all(owner_id=current_user.id)
    print(f"[read_vehicles] Number of vehicles found for owner {current_user.id}: {len(vehicles)}")
    return [Vehicle(**v) for v in vehicles]

@router.get("/{vehicle_id}", response_model=Vehicle)
async def read_vehicle_by_id(
    vehicle_id: str,
    current_user: User = Depends(get_current_driver_or_company)
):
    vehicle_item = await vehicle.get_by_id(vehicle_id)
    if not vehicle_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    
    # Authorization: Only owner can view their vehicle
    if vehicle_item["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this vehicle.")

    return vehicle_item

@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: str,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(get_current_driver_or_company)
):
    existing_vehicle = await vehicle.get_by_id(vehicle_id)
    if not existing_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    
    # Authorization: Only owner can update their vehicle
    if existing_vehicle["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this vehicle.")

    updated_vehicle = await vehicle.update(vehicle_id, vehicle_in)
    if not updated_vehicle:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update vehicle.")
    return updated_vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_driver_or_company)
):
    vehicle_item = await vehicle.get_by_id(vehicle_id)
    if not vehicle_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    
    # Authorization: Only owner can delete their vehicle
    if vehicle_item["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this vehicle.")

    deleted = await vehicle.delete(vehicle_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete vehicle.")
    return
