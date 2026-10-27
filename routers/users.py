from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_session
from lookups import find_product_or_404, find_user_or_404
from models import User
from schemas import ProductRead, UserCreate, UserRead


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    return session.scalars(select(User)).all()

@router.post("", status_code=201, response_model=UserRead)
def create_user(
    data: UserCreate,
    session: Session = Depends(get_session),
):
    user = User(**data.model_dump())
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@router.post(
    "/{user_id}/products/{product_id}",
    status_code=201,
    response_model=ProductRead,
)
def assign_product(
    user_id: int,
    product_id: int,
    session: Session = Depends(get_session),
):
    user = find_user_or_404(session, user_id)
    product = find_product_or_404(session, product_id)
    
    if product in user.products:
        raise HTTPException(
            status_code=409,
            detail="Product already assigned to user",
        )
    
    user.products.append(product)
    session.commit()
    
    return product

@router.get(
    "/{user_id}/products",
    response_model=list[ProductRead],
)
def get_user_products(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = find_user_or_404(session, user_id)
    return user.products

@router.delete(
    "/{user_id}/products/{product_id}",
    status_code=204,
)
def unassign_product(
    user_id: int,
    product_id: int,
    session: Session = Depends(get_session),
):
    user = find_user_or_404(session, user_id)
    product = find_product_or_404(session, product_id)
    
    if product not in user.products:
        raise HTTPException(
            status_code=404,
            detail="Products is not assigned to user"
        )
    
    user.products.remove(product)
    session.commit()
    
    return Response(status_code=204)


