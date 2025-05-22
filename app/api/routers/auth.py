# app/api/routers/auth.py

# FastAPI and related imports
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm  # For login form data
from fastapi import Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# SQLAlchemy specific imports
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.config import settings

# Your application-specific imports
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserWithTokenResponse  # For registration
from app.schemas.token import Token, RefreshTokenRequest  # For the /login and /refresh response_model
from app.crud import crud_user  # Your user CRUD operations
from app.core.security import verify_password, create_access_token, create_refresh_token, add_to_blacklist  # Security utilities

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]  # This groups these endpoints in Swagger UI
)

# --- User Registration Endpoint ---
@router.post("/register", response_model=UserWithTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,  # Expects data matching UserCreate schema in request body
    db: Session = Depends(get_db)
):
    # Check if user with this email already exists
    db_user_by_email = crud_user.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Check if user with this username already exists
    db_user_by_username = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken."
        )

    # Create the new user
    created_user = crud_user.create_user(db=db, user=user_in)

    # Generate tokens for the newly registered user
    # The "sub" (subject) of the tokens will be the user's email
    access_token = create_access_token(data={"sub": created_user.email})
    refresh_token = create_refresh_token(data={"sub": created_user.email})

    # Return the created user's details and both tokens
    return {
        "user": created_user,  # FastAPI will convert this SQLAlchemy model to UserResponse
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# --- User Login Endpoint ---
@router.post("/login", response_model=UserWithTokenResponse)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()  # Handles username/password from form data
):
    # Attempt to fetch user by username (as provided in form_data.username)
    user = crud_user.get_user_by_username(db, username=form_data.username)
    
    # If not found by username, try by email (assuming username field might contain email)
    if not user:
        user = crud_user.get_user_by_email(db, email=form_data.username)

    # If user still not found, or if password verification fails
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},  # Standard header for 401 with Bearer auth
        )
    
    # Generate tokens if authentication is successful
    # The "sub" (subject) will be the user's email
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# --- Token Refresh Endpoint ---
@router.post("/refresh")
async def refresh_token(
    refresh_request: RefreshTokenRequest = Body(...),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            refresh_request.refresh_token,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if not email:
            raise credentials_exception
        # Optionally: Check if the refresh token is in a valid list (if you want to revoke tokens)
        new_access_token = create_access_token(data={"sub": email})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise credentials_exception

# --- User Logout Endpoint ---
http_bearer = HTTPBearer()

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
):
    token = credentials.credentials
    add_to_blacklist(token)
    return {"message": "Successfully logged out"}
