from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from models import Product
from schemas import ProductCreate, ProductRead, ProductType, ProductUpdate
from lookups import find_product_or_404


router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductRead])
def get_products(
    type: ProductType | None = None,
    max_price: int | None = Query(default=None, ge=0),
    session: Session = Depends(get_session),
):
    statement = select(Product)
    
    if type is not None:
        statement = statement.where(Product.type == type.value)
    
    if max_price is not None:
        statement = statement.where(Product.price <= max_price)
    
    return session.scalars(statement).all()

@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
    ):
    return find_product_or_404(session, product_id)

@router.post("", status_code=201, response_model=ProductRead)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
):
    new_product = Product(**product.model_dump(mode="json"))
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    
    return new_product

@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    data: ProductUpdate,
    session: Session = Depends(get_session),
    ):
    product = find_product_or_404(session, product_id)
    changes = data.model_dump(mode="json", exclude_unset=True)
    
    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=422,
            detail="Product field cannot be null",
        )
    
    for field, value in changes.items():
        setattr(product, field, value)

    session.commit()
    session.refresh(product)

    return product

@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session)
    ):
    product = find_product_or_404(session, product_id)

    session.delete(product)
    session.commit()

    return Response(status_code=204)