from fastapi import APIRouter, status
from fastapi.params import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(prefix="/api/v1", tags=["Sellers"])


@router.post(
    "/seller",
    response_model=schemas.DisplaySeller,
    status_code=status.HTTP_201_CREATED,
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
