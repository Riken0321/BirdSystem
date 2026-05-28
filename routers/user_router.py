from fastapi import APIRouter, HTTPException, Depends
from models.user import User_Pydantic, UserIn_Pydantic
from tortoise.exceptions import DoesNotExist
from utils.auth import get_current_user
from services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.post("/users/", response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    return await user_service.create_user(user)

@router.get("/users/", response_model=list[User_Pydantic])
async def get_all_users():
    return await user_service.get_all_users()

@router.get("/users/{user_id}", response_model=User_Pydantic, status_code=200)
async def get_user_by_id(user_id: int):
    try:
        return await user_service.get_user_by_id(user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}", response_model=User_Pydantic)
async def update_user(user_id: int, user: UserIn_Pydantic, current_user: User_Pydantic = Depends(get_current_user)):
    try:
        return await user_service.update_user(user_id, user)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User_Pydantic = Depends(get_current_user)):
    try:
        await user_service.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
