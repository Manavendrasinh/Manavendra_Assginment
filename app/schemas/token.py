# app/schemas/token.py
from pydantic import BaseModel
from typing import Optional # Use Optional for Pydantic v1, or | None for Pydantic v2 + Python 3.10+

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str