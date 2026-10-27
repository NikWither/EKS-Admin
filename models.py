from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

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