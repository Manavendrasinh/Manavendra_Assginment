# app/models/permission.py

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base

class EventPermission(Base):
    __tablename__ = "event_permissions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    event = relationship("Event", back_populates="permissions")
    user = relationship("User", back_populates="permissions")
    role = relationship("Role", back_populates="permissions")

    # Define the unique constraint
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='uq_event_user_permission'),
    )
