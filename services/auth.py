from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from repository.users import get_user_by_email, insert_user
from schemas.user import LoginRequest, NewUser, Token

security = HTTPBearer()


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


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = data.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")


def register_user(data: NewUser):
    user = insert_user(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    if user is None:
        raise HTTPException(status_code=409, detail="Email already registered")
    return user


def login_user(data: LoginRequest):
    user = get_user_by_email(data.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user))
