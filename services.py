from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import HTTPException
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from repository import get_all_users, get_user_by_email, insert_user
from schemas import LoginRequest, NewUser, Token


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": str(user.id), "email": user.email, "exp": expires}
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


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


def login_user(data: LoginRequest):
    user = get_user_by_email(data.email)
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )
    return Token(access_token=create_access_token(user))


def list_users():
    return get_all_users()
