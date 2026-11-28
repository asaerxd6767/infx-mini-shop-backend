from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database import engine
from models.cart import CartItem
from models.order import Order, OrderItem


def create_order(user_id: int, items, total_price: Decimal):
    with Session(engine, expire_on_commit=False) as db:
        order = Order(user_id=user_id, total_price=total_price)
        db.add(order)
        db.flush()  # so order.id exists for the order items

        for item in items:
            db.add(OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                name=item["name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
                line_total=item["line_total"],
            ))

        db.execute(delete(CartItem).where(CartItem.user_id == user_id))
        db.commit()
        db.refresh(order)
        return order


def get_user_orders(user_id: int):
    with Session(engine, expire_on_commit=False) as db:
        return list(
            db.scalars(
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
            )
        )


def get_order_items(order_id: int):
    with Session(engine, expire_on_commit=False) as db:
        return list(
            db.scalars(select(OrderItem).where(OrderItem.order_id == order_id))
        )
