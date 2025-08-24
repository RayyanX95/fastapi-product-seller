from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine, get_db
from .routers import product

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

# Enable CORS for development (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product.router)

models.Base.metadata.create_all(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
