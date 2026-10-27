from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

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
