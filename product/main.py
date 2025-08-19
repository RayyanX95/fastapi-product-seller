from fastapi import FastAPI

from . import models, schemas
from .database import engine

app = FastAPI()

models.Base.metadata.create_all(engine)


@app.post("/product")
def add(request: schemas.Product):
    return {"message": "Product added successfully", "product": request}
