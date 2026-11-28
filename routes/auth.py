from fastapi import APIRouter

from schemas.user import LoginRequest, NewUser, Token, UserRead
from services import auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: NewUser):
    return auth.register_user(data)


@router.post("/login", response_model=Token)
def login(data: LoginRequest):
    return auth.login_user(data)
