from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: int
    description: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None


class DisplayProduct(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class Seller(BaseModel):
    username: str
    email: str
    password: str
