from fastapi import HTTPException

from repository.orders import create_order, get_order_items, get_user_orders
from repository.products import get_product_by_id
from schemas.order import OrderItemOut, OrderOut
from services.cart import get_cart


def order_to_out(order):
    items = []
    rows = get_order_items(order.id)
    for row in rows:
        item = OrderItemOut(
            product_id=row.product_id,
            name=row.name,
            unit_price=row.unit_price,
            quantity=row.quantity,
            line_total=row.line_total,
        )
        items.append(item)

    return OrderOut(
        id=order.id,
        created_at=order.created_at,
        total_price=order.total_price,
        items=items,
    )


def checkout(user_id: int):
    cart = get_cart(user_id)
    if len(cart.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    for item in cart.items:
        product = get_product_by_id(item.product_id)
        if not product.is_available:
            raise HTTPException(
                status_code=400, detail=f"{product.name} is not available"
            )

        row = {
            "product_id": item.product_id,
            "name": item.name,
            "unit_price": item.unit_price,
            "quantity": item.quantity,
            "line_total": item.line_total,
        }
        order_items.append(row)

    order = create_order(user_id, order_items, cart.total_price)
    return order_to_out(order)


def list_orders(user_id: int):
    result = []
    orders = get_user_orders(user_id)
    for order in orders:
        out = order_to_out(order)
        result.append(out)
    return result
