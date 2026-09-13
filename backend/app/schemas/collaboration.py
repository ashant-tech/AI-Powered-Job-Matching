from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CollaborationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class CollaborationResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    email: EmailStr


class InvitationResponse(BaseModel):
    collaboration_id: int
    collaboration_name: str
    invitee_email: EmailStr
    invite_url: str
    expires_at: datetime


class InvitationDetails(BaseModel):
    collaboration_id: int
    collaboration_name: str
    invitee_email: EmailStr
    expires_at: datetime
    accepted: bool


class CollaborationMemberResponse(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    joined_at: datetime