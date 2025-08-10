from typing import List, Dict, Any, Optional
from app.api.v1.schemas.vehicles import VehicleCreate, VehicleUpdate
from app.db import mongodb

class CRUDVehicle:
    async def get_all(self, owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return await mongodb.get_vehicles_mongodb(owner_id)

    async def get_by_id(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        return await mongodb.get_vehicle_by_id_mongodb(vehicle_id)

    async def create(self, vehicle: VehicleCreate) -> Dict[str, Any]:
        return await mongodb.create_vehicle_mongodb(vehicle)

    async def update(self, vehicle_id: str, vehicle_in: VehicleUpdate) -> Optional[Dict[str, Any]]:
        return await mongodb.update_vehicle_mongodb(vehicle_id, vehicle_in.dict(exclude_unset=True))

    async def delete(self, vehicle_id: str) -> bool:
        return await mongodb.delete_vehicle_mongodb(vehicle_id)

vehicle = CRUDVehicle()
