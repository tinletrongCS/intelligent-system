from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from base_schema import ICTBaseModel

class ProductBase(BaseModel):
    price: float
    discounted_price: Optional[float] = None
    product_display_name: str
    brand_name: str
    gender: Optional[str] = None
    age_group: Optional[str] = None
    base_colour: Optional[str] = None
    season: Optional[str] = None
    year: Optional[str] = None
    usage: Optional[str] = None

class ProductResponse(ICTBaseModel, ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime