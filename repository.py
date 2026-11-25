from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import engine
from models import User


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