from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from product.database import get_db

from .. import models, schemas

router = APIRouter(prefix="/api/v1", tags=["Login"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post(
    "/login", response_model=schemas.LoginResponse, status_code=status.HTTP_200_OK
)
def login(request: schemas.Login, db: Session = Depends(get_db)):
    user = (
        db.query(models.Seller)
        .filter(models.Seller.username == request.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # Generate JWT token
    # access_token = create_access_token(data={"sub": user.username})
    return {"access_token": "access_token", "token_type": "bearer"}
