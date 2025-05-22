# app/schemas/permission.py
from pydantic import BaseModel
from typing import List

class EventPermissionCreate(BaseModel):
    """
    Schema for creating a new EventPermission.
    """
    user_id: int
    role_id: int

class EventPermissionResponse(BaseModel):
    """
    Schema for returning an EventPermission.
    """
    id: int
    event_id: int
    user_id: int
    role_id: int

    class Config:
        from_attributes = True

class EventPermissionUpdate(BaseModel):
    role_id: int

# For listing permissions with user/role details
class EventPermissionDetail(BaseModel):
    id: int
    event_id: int
    user_id: int
    username: str
    email: str
    role_id: int
    role_name: str

    class Config:
        from_attributes = True