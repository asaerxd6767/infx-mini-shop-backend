from decimal import Decimal

from fastapi import HTTPException

from repository.cart import add_cart_item, delete_cart_item, get_cart_items
from repository.products import get_product_by_id
from schemas.cart import CartItemCreate, CartItemOut, CartOut


def get_cart(user_id: int):
    items = []
    total = Decimal("0.00")

    cart_rows = get_cart_items(user_id)
    for row in cart_rows:
        product = get_product_by_id(row.product_id)
        if product is None:
            continue

        line_total = product.price * row.quantity
        total = total + line_total

        item = CartItemOut(
            product_id=product.id,
            name=product.name,
            unit_price=product.price,
            quantity=row.quantity,
            line_total=line_total,
        )
        items.append(item)

    return CartOut(items=items, total_price=total)


def add_to_cart(user_id: int, data: CartItemCreate):
    product = get_product_by_id(data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.is_available:
        raise HTTPException(status_code=400, detail="Product is not available")

    add_cart_item(user_id, data.product_id, data.quantity)
    return get_cart(user_id)


def remove_from_cart(user_id: int, product_id: int):
    delete_cart_item(user_id, product_id)
    return get_cart(user_id)
