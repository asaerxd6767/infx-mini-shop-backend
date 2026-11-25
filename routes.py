from fastapi import APIRouter

from schemas import LoginRequest, NewUser, Token, UserRead
import services

router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(tags=["users"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
)
def register(data: NewUser):
    return services.register_user(data)


@router.post("/login", response_model=Token)
def login(data: LoginRequest):
    return services.login_user(data)


@users_router.get("/users", response_model=list[UserRead])
def get_users():
    return services.list_users()
