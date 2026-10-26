from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

from pathlib import Path

from sqlalchemy import create_engine, Integer, String, select, Column, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class ProductType(str, Enum):
    software = "software"
    service = "service"
    equipment = "equipment"

class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    organization: str = Field(min_length=1)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    organization: str

class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    price: int = Field(ge=0)
    type: ProductType
    
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, ge=0)
    type: ProductType | None = None
    
class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: int
    type: ProductType

class Base(DeclarativeBase):
    pass

user_products = Table(
    "user_products",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(255))
    users: Mapped[list["User"]] = relationship(
        secondary=user_products,
        back_populates="products"
    )

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    organization: Mapped[str] = mapped_column(String(255))
    products: Mapped[list["Product"]] = relationship(
        secondary=user_products,
        back_populates="users",
    )

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'erp.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
)

Base.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()

def find_product_or_404(
    session: Session,
    product_id: int
    ) -> Product:
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

@app.get("/")
def root():
    return {"message": "ERP is working"}

@app.post("/users", status_code=201, response_model=UserRead)
def create_user(
    data: UserCreate,
    session: Session = Depends(get_session),
):
    user = User(**data.model_dump())
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@app.post(
    "/users/{user_id}/products/{product_id}",
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

@app.get(
    "/users/{user_id}/products",
    response_model=list[ProductRead],
)
def get_user_products(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = find_user_or_404(session, user_id)
    return user.products

@app.get("/users", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    return session.scalars(select(User)).all()

@app.get("/products", response_model=list[ProductRead])
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

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
    ):
    return find_product_or_404(session, product_id)

@app.post("/products", status_code=201, response_model=ProductRead)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
):
    new_product = Product(**product.model_dump(mode="json"))
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    
    return new_product

@app.patch("/products/{product_id}", response_model=ProductRead)
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

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session)
    ):
    product = find_product_or_404(session, product_id)

    session.delete(product)
    session.commit()

    return Response(status_code=204)