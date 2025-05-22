# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional # Or use `| None` for Python 3.10+ if using Pydantic v2
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for the user")
    email: EmailStr 
    password: str = Field(..., min_length=8, description="User's password, at least 8 characters")

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class UserWithTokenResponse(BaseModel):
    user: UserResponse        # The user's details, shaped by UserResponse
    access_token: str         # The JWT access token
    refresh_token: str 
    token_type: str = "bearer" # Standard token type
