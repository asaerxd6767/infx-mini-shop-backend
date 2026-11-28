from fastapi import APIRouter

from schemas.product import ProductOut
from services import products

router = APIRouter(tags=["products"])


@router.get("/products", response_model=list[ProductOut])
def get_products():
    return products.list_products()
