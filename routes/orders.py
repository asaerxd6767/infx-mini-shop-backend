from fastapi import APIRouter, Depends

from schemas.order import OrderOut
from services import orders
from services.auth import get_current_user_id

router = APIRouter(tags=["orders"])


@router.post("/orders", response_model=OrderOut, status_code=201)
def place_order(user_id: int = Depends(get_current_user_id)):
    return orders.checkout(user_id)


@router.get("/orders", response_model=list[OrderOut])
def get_orders(user_id: int = Depends(get_current_user_id)):
    return orders.list_orders(user_id)
