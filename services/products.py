from repository.products import get_all_products
from schemas.product import ProductOut


def list_products():
    products = get_all_products()
    result = []
    for product in products:
        out = ProductOut(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            is_available=product.is_available,
        )
        result.append(out)
    return result
