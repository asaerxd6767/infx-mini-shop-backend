from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItemOut(BaseModel):
    product_id: int
    name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class OrderOut(BaseModel):
    id: int
    created_at: datetime
    total_price: Decimal
    items: list[OrderItemOut]
