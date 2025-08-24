from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.params import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine

app = FastAPI(
    title="Product Management API",
    description="API for managing products and sellers",
    version="1.0.0",
    summary="A FastAPI application for CRUD operations on products and sellers.",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Support Team",
        "url": "https://example.com/contact",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Products",
            "description": "Operations related to products (list, get, create, update, delete)",
        },
        {"name": "Sellers", "description": "Operations related to seller accounts"},
    ],
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
        {"url": "https://api.example.com", "description": "Production server"},
    ],
)

models.Base.metadata.create_all(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/products",
    response_model=List[schemas.DisplayProduct],
    tags=["Products"],
    summary="List all products",
    description="Retrieve a list of all products. Supports pagination and filtering in future iterations.",
    response_description="A JSON array of product objects",
    operation_id="listProducts",
)
def products(db: Session = Depends(get_db)):
    """Return all products from the database.

    Returns a list of products. Each product is represented using the
    `DisplayProduct` schema (passwords or sensitive info are never returned).
    """
    return db.query(models.Product).all()


@app.get(
    "/products/{id}",
    response_model=schemas.DisplayProduct,
    tags=["Products"],
    summary="Get product by ID",
    description="Retrieve a single product by its unique ID.",
    responses={
        200: {"description": "Product returned successfully"},
        404: {"description": "Product not found"},
    },
    operation_id="getProductById",
)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.delete(
    "/product/{id}",
    tags=["Products"],
    summary="Delete a product",
    description="Delete a product by its ID. Returns a success message on deletion.",
    responses={
        200: {
            "description": "Product deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Product deleted successfully"}
                }
            },
        },
        404: {"description": "Product not found"},
    },
    operation_id="deleteProduct",
)
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if product:
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")


@app.put(
    "/product/{id}",
    response_model=schemas.DisplayProduct,
    tags=["Products"],
    summary="Update a product",
    description="Update one or more fields of a product. Send only the fields to be updated.",
    responses={
        200: {"description": "Product updated successfully"},
        404: {"description": "Product not found"},
        422: {"description": "Validation error"},
    },
    operation_id="updateProduct",
)
def update_product(
    id: int, request: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@app.post(
    "/add_product",
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a new product",
    description="Create a new product. The current implementation assigns seller_id=1 by default.",
    responses={
        201: {
            "description": "Product created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Product added successfully",
                        "product": {
                            "id": 1,
                            "name": "Sample",
                            "description": "Sample desc",
                            "price": 9.99,
                            "seller_id": 1,
                        },
                    }
                }
            },
        },
        400: {"description": "Bad request"},
    },
    operation_id="createProduct",
)
def add(request: schemas.Product, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=request.name,
        description=request.description,
        price=request.price,
        seller_id=1,
    )

    print(
        f"Adding product: {new_product.name}, Price: {new_product.price}, Description: {new_product.description}"
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product added successfully", "product": new_product}


@app.post(
    "/seller",
    response_model=schemas.DisplaySeller,
    status_code=status.HTTP_201_CREATED,
    tags=["Sellers"],
    summary="Create a seller account",
    description="Register a new seller. Passwords are hashed before storage; the returned seller does not include the password field.",
    responses={
        201: {"description": "Seller created successfully"},
        400: {"description": "Invalid input"},
    },
    operation_id="createSeller",
)
def create_seller(request: schemas.Seller, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(request.password)
    new_seller = models.Seller(
        username=request.username, email=request.email, password=hashed_password
    )

    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return new_seller
