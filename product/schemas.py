from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: int
    description: str
    description: str
