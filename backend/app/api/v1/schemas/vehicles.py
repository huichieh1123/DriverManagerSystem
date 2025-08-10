from typing import Optional
from pydantic import BaseModel

class VehicleBase(BaseModel):
    license_plate: str # 車號
    make: Optional[str] = None # 廠牌
    model: Optional[str] = None # 車型
    capacity: Optional[int] = None # 座位數
    color: Optional[str] = None # 顏色
    manufacture_year: Optional[str] = None # 出廠年月
    insurance_valid_date: Optional[str] = None # 保單有效日
    passenger_insurance_amount: Optional[float] = None # 乘客保險金額
    owner_id: Optional[str] = None # User ID of the owner (driver or company)

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    capacity: Optional[int] = None
    color: Optional[str] = None
    manufacture_year: Optional[str] = None
    insurance_valid_date: Optional[str] = None
    passenger_insurance_amount: Optional[float] = None

class Vehicle(VehicleBase):
    id: str

    class Config:
        orm_mode = True
