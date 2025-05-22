# app/models/event.py (or wherever you place the Event model)
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, TEXT, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(TEXT, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False) # Corresponds to TIMESTAMPTZ
    end_time = Column(DateTime(timezone=True), nullable=False)   # Corresponds to TIMESTAMPTZ
    location = Column(String(255), nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow) # Use timezone=True for TIMESTAMPTZ
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship to the User who owns the event
    owner = relationship("User", back_populates="owned_events")

    # Relationships to other event-related tables
    permissions = relationship("EventPermission", back_populates="event", cascade="all, delete-orphan")
    versions = relationship("EventVersion", back_populates="event", cascade="all, delete-orphan")
    changelogs = relationship("Changelog", back_populates="event", cascade="all, delete-orphan")


