from fastapi import APIRouter

from schemas.user import UserRead
from services import users

router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[UserRead])
def get_users():
    return users.list_users()
