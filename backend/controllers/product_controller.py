from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import services.product_service as product_service
from schemas.product_schema import ProductCreate
from uuid import UUID

async def add_product_controller(product_in: ProductCreate, db: Session):
    return await product_service.create_new_product(product_in, db)

async def get_product_controller(product_id: UUID, db: Session):
    product = await product_service.get_product_logic(product_id, db)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Sản phẩm với ID {product_id} không tồn tại"
        )
    return product

async def get_all_products_controller(skip: int, limit: int, db: Session):
    return await product_service.list_products_logic(skip, limit, db)