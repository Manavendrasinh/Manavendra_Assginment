# app/models/changelog.py (or wherever you place Changelog model)
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Changelog(Base):
    __tablename__ = "changelog"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    # A changelog entry is usually associated with a version that resulted from the change
    version_id = Column(Integer, ForeignKey("event_versions.id", ondelete="CASCADE"), nullable=True) # Making it nullable if some logs are not direct version changes
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) # User who made the change
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow) # Corresponds to TIMESTAMPTZ
    changes = Column(JSONB, nullable=False) # Details of what changed (e.g., diff)

    # Relationships
    event = relationship("Event", back_populates="changelogs")
    user_detail = relationship("User", back_populates="changelog_entries_by_user") # Changed from 'user'
 
    version_detail = relationship("EventVersion") 
