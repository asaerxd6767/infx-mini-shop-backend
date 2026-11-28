from decimal import Decimal

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool
