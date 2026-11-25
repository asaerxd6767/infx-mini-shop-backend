import bcrypt
from fastapi import HTTPException

from repository import insert_user
from schemas import NewUser


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def register_user(data: NewUser):
    user = insert_user(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    if user is None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )
    return user