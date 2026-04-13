from sqlalchemy.orm import Session
import repositories.product_repository as product_repo
from schemas.product_schema import ProductCreate
from uuid import UUID

async def create_new_product(product_in: ProductCreate, db: Session):
    # Logic nghiệp vụ thuần túy ở đây
    return product_repo.create_product(db, product_in)

async def get_product_logic(product_id: UUID, db: Session):
    return product_repo.get_product_by_id(db, product_id)

async def list_products_logic(skip: int, limit: int, db: Session):
    return product_repo.get_all_products(db, skip=skip, limit=limit)