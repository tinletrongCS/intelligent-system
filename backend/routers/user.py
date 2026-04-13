from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models.user_model import User
from database import get_db
from dependencies.auth_deps import require_admin, get_current_user
from schemas.user_schema import TokenResponse, UserResponse, UserCreate, RoleUpdate, UserRoleResponse
from uuid import UUID
import services.auth_service as auth_service
router = APIRouter()