# app/api/routers/users.py
from fastapi import APIRouter, Depends
from typing import List # For potential future endpoints returning lists of users

# Import your Pydantic schema for user output
from app.schemas.user import UserResponse
# Import your dependency to get the current authenticated user
from app.api.deps import get_current_user
# Import your SQLAlchemy User model
from app.models.user import User as UserModel

router = APIRouter(
    prefix="/api/users",  # All routes in this file will start with /api/users
    tags=["Users"]        # Group these endpoints under "Users" in Swagger UI
)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Get details for the current logged-in user.
    This endpoint is protected and requires authentication.
    """
    # The current_user object is the SQLAlchemy model instance.
    # FastAPI will automatically convert it to a UserResponse Pydantic model
    # because of the `response_model=UserResponse` decorator.
    return current_user

# You can add other user-related endpoints here later, for example:
# @router.get("/", response_model=List[UserResponse])
# async def read_users(skip: int = 0, limit: int = 100, current_user: UserModel = Depends(get_current_user)):
#     """
#     Retrieve users (example, might need admin privileges in a real app).
#     """
#     # For now, this would just return the current user in a list as an example.
#     # In a real app, you'd fetch users from DB via CRUD operations.
#     # Ensure current_user has permissions to list users.
#     return [current_user]
