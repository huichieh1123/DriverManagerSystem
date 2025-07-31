from typing import Optional, List
from pydantic import BaseModel

# --- Driver Profile ---
class DriverProfileBase(BaseModel):
    license_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    # Add more driver-specific fields here

class DriverProfileCreate(DriverProfileBase):
    pass

class DriverProfileUpdate(DriverProfileBase):
    pass

class DriverProfile(DriverProfileBase):
    pass # No extra fields for now, but could add driver_id if needed

# --- Dispatcher Profile ---
class DispatcherProfileBase(BaseModel):
    dispatch_area: Optional[str] = None
    contact_phone: Optional[str] = None
    # Add more dispatcher-specific fields here

class DispatcherProfileCreate(DispatcherProfileBase):
    pass

class DispatcherProfileUpdate(DispatcherProfileBase):
    pass

class DispatcherProfile(DispatcherProfileBase):
    pass

# --- Company Profile ---
class CompanyProfileBase(BaseModel):
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    contact_person: Optional[str] = None
    # Add more company-specific fields here

class CompanyProfileCreate(CompanyProfileBase):
    pass

class CompanyProfileUpdate(CompanyProfileBase):
    pass

class CompanyProfile(CompanyProfileBase):
    pass
