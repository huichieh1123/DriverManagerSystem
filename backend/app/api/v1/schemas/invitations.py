from typing import Optional
from enum import Enum
from pydantic import BaseModel
from .users import RoleType

class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class InvitationBase(BaseModel):
    company_id: str
    company_name: str
    invitee_id: str
    invitee_username: str
    invitee_role: RoleType
    status: InvitationStatus = InvitationStatus.PENDING

class InvitationCreate(BaseModel):
    invitee_username: str
    invitee_role: RoleType

class Invitation(InvitationBase):
    id: str

    class Config:
        orm_mode = True