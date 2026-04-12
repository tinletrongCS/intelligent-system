from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models.domain_models import User
from database import get_db
from dependencies.auth_deps import require_admin, get_current_user
from schemas.domain_schemas import TokenResponse, UserResponse, UserCreate, RoleUpdate, UserRoleResponse
from uuid import UUID
import services.auth_service as auth_service
router = APIRouter()