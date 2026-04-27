from fastapi import APIRouter, Depends,status, Query
from sqlalchemy.orm import Session
from models import User
from database import get_db
from schemas.product_schema import ProductResponse, ProductCreate, ProductUpdate, ProductQuantityUpdate
from schemas.base_schema import IMessageResponse
from dependencies.auth_deps import get_current_user, require_admin, require_seller
from services import product_service
from typing import List
from uuid import UUID

router = APIRouter()
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)):
    return await product_service.create_new_product(product_in, db)

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return await product_service.list_products_logic(skip, limit, db)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return await product_service.get_product_by_id(current_user.id, product_id, db)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await product_service.update_product_logic(product_id, product_in, db)

@router.patch("/{product_id}/quantity", response_model=ProductResponse)
async def update_product_quantity(
    product_id: UUID,
    quantity_in: ProductQuantityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await product_service.update_product_quantity_logic(product_id, quantity_in.quantity_in_stock, db)

@router.delete("/{product_id}", response_model=IMessageResponse)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return await product_service.delete_product_logic(product_id, db)
