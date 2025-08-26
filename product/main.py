from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import product, seller

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
app.include_router(seller.router)

models.Base.metadata.create_all(engine)
