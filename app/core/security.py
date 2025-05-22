# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any # Added Dict, Any for type hints
from jose import JWTError, jwt
from sqlalchemy import text
from app.db.database import SessionLocal
from hashlib import sha256
# Import your actual settings from app.core.config
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

# In app/core/security.py

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)  # e.g., 30 days
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def add_to_blacklist(token: str):
    token_hash = sha256(token.encode()).hexdigest()
    with SessionLocal() as db:
        db.execute(
            text("INSERT INTO token_blacklist (token_hash, created_at) VALUES (:token_hash, NOW())"),
            {"token_hash": token_hash}
        )
        db.commit()

def is_token_blacklisted(token: str) -> bool:
    token_hash = sha256(token.encode()).hexdigest()
    with SessionLocal() as db:
        result = db.execute(
            text("SELECT 1 FROM token_blacklist WHERE token_hash = :token_hash"),
            {"token_hash": token_hash}
        ).fetchone()
        return result is not None

def cleanup_blacklist(days: int = 7):
    with SessionLocal() as db:
        db.execute(
            text("DELETE FROM token_blacklist WHERE created_at < NOW() - INTERVAL :days DAY"),
            {"days": days}
        )
        db.commit()


