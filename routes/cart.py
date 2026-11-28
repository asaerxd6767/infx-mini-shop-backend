from fastapi import APIRouter, Depends

from schemas.cart import CartItemCreate, CartOut
from services import cart
from services.auth import get_current_user_id

router = APIRouter(tags=["cart"])


@router.post("/cart/items", response_model=CartOut)
def add_to_cart(
    data: CartItemCreate,
    user_id: int = Depends(get_current_user_id),
):
    return cart.add_to_cart(user_id, data)


@router.get("/cart", response_model=CartOut)
def get_cart(user_id: int = Depends(get_current_user_id)):
    return cart.get_cart(user_id)


@router.delete("/cart/items/{product_id}", response_model=CartOut)
def remove_from_cart(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
):
    return cart.remove_from_cart(user_id, product_id)
