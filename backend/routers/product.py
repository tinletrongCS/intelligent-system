from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.product_schema import ProductResponse, ProductCreate
from controllers import product_controller
from typing import List
from uuid import UUID

# router = APIRouter(prefix="/products", tags=["Products"])
router = APIRouter()
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    return await product_controller.add_product_controller(product_in, db)

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return await product_controller.get_all_products_controller(skip, limit, db)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(product_id: UUID, db: Session = Depends(get_db)):
    return await product_controller.get_product_controller(product_id, db)