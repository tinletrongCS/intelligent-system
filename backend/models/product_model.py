import uuid
from sqlalchemy import Column, String, Float, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_name = Column(String(255), nullable=False)
    gender = Column(String(50), nullable=True, index=True)
    master_category = Column(String(100), nullable=True, index=True)
    sub_category = Column(String(100), nullable=True, index=True)
    article_type = Column(String(100), nullable=True)
    base_colour = Column(String(100), nullable=True)
    season = Column(String(100), nullable=True)
    usage = Column(String(100), nullable=True)
    product_display_name = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    discounted_price = Column(Float, nullable=True)
    myntra_rating = Column(Float, nullable=True) 
    fabric = Column(String(255), nullable=True)
    fit = Column(String(100), nullable=True)
    neck = Column(String(100), nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete-orphan")
    wishlisted_by = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")
    in_carts = relationship("Cart", back_populates="product", cascade="all, delete-orphan")