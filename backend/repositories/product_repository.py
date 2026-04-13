from sqlalchemy.orm import Session
from models.product_model import Product
from schemas.product_schema import ProductCreate
from uuid import UUID

def create_product(db: Session, product_in: ProductCreate):
    db_product = Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product_by_id(db: Session, product_id: UUID):
    return db.query(Product).filter(Product.id == product_id).first()

def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()