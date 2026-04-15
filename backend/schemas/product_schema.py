from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from .base_schema import ICTBaseModel

class ProductBase(BaseModel):
    brand_name: str #
    product_display_name: str #
    price: float #
    image_url: Optional[str] = None
    description: Optional[str] = None
    style_note: Optional[str] = None
    occasion: Optional[str] = None
    cross_links: Optional[str] = None
    is_active: bool = True

    discounted_price: Optional[float] = None #
    gender: Optional[str] = None #
    master_category: Optional[str] = None #
    sub_category: Optional[str] = None #
    article_type: Optional[str] = None #
    base_colour: Optional[str] = None #
    season: Optional[str] = None #
    usage: Optional[str] = None #
    myntra_rating: Optional[float] = None #
    fabric: Optional[str] = None #
    fit: Optional[str] = None #
    neck: Optional[str] = None #
    quantity_in_stock: Optional[int] = None #

class ProductCreate(ProductBase):
    pass #

class ProductUpdate(BaseModel):
    """Cập nhật sản phẩm - tất cả field optional"""
    brand_name: Optional[str] = None
    product_display_name: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    style_note: Optional[str] = None
    occasion: Optional[str] = None
    cross_links: Optional[str] = None
    is_active: Optional[bool] = None
    discounted_price: Optional[float] = None
    gender: Optional[str] = None
    master_category: Optional[str] = None
    sub_category: Optional[str] = None
    article_type: Optional[str] = None
    base_colour: Optional[str] = None
    season: Optional[str] = None
    usage: Optional[str] = None
    myntra_rating: Optional[float] = None
    fabric: Optional[str] = None
    fit: Optional[str] = None
    neck: Optional[str] = None
    quantity_in_stock: Optional[int] = None

class ProductQuantityUpdate(BaseModel):
    """Cập nhật số lượng trong kho"""
    quantity_in_stock: int

class ProductResponse(ICTBaseModel, ProductBase):
    id: UUID #
    created_at: datetime #
    updated_at: datetime #