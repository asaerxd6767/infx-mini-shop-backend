from fastapi import APIRouter

from schemas import NewUser, UserRead
import services

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
)
def register(data: NewUser):
    return services.register_user(data)
