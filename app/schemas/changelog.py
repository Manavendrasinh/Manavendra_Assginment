# app/schemas/changelog.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChangelogEntryUserDetailSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class ChangelogEntryResponseSchema(BaseModel):
    id: int
    event_id: int
    version_id: Optional[int] = None # The version that was created as a result of these changes
    user_id: Optional[int] = None
    user_details: Optional[ChangelogEntryUserDetailSchema] = None # Populated if user_id exists
    timestamp: datetime
    changes: Dict[str, Any] # The actual 'old' vs 'new' data

    class Config:
        from_attributes = True
