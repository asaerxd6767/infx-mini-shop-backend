from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0, le=99)


class CartItemOut(BaseModel):
    product_id: int
    name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class CartOut(BaseModel):
    items: list[CartItemOut]
    total_price: Decimal
