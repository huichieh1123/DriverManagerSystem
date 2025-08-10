from typing import List, Optional
from enum import Enum
from pydantic import BaseModel
from .role_profiles import DriverProfile, DispatcherProfile, CompanyProfile, DriverProfileUpdate, DispatcherProfileUpdate, CompanyProfileUpdate

class RoleType(str, Enum):
    DRIVER = "driver"
    DISPATCHER = "dispatcher"
    COMPANY = "company"

class DispatcherAssociationStatus(str, Enum):
    ASSOCIATED = "associated"
    UNASSOCIATED = "unassociated"
    PENDING = "pending"

class DriverAssociationStatus(str, Enum):
    ASSOCIATED = "associated"
    UNASSOCIATED = "unassociated"
    PENDING = "pending"

class UserBase(BaseModel):
    username: str
    name: Optional[str] = None
    roles: List[RoleType] = []

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    roles: Optional[List[RoleType]] = None
    driver_profile: Optional[DriverProfileUpdate] = None
    dispatcher_profile: Optional[DispatcherProfileUpdate] = None
    company_profile: Optional[CompanyProfileUpdate] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    dispatcher_association_status: Optional[DispatcherAssociationStatus] = None
    driver_association_status: Optional[DriverAssociationStatus] = None

class User(UserBase):
    id: str
    driver_profile: Optional[DriverProfile] = None
    dispatcher_profile: Optional[DispatcherProfile] = None
    company_profile: Optional[CompanyProfile] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    dispatcher_association_status: Optional[DispatcherAssociationStatus] = None
    driver_association_status: Optional[DriverAssociationStatus] = None

    class Config:
        orm_mode = True