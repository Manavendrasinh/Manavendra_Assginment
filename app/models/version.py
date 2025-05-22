# app/models/version.py (or wherever you place EventVersion model)
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class EventVersion(Base):
    __tablename__ = "event_versions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    data = Column(JSONB, nullable=False) # Snapshot of event data
    changed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow) # Corresponds to TIMESTAMPTZ

    # Relationships
    event = relationship("Event", back_populates="versions")
    changed_by_user_detail = relationship("User", back_populates="event_versions_changed") 
    # Define the unique constraint
    __table_args__ = (
        UniqueConstraint('event_id', 'version_number', name='uq_event_version'),
    )
