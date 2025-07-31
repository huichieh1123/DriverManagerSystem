from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.v1.schemas.users import UserCreate, UserLogin, User, RoleType, UserUpdate, DispatcherAssociationStatus
from app.crud import user
from app.db.mongodb import users_collection, user_helper # Import users_collection and user_helper

router = APIRouter()

# Dependency to get current user (simplified for now)
# In a real app, this would involve JWT or session management
async def get_current_user(username: str) -> User:
    user_data = await user.get_by_username(username)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_data)

@router.post("/users/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate):
    existing_user = await user.get_by_username(user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # In a real app, hash the password before storing
    new_user = await user.create(user_in)
    return new_user

@router.post("/users/login", response_model=User)
async def login_user(user_in: UserLogin):
    user_data = await user.get_by_username(user_in.username)
    if not user_data or user_data["password"] != user_in.password:
        # In a real app, compare hashed passwords
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return User(**user_data)

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    # This endpoint is simplified. In a real app, the current_user would come from a token.
    # For now, you can pass a username as a query parameter to simulate login.
    # e.g., /api/v1/users/me?username=testuser
    return current_user

@router.put("/users/me", response_model=User)
async def update_users_me(user_in: UserUpdate, current_user: User = Depends(get_current_user)):
    user_data = await user.update(current_user.id, user_in)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found for update")
    return User(**user_data)

@router.get("/users/", response_model=List[User])
async def get_users_by_role(
    role: Optional[RoleType] = None,
    current_user: User = Depends(get_current_user) # Ensure user is logged in
):
    # For simplicity, we'll just return all users for now if no role is specified
    # In a real app, you'd have more granular control over who can see what users
    query = {}
    if role:
        query["roles"] = role.value

    all_users = []
    async for u in users_collection.find(query):
        all_users.append(User(**user_helper(u)))
    return all_users
