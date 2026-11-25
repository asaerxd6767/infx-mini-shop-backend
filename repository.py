from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine
from models import User


def get_user_by_email(email: str):
    with Session(engine, expire_on_commit=False) as db:
        return db.scalar(select(User).where(User.email == email))


def get_all_users():
    with Session(engine, expire_on_commit=False) as db:
        return list(db.scalars(select(User)))


def insert_user(name: str, email: str, password_hash: str):
    with Session(engine, expire_on_commit=False) as db:
        user = User(name=name, email=email, password_hash=password_hash)
        db.add(user)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return None
        return user