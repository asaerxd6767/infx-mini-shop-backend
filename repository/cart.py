from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from models.cart import CartItem


def get_cart_items(user_id: int):
    with Session(engine, expire_on_commit=False) as db:
        return list(db.scalars(select(CartItem).where(CartItem.user_id == user_id)))


def add_cart_item(user_id: int, product_id: int, quantity: int):
    with Session(engine, expire_on_commit=False) as db:
        item = db.scalar(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        )
        if item is None:
            item = CartItem(
                user_id=user_id, product_id=product_id, quantity=quantity
            )
            db.add(item)
        else:
            item.quantity += quantity
        db.commit()
        return item


def delete_cart_item(user_id: int, product_id: int):
    with Session(engine, expire_on_commit=False) as db:
        item = db.scalar(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        )
        if item is None:
            return False
        db.delete(item)
        db.commit()
        return True
