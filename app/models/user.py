from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship # We'll use this later for relationships
from datetime import datetime

from app.db.database import Base # Import the Base from database.py

class User(Base):
    __tablename__ = "users" # Must match your SQL table name exactly

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owned_events = relationship("Event", back_populates="owner") # <<<< THIS LINE IS CRUCIAL
    permissions = relationship("EventPermission", back_populates="user")
    event_versions_changed = relationship("EventVersion", back_populates="changed_by_user_detail")
    changelog_entries_by_user = relationship("Changelog", back_populates="user_detail")
         

class Role(Base):
    __tablename__ = "roles" # Must match your SQL table name exactly

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    permissions = relationship("EventPermission", back_populates="role")
