from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Product, User


def find_product_or_404(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

def find_user_or_404(
    session: Session,
    user_id: int
) -> User:
    user = session.get(User, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user