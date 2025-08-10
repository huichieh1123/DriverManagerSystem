from typing import Optional, List
from pydantic import BaseModel

# --- Driver Profile ---
class DriverProfileBase(BaseModel):
    chinese_name: Optional[str] = None
    english_name: Optional[str] = None
    id_card_number: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    license_valid_date: Optional[str] = None
    license_review_date: Optional[str] = None
    license_type: Optional[str] = None
    gmail: Optional[str] = None

class DriverProfileCreate(DriverProfileBase):
    pass

class DriverProfileUpdate(DriverProfileBase):
    pass

class DriverProfile(DriverProfileBase):
    pass # No extra fields for now, but could add driver_id if needed

# --- Bank Account for Dispatcher ---
class BankAccount(BaseModel):
    bank_code: Optional[str] = None
    account_number: Optional[str] = None

# --- Dispatcher Profile ---
class DispatcherProfileBase(BaseModel):
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    work_nature: Optional[str] = None
    bank_accounts: Optional[List[BankAccount]] = []
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
    tax_id: Optional[str] = None
    admin_line_id: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

class CompanyProfileCreate(CompanyProfileBase):
    pass

class CompanyProfileUpdate(CompanyProfileBase):
    pass

class CompanyProfile(CompanyProfileBase):
    pass
