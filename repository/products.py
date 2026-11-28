from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from models.product import Product


def get_all_products():
    with Session(engine, expire_on_commit=False) as db:
        return list(db.scalars(select(Product).order_by(Product.id)))


def get_product_by_id(product_id: int):
    with Session(engine, expire_on_commit=False) as db:
        return db.scalar(select(Product).where(Product.id == product_id))
