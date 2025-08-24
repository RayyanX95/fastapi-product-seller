from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter()


@router.get(
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


@router.get(
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


@router.delete(
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


@router.put(
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


@router.post(
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
