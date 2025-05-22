# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.db.database import get_db
from app.models.user import User as UserModel
from app.schemas.token import TokenData
from app.core.config import settings
from app.crud import crud_user
from app.core.security import is_token_blacklisted  # <-- Add this import

http_bearer = HTTPBearer()  # This will show a "Bearer <token>" field in Swagger UI

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials object
        token = credentials.credentials

        # Check if token is blacklisted
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str | None = payload.get("sub")
        
        if email is None:
            raise credentials_exception

        try:
            token_data = TokenData(sub=email)
        except ValidationError:
            raise credentials_exception

        user = crud_user.get_user_by_email(db, email=token_data.sub)
        if user is None:
            raise credentials_exception
            
        return user

    except JWTError:
        raise credentials_exception
