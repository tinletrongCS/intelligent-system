from datetime import datetime, timezone, timedelta
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, model_serializer
from uuid import UUID

ICT = timezone(timedelta(hours=7))

def to_ict(dt: datetime) -> str:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ICT).isoformat()

# Base model xử lý múi giờ tại TPHCM (UTC+7)
class ICTBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_serializer(mode='wrap')
    def serialize_datetime(self, handler):
        result = handler(self)
        for key, val in result.items():
            if isinstance(val, datetime):
                result[key] = to_ict(val)
        return result

# USER 
class UserBase(BaseModel):
    username: str
    email: str
    role_id: int
    gender: Optional[str] = None
    age: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(ICTBaseModel, UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageResponse(BaseModel):
    message: str

class ForgotPasswordSchema(BaseModel):
    email: str

class ResetPasswordSchema(BaseModel):
    email: str
    otp: str
    new_password: str

# PRODUCT
class ProductBase(BaseModel):
    price: int
    discounted_price: Optional[int] = None
    product_display_name: str
    brand_name: str
    gender: Optional[str] = None
    age_group: Optional[str] = None
    base_colour: Optional[str] = None
    season: Optional[str] = None
    year: Optional[str] = None
    usage: Optional[str] = None
    # Bạn có thể khai báo thêm các trường khác nếu cần thiết trong API

class ProductResponse(ICTBaseModel, ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


# ORDER 
class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int

class OrderCreate(BaseModel):
    note: Optional[str] = None
    items: List[OrderItemCreate]

class OrderItemResponse(ICTBaseModel):
    id: int
    product_id: UUID
    quantity: int
    unit_price: int
    subtotal: int
    product: Optional[ProductResponse] = None

class OrderResponse(ICTBaseModel):
    id: UUID
    user_id: UUID
    order_date: datetime
    status: int
    total_amount: int
    note: Optional[str] = None
    items: List[OrderItemResponse] = []
    updated_at: datetime


# CART & WISHLIST 
class CartItemAdd(BaseModel):
    product_id: UUID
    quantity: int = 1

class CartItemResponse(ICTBaseModel):
    id: int
    user_id: UUID
    product_id: UUID
    quantity: int
    unit_price: int
    total_price: int
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None

class WishlistAdd(BaseModel):
    product_id: UUID

class WishlistResponse(ICTBaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    created_at: datetime
    product: Optional[ProductResponse] = None