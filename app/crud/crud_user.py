# app/crud/crud_user.py
from sqlalchemy.orm import Session
from typing import Optional

# Import your SQLAlchemy User model and Pydantic UserCreate schema
from app.models.user import User as UserModel # Adjust import if your model is named differently or located elsewhere
from app.schemas.user import UserCreate     # Pydantic schema for creating a user
from app.core.security import get_password_hash # For hashing passwords

def get_user_by_id(db: Session, user_id: int) -> Optional[UserModel]:
    """
    Retrieve a user by their ID.
    """
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """
    Retrieve a user by their email address.
    """
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """
    Retrieve a user by their username.
    """
    return db.query(UserModel).filter(UserModel.username == username).first()

def create_user(db: Session, user: UserCreate) -> UserModel:
    """
    Create a new user in the database.
    - Hashes the password before storing.
    - Adds the new user to the session, commits, and refreshes to get DB-generated values.
    """
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
        # created_at and updated_at will use their default values defined in the model
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # This ensures that 'id', 'created_at', etc., are populated from the DB
    return db_user
