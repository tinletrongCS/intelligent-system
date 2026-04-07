from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from schemas.domain_schemas import TokenResponse, UserResponse, UserCreate
import services.auth_service as auth_service
router = APIRouter()


# Đăng ký
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return await auth_service.register_user(user_in, db)


# Đăng nhập
@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return await auth_service.login(form_data, db)