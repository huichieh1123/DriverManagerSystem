from typing import Optional
from enum import Enum
from pydantic import BaseModel

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class InvitationBase(BaseModel):
    company_id: str # Changed from int to str
    company_name: str
    dispatcher_id: str # Changed from int to str
    dispatcher_username: str
    status: InvitationStatus = InvitationStatus.PENDING

class InvitationCreate(BaseModel):
    dispatcher_username: str # Company sends invitation to this dispatcher

class Invitation(InvitationBase):
    id: str # Changed from int to str

    class Config:
        orm_mode = True
