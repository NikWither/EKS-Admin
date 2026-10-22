from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
from enum import Enum

class ProductType(str, Enum):
    software = "software"
    service = "service"
    equipment = "equipment"

class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    price: int = Field(ge=0)
    type: ProductType
    
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, ge=0)
    type: ProductType | None = None
    
class ProductRead(BaseModel):
    id: int
    name: str
    price: int
    type: ProductType

app = FastAPI()

products = [
    {"id": 1, "name": "ERP System for analyze sales", "type": "software", "price": 15000},
    {"id": 2, "name": "CMS System with SEO", "type": "software", "price": 20000},
]

def find_product_or_404(product_id: int) -> dict:
    for product in products:
        if product["id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/")
def root():
    return {"message": "ERP is working"}

@app.get("/products", response_model=list[ProductRead])
def get_products(
    type: ProductType | None = None,
    max_price: int | None = Query(default=None, ge=0)
):
    result = products
    
    if type is not None:
        result = [
            product for product in result
            if product["type"] == type
        ]
    
    if max_price is not None:
        result = [
            product for product in result
            if product["price"] <= max_price
        ]
    
    return result

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int):
    return find_product_or_404(product_id)

@app.post("/products", status_code=201, response_model=ProductRead)
def create_product(product: ProductCreate):
    new_id = max((item["id"] for item in products), default=0) + 1
    
    new_product = {
        "id": new_id,
        **product.model_dump(mode="json"),
    }
    
    products.append(new_product)
    
    return new_product

@app.patch("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate):
    product = find_product_or_404(product_id)
    changes = data.model_dump(mode="json", exclude_unset=True)
    
    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=422,
            detail="Product field cannot be null",
        )
    
    product.update(changes)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int):
    product = find_product_or_404(product_id)
    products.remove(product)
    return Response(status_code=204)